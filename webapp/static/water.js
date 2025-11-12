// webapp/static/water.js

let waterLocked = false;

// 💧 Добавление воды
async function addWater(amount) {
  if (waterLocked) return;
  waterLocked = true;

  try {
    const res = await fetch("/add_water", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ amount })
    });

    if (!res.ok) throw new Error("Ошибка добавления воды");

    const msg = document.getElementById("water-result");
    if (msg) {
      msg.innerHTML = `<p class="text-green-600 font-semibold">💧 +${amount} мл добавлено</p>`;
      setTimeout(() => (msg.innerHTML = ""), 1500);
    }

    // Сначала обновляем локально воду
    await loadWater();

    // Затем статистику (если есть функция)
    if (typeof loadStats === "function") loadStats();

  } catch (err) {
    console.error(err);
    const msg = document.getElementById("water-result");
    if (msg) msg.innerHTML = `<p class="text-red-600 font-semibold">⚠️ Ошибка</p>`;
  } finally {
    waterLocked = false;
  }
}

// 📊 Загрузка общего количества воды
async function loadWater() {
  try {
    const res = await fetch("/get_water");
    const data = await res.json();
    const total = parseFloat(data.total || 0);

    const totalElement = document.getElementById("water-total");
    if (totalElement) {
      totalElement.textContent = (total / 1000).toFixed(2);
    }

  } catch (err) {
    console.error("Ошибка загрузки воды:", err);
  }
}

window.addEventListener("load", loadWater);
