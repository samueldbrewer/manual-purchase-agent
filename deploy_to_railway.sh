#!/bin/bash
echo "🚀 Deploying Manual Purchase Agent to Railway..."

# Check if logged in
if ! railway whoami > /dev/null 2>&1; then
    echo "❌ Not logged in to Railway. Please run: railway login"
    exit 1
fi

# Show current project
echo "📋 Current project status:"
railway status

echo ""
echo "🌐 Railway Dashboard URL:"
echo "https://railway.com/project/2aaf026e-a3b5-49e9-9710-7df13ebec771"

echo ""
echo "🚀 To complete deployment, please:"
echo "1. Go to the Railway dashboard URL above"
echo "2. Click 'Deploy from GitHub repo' or 'New Service'"
echo "3. Upload your project folder or connect to GitHub"
echo "4. Set environment variables:"
echo "   - SERPAPI_KEY=your_serpapi_key"
echo "   - OPENAI_API_KEY=your_openai_key"
echo "   - SECRET_KEY=manual-purchase-agent-production-secret-key-2024"
echo "   - ENCRYPTION_KEY=z2KGjtN24oYD3KHkkr8bpKsjyxJAN2SgAfgILqWnO54="
echo "   - ENABLE_REAL_PURCHASES=false"
echo ""
echo "5. Add PostgreSQL database service"
echo "6. Deploy!"

echo ""
echo "📁 Files ready for deployment:"
echo "   ✅ Dockerfile (simplified for Railway)"
echo "   ✅ requirements.txt (Railway compatible)"
echo "   ✅ Procfile"
echo "   ✅ railway.json"
echo "   ✅ RAILWAY_DEPLOYMENT.md"

echo ""
echo "🔗 After deployment, your app will be available at:"
echo "   https://manual-purchase-agent-production.up.railway.app"
echo "   (or similar Railway-provided URL)"