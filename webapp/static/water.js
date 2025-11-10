// webapp/static/water.js

async function addWater(amount) {
  await fetch("/add_water", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ amount: amount })
  });

  document.getElementById("water-result").innerHTML =
    `<p class="text-green-600 font-semibold">💧 +${amount} мл добавлено</p>`;
    // 🔄 обновляем статистику
  if (typeof loadStats === "function") loadStats();
  loadWater();
}

async function loadWater() {
  const res = await fetch("/get_water");
  const data = await res.json();
  const total = parseFloat(data.total || 0);
  document.getElementById("water-total").textContent = (total / 1000).toFixed(2);
}

window.addEventListener("load", loadWater);
