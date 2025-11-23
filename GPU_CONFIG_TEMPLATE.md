# GPU Configuration Template

**Copy template này và điền thông tin GPU mới khi thuê:**

---

## 📋 GPU Information (Fill in when renting new GPU)

**SSH Connection:**
```bash
ssh -p [PORT] root@[IP]
```

**IP Address:** `[IP]`  
**SSH Port:** `[PORT]`  
**API Port:** `5001` (default, có thể đổi nếu cần)

**Proxy SSH (nếu có):**
```bash
ssh -p [PROXY_PORT] root@ssh9.vast.ai
```

**Tunnel URL:** `https://[TUNNEL_URL].trycloudflare.com`  
*(Lấy từ vast.ai dashboard → Tunnels sau khi tạo tunnel)*

---

## 🔧 Files to Update

### 1. `GPU_SETUP.md` - Section "Current GPU Configuration"
```markdown
**SSH Connection:**
```bash
ssh -p [PORT] root@[IP]
```

**API Endpoint:**
- IP: `[IP]`
- Port: `5001` (API server)
- Tunnel URL: `https://[TUNNEL_URL].trycloudflare.com`
```

### 2. `app.py` - Comment line 37
```python
# Current GPU: ssh -p [PORT] root@[IP]
```

### 3. `api_server.py` - Comment lines 6-7
```python
# Setup:
# 1. SSH into vast.ai GPU server: ssh -p [PORT] root@[IP]
```

### 4. **Streamlit Cloud Secrets** (MOST IMPORTANT!)
```toml
GPU_API_ENDPOINT = "https://[TUNNEL_URL].trycloudflare.com"
```

---

## ✅ Quick Checklist

- [ ] SSH vào GPU server thành công
- [ ] Upload/copy `api_server.py` lên server
- [ ] Cài dependencies: `pip3 install -r api_requirements.txt`
- [ ] Start API server: `gunicorn -w 1 -b 0.0.0.0:5001 --timeout 300 api_server:app`
- [ ] Test local: `curl http://localhost:5001/health`
- [ ] Tạo tunnel trên vast.ai dashboard cho `http://localhost:5001`
- [ ] Copy tunnel URL
- [ ] Update Streamlit Cloud Secrets với tunnel URL
- [ ] Test tunnel: `curl https://[TUNNEL_URL].trycloudflare.com/health`
- [ ] Test app với Excel file

---

## 📝 Notes

- Port mặc định là **5001** (không phải 5000)
- **BẮT BUỘC** dùng Tunnel URL, không dùng direct IP
- Tunnel URL format: `https://xxxxx.trycloudflare.com` (HTTPS, không có port)
- Sau khi update Secrets, đợi ~1 phút để propagate

