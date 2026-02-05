from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    role: str  # athlete, trainer, admin

class UserLogin(BaseModel):
    email: str
    password: str

@router.post("/register")
async def register(user: UserRegister):
    # Mock registration
    return {"message": "User registered successfully", "user_id": 123}

@router.post("/login")
async def login(user: UserLogin):
    # Mock login
    return {"access_token": "mock-jwt-token", "token_type": "bearer"}
