#!/bin/bash

# Simple curl-based API tests for Manual Purchase Agent v15.6

BASE_URL="http://localhost:7777"

echo "=========================================="
echo "  Manual Purchase Agent API Tests (curl)"
echo "=========================================="

# Function to test an endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    echo ""
    echo "Testing: $description"
    echo "Endpoint: $method $endpoint"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$BASE_URL$endpoint" 2>/dev/null)
    else
        response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X "$method" \
                        -H "Content-Type: application/json" \
                        -d "$data" \
                        "$BASE_URL$endpoint" 2>/dev/null)
    fi
    
    # Extract status code and body
    if [[ $response == *"HTTPSTATUS:"* ]]; then
        body=$(echo "$response" | sed -E 's/HTTPSTATUS:[0-9]{3}$//')
        status=$(echo "$response" | grep -o '[0-9]*$')
    else
        body="Connection failed"
        status="0"
    fi
    
    # Print result
    if [ "$status" -ge 200 ] && [ "$status" -lt 300 ]; then
        echo "✅ PASS - Status: $status"
        echo "Response: $(echo "$body" | head -c 100)..."
    else
        echo "❌ FAIL - Status: $status"
        echo "Response: $body"
    fi
}

# Test 1: System Health Check
test_endpoint "GET" "/api/system/health" "" "System Health Check"

# Test 2: Parts Resolution
part_data='{
    "description": "Bowl Lift Motor",
    "make": "Hobart",
    "model": "HL600",
    "use_database": false,
    "use_manual_search": true,
    "use_web_search": true,
    "save_results": false
}'
test_endpoint "POST" "/api/parts/resolve" "$part_data" "Parts Resolution"

# Test 3: Supplier Search
supplier_data='{
    "part_number": "00-917676",
    "make": "Hobart",
    "model": "HL600",
    "oem_only": false,
    "use_v2": true
}'
test_endpoint "POST" "/api/suppliers/search" "$supplier_data" "Supplier Search"

# Test 4: Manual Search
manual_data='{
    "make": "Hobart",
    "model": "HL600",
    "manual_type": "technical"
}'
test_endpoint "POST" "/api/manuals/search" "$manual_data" "Manual Search"

# Test 5: Get Manuals List
test_endpoint "GET" "/api/manuals" "" "Get Manuals List"

# Test 6: Equipment Enrichment
enrichment_data='{
    "make": "Hobart",
    "model": "HL600",
    "year": "2020"
}'
test_endpoint "POST" "/api/enrichment/equipment" "$enrichment_data" "Equipment Enrichment"

# Test 7: Get Profiles
test_endpoint "GET" "/api/profiles" "" "Get Billing Profiles"

# Test 8: Supplier Screenshots
screenshot_data='{
    "urls": [
        "https://www.partstown.com/hobart/hob00-917676",
        "https://www.webstaurantstore.com/search/hobart-mixer-motor.html"
    ]
}'
test_endpoint "POST" "/api/screenshots/supplier" "$screenshot_data" "Supplier Screenshots"

echo ""
echo "=========================================="
echo "API tests completed"
echo "=========================================="