#!/bin/bash
# Setup script for GPU API server on vast.ai
# Run this on the GPU server after SSH connection

echo "🚀 Setting up GPU API Server for Fabric Product Classifier"
echo "============================================================"

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install Python and pip
echo "🐍 Installing Python..."
apt install -y python3 python3-pip

# Install required packages
echo "📚 Installing Python packages..."
pip3 install flask flask-cors transformers torch torchvision sentencepiece tokenizers huggingface-hub

# Verify GPU
echo "🎮 Checking GPU availability..."
python3 -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"

# Check if api_server.py exists
if [ ! -f "api_server.py" ]; then
    echo "⚠️  api_server.py not found in current directory"
    echo "Please upload api_server.py to the server first"
    exit 1
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the API server:"
echo "  python3 api_server.py"
echo ""
echo "Or run in background with screen:"
echo "  screen -S api_server"
echo "  python3 api_server.py"
echo "  (Press Ctrl+A then D to detach)"
echo ""

