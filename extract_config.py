"""
Configuration Extractor for scan2food
Extracts all API keys and configuration from the database
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

from adminPortal.models import PaymentGateway, Detail, GSTDetails
from theatre.models import Theatre
from django.contrib.auth.models import User

def extract_all_config():
    """Extract all configuration from database"""
    
    print("="*70)
    print("🔐 SCAN2FOOD CONFIGURATION EXTRACTOR")
    print("="*70)
    print()
    
    # 1. Payment Gateways
    print("💳 PAYMENT GATEWAY CREDENTIALS")
    print("-"*70)
    
    gateways = PaymentGateway.objects.all()
    if gateways.exists():
        for gateway in gateways:
            print(f"\n[{gateway.name}]")
            print(f"  Gateway Key/ID:     {gateway.gateway_key}")
            print(f"  Gateway Secret:     {gateway.gateway_secret}")
            if gateway.gateway_salt:
                print(f"  Gateway Salt:       {gateway.gateway_salt}")
            if gateway.merchant_id:
                print(f"  Merchant ID:        {gateway.merchant_id}")
            print(f"  Active:             {gateway.is_active}")
    else:
        print("⚠️  No payment gateways configured in database")
    
    print("\n" + "="*70)
    
    # 2. Theatre/Restaurant Details
    print("\n🏪 THEATRE/RESTAURANT DETAILS")
    print("-"*70)
    
    theatres = Theatre.objects.all()
    if theatres.exists():
        for theatre in theatres:
            print(f"\n[{theatre.name}]")
            print(f"  ID:                 {theatre.pk}")
            print(f"  Phone:              {theatre.phone_number}")
            print(f"  Email:              {theatre.email}")
            print(f"  Address:            {theatre.address}")
            
            # Get detail if exists
            try:
                detail = theatre.detail
                print(f"  Owner Name:         {detail.name}")
                print(f"  Secondary Phone:    {detail.secondary_mobile}")
                print(f"  Selected Gateway:   {detail.selected_gateway.name if detail.selected_gateway else 'None'}")
                print(f"  Payment Model:      {detail.payment_model}")
                print(f"  Razorpay Account:   {detail.razorpay_id if detail.razorpay_id else 'Not configured'}")
                print(f"  Scanning Service:   {detail.scaning_service}")
                
                # GST Details
                try:
                    gst = detail.gst_details
                    print(f"\n  GST Details:")
                    print(f"    GST Number:       {gst.gst_number}")
                    print(f"    Business Name:    {gst.business_name}")
                    print(f"    State:            {gst.gst_state}")
                    print(f"    State Code:       {gst.state_code}")
                except:
                    print(f"  GST Details:        Not configured")
                    
            except:
                print("  Detail:             Not configured")
    else:
        print("⚠️  No theatres/restaurants found in database")
    
    print("\n" + "="*70)
    
    # 3. Admin Users
    print("\n👤 ADMIN USERS")
    print("-"*70)
    
    admins = User.objects.filter(is_superuser=True)
    if admins.exists():
        for admin in admins:
            print(f"\n  Username:           {admin.username}")
            print(f"  Email:              {admin.email}")
            print(f"  Is Active:          {admin.is_active}")
            print(f"  Last Login:         {admin.last_login}")
    else:
        print("⚠️  No admin users found")
    
    print("\n" + "="*70)
    
    # 4. Database Info
    print("\n🗄️  DATABASE INFORMATION")
    print("-"*70)
    
    from django.conf import settings
    db_config = settings.DATABASES['default']
    print(f"  Engine:             {db_config['ENGINE']}")
    print(f"  Name:               {db_config['NAME']}")
    if 'USER' in db_config:
        print(f"  User:               {db_config.get('USER', 'N/A')}")
        print(f"  Password:           {db_config.get('PASSWORD', 'N/A')}")
        print(f"  Host:               {db_config.get('HOST', 'N/A')}")
        print(f"  Port:               {db_config.get('PORT', 'N/A')}")
    
    print("\n" + "="*70)
    
    # 5. Settings.py Important Values
    print("\n⚙️  SETTINGS.PY CONFIGURATION")
    print("-"*70)
    
    print(f"  SECRET_KEY:         {settings.SECRET_KEY}")
    print(f"  DEBUG:              {settings.DEBUG}")
    print(f"  ALLOWED_HOSTS:      {', '.join(settings.ALLOWED_HOSTS)}")
    print(f"  TIME_ZONE:          {settings.TIME_ZONE}")
    print(f"  STATIC_URL:         {settings.STATIC_URL}")
    print(f"  MEDIA_URL:          {settings.MEDIA_URL}")
    print(f"  MEDIA_ROOT:         {settings.MEDIA_ROOT}")
    
    # Redis Configuration
    if 'CHANNEL_LAYERS' in dir(settings):
        redis_config = settings.CHANNEL_LAYERS['default']['CONFIG']['hosts'][0]
        print(f"  Redis Host:         {redis_config[0]}")
        print(f"  Redis Port:         {redis_config[1]}")
    
    print("\n" + "="*70)
    
    # 6. Generate .env file template
    print("\n📝 GENERATING .env FILE TEMPLATE")
    print("-"*70)
    
    env_content = """# Django Settings
SECRET_KEY={secret_key}
DEBUG=False
ALLOWED_HOSTS={allowed_hosts}

# Database Configuration (if using PostgreSQL)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=scan2food_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Redis Configuration
REDIS_HOST=127.0.0.1
REDIS_PORT=6379

# Payment Gateway Credentials
""".format(
        secret_key=settings.SECRET_KEY,
        allowed_hosts=','.join(settings.ALLOWED_HOSTS)
    )
    
    # Add payment gateway credentials
    for gateway in gateways:
        gateway_name = gateway.name.upper().replace(' ', '_').replace('-', '_')
        env_content += f"\n# {gateway.name}\n"
        env_content += f"{gateway_name}_KEY={gateway.gateway_key}\n"
        env_content += f"{gateway_name}_SECRET={gateway.gateway_secret}\n"
        if gateway.gateway_salt:
            env_content += f"{gateway_name}_SALT={gateway.gateway_salt}\n"
        if gateway.merchant_id:
            env_content += f"{gateway_name}_MERCHANT_ID={gateway.merchant_id}\n"
    
    env_content += """
# Security Settings (for production)
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000

# Email Configuration (if needed)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
"""
    
    # Save .env template
    env_file_path = project_root / "application" / "scan2food" / ".env.template"
    with open(env_file_path, 'w') as f:
        f.write(env_content)
    
    print(f"✅ .env template saved to: {env_file_path}")
    print()
    
    # 7. Generate deployment config file
    print("\n📋 GENERATING DEPLOYMENT CONFIG")
    print("-"*70)
    
    deployment_config = {
        "database": {
            "current_engine": db_config['ENGINE'],
            "current_name": str(db_config['NAME']),
            "production_recommendation": "PostgreSQL"
        },
        "payment_gateways": {},
        "theatres": [],
        "redis": {
            "host": redis_config[0] if 'CHANNEL_LAYERS' in dir(settings) else "127.0.0.1",
            "port": redis_config[1] if 'CHANNEL_LAYERS' in dir(settings) else 6379
        },
        "settings": {
            "debug": settings.DEBUG,
            "allowed_hosts": settings.ALLOWED_HOSTS,
            "time_zone": settings.TIME_ZONE
        }
    }
    
    # Add payment gateways
    for gateway in gateways:
        deployment_config["payment_gateways"][gateway.name] = {
            "key": gateway.gateway_key,
            "secret": gateway.gateway_secret,
            "salt": gateway.gateway_salt,
            "merchant_id": gateway.merchant_id,
            "active": gateway.is_active
        }
    
    # Add theatres
    for theatre in theatres:
        theatre_data = {
            "id": theatre.pk,
            "name": theatre.name,
            "phone": theatre.phone_number,
            "email": theatre.email
        }
        try:
            detail = theatre.detail
            theatre_data["payment_model"] = detail.payment_model
            theatre_data["selected_gateway"] = detail.selected_gateway.name if detail.selected_gateway else None
            theatre_data["razorpay_account"] = detail.razorpay_id
        except:
            pass
        deployment_config["theatres"].append(theatre_data)
    
    import json
    config_file_path = project_root / "deployment_config.json"
    with open(config_file_path, 'w') as f:
        json.dump(deployment_config, f, indent=2)
    
    print(f"✅ Deployment config saved to: {config_file_path}")
    print()
    
    print("="*70)
    print("✅ EXTRACTION COMPLETE!")
    print("="*70)
    print()
    print("📁 Files created:")
    print(f"   1. {env_file_path}")
    print(f"   2. {config_file_path}")
    print()
    print("⚠️  IMPORTANT SECURITY NOTES:")
    print("   - Keep these files PRIVATE and SECURE")
    print("   - Never commit them to version control")
    print("   - Use different credentials for production")
    print("   - Change SECRET_KEY for production deployment")
    print()

if __name__ == "__main__":
    try:
        extract_all_config()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you're running this from the project root directory")
        print("and that the database file exists.")
        import traceback
        traceback.print_exc()
