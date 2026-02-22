from django.db import models
from django.contrib.auth.models import User

class FoodItem(models.Model):
    CATEGORY_CHOICES = [
        ('solid', 'Solid'),
        ('liquid', 'Liquid'),
        ('piece', 'Piece'),
    ]
    REGION_CHOICES = [
        ('global', 'Global'),
        ('kerala', 'Kerala'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='solid')
    calories_per_100g = models.FloatField(default=0)
    protein_per_100g = models.FloatField(help_text="Protein in grams per 100g")
    carbs_per_100g = models.FloatField(help_text="Carbs in grams per 100g")
    fats_per_100g = models.FloatField(help_text="Fats in grams per 100g")
    region = models.CharField(max_length=10, choices=REGION_CHOICES, default='global')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.region}) - {self.calories_per_100g} kcal"

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
    total_calories = models.FloatField(default=0, help_text="Total calories consumed")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.meal_type}"

    def update_totals(self):
        """
        Aggregate macros from all NutritionItems and calculate total calories.
        """
        from django.db.models import Sum
        totals = self.items.aggregate(
            total_carbs=Sum('carbohydrates_g'),
            total_protein=Sum('protein_g'),
            total_fats=Sum('fats_g')
        )

        self.carbohydrates_g = totals['total_carbs'] or 0
        self.protein_g = totals['total_protein'] or 0
        self.fats_g = totals['total_fats'] or 0

        self.total_calories = round(
            (self.carbohydrates_g * 4) +
            (self.protein_g * 4) +
            (self.fats_g * 9),
            2
        )

        self.save(update_fields=[
            'carbohydrates_g',
            'protein_g',
            'fats_g',
            'total_calories'
        ])

class NutritionItem(models.Model):
    nutrition_log = models.ForeignKey(NutritionLog, related_name='items', on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity_g = models.FloatField(help_text="Quantity in grams")
    
    # Store calculated macros for this specific item at this time
    carbohydrates_g = models.FloatField(help_text="Carbohydrates in grams")
    protein_g = models.FloatField(help_text="Protein in grams")
    fats_g = models.FloatField(help_text="Fats in grams")

    def save(self, *args, **kwargs):
        if self.food_item and self.quantity_g:
            factor = self.quantity_g / 100
            self.carbohydrates_g = round(
                self.food_item.carbs_per_100g * factor, 2
            )
            self.protein_g = round(
                self.food_item.protein_per_100g * factor, 2
            )
            self.fats_g = round(
                self.food_item.fats_per_100g * factor, 2
            )

        super().save(*args, **kwargs)
        # Update parent log totals
        self.nutrition_log.update_totals()

    def __str__(self):
        return f"{self.food_item.name} ({self.quantity_g}g) for Log #{self.nutrition_log.id}"
