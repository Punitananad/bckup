# WebSocket Setup Guide for Scan2Food

## Overview
This guide covers the complete WebSocket setup for the Scan2Food application using Django Channels and Daphne.

## Architecture
- **Daphne**: ASGI server handling WebSocket connections (port 8001)
- **Gunicorn**: WSGI server handling HTTP requests (port 8000)
- **Nginx**: Reverse proxy routing traffic to appropriate backend
- **Django Channels**: WebSocket framework with InMemoryChannelLayer

## Current Status: ✅ CONFIGURED

### WebSocket Routes
1. `wss://calculatentrade.com/ws/all-seat-datasocket/` - Theatre seat updates
2. `wss://calculatentrade.com/ws/payment-socket/<id>/` - Payment status updates
3. `wss://calculatentrade.com/ws/chat-socket/` - Chat functionality

## Configuration Files

### 1. ASGI Configuration (`theatreApp/asgi.py`)
```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'theatreApp.settings')
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import URLRouter, ProtocolTypeRouter
from channels.auth import AuthMiddlewareStack
from theatre.routing import urlpatterns as theatre_url
from chat_box.routing import urlpatternss as chat_urls

urlpatterns = theatre_url + chat_urls

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(urlpatterns)
    )
})
```

### 2. Django Settings (`theatreApp/settings.py`)
```python
INSTALLED_APPS = [
    'daphne',  # Must be first
    'channels',
    # ... other apps
]

ASGI_APPLICATION = 'theatreApp.asgi.application'

# Using InMemoryChannelLayer (Redis disabled)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    },
}
```

### 3. Daphne Service (`/etc/systemd/system/daphne.service`)
```ini
[Unit]
Description=Daphne ASGI Server for Scan2Food
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/scan2food/application/scan2food
Environment="PATH=/var/www/scan2food/application/scan2food/venv/bin"
ExecStart=/var/www/scan2food/application/scan2food/venv/bin/daphne -b 127.0.0.1 -p 8001 theatreApp.asgi:application
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 4. Nginx Configuration (`/etc/nginx/sites-available/scan2food`)
```nginx
# WebSocket proxy
location /ws/ {
    proxy_pass http://127.0.0.1:8001;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 86400;
}

# Regular HTTP traffic
location / {
    proxy_pass http://127.0.0.1:8000;
    # ... other proxy settings
}
```

## Deployment Steps

### Quick Deploy
```bash
cd /var/www/scan2food
bash deploy_websocket_fix.sh
```

### Manual Deploy
```bash
# 1. Navigate to project
cd /var/www/scan2food

# 2. Pull latest changes
git pull origin main

# 3. Activate virtual environment
cd application/scan2food
source venv/bin/activate

# 4. Restart services
sudo systemctl restart daphne
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# 5. Verify services
sudo systemctl status daphne
sudo systemctl status gunicorn
sudo systemctl status nginx
```

## Troubleshooting

### Check Service Status
```bash
sudo systemctl status daphne
sudo journalctl -u daphne -f
```

### Check Port 8001
```bash
sudo ss -tlnp | grep 8001
```

### Test WebSocket Endpoint
```bash
# Test Daphne directly
curl -I http://127.0.0.1:8001/ws/all-seat-datasocket/

# Test through Nginx
curl -I https://calculatentrade.com/ws/all-seat-datasocket/
```

### Common Issues

#### 1. Daphne Not Running
```bash
sudo systemctl start daphne
sudo systemctl enable daphne
```

#### 2. Redis Connection Error
**Solution**: We're using InMemoryChannelLayer instead of Redis.
If you see Redis errors, verify `CHANNEL_LAYERS` in settings.py uses `InMemoryChannelLayer`.

#### 3. 404 on WebSocket Routes
**Cause**: ASGI routing not configured properly
**Solution**: Verify `theatreApp/asgi.py` includes WebSocket routing

#### 4. Connection Upgrade Failed
**Cause**: Nginx not forwarding WebSocket headers
**Solution**: Verify Nginx has `Upgrade` and `Connection` headers in `/ws/` location block

### View Logs
```bash
# Daphne logs
sudo journalctl -u daphne -n 50 --no-pager

# Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Nginx access logs
sudo tail -f /var/log/nginx/access.log
```

## Testing WebSocket Connection

### Browser Console Test
```javascript
// Open browser console on https://calculatentrade.com
const ws = new WebSocket('wss://calculatentrade.com/ws/all-seat-datasocket/');

ws.onopen = () => console.log('✓ WebSocket connected');
ws.onerror = (error) => console.error('✗ WebSocket error:', error);
ws.onmessage = (event) => console.log('Message:', event.data);
ws.onclose = () => console.log('WebSocket closed');
```

### Expected Output
```
✓ WebSocket connected
```

## Important Notes

1. **InMemoryChannelLayer Limitation**: 
   - Works only with single server
   - For multi-server setup, enable Redis

2. **Redis Setup** (Future):
   ```python
   CHANNEL_LAYERS = {
       "default": {
           "BACKEND": "channels_redis.core.RedisChannelLayer",
           "CONFIG": {
               "hosts": [("127.0.0.1", 6379)],
           },
       },
   }
   ```

3. **Service Restart Order**:
   - Always restart Daphne first
   - Then Gunicorn
   - Finally Nginx

4. **SSL/TLS**:
   - WebSocket uses `wss://` (secure)
   - Nginx handles SSL termination
   - Daphne receives plain HTTP/WebSocket

## Service Management Commands

```bash
# Start services
sudo systemctl start daphne
sudo systemctl start gunicorn
sudo systemctl start nginx

# Stop services
sudo systemctl stop daphne
sudo systemctl stop gunicorn
sudo systemctl stop nginx

# Restart services
sudo systemctl restart daphne
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# Enable on boot
sudo systemctl enable daphne
sudo systemctl enable gunicorn
sudo systemctl enable nginx

# View status
sudo systemctl status daphne
sudo systemctl status gunicorn
sudo systemctl status nginx
```

## Next Steps

1. ✅ Daphne service configured
2. ✅ ASGI routing configured
3. ✅ Nginx WebSocket proxy configured
4. ✅ Channel layers configured (InMemoryChannelLayer)
5. 🔄 Deploy and test
6. ⏳ Monitor WebSocket connections in production

## Support

If issues persist:
1. Run diagnostic: `bash check_websocket_config.sh`
2. Check Daphne logs: `sudo journalctl -u daphne -f`
3. Check Nginx logs: `sudo tail -f /var/log/nginx/error.log`
4. Verify ASGI configuration in `theatreApp/asgi.py`
