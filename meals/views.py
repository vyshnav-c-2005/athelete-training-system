from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import NutritionLog, FoodItem, NutritionItem

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
            
            # 2. Nutrition Items Logic
            import json
            items_json = request.POST.get('items_json', '[]')
            items_data = json.loads(items_json)

            # Initialize totals
            total_carbs = 0.0
            total_protein = 0.0
            total_fats = 0.0
            
            # Create Log first
            log = NutritionLog.objects.create(
                user=request.user,
                date=date,
                day_type=day_type,
                meal_type=meal_type,
                timing=timing,
                # Set totals to 0 initially, will update after processing items
                carbohydrates_g=0,
                protein_g=0,
                fats_g=0,
                hydration_liters=hydration,
                notes=notes
            )

            # Process items
            for item in items_data:
                food_id = item.get('id')
                qty_val = float(item.get('qty', 0))
                
                if food_id and qty_val > 0:
                    food_obj = FoodItem.objects.get(id=food_id)
                    ratio = qty_val / 100.0
                    
                    item_carbs = round(food_obj.carbs_per_100g * ratio, 1)
                    item_protein = round(food_obj.protein_per_100g * ratio, 1)
                    item_fats = round(food_obj.fats_per_100g * ratio, 1)
                    
                    NutritionItem.objects.create(
                        nutrition_log=log,
                        food_item=food_obj,
                        quantity_g=qty_val,
                        carbohydrates_g=item_carbs,
                        protein_g=item_protein,
                        fats_g=item_fats
                    )
                    
                    total_carbs += item_carbs
                    total_protein += item_protein
                    total_fats += item_fats
            
            # If manual entry was also allowed, we might check for manual specific fields, 
            # but per requirements we are moving to multi-item. 
            # If user entered manual macros without food items, we should handle that? 
            # The prompt says: "Allow multiple food items... click Add Food...". it doesn't strictly say remove manual.
            # However, for simplicity and goal "NutritionLog stores... Total macros... computed as SUM", 
            # let's assume if they want manual they might need a "Manual Food" item or just rely on items.
            # But let's check correctly if we also want to allow manual overrides or additions.
            # Seeing the new UI requirement "Table/List", manual override purely by text might be ambiguous.
            # Let's trust the "Totals computed as SUM of its items" requirement.
            
            # Update log totals
            log.carbohydrates_g = round(total_carbs, 1)
            log.protein_g = round(total_protein, 1)
            log.fats_g = round(total_fats, 1)
            log.save()

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
