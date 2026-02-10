# Where Memory Is Used - Complete Breakdown

## Your Server Memory Overview

**Total RAM: 961MB (approximately 1GB)**

This is shared between:
1. Operating System (Ubuntu Linux)
2. Your Django Application (Gunicorn workers)
3. WebSocket Server (Daphne)
4. Web Server (Nginx)
5. Cache/Database (Redis)
6. System Services

---

## Memory Usage Breakdown

### 1. **Gunicorn Workers** (~400MB with 4 workers, ~200MB with 2 workers)
**What it does:** Runs your Django application (scan2food)

**Current situation:**
- You have **4 workers** running
- Each worker = ~100MB
- Total: **4 × 100MB = 400MB**

**Where it's used:**
- Loading Django framework
- Loading your Python code (models, views, etc.)
- Database connections
- Session data
- Request processing

**Location:** `/etc/systemd/system/gunicorn.service`
```bash
# Current config
--workers 4  # Uses 400MB

# Recommended config
--workers 2  # Uses 200MB (saves 200MB!)
```

---

### 2. **Daphne (WebSocket Server)** (~125MB)
**What it does:** Handles real-time WebSocket connections for live updates

**Where it's used:**
- WebSocket protocol handling
- ASGI application loading
- Channel layers (in-memory)
- Connection management

**When it's needed:**
- Real-time seat updates in theatre booking
- Live chat features
- Instant notifications

**Can you disable it?**
- Yes, if you don't need real-time features
- Command: `sudo systemctl stop daphne`
- Saves: 125MB

---

### 3. **Nginx (Web Server)** (~30-50MB)
**What it does:** Handles incoming HTTP/HTTPS requests, serves static files

**Where it's used:**
- Master process: ~10MB
- Worker processes: ~10-15MB each (usually 2 workers)
- SSL/TLS handling
- Static file caching
- Request routing

**Can you reduce it?**
- Not recommended - Nginx is already very efficient
- Essential for serving your website

---

### 4. **Redis (Cache/Message Broker)** (~50MB)
**What it does:** Caches data and handles message queuing

**Where it's used:**
- Session storage
- Cache data (database query results)
- Message queue for background tasks
- WebSocket channel layer (if configured)

**Current status:** 
- You disabled Redis cache (using DummyCache)
- Redis might still be running in background

**Can you reduce it?**
- Stop Redis if not needed: `sudo systemctl stop redis-server`
- Or limit memory: Edit `/etc/redis/redis.conf` → `maxmemory 30mb`

---

### 5. **System Processes** (~200-300MB)
**What it does:** Core operating system functions

**Where it's used:**
- `systemd` - System manager (~20MB)
- `sshd` - SSH server for remote access (~10MB)
- `cron` - Scheduled tasks (~5MB)
- `rsyslog` - System logging (~10MB)
- Kernel buffers and cache (~150-200MB)

**Can you reduce it?**
- No - these are essential for server operation

---

### 6. **Database** (SQLite = minimal, MySQL/PostgreSQL = 50-100MB)
**What it does:** Stores your application data

**Current setup:** SQLite (file-based, minimal memory)

**If using MySQL/PostgreSQL:**
- Would use 50-100MB additional memory
- Not currently a concern for you

---

## Total Memory Calculation

### Current Setup (4 workers):
```
Gunicorn (4 workers):  400MB
Daphne:                125MB
Nginx:                  40MB
Redis:                  50MB
System:                250MB
------------------------
TOTAL:                 865MB
Available:              96MB (only 10% free!)
```

### After Fix (2 workers):
```
Gunicorn (2 workers):  200MB  ⬇️ Reduced by 200MB
Daphne:                125MB
Nginx:                  40MB
Redis:                  50MB
System:                250MB
------------------------
TOTAL:                 665MB
Available:             296MB (30% free - healthy!)
```

---

## Why Memory Matters

### When Memory Runs Out:
1. **Swapping starts** - System uses slow disk as "fake RAM"
2. **Everything slows down** - 100x slower than real RAM
3. **CPU spikes to 100%** - Kernel tries to manage memory
4. **Processes get killed** - OOM (Out of Memory) killer terminates processes
5. **Website becomes unusable** - Timeouts and errors

### Healthy Memory Levels:
- **Good:** 30-40% free (300MB+ available)
- **Acceptable:** 20-30% free (200-300MB available)
- **Warning:** 10-20% free (100-200MB available)
- **Critical:** <10% free (<100MB available) ⚠️

---

## How to Check Memory Usage

### Quick Check:
```bash
free -h
```

### Detailed Check:
```bash
# Run the diagnostic script
chmod +x check_memory_usage.sh
./check_memory_usage.sh
```

### Real-time Monitoring:
```bash
# Update every 2 seconds (Ctrl+C to exit)
watch -n 2 free -h
```

### See Which Processes Use Most Memory:
```bash
ps aux --sort=-%mem | head -20
```

### Check Specific Service:
```bash
# Gunicorn
ps aux | grep gunicorn

# Daphne
ps aux | grep daphne

# Nginx
ps aux | grep nginx
```

---

## Solutions to Memory Issues

### Immediate Fix (Free):
✅ **Reduce Gunicorn workers from 4 to 2**
- Saves: 200MB
- Impact: Minimal (still handles 2 concurrent requests)
- How: Run `./fix_memory_issue.sh`

### Optional Optimizations (Free):
- Disable Daphne if not using WebSocket: Saves 125MB
- Stop Redis if not using cache: Saves 50MB
- Limit Redis memory: `maxmemory 30mb` in config

### Long-term Solution (Paid):
💰 **Upgrade server RAM to 2GB**
- Cost: ~$6-12/month
- Benefit: Run 4 workers + Daphne comfortably
- Recommended if you expect more traffic

---

## Memory Usage by Feature

| Feature | Memory Used | Can Disable? |
|---------|-------------|--------------|
| Basic Django app (2 workers) | 200MB | ❌ No - Essential |
| Extra workers (2 more) | 200MB | ✅ Yes - Reduce to 2 |
| WebSocket (Daphne) | 125MB | ✅ Yes - If not using real-time |
| Web server (Nginx) | 40MB | ❌ No - Essential |
| Cache (Redis) | 50MB | ✅ Yes - Already using DummyCache |
| System | 250MB | ❌ No - Essential |

---

## Monitoring Commands

### Check if memory is the problem:
```bash
# High swap usage = memory problem
free -h | grep Swap

# High system CPU = memory swapping
top -o %CPU

# Check for OOM killer
dmesg | grep -i "out of memory"
```

### Monitor services:
```bash
# Service status
sudo systemctl status gunicorn daphne nginx redis

# Service logs
sudo journalctl -u gunicorn -n 50
sudo journalctl -u daphne -n 50
```

---

## Summary

**Your memory is used by:**
1. **Gunicorn (400MB)** - Your Django app workers ← **FIX THIS**
2. **Daphne (125MB)** - WebSocket server
3. **Nginx (40MB)** - Web server
4. **Redis (50MB)** - Cache
5. **System (250MB)** - Operating system

**The fix:** Reduce Gunicorn workers from 4 to 2 to free up 200MB.

**Run this on your server:**
```bash
./fix_memory_issue.sh
```

Your website will be fast again! 🚀
