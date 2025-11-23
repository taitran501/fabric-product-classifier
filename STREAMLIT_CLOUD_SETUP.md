# Quick Setup Guide for Streamlit Cloud

## Files Structure

Đảm bảo bạn có các file sau trong repository:

```
fabric-product-classifier/
├── app.py              # Main Streamlit app (REQUIRED)
├── requirements.txt    # Python dependencies (REQUIRED)
├── README.md          # Project description
├── .gitignore         # Git ignore rules
└── .streamlit/
    └── config.toml    # Streamlit configuration (optional)
```

## Bước 1: Tạo GitHub Repository

1. Đăng nhập GitHub
2. Click "New repository"
3. Tên: `fabric-product-classifier`
4. Public (cho free hosting)
5. Không tạo README (đã có sẵn)
6. Click "Create repository"

## Bước 2: Push Code lên GitHub

```bash
# Trong folder fabric-product-classifier/
cd fabric-product-classifier

# Initialize git (nếu chưa có)
git init

# Add files
git add app.py requirements.txt README.md .gitignore .streamlit/

# Commit
git commit -m "Initial commit: Fabric Product Classifier for Streamlit Cloud"

# Add remote (thay YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/fabric-product-classifier.git

# Push
git branch -M main
git push -u origin main
```

## Bước 3: Deploy trên Streamlit Cloud

1. Truy cập: https://share.streamlit.io
2. Đăng nhập bằng GitHub account
3. Click "New app"
4. Điền thông tin:
   - **Repository**: `YOUR_USERNAME/fabric-product-classifier`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL**: Chọn subdomain (ví dụ: `fabric-classifier`)
5. Click "Deploy"

## Bước 4: Chờ Deployment

- Lần đầu: 2-5 phút
- Streamlit Cloud sẽ tự động:
  - Install dependencies
  - Build app
  - Deploy

## Bước 5: Truy cập App

Sau khi deploy xong, app sẽ có URL:
```
https://fabric-classifier.streamlit.app
```
(hoặc subdomain bạn chọn)

## Cập nhật App

Mỗi lần push code:
```bash
git add .
git commit -m "Update: [mô tả]"
git push
```

Streamlit Cloud sẽ tự động rebuild.

## Troubleshooting

### Build fails
- Kiểm tra `requirements.txt` có đúng không
- Xem logs trong Streamlit Cloud dashboard
- Đảm bảo `app.py` không có syntax errors

### Model không load
- Verify model trên Hugging Face: https://huggingface.co/aluha501/xlm-roberta-base-fabric
- Check internet connection (model cần download từ HF)
- Lần đầu load sẽ chậm (2-3 phút), sau đó được cache

### App không update
- Force refresh browser (Ctrl+F5)
- Check git push đã thành công
- Xem deployment logs trong dashboard

## Lưu ý

- ✅ Streamlit Cloud free forever
- ✅ Auto-deploy từ GitHub
- ✅ Performance tốt cho Streamlit apps
- ✅ Không cần Dockerfile (khác với HF Spaces)
- ✅ App file phải là `app.py` ở root folder

