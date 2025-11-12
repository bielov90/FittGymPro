// webapp/static/profile.js — обновлён под эндпоинты /profile/save и /profile/get

function calcCalories(weight, height, age, gender, activity, goal) {
  let bmr;
  if (gender === "male") bmr = 88.36 + (13.4 * weight) + (4.8 * height) - (5.7 * age);
  else bmr = 447.6 + (9.2 * weight) + (3.1 * height) - (4.3 * age);

  const factors = { low: 1.2, medium: 1.55, high: 1.725 };
  let calories = bmr * (factors[activity] || 1.2);

  if (goal === "lose") calories *= 0.85;
  if (goal === "gain") calories *= 1.15;

  return Math.round(calories);
}

function calcWater(weight) {
  return weight * 30;
}

async function handleProfileSubmit(e) {
  e.preventDefault();
  const form = e.target;
  const data = Object.fromEntries(new FormData(form));

  const calories = calcCalories(
    parseFloat(data.weight), parseFloat(data.height), parseFloat(data.age),
    data.gender, data.activity, data.goal
  );
  const water = calcWater(parseFloat(data.weight));

  await fetch("/profile/save", {
    method: "POST",
    body: new URLSearchParams({ ...data, calories, water })
  });

  const result = document.getElementById("profile-result");
  result.innerHTML = `
    <p class="text-lg font-semibold text-green-600 mb-2">✅ Данные сохранены</p>
    <p>Ваша дневная норма: <b>${calories}</b> ккал и <b>${(water/1000).toFixed(1)}</b> л воды</p>
  `;

  if (typeof loadStats === "function") loadStats();
}

async function loadProfile() {
  try {
    const res = await fetch("/profile/get");
    const user = await res.json();
    if (!user.name) return;

    const form = document.getElementById("profile-form");
    Object.keys(user).forEach(key => {
      if (form[key]) form[key].value = user[key];
    });

    const result = document.getElementById("profile-result");
    result.innerHTML = `
      <p class="text-lg font-semibold text-blue-600 mb-2">📋 Профиль загружен</p>
      <p>Норма: <b>${user.calories}</b> ккал и <b>${(user.water / 1000).toFixed(1)}</b> л воды</p>
    `;
  } catch (err) {
    console.error("Ошибка загрузки профиля:", err);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadProfile();
  const form = document.getElementById("profile-form");
  if (form) form.addEventListener("submit", handleProfileSubmit);
});
