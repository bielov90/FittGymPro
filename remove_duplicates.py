import sqlite3

conn = sqlite3.connect("db.sqlite3")
cur = conn.cursor()

# Находим количество записей до очистки
cur.execute("SELECT COUNT(*) FROM local_foods")
before = cur.fetchone()[0]

# Удаляем дубликаты по имени (русскому и английскому)
cur.execute("""
DELETE FROM local_foods
WHERE id NOT IN (
    SELECT MIN(id)
    FROM local_foods
    GROUP BY LOWER(TRIM(name_en)), LOWER(TRIM(name_ru))
)
""")

# Проверяем количество записей после
cur.execute("SELECT COUNT(*) FROM local_foods")
after = cur.fetchone()[0]

conn.commit()
conn.close()

print(f"🧹 Очистка завершена!")
print(f"До: {before} записей")
print(f"После: {after} записей")
print(f"Удалено: {before - after}")
