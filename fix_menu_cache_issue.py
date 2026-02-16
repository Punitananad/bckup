#!/usr/bin/env python3
"""
Fix Menu Cache Issue
This script adds cache control headers to prevent browser caching of menu API
"""

import re

# Read the api_views.py file
with open('application/scan2food/theatre/api_views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the all_menu function and add @cache_control decorator
# Pattern to find the function definition
pattern = r'(@api_view\(\[\'GET\'\]\)\ndef all_menu\(request, pk=None\):)'

# Replacement with cache control decorator
replacement = r'@cache_control(no_cache=True, must_revalidate=True, no_store=True, max_age=0)\n@api_view([\'GET\'])\ndef all_menu(request, pk=None):'

# Check if cache_control is already imported
if 'from django.views.decorators.cache import' in content:
    # Add cache_control to existing import
    content = re.sub(
        r'from django\.views\.decorators\.cache import ([^\n]+)',
        r'from django.views.decorators.cache import \1, cache_control',
        content
    )
else:
    # Add new import after other django imports
    content = re.sub(
        r'(from django\.views\.decorators\.csrf import)',
        r'from django.views.decorators.cache import cache_control, never_cache\n\1',
        content
    )

# Apply the replacement
new_content = re.sub(pattern, replacement, content)

# Write back
with open('application/scan2food/theatre/api_views.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✓ Added cache control headers to all_menu endpoint")
print("✓ This will prevent browser from caching menu data")
print("\nNext steps:")
print("1. Restart Daphne: sudo systemctl restart daphne")
print("2. Restart Gunicorn: sudo systemctl restart gunicorn")
print("3. Test the menu page")
