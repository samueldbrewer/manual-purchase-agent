# Railway Deployment Guide

## Quick Deployment Steps

1. **Authenticate with Railway** (user must do this):
   ```bash
   railway login
   ```

2. **Link to your project**:
   ```bash
   railway link 950b76de-fe7f-4376-841e-0bc90acb31eb
   ```

3. **Set up environment variables in Railway dashboard**:
   - `SERPAPI_KEY`: Your SerpAPI key
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `SECRET_KEY`: Generate a secure secret key
   - `ENCRYPTION_KEY`: z2KGjtN24oYD3KHkkr8bpKsjyxJAN2SgAfgILqWnO54=
   - `DATABASE_URI`: Railway will provide PostgreSQL URL
   - `ENABLE_REAL_PURCHASES`: false

4. **Deploy**:
   ```bash
   railway up
   ```

## Files Created for Railway

- `railway.json`: Railway configuration
- `Procfile`: Process definition for Railway
- `start_railway.sh`: Startup script with initialization
- `.env.production`: Environment template
- `RAILWAY_DEPLOYMENT.md`: This guide

## Database Setup

Railway will automatically provision a PostgreSQL database. The DATABASE_URI will be available as an environment variable.

## Domain

After deployment, Railway will provide a URL like:
`https://your-app-name.railway.app`

## Monitoring

- Check logs: `railway logs`
- Check status: `railway status`
- Open dashboard: `railway open`

## Environment Variables Needed

Set these in the Railway dashboard:

```
SERPAPI_KEY=your_serpapi_key_here
OPENAI_API_KEY=your_openai_key_here
SECRET_KEY=your-secure-secret-key-here
ENCRYPTION_KEY=z2KGjtN24oYD3KHkkr8bpKsjyxJAN2SgAfgILqWnO54=
ENABLE_REAL_PURCHASES=false
```

Railway will automatically set:
- `PORT`
- `DATABASE_URI` (if PostgreSQL service is added)

## Post-Deployment

1. The app will be available at your Railway URL
2. Access the API at: `https://your-app.railway.app/api/system/health`
3. Access the V3 interface at: `https://your-app.railway.app/static/api-demo/v3/`