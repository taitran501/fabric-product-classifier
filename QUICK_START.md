# Quick Start - Deploy to Streamlit Cloud

## 📋 Checklist trước khi deploy

- [x] `app.py` - Main app file (✅ có)
- [x] `requirements.txt` - Dependencies (✅ có)
- [x] `README.md` - Project description (✅ có)
- [x] `.gitignore` - Git ignore rules (✅ có)
- [x] `.streamlit/config.toml` - Streamlit config (✅ có)

## 🚀 3 Bước Deploy

### 1. Tạo GitHub Repository

```bash
# Trên GitHub.com
# New repository → fabric-product-classifier → Public → Create
```

### 2. Push Code (Tự động)

**Windows:**
```bash
cd fabric-product-classifier
push_to_github.bat
```

**Linux/Mac:**
```bash
cd fabric-product-classifier
chmod +x push_to_github.sh
./push_to_github.sh
```

**Hoặc thủ công:**
```bash
cd fabric-product-classifier
git init
git add app.py requirements.txt README.md .gitignore .streamlit/
git commit -m "Initial commit: Fabric Product Classifier"
git remote add origin https://github.com/YOUR_USERNAME/fabric-product-classifier.git
git branch -M main
git push -u origin main
```

### 3. Deploy trên Streamlit Cloud

1. Vào: https://share.streamlit.io
2. Login với GitHub
3. New app → Chọn repo → Branch: `main` → Main file: `app.py`
4. Deploy!

## ✅ Done!

App sẽ có URL: `https://your-app-name.streamlit.app`

## 📝 Cập nhật sau này

```bash
git add .
git commit -m "Update: [mô tả]"
git push
# Streamlit Cloud tự động rebuild
```

