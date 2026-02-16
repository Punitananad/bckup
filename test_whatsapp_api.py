#!/usr/bin/env python3
"""
Test WhatsApp API Connection
This script tests if the WhatsApp Meta API credentials are working correctly
"""

import requests
import json

# Your WhatsApp credentials from whatsapp_msg_utils.py
ACCESS_TOKEN = "EAAJph1TVFooBQnWmQjHNFPaiwDrGTk0wDL79VnZAvRd3UnDsIQ4L0hgHVdExqf1K0f65iG76dtYupw88NfLuQwmdNur3QrbPSjZCpPkOforaZA3Bt1Ju2wo8CEab2fgey7ffXDA8tm8oZAgqvtB4eZBWbgwBH51PNXiPAEBGAOJc800ie7p7xZClEAJhUELFkdowZDZD"
PHONE_NUMBER_ID = "706345399217798"

print("=" * 60)
print("WHATSAPP API DIAGNOSTIC TEST")
print("=" * 60)
print()

# Test 1: Check if access token is valid
print("Test 1: Validating Access Token...")
print("-" * 60)

url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
}

try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ Access token is VALID")
        data = response.json()
        print(f"Phone Number ID: {data.get('id')}")
        print(f"Display Name: {data.get('display_phone_number')}")
        print(f"Quality Rating: {data.get('quality_rating')}")
    else:
        print("❌ Access token is INVALID or EXPIRED")
        error_data = response.json()
        print(f"Error: {error_data.get('error', {}).get('message')}")
        print(f"Error Code: {error_data.get('error', {}).get('code')}")
        print()
        print("SOLUTION:")
        print("1. Go to Meta Business Manager: https://business.facebook.com/")
        print("2. Navigate to WhatsApp > API Setup")
        print("3. Generate a new access token")
        print("4. Update ACCESS_TOKEN in application/scan2food/chat_bot/whatsapp_msg_utils.py")
        
except Exception as e:
    print(f"❌ Connection Error: {str(e)}")

print()
print("=" * 60)

# Test 2: Check message templates
print("Test 2: Checking Message Templates...")
print("-" * 60)

url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/message_templates"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
}

try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        templates = data.get('data', [])
        print(f"✅ Found {len(templates)} message templates")
        print()
        print("Available Templates:")
        for template in templates:
            status = template.get('status')
            name = template.get('name')
            language = template.get('language')
            print(f"  - {name} ({language}) - Status: {status}")
            
        print()
        print("Required Templates for Scan2Food:")
        required_templates = [
            "new_order_confirmation_",
            "refund_confirmed",
            "refund_query",
            "activate_service",
            "deactivate_service"
        ]
        
        template_names = [t.get('name') for t in templates]
        for req_template in required_templates:
            if req_template in template_names:
                print(f"  ✅ {req_template} - Found")
            else:
                print(f"  ❌ {req_template} - Missing")
    else:
        print("❌ Failed to fetch templates")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")

print()
print("=" * 60)

# Test 3: Check permissions
print("Test 3: Checking API Permissions...")
print("-" * 60)

print("Required Permissions:")
print("  - whatsapp_business_messaging")
print("  - whatsapp_business_management")
print()
print("To verify permissions:")
print("1. Go to Meta Business Manager")
print("2. Settings > Business Settings > System Users")
print("3. Check your system user has the required permissions")

print()
print("=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)
print()

print("COMMON ISSUES AND SOLUTIONS:")
print()
print("1. Token Expired:")
print("   - Meta tokens expire after 60-90 days")
print("   - Generate a new permanent token from Meta Business Manager")
print()
print("2. Missing Templates:")
print("   - Create message templates in Meta Business Manager")
print("   - Wait for approval (usually 1-24 hours)")
print()
print("3. Phone Number Not Verified:")
print("   - Verify your WhatsApp Business phone number")
print("   - Complete business verification if required")
print()
print("4. Rate Limits:")
print("   - Check if you've exceeded message limits")
print("   - Upgrade your WhatsApp Business tier if needed")
print()
