# 🔧 FIX WHATSAPP MESSAGE SENDING ISSUE

**Problem:** Can receive WhatsApp messages but cannot send (order confirmations not going)

---

## 🔍 QUICK DIAGNOSIS

Run this on your server to check the issue:

```bash
# SSH into server
ssh root@165.22.219.111

# Navigate to project
cd /var/www/scan2food

# Run diagnostic test
python3 test_whatsapp_api.py
```

This will tell you exactly what's wrong.

---

## 🚨 COMMON CAUSES

### 1. Access Token Expired
**Symptoms:** API returns 401 or 403 error

**Solution:**
1. Go to Meta Business Manager: https://business.facebook.com/
2. Navigate to: WhatsApp > API Setup
3. Click "Generate Access Token"
4. Select "Never Expire" option
5. Copy the new token
6. Update in `application/scan2food/chat_bot/whatsapp_msg_utils.py` line 11
7. Push to Git and pull on server
8. Restart services

### 2. Message Templates Not Approved
**Symptoms:** Messages fail silently or return template error

**Solution:**
1. Go to Meta Business Manager
2. Navigate to: WhatsApp > Message Templates
3. Check status of these templates:
   - `new_order_confirmation_`
   - `refund_confirmed`
   - `refund_query`
   - `activate_service`
   - `deactivate_service`
4. If status is "Pending" - wait for approval (1-24 hours)
5. If status is "Rejected" - edit and resubmit
6. If missing - create new templates

### 3. Phone Number Not Verified
**Symptoms:** All API calls fail

**Solution:**
1. Go to Meta Business Manager
2. Navigate to: WhatsApp > Phone Numbers
3. Verify your phone number
4. Complete business verification if required

### 4. Insufficient Permissions
**Symptoms:** 403 Forbidden errors

**Solution:**
1. Go to Meta Business Manager
2. Settings > Business Settings > System Users
3. Find your system user
4. Add permissions:
   - whatsapp_business_messaging
   - whatsapp_business_management

### 5. Rate Limit Exceeded
**Symptoms:** Messages fail after sending many

**Solution:**
1. Check your WhatsApp Business tier
2. Upgrade tier if needed
3. Wait for rate limit to reset (24 hours)

### 6. Wrong API Version
**Symptoms:** API returns "method not found"

**Solution:**
- Current code uses v18.0
- Check if Meta deprecated this version
- Update to latest version in `whatsapp_msg_utils.py`

---

## 📊 CHECK SERVER LOGS

To see actual error messages:

```bash
# SSH into server
ssh root@165.22.219.111

# Check Daphne logs for WhatsApp errors
sudo journalctl -u daphne -n 100 | grep -i whatsapp

# Check Gunicorn logs
sudo journalctl -u gunicorn -n 100 | grep -i whatsapp

# Check for API errors
sudo journalctl -u daphne -n 100 | grep -i "error\|failed"
```

---

## 🧪 TEST MESSAGE SENDING

Create a test script on server:

```bash
# SSH into server
ssh root@165.22.219.111

# Navigate to Django project
cd /var/www/scan2food/application/scan2food

# Activate virtual environment
source venv/bin/activate

# Open Django shell
python manage.py shell
```

Then run this in Django shell:

```python
from chat_bot.whatsapp_msg_utils import send_order_confirmation_message

# Test with your phone number (include country code)
result = send_order_confirmation_message(
    phone_number="919876543210",  # Replace with your number
    theatre_name="Test Theatre",
    seat_name="A1",
    order_pk=1
)

print(result)
```

Check your WhatsApp for the message.

---

## 🔑 UPDATE ACCESS TOKEN

If token expired, follow these steps:

### Step 1: Generate New Token
1. Go to https://business.facebook.com/
2. Select your business
3. Go to WhatsApp > API Setup
4. Click "Generate Access Token"
5. Select these permissions:
   - whatsapp_business_messaging
   - whatsapp_business_management
6. Select "Never Expire" (recommended)
7. Copy the token

### Step 2: Update Code
```bash
# On your local machine
# Edit: application/scan2food/chat_bot/whatsapp_msg_utils.py
# Line 11: ACCESS_TOKEN = "YOUR_NEW_TOKEN_HERE"
```

### Step 3: Deploy
```bash
# Local machine
git add application/scan2food/chat_bot/whatsapp_msg_utils.py
git commit -m "Update WhatsApp access token"
git push origin main

# Server
ssh root@165.22.219.111
cd /var/www/scan2food
git pull origin main
sudo systemctl restart daphne
sudo systemctl restart gunicorn
```

---

## 📋 VERIFY CONFIGURATION

Check these values in `whatsapp_msg_utils.py`:

```python
ACCESS_TOKEN = "EAAJph1TVFoo..."  # Should be long (200+ chars)
PHONE_NUMBER_ID = "706345399217798"  # Your WhatsApp Business phone ID
VERIFY_TOKEN = "scan2food_my_token"  # Webhook verification token
```

**How to find these:**
1. **ACCESS_TOKEN**: Meta Business Manager > WhatsApp > API Setup
2. **PHONE_NUMBER_ID**: Meta Business Manager > WhatsApp > API Setup (shown as "Phone Number ID")
3. **VERIFY_TOKEN**: This is set by you for webhook verification

---

## 🔄 WEBHOOK CONFIGURATION

Make sure webhook is configured correctly:

1. Go to Meta Business Manager
2. Navigate to: WhatsApp > Configuration
3. Webhook URL should be: `https://scan2food.com/chat-bot/webhook/`
4. Verify Token: `scan2food_my_token`
5. Subscribe to these fields:
   - messages
   - message_status (optional)

---

## ✅ VERIFICATION CHECKLIST

After fixing, verify:

- [ ] Access token is valid (not expired)
- [ ] All message templates are approved
- [ ] Phone number is verified
- [ ] Permissions are granted
- [ ] Webhook is configured
- [ ] Services restarted
- [ ] Test message sent successfully

---

## 📞 SUPPORT

If still not working:

**Meta Support:**
- WhatsApp Business API Support: https://business.facebook.com/help
- Developer Support: https://developers.facebook.com/support

**Check Status:**
- Meta Status: https://metastatus.com/
- WhatsApp Business API Status

---

**Last Updated:** February 17, 2026
