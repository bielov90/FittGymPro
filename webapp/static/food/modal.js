// ===============================
// 🪟 МОДАЛЬНОЕ ОКНО
// ===============================

export let selectedFood = null;

export function openFoodModal() {
  document.getElementById("food-modal").classList.add("open");
}

export function closeFoodModal() {
  document.getElementById("food-modal").classList.remove("open");
  document.getElementById("food-name").value = "";
  document.getElementById("food-weight").value = "";
  document.getElementById("calories").textContent = "";
  document.getElementById("proteins").textContent = "";
  document.getElementById("fats").textContent = "";
  document.getElementById("carbs").textContent = "";
  selectedFood = null;
}
