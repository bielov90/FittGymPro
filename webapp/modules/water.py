# webapp/modules/water.py
from fastapi import APIRouter, Request, Form
from datetime import datetime, date, timedelta
from sqlalchemy import func
from database.db import SessionLocal, WaterEntry

router = APIRouter(prefix="/water", tags=["💧 Вода"])

# 💧 Добавление воды
@router.post("/add")
async def add_water(amount: float = Form(...)):
    db = SessionLocal()
    entry = WaterEntry(amount=amount, created_at=datetime.now())
    db.add(entry)
    db.commit()
    db.close()
    return {"status": "ok"}

# 📊 Получение воды за день
@router.get("/today")
async def get_water():
    db = SessionLocal()
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = today_start + timedelta(days=1)
    total = db.query(func.sum(WaterEntry.amount)).filter(
        WaterEntry.created_at >= today_start,
        WaterEntry.created_at < today_end
    ).scalar() or 0
    db.close()
    return {"total": round(total, 1)}
