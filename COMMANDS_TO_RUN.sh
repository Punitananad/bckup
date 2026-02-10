#!/bin/bash

# ═══════════════════════════════════════════════════════════════
# WEBHOOK SECURITY - COMMANDS TO RUN
# ═══════════════════════════════════════════════════════════════

echo "🔒 Webhook Security Implementation - Commands"
echo ""

# ───────────────────────────────────────────────────────────────
# STEP 1: Verify Code Changes
# ───────────────────────────────────────────────────────────────

echo "📝 Step 1: Verify code changes..."
cd /var/www/scan2food/application/scan2food

# Check if webhook_security.py exists
if [ -f "theatre/webhook_security.py" ]; then
    echo "✅ webhook_security.py exists"
else
    echo "❌ webhook_security.py NOT FOUND"
fi

# Check if api_views.py has the import
if grep -q "from .webhook_security import verify_webhook_request" theatre/api_views.py; then
    echo "✅ Import added to api_views.py"
else
    echo "❌ Import NOT FOUND in api_views.py"
fi

echo ""

# ───────────────────────────────────────────────────────────────
# STEP 2: Check Current Services Status
# ───────────────────────────────────────────────────────────────

echo "🔍 Step 2: Check current services status..."
sudo systemctl status gunicorn --no-pager | head -3
sudo systemctl status daphne --no-pager | head -3
echo ""

# ───────────────────────────────────────────────────────────────
# STEP 3: Restart Services
# ───────────────────────────────────────────────────────────────

echo "🔄 Step 3: Restart services..."
echo "Running: sudo systemctl restart gunicorn daphne"
sudo systemctl restart gunicorn daphne

echo "Waiting 10 seconds for services to start..."
sleep 10

echo ""

# ───────────────────────────────────────────────────────────────
# STEP 4: Verify Services Are Running
# ───────────────────────────────────────────────────────────────

echo "✅ Step 4: Verify services are running..."
sudo systemctl is-active gunicorn && echo "✅ Gunicorn is running" || echo "❌ Gunicorn is NOT running"
sudo systemctl is-active daphne && echo "✅ Daphne is running" || echo "❌ Daphne is NOT running"
echo ""

# ───────────────────────────────────────────────────────────────
# STEP 5: Show Recent Logs
# ───────────────────────────────────────────────────────────────

echo "📋 Step 5: Recent logs (last 20 lines)..."
echo "─── Gunicorn Logs ───"
sudo journalctl -u gunicorn -n 20 --no-pager
echo ""
echo "─── Daphne Logs ───"
sudo journalctl -u daphne -n 20 --no-pager
echo ""

# ───────────────────────────────────────────────────────────────
# STEP 6: Monitor Logs (Optional)
# ───────────────────────────────────────────────────────────────

echo "📊 Step 6: Monitor logs in real-time..."
echo "Press Ctrl+C to stop monitoring"
echo ""
echo "Command: sudo journalctl -u gunicorn -f"
echo ""
echo "To run manually:"
echo "  sudo journalctl -u gunicorn -f"
echo ""

# ───────────────────────────────────────────────────────────────
# SUMMARY
# ───────────────────────────────────────────────────────────────

echo "═══════════════════════════════════════════════════════════════"
echo "✅ SERVICES RESTARTED"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Next Steps:"
echo "1. Add webhook secrets to admin panel"
echo "   URL: https://calculatentrade.com/admin/"
echo "   Path: AdminPortal → Payment gateways"
echo ""
echo "2. Test with a payment"
echo "   Monitor: sudo journalctl -u gunicorn -f"
echo "   Look for: ✅ Razorpay webhook verified"
echo ""
echo "3. Verify payment is confirmed"
echo ""
echo "═══════════════════════════════════════════════════════════════"
