import requests
import sqlite3
import time

API_KEY = "EAeIl0Ps1W13f5F0tAoZRW15654oQnneS3rQ6Asw"
BASE_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

# Тематические категории для расширенного парсинга
CATEGORIES = [
    "apple", "banana", "orange", "pear", "grape", "kiwi", "strawberry", "blueberry", "melon", "cherry",
    "potato", "carrot", "cucumber", "tomato", "cabbage", "onion", "broccoli", "garlic", "pepper",
    "rice", "buckwheat", "oats", "barley", "millet", "corn", "pasta", "bread", "flour", "pizza", "cookie",
    "beef", "pork", "chicken", "turkey", "duck", "fish", "salmon", "tuna", "shrimp", "egg",
    "milk", "cheese", "butter", "yogurt", "cream", "ice cream", "kefir",
    "water", "juice", "coffee", "tea", "beer", "wine", "cola",
    "chocolate", "cake", "honey", "jam", "nuts", "almond", "walnut", "hazelnut", "peanut"
]

conn = sqlite3.connect("db.sqlite3")
cur = conn.cursor()

def parse_food(name):
    """Парсинг одного продукта"""
    params = {
        "query": name,
        "pageSize": 5,
        "api_key": API_KEY,
    }
    try:
        r = requests.get(BASE_URL, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        foods = data.get("foods", [])
        for item in foods:
            fdc_id = item.get("fdcId")
            desc = item.get("description", "").strip()
            if not desc or len(desc) > 80:  # убираем длинные и научные описания
                continue

            # Считаем КБЖУ (берём усреднённые данные)
            nutrients = item.get("foodNutrients", [])
            kcal = protein = fat = carbs = 0.0
            for n in nutrients:
                name_nut = (n.get("nutrientName") or "").lower()
                value = float(n.get("value") or 0)
                if "energy" in name_nut and "kj" not in name_nut:
                    kcal = value
                elif "protein" in name_nut:
                    protein = value
                elif "fat" in name_nut:
                    fat = value
                elif "carbohydrate" in name_nut:
                    carbs = value

            if kcal == 0:
                continue

            # Запись в базу
            cur.execute("""
            INSERT OR IGNORE INTO local_foods (fdc_id, name_en, name_ru, category, calories, protein, fat, carbs)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fdc_id,
                desc.lower(),
                desc.lower(),  # позже добавим перевод
                name.lower(),
                round(kcal / 100, 3),
                round(protein / 100, 3),
                round(fat / 100, 3),
                round(carbs / 100, 3),
            ))
        conn.commit()
        print(f"✅ {name}: добавлено {len(foods)} записей")
    except Exception as e:
        print(f"⚠️ Ошибка при обработке {name}: {e}")

# Парсим все категории
for i, cat in enumerate(CATEGORIES, 1):
    print(f"[{i}/{len(CATEGORIES)}] Обработка: {cat}")
    parse_food(cat)
    time.sleep(1.2)  # задержка, чтобы не заблокировали API

conn.close()
print("🎯 Парсинг завершён! Все продукты записаны в local_foods.")
