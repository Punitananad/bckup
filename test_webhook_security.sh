#!/bin/bash

# ═══════════════════════════════════════════════════════════════
# TEST WEBHOOK SECURITY ON SERVER
# ═══════════════════════════════════════════════════════════════

echo "🔍 Testing Webhook Security Implementation"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Navigate to project directory
cd /var/www/scan2food/application/scan2food

echo "📁 Current directory: $(pwd)"
echo ""

# ───────────────────────────────────────────────────────────────
# TEST 1: Check if webhook_security.py exists
# ───────────────────────────────────────────────────────────────

echo "TEST 1: Check if webhook_security.py exists"
if [ -f "theatre/webhook_security.py" ]; then
    echo "✅ webhook_security.py EXISTS"
else
    echo "❌ webhook_security.py NOT FOUND"
    echo "   Run: git pull origin main"
fi
echo ""

# ───────────────────────────────────────────────────────────────
# TEST 2: Check if import exists in api_views.py
# ───────────────────────────────────────────────────────────────

echo "TEST 2: Check if import exists in api_views.py"
if grep -q "from .webhook_security import verify_webhook_request" theatre/api_views.py; then
    echo "✅ Import FOUND in api_views.py"
else
    echo "❌ Import NOT FOUND in api_views.py"
    echo "   Run: git pull origin main"
fi
echo ""

# ───────────────────────────────────────────────────────────────
# TEST 3: Check if verification code exists in razporpay_webhook_url
# ───────────────────────────────────────────────────────────────

echo "TEST 3: Check if verification exists in razporpay_webhook_url"
if grep -q "verify_webhook_request(request, 'Razorpay'" theatre/api_views.py; then
    echo "✅ Verification code FOUND in razporpay_webhook_url"
else
    echo "❌ Verification code NOT FOUND in razporpay_webhook_url"
    echo "   Run: git pull origin main"
fi
echo ""

# ───────────────────────────────────────────────────────────────
# TEST 4: Check if verification code exists in split_razporpay_webhook_url
# ───────────────────────────────────────────────────────────────

echo "TEST 4: Check if verification exists in split_razporpay_webhook_url"
if grep -q "verify_webhook_request(request, 'split_razorpay'" theatre/api_views.py; then
    echo "✅ Verification code FOUND in split_razporpay_webhook_url"
else
    echo "❌ Verification code NOT FOUND in split_razporpay_webhook_url"
    echo "   Run: git pull origin main"
fi
echo ""

# ───────────────────────────────────────────────────────────────
# TEST 5: Check services status
# ───────────────────────────────────────────────────────────────

echo "TEST 5: Check services status"
if systemctl is-active --quiet gunicorn; then
    echo "✅ Gunicorn is RUNNING"
else
    echo "❌ Gunicorn is NOT RUNNING"
    echo "   Run: sudo systemctl restart gunicorn"
fi

if systemctl is-active --quiet daphne; then
    echo "✅ Daphne is RUNNING"
else
    echo "❌ Daphne is NOT RUNNING"
    echo "   Run: sudo systemctl restart daphne"
fi
echo ""

# ───────────────────────────────────────────────────────────────
# TEST 6: Check recent logs for webhook verification
# ───────────────────────────────────────────────────────────────

echo "TEST 6: Check recent logs for webhook verification messages"
echo "Looking for verification messages in last 100 lines..."
if journalctl -u gunicorn -n 100 --no-pager | grep -q "webhook verified\|webhook verification failed"; then
    echo "✅ Webhook verification messages FOUND in logs"
    echo ""
    echo "Recent webhook verification logs:"
    journalctl -u gunicorn -n 100 --no-pager | grep "webhook verified\|webhook verification failed" | tail -5
else
    echo "⚠️  No webhook verification messages in recent logs"
    echo "   This is normal if no payments have been made yet"
fi
echo ""

# ───────────────────────────────────────────────────────────────
# SUMMARY
# ───────────────────────────────────────────────────────────────

echo "═══════════════════════════════════════════════════════════════"
echo "📊 SUMMARY"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Count passed tests
PASSED=0
TOTAL=5

[ -f "theatre/webhook_security.py" ] && ((PASSED++))
grep -q "from .webhook_security import verify_webhook_request" theatre/api_views.py && ((PASSED++))
grep -q "verify_webhook_request(request, 'Razorpay'" theatre/api_views.py && ((PASSED++))
grep -q "verify_webhook_request(request, 'split_razorpay'" theatre/api_views.py && ((PASSED++))
systemctl is-active --quiet gunicorn && systemctl is-active --quiet daphne && ((PASSED++))

echo "Tests Passed: $PASSED / $TOTAL"
echo ""

if [ $PASSED -eq $TOTAL ]; then
    echo "✅ ALL TESTS PASSED - Webhook security is ACTIVE"
    echo ""
    echo "Next Steps:"
    echo "1. Add correct webhook secret to admin panel"
    echo "2. Make a test payment"
    echo "3. Check logs: sudo journalctl -u gunicorn -f"
    echo "4. Should see: ✅ Razorpay webhook verified"
else
    echo "❌ SOME TESTS FAILED - Webhook security is NOT ACTIVE"
    echo ""
    echo "Fix Steps:"
    echo "1. Run: git pull origin main"
    echo "2. Run: sudo systemctl restart gunicorn daphne"
    echo "3. Run this test script again"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
