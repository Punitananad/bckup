#!/usr/bin/env python3
"""
API Key Security Test Script
Tests that API key authentication is working correctly
"""

import requests
import sys
import os

# Configuration
BASE_URL = "https://scan2food.com"  # Change to your domain
TEST_THEATRE_ID = 1  # Change to a valid theatre ID

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_test(name, passed, message=""):
    """Print test result with color"""
    status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
    print(f"{status} - {name}")
    if message:
        print(f"  {message}")
    print()

def test_api_without_key():
    """Test that API rejects requests without API key"""
    print(f"{YELLOW}Test 1: API without key (should fail){RESET}")
    
    url = f"{BASE_URL}/theatre/api/all-menu/{TEST_THEATRE_ID}"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 401:
            data = response.json()
            if 'error' in data and 'API key' in data['error']:
                print_test("API rejects requests without key", True, 
                          f"Status: {response.status_code}, Message: {data['error']}")
                return True
            else:
                print_test("API rejects requests without key", False,
                          f"Wrong error message: {data}")
                return False
        else:
            print_test("API rejects requests without key", False,
                      f"Expected 401, got {response.status_code}")
            return False
            
    except Exception as e:
        print_test("API rejects requests without key", False, f"Error: {str(e)}")
        return False

def test_api_with_invalid_key():
    """Test that API rejects requests with invalid API key"""
    print(f"{YELLOW}Test 2: API with invalid key (should fail){RESET}")
    
    url = f"{BASE_URL}/theatre/api/all-menu/{TEST_THEATRE_ID}"
    headers = {'X-API-Key': 'invalid_key_12345'}
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 401:
            data = response.json()
            if 'error' in data and 'API key' in data['error']:
                print_test("API rejects invalid key", True,
                          f"Status: {response.status_code}, Message: {data['error']}")
                return True
            else:
                print_test("API rejects invalid key", False,
                          f"Wrong error message: {data}")
                return False
        else:
            print_test("API rejects invalid key", False,
                      f"Expected 401, got {response.status_code}")
            return False
            
    except Exception as e:
        print_test("API rejects invalid key", False, f"Error: {str(e)}")
        return False

def test_api_with_valid_key(api_key):
    """Test that API accepts requests with valid API key"""
    print(f"{YELLOW}Test 3: API with valid key (should succeed){RESET}")
    
    url = f"{BASE_URL}/theatre/api/all-menu/{TEST_THEATRE_ID}"
    headers = {'X-API-Key': api_key}
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if 'all_category' in data or 'commission' in data:
                print_test("API accepts valid key", True,
                          f"Status: {response.status_code}, Data received successfully")
                return True
            else:
                print_test("API accepts valid key", False,
                          f"Unexpected response format: {data}")
                return False
        else:
            print_test("API accepts valid key", False,
                      f"Expected 200, got {response.status_code}")
            return False
            
    except Exception as e:
        print_test("API accepts valid key", False, f"Error: {str(e)}")
        return False

def test_webhook_without_key():
    """Test that webhooks work without API key"""
    print(f"{YELLOW}Test 4: Webhook without key (should succeed){RESET}")
    
    # Test with a webhook endpoint (GET request should return 200 or 405)
    url = f"{BASE_URL}/theatre/api/razorpay-webhook-url"
    
    try:
        response = requests.get(url)
        
        # Webhooks typically return 200 or 405 (Method Not Allowed) for GET
        if response.status_code in [200, 405]:
            print_test("Webhook works without API key", True,
                      f"Status: {response.status_code} (webhooks don't require API key)")
            return True
        elif response.status_code == 401:
            print_test("Webhook works without API key", False,
                      "Webhook is incorrectly requiring API key!")
            return False
        else:
            print_test("Webhook works without API key", True,
                      f"Status: {response.status_code} (acceptable for webhook)")
            return True
            
    except Exception as e:
        print_test("Webhook works without API key", False, f"Error: {str(e)}")
        return False

def test_create_order_without_key():
    """Test that create-order endpoint requires API key"""
    print(f"{YELLOW}Test 5: Create order without key (should fail){RESET}")
    
    url = f"{BASE_URL}/theatre/api/create-order"
    data = {
        'theatre_id': TEST_THEATRE_ID,
        'seat': 'Hall A | A1',
        'cart_data': {}
    }
    
    try:
        response = requests.post(url, json=data)
        
        if response.status_code == 401:
            print_test("Create order requires API key", True,
                      f"Status: {response.status_code}")
            return True
        else:
            print_test("Create order requires API key", False,
                      f"Expected 401, got {response.status_code}")
            return False
            
    except Exception as e:
        print_test("Create order requires API key", False, f"Error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("API Key Security Test Suite")
    print("="*60 + "\n")
    
    # Get API key from environment or prompt
    api_key = os.environ.get('API_KEY')
    
    if not api_key:
        print(f"{YELLOW}API_KEY not found in environment variables{RESET}")
        api_key = input("Enter your API key to test (or press Enter to skip valid key test): ").strip()
    
    results = []
    
    # Run tests
    results.append(("API without key", test_api_without_key()))
    results.append(("API with invalid key", test_api_with_invalid_key()))
    
    if api_key:
        results.append(("API with valid key", test_api_with_valid_key(api_key)))
    else:
        print(f"{YELLOW}Skipping valid key test (no API key provided){RESET}\n")
    
    results.append(("Webhook without key", test_webhook_without_key()))
    results.append(("Create order without key", test_create_order_without_key()))
    
    # Summary
    print("="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n{GREEN}✓ All tests passed! API key security is working correctly.{RESET}\n")
        return 0
    else:
        print(f"\n{RED}✗ Some tests failed. Please review the configuration.{RESET}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
