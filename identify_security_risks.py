"""
Security Risk Identifier for scan2food
Identifies all credentials and access points that need to be changed
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root / "application" / "scan2food"))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'theatreApp.settings')
django.setup()

from adminPortal.models import PaymentGateway, Detail
from theatre.models import Theatre
from django.contrib.auth.models import User
from django.conf import settings

def identify_risks():
    print("="*80)
    print("🚨 SECURITY RISK ASSESSMENT - scan2food")
    print("="*80)
    print()
    
    risks = []
    
    # 1. Django SECRET_KEY
    print("1️⃣  DJANGO SECRET_KEY")
    print("-"*80)
    print(f"   Current: {settings.SECRET_KEY}")
    print(f"   Status: 🔴 COMPROMISED - Old developer has this")
    print(f"   Action: Generate new key and replace in settings.py")
    risks.append("Django SECRET_KEY")
    print()
    
    # 2. Admin Users
    print("2️⃣  ADMIN USERS")
    print("-"*80)
    admins = User.objects.filter(is_superuser=True)
    for admin in admins:
        print(f"   Username: {admin.username}")
        print(f"   Email: {admin.email}")
        print(f"   Status: 🔴 CHANGE PASSWORD IMMEDIATELY")
        risks.append(f"Admin user: {admin.username}")
    
    # Check for other staff users
    staff = User.objects.filter(is_staff=True, is_superuser=False)
    if staff.exists():
        print(f"\n   ⚠️  Found {staff.count()} staff users:")
        for s in staff:
            print(f"      - {s.username} ({s.email})")
            print(f"        Status: 🟡 Review and change password if suspicious")
    print()
    
    # 3. Payment Gateways
    print("3️⃣  PAYMENT GATEWAY CREDENTIALS")
    print("-"*80)
    gateways = PaymentGateway.objects.all()
    if gateways.exists():
        for gateway in gateways:
            print(f"   [{gateway.name}]")
            print(f"   Key: {gateway.gateway_key}")
            print(f"   Secret: {gateway.gateway_secret[:10]}..." if len(gateway.gateway_secret) > 10 else gateway.gateway_secret)
            print(f"   Status: 🔴 CRITICAL - Old developer can access payments")
            print(f"   Action: Generate NEW credentials from {gateway.name} dashboard")
            print(f"           IMMEDIATELY REVOKE old credentials")
            risks.append(f"Payment Gateway: {gateway.name}")
            print()
    else:
        print("   ✅ No payment gateways in database (will be configured fresh)")
        print()
    
    # 4. Database Credentials
    print("4️⃣  DATABASE CREDENTIALS")
    print("-"*80)
    db_config = settings.DATABASES['default']
    if 'sqlite3' in db_config['ENGINE']:
        print(f"   Engine: SQLite")
        print(f"   File: {db_config['NAME']}")
        print(f"   Status: 🟡 File-based, secure if server access is secured")
    else:
        print(f"   Engine: {db_config['ENGINE']}")
        print(f"   User: {db_config.get('USER', 'N/A')}")
        print(f"   Password: {db_config.get('PASSWORD', 'N/A')}")
        print(f"   Status: 🔴 CHANGE DATABASE PASSWORD")
        risks.append("Database credentials")
    print()
    
    # 5. Redis
    print("5️⃣  REDIS CONFIGURATION")
    print("-"*80)
    if hasattr(settings, 'CHANNEL_LAYERS'):
        redis_config = settings.CHANNEL_LAYERS['default']['CONFIG']
        hosts = redis_config.get('hosts', [])
        password = redis_config.get('password', None)
        print(f"   Host: {hosts[0] if hosts else 'Not configured'}")
        if password:
            print(f"   Password: Set")
            print(f"   Status: 🟡 Change Redis password")
        else:
            print(f"   Password: NOT SET")
            print(f"   Status: 🔴 CRITICAL - Set Redis password immediately")
            risks.append("Redis password not set")
    print()
    
    # 6. Allowed Hosts
    print("6️⃣  ALLOWED HOSTS")
    print("-"*80)
    print(f"   Current: {', '.join(settings.ALLOWED_HOSTS)}")
    print(f"   Old IP: 134.209.149.31")
    print(f"   Status: 🟡 Update with NEW server IP")
    print(f"   Action: Add new IP, keep domain names")
    print()
    
    # 7. Theatre/Restaurant Razorpay Accounts
    print("7️⃣  THEATRE RAZORPAY LINKED ACCOUNTS")
    print("-"*80)
    theatres = Theatre.objects.all()
    if theatres.exists():
        for theatre in theatres:
            try:
                detail = theatre.detail
                if detail.razorpay_id:
                    print(f"   [{theatre.name}]")
                    print(f"   Razorpay Account: {detail.razorpay_id}")
                    print(f"   Status: 🔴 Old developer may have access")
                    print(f"   Action: Verify account ownership, change credentials")
                    risks.append(f"Theatre Razorpay: {theatre.name}")
                    print()
            except:
                pass
    else:
        print("   ✅ No theatres configured yet")
    print()
    
    # 8. Webhook URLs
    print("8️⃣  WEBHOOK URLs (Need to update in payment gateways)")
    print("-"*80)
    webhooks = [
        "/theatre/api/razorpay-webhook-url",
        "/theatre/api/split-razorpay-webhook-url",
        "/theatre/api/cashfree-data-request",
        "/theatre/api/phonepe-data-request",
        "/theatre/api/payu-webhook-url",
        "/theatre/api/ccavenue-hook"
    ]
    print(f"   Old Server: https://scan2food.com")
    print(f"   New Server: https://YOUR_NEW_IP (or keep domain after DNS update)")
    print(f"\n   Webhooks to update:")
    for webhook in webhooks:
        print(f"      - {webhook}")
    print(f"\n   Status: 🔴 Update in each payment gateway dashboard")
    print()
    
    # Summary
    print("="*80)
    print("📊 RISK SUMMARY")
    print("="*80)
    print(f"   Total Security Risks Found: {len(risks)}")
    print()
    print("   Critical Items to Change:")
    for i, risk in enumerate(risks, 1):
        print(f"      {i}. {risk}")
    print()
    
    # Priority Actions
    print("="*80)
    print("🎯 PRIORITY ACTIONS (DO THESE FIRST)")
    print("="*80)
    print()
    print("   IMMEDIATE (Next 1 hour):")
    print("   1. Backup database from live server")
    print("   2. Change Django admin password")
    print("   3. Generate new SECRET_KEY")
    print()
    print("   URGENT (Next 24 hours):")
    print("   4. Generate NEW payment gateway credentials")
    print("   5. Deploy to new server")
    print("   6. Update webhook URLs")
    print("   7. REVOKE old payment gateway credentials")
    print()
    print("   IMPORTANT (Next 48 hours):")
    print("   8. Update DNS to new IP")
    print("   9. Monitor all transactions")
    print("   10. Shut down old server")
    print()
    
    print("="*80)
    print("⚠️  CRITICAL WARNING")
    print("="*80)
    print()
    print("   The old developer currently has access to:")
    print("   ❌ Payment gateway accounts (can steal money)")
    print("   ❌ Customer data (privacy breach)")
    print("   ❌ Admin panel (can delete everything)")
    print("   ❌ Database (can corrupt data)")
    print("   ❌ Server (can crash application)")
    print()
    print("   DO NOT DELAY - ACT IMMEDIATELY!")
    print()
    print("="*80)

if __name__ == "__main__":
    try:
        identify_risks()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
