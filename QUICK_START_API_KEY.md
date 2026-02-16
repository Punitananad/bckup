# Quick Start: API Key Security

## 🚀 Deploy in 5 Minutes

### Step 1: Generate Key (30 seconds)
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
Copy the output.

### Step 2: Add to Environment (1 minute)
```bash
# On server
nano /var/www/scan2food/application/scan2food/.env

# Add this line (paste your key from Step 1):
API_KEY=paste_your_key_here

# Save: Ctrl+X, Y, Enter
```

### Step 3: Deploy Code (2 minutes)
```bash
# On server
cd /var/www/scan2food
git pull origin main
```

### Step 4: Restart Services (1 minute)
```bash
sudo systemctl restart gunicorn
sudo systemctl restart daphne
```

### Step 5: Test (1 minute)
```bash
# Should return 401 error:
curl https://scan2food.com/theatre/api/all-menu/1

# Should show: {"error": "Invalid or missing API key", "status": 401}
```

## ✅ Done!

Your endpoints are now protected. Old developer is blocked.

## 📊 Monitor

```bash
# Watch for unauthorized access attempts:
tail -f /var/log/gunicorn/error.log | grep "API key validation failed"
```

## 🔄 Rotate Key (if needed)

```bash
# Generate new key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update .env with new key
nano /var/www/scan2food/application/scan2food/.env

# Restart
sudo systemctl restart gunicorn
sudo systemctl restart daphne
```

## 📖 Full Documentation

- **Deployment Guide**: `API_KEY_DEPLOYMENT_GUIDE.md`
- **Implementation Summary**: `API_KEY_IMPLEMENTATION_SUMMARY.md`
- **Test Script**: `python test_api_key_security.py`

## ❓ Troubleshooting

**Customers can't order?**
- Check API key is in `.env`
- Verify services restarted
- Check logs: `tail -f /var/log/gunicorn/error.log`

**Webhooks not working?**
- They should work without API key
- Check payment gateway logs
- Verify webhook URLs contain "webhook"

**Need help?**
- Read `API_KEY_DEPLOYMENT_GUIDE.md`
- Run `python test_api_key_security.py`
- Check service status: `sudo systemctl status gunicorn`
