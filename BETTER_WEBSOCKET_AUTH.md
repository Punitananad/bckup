# Better WebSocket Authentication Strategy

## Current Problem
- API keys are hardcoded in JavaScript files
- Anyone can view source and steal the keys
- Keys are static and shared across all users
- This is "security theater" not real security

## Better Solution: Session-Based Authentication

### Why Session Auth?
1. Users are already logged in via Django sessions
2. Session cookies are httpOnly (can't be stolen via JS)
3. Each user has their own session
4. No keys exposed in frontend code

### Implementation Plan

#### Step 1: Update Consumer to Use Session Auth

```python
from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

class AllSeatConsumers(AsyncWebsocketConsumer):
    async def connect(self):
        # Get user from session
        user = self.scope.get('user', AnonymousUser())
        
        # Check if user is authenticated
        if not user.is_authenticated:
            await self.close()
            return
        
        # Optional: Check if user has permission
        # if not await self.user_has_permission(user):
        #     await self.close()
        #     return
        
        self.group_name = "all-seat-status"
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
    
    @database_sync_to_async
    def user_has_permission(self, user):
        # Check if user is staff or has specific permission
        return user.is_staff or user.has_perm('theatre.view_orders')
```

#### Step 2: Update ASGI Application

```python
# theatreApp/asgi.py
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import theatre.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(  # Add this wrapper
        URLRouter(
            theatre.routing.websocket_urlpatterns
        )
    ),
})
```

#### Step 3: Update Frontend (Remove API Keys)

```javascript
// No more API keys in URL!
const ws_url = `wss://${window.location.host}/ws/all-seat-datasocket/`;
const socket = new WebSocket(ws_url);

// Session cookie is automatically sent with WebSocket connection
```

### Benefits
1. ✅ No keys in frontend code
2. ✅ Uses existing Django authentication
3. ✅ Per-user sessions (can track who's connected)
4. ✅ Can add role-based access control
5. ✅ Session cookies are httpOnly and secure

### Migration Path

**Option A: Quick Fix (Keep Current System)**
- Move keys to environment variables only
- Add IP whitelist for WebSocket connections
- Add rate limiting

**Option B: Proper Fix (Session Auth)**
- Implement session-based auth (30 minutes work)
- Remove all API keys from frontend
- Add permission checks
- Much more secure

## Recommendation

For production, use **Option B (Session Auth)**.

The current API key system is vulnerable to:
- Key theft via browser DevTools
- Key sharing/leaking
- No per-user tracking
- No revocation mechanism

Session auth solves all of these issues and is the Django-native way to handle WebSocket authentication.

## Current Status

The immediate issue is the Nginx static path mismatch:
- Django: `/var/www/scan2food/static`
- Nginx: `/var/www/scan2food/staticfiles` (WRONG)

This must be fixed first before any auth changes.

## Commands to Run Now

```bash
# 1. Fix Nginx path
sudo sed -i 's|/var/www/scan2food/staticfiles/|/var/www/scan2food/static/|g' /etc/nginx/sites-available/scan2food
sudo nginx -t
sudo systemctl restart nginx

# 2. Verify fix
curl -s https://calculatentrade.com/static/theatre_js/live-orders/worker.js | head -20

# 3. Check Daphne logs
sudo journalctl -u daphne -f
```

After fixing the path issue, we can decide whether to:
1. Keep current API key system (quick)
2. Migrate to session auth (better security)
