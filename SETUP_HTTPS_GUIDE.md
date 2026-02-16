# HTTPS/SSL Setup Guide for scan2food.com

## Prerequisites

Before setting up HTTPS, make sure:

1. ✅ Your domain `scan2food.com` is pointing to `165.22.219.111`
2. ✅ DNS has propagated (can take 1-48 hours)
3. ✅ Port 80 and 443 are open in your firewall
4. ✅ Your site is working on HTTP first

## Check DNS Propagation

From your local machine or server:

```bash
# Check if domain resolves to your server
host scan2food.com

# Should show: scan2food.com has address 165.22.219.111
```

Or use online tools:
- https://dnschecker.org
- https://www.whatsmydns.net

## Setup HTTPS/SSL

### Option 1: Automated Script (Recommended)

Run this on your production server:

```bash
# SSH to server
ssh root@165.22.219.111

# Pull latest code
cd /var/www/scan2food
git pull origin main

# Run SSL setup script
chmod +x setup_https_ssl.sh
./setup_https_ssl.sh
```

The script will:
1. Check DNS resolution
2. Install Certbot (if needed)
3. Obtain SSL certificate from Let's Encrypt
4. Configure Nginx for HTTPS
5. Update Django settings for HTTPS
6. Setup auto-renewal
7. Restart all services

### Option 2: Manual Setup

If you prefer manual setup:

```bash
# 1. Install Certbot
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# 2. Obtain SSL certificate
sudo certbot --nginx -d scan2food.com -d www.scan2food.com

# 3. Follow the prompts:
#    - Enter email: punitanand146@gmail.com
#    - Agree to terms: Yes
#    - Redirect HTTP to HTTPS: Yes (recommended)

# 4. Restart services
sudo systemctl restart nginx
sudo systemctl restart daphne

# 5. Test auto-renewal
sudo certbot renew --dry-run
```

## After HTTPS is Setup

### 1. Update Payment Gateway Webhooks

Update webhook URLs in your payment gateway dashboards:

**Razorpay:**
- Old: `http://scan2food.com/theatre/api/razorpay-webhook-url`
- New: `https://scan2food.com/theatre/api/razorpay-webhook-url`

**Cashfree:**
- Old: `http://scan2food.com/theatre/api/cashfree-data-request`
- New: `https://scan2food.com/theatre/api/cashfree-data-request`

**PhonePe:**
- Old: `http://scan2food.com/theatre/api/phonepe-data-request`
- New: `https://scan2food.com/theatre/api/phonepe-data-request`

### 2. Test Your Site

Visit these URLs and verify they work:
- https://scan2food.com
- https://www.scan2food.com
- http://scan2food.com (should redirect to HTTPS)

### 3. Check SSL Certificate

Use these tools to verify your SSL:
- https://www.ssllabs.com/ssltest/
- https://www.whynopadlock.com/

## SSL Certificate Details

- **Issuer:** Let's Encrypt
- **Validity:** 90 days
- **Auto-renewal:** Enabled (runs twice daily via cron)
- **Renewal command:** `sudo certbot renew`

## Troubleshooting

### DNS Not Propagated Yet

```bash
# Check DNS
host scan2food.com

# If it doesn't show 165.22.219.111, wait and try again later
```

### Port 80/443 Not Open

```bash
# Check firewall
sudo ufw status

# Allow ports if needed
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload
```

### Certificate Renewal Failed

```bash
# Check renewal status
sudo certbot renew --dry-run

# View logs
sudo tail -f /var/log/letsencrypt/letsencrypt.log

# Manual renewal
sudo certbot renew --force-renewal
```

### Mixed Content Warnings

If you see "mixed content" warnings in browser console:

1. Check for hardcoded HTTP URLs in templates
2. Update to use HTTPS or relative URLs
3. Check browser console for specific files

### Force HTTPS Redirect Not Working

```bash
# Check Nginx config
sudo cat /etc/nginx/sites-available/scan2food

# Should have: return 301 https://$server_name$request_uri;
# in the HTTP (port 80) server block
```

## Manual Renewal (if needed)

```bash
# Renew certificate manually
sudo certbot renew

# Restart Nginx after renewal
sudo systemctl restart nginx
```

## Certificate Expiry Reminder

Let's Encrypt certificates expire after 90 days, but auto-renewal is configured to run twice daily. You can check renewal status:

```bash
# Check certificate expiry
sudo certbot certificates

# Test renewal process
sudo certbot renew --dry-run
```

## Rollback to HTTP (Emergency Only)

If something goes wrong and you need to rollback:

```bash
# Restore backup Nginx config
sudo cp /etc/nginx/sites-available/scan2food.backup.* /etc/nginx/sites-available/scan2food

# Test and restart
sudo nginx -t
sudo systemctl restart nginx
```

## Important Notes

1. **DNS must be propagated** before running SSL setup
2. **HTTP must work first** before adding HTTPS
3. **Update payment webhooks** after HTTPS is enabled
4. **Auto-renewal is automatic** - no manual intervention needed
5. **Certificate is free** from Let's Encrypt

---

**Need Help?**

Check logs:
```bash
# Nginx logs
sudo tail -f /var/log/nginx/error.log

# Certbot logs
sudo tail -f /var/log/letsencrypt/letsencrypt.log

# Django logs
sudo journalctl -u daphne -f
```
