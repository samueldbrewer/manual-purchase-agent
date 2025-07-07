# 🚀 Railway Quick Deploy Guide

## Current Status
- ✅ Railway CLI installed and authenticated
- ✅ Project created: `manual-purchase-agent`
- ✅ PostgreSQL database added
- ✅ All code prepared and committed to git
- ✅ Deployment files ready (Dockerfile, nixpacks.toml, etc.)

## 🎯 Quick Deploy Steps

### Option 1: Via Railway Dashboard (Easiest)

1. **Open your Railway project**:
   ```
   https://railway.com/project/2aaf026e-a3b5-49e9-9710-7df13ebec771
   ```

2. **Click the "+" button** → **"New Service"** → **"Empty Service"**

3. **Name it**: `web`

4. **Deploy your code**:
   - Click on the `web` service
   - Go to **Settings** → **Source**
   - Choose **"Local Directory"**
   - Drag and drop this folder

5. **Set Environment Variables** (in service settings):
   ```
   SERPAPI_KEY=7219228e748003a6e5394610456ef659f7c7884225b2df7fb0a890da61ad7f48
   OPENAI_API_KEY=your_openai_api_key_here
   SECRET_KEY=manual-purchase-agent-production-secret-key-2024
   ENCRYPTION_KEY=z2KGjtN24oYD3KHkkr8bpKsjyxJAN2SgAfgILqWnO54=
   ENABLE_REAL_PURCHASES=false
   ```

### Option 2: Via GitHub (Automated)

1. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/manual-purchase-agent.git
   git push -u origin main
   ```

2. **In Railway Dashboard**:
   - Click **"+"** → **"New Service"** → **"GitHub Repo"**
   - Connect your GitHub account
   - Select your repository

3. Railway will auto-deploy on every push!

### Option 3: Via CLI (After Creating Service)

1. After creating the `web` service in dashboard, run:
   ```bash
   ./railway_deploy_final.sh
   ```

## 🔗 Your App URLs

After deployment, your app will be available at:
- **Main URL**: `https://manual-purchase-agent-production.up.railway.app`
- **API Health**: `https://manual-purchase-agent-production.up.railway.app/api/system/health`
- **V3 Interface**: `https://manual-purchase-agent-production.up.railway.app/static/api-demo/v3/`

## 📊 Database

PostgreSQL is already provisioned. Railway will automatically inject the `DATABASE_URL` environment variable.

## 🎯 Ready Files

All these files are configured for Railway:
- ✅ `Dockerfile` - Optimized for Railway
- ✅ `requirements.txt` - Production dependencies
- ✅ `nixpacks.toml` - Build configuration
- ✅ `Procfile` - Process definition
- ✅ `railway.json` - Railway config
- ✅ `.gitignore` - Clean deployment

## 🚨 Important Notes

1. The simplified deployment removes Playwright to reduce complexity
2. Purchase automation features will need the recording service deployed separately
3. All other features (manual search, part resolution, supplier finding) work perfectly
4. Railway provides free hosting with generous limits

## 🎉 That's it!

Your Manual Purchase Agent will be live in minutes!