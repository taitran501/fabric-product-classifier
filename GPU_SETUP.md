# GPU Setup Guide - Vast.ai Integration

## 📋 Current GPU Configuration

**SSH Connection:**
```bash
# Direct connection
ssh -p 54754 root@143.55.45.86 -L 8080:localhost:8080

# Proxy connection (if direct doesn't work)
ssh -p 21569 root@ssh9.vast.ai -L 8080:localhost:8080
```

**API Endpoint:**
- IP: `143.55.45.86`
- Port: `5000` (API server)
- Port Forwarding: `8080:localhost:8080` (for web access if needed)
- Proxy SSH: `ssh9.vast.ai:21569` (alternative connection method)

**Streamlit Cloud Environment Variable:**
```
GPU_API_ENDPOINT=http://143.55.45.86:5000
```

---

## 🚀 Setup Instructions

### Step 1: Connect to GPU Server

```bash
ssh -p 54754 root@143.55.45.86
```

### Step 2: Install Dependencies

```bash
# Update system
apt update && apt upgrade -y

# Install Python and pip
apt install -y python3 python3-pip

# Install required packages
pip3 install flask flask-cors transformers torch torchvision

# Verify GPU
python3 -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
```

### Step 3: Upload API Server File

**Option A: Using SCP (from local machine) - Nếu gặp lỗi, dùng Option B**
```bash
# From your local machine (WSL/Linux)
scp -P 54754 api_server.py root@143.55.45.86:/root/

# Hoặc từ Windows PowerShell
scp -P 54754 api_server.py root@143.55.45.86:/root/
```

**Option B: Create file directly on server (RECOMMENDED nếu SCP lỗi)**
```bash
# 1. SSH vào server
ssh -p 54754 root@143.55.45.86

# 2. Tạo file
nano /root/api_server.py

# 3. Copy toàn bộ nội dung từ file api_server_content.txt (trong repo) và paste vào
# 4. Save: Ctrl+O, Enter, Ctrl+X để exit

# Hoặc dùng cat để tạo file nhanh (copy nội dung từ api_server_content.txt):
cat > /root/api_server.py << 'ENDOFFILE'
[paste content here]
ENDOFFILE
```

**Option C: Copy-paste script (EASIEST)**
```bash
# SSH vào server, sau đó chạy:
cd /root
nano api_server.py
# Mở file api_server_content.txt trên máy local, copy toàn bộ, paste vào nano
# Save: Ctrl+O, Enter, Ctrl+X
```

### Step 4: Run API Server

```bash
# Run directly
python3 api_server.py

# Or run in background with nohup
nohup python3 api_server.py > api_server.log 2>&1 &

# Or use screen (recommended)
screen -S api_server
python3 api_server.py
# Press Ctrl+A then D to detach
# Reattach with: screen -r api_server
```

### Step 5: Test API

```bash
# Health check
curl http://localhost:5000/health

# Test prediction
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"texts": ["cotton fabric", "polyester yarn"]}'
```

### Step 6: Configure Firewall (if needed)

```bash
# Allow port 5000
ufw allow 5000/tcp
# Or if using iptables
iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
```

---

## 🔄 When Renting a New GPU

### 1. Update SSH Connection Info

**File: `GPU_SETUP.md`**
- Update SSH command with new IP and port
- Update API endpoint IP

**File: `api_server.py`**
- No changes needed (uses 0.0.0.0 to listen on all interfaces)

### 2. Update Streamlit Cloud Environment Variable

1. Go to Streamlit Cloud dashboard
2. Select your app
3. Go to Settings → Secrets
4. Update `GPU_API_ENDPOINT`:
   ```
   GPU_API_ENDPOINT=http://NEW_IP:5000
   ```
5. Redeploy app

### 3. Update This File

Update the "Current GPU Configuration" section above with:
- New SSH command
- New IP address
- New port (if different)

---

## 🧪 Testing

### Test from Local Machine

```bash
# Test health endpoint
curl http://143.55.45.86:5000/health

# Test prediction
curl -X POST http://143.55.45.86:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"texts": ["cotton fabric", "polyester yarn thread", "fabric label"]}'
```

### Test from Streamlit App

1. Upload Excel file
2. Check browser console for API calls
3. Verify predictions are returned quickly (GPU should be much faster)

---

## 📊 Performance Comparison

**Expected speeds:**
- CPU (Streamlit Cloud): ~10-50 texts/sec
- GPU (vast.ai): ~500-2000 texts/sec (depending on GPU)

**Cost:**
- vast.ai GPU: ~$0.10-0.50/hour (pay only when running)
- Streamlit Cloud: Free (but slower)

---

## 🛠️ Troubleshooting

### API Server Not Accessible

1. Check if server is running:
   ```bash
   ps aux | grep api_server
   ```

2. Check firewall:
   ```bash
   ufw status
   iptables -L -n
   ```

3. Test locally on server:
   ```bash
   curl http://localhost:5000/health
   ```

### Connection Timeout

1. Verify IP address is correct
2. Check if port 5000 is open
3. Try using port forwarding:
   ```bash
   ssh -p 54754 root@143.55.45.86 -L 5000:localhost:5000
   ```
   Then access via: `http://localhost:5000`

### Model Loading Errors

1. Check GPU memory:
   ```bash
   nvidia-smi
   ```

2. Reduce batch size in `api_server.py` if out of memory

3. Check disk space:
   ```bash
   df -h
   ```

---

## 📝 Notes

- API server uses port 5000 by default
- If port 5000 is blocked, change `API_PORT` in `api_server.py`
- Keep API server running in screen/tmux for persistence
- Monitor GPU usage: `watch -n 1 nvidia-smi`
- Check API logs: `tail -f api_server.log` (if using nohup)

---

## 🔐 Security Notes

- Current setup allows access from any IP (0.0.0.0)
- For production, consider:
  - Adding authentication
  - Restricting IP access
  - Using HTTPS
  - Rate limiting

