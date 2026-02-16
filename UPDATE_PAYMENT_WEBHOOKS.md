# 🔗 UPDATE PAYMENT GATEWAY WEBHOOKS

**Date:** February 17, 2026  
**Status:** REQUIRED - Update webhooks to use HTTPS

---

## 📋 OVERVIEW

After migrating to the new domain (scan2food.com) and setting up HTTPS, you need to update the webhook URLs in all payment gateway dashboards. This ensures payment notifications are sent to the correct HTTPS endpoints.

---

## 🔐 WEBHOOK URLS (HTTPS)

### All Webhook Endpoints
```
Razorpay: https://scan2food.com/theatre/api/razorpay-webhook-url
Split Razorpay: https://scan2food.com/theatre/api/split-razorpay-webhook-url
Cashfree: https://scan2food.com/theatre/api/cashfree-data-request
PhonePe: https://scan2food.com/theatre/api/phonepe-data-request
PayU: https://scan2food.com/theatre/api/payu-webhook-url
CCAvenue: https://scan2food.com/theatre/api/ccavenue-hook
```

---

## 1️⃣ RAZORPAY WEBHOOK SETUP

### Step 1: Login to Razorpay Dashboard
```
URL: https://dashboard.razorpay.com/
Email: [Your email from SCAN2FOOD_CREDENTIALS.md]
Password: [Your password]
```

### Step 2: Navigate to Webhooks
1. Click on **Settings** (gear icon) in the left sidebar
2. Click on **Webhooks** under "API Keys & Webhooks"
3. If you have an existing webhook, click **Edit** or click **+ Add New Webhook**

### Step 3: Configure Webhook
```
Webhook URL: https://scan2food.com/theatre/api/razorpay-webhook-url

Active Events: Select these payment events
✓ payment.authorized
✓ payment.captured
✓ payment.failed
✓ order.paid
✓ refund.created
✓ refund.processed

Secret: [Auto-generated - copy and save if you need it for verification]
```

### Step 4: Save and Test
1. Click **Create Webhook** or **Update**
2. Click **Send Test Webhook** to verify
3. Check your application logs: `sudo journalctl -u daphne -n 50`

---

## 2️⃣ SPLIT RAZORPAY WEBHOOK (For Split Payments)

If you're using Razorpay Route (Split Payments), set up a separate webhook:

### Configure Split Webhook
```
Webhook URL: https://scan2food.com/theatre/api/split-razorpay-webhook-url

Active Events:
✓ payment.authorized
✓ payment.captured
✓ payment.failed
✓ transfer.processed
✓ transfer.failed
```

---

## 3️⃣ CASHFREE WEBHOOK SETUP

### Step 1: Login to Cashfree Dashboard
```
URL: https://merchant.cashfree.com/
Email: [Your email from SCAN2FOOD_CREDENTIALS.md]
Password: [Your password]
```

### Step 2: Navigate to Webhooks
1. Click on **Developers** in the top menu
2. Click on **Webhooks** in the left sidebar
3. Click **+ Add Webhook** or **Edit** existing webhook

### Step 3: Configure Webhook
```
Webhook URL: https://scan2food.com/theatre/api/cashfree-data-request

Webhook Events: Select these events
✓ ORDER_PAID
✓ PAYMENT_SUCCESS_WEBHOOK
✓ PAYMENT_FAILED_WEBHOOK
✓ REFUND_STATUS_WEBHOOK

Webhook Version: 2023-08-01 (use latest available)
```

### Step 4: Save and Test
1. Click **Save**
2. Use the **Test Webhook** feature in dashboard
3. Verify in logs: `sudo journalctl -u daphne -n 50`

---

## 4️⃣ PHONEPE WEBHOOK SETUP

### Important Note
PhonePe webhooks are configured by their support team. You cannot configure them yourself from a dashboard.

### Step 1: Contact PhonePe Support
```
Email: merchantsupport@phonepe.com
Subject: Update Webhook URL for Merchant ID [Your Merchant ID]
```

### Step 2: Email Template
```
Subject: Update Webhook URL for Merchant ID [Your Merchant ID]

Dear PhonePe Support Team,

I need to update the webhook URL for my merchant account.

Merchant Details:
- Merchant ID: [Your Merchant ID from credentials]
- Business Name: Scan2Food
- Registered Email: [Your registered email]
- Registered Phone: [Your registered phone]

Current Webhook URL: [Old URL if you know it]
New Webhook URL: https://scan2food.com/theatre/api/phonepe-data-request

Please update this webhook URL for all payment notifications including:
- Payment success notifications
- Payment failure notifications
- Refund status notifications

Thank you,
[Your Name]
[Your Contact Number]
```

### Step 3: Wait for Confirmation
- PhonePe support typically responds within 24-48 hours
- They will update the webhook and send confirmation
- Test with a small transaction after confirmation

---

## 5️⃣ PAYU WEBHOOK SETUP (If Used)

### Step 1: Login to PayU Dashboard
```
URL: https://onboarding.payu.in/
Email: [Your email]
Password: [Your password]
```

### Step 2: Navigate to Webhooks
1. Go to **Settings** → **Technical Settings**
2. Find **Webhook/IPN Settings**
3. Click **Edit** or **Configure**

### Step 3: Configure Webhook
```
Webhook URL: https://scan2food.com/theatre/api/payu-webhook-url

Events: Select all payment events
✓ Payment Success
✓ Payment Failed
✓ Refund Initiated
✓ Refund Completed
```

### Step 4: Save
1. Click **Save**
2. Test with a small transaction

---

## 6️⃣ CCAVENUE WEBHOOK SETUP (If Used)

### Step 1: Login to CCAvenue Dashboard
```
URL: https://dashboard.ccavenue.com/
Email: [Your email]
Password: [Your password]
```

### Step 2: Navigate to Settings
1. Go to **Settings** → **Webhooks/Notifications**
2. Find **Webhook URL** field
3. Click **Edit**

### Step 3: Configure Webhook
```
Webhook URL: https://scan2food.com/theatre/api/ccavenue-hook

Notification Events:
✓ Transaction Success
✓ Transaction Failure
✓ Refund Status
```

### Step 4: Save
1. Click **Update**
2. Test with a small transaction

---

## ✅ VERIFICATION CHECKLIST

After updating all webhooks, verify each one:

### Test Each Gateway
```bash
# SSH into server
ssh root@165.22.219.111

# Monitor logs in real-time
sudo journalctl -u daphne -f

# In another terminal window, also monitor Gunicorn
sudo journalctl -u gunicorn -f

# Test a small payment with each gateway
# Watch the logs for webhook notifications
```

### What to Look For in Logs
```
✅ "Webhook received" or similar message
✅ Payment status updated in database
✅ Order status changed to "Success"
✅ No errors or exceptions
✅ HTTP 200 response sent to gateway
```

### Test Each Gateway
1. **Razorpay**: Create test order, complete payment, check webhook
2. **Cashfree**: Create test order, complete payment, check webhook
3. **PhonePe**: Create test order, complete payment, check webhook
4. **Others**: Test if you're using them

### Verify in Admin Panel
```
1. Login to admin panel: https://scan2food.com/admin-portal/
2. Go to "All Orders" section
3. Check that payment status updates automatically
4. Verify order amount matches payment amount
```

---

## 🔍 TROUBLESHOOTING

### Common Issues and Solutions

#### Issue: Webhook returns 404 Not Found
```
Problem: Wrong webhook URL
Solution: Double-check the URL in gateway dashboard
Correct format: https://scan2food.com/theatre/api/[endpoint-name]
```

#### Issue: Webhook returns 403 Forbidden
```
Problem: Signature verification failed or API key issue
Solution: 
1. Check that API keys in admin panel match gateway dashboard
2. Verify webhook secret is correct (for Razorpay)
3. Check logs: sudo journalctl -u daphne -n 100 | grep -i webhook
```

#### Issue: Webhook returns 500 Server Error
```
Problem: Application error processing webhook
Solution:
1. Check application logs: sudo journalctl -u daphne -n 100
2. Look for Python exceptions or errors
3. Verify database connection is working
4. Check Redis is running: sudo systemctl status redis
```

#### Issue: Webhook times out
```
Problem: Server not responding or firewall blocking
Solution:
1. Check Nginx is running: sudo systemctl status nginx
2. Check Daphne is running: sudo systemctl status daphne
3. Verify firewall allows HTTPS: sudo ufw status
4. Check server load: top or htop
```

#### Issue: Payment successful but order not updated
```
Problem: Webhook received but not processed correctly
Solution:
1. Check webhook logs for errors
2. Verify payment gateway name matches in database
3. Check order ID mapping is correct
4. Look for database errors in logs
```

---

## 🔒 SECURITY NOTES

### Webhook Security Features
Your application implements these security measures:

**Razorpay:**
- HMAC SHA256 signature verification using webhook secret
- Validates X-Razorpay-Signature header

**Cashfree:**
- Signature verification using API secret
- Validates timestamp to prevent replay attacks

**PhonePe:**
- Checksum verification using salt key
- Validates X-VERIFY header

### Best Practices
1. ✅ **Always use HTTPS** for webhook URLs
2. ✅ **Never expose webhook secrets** in code or logs
3. ✅ **Always verify signatures** before processing
4. ✅ **Log all webhook attempts** for audit trail
5. ✅ **Monitor for suspicious activity** (multiple failures, wrong signatures)
6. ✅ **Use idempotency** to handle duplicate webhooks

---

## 📊 MONITORING WEBHOOKS

### View Webhook Logs
```bash
# View recent webhook activity
sudo journalctl -u daphne -n 100 | grep -i webhook

# Monitor webhooks in real-time
sudo journalctl -u daphne -f | grep -i webhook

# Check for webhook errors
sudo journalctl -u daphne --since "1 hour ago" | grep -i "webhook.*error"

# Count webhook requests by gateway
sudo journalctl -u daphne --since "today" | grep -i webhook | grep -i razorpay | wc -l
```

### Check Webhook Response Times
```bash
# View Nginx access logs for webhook endpoints
sudo tail -f /var/log/nginx/access.log | grep "api.*webhook"
```

---

## 📞 SUPPORT CONTACTS

### Payment Gateway Support

**Razorpay Support:**
- Email: support@razorpay.com
- Phone: 1800-102-0480 (India toll-free)
- Live Chat: Available on dashboard (9 AM - 9 PM IST)
- Documentation: https://razorpay.com/docs/webhooks/

**Cashfree Support:**
- Email: care@cashfree.com
- Phone: 080-68727374
- Support Portal: https://support.cashfree.com/
- Documentation: https://docs.cashfree.com/docs/webhooks

**PhonePe Support:**
- Email: merchantsupport@phonepe.com
- Response Time: 24-48 hours
- Documentation: https://developer.phonepe.com/docs/webhooks

**PayU Support:**
- Email: integration@payu.in
- Phone: 0124-4221100
- Documentation: https://devguide.payu.in/

**CCAvenue Support:**
- Email: service@ccavenue.com
- Phone: 022-4000-4444
- Documentation: https://www.ccavenue.com/

---

## 🚀 NEXT STEPS

After updating all webhooks:

### Immediate Actions
1. ✅ Update webhook URLs in all gateway dashboards
2. ✅ Test each gateway with small transactions (₹1-10)
3. ✅ Verify webhook notifications in logs
4. ✅ Check order status updates in admin panel

### Within 24 Hours
1. ✅ Monitor webhook logs for any failures
2. ✅ Test refund webhooks (if applicable)
3. ✅ Verify all payment methods work correctly
4. ✅ Check that settlement amounts are correct

### Ongoing Monitoring
1. ✅ Set up alerts for webhook failures
2. ✅ Review webhook logs weekly
3. ✅ Monitor payment success rates
4. ✅ Keep gateway API keys secure

---

## 📝 WEBHOOK TESTING COMMANDS

### Test Webhook Endpoints (from server)
```bash
# Test Razorpay webhook endpoint
curl -X POST https://scan2food.com/theatre/api/razorpay-webhook-url \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'

# Test Cashfree webhook endpoint
curl -X POST https://scan2food.com/theatre/api/cashfree-data-request \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'

# Test PhonePe webhook endpoint
curl -X POST https://scan2food.com/theatre/api/phonepe-data-request \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

Note: These are basic connectivity tests. Real webhooks will have proper signatures and data.

---

**IMPORTANT:** Keep this document updated when webhook URLs or configurations change!

**Last Updated:** February 17, 2026  
**Next Review:** After first successful transactions with each gateway
