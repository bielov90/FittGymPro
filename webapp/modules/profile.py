# webapp/modules/profile.py
from fastapi import APIRouter, Form
from database.db import SessionLocal, UserProfile

router = APIRouter(prefix="/profile", tags=["⚙️ Профиль"])

# 💾 Сохранение профиля
@router.post("/save")
async def save_profile(
    name: str = Form(...),
    gender: str = Form(...),
    age: int = Form(...),
    height: float = Form(...),
    weight: float = Form(...),
    activity: str = Form(...),
    goal: str = Form(...),
    calories: float = Form(...),
    water: float = Form(...)
):
    db = SessionLocal()
    user = db.query(UserProfile).first()
    if user:
        user.name = name
        user.gender = gender
        user.age = age
        user.height = height
        user.weight = weight
        user.activity = activity
        user.goal = goal
        user.calories = calories
        user.water = water
    else:
        user = UserProfile(
            name=name,
            gender=gender,
            age=age,
            height=height,
            weight=weight,
            activity=activity,
            goal=goal,
            calories=calories,
            water=water
        )
        db.add(user)
    db.commit()
    db.close()
    return {"status": "ok"}

# 📋 Получение профиля
@router.get("/get")
async def get_profile():
    db = SessionLocal()
    user = db.query(UserProfile).first()
    db.close()
    if user:
        return user.__dict__
    return {"status": "empty"}
