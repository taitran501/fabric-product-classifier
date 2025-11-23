"""
GPU API Server for Fabric Product Classifier
Deploy this on vast.ai GPU server to handle predictions with GPU acceleration.

Setup:
1. SSH into vast.ai GPU server: ssh -p 54754 root@143.55.45.86
2. Install dependencies: pip install flask transformers torch
3. Run: python api_server.py
4. API will be available at: http://143.55.45.86:5000

Note: If you rent a new GPU, update:
- IP address in this file (API_HOST)
- IP address in Streamlit Cloud environment variable (GPU_API_ENDPOINT)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import os
import time

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from Streamlit Cloud

# Configuration
MODEL_NAME = "aluha501/xlm-roberta-base-fabric"
VALID_LABELS = ["vải", "sợi", "xơ", "quần/áo", "phụ_trợ"]
MAX_LENGTH = 128
BATCH_SIZE = 128  # Larger batch size for GPU (increased for better throughput)
API_HOST = "0.0.0.0"  # Listen on all interfaces
API_PORT = 5000  # API port (use port forwarding if needed)

# Check GPU availability
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"🚀 Initializing API Server...")
print(f"📱 Using device: {device}")
if torch.cuda.is_available():
    print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
    print(f"💾 GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")

# Load model on GPU
print(f"📥 Loading model: {MODEL_NAME}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
model = model.to(device)
model.eval()

# Use half precision (FP16) for faster inference if GPU supports it
if torch.cuda.is_available() and torch.cuda.is_bf16_supported():
    try:
        model = model.half()  # Use FP16 for faster inference
        print(f"✅ Model loaded with FP16 precision for faster inference")
    except Exception as e:
        print(f"⚠️ Could not use FP16, using FP32: {e}")
else:
    print(f"✅ Model loaded successfully on {device}")

@app.route('/predict', methods=['POST'])
def predict():
    """Predict labels for a batch of texts"""
    try:
        data = request.json
        texts = data.get('texts', [])
        
        if not texts:
            return jsonify({'error': 'No texts provided'}), 400
        
        if not isinstance(texts, list):
            return jsonify({'error': 'Texts must be a list'}), 400
        
        print(f"📊 Received {len(texts)} texts for prediction")
        start_time = time.time()
        
        predictions = []
        total_batches = (len(texts) + BATCH_SIZE - 1) // BATCH_SIZE
        
        for batch_idx, i in enumerate(range(0, len(texts), BATCH_SIZE), 1):
            batch_texts = texts[i:i+BATCH_SIZE]
            
            # Tokenize
            inputs = tokenizer(
                batch_texts,
                padding="max_length",
                truncation=True,
                max_length=MAX_LENGTH,
                return_tensors="pt"
            )
            
            # Move to GPU
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            # Predict
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
                probabilities = torch.nn.functional.softmax(logits, dim=-1)
                pred_ids = torch.argmax(probabilities, dim=-1).cpu().numpy()
            
            batch_predictions = [VALID_LABELS[pred_id] for pred_id in pred_ids]
            predictions.extend(batch_predictions)
            
            if batch_idx % 10 == 0:
                print(f"  Processed {batch_idx}/{total_batches} batches ({len(predictions)}/{len(texts)} texts)")
        
        elapsed_time = time.time() - start_time
        print(f"✅ Completed prediction in {elapsed_time:.2f}s ({len(texts)/elapsed_time:.1f} texts/sec)")
        
        return jsonify({
            'predictions': predictions,
            'count': len(predictions),
            'processing_time': round(elapsed_time, 2)
        })
    
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback.print_exc()
        return jsonify({'error': error_msg}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    gpu_info = {}
    if torch.cuda.is_available():
        gpu_info = {
            'device_name': torch.cuda.get_device_name(0),
            'memory_allocated': f"{torch.cuda.memory_allocated(0) / 1024**3:.2f} GB",
            'memory_reserved': f"{torch.cuda.memory_reserved(0) / 1024**3:.2f} GB"
        }
    
    return jsonify({
        'status': 'healthy',
        'device': str(device),
        'gpu': gpu_info,
        'model': MODEL_NAME
    })

@app.route('/', methods=['GET'])
def index():
    """API information"""
    return jsonify({
        'service': 'Fabric Product Classifier GPU API',
        'version': '1.0',
        'endpoints': {
            '/health': 'GET - Health check',
            '/predict': 'POST - Predict labels (send {"texts": ["text1", "text2", ...]})'
        },
        'device': str(device)
    })

if __name__ == '__main__':
    print(f"\n🌐 Starting API server on {API_HOST}:{API_PORT}")
    print(f"📡 API endpoint: http://{API_HOST}:{API_PORT}")
    print(f"💡 Health check: http://{API_HOST}:{API_PORT}/health")
    print(f"🔗 Predict endpoint: http://{API_HOST}:{API_PORT}/predict")
    print("\n⚠️  Note: If using port forwarding, access via forwarded port")
    print("=" * 60)
    
    # Check if port is already in use
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((API_HOST, API_PORT))
    sock.close()
    
    if result == 0:
        print(f"\n❌ ERROR: Port {API_PORT} is already in use!")
        print("💡 Solutions:")
        print("   1. Kill the process using port 5000:")
        print("      lsof -ti:5000 | xargs kill -9")
        print("      # Or")
        print("      fuser -k 5000/tcp")
        print("   2. Or use a different port by setting API_PORT in the script")
        print("\n🔍 To find what's using the port:")
        print("   lsof -i:5000")
        print("   # Or")
        print("   netstat -tuln | grep 5000")
        exit(1)
    
    # Production mode: Use gunicorn if available, otherwise use Flask dev server
    import sys
    if 'gunicorn' in sys.modules or 'gunicorn' in str(sys.argv):
        # Running with gunicorn
        pass
    else:
        # Development mode - Flask dev server
        print("\n⚠️  Running in development mode (Flask dev server)")
        print("💡 For production, use: gunicorn -w 1 -b 0.0.0.0:5001 api_server:app")
        print("=" * 60)
        app.run(host=API_HOST, port=API_PORT, threaded=True)

