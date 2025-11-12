import { searchFood, selectFood } from "./search.js";
import { saveFood, updateNutrients } from "./save.js";
import { loadFoodList } from "./list.js";
import { openFoodModal, closeFoodModal } from "./modal.js";

// ===============================
// 🚀 ИНИЦИАЛИЗАЦИЯ
// ===============================
document.addEventListener("DOMContentLoaded", () => {
  loadFoodList();

  document.getElementById("add-food-btn").addEventListener("click", openFoodModal);
  document.getElementById("food-weight").addEventListener("input", updateNutrients);
  document.getElementById("save-food-btn").addEventListener("click", saveFood);
  document.getElementById("close-modal").addEventListener("click", closeFoodModal);
});
