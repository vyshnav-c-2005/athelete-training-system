from django.db import models
from django.contrib.auth.models import User

# --- Base Session Model ---
class TrainingSession(models.Model):
    SESSION_TYPES = [
        ('training', 'Training'),
        ('competition', 'Competition'),
        ('recovery', 'Recovery'),
    ]

    DISCIPLINES = [
        # Track
        ('100m', '100m Sprint'),
        ('200m', '200m Sprint'),
        ('400m', '400m Sprint'),
        ('800m', '800m Run'),
        ('1500m', '1500m Run'),
        # Jumps
        ('long_jump', 'Long Jump'),
        ('high_jump', 'High Jump'),
        ('triple_jump', 'Triple Jump'),
        # Throws
        ('shot_put', 'Shot Put'),
        ('discus', 'Discus Throw'),
        ('javelin', 'Javelin Throw'),
        ('hammer', 'Hammer Throw'),
    ]

    ATHLETE_TYPES = [
        ('runner', 'Runner'),
        ('jumper', 'Jumper'),
        ('thrower', 'Thrower'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    discipline = models.CharField(max_length=20, choices=DISCIPLINES)
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES, default='training')
    athlete_type = models.CharField(max_length=20, choices=ATHLETE_TYPES)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.discipline} ({self.date})"

    @property
    def specific_session(self):
        """Helper to get the child object"""
        if hasattr(self, 'runnersession'): return self.runnersession
        if hasattr(self, 'jumpersession'): return self.jumpersession
        if hasattr(self, 'throwersession'): return self.throwersession
        return None


# --- Event Specific Models ---

class RunnerSession(models.Model):
    session = models.OneToOneField(TrainingSession, on_delete=models.CASCADE)
    distance_m = models.FloatField(help_text="Distance in meters (e.g., 100, 200)")
    time_seconds = models.FloatField(help_text="Time in seconds")
    repetitions = models.IntegerField(default=1, help_text="Number of reps")

    def __str__(self):
        return f"Run: {self.distance_m}m x {self.repetitions}"

class JumperSession(models.Model):
    session = models.OneToOneField(TrainingSession, on_delete=models.CASCADE)
    attempts = models.IntegerField(default=1)
    best_jump_m = models.FloatField(help_text="Best result in meters")

    def __str__(self):
        return f"Jump: {self.best_jump_m}m (Best)"

class ThrowerSession(models.Model):
    session = models.OneToOneField(TrainingSession, on_delete=models.CASCADE)
    implement_weight_kg = models.FloatField(help_text="Weight of implement in kg")
    attempts = models.IntegerField(default=1)
    best_throw_m = models.FloatField(help_text="Best result in meters")

    def __str__(self):
        return f"Throw: {self.best_throw_m}m ({self.implement_weight_kg}kg)"
