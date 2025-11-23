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
- **Tunnel URL (RECOMMENDED)**: Use vast.ai Tunnels feature to expose port 5000
- Proxy SSH: `ssh9.vast.ai:21569` (alternative connection method)

**Streamlit Cloud Secrets (TOML format):**
```toml
# Option 1: Using Tunnel URL (RECOMMENDED - works from anywhere)
GPU_API_ENDPOINT = "https://your-tunnel-url.trycloudflare.com"

# Option 2: Direct IP (may not work due to firewall)
GPU_API_ENDPOINT = "http://143.55.45.86:5000"
```

**Important Notes:**
- Use TOML format in Streamlit Cloud Secrets (see https://toml.io/en/v1.0.0)
- The value must be in quotes (string format)
- No spaces around the `=` sign is required, but `key = "value"` format is recommended
- After saving, wait ~1 minute for changes to propagate

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

### Step 6: Create Tunnel to Expose API Server (REQUIRED)

**IMPORTANT:** Vast.ai instances are behind a firewall. You MUST use the Tunnels feature to expose your API server.

**Using Vast.ai Tunnels (RECOMMENDED - EASIEST):**

1. **In vast.ai dashboard:**
   - Go to your instance
   - Click on "Tunnels" in the left sidebar (or "Tunnels (Open New Ports)")
   
2. **Create new tunnel:**
   - In the "Enter target URL" field, enter: `http://localhost:5000`
   - Click "+ Create New Tunnel"
   - Wait a few seconds for tunnel to be created
   
3. **Copy Tunnel URL:**
   - You'll get a URL like: `https://xxxxx.trycloudflare.com`
   - Click "Copy URL" to copy it
   
4. **Update Streamlit Cloud Secrets:**
   - Go to Streamlit Cloud → Settings → Secrets
   - Update `GPU_API_ENDPOINT`:
     ```toml
     GPU_API_ENDPOINT = "https://xxxxx.trycloudflare.com"
     ```
   - Save and wait ~1 minute for changes to propagate

5. **Verify tunnel is working:**
   ```bash
   # Test from your local machine
   curl https://xxxxx.trycloudflare.com/health
   ```

**Why Tunnels?**
- Vast.ai instances don't have public IPs accessible from outside
- Tunnels create a secure HTTPS endpoint that works from anywhere
- No need to configure firewall or port forwarding manually
- Automatically handles SSL/TLS

**Alternative: Direct IP (may not work)**
If you want to try direct IP (usually won't work due to firewall):
```toml
GPU_API_ENDPOINT = "http://143.55.45.86:5000"
```
But this will likely timeout because the instance is behind NAT/firewall.

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

1. **Check if server is running:**
   ```bash
   ps aux | grep api_server
   ```

2. **Check if port is listening:**
   ```bash
   netstat -tuln | grep 5000
   # Or
   ss -tuln | grep 5000
   ```

3. **Test locally on server:**
   ```bash
   curl http://localhost:5000/health
   ```

4. **Check vast.ai Network Settings:**
   - Go to vast.ai dashboard → Your instance
   - Check "Ports" or "Network" section
   - Ensure port 5000 is forwarded/exposed
   - Check if instance has public IP or needs port forwarding

5. **Test from outside (if you have public IP):**
   ```bash
   # From your local machine
   curl http://143.55.45.86:5000/health
   ```

6. **If connection timeout:**
   - Vast.ai instances are often behind NAT/firewall
   - You may need to use vast.ai's port forwarding feature
   - Or set up SSH tunnel through proxy: `ssh -p 21569 root@ssh9.vast.ai -L 5000:localhost:5000`

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

