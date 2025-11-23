#!/bin/bash
# Script to upload files to vast.ai GPU server
# Usage: ./upload_to_gpu.sh

GPU_IP="143.55.45.86"
GPU_PORT="54754"
GPU_USER="root"
REMOTE_DIR="/root"

echo "📤 Uploading files to GPU server..."
echo "Server: $GPU_USER@$GPU_IP:$GPU_PORT"

# Accept SSH fingerprint automatically
ssh-keyscan -p $GPU_PORT $GPU_IP >> ~/.ssh/known_hosts 2>/dev/null

# Upload files
echo "Uploading api_server.py..."
scp -P $GPU_PORT api_server.py $GPU_USER@$GPU_IP:$REMOTE_DIR/

echo "Uploading api_requirements.txt..."
scp -P $GPU_PORT api_requirements.txt $GPU_USER@$GPU_IP:$REMOTE_DIR/

echo "✅ Upload complete!"
echo ""
echo "Next steps:"
echo "1. SSH into server: ssh -p $GPU_PORT $GPU_USER@$GPU_IP"
echo "2. Install dependencies: pip3 install -r $REMOTE_DIR/api_requirements.txt"
echo "3. Run API server: python3 $REMOTE_DIR/api_server.py"

