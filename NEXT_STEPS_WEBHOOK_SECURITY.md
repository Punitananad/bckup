# 🚀 Next Steps - Webhook Security Activation

## ✅ What's Done
- Code updated in `api_views.py`
- Webhook verification added for Razorpay and Split Razorpay
- Import added for verification function
- All changes saved to file

---

## 🔴 What You Need to Do NOW

### Step 1: Get Webhook Secrets (5 minutes)

1. Open Razorpay Dashboard: https://dashboard.razorpay.com/
2. Go to: **Settings → Webhooks**
3. Find your webhook endpoint
4. Copy the **Webhook Secret** (starts with `whsec_`)
5. If you have separate webhooks for Split Razorpay, copy that secret too

---

### Step 2: Add Secrets to Admin Panel (2 minutes)

1. Open: https://calculatentrade.com/admin/
2. Login with your admin credentials
3. Navigate to: **AdminPortal → Payment gateways**
4. Click on **Razorpay**:
   - Find field: **Gateway salt**
   - Paste: Your Razorpay webhook secret
   - Click: **Save**
5. Click on **split_razorpay**:
   - Find field: **Gateway salt**
   - Paste: Your Split Razorpay webhook secret (or same as above)
   - Click: **Save**

---

### Step 3: Restart Services (1 minute)

```bash
sudo systemctl restart gunicorn daphne
```

Wait 10 seconds, then check status:

```bash
sudo systemctl status gunicorn daphne
```

Both should show: **active (running)** in green

---

### Step 4: Test It (5 minutes)

#### Monitor Logs:
```bash
sudo journalctl -u gunicorn -f
```

#### Create Test Order:
1. Go to your website
2. Create an order
3. Make a payment
4. Watch the logs

#### Expected Log Output:
```
✅ Razorpay webhook verified
```

If you see this, **SUCCESS!** The security is working.

---

## 🔒 Security Test (Optional but Recommended)

### Test Wrong Secret:

1. Go to admin panel
2. Change `gateway_salt` to wrong value (e.g., "wrong_secret")
3. Save
4. Try to make a payment
5. Check logs - should see:
   ```
   ❌ Razorpay webhook verification failed: Invalid webhook signature
   ```
6. Payment should NOT be confirmed
7. **Change back to correct secret!**

---

## 📋 Quick Command Reference

```bash
# Restart services
sudo systemctl restart gunicorn daphne

# Check status
sudo systemctl status gunicorn daphne

# Monitor logs
sudo journalctl -u gunicorn -f

# Check if services are running
ps aux | grep -E 'gunicorn|daphne'
```

---

## ⚠️ Important Reminders

1. **Webhook Secret ≠ API Secret**
   - API Secret: Used for creating orders
   - Webhook Secret: Used for verifying webhooks
   - They are DIFFERENT values!

2. **Where to Store:**
   - ✅ Database (gateway_salt field) - CORRECT
   - ❌ .env file - NOT NEEDED

3. **Security Behavior:**
   - Wrong secret = Payment FAILS ✅
   - No secret = Payment FAILS ✅
   - Correct secret = Payment SUCCESS ✅

4. **No Backward Compatibility:**
   - This is intentional for security
   - All payments MUST have valid webhook signature

---

## 🆘 Troubleshooting

### If Services Don't Start:
```bash
# Check error logs
sudo journalctl -u gunicorn -n 50
sudo journalctl -u daphne -n 50

# Check if ports are in use
sudo netstat -tulpn | grep -E '8000|8001'
```

### If Webhook Verification Fails:
1. Check webhook secret is correct in admin panel
2. Check Razorpay dashboard webhook configuration
3. Ensure webhook URL is correct
4. Check logs for exact error message

### If Payment Doesn't Work:
1. Check logs: `sudo journalctl -u gunicorn -f`
2. Look for verification messages
3. Verify webhook secret is correct
4. Test with Razorpay test mode first

---

## 📞 Support Files

- **WEBHOOK_SECURITY_COMPLETE.md** - Full implementation details
- **SIMPLE_IMPLEMENTATION_GATEWAY_SALT.md** - Step-by-step guide
- **webhook_security.py** - Verification logic
- **api_views.py** - Updated webhook handlers

---

## ✅ Completion Checklist

- [ ] Got webhook secrets from Razorpay dashboard
- [ ] Added secrets to admin panel (Razorpay)
- [ ] Added secrets to admin panel (split_razorpay)
- [ ] Restarted gunicorn service
- [ ] Restarted daphne service
- [ ] Tested with real payment
- [ ] Saw "✅ Razorpay webhook verified" in logs
- [ ] Payment confirmed successfully
- [ ] (Optional) Tested with wrong secret to verify security

---

## 🎉 When Complete

Once all checkboxes are checked, your webhook security is ACTIVE and protecting your payment system!

**Estimated Time: 15 minutes total**
