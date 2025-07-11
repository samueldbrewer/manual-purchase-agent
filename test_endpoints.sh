#!/bin/bash

BASE_URL="https://thriving-flow-production.up.railway.app"

echo "Testing Railway API Endpoints"
echo "=============================="

# Test 1: Health check
echo ""
echo "1. Testing Health Check..."
curl -s -o /tmp/response1.json -w "HTTP_CODE:%{http_code} TIME:%{time_total}s\n" \
  -X GET "${BASE_URL}/api/system/health" \
  -H "Accept: application/json"
echo "Response:"
cat /tmp/response1.json
echo ""

# Test 2: Parts resolve
echo ""
echo "2. Testing Parts Resolve..."
curl -s -o /tmp/response2.json -w "HTTP_CODE:%{http_code} TIME:%{time_total}s\n" \
  -X POST "${BASE_URL}/api/parts/resolve" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"description":"Bowl Lift Motor","make":"Hobart","model":"HL600","use_database":false,"use_manual_search":true,"use_web_search":true,"save_results":false}'
echo "Response:"
cat /tmp/response2.json
echo ""

# Test 3: Supplier search
echo ""
echo "3. Testing Supplier Search..."
curl -s -o /tmp/response3.json -w "HTTP_CODE:%{http_code} TIME:%{time_total}s\n" \
  -X POST "${BASE_URL}/api/suppliers/search" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"part_number":"00-917676","make":"Hobart","model":"HL600","oem_only":false,"use_v2":true}'
echo "Response:"
cat /tmp/response3.json
echo ""

# Test 4: Manual search  
echo ""
echo "4. Testing Manual Search..."
curl -s -o /tmp/response4.json -w "HTTP_CODE:%{http_code} TIME:%{time_total}s\n" \
  -X POST "${BASE_URL}/api/manuals/search" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"make":"Hobart","model":"HL600","manual_type":"technical"}'
echo "Response:"
cat /tmp/response4.json
echo ""

# Test 5: Get manuals
echo ""
echo "5. Testing Get Manuals..."
curl -s -o /tmp/response5.json -w "HTTP_CODE:%{http_code} TIME:%{time_total}s\n" \
  -X GET "${BASE_URL}/api/manuals" \
  -H "Accept: application/json"
echo "Response:"
cat /tmp/response5.json
echo ""

# Test 6: Equipment enrichment
echo ""
echo "6. Testing Equipment Enrichment..."
curl -s -o /tmp/response6.json -w "HTTP_CODE:%{http_code} TIME:%{time_total}s\n" \
  -X POST "${BASE_URL}/api/enrichment/equipment" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"make":"Hobart","model":"HL600","year":"2020"}'
echo "Response:"
cat /tmp/response6.json
echo ""

# Test 7: Get profiles
echo ""
echo "7. Testing Get Profiles..."
curl -s -o /tmp/response7.json -w "HTTP_CODE:%{http_code} TIME:%{time_total}s\n" \
  -X GET "${BASE_URL}/api/profiles" \
  -H "Accept: application/json"
echo "Response:"
cat /tmp/response7.json
echo ""

# Test 8: Screenshot supplier
echo ""
echo "8. Testing Supplier Screenshots..."
curl -s -o /tmp/response8.json -w "HTTP_CODE:%{http_code} TIME:%{time_total}s\n" \
  -X POST "${BASE_URL}/api/screenshots/supplier" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"urls":["https://www.partstown.com/hobart/hob00-917676"]}'
echo "Response:"
cat /tmp/response8.json
echo ""

echo "Testing complete!"