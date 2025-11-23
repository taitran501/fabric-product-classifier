# 🧵 Fabric Product Classifier

AI-powered web application for classifying fabric products into 5 categories using a fine-tuned XLM-RoBERTa model.

## 🎯 Features

- **5 Product Categories**: vải (fabric), sợi (yarn/thread), xơ (fiber), quần/áo (pants/shirt), phụ_trợ (accessories)
- **Real-time Prediction**: Instant classification with confidence scores
- **Beautiful UI**: Modern gradient design with dark/light mode support
- **Example Chips**: Quick fill text with pre-loaded examples

## 🚀 Live Demo

Deployed on Streamlit Cloud: [View App](https://your-app-name.streamlit.app)

## 📊 Model

This app uses the `aluha501/xlm-roberta-base-fabric` model from Hugging Face, a fine-tuned XLM-RoBERTa model trained on fabric product descriptions.

## 💡 Example Inputs

- `cotton fabric`
- `polyester yarn thread`
- `polyester fiber roll`
- `children pants`

## 🔧 Technical Details

- **Framework**: Streamlit
- **Model**: XLM-RoBERTa Base (fine-tuned)
- **Max Input Length**: 128 tokens
- **Categories**: 5 classes

## 📦 Installation (Local Development)

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/fabric-product-classifier.git
cd fabric-product-classifier

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run app.py
```

## 📝 License

MIT License

## 👤 Author

aluha501
