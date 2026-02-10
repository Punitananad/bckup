# Fix 500 Error on Production Server

## Step 1: Activate Virtual Environment
```bash
cd /var/www/scan2food
source venv/bin/activate
```

## Step 2: Check Django Logs
```bash
# Check the application log file
tail -n 100 guru.log

# Or check for any error logs in the application directory
tail -n 100 application/scan2food/guru.log
```

## Step 3: Check Gunicorn/Daphne Service Status
```bash
# Check if services are running
sudo systemctl status gunicorn
sudo systemctl status daphne

# Check service logs
sudo journalctl -u gunicorn -n 100 --no-pager
sudo journalctl -u daphne -n 100 --no-pager
```

## Step 4: Check Nginx Logs
```bash
# Check nginx error logs
sudo tail -n 100 /var/log/nginx/error.log

# Check nginx access logs
sudo tail -n 100 /var/log/nginx/access.log
```

## Step 5: Run Django Check
```bash
cd /var/www/scan2food/application/scan2food
python manage.py check --deploy
```

## Step 6: Test Database Connection
```bash
# Try to connect to database
python manage.py dbshell
# Type \q to exit if PostgreSQL, or .exit if SQLite
```

## Step 7: Check Environment Variables
```bash
# Check if .env file exists and has correct values
cat /var/www/scan2food/application/scan2food/.env
```

## Common 500 Error Causes:

1. **Missing Environment Variables**
   - Check if SECRET_KEY, DATABASE_URL, etc. are set

2. **Database Connection Issues**
   - Verify database credentials
   - Check if database service is running

3. **Missing Static Files**
   - Run: `python manage.py collectstatic --noinput`

4. **Permission Issues**
   - Check file permissions: `ls -la /var/www/scan2food`
   - Fix permissions: `sudo chown -R www-data:www-data /var/www/scan2food`

5. **Missing Dependencies**
   - Reinstall: `pip install -r requirements.txt`

6. **Migration Issues**
   - Run: `python manage.py migrate`

## Quick Fix Commands:

```bash
# Navigate to project
cd /var/www/scan2food
source venv/bin/activate
cd application/scan2food

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart services
sudo systemctl restart gunicorn
sudo systemctl restart daphne
sudo systemctl restart nginx

# Check status
sudo systemctl status gunicorn
sudo systemctl status daphne
```

## If Still Getting 500 Error:

1. Enable DEBUG temporarily to see detailed error:
   ```bash
   # Edit settings.py
   nano /var/www/scan2food/application/scan2food/theatreApp/settings.py
   # Change DEBUG = False to DEBUG = True
   # Save and restart services
   ```

2. Check the browser console and network tab for more details

3. Look at the specific error in logs and share it for further debugging
