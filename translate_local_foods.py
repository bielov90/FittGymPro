import sqlite3
import time
from deep_translator import GoogleTranslator

translator = GoogleTranslator(source="en", target="ru")

conn = sqlite3.connect("db.sqlite3")
cur = conn.cursor()

# Берём все записи
cur.execute("SELECT id, name_en FROM local_foods")
rows = cur.fetchall()

print(f"🔍 Найдено {len(rows)} записей для перевода...")

count = 0
for row in rows:
    id_, name_en = row
    try:
        translated = translator.translate(name_en)
        cur.execute("UPDATE local_foods SET name_ru=? WHERE id=?", (translated.lower(), id_))
        conn.commit()
        count += 1
        print(f"✅ {count}: {name_en} → {translated}")
        time.sleep(0.5)
    except Exception as e:
        print(f"⚠️ Ошибка перевода {name_en}: {e}")
        time.sleep(1)

conn.close()
print(f"🎯 Перевод завершён! Обновлено {count} записей.")
