# GPU Setup Guide - Vast.ai Integration

## 📋 Current GPU Configuration

**SSH Connection:**
```bash
ssh -p 54754 root@143.55.45.86
```

**API Port:** `5001`  
**Tunnel URL:** `https://[YOUR_TUNNEL_URL].trycloudflare.com` (lấy từ vast.ai dashboard)

**Streamlit Cloud Secrets (TOML format):**
```toml
GPU_API_ENDPOINT = "https://[YOUR_TUNNEL_URL].trycloudflare.com"
```

---

## 🚀 Quick Setup (Khi thuê GPU mới)

### Step 1: Setup API Server trên GPU

```bash
# 1. SSH vào GPU
ssh -p [PORT] root@[IP]

# 2. Tạo file api_server.py (copy từ api_server_content.txt)
cd /root
nano api_server.py
# Paste nội dung từ api_server_content.txt, Save: Ctrl+O, Enter, Ctrl+X

# 3. Cài dependencies
pip3 install flask flask-cors transformers torch sentencepiece tokenizers huggingface-hub gunicorn

# 4. Verify GPU
python3 -c "import torch; print(f'CUDA: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"

# 5. Start với gunicorn (trong screen)
screen -S api_server
cd /root
gunicorn -w 1 -b 0.0.0.0:5001 --timeout 300 api_server:app
# Press Ctrl+A then D để detach

# 6. Test local
curl http://localhost:5001/health
```

### Step 2: Tạo Tunnel trên vast.ai

1. Vào vast.ai dashboard → Instance → **"Tunnels"**
2. Nhập target URL: `http://localhost:5001`
3. Click **"+ Create New Tunnel"**
4. Copy **Tunnel URL** (dạng `https://xxxxx.trycloudflare.com`)

### Step 3: Update Streamlit Cloud Secrets

1. Streamlit Cloud → App → **Settings** → **Secrets**
2. Update:
   ```toml
   GPU_API_ENDPOINT = "https://[TUNNEL_URL].trycloudflare.com"
   ```
3. Save, đợi ~1 phút

### Step 4: Test

```bash
# Test tunnel từ local
curl https://[TUNNEL_URL].trycloudflare.com/health

# Test app với Excel file
```

---

## 🔄 Khi Thuê GPU Mới - Checklist

- [ ] Lấy SSH info: `ssh -p [PORT] root@[IP]`
- [ ] Upload `api_server.py` lên GPU (copy từ `api_server_content.txt`)
- [ ] Cài dependencies: `pip3 install -r api_requirements.txt`
- [ ] Start API: `gunicorn -w 1 -b 0.0.0.0:5001 --timeout 300 api_server:app`
- [ ] Tạo tunnel trên vast.ai cho `http://localhost:5001`
- [ ] Copy tunnel URL
- [ ] Update Streamlit Secrets: `GPU_API_ENDPOINT = "https://[TUNNEL_URL]"`
- [ ] Test: `curl https://[TUNNEL_URL]/health`

**Files cần update (optional - chỉ để document):**
- `GPU_SETUP.md` - Section "Current GPU Configuration"
- `app.py` - Comment line 37

---

## 🐛 Troubleshooting

### Port đang dùng
```bash
lsof -ti:5001 | xargs kill -9
```

### API server không chạy
```bash
ps aux | grep gunicorn
screen -r api_server  # Xem logs
```

### Tunnel không hoạt động
- Check tunnel active trong vast.ai dashboard
- Test local: `curl http://localhost:5001/health`
- Recreate tunnel nếu cần

### Streamlit không kết nối
- Verify secret format: TOML, có quotes, HTTPS
- Test tunnel URL từ browser
- Đợi 1-2 phút sau khi save secrets

---

## 📝 Quick Commands

```bash
# Check API server
ps aux | grep gunicorn
curl http://localhost:5001/health

# Restart API server
pkill -f gunicorn
screen -S api_server
cd /root
gunicorn -w 1 -b 0.0.0.0:5001 --timeout 300 api_server:app

# Test tunnel
curl https://[TUNNEL_URL].trycloudflare.com/health
```

---

## ⚙️ Configuration

**Port:** `5001` (có thể đổi trong `api_server.py` nếu cần)  
**Batch Size:** `128` (GPU), `64` (CPU)  
**FP16:** Tự động enable nếu GPU hỗ trợ  
**Chunk Size:** `2000` rows per API request

---

## ✅ Success Indicators

- ✅ `curl http://localhost:5001/health` → JSON response (trên GPU)
- ✅ `curl https://tunnel-url/health` → JSON response (từ local)
- ✅ App process files nhanh (~1000-2000+ texts/sec với GPU)
- ✅ Không có connection timeout errors
