from django import forms
from .models import WorkoutLog

class WorkoutForm(forms.ModelForm):
    class Meta:
        model = WorkoutLog
        fields = [
            'duration_minutes',
            'distance_km',
            'intensity',
            'average_heart_rate',
            'sets_reps',
        ]
