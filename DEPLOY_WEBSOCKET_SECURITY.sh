#!/bin/bash

# WebSocket Security Deployment Script
# This script deploys WebSocket authentication to production server

echo "=========================================="
echo "WEBSOCKET SECURITY DEPLOYMENT"
echo "=========================================="
echo ""

# Step 1: Push to GitHub
echo "Step 1: Pushing changes to GitHub..."
git add application/scan2food/theatre/consumers/allSeatConsumer.py
git add application/scan2food/theatre/consumers/paymentSocket.py
git commit -m "Add WebSocket security: Staff authentication for Live Orders, Order validation for Payment Status"
git push origin main

echo ""
echo "✅ Changes pushed to GitHub"
echo ""

# Step 2: Instructions for server
echo "=========================================="
echo "NOW RUN THESE COMMANDS ON SERVER:"
echo "=========================================="
echo ""
echo "# Navigate to project directory"
echo "cd /var/www/scan2food"
echo ""
echo "# Pull latest changes"
echo "git pull origin main"
echo ""
echo "# Restart Daphne service"
echo "sudo systemctl restart daphne"
echo ""
echo "# Check Daphne status"
echo "sudo systemctl status daphne"
echo ""
echo "=========================================="
echo "WHAT WAS CHANGED:"
echo "=========================================="
echo ""
echo "1. Live Orders WebSocket (allSeatConsumer.py):"
echo "   - Added authentication check"
echo "   - Only logged-in staff can connect"
echo "   - Anonymous users are rejected"
echo ""
echo "2. Payment Status WebSocket (paymentSocket.py):"
echo "   - Added order validation"
echo "   - Only valid order IDs can connect"
echo "   - Non-existent orders are rejected"
echo ""
echo "=========================================="
echo "TESTING:"
echo "=========================================="
echo ""
echo "Test 1: Live Orders (Should require login)"
echo "  - Open: https://www.calculatentrade.com/live-orders/"
echo "  - Without login: WebSocket should disconnect"
echo "  - With login: WebSocket should connect"
echo ""
echo "Test 2: Payment Status (Should validate order)"
echo "  - Valid order: wss://www.calculatentrade.com/ws/payment-socket/123/"
echo "  - Invalid order: wss://www.calculatentrade.com/ws/payment-socket/999999/"
echo "  - Invalid should disconnect immediately"
echo ""
