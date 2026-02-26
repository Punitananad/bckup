# Database Architecture

## Overview

Your application now uses PostgreSQL for both local development and production, with completely separate databases.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Your Application                         │
│                    (Django/Scan2Food)                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Reads DB config from .env
                              │
                ┌─────────────┴─────────────┐
                │                           │
                │                           │
    ┌───────────▼──────────┐    ┌──────────▼───────────┐
    │  LOCAL DEVELOPMENT   │    │     PRODUCTION       │
    │                      │    │                      │
    │  Database:           │    │  Database:           │
    │  scan2food_local     │    │  scan2food_db        │
    │                      │    │                      │
    │  User:               │    │  User:               │
    │  scan2food_dev       │    │  scan2food_user      │
    │                      │    │                      │
    │  Password:           │    │  Password:           │
    │  dev_password_123    │    │  scann2Food          │
    │                      │    │                      │
    │  Host:               │    │  Host:               │
    │  localhost           │    │  localhost           │
    │                      │    │                      │
    │  Port: 5432          │    │  Port: 5432          │
    └──────────────────────┘    └──────────────────────┘
            │                            │
            │                            │
    ┌───────▼────────┐          ┌────────▼────────┐
    │  PostgreSQL    │          │  PostgreSQL     │
    │  (Your PC)     │          │  (Server)       │
    └────────────────┘          └─────────────────┘
```

## Data Flow

### Local Development
```
1. You run: run_local.bat
2. Django reads: application/scan2food/.env
3. Connects to: scan2food_local database
4. Using credentials: scan2food_dev / dev_password_123
5. On: localhost:5432
```

### Production
```
1. Server runs: gunicorn/daphne
2. Django reads: .env (on server)
3. Connects to: scan2food_db database
4. Using credentials: scan2food_user / scann2Food
5. On: localhost:5432 (server's localhost)
```

## Database Separation

### Why Separate Databases?

1. **Safety:** Can't accidentally modify production data
2. **Testing:** Experiment freely without consequences
3. **Performance:** Local queries don't affect production
4. **Security:** Different credentials for different environments

### How It Works

```
┌──────────────────────────────────────────────────────────┐
│                    PostgreSQL Server                      │
│                                                           │
│  ┌─────────────────────┐  ┌─────────────────────┐       │
│  │  scan2food_local    │  │  scan2food_db       │       │
│  │  (Development)      │  │  (Production)       │       │
│  │                     │  │                     │       │
│  │  - Your test data   │  │  - Real user data   │       │
│  │  - Can be reset     │  │  - Must be protected│       │
│  │  - Restored from    │  │  - Backed up        │       │
│  │    dbbckup.sql      │  │    regularly        │       │
│  └─────────────────────┘  └─────────────────────┘       │
│                                                           │
│  ┌─────────────────────┐  ┌─────────────────────┐       │
│  │  scan2food_dev      │  │  scan2food_user     │       │
│  │  (Dev User)         │  │  (Prod User)        │       │
│  │                     │  │                     │       │
│  │  Access to:         │  │  Access to:         │       │
│  │  scan2food_local    │  │  scan2food_db       │       │
│  │  only               │  │  only               │       │
│  └─────────────────────┘  └─────────────────────┘       │
└──────────────────────────────────────────────────────────┘
```

## Configuration Files

### .env (Local)
```env
DB_NAME=scan2food_local      # ← Different database
DB_USER=scan2food_dev        # ← Different user
DB_PASSWORD=dev_password_123 # ← Different password
DB_HOST=localhost
DB_PORT=5432
```

### .env (Production - on server)
```env
DB_NAME=scan2food_db         # ← Production database
DB_USER=scan2food_user       # ← Production user
DB_PASSWORD=scann2Food       # ← Production password
DB_HOST=localhost
DB_PORT=5432
```

## Backup & Restore Flow

```
┌─────────────────┐
│  Production DB  │
│  scan2food_db   │
└────────┬────────┘
         │
         │ pg_dump (backup)
         │
         ▼
┌─────────────────┐
│  dbbckup.sql    │
│  (Backup File)  │
└────────┬────────┘
         │
         │ psql (restore)
         │
         ▼
┌─────────────────┐
│  Local DB       │
│  scan2food_local│
└─────────────────┘
```

## Security Model

### Local Development
- **Purpose:** Development and testing
- **Data Sensitivity:** Low (test data)
- **Access:** Only you
- **Credentials:** Simple (dev_password_123)
- **Backup Frequency:** As needed

### Production
- **Purpose:** Live application
- **Data Sensitivity:** High (real user data)
- **Access:** Application only
- **Credentials:** Strong (scann2Food)
- **Backup Frequency:** Regular automated backups

## Connection Strings

### Local
```
postgresql://scan2food_dev:dev_password_123@localhost:5432/scan2food_local
```

### Production
```
postgresql://scan2food_user:scann2Food@localhost:5432/scan2food_db
```

## Migration Path

### Before (SQLite)
```
Local: SQLite file (db.sqlite3)
  ↓
Production: PostgreSQL (scan2food_db)
```

### After (PostgreSQL)
```
Local: PostgreSQL (scan2food_local)
  ↓
Production: PostgreSQL (scan2food_db)
```

## Benefits

1. **Development Parity:** Same database engine everywhere
2. **Feature Testing:** Test PostgreSQL-specific features locally
3. **Query Optimization:** Optimize queries with same database
4. **Migration Testing:** Test migrations before production
5. **Concurrent Testing:** Test concurrent connections locally

## File Structure

```
project/
├── application/scan2food/
│   ├── .env                    # Local DB config
│   └── theatreApp/
│       └── settings.py         # Reads from .env
├── dbbckup.sql                 # Production backup
├── setup_postgres_local.bat    # Setup script
└── verify_postgres_setup.py    # Verification script
```

## Quick Reference

| Aspect | Local | Production |
|--------|-------|------------|
| Database | scan2food_local | scan2food_db |
| User | scan2food_dev | scan2food_user |
| Password | dev_password_123 | scann2Food |
| Host | localhost | localhost |
| Port | 5432 | 5432 |
| Purpose | Development | Live app |
| Data | Test data | Real data |

---

**Remember:** Local and production databases are completely separate. Changes to one don't affect the other!
