# 🔄 Git Push & Deploy Guide

## 🎯 STRATEGY: Push to Git, Pull on Server

---

## ⚠️ CRITICAL: Create .gitignore FIRST!

**Before pushing to Git, we MUST exclude sensitive files!**

---

## STEP 1: Create .gitignore File

**Create file:** `.gitignore` in project root

```bash
# In Windows PowerShell or CMD
cd C:\Users\punit\Downloads\Documents\Desktop\s2f_bp
```

**Create .gitignore with this content:**

```gitignore
# Python
*.py[cod]
*$py.class
*.so
__pycache__/
*.egg-info/
dist/
build/

# Django
*.log
db.sqlite3
db.sqlite3-journal
/staticfiles_collected/
/media/

# Environment variables
.env
.env.local
.env.production
*.env

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
desktop.ini

# Backup files
*.bak
*.backup
*.sql
*.dump

# Documentation (optional - you can commit these)
# *.md

# Credentials
*credentials*.json
*secret*.json

# Node modules (if any)
node_modules/

# Virtual environment
venv/
env/
ENV/

# Byte-compiled / optimized / DLL files
*.pyc
*.pyo

# Database backups
application/scan2food/media/backup_db/*.sql

# Temporary files
*.tmp
*.temp
```

---

## STEP 2: Initialize Git Repository

```bash
# Navigate to project root
cd C:\Users\punit\Downloads\Documents\Desktop\s2f_bp

# Initialize git (if not already)
git init

# Add .gitignore
git add .gitignore

# Check what will be committed
git status
```

---

## STEP 3: Add All Files

```bash
# Add all files (respecting .gitignore)
git add .

# Check what's staged
git status

# You should see:
# - All Python files
# - All templates
# - All static files
# - Documentation files
# - NOT .env files
# - NOT db.sqlite3
# - NOT media/backup_db/*.sql
```

---

## STEP 4: Commit Changes

```bash
git commit -m "Security update: Remove hardcoded credentials, add environment variable support"
```

---

## STEP 5: Create GitHub Repository

### Option A: Using GitHub Website

1. Go to: https://github.com/new
2. Repository name: `scan2food-secure`
3. Description: `Scan2Food - Secure deployment`
4. **IMPORTANT:** Set to **PRIVATE** (not public!)
5. Don't initialize with README (you already have code)
6. Click "Create repository"

### Option B: Using GitHub CLI (if installed)

```bash
gh repo create scan2food-secure --private --source=. --remote=origin
```

---

## STEP 6: Add Remote and Push

**GitHub will show you commands like:**

```bash
# Add remote
git remote add origin https://github.com/YOUR_USERNAME/scan2food-secure.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

**Enter your GitHub credentials when prompted**

---

## STEP 7: Verify on GitHub

1. Go to your repository on GitHub
2. Check that files are there
3. **VERIFY:** No .env files visible
4. **VERIFY:** No db.sqlite3 visible
5. **VERIFY:** No backup SQL files visible

---

## STEP 8: Pull on Server

**SSH into your new server:**

```bash
ssh username@YOUR_NEW_SERVER_IP
```

**Clone the repository:**

```bash
# Navigate to web directory
cd /var/www

# Clone your repository
git clone https://github.com/YOUR_USERNAME/scan2food-secure.git scan2food

# Enter GitHub credentials when prompted
```

**If repository is private, you may need to:**

```bash
# Generate SSH key on server
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub: Settings → SSH Keys → New SSH Key
# Then clone using SSH URL:
git clone git@github.com:YOUR_USERNAME/scan2food-secure.git scan2food
```

---

## STEP 9: Setup on Server

```bash
cd /var/www/scan2food/application/scan2food

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install python-dotenv gunicorn

# Create .env file (NOT in git!)
nano .env
```

**Add to .env:**

```env
DJANGO_ENV=production
SECRET_KEY=^u_*nzz-$&m6jeyj=mml8rmp8^7btom(sj9(r3kb8_#uxn$f^*

DB_NAME=scan2food_db
DB_USER=scan2food_user
DB_PASSWORD=YourStrongPassword123!
DB_HOST=localhost
DB_PORT=5432

REDIS_PASSWORD=YourStrongRedisPassword123!
```

**Save and exit**

---

## 🔒 SECURITY CHECKLIST

### ✅ SAFE TO COMMIT (In Git):
- [x] Python code files (*.py)
- [x] Templates (*.html)
- [x] Static files (CSS, JS, images)
- [x] Requirements.txt
- [x] Documentation (*.md)
- [x] Configuration files (settings.py with env vars)

### ❌ NEVER COMMIT (Excluded by .gitignore):
- [x] .env files
- [x] db.sqlite3
- [x] Database backups (*.sql)
- [x] Media files (uploaded by users)
- [x] __pycache__/
- [x] *.pyc files
- [x] Credentials files

---

## 🔄 FUTURE UPDATES

**When you make changes:**

```bash
# On Windows (local)
git add .
git commit -m "Description of changes"
git push origin main

# On Server
cd /var/www/scan2food
git pull origin main
sudo systemctl restart scan2food
```

---

## 📋 COMPLETE WORKFLOW

```
┌─────────────────────────────────────────────────────────┐
│ 1. Windows (Local Development)                         │
│    - Make changes                                       │
│    - Test locally with SQLite                          │
│    - Commit to Git                                     │
│    - Push to GitHub                                    │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ 2. GitHub (Private Repository)                         │
│    - Stores code securely                              │
│    - No sensitive data (.env excluded)                 │
│    - Version control                                   │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ 3. Production Server                                    │
│    - Pull from GitHub                                  │
│    - Create .env file manually                         │
│    - Run with PostgreSQL                               │
│    - Deploy with Daphne + Nginx                        │
└─────────────────────────────────────────────────────────┘
```

---

## ⚠️ IMPORTANT NOTES

### 1. **NEVER commit .env file**
- Contains passwords
- Contains SECRET_KEY
- Each environment has different .env

### 2. **NEVER commit database files**
- db.sqlite3 (local development)
- *.sql backup files
- Contains user data

### 3. **NEVER commit media files**
- User uploaded images
- Too large for git
- Transfer separately if needed

### 4. **Repository should be PRIVATE**
- Contains your business logic
- Old developer shouldn't access
- Keep it secure

---

## 🆘 TROUBLESHOOTING

### "Permission denied (publickey)"
**Solution:** Use HTTPS instead of SSH, or add SSH key to GitHub

```bash
# Use HTTPS URL
git clone https://github.com/YOUR_USERNAME/scan2food-secure.git
```

### "Repository not found"
**Solution:** Check repository name and make sure it's created

### "Authentication failed"
**Solution:** Use Personal Access Token instead of password
- GitHub Settings → Developer Settings → Personal Access Tokens
- Generate new token with repo access
- Use token as password

---

## ✅ FINAL CHECKLIST

- [ ] .gitignore created
- [ ] Git initialized
- [ ] All files added (except sensitive ones)
- [ ] Committed with message
- [ ] GitHub repository created (PRIVATE)
- [ ] Remote added
- [ ] Pushed to GitHub
- [ ] Verified no sensitive data on GitHub
- [ ] Cloned on server
- [ ] .env created on server (manually)
- [ ] Dependencies installed
- [ ] Ready to deploy!

---

**Now you're ready to push to Git and deploy! Follow the steps above.** 🚀
