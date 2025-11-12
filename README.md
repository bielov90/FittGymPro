# 🏋️‍♂️ FittGymPro — Personal Fitness Tracker

FittGymPro is a Telegram + WebApp fitness tracker built with **FastAPI**, **SQLite**, and **modular JS** frontend.  
Track your meals, workouts, water balance, and daily stats — all in one minimal interface.

---

## 🚀 Version 2.0 (November 2025)

### 🔧 What’s New
- Rebuilt into a **modular architecture**:
  - `food`, `water`, `workouts`, `profile`, `stats` modules separated
- Local food DB (`db.sqlite3`) integrated with **USDA API fallback**
- Added **auto-translation** (RU ⇄ EN) for food names
- Mini-cards for added foods now include `fdc_id` reference
- Fixed Kcal recalculation on edit
- Improved DB migration and duplicate prevention

### 🧠 Tech Stack
- **Backend:** FastAPI + SQLAlchemy + SQLite
- **Frontend:** Vanilla JS + Fetch API + minimal HTML/CSS
- **API:** USDA FoodData Central + MyMemory Translation

---

## 🧩 Modules
| Module | Purpose |
|---------|----------|
| `food.py` | Add, edit, and track foods |
| `water.py` | Track daily water intake |
| `workouts.py` | Log exercises |
| `stats.py` | Display statistics |
| `profile.py` | Manage user profile |

---

## 💡 Development
To run locally:
```bash
uvicorn main:app --reload
