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

  tbody.innerHTML = `<tr><td colspan="5">Loading requests...</td></tr>`;

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
      tbody.innerHTML = `<tr><td colspan="5">No requests yet</td></tr>`;
      return;
    }

    // Sort by created_at (most recent first) and take only top 5
    const recentRequests = data
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      .slice(0, 5);

    tbody.innerHTML = "";

    // Calculate stats from ALL requests (not just the 5 shown)
    updateDashboardStats(data);

    recentRequests.forEach(req => {
      const tr = document.createElement("tr");
      tr.classList.add("request-row");

      tr.dataset.status = req.status;
      tr.dataset.category = req.category;
      tr.dataset.priority = req.priority;

      const noteId = `note-${req.id}`;

      tr.innerHTML = `
        <td>
          <strong class="request-title">${req.request_type}</strong>
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
        <td><span class="status-badge ${req.status}">${req.status}</span></td>
        <td><span class="priority-badge ${req.priority}">${req.priority}</span></td>
        <td>${req.created_at}</td>
      `;

      tbody.appendChild(tr);
    });

    applyFilters(); // reuse your existing filter logic
  } catch (err) {
    console.error("Failed to load requests:", err);
    tbody.innerHTML = `<tr><td colspan="5">Error loading requests</td></tr>`;
  }
}

// Update dashboard statistics
function updateDashboardStats(requests) {
  // Open Items (pending status)
  const openItems = requests.filter(r => r.status === 'pending').length;
  const openItemsEl = document.getElementById('open-items');
  if (openItemsEl) {
    openItemsEl.textContent = openItems;
  }

  // Completed Recently (last 30 days)
  const thirtyDaysAgo = new Date();
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
  
  const completedRecently = requests.filter(r => {
    const createdDate = new Date(r.created_at);
    return (r.status === 'approved' || r.status === 'completed' || r.status === 'denied') 
           && createdDate >= thirtyDaysAgo;
  }).length;
  
  const completedRecentlyEl = document.getElementById('completed-recently');
  if (completedRecentlyEl) {
    completedRecentlyEl.textContent = completedRecently;
  }

  // This Week (last 7 days)
  const sevenDaysAgo = new Date();
  sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
  
  const thisWeek = requests.filter(r => {
    const createdDate = new Date(r.created_at);
    return createdDate >= sevenDaysAgo;
  }).length;
  
  const thisWeekEl = document.getElementById('this-week');
  if (thisWeekEl) {
    thisWeekEl.textContent = thisWeek;
  }

  // Average Processing Time
  const completed = requests.filter(r => 
    r.status === 'approved' || r.status === 'completed' || r.status === 'denied'
  );
  
  if (completed.length > 0) {
    const avgTime = completed.reduce((sum, r) => {
      const start = new Date(r.created_at);
      const end = r.updated_at ? new Date(r.updated_at) : new Date();
      const days = Math.floor((end - start) / (1000 * 60 * 60 * 24));
      return sum + days;
    }, 0) / completed.length;
    
    const avgTimeEl = document.getElementById('avg-time');
    if (avgTimeEl) {
      avgTimeEl.textContent = avgTime.toFixed(1);
    }
  }

  // Show/hide alert banner
  const alertBanner = document.getElementById('alert-banner');
  const alertText = document.getElementById('alert-text');
  
  if (alertBanner) {
    if (openItems > 0) {
      alertBanner.classList.remove('hidden');
      
      // Update alert text with proper pluralization
      if (alertText) {
        if (openItems === 1) {
          alertText.textContent = 'You have 1 request awaiting review';
        } else {
          alertText.textContent = `You have ${openItems} requests awaiting review`;
        }
      }
    } else {
      alertBanner.classList.add('hidden');
    }
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