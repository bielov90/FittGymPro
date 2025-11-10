// webapp/static/food.js

async function handleFoodSubmit(e) {
  e.preventDefault();
  const form = e.target;
  const data = Object.fromEntries(new FormData(form));

  // простая формула: калорийность на грамм * вес
  const kcal = parseFloat(data.calories_per_100g) * parseFloat(data.weight) / 100;
  const proteins = parseFloat(data.proteins_per_100g) * parseFloat(data.weight) / 100;
  const fats = parseFloat(data.fats_per_100g) * parseFloat(data.weight) / 100;
  const carbs = parseFloat(data.carbs_per_100g) * parseFloat(data.weight) / 100;

  await fetch("/add_food", {
    method: "POST",
    body: new URLSearchParams({
      name: data.name,
      weight: data.weight,
      calories: kcal,
      proteins,
      fats,
      carbs,
      meal_type: data.meal_type
    }),
  });

  document.getElementById("food-result").innerHTML =
    `<p class='text-green-600 font-semibold'>✅ ${data.name} добавлен (${kcal.toFixed(0)} ккал)</p>`;
  // 🔄 обновляем статистику
  if (typeof loadStats === "function") loadStats();
  loadFoodList();
}

async function loadFoodList() {
  const res = await fetch("/get_food");
  const foods = await res.json();
  const list = document.getElementById("food-list");
  if (!foods.length) {
    list.innerHTML = "<p class='text-gray-500'>Нет добавленных продуктов</p>";
    return;
  }
  list.innerHTML = foods.map(f => `
    <div class="border-b py-2 text-left">
      <b>${f.name}</b> — ${f.calories.toFixed(0)} ккал (${f.weight} г)
      <div class="text-sm text-gray-500">${f.meal_type} | Б:${f.proteins.toFixed(1)} Ж:${f.fats.toFixed(1)} У:${f.carbs.toFixed(1)}</div>
    </div>
  `).join("");
}

window.addEventListener("load", loadFoodList);
