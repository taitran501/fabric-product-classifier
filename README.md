# 🧵 Fabric Product Classifier - Batch Processing

Web application for classifying fabric products into categories using XLM-RoBERTa model.

## Features

- 📤 Upload Excel files with product descriptions
- 🔄 Automatic text preprocessing
- 🤖 AI-powered batch prediction
- 📥 Download results with predictions

## Categories

- **vải** - Fabric
- **sợi** - Yarn/Thread
- **xơ** - Fiber
- **quần/áo** - Pants/Shirt
- **phụ_trợ** - Accessories

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run app.py
```

### Deployment

Deployed on **Streamlit Community Cloud**

**Repository:** `https://github.com/taitran501/fabric-product-classifier`

**Live Demo:** [Your Streamlit Cloud URL]

## GPU Acceleration (Optional)

For faster predictions, setup GPU server on vast.ai:

1. See `GPU_SETUP.md` for detailed instructions
2. Quick setup:
   - Upload `api_server.py` to GPU server
   - Create tunnel on vast.ai dashboard
   - Update `GPU_API_ENDPOINT` in Streamlit Cloud Secrets

## Files

- `app.py` - Main Streamlit application
- `api_server.py` - GPU API server (deploy on vast.ai)
- `api_server_content.txt` - API server content for copy-paste
- `requirements.txt` - Python dependencies
- `api_requirements.txt` - Dependencies for GPU server
- `GPU_SETUP.md` - GPU setup guide

## Model

- **Model:** `aluha501/xlm-roberta-base-fabric`
- **Base:** XLM-RoBERTa Base
- **Accuracy:** 98.55%
- **Macro F1:** 96.23%

## Usage

1. Upload Excel file with product descriptions
2. Select the product column
3. Click "Process File"
4. Download results with `label_predict` column

---

For GPU setup details, see `GPU_SETUP.md`
