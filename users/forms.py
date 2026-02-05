from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import UserProfile, AthleteProfile, CoachProfile, Suggestion

class SignupForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}))
    
    # Optional profile fields
    full_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=UserProfile.GENDER_CHOICES, required=False)
    sport = forms.CharField(required=False)
    height = forms.FloatField(required=False)
    weight = forms.FloatField(required=False)
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password'])
        
        if commit:
            user.save()
            if hasattr(user, 'userprofile'):
                profile = user.userprofile
                profile.date_of_birth = self.cleaned_data.get('date_of_birth')
                profile.gender = self.cleaned_data.get('gender')
                profile.sport = self.cleaned_data.get('sport')
                if self.cleaned_data.get('height'): profile.height_cm = self.cleaned_data.get('height')
                if self.cleaned_data.get('weight'): profile.weight_kg = self.cleaned_data.get('weight')
                if self.cleaned_data.get('role'): profile.role = self.cleaned_data.get('role')
                profile.save()
            
        return user

class LoginForm(forms.Form):
    username = forms.CharField(label="Username or Email", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username or Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

# --- Existing Forms (Preserved) ---
class AthleteProfileForm(forms.ModelForm):
    class Meta:
        model = AthleteProfile
        fields = ['sport_group', 'sport_event', 'age', 'height_cm', 'weight_kg', 'experience_level', 'training_goal']

class AthleteSignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'password', 'email']

class CoachSignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'password', 'email']

# --- UserProfile Form (Active) ---
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['gender', 'sport', 'date_of_birth', 'height_cm', 'weight_kg', 'role']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'sport': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your main sport'}),
            'height_cm': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Height in cm'}),
            'weight_kg': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Weight in kg'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }

class AssignCoachForm(forms.ModelForm):
    """
    Form to assign a coach to an athlete.
    """
    coach = forms.ModelChoiceField(
        queryset=UserProfile.objects.filter(role='Coach'),
        empty_label="-- Select Coach --",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Select Coach"
    )

    class Meta:
        model = UserProfile
        fields = ['coach']

class SuggestionForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write your suggestion here...'}),
        }

