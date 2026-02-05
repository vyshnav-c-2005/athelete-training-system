from fastapi import APIRouter

router = APIRouter(
    prefix="/nutrition",
    tags=["nutrition"]
)

@router.post("/log")
async def log_meal(meal_data: dict):
    return {"message": "Meal logged successfully", "meal_id": 555}

@router.get("/plans")
async def get_nutrition_plans():
    return [
        {"plan_id": 101, "name": "High Protein Cutting", "calories": 2200},
        {"plan_id": 102, "name": "Clean Bulk", "calories": 3000}
    ]

@router.post("/recommend")
async def recommend_nutrition(user_stats: dict):
    # Mock AI recommendation
    return {"recommended_calories": 2500, "macros": {"protein": 200, "carbs": 250, "fat": 70}}
