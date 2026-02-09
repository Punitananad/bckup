# 🎭 How to Manage Theatres & Generate QR Codes - scan2food

**Complete Guide for Theatre Management**

---

## 📍 Where to Create & Manage Theatres

You have **TWO main places** to manage theatres:

### 1. Django Admin Panel (Recommended for Creating Theatres)
**URL:** `http://localhost:8000/admin/` or `http://165.22.219.111/admin/`

**What you can do:**
- ✅ Create new theatres
- ✅ Create theatre owners (users)
- ✅ Create halls for theatres
- ✅ Create rows and seats
- ✅ Create food categories and items
- ✅ View all orders and payments
- ✅ Full database access

**How to access:**
1. Go to: `http://localhost:8000/admin/`
2. Login with: `punit` / [your password]
3. You'll see all models listed

### 2. Admin Portal (Service Provider Dashboard)
**URL:** `http://localhost:8000/admin-portal/` or `http://165.22.219.111/admin-portal/`

**What you can do:**
- ✅ View all theatres
- ✅ View theatre details
- ✅ Manage payouts
- ✅ View all orders
- ✅ Generate QR codes for halls
- ✅ Approve food items
- ✅ Upload documents
- ✅ Manage payment gateways
- ✅ Download reports

**How to access:**
1. Go to: `http://localhost:8000/login`
2. Login with: `punit` / [your password]
3. You'll be automatically redirected to admin portal

---

## 🎯 Step-by-Step: Creating a New Theatre

### Method 1: Using Django Admin (Easiest)

**Step 1: Create Theatre Owner User**
1. Go to: `http://localhost:8000/admin/auth/user/`
2. Click "Add User"
3. Enter username and password
4. Save

**Step 2: Create Theatre**
1. Go to: `http://localhost:8000/admin/theatre/theatre/`
2. Click "Add Theatre"
3. Fill in:
   - Name (e.g., "PVR Cinemas")
   - Owner Name
   - Address
   - Phone Number
   - Email
4. Save

**Step 3: Create User Profile (Link User to Theatre)**
1. Go to: `http://localhost:8000/admin/theatre/userprofile/`
2. Click "Add User Profile"
3. Select:
   - User (the one you created)
   - Theatre (the one you created)
   - Active Status: ✅ Check this
4. Save

**Step 4: Create Halls**
1. Go to: `http://localhost:8000/admin/theatre/hall/`
2. Click "Add Hall"
3. Fill in:
   - Name (e.g., "Hall 1", "Screen 1")
   - Theatre (select the theatre)
4. Save
5. Repeat for multiple halls

**Step 5: Create Rows in Hall**
1. Go to: `http://localhost:8000/admin/theatre/row/`
2. Click "Add Row"
3. Fill in:
   - Name (e.g., "A", "B", "C")
   - Hall (select the hall)
4. Save
5. Repeat for all rows

**Step 6: Create Seats in Row**
1. Go to: `http://localhost:8000/admin/theatre/seat/`
2. Click "Add Seat"
3. Fill in:
   - Name (e.g., "1", "2", "3")
   - Row (select the row)
4. Save
5. Repeat for all seats (or use bulk creation if available)

**Step 7: Create Food Categories**
1. Go to: `http://localhost:8000/admin/theatre/foodcategory/`
2. Click "Add Food Category"
3. Fill in:
   - Name (e.g., "Beverages", "Snacks", "Combos")
   - Theatre (select the theatre)
4. Save

**Step 8: Create Food Items**
1. Go to: `http://localhost:8000/admin/theatre/fooditem/`
2. Click "Add Food Item"
3. Fill in:
   - Name (e.g., "Popcorn", "Coke")
   - Food Type (Veg/Non-Veg)
   - Price
   - Category (select category)
   - Image (upload)
   - Is Available: ✅ Check this
5. Save

---

## 📱 How to Generate QR Codes

### QR Code Generation Process

**What are QR codes used for?**
- Each **Hall** gets a unique QR code
- Customers scan the QR code to order food
- QR code links to: `http://your-domain.com/theatre/hall/{hall_id}/`

### Method 1: From Admin Portal

**Step 1: Go to Theatres List**
1. Login to Admin Portal: `http://localhost:8000/admin-portal/`
2. Click on "Theatres" in the sidebar
3. You'll see: `http://localhost:8000/admin-portal/all-theatre`

**Step 2: View Theatre Details**
1. Click on any theatre name
2. You'll go to: `http://localhost:8000/admin-portal/theatre-detail/{theatre_id}`
3. You'll see all halls for that theatre

**Step 3: Download QR Code**
1. Find the hall you want
2. Click "Download QR" button next to the hall
3. QR code will be generated and downloaded as PNG
4. File name: `hall-{hall_id}.png`
5. Resolution: 3840x3840px (high quality for printing)

**QR Code URL Format:**
```
http://your-domain.com/theatre/hall/{hall_id}/
```

### Method 2: Programmatically (if needed)

The QR generation function is in:
- **File:** `application/scan2food/adminPortal/views.py`
- **Function:** `download_hall_qr(request, pk)`
- **URL:** `/admin-portal/download-hall-qr/{hall_id}`

**Direct URL to download QR:**
```
http://localhost:8000/admin-portal/download-hall-qr/1
```
(Replace `1` with your hall ID)

---

## 🗂️ Admin Portal Features Explained

### Dashboard (`/admin-portal/`)
- Overview of system
- Quick stats

### Theatres (`/admin-portal/all-theatre`)
- **View all theatres:** List of all registered theatres
- **Theatre details:** Click on theatre to see:
  - Basic info (name, owner, contact)
  - All halls
  - Documents
  - GST details
  - Bank details
  - Logo
  - QR codes for each hall

### Orders (`/admin-portal/all-orders`)
- **View all orders:** From all theatres
- **Filter by date:** Date range picker
- **Order details:** Click to see full order info
- **Refund orders:** Process refunds
- **Download reports:** Excel reports

### Payouts (`/admin-portal/all-payouts`)
- **View payouts:** Money owed to theatres
- **Create payouts:** Generate payout for theatre
- **Settlement tracking:** Mark as settled
- **Download reports:** Payout reports

### Queries (`/admin-portal/all-queries`)
- **Customer queries:** Support tickets
- **Refund requests:** Process refund requests
- **Update status:** Mark as resolved

### Settings (`/admin-portal/settings`)
- **Payment gateways:** Configure Razorpay, Cashfree, PhonePe, etc.
- **System settings:** General configuration

### All Food Items (`/admin-portal/item-approved-list`)
- **Approve items:** Review and approve food items added by theatres
- **Upload images:** Add food images

---

## 🔑 Important URLs Reference

### Localhost (Development)

**Django Admin:**
```
http://localhost:8000/admin/
```

**Admin Portal:**
```
http://localhost:8000/admin-portal/
http://localhost:8000/admin-portal/all-theatre
http://localhost:8000/admin-portal/theatre-detail/{id}
http://localhost:8000/admin-portal/download-hall-qr/{hall_id}
http://localhost:8000/admin-portal/all-orders
http://localhost:8000/admin-portal/all-payouts
```

**Theatre Owner Dashboard:**
```
http://localhost:8000/theatre/
```

**Customer Ordering (via QR):**
```
http://localhost:8000/theatre/hall/{hall_id}/
```

### Production

Replace `localhost:8000` with `165.22.219.111` or `scan2food.com`

---

## 📊 Database Models Overview

### Theatre Structure
```
Theatre
  ├── UserProfile (owner)
  ├── Hall (multiple)
  │   ├── Row (multiple)
  │   │   └── Seat (multiple)
  │   └── QR Code (one per hall)
  ├── FoodCategory (multiple)
  │   └── FoodItem (multiple)
  └── Orders (multiple)
```

### Key Models

**Theatre:**
- name, owner_name, address, phone_number, email

**Hall:**
- name, theatre (FK)

**Row:**
- name, hall (FK)

**Seat:**
- name, row (FK)

**FoodCategory:**
- name, theatre (FK)

**FoodItem:**
- name, food_type, price, category (FK), image, is_available

**Order:**
- seat (FK), payment (FK), food_items (M2M), status

**Payment:**
- order (FK), amount, status, gateway, is_settled

---

## 🎨 Workflow: From Theatre Creation to Customer Order

### 1. Admin Creates Theatre
- Create theatre in Django admin
- Create owner user
- Link user to theatre via UserProfile

### 2. Admin Sets Up Theatre
- Create halls (screens)
- Create rows and seats for each hall
- Create food categories
- Add food items with images

### 3. Admin Generates QR Codes
- Go to admin portal
- View theatre details
- Download QR code for each hall
- Print QR codes

### 4. Theatre Places QR Codes
- Print QR codes on stickers/posters
- Place at each seat or hall entrance

### 5. Customer Scans QR Code
- Customer scans QR with phone
- Opens: `http://scan2food.com/theatre/hall/{hall_id}/`
- Selects seat number
- Browses menu
- Adds items to cart
- Makes payment

### 6. Order Processing
- Order appears in admin portal (live orders)
- Theatre receives order notification
- Theatre prepares food
- Delivers to seat

### 7. Payout
- Admin creates payout for theatre
- Downloads payout report
- Transfers money to theatre
- Marks as settled

---

## 🛠️ Quick Actions Cheat Sheet

### Create Theatre (Quick)
```
1. Admin → Theatre → Add Theatre
2. Admin → User Profile → Add (link user to theatre)
3. Admin → Hall → Add Hall (for the theatre)
4. Admin Portal → Theatres → View → Download QR
```

### Generate QR Code (Quick)
```
1. Admin Portal → Theatres
2. Click theatre name
3. Find hall
4. Click "Download QR"
```

### View Orders (Quick)
```
1. Admin Portal → Orders
2. Filter by date/status
3. Click order to see details
```

### Create Payout (Quick)
```
1. Admin Portal → Payouts
2. Click "Create Payout"
3. Select theatre and date range
4. Generate payout
```

---

## 🔍 Finding Things

### Find Theatre ID
- Admin Portal → Theatres → Look at URL when viewing theatre
- URL: `/admin-portal/theatre-detail/5` → Theatre ID is `5`

### Find Hall ID
- Django Admin → Halls → Click hall → Look at URL
- URL: `/admin/theatre/hall/12/change/` → Hall ID is `12`

### Find Order ID
- Admin Portal → Orders → Click order → Look at URL
- URL: `/admin-portal/order-profile/123` → Order ID is `123`

---

## 💡 Tips & Best Practices

### Theatre Setup
- ✅ Create logical hall names (Hall 1, Screen A, etc.)
- ✅ Use consistent row naming (A, B, C or 1, 2, 3)
- ✅ Number seats sequentially
- ✅ Upload high-quality food images
- ✅ Set realistic prices

### QR Codes
- ✅ Generate high-resolution QR codes (3840x3840px)
- ✅ Test QR codes before printing
- ✅ Print on durable material
- ✅ Place QR codes in visible locations
- ✅ Include instructions for customers

### Food Menu
- ✅ Organize items into categories
- ✅ Mark items as available/unavailable
- ✅ Update prices regularly
- ✅ Use clear, appetizing images
- ✅ Approve items before they go live

### Orders & Payouts
- ✅ Monitor live orders regularly
- ✅ Process refunds promptly
- ✅ Generate payouts on schedule
- ✅ Download reports for records
- ✅ Verify settlements

---

## 🚨 Common Issues & Solutions

### Issue: Can't see theatre in admin portal
**Solution:** Make sure theatre has at least one hall created

### Issue: QR code download fails
**Solution:** Check that hall ID exists and you have permissions

### Issue: Food items not showing
**Solution:** Check that items are marked as "available" and approved

### Issue: Orders not appearing
**Solution:** Check payment status and order status filters

### Issue: Can't create payout
**Solution:** Ensure theatre has completed orders with successful payments

---

## 📞 Need Help?

### Check These First
1. Django Admin: `http://localhost:8000/admin/`
2. Admin Portal: `http://localhost:8000/admin-portal/`
3. Database: Check models in Django admin
4. Logs: Check terminal for errors

### Useful Commands
```bash
# Check database
python manage.py dbshell

# Create superuser
python manage.py createsuperuser

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic
```

---

**Last Updated:** February 9, 2026  
**Version:** 1.0

