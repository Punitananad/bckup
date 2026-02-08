"""
Generate a new Django SECRET_KEY
"""

from django.core.management.utils import get_random_secret_key

print("="*70)
print("🔑 DJANGO SECRET_KEY GENERATOR")
print("="*70)
print()
print("Your NEW SECRET_KEY:")
print()
print(get_random_secret_key())
print()
print("="*70)
print("📝 INSTRUCTIONS:")
print("="*70)
print()
print("1. Copy the key above")
print("2. Open: application/scan2food/theatreApp/settings.py")
print("3. Find line 21 (SECRET_KEY = '...')")
print("4. Replace with your new key")
print("5. Save the file")
print()
print("⚠️  IMPORTANT: Keep this key SECRET and SECURE!")
print()
