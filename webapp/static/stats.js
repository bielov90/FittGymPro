// webapp/static/stats.js
async function loadStats() {
  try {
    const response = await fetch("/get_stats");
    const data = await response.json();

    // Если ошибка — вывести в консоль
    if (data.error) {
      console.error("Ошибка статистики:", data.error);
      return;
    }

    // Элементы на странице
    const kcalValue = document.getElementById("kcal-value");
    const kcalGoal = document.getElementById("kcal-goal");
    const statBar = document.getElementById("stat-bar");
    const statProg = document.getElementById("stat-prog");
    const macroInfo = document.getElementById("macro-info");
    const waterInfo = document.getElementById("water-info");
    const workoutInfo = document.getElementById("workout-info");

    // Основные значения
    const kcal = data.today_kcal || 0;
    const kcalGoalValue = data.goal_kcal || 2000;
    const progress = Math.min((kcal / kcalGoalValue) * 100, 100).toFixed(1);

    kcalValue.textContent = kcal.toFixed(0);
    kcalGoal.textContent = kcalGoalValue;
    statBar.value = progress;
    statProg.textContent = `${progress}%`;

    // Макросы
    macroInfo.textContent = `Б: ${data.today_proteins || 0} • Ж: ${data.today_fats || 0} • У: ${data.today_carbs || 0}`;

    // Вода
    waterInfo.textContent = `💧 Вода: ${data.today_water?.toFixed(2) || 0} л`;

    // 🔥 Добавляем тренировки
    workoutInfo.textContent = `🏋️ Тренировки: ${data.workout_kcal?.toFixed(0) || 0} ккал`;
  } catch (e) {
    console.error("Ошибка загрузки статистики:", e);
  }
}

// Обновляем статистику при загрузке
document.addEventListener("DOMContentLoaded", loadStats);
