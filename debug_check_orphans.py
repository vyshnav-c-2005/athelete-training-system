import os
import django
import sys

sys.path.append('c:/project02')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'athlete_ai_system.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile

def check_orphans():
    with open('c:/project02/debug_orphans.txt', 'w', encoding='utf-8') as f:
        f.write("--- RECENTLY JOINED USERS ---\n")
        users = User.objects.all().order_by('-date_joined')[:10]
        for u in users:
            has_profile = hasattr(u, 'userprofile')
            role = u.userprofile.role if has_profile else "NO PROFILE"
            f.write(f"User: {u.username:<15} Joined: {u.date_joined.strftime('%Y-%m-%d %H:%M:%S')} Profile: {has_profile} Role: {role}\n")

if __name__ == "__main__":
    check_orphans()
