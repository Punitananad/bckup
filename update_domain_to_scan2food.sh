#!/bin/bash
# Update Server Configuration from calculaentrade.com to scan2food.com
# Run this on production server: 165.22.219.111

echo "=========================================="
echo "Updating Domain Configuration"
echo "From: calculaentrade.com"
echo "To: scan2food.com"
echo "=========================================="

# 1. Update Django ALLOWED_HOSTS (remove old domain)
echo ""
echo "Step 1: Updating Django settings..."
cd /var/www/scan2food/application/scan2food

# Backup settings file
cp theatreApp/settings.py theatreApp/settings.py.backup

# Update ALLOWED_HOSTS to remove calculaentrade.com
sed -i "s/'calculatentrade.com', 'www.calculatentrade.com', //g" theatreApp/settings.py

echo "✓ Django settings updated"

# 2. Update Nginx configuration
echo ""
echo "Step 2: Updating Nginx configuration..."

# Check if scan2food config exists
if [ -f /etc/nginx/sites-available/scan2food ]; then
    echo "Found existing scan2food Nginx config"
    
    # Backup current config
    sudo cp /etc/nginx/sites-available/scan2food /etc/nginx/sites-available/scan2food.backup
    
    # Update server_name to use scan2food.com
    sudo sed -i 's/server_name .*/server_name scan2food.com www.scan2food.com 165.22.219.111;/g' /etc/nginx/sites-available/scan2food
    
    echo "✓ Nginx config updated"
else
    echo "Creating new Nginx configuration for scan2food.com..."
    
    sudo tee /etc/nginx/sites-available/scan2food > /dev/null <<'EOF'
server {
    listen 80;
    server_name scan2food.com www.scan2food.com 165.22.219.111;

    # Static files
    location /static/ {
        alias /var/www/scan2food/application/scan2food/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /var/www/scan2food/application/scan2food/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Proxy to Daphne for HTTP requests
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_buffering off;
    }

    # WebSocket support
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    client_max_body_size 100M;
}
EOF
    
    # Enable the site
    sudo ln -sf /etc/nginx/sites-available/scan2food /etc/nginx/sites-enabled/
    
    echo "✓ New Nginx config created"
fi

# 3. Remove old calculaentrade config if exists
if [ -f /etc/nginx/sites-enabled/calculaentrade ]; then
    echo ""
    echo "Step 3: Removing old calculaentrade configuration..."
    sudo rm /etc/nginx/sites-enabled/calculaentrade
    echo "✓ Old config removed"
fi

# 4. Test Nginx configuration
echo ""
echo "Step 4: Testing Nginx configuration..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✓ Nginx configuration is valid"
    
    # 5. Restart services
    echo ""
    echo "Step 5: Restarting services..."
    
    sudo systemctl restart nginx
    echo "✓ Nginx restarted"
    
    sudo systemctl restart daphne
    echo "✓ Daphne restarted"
    
    if systemctl is-active --quiet gunicorn; then
        sudo systemctl restart gunicorn
        echo "✓ Gunicorn restarted"
    fi
    
    echo ""
    echo "=========================================="
    echo "✅ Domain update completed successfully!"
    echo "=========================================="
    echo ""
    echo "Your site should now be accessible at:"
    echo "  - http://scan2food.com"
    echo "  - http://www.scan2food.com"
    echo "  - http://165.22.219.111"
    echo ""
    echo "Next steps:"
    echo "1. Test the site: http://165.22.219.111"
    echo "2. Wait for DNS propagation (can take up to 48 hours)"
    echo "3. Once DNS is working, install SSL certificate:"
    echo "   sudo certbot --nginx -d scan2food.com -d www.scan2food.com"
    echo ""
else
    echo "❌ Nginx configuration test failed!"
    echo "Please check the error messages above"
    exit 1
fi
