# PostgreSQL Backup Script

> This repository contains a simple Python script that automatically takes a backup of a PostgreSQL database.  

> The script is lightweight, easy to understand, and suitable for running manually or scheduling with cron.

---

## 📌 Overview

The script uses the PostgreSQL `pg_dump` command to generate a `.sql` backup of your database.  
Each backup file includes a timestamp in format (`%d-%b-%Y`), making it easy to track and manage historical backups.

---

## 📁 Project Structure

```mermaid
graph TD;
    User[Porject] --> | main.py |

```


## 🔧 Requirements

Ensure the following are installed on your system:

- **Python 3**
- **PostgreSQL client tools** (required: `pg_dump`)
- PostgreSQL database credentials

Verify that `pg_dump` is available:

```
bash
pg_dump --version
```