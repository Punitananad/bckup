#!/bin/bash
# Fix static files for production

echo "=========================================="
echo "FIXING STATIC FILES FOR PRODUCTION"
echo "=========================================="

# Navigate to project
cd /var/www/scan2food/application/scan2food

# Activate virtual environment
source venv/bin/activate

echo ""
echo "1. Creating static directory..."
mkdir -p /var/www/scan2food/static

echo ""
echo "2. Updating settings to enable STATIC_ROOT..."
# We'll do this manually - see instructions below

echo ""
echo "3. Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "4. Setting correct permissions..."
sudo chown -R www-data:www-data /var/www/scan2food/static
sudo chmod -R 755 /var/www/scan2food/static

echo ""
echo "5. Restarting services..."
sudo systemctl restart gunicorn
sudo systemctl restart daphne
sudo systemctl restart nginx

echo ""
echo "=========================================="
echo "DONE! Check your website now."
echo "=========================================="
