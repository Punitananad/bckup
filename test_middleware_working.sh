#!/bin/bash
# Test if API Key Middleware is Working
# Tests both with and without API key

API_KEY="RDnXh86Ciczn2Orbc2CxQtQ6VB-tzl19bcKTtNrSK4Y"
BASE_URL="https://scan2food.com"

echo "=== TESTING API KEY MIDDLEWARE ==="
echo ""

# Test 1: Request WITHOUT API key (should fail with 401)
echo "Test 1: Request WITHOUT API key (should return 401 error)"
echo "URL: $BASE_URL/theatre/api/theatre-detail"
echo ""
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$BASE_URL/theatre/api/theatre-detail")
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE:/d')

echo "Response Code: $HTTP_CODE"
echo "Response Body: $BODY"
echo ""

if [ "$HTTP_CODE" = "401" ]; then
    echo "✓ PASS: Middleware correctly blocked request without API key"
else
    echo "✗ FAIL: Expected 401, got $HTTP_CODE"
    echo "⚠️  MIDDLEWARE IS NOT WORKING!"
fi
echo ""
echo "---"
echo ""

# Test 2: Request WITH valid API key (should succeed)
echo "Test 2: Request WITH valid API key (should return 200 OK)"
echo "URL: $BASE_URL/theatre/api/theatre-detail"
echo "Header: X-API-Key: $API_KEY"
echo ""
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -H "X-API-Key: $API_KEY" "$BASE_URL/theatre/api/theatre-detail")
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE:/d')

echo "Response Code: $HTTP_CODE"
echo "Response Body (first 200 chars): ${BODY:0:200}..."
echo ""

if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ PASS: Middleware correctly allowed request with valid API key"
else
    echo "✗ FAIL: Expected 200, got $HTTP_CODE"
fi
echo ""
echo "---"
echo ""

# Test 3: Request WITH invalid API key (should fail with 401)
echo "Test 3: Request WITH invalid API key (should return 401 error)"
echo "URL: $BASE_URL/theatre/api/theatre-detail"
echo "Header: X-API-Key: INVALID_KEY_12345"
echo ""
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -H "X-API-Key: INVALID_KEY_12345" "$BASE_URL/theatre/api/theatre-detail")
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE:/d')

echo "Response Code: $HTTP_CODE"
echo "Response Body: $BODY"
echo ""

if [ "$HTTP_CODE" = "401" ]; then
    echo "✓ PASS: Middleware correctly blocked request with invalid API key"
else
    echo "✗ FAIL: Expected 401, got $HTTP_CODE"
fi
echo ""
echo "---"
echo ""

# Test 4: Webhook should work WITHOUT API key (webhooks are excluded)
echo "Test 4: Webhook endpoint WITHOUT API key (should work - webhooks excluded)"
echo "URL: $BASE_URL/theatre/api/payu-webhook-url"
echo ""
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "$BASE_URL/theatre/api/payu-webhook-url")
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)

echo "Response Code: $HTTP_CODE"
echo ""

if [ "$HTTP_CODE" != "401" ]; then
    echo "✓ PASS: Webhook correctly bypassed API key check"
else
    echo "✗ FAIL: Webhook should not require API key"
fi
echo ""

echo "=== TEST SUMMARY ==="
echo ""
echo "If all tests passed, middleware is working correctly!"
echo "If tests failed, check:"
echo "  1. Middleware is in MIDDLEWARE list in settings.py"
echo "  2. Python cache is cleared"
echo "  3. Services are restarted"
echo "  4. Check logs: sudo journalctl -u gunicorn -n 100 | grep MIDDLEWARE"
