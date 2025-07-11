#!/bin/bash

# API Test Runner for Manual Purchase Agent v15.6
# This script starts the Flask service and runs comprehensive API tests

PROJECT_DIR="/Users/sambrewer/Desktop/Data Services/Data Services - Fresh Claude/manual-purchase-agent_20250513_125500_v15.6"

echo "=========================================="
echo "  Manual Purchase Agent API Test Runner"
echo "=========================================="

cd "$PROJECT_DIR" || {
    echo "❌ Failed to navigate to project directory"
    exit 1
}

# Check if service is already running
if lsof -i:7777 >/dev/null 2>&1; then
    echo "✅ Flask service already running on port 7777"
    STARTED_SERVICE=false
else
    echo "🚀 Starting Flask service..."
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "❌ Virtual environment not found. Please create it first:"
        echo "   python3 -m venv venv"
        echo "   source venv/bin/activate"
        echo "   pip install -r requirements.txt"
        exit 1
    fi
    
    # Activate virtual environment and start service
    source venv/bin/activate
    export PYTHONPATH="$PROJECT_DIR"
    
    # Start Flask in background
    python app.py > flask_test.log 2>&1 &
    FLASK_PID=$!
    STARTED_SERVICE=true
    
    echo "⏳ Waiting for service to start..."
    sleep 5
    
    # Check if service started successfully
    if ! lsof -i:7777 >/dev/null 2>&1; then
        echo "❌ Failed to start Flask service. Check flask_test.log for errors."
        exit 1
    fi
    
    echo "✅ Flask service started successfully (PID: $FLASK_PID)"
fi

echo ""
echo "🧪 Running API tests..."
echo ""

# Run the comprehensive API tests
python test_api_comprehensive.py
TEST_RESULT=$?

# Cleanup: Stop service if we started it
if [ "$STARTED_SERVICE" = true ]; then
    echo ""
    echo "🛑 Stopping Flask service..."
    if [ -n "$FLASK_PID" ]; then
        kill $FLASK_PID 2>/dev/null || true
    fi
    # Also kill by port in case PID doesn't work
    lsof -ti:7777 | xargs kill -9 2>/dev/null || true
    echo "✅ Service stopped"
fi

echo ""
echo "=========================================="
if [ $TEST_RESULT -eq 0 ]; then
    echo "🎉 All tests completed successfully!"
else
    echo "⚠️  Some tests failed. Check output above."
fi
echo "=========================================="

exit $TEST_RESULT