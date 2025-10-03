#!/bin/bash

# Start MoneySplit Backend API

echo "🚀 Starting MoneySplit Backend API..."
echo "📍 API will be available at: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

python3 -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
