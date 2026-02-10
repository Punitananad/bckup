# Razorpay Webhook Setup Guide

## Webhook URL
Your Razorpay webhook URL is:
```
https://calculatentrade.com/theatre/api/razorpay-webhook-url
```

## Setup Steps in Razorpay Dashboard

1. **Log in to Razorpay Dashboard**
   - Go to: https://dashboard.razorpay.com/

2. **Navigate to Webhooks**
   - Click on "Settings" in the left sidebar
   - Click on "Webhooks"

3. **Create New Webhook**
   - Click "Add New Webhook"
   - Enter the webhook URL: `https://calculatentrade.com/theatre/api/razorpay-webhook-url`
   - Select the following events:
     - ✅ `payment.captured`
     - ✅ `payment.failed`
   - Set "Active" to ON
   - Click "Create Webhook"

4. **Note the Webhook Secret**
   - After creating, you'll see a webhook secret
   - Copy this secret (you may need it for signature verification)

## Testing the Webhook

### Method 1: Using Razorpay Dashboard
1. Go to your webhook in Razorpay dashboard
2. Click "Test Webhook"
3. Select "payment.captured" event
4. Click "Send Test Webhook"

### Method 2: Make a Test Payment
1. Create a test order on your site
2. Complete the payment using test card details
3. Check if the order status updates

## Troubleshooting

### Webhook Not Receiving Events
- Check if the webhook URL is accessible: `curl https://calculatentrade.com/theatre/api/razorpay-webhook-url`
- Check Gunicorn logs: `sudo journalctl -u gunicorn -f`
- Check Nginx logs: `sudo tail -f /var/log/nginx/error.log`

### Webhook Returns 403 Forbidden
- ✅ Fixed! The `@csrf_exempt` decorator has been added

### Webhook Returns 500 Error
- Check the application logs for detailed error messages
- Verify the payment gateway is configured correctly in admin panel

## WebSocket Issues (Live Updates)

The WebSocket errors you're seeing are separate from the webhook. To fix WebSocket:

### Option 1: Setup Daphne Service
Create `/etc/systemd/system/daphne.service`:
```ini
[Unit]
Description=Daphne ASGI Server
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/scan2food/application/scan2food
ExecStart=/var/www/scan2food/application/scan2food/venv/bin/daphne -b 0.0.0.0 -p 8001 theatreApp.asgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable daphne
sudo systemctl start daphne
```

### Option 2: Disable WebSocket Features (Quick Fix)
If you don't need real-time updates, you can disable WebSocket features temporarily.

## Verify Webhook is Working

After setup, check the webhook logs in Razorpay dashboard:
1. Go to Settings > Webhooks
2. Click on your webhook
3. Check the "Recent Deliveries" tab
4. You should see successful deliveries (200 OK status)

## Important Notes

- Webhook URL must be HTTPS (✅ you have this)
- Webhook must return 200 OK status (✅ fixed)
- CSRF must be exempted for webhooks (✅ fixed)
- Make sure Razorpay gateway name in admin is exactly "Razorpay" (✅ you have this)
