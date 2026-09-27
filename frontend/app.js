const API = "/api";

const CATEGORY_COLORS = [
  "#2f5233", // forest
  "#a15c3b", // clay
  "#6b7a5e", // sage
  "#8a6d3b", // ochre
  "#4a6670", // slate blue
  "#7a4b5c", // muted plum
  "#9a8c5e", // olive tan
  "#5c675e", // ink-soft, fallback
];

const monthInput = document.getElementById("month-input");
const entryForm = document.getElementById("entry-form");
const formError = document.getElementById("form-error");
const categorySelect = document.getElementById("category");
const ledgerEl = document.getElementById("ledger");
const emptyState = document.getElementById("empty-state");
const breakdownEl = document.getElementById("breakdown");
const totalSpentEl = document.getElementById("total-spent");
const entryCountEl = document.getElementById("entry-count");
const dateInput = document.getElementById("date");

function currentMonthString() {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
}

function formatMoney(amount) {
  return `$${amount.toFixed(2)}`;
}

function formatDate(isoDate) {
  const d = new Date(isoDate + "T00:00:00");
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

async function loadCategories() {
  const res = await fetch(`${API}/categories`);
  const categories = await res.json();
  categorySelect.innerHTML = categories
    .map((c) => `<option value="${c}">${c}</option>`)
    .join("");
}

async function loadExpenses(month) {
  const res = await fetch(`${API}/expenses?month=${month}`);
  const expenses = await res.json();
  renderLedger(expenses);
}

async function loadSummary(month) {
  const res = await fetch(`${API}/summary?month=${month}`);
  const summary = await res.json();
  renderSummary(summary);
}

function renderLedger(expenses) {
  if (expenses.length === 0) {
    ledgerEl.innerHTML = "";
    ledgerEl.appendChild(emptyState);
    return;
  }

  const rows = expenses
    .map(
      (e) => `
      <div class="ledger-row" data-id="${e.id}">
        <div class="col-date">${formatDate(e.date)}</div>
        <div class="col-description">${escapeHtml(e.description)}</div>
        <div class="col-category">${escapeHtml(e.category)}</div>
        <div class="col-amount">${formatMoney(e.amount)}</div>
        <div class="col-delete">
          <button class="delete-button" data-id="${e.id}" title="Delete entry">&times;</button>
        </div>
      </div>`
    )
    .join("");

  ledgerEl.innerHTML = rows;

  ledgerEl.querySelectorAll(".delete-button").forEach((btn) => {
    btn.addEventListener("click", () => deleteExpense(btn.dataset.id));
  });
}

function renderSummary(summary) {
  totalSpentEl.textContent = formatMoney(summary.total_spent);
  entryCountEl.textContent = summary.expense_count;

  if (summary.by_category.length === 0) {
    breakdownEl.innerHTML = `<p class="breakdown-empty">No spending recorded for this month yet.</p>`;
    return;
  }

  const maxTotal = Math.max(...summary.by_category.map((c) => c.total));

  breakdownEl.innerHTML = summary.by_category
    .map((c, i) => {
      const widthPct = maxTotal > 0 ? (c.total / maxTotal) * 100 : 0;
      const color = CATEGORY_COLORS[i % CATEGORY_COLORS.length];
      return `
        <div class="breakdown-row">
          <div class="cat-name">${escapeHtml(c.category)}</div>
          <div class="breakdown-track">
            <div class="breakdown-fill" style="width:${widthPct}%; background:${color};"></div>
          </div>
          <div class="cat-total">${formatMoney(c.total)}</div>
        </div>`;
    })
    .join("");
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

async function refresh() {
  const month = monthInput.value;
  await Promise.all([loadExpenses(month), loadSummary(month)]);
}

async function deleteExpense(id) {
  await fetch(`${API}/expenses/${id}`, { method: "DELETE" });
  await refresh();
}

entryForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  formError.textContent = "";

  const payload = {
    description: document.getElementById("description").value.trim(),
    amount: parseFloat(document.getElementById("amount").value),
    category: categorySelect.value,
    date: dateInput.value,
  };

  if (!payload.description || !payload.date || isNaN(payload.amount) || payload.amount <= 0) {
    formError.textContent = "Fill in a description, a positive amount, and a date.";
    return;
  }

  const res = await fetch(`${API}/expenses`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    formError.textContent = "Couldn't save that entry — try again.";
    return;
  }

  entryForm.reset();
  dateInput.value = new Date().toISOString().slice(0, 10);
  await refresh();
});

monthInput.addEventListener("change", refresh);

(async function init() {
  monthInput.value = currentMonthString();
  dateInput.value = new Date().toISOString().slice(0, 10);
  await loadCategories();
  await refresh();
})();
