// Permission Management
// Handles role-based UI restrictions across all pages

let currentUserRole = null;
let currentUser = null;

// Fetch current user information and role
async function fetchCurrentUser() {
  try {
    const response = await fetch('/api/auth/me/');
    
    if (response.ok) {
      currentUser = await response.json();
      currentUserRole = currentUser.role;
      return currentUser;
    } else if (response.status === 401) {
      // Not authenticated, redirect to login
      window.location.href = '/login/';
      return null;
    }
  } catch (error) {
    console.error('Error fetching current user:', error);
    return null;
  }
}

// Check if user has specific role
function hasRole(role) {
  if (currentUser?.is_superuser) return true;
  return currentUserRole === role;
}

// Check if user is Admin
function isAdmin() {
  return currentUser?.is_superuser || currentUserRole === 'Admin';
}

// Check if user is Staff or higher
function isStaff() {
  return currentUser?.is_superuser || ['Admin', 'Staff'].includes(currentUserRole);
}

// Check if user is Clerk or higher (basically any authenticated user)
function isClerk() {
  return currentUser?.is_superuser || ['Admin', 'Staff', 'Clerk'].includes(currentUserRole);
}

// Apply permissions to UI elements
function applyPermissions() {
  if (!currentUserRole) {
    console.warn('No user role found, redirecting to login');
    window.location.href = '/login/';
    return;
  }

  console.log('Applying permissions for role:', currentUserRole);

  // Hide settings tab for non-admin/staff users
  if (!isStaff()) {
    hideElement('.tab[data-tab="settings"]');
    hideElement('#settings-content');
    // Hide Orders tab for Clerk (preserve layout)
    preserveHide('.tab[data-tab="orders"]');
    hideElement('#orders-content');

    // Hide Manage Products button on the Product page for Clerk (remove completely)
    hideElement('#productslist_manageProductBtn');

    // Hide certain sidebar navigation labels for Clerk but keep icons/logos visible (preserve layout)
    preserveHide('button.nav-label[data-item="dashboard"]');
    preserveHide('button.nav-label[data-item="transactions"]');
    preserveHide('button.nav-label[data-item="settings"]');

    // Additionally hide and disable the sidebar icon buttons for Clerk
    try {
      const iconSelectors = ['dashboard', 'transactions', 'settings'];
      iconSelectors.forEach(name => {
        const icons = document.querySelectorAll(`.nav-icon[data-item="${name}"]`);
        icons.forEach(ic => {
          try { if ('disabled' in ic) ic.disabled = true; } catch (err) {}
          ic.style.opacity = '0';
          ic.style.pointerEvents = 'none';
          ic.setAttribute('aria-hidden', 'true');
          ic.setAttribute('tabindex', '-1');
          ic.setAttribute('title', 'Restricted');

          // hide inner icon element as well for extra safety
          const inner = ic.querySelector('i');
          if (inner) inner.style.display = 'none';

          if (!ic.dataset.permissionBlocked) {
            const blockHandler = function(e) {
              e.preventDefault();
              e.stopImmediatePropagation();
              e.stopPropagation();
              return false;
            };
            ic.addEventListener('click', blockHandler, true);
            ic.dataset.permissionBlocked = '1';
          }
        });
      });
    } catch (err) {
      // Non-fatal
      console.warn('Error hiding sidebar icons for Clerk', err);
    }
  }

  // Disable archive/unarchive buttons for non-admin users
  if (!isAdmin()) {
    disableArchiveButtons();
  }

  // Disable create/edit buttons for Clerk users
  if (!isStaff()) {
    disableCreateEditButtons();
  }

  // Apply specific page restrictions
  applyPageSpecificPermissions();
}

// Disable archive/unarchive buttons (Admin only)
function disableArchiveButtons() {
  const archiveButtons = document.querySelectorAll('.action-btn.archive-btn, .action-btn.unarchive-btn, .archive-btn, .unarchive-btn');
  archiveButtons.forEach(btn => {
    // Visual disable
    btn.classList.add('disabled-permission');
    btn.style.opacity = '0.5';
    btn.style.cursor = 'not-allowed';
    btn.setAttribute('title', 'Admin only');

    // For form controls (button/input) set the disabled property
    if ('disabled' in btn) {
      try { btn.disabled = true; } catch (err) { /* ignore */ }
    } else {
      // For anchors or other elements that don't support disabled
      btn.setAttribute('aria-disabled', 'true');
      btn.setAttribute('tabindex', '-1');
    }

    // Add a capture-phase listener to block any click handlers (prevents propagation)
    // Store a marker so we don't attach multiple handlers
    if (!btn.dataset.permissionBlocked) {
      const blockHandler = function(e) {
        e.preventDefault();
        e.stopImmediatePropagation();
        e.stopPropagation();
        try {
          // Non-intrusive notification; replace with a nicer UI toast if desired
          alert('You do not have permission to archive/unarchive records. Admin access required.');
        } catch (err) { /* ignore */ }
        return false;
      };

      btn.addEventListener('click', blockHandler, true);
      btn.dataset.permissionBlocked = '1';
    }
  });
}

// Disable create/edit buttons for Clerk users
function disableCreateEditButtons() {
  // EXCLUDE cart-related buttons: #addToCartBtn, #placeAllOrdersBtn
  const buttons = document.querySelectorAll(
    '#addSupplierBtn, #addProductBtn, #addCategoryBtn, #toggleCategoryForm, #toggleSubcategoryForm, ' +
    '.edit-btn, #saveSupplierBtn, #saveProductBtn, #addCategoryBtn, #addSubCategoryBtn, ' +
    '#updateSupplierEditBtn, #updateProductBtn, #updateCategoryEditBtn, #addOrderBtn, #confirmAddOrderBtn, #saveOrderBtn, .create-order-btn'
  );
  
  buttons.forEach(btn => {
    // Skip cart buttons
    if (btn.id === 'addToCartBtn' || btn.id === 'placeAllOrdersBtn') {
      return;
    }
    
    btn.disabled = true;
    btn.style.opacity = '0.5';
    btn.style.cursor = 'not-allowed';
    btn.title = 'Staff or Admin access required';
    
    btn.onclick = (e) => {
      e.preventDefault();
      e.stopPropagation();
      alert('You do not have permission to create or edit records. Staff or Admin access required.');
      return false;
    };
  });
}

// Page-specific permission restrictions
function applyPageSpecificPermissions() {
  const currentPath = window.location.pathname.toLowerCase();

  // Settings page - restrict access for Clerk
  if (currentPath.includes('settings') || currentPath.includes('system_settings')) {
    if (!isStaff()) {
      // Hide add buttons and forms
      hideElement('#addSupplierBtn');
      hideElement('#addProductBtn');
      hideElement('.form-section');
      hideElement('#categoryFormContainer');
      hideElement('#subcategoryFormContainer');
      hideElement('#toggleCategoryForm');
      hideElement('#toggleSubcategoryForm');
    }
  }

  // Inventory page - restrict stock adjustments for Clerk
  if (currentPath.includes('inventory')) {
    if (!isStaff()) {
      hideElement('.adjust-stock-btn');
      hideElement('#adjustStockBtn');
      
      // Disable stock adjustment inputs
      const inputs = document.querySelectorAll('input[type="number"]');
      inputs.forEach(input => {
        if (input.id.includes('adjust') || input.id.includes('quantity')) {
          input.disabled = true;
        }
      });
    }
  }

  // Orders page - restrict receiving for Clerk
  if (currentPath.includes('orders')) {
    if (!isStaff()) {
      // Disable receive buttons rather than hiding so layout remains consistent
      const receiveBtns = document.querySelectorAll('.receive-btn, #receiveOrderBtn, #bulkReceiveBtn');
      receiveBtns.forEach(btn => {
        try { if ('disabled' in btn) btn.disabled = true; } catch (err) { /* ignore */ }
        btn.style.opacity = '0.5';
        btn.style.cursor = 'not-allowed';
        btn.setAttribute('title', 'Staff or Admin access required');

        // For non-form elements
        if (!('disabled' in btn)) {
          btn.setAttribute('aria-disabled', 'true');
          btn.setAttribute('tabindex', '-1');
        }

        if (!btn.dataset.permissionBlocked) {
          const blockHandler = function(e) {
            e.preventDefault();
            e.stopImmediatePropagation();
            e.stopPropagation();
            try { alert('You do not have permission to receive orders. Staff or Admin access required.'); } catch (err) {}
            return false;
          };
          btn.addEventListener('click', blockHandler, true);
          btn.dataset.permissionBlocked = '1';
        }
      });

      // Disable create/add order buttons EXCEPT cart buttons
      const addOrderBtns = document.querySelectorAll('#addOrderBtn, .create-order-btn, #confirmAddOrderBtn');
      addOrderBtns.forEach(btn => {
        // Skip cart buttons
        if (btn.id === 'addToCartBtn' || btn.id === 'placeAllOrdersBtn') {
          return;
        }
        
        try { if ('disabled' in btn) btn.disabled = true; } catch (err) { /* ignore */ }
        btn.style.opacity = '0.5';
        btn.style.cursor = 'not-allowed';
        btn.setAttribute('title', 'Staff or Admin access required');
        if (!('disabled' in btn)) {
          btn.setAttribute('aria-disabled', 'true');
          btn.setAttribute('tabindex', '-1');
        }
        if (!btn.dataset.permissionBlocked) {
          const blockHandler = function(e) {
            e.preventDefault();
            e.stopImmediatePropagation();
            e.stopPropagation();
            try { alert('You do not have permission to create orders. Staff or Admin access required.'); } catch (err) {}
            return false;
          };
          btn.addEventListener('click', blockHandler, true);
          btn.dataset.permissionBlocked = '1';
        }
      });
    }
  }
}

// Helper function to hide elements
function hideElement(selector) {
  const elements = document.querySelectorAll(selector);
  elements.forEach(el => {
    if (el) {
      el.style.display = 'none';
    }
  });
}

// Helper to hide visually but preserve layout (used for sidebar labels/tabs)
function preserveHide(selector) {
  const elements = document.querySelectorAll(selector);
  elements.forEach(el => {
    if (el) {
      try { el.style.visibility = 'hidden'; } catch (err) {}
      try { el.style.pointerEvents = 'none'; } catch (err) {}
      try { el.setAttribute('aria-hidden', 'true'); } catch (err) {}
    }
  });
}

// Initialize permissions when DOM is ready
document.addEventListener('DOMContentLoaded', async function() {
  await fetchCurrentUser();
  
  if (currentUser) {
    // Wait a bit for the page to fully load before applying permissions
    setTimeout(applyPermissions, 200);
    
    // Also observe for dynamically added content
    observeDynamicContent();
  }
});

// Observe for dynamically added content and reapply permissions
function observeDynamicContent() {
  const observer = new MutationObserver((mutations) => {
    let shouldReapply = false;
    
    mutations.forEach((mutation) => {
      if (mutation.addedNodes.length > 0) {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === 1) { // Element node
            // Skip cart-related buttons
            if (node.id === 'addToCartBtn' || node.id === 'placeAllOrdersBtn' || 
                node.id === 'multipleOrdersList' || node.id === 'ordersCount') {
              return;
            }
            
            if (node.classList?.contains('archive-btn') || 
                node.classList?.contains('edit-btn') ||
                node.classList?.contains('unarchive-btn') ||
                node.tagName === 'BUTTON') {
              shouldReapply = true;
            } else {
              // If a container was added (e.g. a table row), check descendants for relevant buttons
              try {
                if (node.querySelector && node.querySelector('.archive-btn, .unarchive-btn, .edit-btn')) {
                  shouldReapply = true;
                }
              } catch (err) {
                // ignore selector errors on exotic nodes
              }
            }
          }
        });
      }
    });
    
    if (shouldReapply && currentUserRole) {
      applyPermissions();
    }
  });
  
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
}

// Export functions for use in other scripts
window.userPermissions = {
  isAdmin,
  isStaff,
  isClerk,
  hasRole,
  getCurrentUser: () => currentUser,
  getCurrentRole: () => currentUserRole,
  applyPermissions
};