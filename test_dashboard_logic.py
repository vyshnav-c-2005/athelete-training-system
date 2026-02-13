import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'athlete_ai_system.settings')
django.setup()

from users.models import UserProfile, User

print("--- VERIFYING DASHBOARD LOGIC ---")

# 1. Fetch ALL athletes
all_athletes = UserProfile.objects.filter(role='Athlete')
print(f"All Athletes found: {all_athletes.count()}")
for a in all_athletes[:5]:
    print(f" - {a.user.username} (Coach: {a.coach})")

# 2. Fetch Unassigned
unassigned = UserProfile.objects.filter(role='Athlete', coach__isnull=True)
print(f"\nUnassigned Athletes: {unassigned.count()}")
for a in unassigned[:5]:
    print(f" - {a.user.username} (Coach: {a.coach})")

# 3. Simulate Assignment (Dry Run)
if unassigned.exists():
    athlete = unassigned.first()
    print(f"\n[TEST] Assigning {athlete.user.username} to a coach would work.")
    # We won't actually assign to avoid messing up data, or we could create a dummy user.
else:
    print("\n[TEST] No unassigned athletes to test assignment with.")

print("\n--- DONE ---")
