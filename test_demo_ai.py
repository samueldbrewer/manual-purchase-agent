#!/usr/bin/env python3
"""
Test script to verify the demo AI endpoints are working properly
"""

import requests
import json
import sys

# Demo API URL
DEMO_BASE_URL = "http://localhost:7777/api/demo"

# Demo API key (from context, seems to be test key)
DEMO_KEY = "prefix_test_key"

def test_demo_endpoint(endpoint, method="GET", data=None):
    """Test a demo endpoint"""
    url = f"{DEMO_BASE_URL}{endpoint}"
    headers = {"X-Demo-Key": DEMO_KEY}
    
    if method == "POST" and data:
        headers["Content-Type"] = "application/json"
    
    print(f"\n🧪 Testing {method} {endpoint}")
    print(f"URL: {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        else:
            response = requests.post(url, headers=headers, json=data)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {json.dumps(result, indent=2)[:500]}...")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    print("🔧 Testing Demo AI Endpoints")
    print("=" * 50)
    
    # Test manual search first
    print("\n📖 1. Testing Manual Search")
    manual_search_data = {
        "make": "Henny Penny",
        "model": "500",
        "manual_type": "technical"
    }
    
    if not test_demo_endpoint("/manuals/search", "POST", manual_search_data):
        print("❌ Manual search failed - can't test AI endpoints without a manual")
        sys.exit(1)
    
    # Test AI-powered error codes extraction
    print("\n🚨 2. Testing AI Error Codes Extraction")
    if not test_demo_endpoint("/manuals/error-codes?manual_id=1"):
        print("❌ Error codes extraction failed")
    
    # Test AI-powered part numbers extraction  
    print("\n🔧 3. Testing AI Part Numbers Extraction")
    if not test_demo_endpoint("/manuals/part-numbers?manual_id=1"):
        print("❌ Part numbers extraction failed")
    
    # Test parts resolution
    print("\n🔍 4. Testing Parts Resolution")
    parts_data = {
        "description": "Bowl Lift Motor",
        "make": "Hobart", 
        "model": "HL600",
        "use_database": False,
        "use_manual_search": True,
        "use_web_search": True,
        "save_results": False
    }
    
    if not test_demo_endpoint("/parts/resolve", "POST", parts_data):
        print("❌ Parts resolution failed")
    
    # Test supplier search
    print("\n🛒 5. Testing Supplier Search")
    supplier_data = {
        "part_number": "00-917676",
        "make": "Hobart",
        "model": "HL600",
        "oem_only": False,
        "use_v2": True
    }
    
    if not test_demo_endpoint("/suppliers/search", "POST", supplier_data):
        print("❌ Supplier search failed")

    print("\n🎉 Demo AI testing completed!")

if __name__ == "__main__":
    main()