// Get filter elements
const statusFilter = document.getElementById('statusFilter');
const categoryFilter = document.getElementById('categoryFilter');
const priorityFilter = document.getElementById('priorityFilter');
const departmentFilter = document.getElementById('departmentFilter');


// Run whenever a filter changes
function applyFilters() {
  if (!statusFilter || !categoryFilter || !priorityFilter || !departmentFilter) {
    return; // user dashboard has no filters
  }

  const status = statusFilter.value;
  const category = categoryFilter.value;
  const priority = priorityFilter.value;
  const department = departmentFilter.value;

  document.querySelectorAll('.request-row').forEach(row => {
    const matchesStatus =
      status === 'all' || row.dataset.status === status;

    const matchesCategory =
      category === 'all' || row.dataset.category === category;

    const matchesPriority =
      priority === 'all' || row.dataset.priority === priority;

    const matchesDepartment =
      department === 'all' || row.dataset.department === department;

    row.style.display =
      matchesStatus && matchesCategory && matchesPriority && matchesDepartment
        ? ''
        : 'none';
  });
}


// Attach listeners
if (statusFilter && categoryFilter && priorityFilter && departmentFilter) {
  statusFilter.addEventListener('change', applyFilters);
  categoryFilter.addEventListener('change', applyFilters);
  priorityFilter.addEventListener('change', applyFilters);
  departmentFilter.addEventListener('change', applyFilters);
}


// Admin notes helper - Two-click flow
document.addEventListener("click", function (e) {
  const btn = e.target.closest("[data-requires-notes]");
  if (!btn) return;

  const form = btn.closest("form");
  const row = btn.closest("tr");
  if (!form || !row) return;

  const notesWrap = row.querySelector(".admin-notes-wrap");
  const textarea = row.querySelector(".admin-notes-shared");

  if (!notesWrap || !textarea) return;

  // Check if textarea is already visible
  if (notesWrap.style.display === "none" || notesWrap.style.display === "") {
    // FIRST CLICK: Show textarea, prevent submission
    e.preventDefault();
    
    notesWrap.style.display = "block";
    textarea.focus();
    
    // Update button to show it needs another click
    const originalText = btn.textContent;
    btn.dataset.originalText = originalText;
    btn.textContent = originalText + " (Click again)";
    
  } else {
    // SECOND CLICK: Transfer notes to hidden field and submit
    const hidden = form.querySelector('input[name="admin_review_notes"]');
    if (hidden) {
      hidden.value = textarea.value.trim();
    }
    
    // Change button type to submit so form will submit
    btn.type = "submit";
    // Form will submit naturally after this click
  }
});



// Optional: ESC key to cancel
document.addEventListener("keydown", function (e) {
  if (e.key === "Escape") {
    const visibleNotes = document.querySelector('.admin-notes-wrap[style*="display: block"]');
    if (visibleNotes) {
      const row = visibleNotes.closest("tr");
      const textarea = visibleNotes.querySelector(".admin-notes-shared");
      const btn = row.querySelector("[data-requires-notes]");
      
      // Hide and reset
      visibleNotes.style.display = "none";
      textarea.value = "";
      
      if (btn && btn.dataset.originalText) {
        btn.textContent = btn.dataset.originalText;
        delete btn.dataset.originalText;
      }
    }
  }
});
// -------------------------------
// User Requests Loader
// -------------------------------
async function loadUserRequests() {
  const tbody = document.querySelector("#my-requests-body");
  if (!tbody) return;

  tbody.innerHTML = `<tr><td colspan="6">Loading requests...</td></tr>`;

  try {
    const res = await fetch("/dashboard/api/user/requests", {
  credentials: "include"
});
console.log("FETCHED /dashboard/api/user/requests");

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }

    const data = await res.json();

    if (!Array.isArray(data) || data.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6">No requests yet</td></tr>`;
      return;
    }

    tbody.innerHTML = "";

    data.forEach(req => {
      const tr = document.createElement("tr");
      tr.classList.add("request-row");

      tr.dataset.status = req.status;
      tr.dataset.category = req.category;
      tr.dataset.priority = req.priority;
      tr.dataset.department = req.department;

    const noteId = `note-${req.id}`;

tr.innerHTML = `
  <td>
    <strong>${req.request_type}</strong>
    ${
      req.admin_review_notes
        ? `
        <div class="admin-note-container">
          <button class="admin-note-toggle" data-note-id="${noteId}">
            <span>View Admin Note</span>
            <span class="chevron">⌄</span>
          </button>
          <div class="admin-note-content" id="${noteId}">
            <div class="admin-note-text">
              ${req.admin_review_notes}
            </div>
          </div>
        </div>
        `
        : ""
    }
  </td>
  <td>${req.category}</td>
  <td>${req.department || "-"}</td>
  <td>${req.priority}</td>
  <td><span class="badge ${req.status}">${req.status}</span></td>
  <td>${req.created_at}</td>
`;


      tbody.appendChild(tr);
    });

    applyFilters(); // reuse your existing filter logic
  } catch (err) {
    console.error("Failed to load requests:", err);
    tbody.innerHTML = `<tr><td colspan="6">Error loading requests</td></tr>`;
  }
}

// Auto-load on page load
document.addEventListener("DOMContentLoaded", loadUserRequests);


// User dashboard: toggle admin note visibility (FORCE INLINE)
document.addEventListener("click", function (e) {
  const button = e.target.closest(".admin-note-toggle");
  if (!button) return;

  e.preventDefault();

  const noteId = button.dataset.noteId;
  const content = document.getElementById(noteId);
  if (!content) return;

  // 🔥 INLINE TOGGLE — ignores CSS entirely
  if (content.style.display === "block") {
    content.style.display = "none";
    button.classList.remove("active");
  } else {
    content.style.display = "block";
    button.classList.add("active");
  }
});



