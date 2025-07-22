#!/usr/bin/env python3
"""
Example showing how to use the new PDF URL processing endpoint
"""

import requests
import json

# Demo API configuration
DEMO_BASE_URL = "http://localhost:7777/api/demo"
DEMO_KEY = "prefix_test_key"

def process_pdf_url(pdf_url, make=None, model=None):
    """Process a PDF directly from URL using AI"""
    
    url = f"{DEMO_BASE_URL}/manuals/process"
    headers = {
        "Content-Type": "application/json",
        "X-Demo-Key": DEMO_KEY
    }
    
    data = {
        "pdf_url": pdf_url,
        "make": make or "Unknown",
        "model": model or "Unknown"
    }
    
    print(f"🔧 Processing PDF: {pdf_url}")
    print(f"📍 Make/Model: {make}/{model}")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Success! Processing completed")
            print(f"📊 Manual Subject: {result.get('manual_subject', 'Unknown')}")
            print(f"🚨 Error Codes Found: {result.get('error_codes_count', 0)}")
            print(f"🔧 Part Numbers Found: {result.get('part_numbers_count', 0)}")
            
            # Show first few error codes
            error_codes = result.get('error_codes', [])
            if error_codes:
                print(f"\n🚨 Sample Error Codes:")
                for i, error in enumerate(error_codes[:3]):
                    if isinstance(error, dict):
                        print(f"  {i+1}. {error.get('code', 'N/A')}: {error.get('description', 'N/A')}")
                    else:
                        print(f"  {i+1}. {error}")
            
            # Show first few part numbers
            part_numbers = result.get('part_numbers', [])
            if part_numbers:
                print(f"\n🔧 Sample Part Numbers:")
                for i, part in enumerate(part_numbers[:3]):
                    if isinstance(part, dict):
                        print(f"  {i+1}. {part.get('code', 'N/A')}: {part.get('description', 'N/A')}")
                    else:
                        print(f"  {i+1}. {part}")
            
            return result
            
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def main():
    print("📄 PDF URL Processing Demo")
    print("=" * 40)
    
    # Example PDFs to test
    test_pdfs = [
        {
            "url": "https://www.hennypenny.com/wp-content/uploads/2015/01/PFE-PFG_500-561-600-Ops-Manual-Electro-Mech.pdf",
            "make": "Henny Penny",
            "model": "500"
        },
        {
            "url": "https://example-manual.com/manual.pdf",  # This will fail gracefully
            "make": "Test Brand",
            "model": "Test Model"
        }
    ]
    
    for i, test in enumerate(test_pdfs, 1):
        print(f"\n📋 Test {i}:")
        result = process_pdf_url(
            test["url"], 
            test["make"], 
            test["model"]
        )
        
        if result:
            print(f"✅ Test {i} completed successfully")
        else:
            print(f"❌ Test {i} failed")
        
        print("-" * 40)

if __name__ == "__main__":
    main()