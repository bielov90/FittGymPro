# webapp/main.py
import os
import requests
import sqlite3
from datetime import datetime, date, timedelta
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func
from database.db import SessionLocal, UserProfile, FoodEntry, WaterEntry, WorkoutEntry

app = FastAPI()
FOOD_API_KEY = "EAeIl0Ps1W13f5F0tAoZRW15654oQnneS3rQ6Asw"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "db.sqlite3")

# ==============================
# 📁 ПРОФИЛЬ
# ==============================
@app.post("/save_profile")
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
            name=name, gender=gender, age=age, height=height, weight=weight,
            activity=activity, goal=goal, calories=calories, water=water
        )
        db.add(user)
    db.commit()
    db.close()
    return {"status": "ok"}

@app.get("/get_profile")
async def get_profile():
    db = SessionLocal()
    user = db.query(UserProfile).first()
    db.close()
    if user:
        return user.__dict__
    return {"status": "empty"}

# ==============================
# 🔍 ПЕРЕВОД
# ==============================
def translate(text: str, langpair: str = "ru|en") -> str:
    try:
        url = "https://api.mymemory.translated.net/get"
        resp = requests.get(url, params={"q": text, "langpair": langpair}, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("responseData", {}).get("translatedText", text).strip()
    except Exception as e:
        print("Ошибка перевода:", e)
    return text

# ==============================
# 🔍 ПОИСК В ЛОКАЛЬНОЙ БАЗЕ
# ==============================
def get_local_foods(query: str):
    q = query.strip().lower()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT fdc_id, name_en, name_ru
        FROM local_foods
        WHERE LOWER(name_ru) LIKE ? OR LOWER(name_en) LIKE ?
        LIMIT 10
    """, (f"%{q}%", f"%{q}%"))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    seen = set()
    unique = []
    for r in rows:
        name = r["name_ru"].strip().lower()
        if name not in seen:
            unique.append(r)
            seen.add(name)
    return unique

# ==============================
# 🔍 ПОИСК ПРОДУКТОВ
# ==============================
@app.get("/search_food_list")
async def search_food_list(query: str):
    query_clean = query.strip().lower()

    # 1️⃣ Проверяем локальную базу
    local_results = get_local_foods(query_clean)
    if local_results:
        return {"results": local_results, "source": "local"}

    # 2️⃣ Переводим и ищем через API
    translated_query = translate(query_clean, "ru|en") if any("а" <= c <= "я" for c in query_clean) else query_clean
    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {
        "api_key": FOOD_API_KEY,
        "query": translated_query,
        "pageSize": 10,
        "dataType": ["Survey (FNDDS)", "Foundation", "Branded"]
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        foods = resp.json().get("foods", [])
        if not foods:
            return {"error": True, "message": "Продукт не найден"}

        banned_words = [
            "acid", "composition", "study", "analysis", "identification",
            "extract", "characterization", "phenol", "amino", "marker", "determination", "investigation"
        ]

        seen, results = set(), []
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        for f in foods:
            desc = f.get("description", "").strip()
            if not desc:
                continue
            desc_lower = desc.lower()
            if len(desc) > 70 or any(w in desc_lower for w in banned_words) or desc_lower in seen:
                continue
            seen.add(desc_lower)

            nutrients = f.get("foodNutrients", [])
            cal = prot = fat = carb = 0.0
            for n in nutrients:
                n_name = n.get("nutrientName", "").lower()
                value = n.get("value", 0.0)
                if "energy" in n_name:
                    cal = value / 100
                elif "protein" in n_name:
                    prot = value / 100
                elif "fat" in n_name:
                    fat = value / 100
                elif "carbohydrate" in n_name:
                    carb = value / 100

            ru_desc = translate(desc, "en|ru")
            results.append({
                "id": f.get("fdcId"),
                "name_en": desc.capitalize(),
                "name_ru": ru_desc.capitalize()
            })

            cur.execute("""
                INSERT OR REPLACE INTO local_foods
                (fdc_id, category, name_en, name_ru, calories, protein, fat, carbs)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f.get("fdcId"),
                "Импортировано",
                desc_lower,
                ru_desc.lower(),
                cal,
                prot,
                fat,
                carb
            ))

        conn.commit()
        conn.close()
        return {"results": results[:5], "source": "usda"}

    except Exception as e:
        print("Ошибка при поиске по API:", e)
        return {"error": True, "message": str(e)}

# ==============================
# 🍏 ДЕТАЛИ ПРОДУКТА
# ==============================
@app.get("/get_food_details")
async def get_food_details(fdc_id: int = None, name: str = None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    try:
        name = name.lower().strip() if name else None

        # 🔹 Поиск по имени
        if name:
            cur.execute("""
                SELECT name_en, name_ru, calories, protein, fat, carbs, fdc_id
                FROM local_foods
                WHERE LOWER(name_en)=? OR LOWER(name_ru)=?
                LIMIT 1
            """, (name, name))
            row = cur.fetchone()
            if row:
                kcal = float(row["calories"] or 0)
                prot = float(row["protein"] or 0)
                fat = float(row["fat"] or 0)
                carb = float(row["carbs"] or 0)
                fdc = row["fdc_id"]

                if any([kcal, prot, fat, carb]):
                    conn.close()
                    return {
                        "name": row["name_ru"] or row["name_en"],
                        "per_1g": {
                            "calories": round(kcal, 4),
                            "protein": round(prot, 4),
                            "fat": round(fat, 4),
                            "carbs": round(carb, 4)
                        },
                        "per_100g": {
                            "calories": round(kcal * 100, 1),
                            "protein": round(prot * 100, 2),
                            "fat": round(fat * 100, 2),
                            "carbs": round(carb * 100, 2)
                        }
                    }

        # 🔹 Поиск по fdc_id
        if fdc_id:
            cur.execute("""
                SELECT name_en, name_ru, calories, protein, fat, carbs
                FROM local_foods
                WHERE fdc_id=?
                LIMIT 1
            """, (fdc_id,))
            row = cur.fetchone()
            if row:
                kcal = float(row["calories"] or 0)
                prot = float(row["protein"] or 0)
                fat = float(row["fat"] or 0)
                carb = float(row["carbs"] or 0)
                conn.close()
                return {
                    "name": row["name_ru"] or row["name_en"],
                    "per_1g": {
                        "calories": round(kcal, 4),
                        "protein": round(prot, 4),
                        "fat": round(fat, 4),
                        "carbs": round(carb, 4)
                    },
                    "per_100g": {
                        "calories": round(kcal * 100, 1),
                        "protein": round(prot * 100, 2),
                        "fat": round(fat * 100, 2),
                        "carbs": round(carb * 100, 2)
                    }
                }

        conn.close()
        return {"error": True, "message": "Нет данных в локальной базе"}

    except Exception as e:
        conn.close()
        print("Ошибка при получении данных:", e)
        return {"error": True, "message": str(e)}

# 💧 ВОДА, 🏋️‍♂️ ТРЕНИРОВКИ, 🍽 ПИТАНИЕ, 📊 СТАТИСТИКА — оставлены без изменений
# ==============================
# (всё ниже — как в твоей версии)
# ==============================

# 💧 ВОДА
@app.post("/add_water")
async def add_water(request: Request):
    form = await request.form()
    amount = float(form.get("amount", 0))
    db = SessionLocal()
    entry = WaterEntry(amount=amount, created_at=datetime.now())
    db.add(entry)
    db.commit()
    db.close()
    return {"status": "ok"}

@app.get("/get_water")
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

# 🏋️‍♂️ ТРЕНИРОВКИ
@app.post("/add_workout")
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

@app.get("/get_workouts")
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

# 📊 СТАТИСТИКА
@app.get("/get_stats")
async def get_stats():
    db = SessionLocal()
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = today_start + timedelta(days=1)

    food = db.query(
        func.sum(FoodEntry.calories),
        func.sum(FoodEntry.proteins),
        func.sum(FoodEntry.fats),
        func.sum(FoodEntry.carbs)
    ).filter(
        FoodEntry.created_at >= today_start,
        FoodEntry.created_at < today_end
    ).first()

    water_total = db.query(func.sum(WaterEntry.amount)).filter(
        WaterEntry.created_at >= today_start,
        WaterEntry.created_at < today_end
    ).scalar() or 0

    workout_total = db.query(func.sum(WorkoutEntry.calories)).filter(
        WorkoutEntry.created_at >= today_start,
        WorkoutEntry.created_at < today_end
    ).scalar() or 0

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

# 🍽 ПИТАНИЕ
@app.post("/save_food")
async def save_food(request: Request):
    try:
        form = await request.form()
        name = form.get("name")
        weight = float(form.get("weight", 0))
        meal_type = form.get("meal_type", "другое")
        calories = float(form.get("calories", 0))
        proteins = float(form.get("proteins", 0))
        fats = float(form.get("fats", 0))
        carbs = float(form.get("carbs", 0))

        db = SessionLocal()
        entry = FoodEntry(
            name=name,
            weight=weight,
            meal_type=meal_type,
            calories=calories,
            proteins=proteins,
            fats=fats,
            carbs=carbs,
            created_at=datetime.now()
        )
        db.add(entry)
        db.commit()
        db.close()
        return {"status": "ok"}
    except Exception as e:
        print("Ошибка сохранения:", e)
        return {"status": "error", "message": str(e)}

@app.get("/get_foods")
async def get_foods():
    try:
        db = SessionLocal()
        today_start = datetime.combine(date.today(), datetime.min.time())
        today_end = today_start + timedelta(days=1)
        foods = db.query(FoodEntry).filter(
            FoodEntry.created_at >= today_start,
            FoodEntry.created_at < today_end
        ).all()
        db.close()
        return [{
            "id": f.id,
            "name": f.name,
            "weight": f.weight,
            "meal_type": f.meal_type,
            "calories": f.calories,
            "proteins": f.proteins,
            "fats": f.fats,
            "carbs": f.carbs
        } for f in foods]
    except Exception as e:
        print("Ошибка загрузки продуктов:", e)
        return {"error": True, "message": str(e)}

# 🌐 СТАТИКА
app.mount("/static", StaticFiles(directory="webapp/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("webapp/static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())
