import streamlit as st
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
import pandas as pd
import re
import os
from pathlib import Path
from io import BytesIO
import requests

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

# GPU API configuration (for vast.ai GPU server)
# Set GPU_API_ENDPOINT environment variable in Streamlit Cloud to enable GPU acceleration
# Example: GPU_API_ENDPOINT=http://143.55.45.86:5000
# When renting new GPU, update this value in Streamlit Cloud Secrets
# Current GPU: ssh -p 54754 root@143.55.45.86
GPU_API_ENDPOINT = os.getenv("GPU_API_ENDPOINT", None)

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

def predict_batch_api(texts, api_endpoint, progress_callback=None):
    """Predict using GPU API endpoint (vast.ai)"""
    total = len(texts)
    predictions = []
    
    # Chia thành chunks lớn hơn cho API (2000 rows mỗi request để tối ưu throughput)
    # Larger chunks = fewer HTTP requests = faster overall processing
    chunk_size = 2000
    total_chunks = (total + chunk_size - 1) // chunk_size
    
    for chunk_idx in range(total_chunks):
        start_idx = chunk_idx * chunk_size
        end_idx = min(start_idx + chunk_size, total)
        chunk_texts = texts[start_idx:end_idx]
        
        try:
            response = requests.post(
                f"{api_endpoint}/predict",
                json={'texts': chunk_texts},
                timeout=300  # 5 minutes timeout per chunk
            )
            response.raise_for_status()
            result = response.json()
            chunk_predictions = result['predictions']
            predictions.extend(chunk_predictions)
            
            if progress_callback:
                progress = (chunk_idx + 1) / total_chunks
                processed = len(predictions)
                progress_callback(progress, chunk_idx + 1, total_chunks, processed, total)
        
        except requests.exceptions.ConnectTimeout:
            error_msg = "GPU API connection timeout"
            st.error(f"❌ {error_msg}")
            raise Exception(error_msg)
        except requests.exceptions.ConnectionError:
            error_msg = "GPU API connection failed - check if server is running and accessible"
            st.error(f"❌ {error_msg}")
            raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            # Hide IP addresses from error messages
            import re
            error_msg = str(e)
            error_msg = re.sub(r'\d+\.\d+\.\d+\.\d+', '[IP_HIDDEN]', error_msg)
            st.error(f"❌ Error calling GPU API: {error_msg}")
            raise Exception(f"GPU API error: {error_msg}")
    
    return predictions

def predict_batch(texts, tokenizer, model, batch_size=32, progress_callback=None, use_gpu_api=False, gpu_api_endpoint=None):
    """
    Predict labels for a batch of texts.
    Uses GPU API if available, otherwise falls back to local model (CPU).
    """
    # Priority: GPU API > Local Model
    if use_gpu_api and gpu_api_endpoint:
        try:
            # Test API connection first
            health_response = requests.get(f"{gpu_api_endpoint}/health", timeout=5)
            if health_response.status_code == 200:
                # Silently use GPU - no message to users
                return predict_batch_api(texts, gpu_api_endpoint, progress_callback)
            else:
                # Silently fallback to CPU
                pass
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError, Exception):
            # Silently fallback to CPU - don't show errors to users
            pass
    
    # Fallback to local model (CPU) - model must be loaded
    if model is None or tokenizer is None:
        raise ValueError("Model and tokenizer must be loaded when GPU API is not available")
    
    device = next(model.parameters()).device
    predictions = []
    total_batches = (len(texts) + batch_size - 1) // batch_size
    
    for batch_idx, i in enumerate(range(0, len(texts), batch_size), 1):
        batch_texts = texts[i:i+batch_size]
        
        # Tokenize batch (optimized: use padding='longest' for variable length)
        inputs = tokenizer(
            batch_texts,
            padding=True,  # 'longest' padding is faster than 'max_length'
            truncation=True,
            max_length=MAX_LENGTH,
            return_tensors="pt"
        )
        
        # Move to device (with non_blocking for faster transfer if CUDA)
        if device.type == 'cuda':
            inputs = {k: v.to(device, non_blocking=True) for k, v in inputs.items()}
        else:
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
    # Read GPU_API_ENDPOINT from environment (re-read each time to avoid UnboundLocalError)
    # Streamlit Cloud Secrets are available as environment variables
    # Format in Streamlit Cloud Secrets (TOML):
    # GPU_API_ENDPOINT = "http://143.55.45.86:5000"
    gpu_api_endpoint = os.getenv("GPU_API_ENDPOINT", None)
    
    # Debug mode: Only show GPU info in local development (not on Streamlit Cloud)
    # Check if running locally by checking for .env file or localhost
    is_local = os.path.exists(".env") or "localhost" in os.getenv("STREAMLIT_SERVER_PORT", "")
    
    # Only show debug info locally, not on production
    if is_local and gpu_api_endpoint:
        endpoint_preview = gpu_api_endpoint.split("://")[-1].split("/")[0] if "://" in gpu_api_endpoint else "[configured]"
        st.info(f"🔧 [DEBUG] GPU API endpoint configured: {endpoint_preview}")
    elif is_local:
        st.info("ℹ️ [DEBUG] GPU API endpoint not configured - using CPU mode")
    
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
    
    # Check GPU API availability and load model accordingly
    tokenizer = None
    model = None
    use_gpu_api = False  # Track if we should use GPU API
    
    if gpu_api_endpoint:
        try:
            health_response = requests.get(f"{gpu_api_endpoint}/health", timeout=5)
            if health_response.status_code == 200:
                health_data = health_response.json()
                # Only show success message in local debug mode
                if is_local:
                    st.success(f"✅ [DEBUG] GPU acceleration available! ({health_data.get('device', 'GPU')})")
                use_gpu_api = True  # GPU API is available
            else:
                # Only show warning in local debug mode
                if is_local:
                    st.warning("⚠️ [DEBUG] GPU API not responding, will use CPU fallback")
                use_gpu_api = False
        except requests.exceptions.ConnectTimeout:
            # Silently fallback to CPU - don't show error to users
            use_gpu_api = False
        except requests.exceptions.ConnectionError:
            # Silently fallback to CPU - don't show error to users
            use_gpu_api = False
        except Exception as e:
            # Silently fallback to CPU - don't show error to users
            use_gpu_api = False
    
    # Load model (only needed if GPU API is not available)
    if not use_gpu_api:
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
                    progress_callback=update_prediction_progress,
                    use_gpu_api=use_gpu_api,
                    gpu_api_endpoint=gpu_api_endpoint
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
