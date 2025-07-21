#!/bin/bash

echo "========================================"
echo "Testing Railway API Endpoints"
echo "Date: $(date)"
echo "========================================"
echo ""

# Base URL
BASE_URL="https://thriving-flow-production.up.railway.app"

# Test 1: System Health
echo "1. GET /api/system/health"
echo "-------------------------"
START_TIME=$(date +%s.%N)
RESPONSE=$(curl -s -X GET "$BASE_URL/api/system/health" -w "\nHTTP_STATUS:%{http_code}")
END_TIME=$(date +%s.%N)
HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS:" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS:/d')
ELAPSED=$(echo "$END_TIME - $START_TIME" | bc)
echo "HTTP Status: $HTTP_STATUS"
echo "Response Time: ${ELAPSED}s"
echo "Response Body: $BODY"
echo ""

# Test 2: Parts Resolve
echo "2. POST /api/parts/resolve"
echo "--------------------------"
START_TIME=$(date +%s.%N)
RESPONSE=$(curl -s -X POST "$BASE_URL/api/parts/resolve" \
  -H "Content-Type: application/json" \
  -d '{
    "description":"Bowl Lift Motor",
    "make":"Hobart",
    "model":"HL600",
    "use_database":false,
    "use_manual_search":true,
    "use_web_search":true,
    "save_results":false
  }' -w "\nHTTP_STATUS:%{http_code}")
END_TIME=$(date +%s.%N)
HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS:" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS:/d')
ELAPSED=$(echo "$END_TIME - $START_TIME" | bc)
echo "HTTP Status: $HTTP_STATUS"
echo "Response Time: ${ELAPSED}s"
echo "Response Body (first 500 chars): ${BODY:0:500}..."
echo ""

# Test 3: Suppliers Search
echo "3. POST /api/suppliers/search"
echo "-----------------------------"
START_TIME=$(date +%s.%N)
RESPONSE=$(curl -s -X POST "$BASE_URL/api/suppliers/search" \
  -H "Content-Type: application/json" \
  -d '{
    "part_number":"00-917676",
    "make":"Hobart",
    "model":"HL600",
    "oem_only":false,
    "use_v2":true
  }' -w "\nHTTP_STATUS:%{http_code}")
END_TIME=$(date +%s.%N)
HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS:" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS:/d')
ELAPSED=$(echo "$END_TIME - $START_TIME" | bc)
echo "HTTP Status: $HTTP_STATUS"
echo "Response Time: ${ELAPSED}s"
echo "Response Body (first 500 chars): ${BODY:0:500}..."
echo ""

# Test 4: Manuals Search
echo "4. POST /api/manuals/search"
echo "---------------------------"
START_TIME=$(date +%s.%N)
RESPONSE=$(curl -s -X POST "$BASE_URL/api/manuals/search" \
  -H "Content-Type: application/json" \
  -d '{
    "make":"Hobart",
    "model":"HL600",
    "manual_type":"technical"
  }' -w "\nHTTP_STATUS:%{http_code}")
END_TIME=$(date +%s.%N)
HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS:" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS:/d')
ELAPSED=$(echo "$END_TIME - $START_TIME" | bc)
echo "HTTP Status: $HTTP_STATUS"
echo "Response Time: ${ELAPSED}s"
echo "Response Body (first 500 chars): ${BODY:0:500}..."
echo ""

# Test 5: Get Manuals
echo "5. GET /api/manuals"
echo "-------------------"
START_TIME=$(date +%s.%N)
RESPONSE=$(curl -s -X GET "$BASE_URL/api/manuals" -w "\nHTTP_STATUS:%{http_code}")
END_TIME=$(date +%s.%N)
HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS:" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS:/d')
ELAPSED=$(echo "$END_TIME - $START_TIME" | bc)
echo "HTTP Status: $HTTP_STATUS"
echo "Response Time: ${ELAPSED}s"
echo "Response Body (first 500 chars): ${BODY:0:500}..."
echo ""

# Test 6: Enrichment Equipment (THIS IS THE KEY TEST)
echo "6. POST /api/enrichment/equipment"
echo "---------------------------------"
START_TIME=$(date +%s.%N)
RESPONSE=$(curl -s -X POST "$BASE_URL/api/enrichment/equipment" \
  -H "Content-Type: application/json" \
  -d '{
    "make":"Hobart",
    "model":"HL600",
    "year":"2020"
  }' -w "\nHTTP_STATUS:%{http_code}")
END_TIME=$(date +%s.%N)
HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS:" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS:/d')
ELAPSED=$(echo "$END_TIME - $START_TIME" | bc)
echo "HTTP Status: $HTTP_STATUS"
echo "Response Time: ${ELAPSED}s"
echo "Response Body: $BODY"
echo ""

# Test 7: Get Profiles
echo "7. GET /api/profiles"
echo "--------------------"
START_TIME=$(date +%s.%N)
RESPONSE=$(curl -s -X GET "$BASE_URL/api/profiles" -w "\nHTTP_STATUS:%{http_code}")
END_TIME=$(date +%s.%N)
HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS:" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS:/d')
ELAPSED=$(echo "$END_TIME - $START_TIME" | bc)
echo "HTTP Status: $HTTP_STATUS"
echo "Response Time: ${ELAPSED}s"
echo "Response Body (first 500 chars): ${BODY:0:500}..."
echo ""

# Test 8: Screenshots Supplier
echo "8. POST /api/screenshots/supplier"
echo "---------------------------------"
START_TIME=$(date +%s.%N)
RESPONSE=$(curl -s -X POST "$BASE_URL/api/screenshots/supplier" \
  -H "Content-Type: application/json" \
  -d '{
    "urls":["https://www.partstown.com/hobart/hob00-917676"]
  }' -w "\nHTTP_STATUS:%{http_code}")
END_TIME=$(date +%s.%N)
HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS:" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS:/d')
ELAPSED=$(echo "$END_TIME - $START_TIME" | bc)
echo "HTTP Status: $HTTP_STATUS"
echo "Response Time: ${ELAPSED}s"
echo "Response Body (first 500 chars): ${BODY:0:500}..."
echo ""

# Test 9: Clear Database
echo "9. POST /api/system/clear-database"
echo "----------------------------------"
START_TIME=$(date +%s.%N)
RESPONSE=$(curl -s -X POST "$BASE_URL/api/system/clear-database" -w "\nHTTP_STATUS:%{http_code}")
END_TIME=$(date +%s.%N)
HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS:" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS:/d')
ELAPSED=$(echo "$END_TIME - $START_TIME" | bc)
echo "HTTP Status: $HTTP_STATUS"
echo "Response Time: ${ELAPSED}s"
echo "Response Body: $BODY"
echo ""

echo "========================================"
echo "Testing Complete"
echo "========================================"