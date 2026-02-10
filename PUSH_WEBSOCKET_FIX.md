# Push WebSocket Fix to GitHub

## Step 1: Check what changed
```bash
git status
```

## Step 2: Add the changes
```bash
git add application/scan2food/theatreApp/settings.py
git add WEBSOCKET_FIX_INSTRUCTIONS.md
git add deploy_websocket_fix.sh
git add check_websocket_config.sh
git add SETUP_WEBSOCKET.md
git add fix_websocket_complete.sh
git add PUSH_WEBSOCKET_FIX.md
```

## Step 3: Commit the changes
```bash
git commit -m "Fix WebSocket: Switch CHANNEL_LAYERS to InMemoryChannelLayer (Redis disabled)"
```

## Step 4: Push to GitHub
```bash
git push origin main
```

## Step 5: Deploy on Server
Now SSH to your server and run:
```bash
cd /var/www/scan2food
git pull origin main
cd application/scan2food
source venv/bin/activate
sudo systemctl restart daphne gunicorn nginx
```

## Step 6: Verify
```bash
# Check services
sudo systemctl status daphne

# Check port
sudo ss -tlnp | grep 8001

# Test WebSocket
curl -I http://127.0.0.1:8001/ws/all-seat-datasocket/
```

## Quick Commands (Copy-Paste)
```bash
# Local machine - Push changes
git add -A
git commit -m "Fix WebSocket: Switch CHANNEL_LAYERS to InMemoryChannelLayer"
git push origin main

# Server - Deploy changes
cd /var/www/scan2food && git pull origin main && cd application/scan2food && source venv/bin/activate && sudo systemctl restart daphne gunicorn nginx
```
