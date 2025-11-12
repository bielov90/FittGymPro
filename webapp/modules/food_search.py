import os
import sqlite3
import requests
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH_LOCAL = os.path.join(BASE_DIR, "db.sqlite3")
FOOD_API_KEY = "EAeIl0Ps1W13f5F0tAoZRW15654oQnneS3rQ6Asw"

# ----------------------------------------------------
# 🌍 Перевод (MyMemory)
# ----------------------------------------------------
def translate(text: str, langpair: str = "ru|en") -> str:
    try:
        url = "https://api.mymemory.translated.net/get"
        resp = requests.get(url, params={"q": text, "langpair": langpair}, timeout=5)
        if resp.status_code == 200:
            return resp.json()["responseData"]["translatedText"]
    except Exception as e:
        print("Ошибка перевода:", e)
    return text


# ----------------------------------------------------
# 🧩 Безопасная миграция структуры таблицы
# ----------------------------------------------------
def ensure_food_table_structure():
    """Создаёт таблицу local_foods и при необходимости делает миграцию с UNIQUE(fdc_id)."""
    try:
        conn_mig = sqlite3.connect(DB_PATH_LOCAL, timeout=10)
        cur = conn_mig.cursor()
        # создаём таблицу, если её нет
        cur.execute("""
            CREATE TABLE IF NOT EXISTS local_foods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fdc_id INTEGER UNIQUE,
                category TEXT,
                name_en TEXT,
                name_ru TEXT,
                calories REAL,
                protein REAL,
                fat REAL,
                carbs REAL
            )
        """)
        # проверяем уникальность fdc_id
        cur.execute("PRAGMA index_list(local_foods);")
        indexes = cur.fetchall()
        unique_exists = any("unique" in str(i).lower() for i in indexes)
        if not unique_exists:
            print("⚙️ Выполняется миграция схемы local_foods...")
            try:
                cur.execute("ALTER TABLE local_foods RENAME TO local_foods_old;")
                cur.execute("""
                    CREATE TABLE local_foods (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fdc_id INTEGER UNIQUE,
                        category TEXT,
                        name_en TEXT,
                        name_ru TEXT,
                        calories REAL,
                        protein REAL,
                        fat REAL,
                        carbs REAL
                    );
                """)
                cur.execute("""
                    INSERT OR IGNORE INTO local_foods
                    (fdc_id, category, name_en, name_ru, calories, protein, fat, carbs)
                    SELECT fdc_id, category, name_en, name_ru, calories, protein, fat, carbs
                    FROM local_foods_old
                    GROUP BY fdc_id;
                """)
                cur.execute("DROP TABLE IF EXISTS local_foods_old;")
                conn_mig.commit()
                print("✅ Миграция завершена успешно.")
            except Exception as e:
                print("⚠️ Ошибка при миграции local_foods:", e)
        conn_mig.close()
    except sqlite3.OperationalError as e:
        print("⚠️ База занята, пропускаем миграцию:", e)
    except Exception as e:
        print("❌ Ошибка ensure_food_table_structure:", e)


# ----------------------------------------------------
# 🔍 Основная логика поиска
# ----------------------------------------------------
def search_food_logic(query: str):
    ensure_food_table_structure()  # вызываем отдельно

    q = query.strip().lower()
    conn = sqlite3.connect(DB_PATH_LOCAL, timeout=10)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # -------------------------------
    # 1️⃣ Локальный поиск по частям (русские слова тоже учитываются)
    # -------------------------------
    parts = [p.strip().lower() for p in query.replace(",", " ").replace("-", " ").split() if p.strip()]

    cur.execute("""
        SELECT fdc_id, name_en, name_ru, category, calories, protein, fat, carbs
        FROM local_foods
        LIMIT 5000
    """)
    rows_all = [dict(r) for r in cur.fetchall()]

    found = []
    for row in rows_all:
        text = f"{row['name_en']} {row['name_ru']}".lower().replace(",", " ").replace("-", " ")
        if all(p in text for p in parts):
            found.append(row)

    if found:
        conn.close()
        print(f"✅ Найдено локально: {len(found)} записей для '{query}'")
        return {"results": found[:10], "source": "local"}

    # -------------------------------
    # 2️⃣ Если не найдено — запрос к API
    # -------------------------------
    translated = translate(q, "ru|en") if any("а" <= c <= "я" for c in q) else q
    print(f"🔍 '{q}' не найден локально. Поиск по API → '{translated}'")

    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {
        "api_key": FOOD_API_KEY,
        "query": translated,
        "pageSize": 10,
        "dataType": ["Survey (FNDDS)", "Foundation", "Branded"]
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        foods_json = response.json().get("foods", [])
        if not foods_json:
            conn.close()
            return {"error": True, "message": f"Продукт '{q}' не найден"}

        banned = ["acid", "extract", "study", "composition", "investigation", "analysis"]
        seen = set()
        results = []

        for f in foods_json:
            desc = f.get("description", "").strip()
            if not desc:
                continue
            desc_low = desc.lower()
            if any(b in desc_low for b in banned) or desc_low in seen:
                continue
            seen.add(desc_low)

            nutrients = f.get("foodNutrients", [])
            cal = prot = fat = carb = 0.0
            for n in nutrients:
                name = n.get("nutrientName", "").lower()
                val = n.get("value", 0.0)
                if "energy" in name:
                    cal = val / 100
                elif "protein" in name:
                    prot = val / 100
                elif "fat" in name:
                    fat = val / 100
                elif "carbohydrate" in name:
                    carb = val / 100

            ru_name = translate(desc, "en|ru")
            fdc_id = f.get("fdcId")
            category = f.get("foodCategory", "Импортировано")

            # Сохраняем с защитой от блокировки
            for attempt in range(3):
                try:
                    cur.execute("""
                        INSERT OR REPLACE INTO local_foods
                        (fdc_id, category, name_en, name_ru, calories, protein, fat, carbs)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        fdc_id, category, desc, ru_name,
                        float(cal), float(prot), float(fat), float(carb)
                    ))
                    conn.commit()
                    print(f"💾 Добавлен/обновлён: {ru_name} ({fdc_id})")
                    break
                except sqlite3.OperationalError as e:
                    if "locked" in str(e).lower() and attempt < 2:
                        print(f"⏳ База занята, повтор через 0.5 с... ({attempt+1}/3)")
                        time.sleep(0.5)
                        continue
                    else:
                        print(f"⚠️ Ошибка при сохранении {desc}: {e}")
                        break

            results.append({
                "fdc_id": fdc_id,
                "name_en": desc,
                "name_ru": ru_name,
                "category": category,
                "calories": cal,
                "protein": prot,
                "fat": fat,
                "carbs": carb
            })

        conn.close()
        print(f"✅ {len(results)} новых продуктов сохранено в локальную базу.")
        return {"results": results, "source": "api"}

    except Exception as e:
        conn.close()
        print(f"❌ Ошибка при поиске по API: {e}")
        return {"error": True, "message": str(e)}
