import { selectedFood } from "./modal.js";

// ===============================
// 🔍 ПОИСК ПРОДУКТА
// ===============================

export async function searchFood(query) {
  if (!query) return [];

  const resp = await fetch(`/food/search?query=${encodeURIComponent(query)}`);
  const data = await resp.json();
  return data.results || [];
}

// ===============================
// ✅ ВЫБОР ПРОДУКТА
// ===============================

export function selectFood(item) {
  document.getElementById("food-name").value = item.name_ru;
  document.getElementById("calories").textContent = item.calories;
  document.getElementById("proteins").textContent = item.protein;
  document.getElementById("fats").textContent = item.fat;
  document.getElementById("carbs").textContent = item.carbs;

  // сохраняем fdc_id для последующего сохранения
  selectedFood = item;
}
