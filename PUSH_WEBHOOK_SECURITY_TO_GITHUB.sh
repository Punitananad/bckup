#!/bin/bash

# ═══════════════════════════════════════════════════════════════
# PUSH WEBHOOK SECURITY CODE TO GITHUB
# ═══════════════════════════════════════════════════════════════

echo "🚀 Pushing webhook security implementation to GitHub..."
echo ""

# Step 1: Check git status
echo "📋 Step 1: Checking git status..."
git status
echo ""

# Step 2: Add all changes
echo "➕ Step 2: Adding all changes..."
git add .
echo ""

# Step 3: Commit changes
echo "💾 Step 3: Committing changes..."
git commit -m "Add webhook security verification for Razorpay and Split Razorpay

- Added webhook signature verification to api_views.py
- Import verify_webhook_request from webhook_security
- Updated razporpay_webhook_url with signature verification
- Updated split_razporpay_webhook_url with signature verification
- Returns 401 error for invalid/missing webhook signatures
- Uses gateway_salt field for webhook secret storage
- Strict security: wrong secret = payment fails"
echo ""

# Step 4: Push to GitHub
echo "🌐 Step 4: Pushing to GitHub (main branch)..."
git push origin main
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "✅ CODE PUSHED TO GITHUB"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Next Steps:"
echo "1. SSH to server: ssh root@your-server-ip"
echo "2. Pull code: cd /var/www/scan2food && git pull origin main"
echo "3. Add webhook secrets to admin panel"
echo "4. Restart services: sudo systemctl restart gunicorn daphne"
echo ""
echo "═══════════════════════════════════════════════════════════════"
