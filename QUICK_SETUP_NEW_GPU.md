# 🚀 Quick Setup Guide - New GPU Rental

**Tài liệu này hướng dẫn setup nhanh khi bạn thuê GPU mới từ vast.ai**

---

## 📋 Checklist - Tất cả các bước cần làm:

- [ ] 1. Lấy thông tin SSH từ vast.ai
- [ ] 2. Upload và setup API server trên GPU mới
- [ ] 3. Tạo Tunnel trên vast.ai dashboard
- [ ] 4. Test Tunnel URL
- [ ] 5. Cập nhật Streamlit Cloud Secrets
- [ ] 6. Test app

---

## 🔧 Step 1: Lấy thông tin GPU mới

Từ vast.ai dashboard, lấy thông tin:
- **SSH Command**: `ssh -p [PORT] root@[IP]`
- **IP Address**: `[IP]`
- **Port**: `[PORT]`
- **Proxy SSH** (nếu có): `ssh -p [PROXY_PORT] root@ssh9.vast.ai`

**Ví dụ:**
```bash
ssh -p 54754 root@143.55.45.86
```

---

## 📤 Step 2: Setup API Server trên GPU mới

### 2.1. SSH vào GPU server
```bash
ssh -p [PORT] root@[IP]
```

### 2.2. Tạo file api_server.py

**Option A: Copy-paste (EASIEST)**
```bash
cd /root
nano api_server.py
# Copy toàn bộ nội dung từ file api_server_content.txt (trong repo) và paste vào
# Save: Ctrl+O, Enter, Ctrl+X
```

**Option B: Upload bằng SCP (từ local machine)**
```bash
# Từ máy local
scp -P [PORT] api_server.py root@[IP]:/root/
```

### 2.3. Cài đặt dependencies
```bash
cd /root
pip3 install flask flask-cors transformers torch sentencepiece tokenizers huggingface-hub gunicorn
```

### 2.4. Verify GPU
```bash
python3 -c "import torch; print(f'CUDA: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
```

### 2.5. Start API server với gunicorn
```bash
# Start trong screen để giữ chạy
screen -S api_server
cd /root
gunicorn -w 1 -b 0.0.0.0:5001 --timeout 300 api_server:app
# Press Ctrl+A then D để detach
```

### 2.6. Test local
```bash
# Trong screen hoặc terminal khác
curl http://localhost:5001/health
```

---

## 🌐 Step 3: Tạo Tunnel trên vast.ai Dashboard

1. **Vào vast.ai dashboard:**
   - Navigate to your instance
   - Click **"Tunnels"** ở sidebar trái

2. **Create tunnel:**
   - Trong ô "Enter target URL", nhập: `http://localhost:5001`
   - Click **"+ Create New Tunnel"**
   - Đợi 10-30 giây

3. **Copy Tunnel URL:**
   - Bạn sẽ thấy Tunnel URL dạng: `https://xxxxx.trycloudflare.com`
   - Click **"Copy URL"** để copy

---

## ✅ Step 4: Test Tunnel URL

**Từ máy local của bạn:**
```bash
# Test health endpoint
curl https://your-tunnel-url.trycloudflare.com/health

# Expected: JSON response với GPU info
```

**Nếu thấy JSON response → Tunnel hoạt động! ✅**

---

## 🔐 Step 5: Cập nhật Streamlit Cloud Secrets

1. **Vào Streamlit Cloud:**
   - Go to your app
   - Click **"Manage app"** (bottom right)
   - **Settings** → **Secrets**

2. **Cập nhật secret (TOML format):**
   ```toml
   GPU_API_ENDPOINT = "https://your-tunnel-url.trycloudflare.com"
   ```
   
   ⚠️ **Lưu ý:**
   - Dùng **Tunnel URL** (không phải direct IP)
   - Dùng **HTTPS** (không phải HTTP)
   - **Có dấu ngoặc kép**
   - Không cần port number

3. **Save và đợi:**
   - Click **Save**
   - Đợi ~1 phút để propagate
   - App sẽ tự động redeploy

---

## 🧪 Step 6: Test App

1. **Mở Streamlit app:**
   - Go to your app URL

2. **Test với Excel file:**
   - Upload Excel file
   - Process file
   - Kiểm tra tốc độ (GPU nhanh hơn nhiều)

3. **Verify GPU đang được dùng:**
   - GPU mode: ~1000-2000+ texts/sec
   - CPU mode: ~10-50 texts/sec

---

## 📝 Files cần cập nhật (nếu muốn document)

### File 1: `GPU_SETUP.md`
**Section cần update:**
```markdown
## 📋 Current GPU Configuration

**SSH Connection:**
```bash
ssh -p [NEW_PORT] root@[NEW_IP]
```

**API Endpoint:**
- IP: `[NEW_IP]`
- Port: `5001` (API server)
- Tunnel URL: `https://[NEW_TUNNEL_URL].trycloudflare.com`
```

### File 2: `api_server_content.txt` (nếu cần)
**Chỉ cần update comment ở đầu file:**
```python
# Setup:
# 1. SSH into vast.ai GPU server: ssh -p [NEW_PORT] root@[NEW_IP]
```

**Lưu ý:** File này chỉ để copy-paste, không cần sửa logic.

---

## 🔄 Quick Reference - Tất cả config cần thay đổi:

| Item | Old Value | New Value | Where to Update |
|------|-----------|-----------|-----------------|
| SSH Command | `ssh -p 54754 root@143.55.45.86` | `ssh -p [NEW_PORT] root@[NEW_IP]` | GPU_SETUP.md, notes |
| IP Address | `143.55.45.86` | `[NEW_IP]` | GPU_SETUP.md |
| Tunnel URL | `https://old-url.trycloudflare.com` | `https://new-url.trycloudflare.com` | **Streamlit Cloud Secrets** |
| Port | `5001` | `5001` (thường giữ nguyên) | N/A (nếu đổi port, update tunnel target) |

---

## ⚡ Quick Commands Cheat Sheet

### On GPU Server:
```bash
# Check API server running
ps aux | grep gunicorn

# View logs
screen -r api_server

# Restart API server
pkill -f gunicorn
screen -S api_server
cd /root
gunicorn -w 1 -b 0.0.0.0:5001 --timeout 300 api_server:app
```

### From Local Machine:
```bash
# Test tunnel
curl https://your-tunnel-url.trycloudflare.com/health

# Test prediction
curl -X POST https://your-tunnel-url.trycloudflare.com/predict \
  -H "Content-Type: application/json" \
  -d '{"texts": ["cotton fabric", "polyester yarn"]}'
```

---

## 🐛 Troubleshooting

### API server không start
```bash
# Check port đang dùng
lsof -i:5001
# Kill process nếu cần
lsof -ti:5001 | xargs kill -9
```

### Tunnel không hoạt động
- Verify tunnel đang "Active" trong vast.ai dashboard
- Check API server đang chạy: `curl http://localhost:5001/health`
- Recreate tunnel nếu cần

### Streamlit không kết nối được
- Verify secret format đúng (TOML, có quotes, HTTPS)
- Test tunnel URL từ browser: `https://your-tunnel-url.trycloudflare.com/health`
- Đợi 1-2 phút sau khi save secrets

---

## ✅ Success Checklist

Bạn biết setup thành công khi:
- ✅ `curl http://localhost:5001/health` trả về JSON (trên GPU server)
- ✅ `curl https://tunnel-url.trycloudflare.com/health` trả về JSON (từ local)
- ✅ Streamlit app process files nhanh (GPU speed)
- ✅ Không có connection timeout errors

---

## 📌 Important Notes

1. **Tunnel URL thay đổi mỗi lần tạo tunnel mới** → Phải update Streamlit Secrets
2. **Port 5001** là default, có thể đổi nếu cần (nhớ update tunnel target)
3. **API server phải chạy trong screen** để giữ chạy khi disconnect SSH
4. **Gunicorn** là production server, tốt hơn Flask dev server
5. **FP16** tự động enable nếu GPU hỗ trợ (Tesla V100 hỗ trợ)

---

## 🎯 TL;DR - 5 bước nhanh nhất:

1. **SSH vào GPU** → Upload `api_server.py` → `pip install` → Start với gunicorn
2. **Tạo Tunnel** trên vast.ai dashboard cho `http://localhost:5001`
3. **Copy Tunnel URL** (dạng `https://xxxxx.trycloudflare.com`)
4. **Update Streamlit Secrets**: `GPU_API_ENDPOINT = "https://xxxxx.trycloudflare.com"`
5. **Test app** → Done! ✅

---

**Thời gian ước tính:** 5-10 phút cho toàn bộ setup.

