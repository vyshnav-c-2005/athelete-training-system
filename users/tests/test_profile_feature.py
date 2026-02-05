from django.test import TestCase, Client
from django.contrib.auth.models import User
from users.models import UserProfile
import datetime

class UserProfileTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testathlete', password='password123')
        # Profile should be created by signal
        
    def test_profile_created_signal(self):
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())
        profile = self.user.userprofile
        self.assertEqual(profile.role, 'Athlete') # Default

    def test_profile_view_login_required(self):
        response = self.client.get('/users/profile/')
        self.assertNotEqual(response.status_code, 200) # Should redirect

    def test_profile_view_logged_in(self):
        self.client.login(username='testathlete', password='password123')
        response = self.client.get('/users/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testathlete')

    def test_edit_profile(self):
        self.client.login(username='testathlete', password='password123')
        data = {
            'gender': 'Male',
            'sport': 'Sprinting',
            'date_of_birth': '2000-01-01',
            'height_cm': 180,
            'weight_kg': 75,
            'role': 'Athlete'
        }
        response = self.client.post('/users/profile/edit/', data)
        self.assertEqual(response.status_code, 302) # Redirect after save
        
        self.user.userprofile.refresh_from_db()
        self.assertEqual(self.user.userprofile.sport, 'Sprinting')
        self.assertEqual(self.user.userprofile.height_cm, 180.0)
        self.assertEqual(self.user.userprofile.bmi(), 23.15)
