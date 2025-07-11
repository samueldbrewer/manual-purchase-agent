#!/bin/bash

# Railway API Endpoint Test Script
# Tests all Manual Purchase Agent API endpoints and captures detailed results

BASE_URL="https://thriving-flow-production.up.railway.app"
OUTPUT_FILE="api_test_results.txt"

echo "===========================================" > $OUTPUT_FILE
echo "Railway API Endpoint Test Results" >> $OUTPUT_FILE
echo "Timestamp: $(date)" >> $OUTPUT_FILE
echo "Base URL: $BASE_URL" >> $OUTPUT_FILE
echo "===========================================" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Function to test an endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    echo "Testing: $description" | tee -a $OUTPUT_FILE
    echo "Method: $method" | tee -a $OUTPUT_FILE
    echo "Endpoint: $endpoint" | tee -a $OUTPUT_FILE
    if [ ! -z "$data" ]; then
        echo "Request Body: $data" | tee -a $OUTPUT_FILE
    fi
    echo "---" | tee -a $OUTPUT_FILE
    
    # Capture response with timing
    if [ "$method" = "GET" ]; then
        response=$(curl -w "\nHTTP_CODE:%{http_code}\nTIME_TOTAL:%{time_total}\n" \
                       -s -X GET "$BASE_URL$endpoint" \
                       -H "Accept: application/json" 2>&1)
    else
        response=$(curl -w "\nHTTP_CODE:%{http_code}\nTIME_TOTAL:%{time_total}\n" \
                       -s -X POST "$BASE_URL$endpoint" \
                       -H "Content-Type: application/json" \
                       -H "Accept: application/json" \
                       -d "$data" 2>&1)
    fi
    
    echo "Response:" | tee -a $OUTPUT_FILE
    echo "$response" | tee -a $OUTPUT_FILE
    echo "" | tee -a $OUTPUT_FILE
    echo "=========================================" | tee -a $OUTPUT_FILE
    echo "" | tee -a $OUTPUT_FILE
}

echo "Starting API endpoint tests..." | tee -a $OUTPUT_FILE
echo "" | tee -a $OUTPUT_FILE

# Test 1: Health Check
test_endpoint "GET" "/api/system/health" "" "System Health Check"

# Test 2: Parts Resolution
test_endpoint "POST" "/api/parts/resolve" \
    '{"description":"Bowl Lift Motor","make":"Hobart","model":"HL600","use_database":false,"use_manual_search":true,"use_web_search":true,"save_results":false}' \
    "Parts Resolution"

# Test 3: Supplier Search
test_endpoint "POST" "/api/suppliers/search" \
    '{"part_number":"00-917676","make":"Hobart","model":"HL600","oem_only":false,"use_v2":true}' \
    "Supplier Search"

# Test 4: Manual Search
test_endpoint "POST" "/api/manuals/search" \
    '{"make":"Hobart","model":"HL600","manual_type":"technical"}' \
    "Manual Search"

# Test 5: Get All Manuals
test_endpoint "GET" "/api/manuals" "" "Get All Manuals"

# Test 6: Equipment Enrichment
test_endpoint "POST" "/api/enrichment/equipment" \
    '{"make":"Hobart","model":"HL600","year":"2020"}' \
    "Equipment Enrichment"

# Test 7: Get Billing Profiles
test_endpoint "GET" "/api/profiles" "" "Get Billing Profiles"

# Test 8: Supplier Screenshots
test_endpoint "POST" "/api/screenshots/supplier" \
    '{"urls":["https://www.partstown.com/hobart/hob00-917676"]}' \
    "Supplier Screenshots"

# Test 9: Clear Database (for testing)
test_endpoint "POST" "/api/system/clear-database" "" "Clear Database"

echo "All tests completed!" | tee -a $OUTPUT_FILE
echo "Results saved to: $OUTPUT_FILE" | tee -a $OUTPUT_FILE
echo "" | tee -a $OUTPUT_FILE
echo "To view results: cat $OUTPUT_FILE" | tee -a $OUTPUT_FILE