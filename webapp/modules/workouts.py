# webapp/modules/workouts.py
from fastapi import APIRouter, Form
from datetime import datetime, date, timedelta
from sqlalchemy import func
from database.db import SessionLocal, WorkoutEntry

router = APIRouter(prefix="/workouts", tags=["🏋️ Тренировки"])

# 🏋️‍♂️ Добавление тренировки
@router.post("/add")
async def add_workout(
    type: str = Form(...),
    duration: int = Form(...),
    calories: float = Form(...)
):
    db = SessionLocal()
    entry = WorkoutEntry(
        type=type,
        duration=duration,
        calories=calories,
        created_at=datetime.now()
    )
    db.add(entry)
    db.commit()
    db.close()
    return {"status": "ok"}

# 📋 Получение тренировок за сегодня
@router.get("/today")
async def get_workouts():
    db = SessionLocal()
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = today_start + timedelta(days=1)
    workouts = db.query(WorkoutEntry).filter(
        WorkoutEntry.created_at >= today_start,
        WorkoutEntry.created_at < today_end
    ).all()
    db.close()
    return [w.__dict__ for w in workouts]
