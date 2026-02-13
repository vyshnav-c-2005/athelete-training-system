import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'athlete_ai_system.settings')
django.setup()

from users.models import UserProfile, User

print("--- CHECKING LAST USER ---")
try:
    last_user = User.objects.latest('date_joined')
    print(f"Last User: {last_user.username}")
    print(f"  ID: {last_user.id}")
    print(f"  Date Joined: {last_user.date_joined}")
    print(f"  Is Active: {last_user.is_active}")
    
    # Check if this user has a profile
    if hasattr(last_user, 'userprofile'):
        profile = last_user.userprofile
        print(f"  Profile Role: {profile.role}")
        print(f"  Profile Coach: {profile.coach}")
        print(f"  Profile Sport: {profile.sport}")
        
        # Check why it might not be in unassigned
        is_unassigned = UserProfile.objects.filter(role='Athlete', coach__isnull=True, id=profile.id).exists()
        print(f"  Is in Unassigned Query? {is_unassigned}")
        
        if not is_unassigned:
             print(f"  WHY NOT? Role={profile.role}, Coach={profile.coach}")
    else:
        print("  NO PROFILE FOUND")

except Exception as e:
    print(f"Error: {e}")
