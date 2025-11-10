from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

engine = create_engine("sqlite:///database/fittgympro.db", connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ---- Модели ----

class UserProfile(Base):
    __tablename__ = "user_profile"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    gender = Column(String)
    age = Column(Integer)
    height = Column(Float)
    weight = Column(Float)
    activity = Column(String)
    goal = Column(String)
    calories = Column(Float)
    water = Column(Float)

class FoodEntry(Base):
    __tablename__ = "food_entries"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    weight = Column(Float)
    calories = Column(Float)
    proteins = Column(Float)
    fats = Column(Float)
    carbs = Column(Float)
    meal_type = Column(String)
    created_at = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

class WaterEntry(Base):
    __tablename__ = "water_entries"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    created_at = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

class WorkoutEntry(Base):
    __tablename__ = "workout_entries"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    duration = Column(Integer)
    calories = Column(Float)
    created_at = Column(DateTime, default=datetime.now)

# ---- Создаём все таблицы ----
Base.metadata.create_all(bind=engine)
