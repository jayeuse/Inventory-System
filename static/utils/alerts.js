/**
 * Inventory Alerts Management
 * Handles low stock and near expiry notifications
 */

(function() {
  'use strict';

  // Store alerts data
  let alertsData = {
    summary: { total: 0, critical: 0, warning: 0 },
    alerts: []
  };
  let currentFilter = 'all';
  let isLoading = false;
  let panelOpen = false;

  /**
   * Initialize the alerts system
   */
  function initAlerts() {
    // Wait for sidebar to be loaded
    const checkSidebar = setInterval(() => {
      const bellIcon = document.getElementById('notificationBellIcon');
      const bellLabel = document.getElementById('notificationBellLabel');
      
      if (bellIcon || bellLabel) {
        clearInterval(checkSidebar);
        setupEventListeners();
        fetchAlerts();
        
        // Refresh alerts every 5 minutes
        setInterval(fetchAlerts, 5 * 60 * 1000);
      }
    }, 100);

    // Stop checking after 10 seconds
    setTimeout(() => clearInterval(checkSidebar), 10000);
  }

  /**
   * Setup event listeners for notification elements
   */
  function setupEventListeners() {
    const bellIcon = document.getElementById('notificationBellIcon');
    const bellLabel = document.getElementById('notificationBellLabel');
    const closeBtn = document.getElementById('notificationClose');
    const panel = document.getElementById('notificationPanel');
    const filtersContainer = document.getElementById('notificationFilters');

    // Toggle panel on bell click
    if (bellIcon) {
      bellIcon.addEventListener('click', (e) => {
        e.stopPropagation();
        togglePanel();
      });
    }

    if (bellLabel) {
      bellLabel.addEventListener('click', (e) => {
        e.stopPropagation();
        togglePanel();
      });
    }

    // Close panel
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        closePanel();
      });
    }

    // Filter buttons
    if (filtersContainer) {
      filtersContainer.addEventListener('click', (e) => {
        const filterBtn = e.target.closest('.filter-btn');
        if (filterBtn) {
          const filter = filterBtn.dataset.filter;
          setFilter(filter);
        }
      });
    }

    // Close panel when clicking outside
    document.addEventListener('click', (e) => {
      if (panelOpen && panel && !panel.contains(e.target)) {
        const bellIcon = document.getElementById('notificationBellIcon');
        const bellLabel = document.getElementById('notificationBellLabel');
        if (bellIcon && !bellIcon.contains(e.target) && bellLabel && !bellLabel.contains(e.target)) {
          closePanel();
        }
      }
    });

    // Close panel on escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && panelOpen) {
        closePanel();
      }
    });
  }

  /**
   * Toggle the notification panel
   */
  function togglePanel() {
    const panel = document.getElementById('notificationPanel');
    if (!panel) return;

    if (panelOpen) {
      closePanel();
    } else {
      openPanel();
    }
  }

  /**
   * Open the notification panel
   */
  function openPanel() {
    const panel = document.getElementById('notificationPanel');
    if (!panel) return;

    panel.style.display = 'flex';
    panelOpen = true;
    
    // Refresh alerts when opening
    fetchAlerts();
  }

  /**
   * Close the notification panel
   */
  function closePanel() {
    const panel = document.getElementById('notificationPanel');
    if (!panel) return;

    panel.style.display = 'none';
    panelOpen = false;
  }

  /**
   * Fetch alerts from the API
   */
  async function fetchAlerts() {
    if (isLoading) return;
    isLoading = true;

    const listContainer = document.getElementById('notificationList');
    if (listContainer && panelOpen) {
      listContainer.innerHTML = `
        <div class="notification-loading">
          <i class="fa-solid fa-spinner fa-spin"></i> Loading alerts...
        </div>
      `;
    }

    try {
      const response = await fetch('/api/alerts/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken()
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch alerts');
      }

      const data = await response.json();
      alertsData = data;
      
      updateBadge();
      updateSummary();
      renderAlerts();
      
    } catch (error) {
      console.error('Error fetching alerts:', error);
      if (listContainer && panelOpen) {
        listContainer.innerHTML = `
          <div class="notification-empty">
            <i class="fa-solid fa-exclamation-triangle" style="color: #f59e0b;"></i>
            <h4>Unable to load alerts</h4>
            <p>Please try again later</p>
          </div>
        `;
      }
    } finally {
      isLoading = false;
    }
  }

  /**
   * Get CSRF token for API requests
   */
  function getCSRFToken() {
    // Try to get from cookie
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue || '';
  }

  /**
   * Update the notification badge count
   */
  function updateBadge() {
    const badge = document.getElementById('notificationBadge');
    const badgeLabel = document.getElementById('notificationBadgeLabel');
    const count = alertsData.summary.total || 0;

    if (badge) {
      if (count > 0) {
        badge.textContent = count > 99 ? '99+' : count;
        badge.style.display = 'flex';
      } else {
        badge.style.display = 'none';
      }
    }

    if (badgeLabel) {
      if (count > 0) {
        badgeLabel.textContent = count > 99 ? '99+' : count;
        badgeLabel.style.display = 'flex';
      } else {
        badgeLabel.style.display = 'none';
      }
    }
  }

  /**
   * Update the summary section
   */
  function updateSummary() {
    const criticalCount = document.getElementById('criticalCount');
    const warningCount = document.getElementById('warningCount');

    if (criticalCount) {
      criticalCount.textContent = alertsData.summary.critical || 0;
    }

    if (warningCount) {
      warningCount.textContent = alertsData.summary.warning || 0;
    }
  }

  /**
   * Set the current filter
   */
  function setFilter(filter) {
    currentFilter = filter;

    // Update filter button states
    const filterBtns = document.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => {
      btn.classList.toggle('active', btn.dataset.filter === filter);
    });

    renderAlerts();
  }

  /**
   * Render the alerts list
   */
  function renderAlerts() {
    const listContainer = document.getElementById('notificationList');
    if (!listContainer) return;

    // Filter alerts based on current filter
    let filteredAlerts = alertsData.alerts || [];
    
    if (currentFilter !== 'all') {
      if (currentFilter === 'low_stock') {
        filteredAlerts = filteredAlerts.filter(a => a.type === 'low_stock');
      } else if (currentFilter === 'out_of_stock') {
        filteredAlerts = filteredAlerts.filter(a => a.type === 'out_of_stock');
      } else if (currentFilter === 'near_expiry') {
        filteredAlerts = filteredAlerts.filter(a => a.type === 'near_expiry');
      } else if (currentFilter === 'expired') {
        filteredAlerts = filteredAlerts.filter(a => a.type === 'expired');
      }
    }

    if (filteredAlerts.length === 0) {
      listContainer.innerHTML = `
        <div class="notification-empty">
          <i class="fa-solid fa-check-circle"></i>
          <h4>All Clear!</h4>
          <p>No ${currentFilter === 'all' ? '' : currentFilter.replace('_', ' ')} alerts at this time</p>
        </div>
      `;
      return;
    }

    const alertsHtml = filteredAlerts.map(alert => {
      const icon = getAlertIcon(alert.type);
      const typeBadge = getTypeBadge(alert.type);
      const severityClass = alert.severity || 'warning';
      const stockId = alert.stock_id || '';
      
      return `
        <div class="alert-item ${severityClass}" data-stock-id="${stockId}" data-product-id="${alert.product_id}" onclick="InventoryAlerts.openStock('${stockId}')">
          <div class="alert-icon">
            <i class="${icon}"></i>
          </div>
          <div class="alert-content">
            <div class="alert-title" title="${alert.product_name}">${alert.product_name}</div>
            <div class="alert-message">${alert.message}</div>
            <div class="alert-meta">
              ${typeBadge}
              <span>${alert.category}</span>
            </div>
          </div>
          <div class="alert-arrow">
            <i class="fa-solid fa-chevron-right"></i>
          </div>
        </div>
      `;
    }).join('');

    listContainer.innerHTML = alertsHtml;
  }

  /**
   * Get icon for alert type
   */
  function getAlertIcon(type) {
    switch (type) {
      case 'low_stock':
        return 'fa-solid fa-box-open';
      case 'out_of_stock':
        return 'fa-solid fa-box';
      case 'near_expiry':
        return 'fa-solid fa-clock';
      case 'expired':
        return 'fa-solid fa-skull-crossbones';
      default:
        return 'fa-solid fa-exclamation-triangle';
    }
  }

  /**
   * Get type badge HTML
   */
  function getTypeBadge(type) {
    const labels = {
      'low_stock': 'Low Stock',
      'out_of_stock': 'Out of Stock',
      'near_expiry': 'Near Expiry',
      'expired': 'Expired'
    };
    
    const cssClass = type.replace('_', '-');
    return `<span class="alert-type-badge ${cssClass}">${labels[type] || type}</span>`;
  }

  /**
   * Navigate to inventory page and open the specific stock record
   */
  function openStock(stockId) {
    if (!stockId) {
      window.location.href = '/inventory/';
      return;
    }

    // Check if we're already on the inventory page
    const currentPath = window.location.pathname;
    
    if (currentPath === '/inventory/' || currentPath === '/inventory') {
      // Already on inventory page - use the exposed function to search and expand
      closePanel();
      if (typeof window.expandStockById === 'function') {
        window.expandStockById(stockId);
      }
    } else {
      // Navigate to inventory page with stock_id parameter
      window.location.href = `/inventory/?expand_stock=${encodeURIComponent(stockId)}`;
    }
  }

  /**
   * Expose functions for external use
   */
  window.InventoryAlerts = {
    init: initAlerts,
    refresh: fetchAlerts,
    open: openPanel,
    close: closePanel,
    toggle: togglePanel,
    openStock: openStock
  };

  // Auto-initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAlerts);
  } else {
    // DOM already loaded, wait a bit for sidebar to load
    setTimeout(initAlerts, 500);
  }

})();
