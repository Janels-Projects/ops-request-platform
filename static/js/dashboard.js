// Get filter elements
const statusFilter = document.getElementById('statusFilter');
const categoryFilter = document.getElementById('categoryFilter');
const priorityFilter = document.getElementById('priorityFilter');
const departmentFilter = document.getElementById('departmentFilter');


// Run whenever a filter changes
function applyFilters() {
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
statusFilter.addEventListener('change', applyFilters);
categoryFilter.addEventListener('change', applyFilters);
priorityFilter.addEventListener('change', applyFilters);
departmentFilter.addEventListener('change', applyFilters);

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
