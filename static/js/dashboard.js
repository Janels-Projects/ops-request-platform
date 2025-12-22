// Get filter elements
const statusFilter = document.getElementById('statusFilter');
const categoryFilter = document.getElementById('categoryFilter');
const priorityFilter = document.getElementById('priorityFilter');

// Run whenever a filter changes
function applyFilters() {
  const status = statusFilter.value;
  const category = categoryFilter.value;
  const priority = priorityFilter.value;

  document.querySelectorAll('.request-row').forEach(row => {
    const matchesStatus =
      status === 'all' || row.dataset.status === status;

    const matchesCategory =
      category === 'all' || row.dataset.category === category;

    const matchesPriority =
      priority === 'all' || row.dataset.priority === priority;

    row.style.display =
      matchesStatus && matchesCategory && matchesPriority
        ? ''
        : 'none';
  });
}

// Attach listeners
statusFilter.addEventListener('change', applyFilters);
categoryFilter.addEventListener('change', applyFilters);
priorityFilter.addEventListener('change', applyFilters);
