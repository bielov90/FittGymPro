# webapp/main.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func
from datetime import datetime, date
from database.db import SessionLocal, UserProfile, FoodEntry, WaterEntry, WorkoutEntry

app = FastAPI()

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
        return {
            "name": user.name,
            "gender": user.gender,
            "age": user.age,
            "height": user.height,
            "weight": user.weight,
            "activity": user.activity,
            "goal": user.goal,
            "calories": user.calories,
            "water": user.water
        }
    else:
        return {"status": "empty"}


# ==============================
# 🍽 ПИТАНИЕ
# ==============================
@app.post("/add_food")
async def add_food(
    name: str = Form(...),
    weight: float = Form(...),
    calories: float = Form(...),
    proteins: float = Form(...),
    fats: float = Form(...),
    carbs: float = Form(...),
    meal_type: str = Form(...)
):
    db = SessionLocal()
    entry = FoodEntry(
        name=name,
        weight=weight,
        calories=calories,
        proteins=proteins,
        fats=fats,
        carbs=carbs,
        meal_type=meal_type
    )
    db.add(entry)
    db.commit()
    db.close()
    return {"status": "ok"}


@app.get("/get_food")
async def get_food():
    db = SessionLocal()
    items = db.query(FoodEntry).all()
    db.close()
    return JSONResponse(content=[
        {
            "name": f.name,
            "weight": f.weight,
            "calories": f.calories,
            "proteins": f.proteins,
            "fats": f.fats,
            "carbs": f.carbs,
            "meal_type": f.meal_type,
            "created_at": f.created_at
        }
        for f in items
    ])


# ==============================
# 💧 ВОДА
# ==============================
@app.post("/add_water")
async def add_water(request: Request):
    form = await request.form()
    amount = float(form.get("amount", 0))
    db = SessionLocal()
    entry = WaterEntry(amount=amount)
    db.add(entry)
    db.commit()
    db.close()
    return {"status": "ok"}


@app.get("/get_water")
async def get_water():
    db = SessionLocal()
    today = date.today().strftime("%Y-%m-%d")
    total = db.query(func.sum(WaterEntry.amount)).filter(WaterEntry.created_at.like(f"{today}%")).scalar()
    db.close()
    return {"total": round(total or 0, 1)}


# ==============================
# 🏋️ ТРЕНИРОВКИ
# ==============================
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
    db.refresh(entry)
    db.close()
    return {"status": "ok"}


@app.get("/get_workouts")
async def get_workouts():
    db = SessionLocal()
    today = date.today().strftime("%Y-%m-%d")
    workouts = db.query(WorkoutEntry).filter(
        func.strftime("%Y-%m-%d", WorkoutEntry.created_at) == today
    ).all()
    db.close()
    return workouts


# ==============================
# 📊 СТАТИСТИКА
# ==============================
@app.get("/get_stats")
async def get_stats():
    try:
        db = SessionLocal()
        today = date.today().strftime("%Y-%m-%d")

        # 🍽 Питание
        food_stats = db.query(
            func.sum(FoodEntry.calories),
            func.sum(FoodEntry.proteins),
            func.sum(FoodEntry.fats),
            func.sum(FoodEntry.carbs)
        ).filter(func.strftime("%Y-%m-%d", FoodEntry.created_at) == today).first() or (0, 0, 0, 0)

        # 💧 Вода
        water_total = db.query(func.sum(WaterEntry.amount)).filter(
            func.strftime("%Y-%m-%d", WaterEntry.created_at) == today
        ).scalar() or 0

        # 🏋️ Тренировки
        workout_total = db.query(func.sum(WorkoutEntry.calories)).filter(
            func.strftime("%Y-%m-%d", WorkoutEntry.created_at) == today
        ).scalar() or 0

        # 👤 Профиль
        profile = db.query(UserProfile).first()
        db.close()

        # Расчёты
        calories = round(food_stats[0] or 0, 1)
        proteins = round(food_stats[1] or 0, 1)
        fats = round(food_stats[2] or 0, 1)
        carbs = round(food_stats[3] or 0, 1)
        water_liters = round(water_total / 1000, 2)
        workout_kcal = round(workout_total or 0, 1)

        water_goal = round((profile.water / 1000), 1) if profile else 2.0
        kcal_goal = round(profile.calories) if profile else 2000

        return {
            "today_kcal": calories,
            "today_proteins": proteins,
            "today_fats": fats,
            "today_carbs": carbs,
            "goal_kcal": kcal_goal,
            "goal_water": water_goal,
            "today_water": water_liters,
            "workout_kcal": workout_kcal
        }

    except Exception as e:
        print("❌ ERROR in /get_stats:", e)
        return {"error": str(e)}


# ==============================
# 🌐 СТАТИКА + ГЛАВНАЯ СТРАНИЦА
# ==============================
app.mount("/static", StaticFiles(directory="webapp/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("webapp/static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())
