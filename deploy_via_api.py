#!/usr/bin/env python3
"""
Deploy to Railway via API
"""
import subprocess
import json
import time
import sys

def run_command(cmd):
    """Run a command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return None
        return result.stdout.strip()
    except Exception as e:
        print(f"Exception: {e}")
        return None

def main():
    print("🚀 Starting Railway deployment process...")
    
    # Check if logged in
    user = run_command("railway whoami")
    if not user:
        print("❌ Not logged in to Railway. Please run: railway login")
        sys.exit(1)
    print(f"✅ Logged in as: {user}")
    
    # Get project info
    print("\n📋 Current project status:")
    status = run_command("railway status")
    print(status)
    
    # Try to deploy with environment variables
    print("\n🔧 Setting environment variables...")
    env_vars = {
        "FLASK_ENV": "production",
        "SECRET_KEY": "manual-purchase-agent-production-secret-key-2024",
        "ENCRYPTION_KEY": "z2KGjtN24oYD3KHkkr8bpKsjyxJAN2SgAfgILqWnO54=",
        "ENABLE_REAL_PURCHASES": "false",
        "PYTHONPATH": "/app"
    }
    
    for key, value in env_vars.items():
        cmd = f'railway variables --set "{key}={value}"'
        result = run_command(cmd)
        if result:
            print(f"  ✅ Set {key}")
        else:
            print(f"  ⚠️  Could not set {key} (will need to set in dashboard)")
    
    print("\n🚀 Attempting deployment...")
    print("Running: railway up")
    
    # Try to deploy
    deploy_result = run_command("railway up --detach")
    if deploy_result:
        print("✅ Deployment initiated!")
        print(deploy_result)
    else:
        print("⚠️  Could not deploy via CLI. Please use the Railway dashboard.")
    
    print("\n📌 Next steps:")
    print("1. Go to: https://railway.com/project/2aaf026e-a3b5-49e9-9710-7df13ebec771")
    print("2. Click 'New Service' → 'GitHub Repo' or 'Empty Service'")
    print("3. If using Empty Service, drag and drop this folder")
    print("4. Add environment variables (SERPAPI_KEY and OPENAI_API_KEY)")
    print("5. Add PostgreSQL database service")
    print("6. Deploy!")

if __name__ == "__main__":
    main()