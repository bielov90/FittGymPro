import { selectedFood, closeFoodModal } from "./modal.js";
import { loadFoodList } from "./list.js";

// ===============================
// 🔢 ПЕРЕСЧЁТ КБЖУ
// ===============================
export function updateNutrients() {
  const weight = parseFloat(document.getElementById("food-weight").value);
  if (!selectedFood || isNaN(weight)) return;

  const mult = weight;
  document.getElementById("calories").textContent = (selectedFood.calories * mult).toFixed(1);
  document.getElementById("proteins").textContent = (selectedFood.protein * mult).toFixed(2);
  document.getElementById("fats").textContent = (selectedFood.fat * mult).toFixed(2);
  document.getElementById("carbs").textContent = (selectedFood.carbs * mult).toFixed(2);
}

// ===============================
// 💾 СОХРАНЕНИЕ ПРОДУКТА
// ===============================
export async function saveFood() {
  const name = document.getElementById("food-name").value.trim();
  const weight = parseFloat(document.getElementById("food-weight").value);
  const mealType = document.getElementById("meal-type").value;
  const calories = parseFloat(document.getElementById("calories").textContent) || 0;
  const proteins = parseFloat(document.getElementById("proteins").textContent) || 0;
  const fats = parseFloat(document.getElementById("fats").textContent) || 0;
  const carbs = parseFloat(document.getElementById("carbs").textContent) || 0;

  const status = document.getElementById("save-status");

  if (!name || isNaN(weight) || weight <= 0) {
    status.textContent = "⚠️ Укажите продукт и вес";
    return;
  }

  status.textContent = "⏳ Сохраняем...";

  const formData = new FormData();
  formData.append("name", name);
  formData.append("weight", weight);
  formData.append("meal_type", mealType);
  formData.append("calories", calories);
  formData.append("proteins", proteins);
  formData.append("fats", fats);
  formData.append("carbs", carbs);
  formData.append("fdc_id", selectedFood?.fdc_id || 0);

  try {
    const resp = await fetch("/food/save", { method: "POST", body: formData });
    const data = await resp.json();

    if (data.status === "ok") {
      status.textContent = "✅ Сохранено";
      setTimeout(() => {
        closeFoodModal();
        loadFoodList();
      }, 600);
    } else {
      status.textContent = "❌ Ошибка сохранения";
    }
  } catch (err) {
    console.error("Ошибка сохранения:", err);
    status.textContent = "❌ Ошибка сервера";
  }
}
