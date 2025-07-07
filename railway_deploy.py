#!/usr/bin/env python3
"""
Automated Railway deployment script
"""
import subprocess
import os
import json
import time

def run_command(cmd, env=None):
    """Run command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env)
        return result.stdout.strip(), result.returncode
    except Exception as e:
        return str(e), 1

def main():
    print("🚀 Starting Railway deployment...")
    
    # Set up environment
    env = os.environ.copy()
    
    # First, let's check current status
    output, code = run_command("railway status", env)
    print(f"\n📊 Current status:\n{output}")
    
    # Try to deploy directly - Railway will create service if needed
    print("\n🚂 Attempting deployment...")
    print("This will create a new service if one doesn't exist...")
    
    # Create a nixpacks.toml for better control
    nixpacks_content = """[phases.setup]
nixPkgs = ["python311"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 app:create_app()"
"""
    
    with open("nixpacks.toml", "w") as f:
        f.write(nixpacks_content)
    print("✅ Created nixpacks.toml for deployment configuration")
    
    # Try deployment
    print("\n🚀 Running: railway up --detach")
    deploy_cmd = "railway up --detach"
    output, code = run_command(deploy_cmd, env)
    
    if code == 0:
        print(f"✅ Deployment started successfully!")
        print(f"Output: {output}")
        
        # Get deployment URL
        print("\n🔍 Getting deployment URL...")
        url_output, _ = run_command("railway domain", env)
        if url_output:
            print(f"🌐 Your app URL: {url_output}")
    else:
        print(f"⚠️  Deployment output: {output}")
        print("\n📝 Manual steps required:")
        print("1. Go to: https://railway.com/project/2aaf026e-a3b5-49e9-9710-7df13ebec771")
        print("2. Click the '+' button to add a new service")
        print("3. Choose 'Empty Service'")
        print("4. Name it 'web'")
        print("5. Come back here and run: ./railway_deploy_final.sh")
    
    # Create final deployment script
    final_script = """#!/bin/bash
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
"""
    
    with open("railway_deploy_final.sh", "w") as f:
        f.write(final_script)
    os.chmod("railway_deploy_final.sh", 0o755)
    print("\n✅ Created railway_deploy_final.sh for manual service deployment")

if __name__ == "__main__":
    main()