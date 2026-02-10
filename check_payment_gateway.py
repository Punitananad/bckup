#!/usr/bin/env python
"""
Quick script to check payment gateway configuration
Run this on the server to see what gateways are configured
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'theatreApp.settings')
django.setup()

from adminPortal.models import PaymentGateway

print("=" * 60)
print("PAYMENT GATEWAY CONFIGURATION CHECK")
print("=" * 60)

gateways = PaymentGateway.objects.all()

if not gateways.exists():
    print("\n❌ NO PAYMENT GATEWAYS CONFIGURED!")
    print("\nPlease add a payment gateway in the admin panel:")
    print("https://calculatentrade.com/admin/adminPortal/paymentgateway/")
else:
    print(f"\n✅ Found {gateways.count()} payment gateway(s):\n")
    
    for gateway in gateways:
        print(f"Name: {gateway.name}")
        print(f"Active: {gateway.is_active}")
        print(f"Has Key: {'Yes' if gateway.gateway_key else 'No'}")
        print(f"Has Secret: {'Yes' if gateway.gateway_secret else 'No'}")
        print("-" * 60)

print("\n" + "=" * 60)
print("EXPECTED GATEWAY NAMES (case-sensitive):")
print("=" * 60)
print("- Razorpay")
print("- split_razorpay")
print("- Cashfree")
print("- Phonepe")
print("- PayU")
print("- CCAvenue (or ccavenue)")
print("\n⚠️  Make sure your gateway name matches exactly!")
