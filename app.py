import streamlit as st
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
import os
from pathlib import Path
# Try to load .env file if it exists (for local development)
# On Hugging Face Spaces, this will be skipped automatically
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not required on HF Spaces

# Page configuration
st.set_page_config(
    page_title="Fabric Product Classifier",
    page_icon="🧵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize theme in session state
if 'theme' not in st.session_state:
    # Try to detect system preference
    st.session_state.theme = 'light'

def get_css(theme):
    """Generate CSS based on theme"""
    if theme == 'dark':
        bg_color = "#0e1117"
        card_bg = "#1e1e1e"
        text_color = "#ffffff"
        text_secondary = "#b0b0b0"
        border_color = "#333333"
        example_bg = "#2a2a2a"
        pred_item_bg = "#2a2a2a"
        pred_item_top_bg = "linear-gradient(90deg, #2a2a3a 0%, #2a2a2a 100%)"
    else:  # light
        bg_color = "#ffffff"
        card_bg = "#ffffff"
        text_color = "#333333"
        text_secondary = "#666666"
        border_color = "#e0e0e0"
        example_bg = "#f8f9fa"
        pred_item_bg = "#ffffff"
        pred_item_top_bg = "linear-gradient(90deg, #f0f4ff 0%, white 100%)"
    
    return f"""
    <style>
        /* Main styling */
        .main {{
            padding-top: 0;
        }}
        
        /* Remove extra padding */
        .block-container {{
            padding-top: 1rem;
            padding-bottom: 1rem;
        }}
        
        /* Force theme colors */
        .stApp {{
            background-color: {bg_color};
        }}
        
        /* Header styling */
        .header-container {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem 2rem;
            border-radius: 15px;
            margin-bottom: 1.5rem;
            margin-top: 0.5rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        
        .header-title {{
            color: white;
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            text-align: center;
        }}
        
        .header-subtitle {{
            color: rgba(255,255,255,0.9);
            font-size: 1.2rem;
            text-align: center;
            margin-top: 0.5rem;
        }}
        
        /* Category cards */
        .category-card {{
            background: {card_bg};
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
            border-left: 4px solid #667eea;
            margin-bottom: 1rem;
            color: {text_color};
        }}
        
        .category-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }}
        
        /* Result cards */
        .result-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            color: white;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 2rem;
        }}
        
        .prediction-label {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}
        
        .confidence-score {{
            font-size: 1.5rem;
            opacity: 0.9;
        }}
        
        /* Prediction item */
        .pred-item {{
            background: {pred_item_bg};
            padding: 1rem 1.5rem;
            border-radius: 10px;
            margin-bottom: 0.8rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .pred-item-top {{
            border-left: 5px solid #667eea;
            background: {pred_item_top_bg};
        }}
        
        .pred-label {{
            font-size: 1.2rem;
            font-weight: 600;
            color: {text_color};
        }}
        
        .pred-conf {{
            font-size: 1.1rem;
            font-weight: 700;
            color: #667eea;
        }}
        
        /* Button styling - Primary */
        .stButton>button[kind="primary"] {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-size: 1.1rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }}
        
        .stButton>button[kind="primary"]:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }}
        
        /* Button styling - Secondary (Example chips) */
        .stButton>button[kind="secondary"] {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 20px;
            padding: 0.5rem 1rem;
            font-size: 0.85rem;
            font-weight: 500;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
        }}
        
        .stButton>button[kind="secondary"]:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.5);
        }}
        
        .example-chip:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.5);
            border-color: rgba(255,255,255,0.3);
        }}
        
        .example-chip:active {{
            transform: translateY(0);
        }}
        
        .example-section-title {{
            color: {text_color};
            font-size: 0.95rem;
            font-weight: 600;
            margin-bottom: 0.8rem;
            opacity: 0.8;
        }}
        
        /* Status badge */
        .status-badge {{
            display: inline-block;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }}
        
        .status-success {{
            background: #d4edda;
            color: #155724;
        }}
        
        /* Text area styling */
        .stTextArea textarea {{
            background-color: {card_bg} !important;
            color: {text_color} !important;
        }}
        
        /* Section headers */
        h3 {{
            color: {text_color} !important;
        }}
        
        /* Hide Streamlit default elements */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
    </style>
    """

# Apply CSS based on current theme
st.markdown(get_css(st.session_state.theme), unsafe_allow_html=True)

# Model configuration - can be overridden by .env file
MODEL_NAME = os.getenv("MODEL_NAME", "aluha501/xlm-roberta-base-fabric")
MODEL_PATH = os.getenv("MODEL_PATH", None)  # Optional local path
VALID_LABELS = ["vải", "sợi", "xơ", "quần/áo", "phụ_trợ"]
LABEL_DESCRIPTIONS = {
    "vải": "Fabric",
    "sợi": "Yarn/Thread",
    "xơ": "Fiber",
    "quần/áo": "Pants/Shirt",
    "phụ_trợ": "Accessories"
}
MAX_LENGTH = int(os.getenv("MAX_LENGTH", "128"))

# Cache the model and tokenizer for faster loading
@st.cache_resource
def load_model():
    """Load the model and tokenizer from Hugging Face or local path"""
    # Try loading from local path first if specified
    if MODEL_PATH and Path(MODEL_PATH).exists():
        try:
            tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
            model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
            model.eval()
            return tokenizer, model
        except Exception as e:
            st.warning(f"⚠️ Failed to load from local path: {str(e)}")
            st.info("🔄 Trying to load from Hugging Face instead...")
    
    # Try loading from Hugging Face with multiple fallback methods
    try:
        # Load tokenizer first (usually works)
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        
        # Try different methods to load the model
        model = None
        last_error = None
        
        # Method 1: Standard AutoModel load
        try:
            model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
        except Exception as e1:
            last_error = e1
            # Method 2: With trust_remote_code
            try:
                model = AutoModelForSequenceClassification.from_pretrained(
                    MODEL_NAME, 
                    trust_remote_code=True
                )
            except Exception as e2:
                last_error = e2
                # Method 3: Load with explicit XLM-RoBERTa class
                try:
                    from transformers import XLMRobertaForSequenceClassification
                    model = XLMRobertaForSequenceClassification.from_pretrained(MODEL_NAME)
                except Exception as e3:
                    last_error = e3
                    # Method 4: Load base model and configure
                    try:
                        from transformers import XLMRobertaConfig
                        config = XLMRobertaConfig.from_pretrained(MODEL_NAME)
                        config.num_labels = len(VALID_LABELS)
                        # Try to create model with config
                        from transformers import XLMRobertaForSequenceClassification
                        model = XLMRobertaForSequenceClassification.from_pretrained(
                            MODEL_NAME,
                            config=config,
                            ignore_mismatched_sizes=True
                        )
                    except Exception as e4:
                        last_error = e4
        
        if model is None:
            raise Exception(f"All loading methods failed. Last error: {str(last_error)}")
        
        model.eval()
        return tokenizer, model
        
    except Exception as e:
        error_msg = str(e)
        st.error(f"❌ Error loading model: {error_msg}")
        
        # Provide helpful troubleshooting
        troubleshooting = """
        💡 **Troubleshooting Tips:**
        
        1. **Use local model path (Recommended if Hugging Face fails):**
           - Create `.env` file in `web_app` folder
           - Add: `MODEL_PATH=../final/fabric_classifier_hf`
           - This will load from your local trained model
        
        2. **Update packages:**
           ```bash
           pip install --upgrade torch transformers
           ```
        
        3. **Check internet connection** - Model needs to download from Hugging Face
        
        4. **Verify model on Hugging Face:**
           - Visit: https://huggingface.co/aluha501/xlm-roberta-base-fabric
           - Ensure model files (config.json, pytorch_model.bin) are available
        
        5. **Clear Hugging Face cache:**
           ```bash
           rm -rf ~/.cache/huggingface/
           ```
        """
        st.markdown(troubleshooting)
        return None, None

def predict(text, tokenizer, model):
    """Predict the label for the input text"""
    if not text.strip():
        return None, None, None
    
    # Tokenize the input
    inputs = tokenizer(
        text,
        padding="max_length",
        truncation=True,
        max_length=MAX_LENGTH,
        return_tensors="pt"
    )
    
    # Move inputs to the same device as model
    device = next(model.parameters()).device
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    # Get predictions
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
    
    # Convert to probabilities
    probabilities = torch.nn.functional.softmax(logits, dim=-1)
    probabilities = probabilities.cpu().numpy()[0]
    
    # Get predicted label
    predicted_id = np.argmax(probabilities)
    predicted_label = VALID_LABELS[predicted_id]
    confidence = probabilities[predicted_id]
    
    # Get all predictions sorted by confidence
    all_predictions = [
        {"label": VALID_LABELS[i], "confidence": float(probabilities[i])}
        for i in range(len(VALID_LABELS))
    ]
    all_predictions.sort(key=lambda x: x["confidence"], reverse=True)
    
    return predicted_label, confidence, all_predictions

# Main app
def main():
    # Theme toggle and header in one clean row
    theme_icon = "🌙" if st.session_state.theme == 'light' else "☀️"
    theme_tooltip = "Switch to Dark Mode" if st.session_state.theme == 'light' else "Switch to Light Mode"
    
    # Header row with theme toggle
    h1, h2 = st.columns([0.96, 0.04])
    with h1:
        st.markdown("""
        <div class="header-container">
            <div class="header-title">🧵 Fabric Product Classifier</div>
            <div class="header-subtitle">AI-Powered Text Classification for Fabric Products</div>
        </div>
        """, unsafe_allow_html=True)
    with h2:
        if st.button(theme_icon, key="theme_toggle", help=theme_tooltip, use_container_width=True):
            st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
            st.rerun()
    
    # Load model
    with st.spinner("🔄 Loading AI model from Hugging Face... This may take a moment on first run."):
        tokenizer, model = load_model()
    
    if tokenizer is None or model is None:
        st.stop()
    
    # Success badge
    st.markdown("""
    <div class="status-badge status-success">
        ✅ Model loaded successfully! Ready to classify products.
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for layout
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        # Input section
        st.markdown("### 📝 Enter Product Description")
        
        # Text input area
        user_input = st.text_area(
            " ",
            placeholder="Enter product description here...\n\nSee example inputs below for reference!",
            height=180,
            help="Enter the product description in Vietnamese or English",
            key="input_text",
            label_visibility="collapsed"
        )
        
        # Example inputs - display only (for reference)
        examples_data = [
            ("🧵", "cotton fabric"),
            ("🪡", "polyester yarn thread"),
            ("🌾", "polyester fiber roll"),
            ("👕", "children pants")
        ]
        
        text_color = "#b0b0b0" if st.session_state.theme == 'dark' else "#666666"
        st.markdown(f'<div class="example-section-title">💡 Example inputs (for reference):</div>', unsafe_allow_html=True)
        
        # Display examples as styled text (not clickable buttons)
        bg_color = "#2a2a2a" if st.session_state.theme == 'dark' else "#f0f4ff"
        border_color = "#444444" if st.session_state.theme == 'dark' else "#d0d0d0"
        
        example_chips_html = f'<div style="display: flex; flex-wrap: wrap; gap: 0.75rem; margin-top: 0.5rem;">'
        for icon, example in examples_data:
            example_chips_html += f'<div style="background: {bg_color}; border: 1px solid {border_color}; border-radius: 12px; padding: 0.75rem 1rem; display: flex; align-items: center; gap: 0.5rem; font-size: 0.9rem;"><span style="font-size: 1.2rem;">{icon}</span><code style="background: transparent; color: {text_color}; font-size: 0.9rem; padding: 0; border: none;">{example}</code></div>'
        example_chips_html += '</div>'
        st.markdown(example_chips_html, unsafe_allow_html=True)
        
        # Predict button
        predict_clicked = st.button("🔮 Predict Product Category", type="primary", use_container_width=True)
        
        # Results section
        if predict_clicked:
            if user_input and user_input.strip():
                with st.spinner("🤖 Analyzing product description..."):
                    predicted_label, confidence, all_predictions = predict(user_input, tokenizer, model)
                
                if predicted_label:
                    # Main result card
                    st.markdown(f"""
                    <div class="result-card">
                        <div style="text-align: center;">
                            <div style="font-size: 1.2rem; opacity: 0.9; margin-bottom: 1rem;">Predicted Category</div>
                            <div class="prediction-label">{predicted_label}</div>
                            <div style="font-size: 1rem; opacity: 0.8; margin-top: 0.5rem;">{LABEL_DESCRIPTIONS[predicted_label]}</div>
                            <div class="confidence-score" style="margin-top: 1.5rem;">
                                Confidence: {confidence:.1%}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Confidence progress bar with custom styling
                    st.progress(float(confidence))
                    
                    # All predictions
                    st.markdown("### 📊 Detailed Predictions")
                    for i, pred in enumerate(all_predictions):
                        label = pred["label"]
                        conf = pred["confidence"]
                        is_top = i == 0
                        
                        # Create prediction item HTML
                        badge = "🥇" if is_top else f"#{i+1}"
                        card_class = "pred-item pred-item-top" if is_top else "pred-item"
                        
                        text_secondary = "#b0b0b0" if st.session_state.theme == 'dark' else "#666666"
                        st.markdown(f"""
                        <div class="{card_class}">
                            <div>
                                <span style="font-size: 1.5rem; margin-right: 0.5rem;">{badge}</span>
                                <span class="pred-label">{label}</span>
                                <span style="color: {text_secondary}; font-size: 0.9rem; margin-left: 0.5rem;">({LABEL_DESCRIPTIONS[label]})</span>
                            </div>
                            <div class="pred-conf">{conf:.1%}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Progress bar for each prediction
                        st.progress(float(conf))
            else:
                st.warning("⚠️ Please enter a product description to get a prediction.")
    
    with col_right:
        # Categories info
        st.markdown("### 🏷️ Categories")
        
        categories_info = [
            ("🧵", "vải", "Fabric"),
            ("🪡", "sợi", "Yarn/Thread"),
            ("🌾", "xơ", "Fiber"),
            ("👕", "quần/áo", "Pants/Shirt"),
            ("🔧", "phụ_trợ", "Accessories")
        ]
        
        for icon, label, desc in categories_info:
            text_secondary = "#b0b0b0" if st.session_state.theme == 'dark' else "#666666"
            st.markdown(f"""
            <div class="category-card">
                <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{icon} <strong>{label}</strong></div>
                <div style="color: {text_secondary}; font-size: 0.9rem;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    footer_color = "#b0b0b0" if st.session_state.theme == 'dark' else "#666666"
    st.markdown(f"""
    <div style="text-align: center; color: {footer_color}; padding: 2rem;">
        <p>Powered by <strong>XLM-RoBERTa</strong> • Model: <code>aluha501/xlm-roberta-base-fabric</code></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
