# Upgrade WebSocket to Session-Based Authentication

## Why This Is Better Than API Keys in JavaScript

**Current Problem:**
- API keys are visible in browser DevTools
- Anyone can copy the key and spam your WebSocket
- Keys are static and don't expire
- No per-user access control

**Session Auth Benefits:**
- Uses existing Django session cookies
- Keys are httpOnly (not accessible to JavaScript)
- Automatic expiration (SESSION_COOKIE_AGE)
- Per-user authentication
- No secrets in frontend code

---

## Implementation Steps

### Step 1: Update ASGI Application (theatreApp/asgi.py)

```python
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack  # ← Add this
from channels.security.websocket import AllowedHostsOriginValidator
import theatre.routing
import chat_box.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'theatreApp.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(  # ← Wrap with AuthMiddlewareStack
            URLRouter(
                theatre.routing.websocket_urlpatterns +
                chat_box.routing.websocket_urlpatterns
            )
        )
    ),
})
```

### Step 2: Update Consumers to Use Session Auth

#### AllSeatConsumer (theatre/consumers/allSeatConsumer.py)

```python
class AllSeatConsumers(AsyncWebsocketConsumer):
    async def connect(self):
        # Get user from scope (provided by AuthMiddlewareStack)
        user = self.scope["user"]
        
        # Check if user is authenticated
        if not user.is_authenticated:
            await self.close()
            return
        
        # Optional: Check if user has permission (staff only)
        if not await self.user_is_staff(user):
            await self.close()
            return
        
        # User is authenticated - allow connection
        self.group_name = "all-seat-status"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
    
    @database_sync_to_async
    def user_is_staff(self, user):
        return user.is_staff or user.is_superuser
    
    async def disconnect(self, code):
        # ... rest of disconnect logic ...
```

#### PaymentSocket (theatre/consumers/paymentSocket.py)

```python
class PaymentSocket(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        
        # Check if user is authenticated
        if not user.is_authenticated:
            await self.close()
            return
        
        # Get order_id from URL
        self.order_id = self.scope['url_route']['kwargs']['pk']
        
        # Optional: Verify user owns this order
        if not await self.user_owns_order(user, self.order_id):
            await self.close()
            return
        
        await self.accept()
    
    @database_sync_to_async
    def user_owns_order(self, user, order_id):
        from theatre.models import Order
        try:
            order = Order.objects.get(pk=order_id)
            # Add your ownership logic here
            # For example: return order.user == user
            return True  # Adjust based on your model
        except Order.DoesNotExist:
            return False
```

#### ChatConsumer (chat_box/consumer/chatConsumer.py)

```python
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        
        # Check if user is authenticated
        if not user.is_authenticated:
            await self.close()
            return
        
        # Optional: Check if user is staff (for admin chat)
        if not await self.user_is_staff(user):
            await self.close()
            return
        
        self.group_name = 'chat-consuer'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
    
    @database_sync_to_async
    def user_is_staff(self, user):
        return user.is_staff or user.is_superuser
```

### Step 3: Update JavaScript (Remove API Keys)

#### worker.js (all locations)

**Before:**
```javascript
const ws_key = "05XnhaghUWM6Hd7YVR6_iPcJGfH_YDn3RiDv1Rh-zNM";
const socket = new WebSocket(`wss://${window.location.host}/ws/all-seat-datasocket/?key=${ws_key}`);
```

**After:**
```javascript
// No API key needed - session cookie is sent automatically
const socket = new WebSocket(`wss://${window.location.host}/ws/all-seat-datasocket/`);
```

### Step 4: Update Settings (Optional - Enhance Security)

```python
# In settings.py

# Ensure session cookies work with WebSocket
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access
SESSION_COOKIE_SECURE = True    # HTTPS only (production)
SESSION_COOKIE_SAMESITE = 'Lax' # CSRF protection

# Optional: Shorter session timeout for WebSocket users
SESSION_COOKIE_AGE = 3600  # 1 hour
```

### Step 5: Remove API Keys from Settings

```python
# In settings.py - REMOVE these lines:
# LIVE_ORDERS_WS_KEY = os.environ.get('LIVE_ORDERS_WS_KEY', '...')
# PAYMENT_STATUS_WS_KEY = os.environ.get('PAYMENT_STATUS_WS_KEY', '...')
# CHAT_WS_KEY = os.environ.get('CHAT_WS_KEY', '...')
```

---

## Testing the Upgrade

### Test 1: Authenticated User
1. Log in to the application
2. Navigate to live orders page
3. WebSocket should connect successfully
4. Check Daphne logs: Should see "WSCONNECT"

### Test 2: Unauthenticated User
1. Open incognito/private window
2. Navigate directly to live orders page (without logging in)
3. WebSocket should be rejected
4. Check Daphne logs: Should see connection closed immediately

### Test 3: Session Expiry
1. Log in and connect WebSocket
2. Wait for session to expire (or manually delete session cookie)
3. Try to reconnect WebSocket
4. Should be rejected

---

## Migration Plan

### Phase 1: Implement (Development)
1. Update asgi.py with AuthMiddlewareStack
2. Update all consumers to check `self.scope["user"]`
3. Update JavaScript to remove API keys
4. Test locally

### Phase 2: Deploy (Production)
1. Push code to GitHub
2. Pull on server
3. Restart Daphne: `sudo systemctl restart daphne`
4. Test with logged-in user
5. Test with logged-out user

### Phase 3: Cleanup
1. Remove API key environment variables from `.env`
2. Remove API key settings from `settings.py`
3. Update documentation

---

## Rollback Plan (If Something Goes Wrong)

```bash
# On server:
cd /var/www/scan2food
git log --oneline -5  # Find commit before session auth
git checkout <commit-hash>
sudo systemctl restart daphne gunicorn
```

---

## Benefits Summary

| Feature | API Key in JS | Session Auth |
|---------|--------------|--------------|
| Security | ❌ Weak | ✅ Strong |
| Visible in DevTools | ❌ Yes | ✅ No |
| Can be stolen | ❌ Yes | ✅ No (httpOnly) |
| Expires | ❌ Never | ✅ Auto |
| Per-user control | ❌ No | ✅ Yes |
| Requires login | ❌ No | ✅ Yes |

---

## When to Implement This

**Do this AFTER:**
- ✅ Nginx static path is fixed
- ✅ WebSocket connections work with API keys
- ✅ Live orders feature is stable

**Estimated Time:** 1-2 hours

**Risk Level:** Low (easy to rollback)

**Priority:** Medium (current API key approach works, but this is more secure)
