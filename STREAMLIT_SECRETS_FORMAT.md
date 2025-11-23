# Streamlit Cloud Secrets Format Guide

## TOML Format for Secrets

Streamlit Cloud uses TOML format for secrets. According to the [TOML specification](https://toml.io/en/v1.0.0), here's the correct format:

### Correct Format

```toml
GPU_API_ENDPOINT = "http://143.55.45.86:5000"
```

### Key Points:

1. **Use quotes for string values**: The URL must be in double quotes
2. **Spaces around `=` are optional**: Both `key = "value"` and `key="value"` work
3. **Case-sensitive**: Keys are case-sensitive
4. **No trailing commas**: Don't add commas after the last entry

### Example Secrets Configuration:

```toml
# GPU API Configuration
GPU_API_ENDPOINT = "http://143.55.45.86:5000"

# Optional: Other environment variables
MODEL_NAME = "aluha501/xlm-roberta-base-fabric"
MAX_LENGTH = "128"
```

### How to Set in Streamlit Cloud:

1. Go to your app on Streamlit Cloud
2. Click "Manage app" (bottom right)
3. Go to "Settings" → "Secrets"
4. Paste the TOML format above
5. Click "Save"
6. Wait ~1 minute for changes to propagate
7. The app will automatically redeploy

### Common Mistakes:

❌ **Wrong:**
```toml
GPU_API_ENDPOINT=http://143.55.45.86:5000  # Missing quotes
GPU_API_ENDPOINT = 'http://143.55.45.86:5000'  # Single quotes (works but double quotes preferred)
GPU_API_ENDPOINT = http://143.55.45.86:5000  # No quotes
```

✅ **Correct:**
```toml
GPU_API_ENDPOINT = "http://143.55.45.86:5000"
```

### Testing:

After setting the secret, check the app logs to see if it's being read correctly. The app will show:
- "🔧 GPU API endpoint configured: [host:port]" if configured
- "ℹ️ GPU API endpoint not configured - using CPU mode" if not configured

### Troubleshooting:

If you see "GPU API connection timeout":
1. Verify the secret is set correctly (check format above)
2. Check if the GPU server is running: `curl http://143.55.45.86:5000/health`
3. Check vast.ai network settings (port forwarding, firewall)
4. Verify the IP and port are correct

