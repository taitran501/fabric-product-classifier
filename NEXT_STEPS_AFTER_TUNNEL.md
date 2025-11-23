# Next Steps After Creating Tunnel and Starting Gunicorn

## ✅ Checklist - What You've Done:
- [x] API server running with gunicorn on port 5001
- [x] Tunnel created in vast.ai dashboard
- [x] Tunnel URL copied

## 📋 Next Steps:

### Step 1: Test Tunnel URL

**From your local machine:**
```bash
# Replace with your actual tunnel URL
curl https://your-tunnel-url.trycloudflare.com/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "device": "cuda",
  "gpu": {
    "device_name": "Tesla V100-SXM2-16GB",
    "memory_allocated": "X.XX GB",
    "memory_reserved": "X.XX GB"
  },
  "model": "aluha501/xlm-roberta-base-fabric"
}
```

✅ **If you see this response → Tunnel is working!**

### Step 2: Update Streamlit Cloud Secrets

1. **Go to Streamlit Cloud:**
   - Navigate to your app
   - Click **"Manage app"** (bottom right)
   - Go to **"Settings"** → **"Secrets"**

2. **Update the secret:**
   ```toml
   GPU_API_ENDPOINT = "https://your-tunnel-url.trycloudflare.com"
   ```
   
   ⚠️ **Important:**
   - Use the **Tunnel URL** (not direct IP)
   - Must be **HTTPS** (not HTTP)
   - No port number needed (tunnel handles it)
   - Use **quotes** around the URL

3. **Save and wait:**
   - Click **"Save"**
   - Wait ~1 minute for changes to propagate
   - App will automatically redeploy

### Step 3: Verify in Streamlit App

1. **Open your Streamlit app:**
   - Go to your app URL (e.g., `https://your-app.streamlit.app`)

2. **Check if GPU is being used:**
   - Upload an Excel file
   - Process it
   - GPU should be much faster than CPU
   - No error messages about GPU connection

3. **Monitor performance:**
   - CPU mode: ~10-50 texts/sec
   - GPU mode: ~500-2000 texts/sec (much faster!)

### Step 4: Monitor API Server (Optional)

**Check API server logs:**
```bash
# SSH into GPU server
ssh -p 54754 root@143.55.45.86

# Reattach to screen
screen -r api_server

# You'll see request logs when Streamlit app calls the API
# Press Ctrl+A then D to detach again
```

**Check if gunicorn is running:**
```bash
ps aux | grep gunicorn
```

## 🧪 Testing Commands

### Test Health Endpoint:
```bash
curl https://your-tunnel-url.trycloudflare.com/health
```

### Test Prediction:
```bash
curl -X POST https://your-tunnel-url.trycloudflare.com/predict \
  -H "Content-Type: application/json" \
  -d '{"texts": ["cotton fabric", "polyester yarn", "fabric label"]}'
```

**Expected response:**
```json
{
  "predictions": ["vải", "sợi", "phụ_trợ"],
  "count": 3,
  "processing_time": 0.XX
}
```

## 🔧 Troubleshooting

### Tunnel URL not working:
1. Check tunnel is active in vast.ai dashboard
2. Verify API server is running: `ps aux | grep gunicorn`
3. Test locally on server: `curl http://localhost:5001/health`

### Streamlit still shows CPU fallback:
1. Verify secret is saved correctly (check TOML format)
2. Wait 1-2 minutes for propagation
3. Check browser console for errors
4. Verify tunnel URL is accessible: `curl https://your-tunnel-url.trycloudflare.com/health`

### Slow performance:
- If still slow, GPU might not be used
- Check API server logs for requests
- Verify tunnel URL in secrets matches actual tunnel URL

## ✅ Success Indicators

You'll know it's working when:
- ✅ Tunnel URL returns health check successfully
- ✅ Streamlit app processes files quickly (GPU speed)
- ✅ No connection timeout errors
- ✅ API server logs show incoming requests

## 📝 Notes

- **Tunnel URLs may change** if you recreate the tunnel - update secrets accordingly
- **Keep gunicorn running** in screen session
- **Monitor GPU usage** in vast.ai dashboard
- **Cost**: You're only charged when GPU instance is running

