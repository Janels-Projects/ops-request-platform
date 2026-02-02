/**
 * User Requests Page - JavaScript
 * Handles request loading, filtering, display, and modal interactions
 */

// ============================================
// Global State
// ============================================

let allRequests = [];
let filteredRequests = [];


// ============================================
// Initialization
// ============================================

document.addEventListener('DOMContentLoaded', function() {
  loadRequests();
  
  // Set up search
  document.getElementById('requests-search').addEventListener('input', applyFilters);
  
  // Set up filters
  document.getElementById('filter-status').addEventListener('change', applyFilters);
  document.getElementById('filter-priority').addEventListener('change', applyFilters);
  document.getElementById('filter-category').addEventListener('change', applyFilters);
  
  // Close modals on overlay click
  document.addEventListener('click', function(e) {
    if (e.target.classList.contains('modal-overlay')) {
      e.target.classList.remove('active');
    }
  });
});


// ============================================
// Data Loading
// ============================================

async function loadRequests() {
  try {
    const response = await fetch('/dashboard/api/user/requests', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to load requests');
    }

    allRequests = await response.json();
    filteredRequests = [...allRequests];
    
    renderRequests();
  } catch (error) {
    console.error('Error loading requests:', error);
    showError();
  }
}


// ============================================
// Filtering
// ============================================

function applyFilters() {
  const searchTerm = document.getElementById('requests-search').value.toLowerCase();
  const statusFilter = document.getElementById('filter-status').value;
  const priorityFilter = document.getElementById('filter-priority').value;
  const categoryFilter = document.getElementById('filter-category').value;

  filteredRequests = allRequests.filter(request => {
    // Search filter
    const matchesSearch = !searchTerm || 
      request.request_type.toLowerCase().includes(searchTerm) ||
      request.category.toLowerCase().includes(searchTerm) ||
      request.id.toString().includes(searchTerm);

    // Status filter
    const matchesStatus = !statusFilter || request.status === statusFilter;

    // Priority filter
    const matchesPriority = !priorityFilter || request.priority === priorityFilter;

    // Category filter
    const matchesCategory = !categoryFilter || request.category === categoryFilter;

    return matchesSearch && matchesStatus && matchesPriority && matchesCategory;
  });

  renderRequests();
}


// ============================================
// Rendering
// ============================================

function renderRequests() {
  const container = document.getElementById('requests-container');
  const emptyState = document.getElementById('empty-state');

  if (filteredRequests.length === 0) {
    container.style.display = 'none';
    emptyState.style.display = 'flex';
    return;
  }

  container.style.display = 'grid';
  emptyState.style.display = 'none';

  container.innerHTML = filteredRequests.map(request => `
    <div class="request-card" onclick="showRequestDetail(${request.id})">
      <div class="request-card-header">
        <div class="request-title-section">
          <h3 class="request-type">${escapeHtml(request.request_type)}</h3>
          <span class="request-id">#${request.id}</span>
        </div>
        <div class="request-badges">
          ${getStatusBadge(request.status)}
          ${getSLABadge(request.sla)}
        </div>
      </div>

      <div class="request-meta">
        <div class="meta-item">
          <svg class="meta-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M5 2h6a3 3 0 0 1 3 3v6a3 3 0 0 1-3 3H5a3 3 0 0 1-3-3V5a3 3 0 0 1 3-3z" stroke="currentColor" stroke-width="1.5"/>
          </svg>
          <span>${escapeHtml(request.category)}</span>
        </div>
        <div class="meta-item">
          <svg class="meta-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
            <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.5"/>
            <path d="M8 4v4l2 2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          <span>${formatDate(request.created_at)}</span>
        </div>
        <div class="meta-item">
          ${getPriorityIcon(request.priority)}
          <span class="priority-${request.priority}">${capitalizeFirst(request.priority)}</span>
        </div>
      </div>

      ${request.department ? `
        <div class="request-department">
          <svg class="dept-icon" width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M1 13V4.5L7 1l6 3.5V13M4 13V7h6v6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          ${escapeHtml(request.department)}
        </div>
      ` : ''}
    </div>
  `).join('');
}

function showError() {
  const container = document.getElementById('requests-container');
  container.innerHTML = `
    <div class="error-state">
      <svg class="error-icon" width="80" height="80" viewBox="0 0 80 80" fill="none">
        <circle cx="40" cy="40" r="35" stroke="#ef4444" stroke-width="2"/>
        <path d="M40 25v20M40 55v.1" stroke="#ef4444" stroke-width="3" stroke-linecap="round"/>
      </svg>
      <h2>Failed to load requests</h2>
      <p>Please try refreshing the page</p>
    </div>
  `;
}


// ============================================
// Modal Management
// ============================================

function showRequestDetail(requestId) {
  const request = allRequests.find(r => r.id === requestId);
  if (!request) return;

  // Populate modal
  document.getElementById('detail-request-id').textContent = request.id;
  document.getElementById('detail-request-type').textContent = request.request_type;
  document.getElementById('detail-category').textContent = request.category;
  document.getElementById('detail-department').textContent = request.department || 'N/A';
  
  // Status with badge
  const statusElement = document.getElementById('detail-status');
  statusElement.innerHTML = getStatusBadge(request.status);
  
  // Priority with badge
  const priorityElement = document.getElementById('detail-priority');
  priorityElement.innerHTML = getPriorityBadge(request.priority);
  
  // Dates
  document.getElementById('detail-created').textContent = formatDateTime(request.created_at);
  document.getElementById('detail-reviewed').textContent = request.reviewed_at ? formatDateTime(request.reviewed_at) : 'Not yet reviewed';
  
  // SLA
  const slaElement = document.getElementById('detail-sla');
  slaElement.innerHTML = getSLABadge(request.sla);

  // Review notes
  const reviewSection = document.getElementById('review-notes-section');
  const reviewNotes = document.getElementById('detail-review-notes');
  if (request.admin_review_notes) {
    reviewSection.style.display = 'block';
    reviewNotes.textContent = request.admin_review_notes;
  } else {
    reviewSection.style.display = 'none';
  }

  // Show modal
  document.getElementById('requestDetailModal').classList.add('active');
}

function closeDetailModal() {
  document.getElementById('requestDetailModal').classList.remove('active');
}

function openNewRequestModal() {
  document.getElementById('newRequestModal').classList.add('active');
}

function closeNewRequestModal() {
  document.getElementById('newRequestModal').classList.remove('active');
}


// ============================================
// Badge Generators
// ============================================

function getStatusBadge(status) {
  const statusMap = {
    'pending': { label: 'Pending', class: 'status-pending' },
    'in_progress': { label: 'In Progress', class: 'status-progress' },
    'approved': { label: 'Approved', class: 'status-approved' },
    'denied': { label: 'Denied', class: 'status-denied' },
    'completed': { label: 'Completed', class: 'status-completed' }
  };
  
  const config = statusMap[status] || { label: status, class: 'status-default' };
  return `<span class="status-badge ${config.class}">${config.label}</span>`;
}

function getSLABadge(sla) {
  if (!sla) return '';
  
  const slaMap = {
    'on_time': { label: 'On Time', class: 'sla-good' },
    'at_risk': { label: 'At Risk', class: 'sla-warning' },
    'overdue': { label: 'Overdue', class: 'sla-danger' }
  };
  
  const config = slaMap[sla] || { label: sla, class: 'sla-default' };
  return `<span class="sla-badge ${config.class}">${config.label}</span>`;
}

function getPriorityBadge(priority) {
  const priorityMap = {
    'low': { label: 'Low', class: 'priority-low' },
    'medium': { label: 'Medium', class: 'priority-medium' },
    'high': { label: 'High', class: 'priority-high' }
  };
  
  const config = priorityMap[priority] || { label: priority, class: 'priority-default' };
  return `<span class="priority-badge ${config.class}">${config.label}</span>`;
}

function getPriorityIcon(priority) {
  const icons = {
    'low': '<svg class="meta-icon" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 12V4M5 9l3 3 3-3" stroke="#10b981" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    'medium': '<svg class="meta-icon" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3 8h10" stroke="#f59e0b" stroke-width="1.5" stroke-linecap="round"/></svg>',
    'high': '<svg class="meta-icon" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 4v8M5 7l3-3 3 3" stroke="#ef4444" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
  };
  return icons[priority] || '';
}


// ============================================
// Utility Functions
// ============================================

function formatDate(dateString) {
  const date = new Date(dateString);
  const now = new Date();
  const diffTime = Math.abs(now - date);
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return `${diffDays} days ago`;
  
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function formatDateTime(dateString) {
  const date = new Date(dateString);
  return date.toLocaleString('en-US', { 
    month: 'short', 
    day: 'numeric', 
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  });
}

function capitalizeFirst(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}