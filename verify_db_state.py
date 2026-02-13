from users.models import UserProfile, User
print("All Users:")
for u in User.objects.all():
    print(f"User: {u.username}, ID: {u.id}, IsActive: {u.is_active}")
    try:
        p = u.userprofile
        print(f"  Profile: Role={p.role}, Coach={p.coach}, Sport={p.sport}, DOB={p.date_of_birth}")
    except UserProfile.DoesNotExist:
        print("  NO PROFILE FOUND")

print("\nUnassigned Athletes Query Check:")
unassigned = UserProfile.objects.filter(role='Athlete', coach__isnull=True)
print(f"Count: {unassigned.count()}")
for p in unassigned:
    print(f"  - {p.user.username} (Coach: {p.coach})")
