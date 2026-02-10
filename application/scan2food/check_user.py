import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'theatreApp.settings')
django.setup()

from django.contrib.auth.models import User
from theatre.models import UserProfile

# Check user with mobile number
username = '7988269870'
u = User.objects.filter(username=username).first()

print(f"User found: {u is not None}")
if u:
    print(f"Username: {u.username}")
    print(f"Is superuser: {u.is_superuser}")
    print(f"Groups: {[g.name for g in u.groups.all()]}")
    
    profile = UserProfile.objects.filter(user=u).first()
    print(f"Has UserProfile: {profile is not None}")
    
    if profile:
        print(f"Theatre: {profile.theatre.name if profile.theatre else 'None'}")
        print(f"Active status: {profile.active_status}")
    else:
        print("No UserProfile found - creating one...")
        from theatre.models import Theatre
        theatre = Theatre.objects.first()
        if theatre:
            profile = UserProfile.objects.create(
                user=u,
                theatre=theatre,
                active_status=True
            )
            print(f"Created UserProfile linked to theatre: {theatre.name}")
        else:
            print("No theatre found in database!")
else:
    print(f"User with username '{username}' not found in database")
