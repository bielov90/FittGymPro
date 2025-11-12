// webapp/static/food_api.js (новая версия для модульной структуры)

let foodData = null;
let selectedFoodId = null;

// ===============================
// 🎯 МОДАЛЬНОЕ ОКНО
// ===============================
function openFoodModal() {
  document.getElementById("foodModal").classList.remove("hidden");
  document.body.style.overflow = "hidden";
}

function closeFoodModal() {
  document.getElementById("foodModal").classList.add("hidden");
  document.body.style.overflow = "auto";
  document.getElementById("food-name").value = "";
  document.getElementById("food-weight").value = "";
  document.getElementById("food-options").innerHTML = "";
  document.getElementById("food-status").textContent = "";
  document.getElementById("save-status").textContent = "";
  document.getElementById("calories").textContent = "-";
  document.getElementById("proteins").textContent = "-";
  document.getElementById("fats").textContent = "-";
  document.getElementById("carbs").textContent = "-";
  foodData = null;
  selectedFoodId = null;
}

// ===============================
// 🔍 ПОИСК СПИСКА ПРОДУКТОВ (ШАГ 1)
// ===============================
async function fetchFoodOptions(name) {
  const status = document.getElementById("food-status");
  const optionsBox = document.getElementById("food-options");
  status.textContent = "⏳ Поиск...";
  optionsBox.innerHTML = "";

  try {
    const res = await fetch(`/food/search?query=${encodeURIComponent(name)}`);
    const data = await res.json();

    if (data.error || !data.results?.length) {
      status.textContent = "❌ Продукт не найден";
      return;
    }

    status.textContent = "Выберите продукт:";
    optionsBox.innerHTML = data.results
      .map(
        (item) => `
        <button class="block w-full text-left px-3 py-2 border-b hover:bg-gray-50 transition"
                onclick="selectFood(${item.id || item.fdc_id}, '${item.name_ru.replace(/'/g, "\\'")}')">
          <span class="font-semibold">${item.name_ru}</span>
          <span class="text-xs text-gray-500 ml-1">(${item.name_en})</span>
        </button>`
      )
      .join("");
    optionsBox.classList.remove("hidden");
  } catch (err) {
    console.error("Ошибка при поиске:", err);
    status.textContent = "⚠️ Ошибка загрузки";
  }
}

// ===============================
// ✅ ВЫБОР ПРОДУКТА (ШАГ 2)
// ===============================
async function selectFood(id, name) {
  selectedFoodId = id;
  const status = document.getElementById("food-status");
  const optionsBox = document.getElementById("food-options");
  status.textContent = "⏳ Загрузка данных...";
  optionsBox.innerHTML = "";

  try {
    const res = await fetch(`/food/details?fdc_id=${id}`);
    const data = await res.json();

    if (data.error) {
      status.textContent = "❌ Ошибка загрузки данных";
      return;
    }

    // Поддержка формата (per_1g) и простых значений
    foodData = data.per_1g || data;
    foodData.fdc_id = id;

    document.getElementById("food-name").value = name;
    status.textContent = "✅ Данные загружены";
  } catch (err) {
    console.error("Ошибка при получении деталей:", err);
    status.textContent = "⚠️ Ошибка сети";
  }
}

// задержка при вводе
let typingTimer;
document.getElementById("food-name").addEventListener("input", (e) => {
  clearTimeout(typingTimer);
  const value = e.target.value.trim();
  if (value.length < 2) return;
  typingTimer = setTimeout(() => fetchFoodOptions(value), 600);
});

// ===============================
// 🔢 ПЕРЕСЧЁТ КБЖУ
// ===============================
function updateNutrients() {
  if (!foodData) return;
  const grams = parseFloat(document.getElementById("food-weight").value);
  if (isNaN(grams) || grams <= 0) return;

  document.getElementById("calories").textContent = (foodData.calories * grams).toFixed(1);
  document.getElementById("proteins").textContent = (foodData.protein * grams).toFixed(2);
  document.getElementById("fats").textContent = (foodData.fat * grams).toFixed(2);
  document.getElementById("carbs").textContent = (foodData.carbs * grams).toFixed(2);
}
document.getElementById("food-weight").addEventListener("input", updateNutrients);

// ===============================
// 💾 СОХРАНЕНИЕ ПРОДУКТА
// ===============================
async function saveFood() {
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
  formData.append("fdc_id", foodData?.fdc_id || 0);

  try {
    const resp = await fetch("/food/save", { method: "POST", body: formData });
    const data = await resp.json();

    if (data.status === "ok") {
      status.textContent = "✅ Сохранено";
      setTimeout(() => {
        closeFoodModal();
        loadFoodList();
        if (typeof loadStats === "function") loadStats();
      }, 600);
    } else {
      status.textContent = "❌ Ошибка сохранения";
    }
  } catch (err) {
    console.error("Ошибка сохранения:", err);
    status.textContent = "❌ Ошибка сервера";
  }
}

// ===============================
// 📋 СПИСОК ПРОДУКТОВ (с редактированием и удалением)
// ===============================
async function loadFoodList() {
  const list = document.getElementById("food-list");
  list.innerHTML = `<p class="text-gray-500">⏳ Загрузка...</p>`;

  try {
    const res = await fetch("/food/today");
    const foods = await res.json();

    if (!foods.length) {
      list.innerHTML = `<p class="text-gray-400">Пока ничего не добавлено</p>`;
      return;
    }

    list.innerHTML = foods.map(
      (f) => `
      <div class="food-item bg-white rounded-xl shadow-sm border border-gray-100 p-3 mb-2 hover:shadow-md transition" data-id="${f.id}">
        <div class="flex justify-between items-center">
          <div class="text-left">
            <p class="font-semibold text-gray-800">${f.name}</p>
            <p class="text-xs text-gray-500">${f.meal_type || "перекус"}</p>
          </div>
          <div class="flex gap-2">
            <button class="text-blue-600 hover:text-blue-800 text-sm" onclick="editFood(${f.id})">✏️</button>
            <button class="text-red-600 hover:text-red-800 text-sm" onclick="deleteFood(${f.id})">🗑</button>
          </div>
        </div>
        <div class="text-sm mt-1 text-gray-700">
          <span class="text-red-600 font-semibold">К: ${Math.round(f.calories || 0)}</span>
          <span class="text-green-600 ml-2">Б: ${Number(f.proteins || 0).toFixed(1)}г</span>
          <span class="text-yellow-600 ml-2">Ж: ${Number(f.fats || 0).toFixed(1)}г</span>
          <span class="text-blue-600 ml-2">У: ${Number(f.carbs || 0).toFixed(1)}г</span>
          <span class="text-gray-400 ml-2">(${Number(f.weight || 0)}г)</span>
        </div>
      </div>`
    ).join("");


  } catch (err) {
    console.error("Ошибка загрузки списка:", err);
    list.innerHTML = `<p class="text-red-500">Ошибка загрузки</p>`;
  }
}
// ===============================
// ✏️ РЕДАКТИРОВАНИЕ ПРОДУКТА (с пересчётом из базы)
// ===============================
async function editFood(id) {
  const grams = prompt("Введите новый вес (в граммах):", "");
  if (!grams || isNaN(grams) || grams <= 0) return;

  const formData = new FormData();
  formData.append("id", id);
  formData.append("weight", grams);

  try {
    const res = await fetch("/food/edit", { method: "POST", body: formData });
    const data = await res.json();

    if (data.status === "ok") {
      await loadFoodList();
      if (typeof loadStats === "function") loadStats();
    } else {
      alert(data.message || "Ошибка пересчёта продукта");
    }
  } catch (err) {
    console.error("Ошибка редактирования:", err);
    alert("⚠️ Ошибка соединения при редактировании");
  }
}


// ===============================
// 🗑 УДАЛЕНИЕ ПРОДУКТА
// ===============================
async function deleteFood(id) {
  if (!confirm("Удалить этот продукт?")) return;

  const formData = new FormData();
  formData.append("id", id);

  try {
    const res = await fetch("/food/delete", { method: "POST", body: formData });
    const data = await res.json();

    if (data.status === "deleted") {
      document.querySelector(`.food-item[data-id="${id}"]`)?.remove();
      if (typeof loadStats === "function") loadStats();
    } else {
      alert("Ошибка удаления");
    }
  } catch (err) {
    console.error("Ошибка удаления:", err);
    alert("Ошибка соединения");
  }
}

// ===============================
// 🚀 ПЕРВОНАЧАЛЬНАЯ ЗАГРУЗКА
// ===============================
document.addEventListener("DOMContentLoaded", () => {
  const list = document.getElementById("food-list");
  if (list) loadFoodList();
});
