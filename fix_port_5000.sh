#!/bin/bash
# Script to fix "Address already in use" error on port 5000
# Run this on the GPU server

echo "🔍 Checking what's using port 5000..."

# Find process using port 5000
PID=$(lsof -ti:5000 2>/dev/null || fuser 5000/tcp 2>/dev/null | awk '{print $1}')

if [ -z "$PID" ]; then
    echo "❌ Could not find process using port 5000"
    echo "Trying alternative method..."
    PID=$(netstat -tuln | grep :5000 | awk '{print $7}' | cut -d'/' -f1 | head -1)
fi

if [ -n "$PID" ]; then
    echo "✅ Found process: PID $PID"
    echo "Process details:"
    ps aux | grep $PID | grep -v grep
    
    echo ""
    read -p "Kill this process? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kill -9 $PID
        echo "✅ Process killed"
        sleep 2
        echo "🚀 You can now start api_server.py"
    else
        echo "⚠️ Process not killed. Use a different port or kill manually."
    fi
else
    echo "⚠️ No process found using port 5000"
    echo "Try checking with: netstat -tuln | grep 5000"
fi

