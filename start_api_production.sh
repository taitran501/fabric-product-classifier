#!/bin/bash
# Production startup script for API server using gunicorn
# Run this instead of python3 api_server.py for production

PORT=${1:-5001}  # Default port 5001, or pass as argument

echo "🚀 Starting API server in PRODUCTION mode with gunicorn..."
echo "📡 Port: $PORT"
echo ""

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo "❌ gunicorn not found. Installing..."
    pip3 install gunicorn
fi

# Start with gunicorn
# -w 1: 1 worker (sufficient for GPU API, avoids GPU memory conflicts)
# -b: bind address
# --timeout: request timeout (5 minutes for large batches)
# --workers: number of worker processes
gunicorn -w 1 \
         -b 0.0.0.0:$PORT \
         --timeout 300 \
         --access-logfile - \
         --error-logfile - \
         api_server:app

