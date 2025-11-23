---
title: Fabric Product Classifier
emoji: 🧵
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: 1.28.0
app_file: app.py
pinned: false
license: mit
---

# 🧵 Fabric Product Classifier

AI-powered web application for classifying fabric products into 5 categories using a fine-tuned XLM-RoBERTa model.

## 🎯 Features

- **5 Product Categories**: vải (fabric), sợi (yarn/thread), xơ (fiber), quần/áo (pants/shirt), phụ_trợ (accessories)
- **Real-time Prediction**: Instant classification with confidence scores
- **Beautiful UI**: Modern gradient design with dark/light mode support
- **One-click Examples**: Quick test with pre-loaded examples

## 🚀 Usage

1. Enter a product description in the text area (supports Vietnamese and English)
2. Click "Predict Product Category" or use one of the example chips
3. View the predicted category with confidence score
4. See detailed predictions for all 5 categories

## 📊 Model

This app uses the `aluha501/xlm-roberta-base-fabric` model, a fine-tuned XLM-RoBERTa model trained on fabric product descriptions.

## 💡 Example Inputs

- `cotton fabric 100% new`
- `polyester yarn thread`
- `polyester fiber roll`
- `children pants`

## 🔧 Technical Details

- **Framework**: Streamlit
- **Model**: XLM-RoBERTa Base (fine-tuned)
- **Max Input Length**: 128 tokens
- **Categories**: 5 classes

## 📝 License

MIT License

