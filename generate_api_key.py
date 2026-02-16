#!/usr/bin/env python3
"""
Generate a secure API key for Scan2Food
"""

import secrets

def generate_api_key(length=32):
    """
    Generate a cryptographically secure random API key.
    
    Args:
        length: Number of bytes (default 32 = 256 bits of entropy)
    
    Returns:
        URL-safe base64 encoded string
    """
    return secrets.token_urlsafe(length)

def main():
    print("=" * 60)
    print("Scan2Food API Key Generator")
    print("=" * 60)
    print()
    
    # Generate key
    api_key = generate_api_key()
    
    print("Your new API key:")
    print()
    print(f"  {api_key}")
    print()
    print("=" * 60)
    print()
    
    # Instructions
    print("Next steps:")
    print()
    print("1. Copy the key above")
    print()
    print("2. Add to your .env file:")
    print(f"   API_KEY={api_key}")
    print()
    print("3. Restart your services:")
    print("   sudo systemctl restart gunicorn")
    print("   sudo systemctl restart daphne")
    print()
    print("=" * 60)
    print()
    
    # Security notes
    print("Security Notes:")
    print("- Keep this key secret")
    print("- Don't commit it to git")
    print("- Rotate every 3-6 months")
    print("- Use different keys for dev/production")
    print()

if __name__ == "__main__":
    main()
