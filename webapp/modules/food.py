# webapp/modules/food.py
import os
import sqlite3
import requests
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Request, Form
from sqlalchemy import func
from database.db import SessionLocal, FoodEntry

router = APIRouter(prefix="/food", tags=["🍽 Питание"])

# 🔹 Путь к локальной базе продуктов
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH_LOCAL = os.path.join(BASE_DIR, "db.sqlite3")  # локальная база с продуктами

# 🔹 API ключ USDA
FOOD_API_KEY = "EAeIl0Ps1W13f5F0tAoZRW15654oQnneS3rQ6Asw"


# ==============================
# 🔍 Перевод для поиска
# ==============================
def translate(text: str, langpair: str = "ru|en") -> str:
    try:
        url = "https://api.mymemory.translated.net/get"
        resp = requests.get(url, params={"q": text, "langpair": langpair}, timeout=5)
        if resp.status_code == 200:
            return resp.json()["responseData"]["translatedText"]
    except Exception as e:
        print("Ошибка перевода:", e)
    return text


# ==============================
# 🔍 Поиск продукта (локально + API с записью)
# ==============================
@router.get("/search")
async def search_food(query: str):
    from .food_search import search_food_logic
    return search_food_logic(query)

# ==============================
# 🍏 Детали продукта
# ==============================
@router.get("/details")
async def food_details(fdc_id: int = None, name: str = None):
    conn = sqlite3.connect(DB_PATH_LOCAL)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        if fdc_id:
            cur.execute("""
                SELECT name_en, name_ru, calories, protein, fat, carbs
                FROM local_foods
                WHERE fdc_id=?
            """, (fdc_id,))
        elif name:
            cur.execute("""
                SELECT name_en, name_ru, calories, protein, fat, carbs
                FROM local_foods
                WHERE LOWER(name_en)=? OR LOWER(name_ru)=?
            """, (name.lower(), name.lower()))
        else:
            return {"error": True, "message": "Не указан продукт"}

        row = cur.fetchone()
        conn.close()
        if not row:
            return {"error": True, "message": "Нет данных"}
        return {
            "name": row["name_ru"] or row["name_en"],
            "per_1g": {
                "calories": float(row["calories"] or 0),
                "protein": float(row["protein"] or 0),
                "fat": float(row["fat"] or 0),
                "carbs": float(row["carbs"] or 0),
            }
        }
    except Exception as e:
        conn.close()
        return {"error": True, "message": str(e)}


# ==============================
# 💾 Сохранение выбранного продукта пользователем
# ==============================
@router.post("/save")
async def save_food(request: Request):
    form = await request.form()
    db = SessionLocal()
    entry = FoodEntry(
        fdc_id=int(form.get("fdc_id", 0)),
        name=form.get("name"),
        weight=float(form.get("weight", 0)),
        meal_type=form.get("meal_type", "другое"),
        calories=float(form.get("calories", 0)),
        proteins=float(form.get("proteins", 0)),
        fats=float(form.get("fats", 0)),
        carbs=float(form.get("carbs", 0)),
        created_at=datetime.now()
    )
    db.add(entry)
    db.commit()
    db.close()
    return {"status": "ok"}


# ==============================
# 📋 Получение продуктов за сегодня
# ==============================
@router.get("/today")
async def get_today_foods():
    db = SessionLocal()
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = today_start + timedelta(days=1)
    foods = db.query(FoodEntry).filter(
        FoodEntry.created_at >= today_start,
        FoodEntry.created_at < today_end
    ).all()
    db.close()
    return [f.__dict__ for f in foods]


# ==============================
# ✏️ РЕДАКТИРОВАНИЕ ПРОДУКТА (пересчёт из базы)
# ==============================
@router.post("/edit")
async def edit_food(request: Request):
    import traceback
    form = await request.form()
    food_id = int(form.get("id"))
    new_weight = float(form.get("weight", 0))

    db = SessionLocal()
    entry = db.query(FoodEntry).filter(FoodEntry.id == food_id).first()
    if not entry:
        db.close()
        return {"error": True, "message": "Продукт не найден"}

    try:
        conn = sqlite3.connect(DB_PATH_LOCAL)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""
            SELECT calories, protein, fat, carbs
            FROM local_foods
            WHERE fdc_id = ?
        """, (entry.fdc_id,))
        row = cur.fetchone()

        conn.close()

        if not row:
            db.close()
            return {"error": True, "message": f"'{entry.name}' не найден в локальной базе"}

        cal_per_g = float(row["calories"] or 0)
        prot_per_g = float(row["protein"] or 0)
        fat_per_g = float(row["fat"] or 0)
        carb_per_g = float(row["carbs"] or 0)

        entry.weight = new_weight
        entry.calories = cal_per_g * new_weight
        entry.proteins = prot_per_g * new_weight
        entry.fats = fat_per_g * new_weight
        entry.carbs = carb_per_g * new_weight

        db.commit()

        updated_data = {
            "status": "ok",
            "calories": entry.calories,
            "proteins": entry.proteins,
            "fats": entry.fats,
            "carbs": entry.carbs
        }

        db.close()
        return updated_data

    except Exception as e:
        db.close()
        print("❌ Ошибка при редактировании:", e)
        traceback.print_exc()
        return {"error": True, "message": f"Ошибка сервера: {str(e)}"}


# ==============================
# 🗑 УДАЛЕНИЕ ПРОДУКТА
# ==============================
@router.post("/delete")
async def delete_food(request: Request):
    form = await request.form()
    food_id = int(form.get("id"))

    db = SessionLocal()
    entry = db.query(FoodEntry).filter(FoodEntry.id == food_id).first()
    if not entry:
        db.close()
        return {"error": True, "message": "Продукт не найден"}

    db.delete(entry)
    db.commit()
    db.close()
    return {"status": "deleted"}
