# 🔄 Login Redirect Update

**Date:** February 9, 2026  
**Status:** ✅ COMPLETED

---

## 📝 Changes Made

### 1. Updated Login Redirect Logic

**File Modified:** `application/scan2food/theatreApp/views.py`

**Changes:**
- Updated `CustomLoginView` to redirect users based on their role
- Added `get_success_url()` method for post-login redirect
- Added user type checking in `dispatch()` method

**Redirect Logic:**
```
Superuser → /admin-portal/
Service Provider (group) → /admin-portal/
Theatre Owner → /theatre/
```

### 2. Fixed Decorator Error

**File Modified:** `application/scan2food/theatre/decorator.py`

**Changes:**
- Fixed AttributeError when user has no groups
- Added null check for `request.user.groups.first()`
- Added redirect to admin panel for superusers

### 3. Updated Documentation

**File Modified:** `SCAN2FOOD_CREDENTIALS.md`

**Changes:**
- Added Admin Portal URLs for both production and localhost
- Documented the automatic redirect behavior
- Added notes about user types and redirects

---

## 🎯 How It Works Now

### Login Flow

1. **User visits:** `http://localhost:8000/login` or `http://165.22.219.111/login`

2. **User enters credentials:**
   - Username: punit
   - Password: [your password]

3. **System checks user type:**
   - ✅ Is superuser? → Redirect to `/admin-portal/`
   - ✅ Has 'service_provider' group? → Redirect to `/admin-portal/`
   - ✅ Has theatre profile? → Redirect to `/theatre/`

4. **User lands on appropriate dashboard**

---

## 🔗 Access URLs

### Production (165.22.219.111)

**Login Page:**
```
http://165.22.219.111/login
```

**Admin Portal (after login):**
```
http://165.22.219.111/admin-portal/
```

**Django Admin (direct access):**
```
http://165.22.219.111/admin/
```

### Localhost (Development)

**Login Page:**
```
http://localhost:8000/login
```

**Admin Portal (after login):**
```
http://localhost:8000/admin-portal/
```

**Django Admin (direct access):**
```
http://localhost:8000/admin/
```

---

## 👥 User Types

### 1. Superuser (punit)
- **Access:** Full system access
- **Login Redirect:** Admin Portal
- **Can Access:**
  - Django Admin (`/admin/`)
  - Admin Portal (`/admin-portal/`)
  - All features

### 2. Service Provider
- **Group:** service_provider
- **Login Redirect:** Admin Portal
- **Can Access:**
  - Admin Portal (`/admin-portal/`)
  - Dashboard, Orders, Theatres, Payouts, Queries, Settings

### 3. Theatre Owner
- **Profile:** UserProfile with theatre
- **Login Redirect:** Theatre Dashboard
- **Can Access:**
  - Theatre Dashboard (`/theatre/`)
  - Menu management, Orders, Settings

---

## 🧪 Testing

### Test the Login Redirect

1. **Logout** (if logged in):
   ```
   http://localhost:8000/logout
   ```

2. **Go to login page:**
   ```
   http://localhost:8000/login
   ```

3. **Login with:**
   - Username: punit
   - Password: [your password]

4. **Expected Result:**
   - Should automatically redirect to: `http://localhost:8000/admin-portal/`
   - Should see: Dashboard, Orders, Theatres, Payouts, Queries, Settings menu

### Test Direct Access

**If already logged in:**
- Visit `http://localhost:8000/login`
- Should immediately redirect to admin portal (no login form shown)

---

## 🔧 Code Changes Summary

### CustomLoginView (views.py)

**Before:**
```python
def dispatch(self, request, *args, **kwargs):
    if request.user.is_authenticated:
        return redirect("theatre:all-seats")
    return super().dispatch(request, *args, **kwargs)
```

**After:**
```python
def dispatch(self, request, *args, **kwargs):
    if request.user.is_authenticated:
        user_group = request.user.groups.first()
        
        if user_group and user_group.name == 'service_provider':
            return redirect('admin-portal:index')
        
        if request.user.is_superuser:
            return redirect('admin-portal:index')
        
        return redirect("theatre:all-seats")
    return super().dispatch(request, *args, **kwargs)

def get_success_url(self):
    user_group = self.request.user.groups.first()
    
    if user_group and user_group.name == 'service_provider':
        return '/admin-portal/'
    
    if self.request.user.is_superuser:
        return '/admin-portal/'
    
    return '/theatre/'
```

---

## ✅ Benefits

1. **Better UX:** Users land on the right dashboard automatically
2. **No Errors:** Fixed AttributeError for users without groups
3. **Role-Based:** Different users see different dashboards
4. **Secure:** Superusers have full access to admin portal
5. **Flexible:** Easy to add more user types in the future

---

## 📌 Next Steps

1. ✅ Test login on localhost
2. ⏳ Deploy changes to production server
3. ⏳ Test login on production
4. ⏳ Update production .env if needed

---

## 🚀 Deploy to Production

When ready to deploy these changes:

```bash
# On your local machine
cd C:\Users\punit\Downloads\Documents\Desktop\s2f_bp
git add .
git commit -m "Updated login redirect to admin portal for superusers"
git push origin main

# On production server (SSH)
ssh root@165.22.219.111
cd /var/www/scan2food
git pull origin main
source application/scan2food/venv/bin/activate
cd application/scan2food
sudo systemctl restart scan2food
```

---

**Status:** ✅ Ready to test on localhost  
**Next:** Deploy to production after testing

