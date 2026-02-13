from users.models import UserProfile, User
try:
    last_user = User.objects.latest('date_joined')
    print(f"Last User: {last_user.username} (ID: {last_user.id})")
    print(f"  Date Joined: {last_user.date_joined}")
    print(f"  Is Active: {last_user.is_active}")
    
    profile = last_user.userprofile
    print(f"  Profile Role: {profile.role}")
    print(f"  Profile Coach: {profile.coach}")
    print(f"  Profile ID: {profile.id}")
    
    # Check if this user is in the unassigned query
    is_unassigned = UserProfile.objects.filter(role='Athlete', coach__isnull=True, id=profile.id).exists()
    print(f"  Is in Unassigned Query? {is_unassigned}")

except Exception as e:
    print(f"Error: {e}")
