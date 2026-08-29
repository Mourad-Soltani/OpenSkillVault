/**
 * OpenSkillVault Frontend
 * Author: Mourad.Soltani
 * Signature: Mourad.Soltani - 2026 AI Agent Skills Manager
 */

const API = "";

let currentCategory = "";
let currentQuery = "";

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

function toast(msg, type = "success") {
  const el = $("#toast");
  el.textContent = msg + " · Mourad.Soltani";
  el.className = `toast ${type}`;
  el.classList.remove("hidden");
  setTimeout(() => el.classList.add("hidden"), 3000);
}

async function fetchJSON(url, options = {}) {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || res.statusText);
  return data;
}

async function loadStats() {
  try {
    const data = await fetchJSON("/api/stats");
    $("#stats").innerHTML = `
      <p><strong>${data.skills_count}</strong> skills</p>
      <p>${data.categories.length} categories</p>
      <p class="sig">by ${data.author}</p>
    `;
  } catch (e) {
    $("#stats").innerHTML = `<p>Offline</p><p class="sig">Mourad.Soltani</p>`;
  }
}

async function loadCategories() {
  try {
    const data = await fetchJSON("/api/categories");
    const list = $("#category-list");
    list.innerHTML = `<li class="active" data-cat="">All</li>`;
    data.categories.forEach((c) => {
      const li = document.createElement("li");
      li.dataset.cat = c;
      li.textContent = c;
      list.appendChild(li);
    });
    $$("#category-list li").forEach((li) => {
      li.addEventListener("click", () => {
        $$("#category-list li").forEach((x) => x.classList.remove("active"));
        li.classList.add("active");
        currentCategory = li.dataset.cat;
        loadSkills();
      });
    });
  } catch (e) {
    console.error(e);
  }
}

function renderSkill(skill) {
  const card = document.createElement("article");
  card.className = "skill-card";
  card.innerHTML = `
    <span class="cat">${skill.category || "general"}</span>
    <h3>${escapeHtml(skill.title || skill.name)}</h3>
    <p class="desc">${escapeHtml(skill.description || "No description")}</p>
    <div class="meta">
      <span>${skill.author || "Mourad.Soltani"}</span>
      <span>${(skill.updated_at || "").slice(0, 10)}</span>
    </div>
    <div class="actions">
      <button class="btn" data-action="view" data-id="${skill.id}">View</button>
      <button class="btn" data-action="edit" data-id="${skill.id}">Edit</button>
      <button class="btn danger" data-action="delete" data-id="${skill.id}">Delete</button>
    </div>
  `;
  card.querySelectorAll("[data-action]").forEach((btn) => {
    btn.addEventListener("click", () => handleAction(btn.dataset.action, btn.dataset.id));
  });
  return card;
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

async function loadSkills() {
  const params = new URLSearchParams();
  if (currentCategory) params.set("category", currentCategory);
  if (currentQuery) params.set("q", currentQuery);
  try {
    const data = await fetchJSON(`/api/skills?${params}`);
    const list = $("#skill-list");
    list.innerHTML = "";
    if (!data.skills.length) {
      $("#empty-state").classList.remove("hidden");
    } else {
      $("#empty-state").classList.add("hidden");
      data.skills.forEach((s) => list.appendChild(renderSkill(s)));
    }
  } catch (e) {
    toast("Failed to load skills", "error");
  }
}

async function handleAction(action, id) {
  if (action === "delete") {
    if (!confirm("Delete this skill? Mourad.Soltani")) return;
    try {
      await fetchJSON(`/api/skills/${id}`, { method: "DELETE" });
      toast("Skill deleted");
      loadSkills();
      loadStats();
      loadCategories();
    } catch (e) {
      toast(e.message, "error");
    }
  } else if (action === "edit" || action === "view") {
    try {
      const skill = await fetchJSON(`/api/skills/${id}`);
      openModal(skill, action === "view");
    } catch (e) {
      toast(e.message, "error");
    }
  }
}

function openModal(skill = null, readOnly = false) {
  const modal = $("#modal");
  $("#modal-title").textContent = skill ? (readOnly ? "View Skill" : "Edit Skill") : "New Skill";
  $("#skill-id").value = skill?.id || "";
  $("#skill-name").value = skill?.name || "";
  $("#skill-name").disabled = !!skill;
  $("#skill-title").value = skill?.title || "";
  $("#skill-category").value = skill?.category || "general";
  $("#skill-description").value = skill?.description || "";
  $("#skill-content").value = skill?.content || "";
  const inputs = $$("#skill-form input, #skill-form textarea");
  inputs.forEach((el) => (el.readOnly = readOnly));
  $("#skill-form").querySelector('button[type="submit"]').style.display = readOnly ? "none" : "inline-block";
  modal.classList.remove("hidden");
}

function closeModal() {
  $("#modal").classList.add("hidden");
}

$("#btn-new").addEventListener("click", () => openModal());
$("#modal-close").addEventListener("click", closeModal);
$("#btn-cancel").addEventListener("click", closeModal);

$("#skill-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const id = $("#skill-id").value;
  const payload = {
    name: $("#skill-name").value.trim(),
    title: $("#skill-title").value.trim(),
    category: $("#skill-category").value.trim() || "general",
    description: $("#skill-description").value.trim(),
    content: $("#skill-content").value,
  };
  try {
    if (id) {
      await fetchJSON(`/api/skills/${id}`, { method: "PUT", body: JSON.stringify(payload) });
      toast("Skill updated");
    } else {
      await fetchJSON("/api/skills", { method: "POST", body: JSON.stringify(payload) });
      toast("Skill created");
    }
    closeModal();
    loadSkills();
    loadStats();
    loadCategories();
  } catch (err) {
    toast(err.message, "error");
  }
});

$("#btn-export").addEventListener("click", async () => {
  try {
    const pack = await fetchJSON("/api/export");
    const blob = new Blob([JSON.stringify(pack, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `openskillvault-pack-mourad-soltani.json`;
    a.click();
    URL.revokeObjectURL(url);
    toast("Pack exported · Mourad.Soltani");
  } catch (e) {
    toast(e.message, "error");
  }
});

$("#btn-health").addEventListener("click", async () => {
  try {
    const h = await fetchJSON("/health");
    toast(`Healthy · ${h.skills_count} skills · ${h.signature}`);
  } catch (e) {
    toast("Health check failed", "error");
  }
});

let searchTimer;
$("#search").addEventListener("input", (e) => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    currentQuery = e.target.value.trim();
    loadSkills();
  }, 250);
});

// Boot
document.addEventListener("DOMContentLoaded", () => {
  console.log("OpenSkillVault by Mourad.Soltani — ready");
  loadStats();
  loadCategories();
  loadSkills();
});
