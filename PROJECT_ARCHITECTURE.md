# 🏗️ scan2food Project Architecture

## 📐 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│  (Web Browsers, Mobile Apps, QR Code Scanners)             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Nginx/Apache (Reverse Proxy)             │
│  - Static Files Serving                                     │
│  - Media Files Serving                                      │
│  - SSL Termination                                          │
└────────────┬────────────────────────────┬───────────────────┘
             │                            │
             ▼                            ▼
┌────────────────────────┐    ┌──────────────────────────────┐
│   HTTP Requests        │    │   WebSocket Connections      │
│   (Django Views)       │    │   (Django Channels)          │
└────────────┬───────────┘    └──────────┬───────────────────┘
             │                           │
             ▼                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Django Application (theatreApp)                 │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │ theatre  │adminPortal│ chat_bot │ chat_box │ website  │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
└────────────┬────────────────────────────────┬───────────────┘
             │                                │
             ▼                                ▼
┌────────────────────────┐         ┌──────────────────────────┐
│   SQLite/PostgreSQL    │         │   Redis (Channel Layer)  │
│   (Main Database)      │         │   (WebSocket Messages)   │
└────────────────────────┘         └──────────────────────────┘
```

---

## 🎯 Application Components

### 1. **theatre** (Main Food Ordering System)
**Purpose:** Core food ordering and management system for theatres/restaurants

**Key Features:**
- 🍕 Food menu management (19 models)
- 🛒 Order processing and tracking
- 💳 Payment gateway integration (Razorpay, Cashfree, PhonePe)
- 📊 Sales analytics and reporting
- 🔔 Real-time order notifications (WebSocket)
- 📱 QR code generation for tables/seats
- 🎫 Ticket integration (if theatre-based)

**Files:**
- `models.py` - 19 database models (Food, Order, Payment, etc.)
- `views.py` - HTTP request handlers
- `api_views.py` - REST API endpoints
- `consumers/` - WebSocket consumers for real-time updates
- `routing.py` - WebSocket URL routing
- `templates/` - HTML templates

**URL Pattern:** `/theatre/`

---

### 2. **adminPortal** (Admin Management)
**Purpose:** Administrative interface for restaurant/theatre owners

**Key Features:**
- 👤 User management and authentication
- 🏪 Restaurant/theatre profile setup
- 📄 Document management (licenses, certificates)
- 💰 Payout and commission tracking
- 🔐 GST details management
- 📧 Query/support ticket system
- 🔑 Payment gateway configuration

**Files:**
- `models.py` - 9 models (Detail, GSTDetails, Payment, Commission, etc.)
- `views.py` - Admin dashboard views
- `decorator.py` - Custom authentication decorators
- `form.py` - Admin forms

**URL Pattern:** `/admin-portal/`

---

### 3. **chat_bot** (Customer Support Bot)
**Purpose:** Automated customer support via chat/WhatsApp

**Key Features:**
- 💬 Real-time chat interface (WebSocket)
- 🤖 Automated responses
- 📱 WhatsApp integration
- 📝 Message history
- 🔔 Notification system

**Files:**
- `consumers/chatConsumers.py` - WebSocket chat handler
- `whatsapp_msg_utils.py` - WhatsApp API integration
- `sse_utilts.py` - Server-Sent Events utilities
- `routing.py` - WebSocket routing

**URL Pattern:** `/chat-bot/` (not in main URLs, might be internal)

---

### 4. **chat_box** (Internal Chat System)
**Purpose:** Communication between customers and restaurant staff

**Key Features:**
- 💬 Real-time messaging (WebSocket)
- 👥 Customer-to-staff communication
- 📱 WhatsApp integration
- 📝 Chat history (2 models)

**Files:**
- `consumer/chatConsumer.py` - WebSocket handler
- `models.py` - 2 models for chat messages
- `whatsapp_msg_utils.py` - WhatsApp integration

**URL Pattern:** `/chat-box/`

---

### 5. **website** (Public Website)
**Purpose:** Public-facing website and landing pages

**Key Features:**
- 🏠 Homepage
- ℹ️ About/Contact pages
- 📱 Mobile app download links
- 📰 Blog/news (URL pattern exists)

**URL Pattern:** `/` (root) and `/blog/`

---

## 🗄️ Database Schema Overview

### Key Models (from analysis)

**theatre app (19 models):**
- Food items and categories
- Orders and order items
- Payments and transactions
- Customers and user profiles
- Tables/seats management
- Coupons and discounts
- Notifications
- Analytics data

**adminPortal app (9 models):**
- Detail (restaurant/theatre info)
- GSTDetails (tax information)
- Payment (payment gateway config)
- PaymentGateway
- Commission (platform fees)
- PayoutLogs (settlement tracking)
- RazorpayDetail
- Query (support tickets)

**chat_box app (2 models):**
- ChatMessage
- ChatRoom/Conversation

---

## 🔌 WebSocket Architecture

### How Real-Time Features Work

```
Client Browser
     │
     │ WebSocket Connection
     ▼
Django Channels (ASGI)
     │
     │ Channel Layer
     ▼
Redis (Message Broker)
     │
     │ Broadcast
     ▼
All Connected Clients
```

### WebSocket Endpoints

1. **Theatre Orders** (`theatre/routing.py`)
   - Real-time order updates
   - Kitchen display notifications
   - Order status changes

2. **Chat Bot** (`chat_bot/routing.py`)
   - Customer support messages
   - Automated responses

3. **Chat Box** (`chat_box/routing.py`)
   - Customer-staff messaging
   - Real-time chat

---

## 💳 Payment Flow

```
Customer Places Order
        │
        ▼
Select Payment Method
        │
        ├─→ Razorpay
        ├─→ Cashfree
        ├─→ PhonePe
        └─→ Cash on Delivery
        │
        ▼
Payment Gateway API
        │
        ▼
Payment Verification
        │
        ▼
Order Confirmation
        │
        ▼
Kitchen Notification (WebSocket)
```

### Payment Gateway Integration

**Razorpay:**
- File: `theatre/models.py` (RazorpayDetail)
- Configuration in adminPortal

**Cashfree:**
- Package: `cashfree-pg==4.3.7`
- Configuration in settings

**PhonePe:**
- Package: `phonepe_sdk==2.1.2`
- Custom integration

**CCAvenue:**
- File: `theatre/ccavutil.py`
- Encryption utilities

---

## 📱 QR Code System

### How It Works

1. **QR Code Generation:**
   - Package: `qrcode==7.4.2`, `segno`
   - Each table/seat gets unique QR code
   - QR contains: restaurant_id, table_id, session_token

2. **Customer Scans QR:**
   - Redirects to menu page
   - Auto-selects table/seat
   - Session tracking

3. **Order Placement:**
   - Order linked to table
   - Kitchen gets table number
   - Real-time status updates

---

## 🔐 Authentication & Security

### User Types

1. **Super Admin** (Django admin)
   - Full system access
   - Platform management

2. **Restaurant Owner** (adminPortal)
   - Restaurant management
   - Menu and orders
   - Analytics

3. **Staff** (theatre app)
   - Order management
   - Kitchen operations

4. **Customers** (public)
   - Browse menu
   - Place orders
   - Track orders

### Security Features

- Custom decorators (`adminPortal/decorator.py`)
- Session management
- CSRF protection
- Secure payment handling
- SSL/HTTPS (production)

---

## 📊 Data Flow

### Order Processing Flow

```
1. Customer Scans QR Code
   └─→ Loads Menu (theatre/views.py)

2. Customer Adds Items to Cart
   └─→ Session storage

3. Customer Places Order
   └─→ Create Order (theatre/models.py)
   └─→ Payment Gateway
   └─→ Payment Verification

4. Order Confirmed
   └─→ Save to Database
   └─→ WebSocket Notification to Kitchen
   └─→ SMS/Email to Customer

5. Kitchen Prepares Order
   └─→ Update Status (WebSocket)
   └─→ Customer sees real-time updates

6. Order Delivered
   └─→ Final status update
   └─→ Generate invoice
   └─→ Update analytics
```

---

## 🗂️ File Structure Explained

```
application/scan2food/
│
├── theatreApp/              # Main Django project
│   ├── settings.py          # Configuration
│   ├── urls.py              # Main URL routing
│   ├── asgi.py              # ASGI config (WebSocket)
│   └── wsgi.py              # WSGI config (HTTP)
│
├── theatre/                 # Food ordering app
│   ├── models.py            # 19 models
│   ├── views.py             # HTTP views
│   ├── api_views.py         # REST API
│   ├── consumers/           # WebSocket handlers
│   ├── templates/           # HTML templates
│   └── migrations/          # Database migrations
│
├── adminPortal/             # Admin management
│   ├── models.py            # 9 models
│   ├── views.py             # Admin views
│   ├── decorator.py         # Auth decorators
│   └── templates/           # Admin templates
│
├── chat_bot/                # Support bot
│   ├── consumers/           # WebSocket chat
│   └── whatsapp_msg_utils.py
│
├── chat_box/                # Internal chat
│   ├── consumer/            # WebSocket chat
│   └── models.py            # 2 models
│
├── website/                 # Public website
│   ├── views.py
│   └── templates/
│
├── media/                   # User uploads
│   ├── food_images/         # Menu item images
│   ├── documents/           # Restaurant docs
│   ├── backup_db/           # Database backups
│   └── theatre_logo/        # Logos
│
├── db.sqlite3               # Database (0.47 MB)
├── manage.py                # Django CLI
└── requirements.txt         # Dependencies

static_files/                # Static assets
└── scan2food-static/
    └── static/
        ├── admin/           # Django admin CSS/JS
        ├── assets/          # Custom CSS/JS/images
        ├── dashboard/       # Dashboard assets
        └── theatre_js/      # Theatre-specific JS
```

---

## 🔄 Request/Response Cycle

### HTTP Request (Regular Page)

```
1. Client → Nginx → Django
2. Django URLs → View Function
3. View → Database Query
4. View → Render Template
5. Response → Nginx → Client
```

### WebSocket Connection (Real-Time)

```
1. Client → Nginx (Upgrade to WebSocket)
2. Nginx → Daphne (ASGI Server)
3. Daphne → Django Channels
4. Channels → Consumer (Python class)
5. Consumer → Redis (Channel Layer)
6. Redis → Broadcast to all connected clients
```

### API Request (REST)

```
1. Client → Nginx → Django
2. Django URLs → api_views.py
3. API View → Database
4. API View → JSON Response
5. Response → Client
```

---

## 🛠️ Technology Stack

### Backend
- **Framework:** Django 4.2.14
- **ASGI Server:** Daphne 4.1.2
- **WebSocket:** Django Channels 4.3.1
- **Message Broker:** Redis 6.2.0
- **Database:** SQLite (dev) / PostgreSQL (prod)

### Frontend
- **Templates:** Django Templates
- **JavaScript:** Vanilla JS + WebSocket API
- **CSS:** Custom + Bootstrap (likely)

### Payment Gateways
- Razorpay 1.4.2
- Cashfree PG 4.3.7
- PhonePe SDK 2.1.2
- CCAvenue (custom)

### Other Services
- **QR Codes:** qrcode 7.4.2, segno
- **Image Processing:** Pillow 10.4.0
- **Excel Export:** openpyxl 3.1.5, pandas 2.2.2
- **Notifications:** Firebase Admin 6.6.0
- **Task Scheduling:** APScheduler 3.10.1

---

## 🔍 How to Find Things

### "Where is the menu management?"
→ `theatre/models.py` (Food model)  
→ `theatre/views.py` (menu views)  
→ `theatre/templates/` (menu templates)

### "Where are orders processed?"
→ `theatre/models.py` (Order model)  
→ `theatre/views.py` (order views)  
→ `theatre/api_views.py` (order API)

### "Where is payment handled?"
→ `theatre/models.py` (Payment model)  
→ `theatre/views.py` (payment views)  
→ `adminPortal/models.py` (PaymentGateway config)

### "Where is WebSocket code?"
→ `theatre/consumers/` (order updates)  
→ `chat_bot/consumers/` (support chat)  
→ `chat_box/consumer/` (internal chat)  
→ `theatreApp/asgi.py` (ASGI config)

### "Where are admin features?"
→ `adminPortal/views.py` (admin dashboard)  
→ `adminPortal/models.py` (admin data)  
→ `adminPortal/templates/` (admin UI)

### "Where is the database?"
→ `db.sqlite3` (current)  
→ `theatreApp/settings.py` (database config)

### "Where are uploaded files?"
→ `media/food_images/` (menu images)  
→ `media/documents/` (restaurant docs)  
→ `media/theatre_logo/` (logos)

---

## 📝 Configuration Files

### Important Settings

**settings.py locations:**
- Main: `theatreApp/settings.py`
- Backup: `theatreApp/settings.py.backup`

**Key settings to check:**
- `DEBUG` - Must be False in production
- `ALLOWED_HOSTS` - Add your domain/IP
- `DATABASES` - Database configuration
- `CHANNEL_LAYERS` - Redis configuration
- `STATIC_ROOT` - Static files location
- `MEDIA_ROOT` - Upload files location

---

## 🚀 Deployment Considerations

### What Needs to Run

1. **Daphne** (ASGI server for Django + WebSocket)
2. **Redis** (for WebSocket message passing)
3. **Nginx** (reverse proxy, static files)
4. **Database** (SQLite or PostgreSQL)

### What Needs Configuration

1. Environment variables (.env file)
2. Payment gateway credentials
3. Firebase credentials (if using push notifications)
4. Email settings (if using email)
5. Domain/IP in ALLOWED_HOSTS
6. SSL certificate

### What Needs Monitoring

1. Daphne process (systemd service)
2. Redis service
3. Database backups
4. Disk space (media files grow)
5. Error logs

---

**This architecture document should help you understand how everything connects and works together!**
