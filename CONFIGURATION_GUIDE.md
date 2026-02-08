# 🔧 scan2food Configuration Guide

## ⚠️ IMPORTANT: This Project Does NOT Use .env Files!

Your project stores configuration in **TWO places**:

1. **settings.py** - Django settings (hardcoded)
2. **Database** - Payment gateway credentials (via Django admin)

---

## 📍 Where Everything Is Stored

### 1. Django Settings (settings.py)

**Location:** `application/scan2food/theatreApp/settings.py`

**What's stored here:**
```python
SECRET_KEY = 'django-insecure-a@q^h)$szzhw_$wd)0zu@8x^woi^d9vufw#^!-uuhv2%j2r%*e'
DEBUG = True
ALLOWED_HOSTS = ['134.209.149.31', 'scan2food.com', 'www.scan2food.com', 'localhost', '127.0.0.1', '192.168.1.33']
TIME_ZONE = 'Asia/Kolkata'

# Database config (lines 110-117)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Redis config (lines 97-104)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}
```

### 2. Payment Gateway Credentials (Database)

**Location:** Database table `adminPortal_paymentgateway`

**Accessed via:** Django Admin Panel at `http://your-domain/admin/`

**Model:** `adminPortal.models.PaymentGateway`

**Fields:**
- `name` - Gateway name (Razorpay, Cashfree, PhonePe, PayU, etc.)
- `gateway_key` - API Key / Client ID / Merchant Key
- `gateway_secret` - API Secret / Client Secret
- `gateway_salt` - Salt (for PayU)
- `merchant_id` - Merchant ID (for some gateways)
- `is_active` - Enable/disable gateway

---

## 🚀 Deployment to 