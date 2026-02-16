#!/bin/bash
# Setup HTTPS/SSL for scan2food.com
# Run this on: 165.22.219.111

echo "=========================================="
echo "Setting up HTTPS/SSL for scan2food.com"
echo "=========================================="

# Check if domain is resolving
echo ""
echo "Step 1: Checking DNS resolution..."
if host scan2food.com | grep -q "165.22.219.111"; then
    echo "✓ scan2food.com resolves to 165.22.219.111"
else
    echo "⚠️  WARNING: scan2food.com does not resolve to this server yet"
    echo "DNS propagation may still be in progress"
    echo ""
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting. Please wait for DNS to propagate and try again."
        exit 1
    fi
fi

# Install certbot if not already installed
echo ""
echo "Step 2: Installing Certbot..."
if ! command -v certbot &> /dev/null; then
    sudo apt update
    sudo apt install -y certbot python3-certbot-nginx
    echo "✓ Certbot installed"
else
    echo "✓ Certbot already installed"
fi

# Backup current Nginx config
echo ""
echo "Step 3: Backing up Nginx configuration..."
sudo cp /etc/nginx/sites-available/scan2food /etc/nginx/sites-available/scan2food.backup.$(date +%Y%m%d_%H%M%S)
echo "✓ Backup created"

# Test Nginx configuration
echo ""
echo "Step 4: Testing current Nginx configuration..."
sudo nginx -t
if [ $? -ne 0 ]; then
    echo "❌ Nginx configuration has errors. Please fix them first."
    exit 1
fi
echo "✓ Nginx configuration is valid"

# Obtain SSL certificate
echo ""
echo "Step 5: Obtaining SSL certificate from Let's Encrypt..."
echo "This will:"
echo "  - Verify domain ownership"
echo "  - Issue SSL certificate"
echo "  - Automatically configure Nginx"
echo "  - Setup auto-renewal"
echo ""

sudo certbot --nginx -d scan2food.com -d www.scan2food.com --non-interactive --agree-tos --email punitanand146@gmail.com --redirect

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ SSL certificate obtained and installed successfully!"
    
    # Update Django settings for HTTPS
    echo ""
    echo "Step 6: Updating Django settings for HTTPS..."
    
    cd /var/www/scan2food/application/scan2food
    
    # Check if HTTPS settings already exist
    if ! grep -q "SECURE_SSL_REDIRECT" theatreApp/settings.py; then
        cat >> theatreApp/settings.py << 'DJANGO_HTTPS'

# HTTPS/SSL Settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
DJANGO_HTTPS
        echo "✓ HTTPS settings added to Django"
    else
        echo "✓ HTTPS settings already exist in Django"
    fi
    
    # Update CSRF_TRUSTED_ORIGINS for HTTPS
    if grep -q "CSRF_TRUSTED_ORIGINS" theatreApp/settings.py; then
        sed -i "s|http://scan2food.com|https://scan2food.com|g" theatreApp/settings.py
        sed -i "s|http://www.scan2food.com|https://www.scan2food.com|g" theatreApp/settings.py
        echo "✓ CSRF_TRUSTED_ORIGINS updated for HTTPS"
    fi
    
    # Restart services
    echo ""
    echo "Step 7: Restarting services..."
    sudo systemctl restart nginx
    echo "✓ Nginx restarted"
    
    sudo systemctl restart daphne
    echo "✓ Daphne restarted"
    
    if systemctl is-active --quiet gunicorn; then
        sudo systemctl restart gunicorn
        echo "✓ Gunicorn restarted"
    fi
    
    # Test auto-renewal
    echo ""
    echo "Step 8: Testing SSL auto-renewal..."
    sudo certbot renew --dry-run
    
    if [ $? -eq 0 ]; then
        echo "✓ Auto-renewal is configured correctly"
    else
        echo "⚠️  Auto-renewal test failed, but certificate is still valid"
    fi
    
    echo ""
    echo "=========================================="
    echo "✅ HTTPS/SSL Setup Complete!"
    echo "=========================================="
    echo ""
    echo "Your site is now accessible via HTTPS:"
    echo "  - https://scan2food.com"
    echo "  - https://www.scan2food.com"
    echo ""
    echo "Certificate Details:"
    echo "  - Issuer: Let's Encrypt"
    echo "  - Valid for: 90 days"
    echo "  - Auto-renewal: Enabled (runs twice daily)"
    echo ""
    echo "HTTP traffic will automatically redirect to HTTPS"
    echo ""
    echo "Next steps:"
    echo "1. Test your site: https://scan2food.com"
    echo "2. Update payment gateway webhook URLs to use HTTPS"
    echo "3. Update any hardcoded HTTP URLs in your code"
    echo ""
    
else
    echo ""
    echo "❌ SSL certificate installation failed!"
    echo ""
    echo "Common reasons:"
    echo "1. DNS not propagated yet (wait 24-48 hours)"
    echo "2. Port 80/443 not open in firewall"
    echo "3. Domain not pointing to this server"
    echo ""
    echo "Check DNS with: host scan2food.com"
    echo "Check firewall: sudo ufw status"
    echo ""
    echo "Try again later or check certbot logs:"
    echo "sudo tail -f /var/log/letsencrypt/letsencrypt.log"
    exit 1
fi
