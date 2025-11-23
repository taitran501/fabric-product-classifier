import streamlit as st
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
import pandas as pd
import re
import os
from pathlib import Path
from io import BytesIO

# Try to load .env file if it exists (for local development)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not required on HF Spaces

# Page configuration
st.set_page_config(
    page_title="Fabric Product Classifier - Batch Processing",
    page_icon="🧵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Model configuration
MODEL_NAME = os.getenv("MODEL_NAME", "aluha501/xlm-roberta-base-fabric")
MODEL_PATH = os.getenv("MODEL_PATH", None)
VALID_LABELS = ["vải", "sợi", "xơ", "quần/áo", "phụ_trợ"]
MAX_LENGTH = int(os.getenv("MAX_LENGTH", "128"))

# Preprocessing function from preprocessing.ipynb
def clean_product_string(s):
    """Clean product string based on preprocessing.ipynb logic"""
    if pd.isna(s) or s == '':
        return ''
    
    s = str(s).strip()
    
    # 1. Xóa @ ở cuối
    s = re.sub(r'\s*@$', '', s).strip()
    
    # 2. Xử lý các prefix/suffix có #&
    for _ in range(3):
        original_s = s
        s = re.sub(r'\s*#&(?:VN|CN|KR|TW|IT|JP)\s*$', '', s, flags=re.IGNORECASE).strip()
        if s == original_s:
            break

    s = re.sub(r'^[^\s]*#&\s*', '', s).strip()
    s = re.sub(r'\s*#&\s*', ' ', s).strip()

    # 3. Clean up ký tự đặc biệt thừa
    s = s.strip('\"')
    s = re.sub(r'[\s\.\,\-\']+$', '', s).strip()
    s = re.sub(r'[\[\]\{\}]', ' ', s).strip()
    
    # 4. Xóa dấu phẩy/chấm kép thừa
    s = re.sub(r'[,\.]{2,}', ',', s).strip()
    
    # 5. Xóa khoảng trắng thừa
    s = re.sub(r'\s+', ' ', s).strip()
    
    return s

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
        # Load tokenizer first
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
                        from transformers import XLMRobertaForSequenceClassification
                        model = XLMRobertaForSequenceClassification.from_pretrained(
                            MODEL_NAME,
                            config=config,
                            ignore_mismatched_sizes=True
                        )
                    except Exception as e4:
                        last_error = e4
        
        if model is None:
            raise last_error
        
        model.eval()
        return tokenizer, model
        
    except Exception as e:
        error_msg = str(e)
        st.error(f"❌ Error loading model: {error_msg}")
        st.stop()
        return None, None

def predict_batch(texts, tokenizer, model, batch_size=32, progress_callback=None):
    """Predict labels for a batch of texts"""
    device = next(model.parameters()).device
    predictions = []
    total_batches = (len(texts) + batch_size - 1) // batch_size
    
    for batch_idx, i in enumerate(range(0, len(texts), batch_size), 1):
        batch_texts = texts[i:i+batch_size]
        
        # Tokenize batch
        inputs = tokenizer(
            batch_texts,
            padding="max_length",
            truncation=True,
            max_length=MAX_LENGTH,
            return_tensors="pt"
        )
        
        # Move to device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Predict
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probabilities = torch.nn.functional.softmax(logits, dim=-1)
            pred_ids = torch.argmax(probabilities, dim=-1).cpu().numpy()
        
        # Convert to labels
        batch_predictions = [VALID_LABELS[pred_id] for pred_id in pred_ids]
        predictions.extend(batch_predictions)
        
        # Update progress if callback provided
        if progress_callback:
            progress = batch_idx / total_batches
            progress_callback(progress, batch_idx, total_batches, len(predictions), len(texts))
    
    return predictions

def main():
    # Custom CSS for beautiful header
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        margin: 0;
    }
    .section-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Beautiful centered header
    st.markdown("""
    <div class="main-header">
        <h1>🧵 Fabric Product Classifier</h1>
        <p>Batch Processing • Upload Excel • Get Predictions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load model
    with st.spinner("🔄 Loading AI model... This may take a moment on first run."):
        tokenizer, model = load_model()
    
    if tokenizer is None or model is None:
        st.stop()
    
    st.success("✅ Model loaded successfully!")
    
    # File upload section
    st.markdown("---")
    st.subheader("📤 Step 1: Upload Excel File")
    
    uploaded_file = st.file_uploader(
        "Choose an Excel file (.xlsx or .xls)",
        type=['xlsx', 'xls'],
        help="Upload an Excel file containing product descriptions"
    )
    
    if uploaded_file is not None:
        try:
            # Read Excel file
            df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ File loaded successfully! ({len(df)} rows, {len(df.columns)} columns)")
            
            # Show preview
            st.subheader("📋 File Preview")
            st.dataframe(df.head(10), width='stretch')
            
            # Column selection
            st.markdown("---")
            st.subheader("⚙️ Step 2: Configure Processing")
            
            # Auto-detect product column
            product_column_candidates = [col for col in df.columns if any(keyword in col.lower() for keyword in ['product', 'name', 'description', 'text', 'mô tả', 'sản phẩm'])]
            
            if product_column_candidates:
                default_column = product_column_candidates[0]
            else:
                default_column = df.columns[0] if len(df.columns) > 0 else None
            
            product_column = st.selectbox(
                "Select the column containing product descriptions:",
                options=df.columns.tolist(),
                index=df.columns.tolist().index(default_column) if default_column and default_column in df.columns else 0,
                help="Choose the column that contains product names/descriptions"
            )
            
            # Process button
            if st.button("🚀 Process File", type="primary", width='stretch'):
                if product_column not in df.columns:
                    st.error(f"❌ Column '{product_column}' not found in the file!")
                    st.stop()
                
                # Step 1: Preprocessing
                st.markdown("---")
                st.subheader("🔄 Processing...")
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("Step 1/3: Preprocessing product texts...")
                progress_bar.progress(0.1)
                
                # Apply preprocessing
                df['product_clean'] = df[product_column].astype(str).apply(clean_product_string)
                
                # Filter out rows with empty or '?' in cleaned text
                initial_count = len(df)
                df = df[df['product_clean'].str.len() > 0].copy()
                df = df[~df['product_clean'].str.contains(r'\?', na=False)].copy()
                filtered_count = len(df)
                
                progress_bar.progress(0.3)
                status_text.text(f"Step 1/3: Preprocessing complete. Processed {filtered_count} rows (removed {initial_count - filtered_count} invalid rows)")
                
                if filtered_count == 0:
                    st.error("❌ No valid rows after preprocessing!")
                    st.stop()
                
                # Step 2: Batch Prediction
                status_text.text("Step 2/3: Predicting labels...")
                progress_bar.progress(0.4)
                
                texts = df['product_clean'].tolist()
                
                # Create detailed progress bar for prediction
                prediction_progress_bar = st.progress(0)
                prediction_status = st.empty()
                
                def update_prediction_progress(progress, batch_idx, total_batches, processed, total):
                    """Callback to update prediction progress"""
                    prediction_progress_bar.progress(progress)
                    prediction_status.text(
                        f"Processing batch {batch_idx}/{total_batches} "
                        f"({processed}/{total} rows predicted - {progress*100:.1f}%)"
                    )
                    # Also update main progress bar (40% to 85%)
                    main_progress = 0.4 + (progress * 0.45)
                    progress_bar.progress(main_progress)
                
                predictions = predict_batch(
                    texts, 
                    tokenizer, 
                    model, 
                    batch_size=32,
                    progress_callback=update_prediction_progress
                )
                
                # Clear prediction progress bars
                prediction_progress_bar.empty()
                prediction_status.empty()
                
                df['label_predict'] = predictions
                
                progress_bar.progress(0.9)
                status_text.text("Step 3/3: Preparing download file...")
                
                # Step 3: Prepare download
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                output.seek(0)
                
                progress_bar.progress(1.0)
                status_text.text("✅ Processing complete!")
                
                # Show results summary
                st.markdown("---")
                st.subheader("📊 Results Summary")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Rows Processed", f"{filtered_count:,}")
                with col2:
                    st.metric("Rows with Predictions", f"{len(predictions):,}")
                with col3:
                    st.metric("Unique Labels", df['label_predict'].nunique())
                
                # Show label distribution
                st.markdown("**Label Distribution:**")
                label_counts = df['label_predict'].value_counts()
                st.bar_chart(label_counts)
                
                # Show sample results
                st.markdown("**Sample Results (first 10 rows):**")
                display_cols = [product_column, 'product_clean', 'label_predict']
                available_cols = [col for col in display_cols if col in df.columns]
                st.dataframe(df[available_cols].head(10), width='stretch')
                
                # Download button
                st.markdown("---")
                st.subheader("📥 Step 3: Download Results")
                
                filename = f"predictions_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                
                st.download_button(
                    label="⬇️ Download Excel File with Predictions",
                    data=output,
                    file_name=filename,
                    mime="application/vnd.openpyxl.formats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    width='stretch'
                )
                
                st.info("💡 The downloaded file contains all original columns plus the new 'label_predict' column.")
        
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.exception(e)
    else:
        st.info("👆 Please upload an Excel file to get started.")

if __name__ == "__main__":
    main()
