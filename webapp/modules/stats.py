# webapp/modules/stats.py
from fastapi import APIRouter
from datetime import datetime, date, timedelta
from sqlalchemy import func
from database.db import SessionLocal, FoodEntry, WaterEntry, WorkoutEntry, UserProfile

router = APIRouter(prefix="/stats", tags=["📊 Статистика"])

@router.get("/today")
async def get_stats():
    db = SessionLocal()
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = today_start + timedelta(days=1)

    # 🍽 Питание
    food = db.query(
        func.sum(FoodEntry.calories),
        func.sum(FoodEntry.proteins),
        func.sum(FoodEntry.fats),
        func.sum(FoodEntry.carbs)
    ).filter(
        FoodEntry.created_at >= today_start,
        FoodEntry.created_at < today_end
    ).first()

    # 💧 Вода
    water_total = db.query(func.sum(WaterEntry.amount)).filter(
        WaterEntry.created_at >= today_start,
        WaterEntry.created_at < today_end
    ).scalar() or 0

    # 🏋️ Тренировки
    workout_total = db.query(func.sum(WorkoutEntry.calories)).filter(
        WorkoutEntry.created_at >= today_start,
        WorkoutEntry.created_at < today_end
    ).scalar() or 0

    # ⚙️ Профиль
    profile = db.query(UserProfile).first()
    db.close()

    return {
        "today_kcal": round(food[0] or 0, 1),
        "today_proteins": round(food[1] or 0, 1),
        "today_fats": round(food[2] or 0, 1),
        "today_carbs": round(food[3] or 0, 1),
        "goal_kcal": round(profile.calories if profile else 2000, 1),
        "today_water": round(water_total / 1000, 2),
        "goal_water": round((profile.water / 1000) if profile else 2.0, 1),
        "workout_kcal": round(workout_total, 1)
    }
