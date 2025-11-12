// webapp/static/stats.js — обновлён под эндпоинт /stats/today

async function loadStats() {
  try {
    const res = await fetch("/stats/today");
    const data = await res.json();

    if (data.error) {
      console.error("Ошибка статистики:", data.error);
      return;
    }

    // Элементы
    const kcalValue = document.getElementById("kcal-value");
    const kcalGoal = document.getElementById("kcal-goal");
    const statBar = document.getElementById("stat-bar");
    const statProg = document.getElementById("stat-prog");
    const macroInfo = document.getElementById("macro-info");
    const waterInfo = document.getElementById("water-info");
    const workoutInfo = document.getElementById("workout-info");

    if (!kcalValue || !kcalGoal) return;

    const kcal = parseFloat(data.today_kcal || 0);
    const kcalGoalValue = parseFloat(data.goal_kcal || 2000);
    const progress = isNaN(kcal) || isNaN(kcalGoalValue)
      ? 0
      : Math.min((kcal / kcalGoalValue) * 100, 100).toFixed(1);

    kcalValue.textContent = kcal.toFixed(0);
    kcalGoal.textContent = kcalGoalValue;
    statBar.value = progress;
    statProg.textContent = `${progress}%`;

    if (macroInfo) {
      macroInfo.textContent = `Б: ${(data.today_proteins || 0).toFixed(1)} • Ж: ${(data.today_fats || 0).toFixed(1)} • У: ${(data.today_carbs || 0).toFixed(1)}`;
    }
    if (waterInfo) {
      waterInfo.textContent = `💧 Вода: ${(data.today_water || 0).toFixed(2)} л`;
    }
    if (workoutInfo) {
      workoutInfo.textContent = `🏋️ Тренировки: ${(data.workout_kcal || 0).toFixed(0)} ккал`;
    }

  } catch (err) {
    console.error("Ошибка загрузки статистики:", err);
  }
}

// 🔁 Автообновление каждые 30 секунд
setInterval(loadStats, 30000);
document.addEventListener("DOMContentLoaded", loadStats);
