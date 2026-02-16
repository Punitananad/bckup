#!/bin/bash
# Fix Static Files on Production Server
# Run this on: 165.22.219.111

echo "=========================================="
echo "Fixing Static Files Configuration"
echo "=========================================="

# 1. Navigate to Django project
cd /var/www/scan2food/application/scan2food

# 2. Activate virtual environment
source /var/www/scan2food/application/scan2food/venv/bin/activate

# 3. Create static root directory if it doesn't exist
echo ""
echo "Step 1: Creating static directories..."
sudo mkdir -p /var/www/scan2food/static
sudo chown -R www-data:www-data /var/www/scan2food/static
echo "✓ Static directory created"

# 4. Collect static files
echo ""
echo "Step 2: Collecting static files..."
python manage.py collectstatic --noinput --clear
echo "✓ Static files collected"

# 5. Set proper permissions
echo ""
echo "Step 3: Setting permissions..."
sudo chown -R www-data:www-data /var/www/scan2food/static
sudo chmod -R 755 /var/www/scan2food/static
echo "✓ Permissions set"

# 6. Update Nginx configuration for static files
echo ""
echo "Step 4: Updating Nginx configuration..."

sudo tee /etc/nginx/sites-available/scan2food > /dev/null <<'EOF'
server {
    listen 80;
    server_name scan2food.com www.scan2food.com 165.22.219.111;

    # Static files - UPDATED PATH
    location /static/ {
        alias /var/www/scan2food/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Media files
    location /media/ {
        alias /var/www/scan2food/application/scan2food/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
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

echo "✓ Nginx configuration updated"

# 7. Test Nginx configuration
echo ""
echo "Step 5: Testing Nginx configuration..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✓ Nginx configuration is valid"
    
    # 8. Restart services
    echo ""
    echo "Step 6: Restarting services..."
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
    echo "✅ Static files fixed successfully!"
    echo "=========================================="
    echo ""
    echo "Static files location: /var/www/scan2food/static/"
    echo ""
    echo "Test your site now:"
    echo "  - http://165.22.219.111"
    echo "  - http://scan2food.com"
    echo ""
    echo "If CSS still doesn't load, check browser console for errors"
    echo "and run: sudo tail -f /var/log/nginx/error.log"
    echo ""
else
    echo "❌ Nginx configuration test failed!"
    echo "Please check the error messages above"
    exit 1
fi
