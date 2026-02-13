import os
import django
import sys

sys.path.append('c:/project02')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'athlete_ai_system.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile

def check_athletes():
    with open('c:/project02/debug_athletes_output.txt', 'w', encoding='utf-8') as f:
        f.write("--- ALL PROFILES ---\n")
        profiles = UserProfile.objects.all().order_by('user__username')
        for p in profiles:
            f.write(f"User: {p.user.username:<15} Role: '{p.role}' Coach: {p.coach}\n")

        f.write("\n--- UNASSIGNED ATHLETES (role='Athlete', coach=None) ---\n")
        unassigned = UserProfile.objects.filter(role='Athlete', coach__isnull=True)
        f.write(f"Count: {unassigned.count()}\n")
        for p in unassigned:
            f.write(f" - {p.user.username}\n")

if __name__ == "__main__":
    check_athletes()
