// ===============================
// 📋 ЗАГРУЗКА СПИСКА ПРОДУКТОВ
// ===============================
export async function loadFoodList() {
  const container = document.getElementById("food-list");
  const resp = await fetch("/food/list");
  const data = await resp.json();

  container.innerHTML = "";
  for (const item of data) {
    const div = document.createElement("div");
    div.classList.add("food-item");
    div.innerHTML = `
      <div>
        <strong>${item.name}</strong> - ${item.weight}г
        <span>${item.calories.toFixed(1)} ккал</span>
      </div>
      <button onclick="editFood(${item.id})">✏️</button>
      <button onclick="deleteFood(${item.id})">🗑</button>
    `;
    container.appendChild(div);
  }
}

// ===============================
// ✏️ РЕДАКТИРОВАНИЕ
// ===============================
export async function editFood(id) {
  const resp = await fetch(`/food/edit/${id}`);
  const data = await resp.json();
  console.log("Редактирование:", data);
}

// ===============================
// ❌ УДАЛЕНИЕ
// ===============================
export async function deleteFood(id) {
  if (!confirm("Удалить продукт?")) return;
  await fetch(`/food/delete/${id}`, { method: "DELETE" });
  loadFoodList();
}
