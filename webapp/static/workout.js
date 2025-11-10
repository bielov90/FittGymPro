// webapp/static/workout.js
async function handleWorkoutSubmit(event) {
  event.preventDefault();

  const form = event.target;
  const formData = new FormData(form);

  const type = formData.get("type");
  const duration = formData.get("duration");
  const calories = formData.get("calories");

  const response = await fetch("/add_workout", {
    method: "POST",
    body: new URLSearchParams({
      type,
      duration,
      calories,
    }),
  });

  const result = await response.json();

  const msg = document.getElementById("workout-result");
  if (result.status === "ok") {
    msg.innerHTML = `✅ <span class="text-green-600">Добавлено:</span> ${type} (${duration} мин, ${calories} ккал)`;
    form.reset();
    // 🔄 обновляем статистику
    if (typeof loadStats === "function") loadStats();
    loadWorkouts();
  } else {
    msg.innerHTML = `❌ Ошибка при добавлении`;
  }
}

async function loadWorkouts() {
  const response = await fetch("/get_workouts");
  const data = await response.json();

  const list = document.getElementById("workout-list");
  if (!data.length) {
    list.innerHTML = "<p class='text-gray-500'>Тренировок за сегодня нет</p>";
    return;
  }

  list.innerHTML = data
    .map(
      (w) =>
        `<p class='text-sm text-gray-700'>${w.type} — ${w.duration} мин (${w.calories} ккал)</p>`
    )
    .join("");
}

document.addEventListener("DOMContentLoaded", loadWorkouts);
