// webapp/static/workout.js — обновлённый под модуль workouts.py

// 🏋️‍♂️ Добавление тренировки
async function handleWorkoutSubmit(event) {
  event.preventDefault();

  const form = event.target;
  const formData = new FormData(form);

  const type = formData.get("type")?.trim();
  const duration = parseFloat(formData.get("duration"));
  const calories = parseFloat(formData.get("calories"));
  const msg = document.getElementById("workout-result");

  // Проверка
  if (!type || isNaN(duration) || isNaN(calories) || duration <= 0 || calories <= 0) {
    msg.innerHTML = `<p class="text-red-600 font-semibold">⚠️ Заполните все поля корректно</p>`;
    return;
  }

  try {
    const response = await fetch("/workouts/add", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ type, duration, calories })
    });

    const result = await response.json();

    if (result.status === "ok") {
      msg.innerHTML = `<p class="text-green-600 font-semibold">✅ ${type} (${duration} мин, ${calories} ккал) добавлено</p>`;
      form.reset();

      // Обновляем статистику
      if (typeof loadStats === "function") loadStats();

      // Обновляем список
      await loadWorkouts();

      setTimeout(() => (msg.innerHTML = ""), 2000);
    } else {
      msg.innerHTML = `<p class="text-red-600 font-semibold">❌ Ошибка при добавлении</p>`;
    }
  } catch (err) {
    console.error("Ошибка при добавлении тренировки:", err);
    msg.innerHTML = `<p class="text-red-600 font-semibold">⚠️ Ошибка соединения</p>`;
  }
}

// 📋 Загрузка списка тренировок
async function loadWorkouts() {
  const list = document.getElementById("workout-list");
  if (!list) return;

  try {
    const response = await fetch("/workouts/today");
    const data = await response.json();

    if (!data.length) {
      list.innerHTML = "<p class='text-gray-500'>Тренировок за сегодня нет</p>";
      return;
    }

    list.innerHTML = data.map(
      (w) => `
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-3 flex justify-between items-center hover:shadow-md transition">
          <div>
            <p class="font-semibold text-gray-800">${w.type}</p>
            <p class="text-xs text-gray-500">${w.duration} мин • ${w.calories} ккал</p>
          </div>
          <span class="text-gray-400 text-sm">${new Date(w.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
        </div>
      `
    ).join("");

  } catch (err) {
    console.error("Ошибка загрузки тренировок:", err);
    list.innerHTML = "<p class='text-red-600'>⚠️ Не удалось загрузить данные</p>";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadWorkouts();
  const form = document.getElementById("workout-form");
  if (form) form.addEventListener("submit", handleWorkoutSubmit);
});
