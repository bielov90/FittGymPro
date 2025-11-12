# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import sys
import os

# Добавляем путь, чтобы Python видел webapp
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, "webapp"))

# Импортируем модули
from webapp.modules import food, water, workouts, stats, profile

app = FastAPI(title="FittGymPro Modular")

# Подключаем модули (роутеры)
app.include_router(food.router)
app.include_router(water.router)
app.include_router(workouts.router)
app.include_router(stats.router)
app.include_router(profile.router)

# Подключаем статику
app.mount("/static", StaticFiles(directory="webapp/static"), name="static")

# Главная страница
@app.get("/", response_class=HTMLResponse)
async def home():
    with open("webapp/static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())
