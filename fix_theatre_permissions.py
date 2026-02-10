import re

# Read the file
with open('application/scan2food/theatre/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to match the old permission check
pattern = r'permission = Permission\.objects\.get\(codename=["\']([^"\']+)["\']\)\s+if request\.user\.groups\.first\(\)\.permissions\.filter\(id=permission\.id\)\.exists\(\):'

# Replacement
replacement = r'if user_has_permission(request.user, "\1"):'

# Replace all occurrences
new_content = re.sub(pattern, replacement, content)

# Write back
with open('application/scan2food/theatre/views.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Fixed all permission checks in theatre/views.py")
print(f"Replaced {len(re.findall(pattern, content))} occurrences")
