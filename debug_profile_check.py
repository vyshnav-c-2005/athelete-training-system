import os
import django
import sys

# Force output to unbuffered
sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'athlete_ai_system.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from users.models import UserProfile
from django.urls import reverse

def check_profile():
    print("DEBUG: Starting check")
    try:
        url = reverse('users:profile')
        print(f"DEBUG: URL is {url}")
    except Exception as e:
        print(f"DEBUG: URL Reverse Failed: {e}")
        return

    username = 'debug_user_final'
    try:
        if User.objects.filter(username=username).exists():
            User.objects.get(username=username).delete()
        user = User.objects.create_user(username=username, password='password123')
        print("DEBUG: User created")
    except Exception as e:
        print(f"DEBUG: User create failed: {e}")
        return

    try:
        profile = UserProfile.objects.get(user=user)
        print(f"DEBUG: Profile exists: {profile}")
    except Exception as e:
        print(f"DEBUG: Profile check failed: {e}")

    c = Client()
    if c.login(username=username, password='password123'):
        print("DEBUG: Login successful")
    else:
        print("DEBUG: Login failed")

    try:
        response = c.get(url)
        print(f"DEBUG: Response code: {response.status_code}")
        if response.status_code != 200:
            print(f"DEBUG: Response content (first 100 chars): {response.content[:100]}")
    except Exception as e:
        print(f"DEBUG: View access exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_profile()
