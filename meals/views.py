from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import NutritionLog, FoodItem

@login_required
def log_nutrition(request):
    foods = FoodItem.objects.all().order_by('name')
    
    if request.method == "POST":
        try:
            # 1. Base Data
            date = request.POST.get('date')
            day_type = request.POST.get('day_type')
            meal_type = request.POST.get('meal_type')
            timing = request.POST.get('timing')
            notes = request.POST.get('notes')
            hydration = float(request.POST.get('hydration_liters') or 0)
            
            # 2. Macro Logic (Auto vs Manual)
            food_id = request.POST.get('food_item')
            qty_raw = request.POST.get('quantity_g')
            
            carbs = 0.0
            protein = 0.0
            fats = 0.0
            
            selected_food = None
            quantity_g = None

            if food_id and qty_raw:
                # Auto-calculate
                selected_food = FoodItem.objects.get(id=food_id)
                quantity_g = float(qty_raw)
                ratio = quantity_g / 100.0
                
                carbs = round(selected_food.carbs_per_100g * ratio, 1)
                protein = round(selected_food.protein_per_100g * ratio, 1)
                fats = round(selected_food.fats_per_100g * ratio, 1)
            else:
                # Manual entry
                carbs = float(request.POST.get('carbohydrates_g') or 0)
                protein = float(request.POST.get('protein_g') or 0)
                fats = float(request.POST.get('fats_g') or 0)

            NutritionLog.objects.create(
                user=request.user,
                date=date,
                day_type=day_type,
                meal_type=meal_type,
                timing=timing,
                
                food_item=selected_food,
                quantity_g=quantity_g,
                
                carbohydrates_g=carbs,
                protein_g=protein,
                fats_g=fats,
                hydration_liters=hydration,
                notes=notes
            )
            messages.success(request, "Nutrition log added successfully!")
            return redirect('nutrition_history')
        except Exception as e:
            messages.error(request, f"Error logging nutrition: {e}")
            # In production, pass data back to form
            return redirect('log_nutrition')

    return render(request, "meals/log_nutrition.html", {}) # Removed 'foods' to prevent loading all items

def search_foods(request):
    """
    AJAX search endpoint for foods.
    Returns JSON list of matching foods.
    """
    query = request.GET.get('q', '').strip()
    
    # 1. Common Foods for empty query
    if not query:
        common_names = ["Rice", "Banana", "Egg", "Milk", "Chicken Breast", "Apple", "Bread", "Oats"]
        # Use name__in to preserve ordering roughly or just fetch
        foods = FoodItem.objects.filter(name__in=common_names)[:15]
        
    # 2. Single Character -> Starts With
    elif len(query) == 1:
        foods = FoodItem.objects.filter(name__istartswith=query)[:15]
        
    # 3. Multiple Characters -> Contains
    else:
        foods = FoodItem.objects.filter(name__icontains=query)[:20]

    results = [
        {
            'id': food.id,
            'name': food.name,
            'carbs': food.carbs_per_100g,
            'protein': food.protein_per_100g,
            'fats': food.fats_per_100g
        }
        for food in foods
    ]
    return JsonResponse(results, safe=False)


@login_required
def nutrition_history(request):
    logs = NutritionLog.objects.filter(user=request.user)
    return render(request, "meals/nutrition_list.html", {'logs': logs})
