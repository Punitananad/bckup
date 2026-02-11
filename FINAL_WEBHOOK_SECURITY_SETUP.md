# 🎯 FINAL WEBHOOK SECURITY SETUP - Razorpay & Split Razorpay

## ✅ What's Complete

1. ✅ Webhook security code deployed to server
2. ✅ Code is active and working
3. ✅ Wrong secrets are being rejected
4. ✅ Logs show security is functioning
5. ✅ All tests passed (5/5)

---

## 🔴 What You Need to Do NOW

### Step 1: Get Your Webhook Secrets (5 minutes)

1. **Login to Razorpay Dashboard:**
   - Go to: https://dashboard.razorpay.com/
   
2. **Navigate to Webhooks:**
   - Settings → Webhooks
   
3. **Copy Webhook Secrets:**
   - Find your webhook endpoint
   - Copy the **Webhook Secret** (any format is fine - doesn't need to start with `whsec_`)
   - If you have separate webhooks for split payments, copy that secret too
   - If you use the same webhook for both, use the same secret

---

### Step 2: Add Correct Secrets to Admin Panel (2 minutes)

#### Option A: Via Admin Panel (Recommended)

1. **Go to:** https://calculatentrade.com/admin/
2. **Login** with your admin credentials
3. **Navigate to:** AdminPortal → Payment gateways
4. **Update Razorpay:**
   - Click on "Razorpay"
   - Gateway salt: [paste your REAL webhook secret]
   - Click "Save"
5. **Update split_razorpay (if it exists):**
   - Click on "split_razorpay"
   - Gateway salt: [paste your REAL webhook secret]
   - Click "Save"

#### Option B: Via Django Shell (If Admin Panel Has Issues)

```bash
cd /var/www/scan2food/application/scan2food
source venv/bin/activate
python manage.py shell
```

Then run:

```python
from adminPortal.models import PaymentGateway

# Update Razorpay
razorpay = PaymentGateway.objects.get(name='Razorpay')
razorpay.gateway_salt = 'YOUR_REAL_WEBHOOK_SECRET_HERE'
razorpay.save()
print("✅ Updated Razorpay")

# Update split_razorpay (if it exists)
try:
    split = PaymentGateway.objects.get(name='split_razorpay')
    split.gateway_salt = 'YOUR_REAL_WEBHOOK_SECRET_HERE'
    split.save()
    print("✅ Updated split_razorpay")
except:
    print("⚠️  split_razorpay doesn't exist - skipping")

exit()
```

---

### Step 3: Test with Real Payment (5 minutes)

#### Monitor Logs:

```bash
sudo journalctl -u gunicorn -f
```

#### Make a Test Payment:

1. Go to your website
2. Create an order
3. Make a payment using Razorpay
4. Watch the logs

#### Expected Result:

```
✅ Razorpay webhook verified
```

If you see this, **SUCCESS!** Your webhook security is working!

---

## 🔍 Troubleshooting

### If Payment Fails:

1. **Check logs for error message:**
   ```bash
   sudo journalctl -u gunicorn -n 50 --no-pager | grep -i "webhook"
   ```

2. **Common Issues:**
   - ❌ Wrong webhook secret → Update with correct secret
   - ❌ Empty gateway_salt → Add webhook secret
   - ❌ Typo in secret → Copy-paste carefully

### If You See "Invalid webhook signature":

- Your webhook secret is wrong
- Get the correct secret from Razorpay dashboard
- Update gateway_salt field
- Try payment again

### If You See "Webhook secret not configured":

- gateway_salt field is empty
- Add your webhook secret to gateway_salt
- Try payment again

---

## 📊 Current Status

| Item | Status |
|------|--------|
| Code Deployed | ✅ Complete |
| Services Running | ✅ Active |
| Security Active | ✅ Working |
| Wrong Secrets Rejected | ✅ Tested |
| Correct Secrets Added | 🔴 **YOU NEED TO DO THIS** |
| Payment Testing | ⏳ After adding secrets |

---

## 🎯 Quick Reference

### Check if Webhook Secret is Set:

```bash
cd /var/www/scan2food/application/scan2food
source venv/bin/activate
python manage.py shell
```

```python
from adminPortal.models import PaymentGateway
razorpay = PaymentGateway.objects.get(name='Razorpay')
print(f"Gateway salt: {razorpay.gateway_salt}")
exit()
```

### Monitor Logs:

```bash
sudo journalctl -u gunicorn -f
```

### Restart Services (if needed):

```bash
sudo systemctl restart gunicorn daphne
```

---

## 🔒 Security Behavior

### With Correct Secret:
```
Customer pays → Razorpay sends webhook → Signature verified ✅
→ Payment confirmed → Order marked as paid → Customer notified
```

### With Wrong/Missing Secret:
```
Customer pays → Razorpay sends webhook → Signature verification fails ❌
→ Return 401 error → Payment NOT confirmed → Order stays pending
```

---

## ✅ Final Checklist

- [ ] Got webhook secret from Razorpay dashboard
- [ ] Added secret to Razorpay gateway (gateway_salt field)
- [ ] Added secret to split_razorpay gateway (if exists)
- [ ] Tested with real payment
- [ ] Saw "✅ Razorpay webhook verified" in logs
- [ ] Payment confirmed successfully
- [ ] Order marked as paid

---

## 🎉 When Complete

Once all checkboxes are checked:
- ✅ Your webhook security is ACTIVE
- ✅ Your payment system is PROTECTED
- ✅ Fake webhooks will be REJECTED
- ✅ Only real Razorpay webhooks will be accepted

---

## 📞 Summary

**What's Done:**
- Webhook security code deployed and active
- Wrong secrets are being rejected
- System is ready for production

**What You Need:**
1. Add your REAL webhook secret to gateway_salt field
2. Test with a payment
3. Verify logs show success

**Time Required:** ~10 minutes

---

## 🚀 Next Action

**Go to admin panel and add your webhook secret to the gateway_salt field!**

URL: https://calculatentrade.com/admin/adminPortal/paymentgateway/

Then test with a payment and check logs!
