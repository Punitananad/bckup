#!/usr/bin/env python
"""
Verify PostgreSQL setup for local development
Run this script to check if your PostgreSQL database is properly configured
"""

import os
import sys

# Add Django project to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'application', 'scan2food'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'theatreApp.settings')

import django
django.setup()

from django.db import connection
from django.conf import settings

def verify_postgres_setup():
    print("=" * 60)
    print("PostgreSQL Setup Verification")
    print("=" * 60)
    print()
    
    # Check database configuration
    db_config = settings.DATABASES['default']
    print("📋 Database Configuration:")
    print(f"   Engine: {db_config['ENGINE']}")
    print(f"   Name: {db_config['NAME']}")
    print(f"   User: {db_config['USER']}")
    print(f"   Host: {db_config['HOST']}")
    print(f"   Port: {db_config['PORT']}")
    print()
    
    # Test connection
    print("🔌 Testing database connection...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"   ✅ Connected successfully!")
            print(f"   PostgreSQL version: {version.split(',')[0]}")
            print()
            
            # Check if tables exist
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            table_count = cursor.fetchone()[0]
            print(f"📊 Database Statistics:")
            print(f"   Tables: {table_count}")
            
            if table_count > 0:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    ORDER BY table_name 
                    LIMIT 10
                """)
                tables = cursor.fetchall()
                print(f"   Sample tables: {', '.join([t[0] for t in tables])}")
            else:
                print("   ⚠️  No tables found. You may need to:")
                print("      1. Restore backup: psql -U scan2food_dev -d scan2food_local -f dbbckup.sql")
                print("      2. Run migrations: python manage.py migrate")
            
            print()
            print("=" * 60)
            print("✅ PostgreSQL setup is working correctly!")
            print("=" * 60)
            
    except Exception as e:
        print(f"   ❌ Connection failed!")
        print(f"   Error: {str(e)}")
        print()
        print("Troubleshooting:")
        print("1. Make sure PostgreSQL is installed and running")
        print("2. Check your .env file has correct credentials")
        print("3. Run setup_postgres_local.bat to create database")
        print("4. Install psycopg2: pip install psycopg2-binary")
        print()
        return False
    
    return True

if __name__ == "__main__":
    try:
        verify_postgres_setup()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
