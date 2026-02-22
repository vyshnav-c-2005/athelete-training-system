from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import NutritionLog, FoodItem, NutritionItem

@login_required
def log_nutrition(request):
    if request.method == "POST":
        try:
            # 1. Base Data
            date = request.POST.get('date')
            day_type = request.POST.get('day_type')
            meal_type = request.POST.get('meal_type')
            timing = request.POST.get('timing')
            notes = request.POST.get('notes')
            hydration = float(request.POST.get('hydration_liters') or 0)
            
            # 2. Create NutritionLog first (Dashboard filtered by user/date)
            log = NutritionLog.objects.create(
                user=request.user,
                date=date,
                day_type=day_type,
                meal_type=meal_type,
                timing=timing,
                hydration_liters=hydration,
                notes=notes,
                carbohydrates_g=0,
                protein_g=0,
                fats_g=0,
                total_calories=0
            )

            # 3. Process Multiple Items (from JSON table)
            import json
            items_json = request.POST.get('items_json', '[]')
            items_data = json.loads(items_json)

            for item in items_data:
                food_id = item.get('id')
                qty = float(item.get('qty', 0))
                
                if food_id and qty > 0:
                    food_obj = FoodItem.objects.get(id=food_id)
                    # Let NutritionItem.save() handle calculations and log update
                    NutritionItem.objects.create(
                        nutrition_log=log,
                        food_item=food_obj,
                        quantity_g=qty
                    )

            # 4. Validation/Fallback: Single item submission (if bypass JS)
            single_food_id = request.POST.get('food_item')
            single_qty = request.POST.get('quantity_g')
            
            if single_food_id and single_qty:
                qty_val = float(single_qty)
                if qty_val > 0:
                    food_obj = FoodItem.objects.get(id=single_food_id)
                    # Create if not already in JSON items (prevent duplication)
                    if not log.items.filter(food_item=food_obj, quantity_g=qty_val).exists():
                        NutritionItem.objects.create(
                            nutrition_log=log,
                            food_item=food_obj,
                            quantity_g=qty_val
                        )

            messages.success(request, "Nutrition log added successfully!")
            return redirect('nutrition_history')
        except Exception as e:
            messages.error(request, f"Error logging nutrition: {e}")
            return redirect('log_nutrition')

    return render(request, "meals/log_nutrition.html", {})

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
