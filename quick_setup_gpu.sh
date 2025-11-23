#!/bin/bash
# Quick setup script - Run this ON the GPU server after SSH connection
# Copy and paste this entire script into the GPU server terminal

echo "🚀 Quick Setup for GPU API Server"
echo "=================================="

# Create api_requirements.txt
cat > /root/api_requirements.txt << 'EOF'
flask>=2.3.0
flask-cors>=4.0.0
transformers>=4.30.0
torch>=2.0.0
sentencepiece>=0.1.99
tokenizers>=0.13.0
huggingface-hub>=0.16.0
EOF

echo "✅ Created api_requirements.txt"

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install flask flask-cors transformers torch sentencepiece tokenizers huggingface-hub

echo ""
echo "✅ Dependencies installed!"
echo ""
echo "⚠️  Next: Create api_server.py file"
echo "Run: nano /root/api_server.py"
echo "Then copy-paste the content from api_server.py in your repo"

