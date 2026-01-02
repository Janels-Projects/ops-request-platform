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

// Show admin notes textarea when an action button is clicked
document.addEventListener("click", function (e) {
  const btn = e.target.closest(".action-btn");
  if (!btn) return;

  const form = btn.closest("form");
  if (!form) return;

  const notes = form.querySelector(".admin-notes");
  if (!notes) return;

  // Check if textarea is already visible
  if (notes.style.display === "none" || notes.style.display === "") {
    // Prevent form submission on first click
    e.preventDefault();
    
    // Show the textarea
    notes.style.display = "block";
    notes.focus();
    
    // Change button text to indicate next click will submit
    const originalText = btn.textContent;
    btn.dataset.originalText = originalText;
    btn.textContent = originalText + " (Click again to submit)";
    
  } else {
    // Textarea is visible, allow form to submit normally
    // (no e.preventDefault() here)
  }
});

// Optional: Add a cancel button functionality
document.addEventListener("keydown", function (e) {
  if (e.key === "Escape") {
    const activeNotes = document.querySelector(".admin-notes[style*='display: block']");
    if (activeNotes) {
      const form = activeNotes.closest("form");
      const btn = form.querySelector(".action-btn");
      
      // Hide textarea
      activeNotes.style.display = "none";
      activeNotes.value = "";
      
      // Restore button text
      if (btn.dataset.originalText) {
        btn.textContent = btn.dataset.originalText;
        delete btn.dataset.originalText;
      }
    }
  }
});
