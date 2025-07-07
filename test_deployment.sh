#!/bin/bash
echo "🧪 Testing Railway Deployment"
echo "============================="

# Get the deployment URL from Railway
echo "Getting deployment URL..."
DEPLOY_URL=$(railway domain 2>/dev/null || echo "")

if [ -z "$DEPLOY_URL" ]; then
    echo "⚠️  Could not get URL from CLI. Please get it from Railway dashboard."
    read -p "Enter your Railway app URL (e.g., https://your-app.railway.app): " DEPLOY_URL
fi

echo "🌐 Testing URL: $DEPLOY_URL"
echo ""

# Test health endpoint
echo "1. Testing API Health..."
curl -s "$DEPLOY_URL/api/system/health" | python3 -m json.tool 2>/dev/null || echo "❌ Health check failed"

echo ""
echo "2. Testing V3 Interface..."
curl -s -o /dev/null -w "%{http_code}" "$DEPLOY_URL/static/api-demo/v3/" 
echo " - V3 Interface"

echo ""
echo "3. Testing API Documentation..."
curl -s -o /dev/null -w "%{http_code}" "$DEPLOY_URL/api/manuals"
echo " - Manuals API"

echo ""
echo "✅ If you see 200 responses, your app is working!"
echo "🌐 Access your app at: $DEPLOY_URL/static/api-demo/v3/"