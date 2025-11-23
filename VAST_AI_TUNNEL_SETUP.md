# Vast.ai Tunnel Setup Guide

## Why Tunnels?

Vast.ai GPU instances are behind a firewall/NAT and don't have publicly accessible IPs. To expose your API server (running on port 5000) to the internet, you **MUST** use vast.ai's Tunnels feature.

## Step-by-Step Setup

### 1. Start API Server on GPU

```bash
# SSH into GPU server
ssh -p 54754 root@143.55.45.86

# Start API server (in screen to keep it running)
screen -S api_server
cd /root
python3 api_server.py
# Press Ctrl+A then D to detach
```

### 2. Create Tunnel in Vast.ai Dashboard

1. **Go to vast.ai dashboard:**
   - Navigate to your instance
   - Click **"Tunnels"** in the left sidebar (or "Tunnels (Open New Ports)")

2. **Create new tunnel:**
   - In the input field labeled "Enter target URL", enter:
     ```
     http://localhost:5000
     ```
   - Click **"+ Create New Tunnel"** button
   - Wait 10-30 seconds for tunnel to be created

3. **Copy Tunnel URL:**
   - You'll see a new row in the tunnels table
   - **Target URL**: `http://localhost:5000`
   - **Tunnel URL**: `https://xxxxx.trycloudflare.com` (this is what you need!)
   - Click **"Copy URL"** button to copy the tunnel URL

### 3. Test Tunnel

From your local machine, test if tunnel works:

```bash
# Replace with your actual tunnel URL
curl https://xxxxx.trycloudflare.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "device": "cuda",
  "gpu": {
    "device_name": "Tesla V100-SXM2-16GB",
    ...
  },
  "model": "aluha501/xlm-roberta-base-fabric"
}
```

### 4. Update Streamlit Cloud Secrets

1. Go to **Streamlit Cloud** → Your app → **Settings** → **Secrets**

2. Update the secret (TOML format):
   ```toml
   GPU_API_ENDPOINT = "https://xxxxx.trycloudflare.com"
   ```
   ⚠️ **Important**: Use the Tunnel URL, NOT the direct IP!

3. Click **Save**

4. Wait ~1 minute for changes to propagate

5. App will automatically redeploy

### 5. Verify It Works

1. Open your Streamlit app
2. Upload an Excel file and process it
3. Check if it's using GPU (should be faster, no error messages)

## Troubleshooting

### Tunnel URL not working

**Check 1: API server is running**
```bash
# On GPU server
ps aux | grep api_server
curl http://localhost:5000/health
```

**Check 2: Tunnel is active**
- Go to vast.ai dashboard → Tunnels
- Verify tunnel shows "Active" or green status
- If not, delete and recreate the tunnel

**Check 3: Correct URL format**
- ✅ Correct: `https://xxxxx.trycloudflare.com`
- ❌ Wrong: `http://xxxxx.trycloudflare.com` (missing 's')
- ❌ Wrong: `https://xxxxx.trycloudflare.com:5000` (don't add port)

### Connection timeout in Streamlit

1. **Verify tunnel URL in secrets:**
   - Check Streamlit Cloud → Settings → Secrets
   - Ensure it's the tunnel URL, not direct IP

2. **Test tunnel from browser:**
   - Open `https://xxxxx.trycloudflare.com/health` in browser
   - Should see JSON response

3. **Check API server logs:**
   ```bash
   # On GPU server
   screen -r api_server
   # Check for any errors
   ```

### Tunnel keeps disconnecting

- Tunnels may disconnect if instance is idle
- Recreate tunnel if needed
- Consider using a process manager (systemd, supervisor) to keep API server running

## Example Tunnel Configuration

```
Target URL: http://localhost:5000
Tunnel URL: https://motels-stronger-fell-pasta.trycloudflare.com
Status: Active
```

**Streamlit Cloud Secret:**
```toml
GPU_API_ENDPOINT = "https://motels-stronger-fell-pasta.trycloudflare.com"
```

## Notes

- Tunnel URLs are HTTPS (secure)
- No need to configure firewall or port forwarding
- Tunnels work from anywhere (Streamlit Cloud, your local machine, etc.)
- Tunnel URLs may change if you recreate them - update Streamlit secrets accordingly

