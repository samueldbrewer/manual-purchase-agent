#!/bin/bash
echo "🚀 Final Railway Deployment"
echo "========================="

# Link to the web service
echo "Linking to web service..."
railway link --service web

# Set environment variables
echo "Setting environment variables..."
railway variables --set "FLASK_ENV=production"
railway variables --set "SECRET_KEY=manual-purchase-agent-production-secret-key-2024"
railway variables --set "ENCRYPTION_KEY=z2KGjtN24oYD3KHkkr8bpKsjyxJAN2SgAfgILqWnO54="
railway variables --set "ENABLE_REAL_PURCHASES=false"
railway variables --set "PYTHONPATH=/app"

echo ""
echo "⚠️  Don't forget to add these in Railway dashboard:"
echo "SERPAPI_KEY=your_key"
echo "OPENAI_API_KEY=your_key"

# Deploy
echo ""
echo "Deploying..."
railway up

echo ""
echo "✅ Deployment complete!"
railway domain
