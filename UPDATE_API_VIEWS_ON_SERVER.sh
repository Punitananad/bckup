#!/bin/bash
# Script to update api_views.py with webhook security

echo "Updating api_views.py with webhook security..."

cd /var/www/scan2food/application/scan2food/theatre

# Backup original file
cp api_views.py api_views.py.backup

# Add the import at the top (after other imports)
# Find the line with "from .update_websocket import" and add after it
sed -i '/from \.update_websocket import/a from .webhook_security import verify_webhook_request' api_views.py

echo "✅ Added import"
echo ""
echo "Now you need to manually add verification to webhook functions:"
echo ""
echo "1. Edit api_views.py:"
echo "   nano api_views.py"
echo ""
echo "2. Find 'def razporpay_webhook_url(request):' (around line 936)"
echo "   Add after 'if request.method == 'POST':':"
echo ""
echo "   gateway_detail = PaymentGateway.objects.get(name='Razorpay')"
echo "   is_valid, error_message = verify_webhook_request(request, 'Razorpay', gateway_detail.gateway_salt)"
echo "   if not is_valid:"
echo "       print(f'❌ Razorpay webhook verification failed: {error_message}')"
echo "       return JsonResponse({'status': 'error', 'message': 'Invalid signature'}, status=401)"
echo "   print('✅ Razorpay webhook verified')"
echo ""
echo "3. Find 'def split_razporpay_webhook_url(request):' (around line 1020)"
echo "   Add the same verification code but use 'split_razorpay'"
echo ""
echo "Backup saved as: api_views.py.backup"
