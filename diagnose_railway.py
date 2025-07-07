#!/usr/bin/env python3
"""
Diagnose Railway deployment issues
"""
import subprocess
import requests
import json

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1

def main():
    print("🔍 Railway Deployment Diagnosis")
    print("=" * 40)
    
    # Check Railway status
    print("\n1. Checking Railway status...")
    stdout, stderr, code = run_cmd("railway status")
    print(f"Status: {stdout}")
    if stderr:
        print(f"Error: {stderr}")
    
    # Check domain
    print("\n2. Getting domain...")
    stdout, stderr, code = run_cmd("railway domain")
    print(f"Domain: {stdout}")
    
    # Test URL
    url = "https://thriving-flow-production.up.railway.app"
    print(f"\n3. Testing URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
    except Exception as e:
        print(f"Connection error: {e}")
    
    # Test API endpoint
    api_url = f"{url}/api/system/health"
    print(f"\n4. Testing API: {api_url}")
    
    try:
        response = requests.get(api_url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
    except Exception as e:
        print(f"API error: {e}")
    
    print("\n" + "=" * 40)
    print("🔧 Possible Issues:")
    print("1. App might not be starting (check Railway dashboard logs)")
    print("2. Environment variables might be missing")
    print("3. Database connection issues")
    print("4. Port configuration problems")
    print("\n💡 Solutions:")
    print("1. Check Railway dashboard for build/runtime logs")
    print("2. Ensure environment variables are set")
    print("3. Try redeploying from Railway dashboard")

if __name__ == "__main__":
    main()