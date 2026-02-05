from fastapi import APIRouter

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/profile")
async def get_profile():
    return {"user_id": 123, "username": "testathlete", "role": "athlete"}

@router.put("/profile")
async def update_profile(data: dict):
    return {"message": "Profile updated", "data": data}
