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

