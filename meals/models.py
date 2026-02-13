from django.db import models
from django.contrib.auth.models import User

class FoodItem(models.Model):
    name = models.CharField(max_length=100)
    carbs_per_100g = models.FloatField(help_text="Carbs in grams per 100g")
    protein_per_100g = models.FloatField(help_text="Protein in grams per 100g")
    fats_per_100g = models.FloatField(help_text="Fats in grams per 100g")

    def __str__(self):
        return f"{self.name} (C:{self.carbs_per_100g} P:{self.protein_per_100g} F:{self.fats_per_100g})"

class NutritionLog(models.Model):
    # ... choices ...

    DAY_TYPE_CHOICES = [
        ('training', 'Training Day'),
        ('competition', 'Competition Day'),
        ('rest', 'Rest Day'),
    ]

    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]

    TIMING_CHOICES = [
        ('pre_training', 'Pre-Training'),
        ('post_training', 'Post-Training'),
        ('general', 'General'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    day_type = models.CharField(max_length=20, choices=DAY_TYPE_CHOICES)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    timing = models.CharField(max_length=20, choices=TIMING_CHOICES)
    
    # Food-based logging (Optional)
    food_item = models.ForeignKey(FoodItem, on_delete=models.SET_NULL, null=True, blank=True)
    quantity_g = models.FloatField(null=True, blank=True, help_text="Quantity in grams (if food item selected)")
    
    carbohydrates_g = models.FloatField(help_text="Carbohydrates in grams")
    protein_g = models.FloatField(help_text="Protein in grams")
    fats_g = models.FloatField(help_text="Fats in grams")
    hydration_liters = models.FloatField(help_text="Hydration in liters")
    
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.meal_type}"

class NutritionItem(models.Model):
    nutrition_log = models.ForeignKey(NutritionLog, related_name='items', on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity_g = models.FloatField(help_text="Quantity in grams")
    
    # Store calculated macros for this specific item at this time
    carbohydrates_g = models.FloatField(help_text="Carbohydrates in grams")
    protein_g = models.FloatField(help_text="Protein in grams")
    fats_g = models.FloatField(help_text="Fats in grams")

    def __str__(self):
        return f"{self.food_item.name} ({self.quantity_g}g) for Log #{self.nutrition_log.id}"
