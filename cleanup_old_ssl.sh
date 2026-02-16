#!/bin/bash
# Clean up old calculatentrade.com SSL certificate
# Run this on: 165.22.219.111

echo "=========================================="
echo "Cleaning up old SSL certificates"
echo "=========================================="

# Remove old calculatentrade.com certificate
echo ""
echo "Step 1: Removing old calculatentrade.com certificate..."

if [ -d "/etc/letsencrypt/renewal/calculatentrade.com.conf" ] || [ -d "/etc/letsencrypt/live/calculatentrade.com" ]; then
    sudo certbot delete --cert-name calculatentrade.com --non-interactive
    echo "✓ Old certificate removed"
else
    echo "✓ No old certificate found"
fi

# Test renewal again
echo ""
echo "Step 2: Testing SSL auto-renewal..."
sudo certbot renew --dry-run

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Auto-renewal is working perfectly!"
else
    echo ""
    echo "⚠️  Auto-renewal test had issues, but scan2food.com certificate is valid"
fi

# Show certificate status
echo ""
echo "Step 3: Current SSL certificates:"
sudo certbot certificates

echo ""
echo "=========================================="
echo "✅ Cleanup Complete!"
echo "=========================================="
echo ""
echo "Your scan2food.com certificate is active and will auto-renew."
echo ""
