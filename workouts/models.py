from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


# ==========================
# Base Training Load Model
# ==========================

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

    INTENSITY_CHOICES = [
        ('low', 'Low (MET 4)'),
        ('moderate', 'Moderate (MET 7)'),
        ('high', 'High (MET 10)'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    date = models.DateField()
    discipline = models.CharField(max_length=20, choices=DISCIPLINES)
    session_type = models.CharField(
        max_length=20,
        choices=SESSION_TYPES,
        default='training'
    )

    # Core Load Metrics
    duration_minutes = models.FloatField(default=0)
    intensity = models.CharField(
        max_length=10,
        choices=INTENSITY_CHOICES,
        default='moderate'
    )

    rpe = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    calories_burned = models.FloatField(default=0)

    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    # ==========================
    # Calorie Calculation Engine
    # ==========================

    def save(self, *args, **kwargs):

        # Default weight fallback
        weight = 70.0

        try:
            if hasattr(self.user, 'athleteprofile') and self.user.athleteprofile.weight_kg:
                weight = self.user.athleteprofile.weight_kg
        except:
            pass

        # MET mapping
        met_map = {
            'low': 4,
            'moderate': 7,
            'high': 10,
        }

        met = met_map.get(self.intensity, 7)

        duration_hours = (self.duration_minutes or 0) / 60

        self.calories_burned = round(met * weight * duration_hours, 2)

        super().save(*args, **kwargs)

    # ==========================
    # Training Load Property
    # ==========================

    @property
    def training_load(self):
        return (self.duration_minutes or 0) * (self.rpe or 0)

    def __str__(self):
        return f"{self.user.username} - {self.discipline} ({self.date})"


# =====================================
# Event Specific Performance Tracking
# =====================================

class RunnerSession(models.Model):
    session = models.OneToOneField(
        TrainingSession,
        on_delete=models.CASCADE
    )
    distance_m = models.FloatField(help_text="Distance in meters")
    time_seconds = models.FloatField(help_text="Time in seconds")
    repetitions = models.IntegerField(default=1)

    def __str__(self):
        return f"Runner Data - {self.session}"


class JumperSession(models.Model):
    session = models.OneToOneField(
        TrainingSession,
        on_delete=models.CASCADE
    )
    attempts = models.IntegerField(default=1)
    best_jump_m = models.FloatField(help_text="Best result in meters")

    def __str__(self):
        return f"Jumper Data - {self.session}"


class ThrowerSession(models.Model):
    session = models.OneToOneField(
        TrainingSession,
        on_delete=models.CASCADE
    )
    implement_weight_kg = models.FloatField(help_text="Weight of implement in kg")
    attempts = models.IntegerField(default=1)
    best_throw_m = models.FloatField(help_text="Best result in meters")

    def __str__(self):
        return f"Thrower Data - {self.session}"