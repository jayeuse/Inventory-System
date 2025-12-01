// Product management: load, render, add, edit, archive

document.addEventListener('DOMContentLoaded', function () {
  console.log('Product Management script loaded');
  
  // Initialize currency settings if available
  if (typeof initializeCurrency === 'function') {
    initializeCurrency();
  }
  
  let currentEditProductId = null;
  // caches for categories/subcategories so other handlers can reuse them
  let categoriesCache = [];
  let subcategoriesCache = [];

  // Pagination variables
  let allActiveProducts = [];
  let allArchivedProducts = [];
  let activeCurrentPage = 1;
  let archivedCurrentPage = 1;
  const recordsPerPage = 8;
  const truncateText = (text, maxLength = 30) => {
    if (!text) return '-';
    return text.length > maxLength ? `${text.slice(0, maxLength)}...` : text;
  };
  
  console.log('Checking for products-content:', document.getElementById('products-content'));
  console.log('Checking for product tabs:', document.querySelectorAll('.product-tab').length);

  // Scope queries to the products section to avoid ID collisions in the page
  const container = document.getElementById('products-content');
  if (!container) return; // nothing to do if products content isn't present

  const tableBody = container.querySelector('#tableBody');
  const archivedBody = container.querySelector('#archivedTableBody');
  // place to show archived count (we'll create element if missing)
  let archivedCountEl = container.querySelector('#archivedCount');
  const addProductModal = document.getElementById('addProductModal');
  const editProductModal = document.getElementById('editProductModal');
  const archiveModal = document.getElementById('archiveModal');
  const unarchiveModal = document.getElementById('unarchiveModal');

  // Fetch and render products (UPDATED)
  async function loadProductsList() {
    try {
      const [activeRes, archivedRes] = await Promise.all([
        fetch('/api/products/'),
        fetch('/api/products/?show_archived=true')
      ]);

      if (!activeRes.ok) throw new Error('Failed to fetch active products');
      if (!archivedRes.ok) throw new Error('Failed to fetch archived products');

      const activeData = await activeRes.json();
      const archivedData = await archivedRes.json();

      allActiveProducts = Array.isArray(activeData) ? activeData : (activeData.results || []);
      allArchivedProducts = Array.isArray(archivedData) ? archivedData : (archivedData.results || []);

      // Reset to page 1
      activeCurrentPage = 1;
      archivedCurrentPage = 1;

      // Display products with pagination
      displayActiveProducts();
      displayArchivedProducts();

      console.debug('loadProductsList: activeProducts count=', allActiveProducts.length, 'archivedProducts count=', allArchivedProducts.length);

      // Update counts
      let activeCountEl = container.querySelector('#activeCount');
      if (!activeCountEl) {
        const activeTabHeader = document.querySelector('.product-tab[data-product-tab="active"]');
        if (activeTabHeader) {
          activeCountEl = document.createElement('span');
          activeCountEl.id = 'activeCount';
          activeCountEl.style.marginLeft = '8px';
          activeCountEl.style.fontSize = '0.9em';
          activeTabHeader.appendChild(activeCountEl);
        }
      }

      let archivedCountEl = container.querySelector('#archivedCount');
      if (!archivedCountEl) {
        const archivedTabHeader = document.querySelector('.product-tab[data-product-tab="archived"]');
        if (archivedTabHeader) {
          archivedCountEl = document.createElement('span');
          archivedCountEl.id = 'archivedCount';
          archivedCountEl.style.marginLeft = '8px';
          archivedCountEl.style.fontSize = '0.9em';
          archivedTabHeader.appendChild(archivedCountEl);
        }
      }

      if (activeCountEl) activeCountEl.textContent = `(${allActiveProducts.length})`;
      if (archivedCountEl) archivedCountEl.textContent = `(${allArchivedProducts.length})`;

    } catch (err) {
      console.error('Error loading products:', err);
      if (tableBody) tableBody.innerHTML = '<tr><td colspan="10">Error loading products.</td></tr>';
    }
  }

  // Display active products with pagination
  function displayActiveProducts() {
    const searchTerm = document.getElementById('activeSearchInput')?.value.trim().toLowerCase() || '';
    const categoryFilter = document.getElementById('categoryFilter')?.value || 'all';

    // Filter products
    let filteredProducts = allActiveProducts.filter(product => {
      const matchesSearch = 
        (product.product_id || '').toLowerCase().includes(searchTerm) ||
        (product.brand_name || '').toLowerCase().includes(searchTerm) ||
        (product.generic_name || '').toLowerCase().includes(searchTerm);
      
      const matchesCategory = categoryFilter === 'all' || (product.category_name || '').toLowerCase() === categoryFilter.toLowerCase();

      return matchesSearch && matchesCategory;
    });

    // Calculate pagination
    const totalPages = Math.ceil(filteredProducts.length / recordsPerPage);
    const startIndex = (activeCurrentPage - 1) * recordsPerPage;
    const endIndex = startIndex + recordsPerPage;
    const paginatedProducts = filteredProducts.slice(startIndex, endIndex);

    // Populate table
    if (!tableBody) return;
    tableBody.innerHTML = '';

    if (filteredProducts.length === 0) {
      // Show "No products found" message
      const tr = document.createElement('tr');
      tr.innerHTML = '<td colspan="10" style="text-align: center; padding: 40px; color: var(--muted);">No products found.</td>';
      tableBody.appendChild(tr);
    } else {
      // Fill with actual data or placeholders to maintain 6 rows
      for (let i = 0; i < recordsPerPage; i++) {
        const row = document.createElement('tr');
        
        if (i < paginatedProducts.length) {
          // Actual product data
          const p = paginatedProducts[i];
          row.dataset.categoryName = p.category_name || '';
          const unitPriceDisplay = (p.price_per_unit !== undefined && p.price_per_unit !== null) 
            ? (typeof formatCurrency === 'function' ? formatCurrency(p.price_per_unit) : '₱' + Number(p.price_per_unit).toFixed(2))
            : '';
          
          row.innerHTML = `
            <td>${p.product_id || ''}</td>
            <td class="truncate-cell truncate-200" title="${p.brand_name || ''}">${truncateText(p.brand_name, 32)}</td>
            <td class="truncate-cell truncate-200" title="${p.generic_name || ''}">${truncateText(p.generic_name, 32)}</td>
            <td class="truncate-cell truncate-160" title="${p.category_name || ''}">${truncateText(p.category_name, 24)}</td>
            <td class="truncate-cell truncate-160" title="${p.subcategory_name || ''}">${truncateText(p.subcategory_name, 24)}</td>
            <td>${unitPriceDisplay} / ${p.unit_of_measurement || ''}</td>
            <td>${p.low_stock_threshold || ''} units</td>
            <td>${p.expiry_threshold_days || ''} days</td>
            <td class="last-update-cell" title="${p.last_updated || ''}">${truncateText(p.last_updated)}</td>
            <td class="actions-cell">
              <div class="op-buttons">
                <button class="action-btn edit-btn"><i class="bi bi-pencil"></i> Edit</button>
                <button class="action-btn archive-btn"><i class="fas fa-archive"></i> Archive</button>
              </div>
            </td>
          `;

            // Helper to populate edit modal
            const populateEditModal = (product) => {
              currentEditProductId = product.product_id || product.productId || null;
              const setIf = (selector, value) => {
                const el = document.querySelector(selector);
                if (el) el.value = value ?? '';
              };
              setIf('#editBrandName', product.brand_name || '');
              setIf('#editGenericName', product.generic_name || '');
              setIf('#editPrice', product.price_per_unit ?? '');
              setIf('#editUnitOfMeasurement', product.unit_of_measurement || '');
              setIf('#editLowStockThreshold', product.low_stock_threshold ?? '');
              setIf('#editExpiryThreshold', product.expiry_threshold_days ?? '');
              setIf('#editNotificationRecipient', product.notification_recipient || '');

              const editCategory = document.getElementById('editCategory');
              const editSubcategory = document.getElementById('editSubcategory');
              const categoryVal = product.category_id || product.category || '';
              const subcategoryVal = product.subcategory_id || product.subcategory || '';

              if (editCategory) {
                editCategory.value = categoryVal;
                populateSubSelectForCategory(editSubcategory, categoryVal);
              }

              if (editSubcategory) {
                if (!categoryVal) editSubcategory.innerHTML = '<option value="">Select Subcategory</option>';
                editSubcategory.value = subcategoryVal;
              }

              if (editProductModal) editProductModal.style.display = 'flex';
            };

          row.querySelector('.edit-btn')?.addEventListener('click', () => populateEditModal(p));
          row.querySelector('.archive-btn')?.addEventListener('click', function () {
            const id = p.product_id || p.productId || null;
            if (!id) return alert('Product id missing');
            if (!archiveModal) return alert('Archive modal not found');
            archiveModal.dataset.targetApi = `/api/products/${id}/`;
            archiveModal.dataset.targetAction = 'archive';
            archiveModal.style.display = 'flex';
          });
        } else {
          // Empty placeholder row (mirrors structure for consistent height)
          row.classList.add('placeholder-row');
          row.innerHTML = `
            <td class="placeholder-value">-</td>
            <td class="truncate-cell truncate-200 placeholder-value">-</td>
            <td class="truncate-cell truncate-200 placeholder-value">-</td>
            <td class="truncate-cell truncate-160 placeholder-value">-</td>
            <td class="truncate-cell truncate-160 placeholder-value">-</td>
            <td class="placeholder-value">-</td>
            <td class="placeholder-value">-</td>
            <td class="placeholder-value">-</td>
            <td class="last-update-cell placeholder-value">-</td>
            <td class="actions-cell">
              <div class="op-buttons placeholder-buttons">
                <span>-</span>
              </div>
            </td>
          `;
        }
        
        tableBody.appendChild(row);
      }
    }

    // Update pagination buttons
    updatePaginationButtons(activeCurrentPage, totalPages, false);
    // Reapply frontend permissions (disable/archive buttons) after rendering rows
    if (window.userPermissions && typeof window.userPermissions.applyPermissions === 'function') {
      try { window.userPermissions.applyPermissions(); } catch (err) { console.error('Error applying user permissions:', err); }
    }
  }

  // Display archived products with pagination
  function displayArchivedProducts() {
    const searchTerm = document.getElementById('archivedSearchInput')?.value.trim().toLowerCase() || '';
    const categoryFilter = document.getElementById('archivedCategoryFilter')?.value || 'all';

    // Filter products
    let filteredProducts = allArchivedProducts.filter(product => {
      const matchesSearch = 
        (product.product_id || '').toLowerCase().includes(searchTerm) ||
        (product.brand_name || '').toLowerCase().includes(searchTerm) ||
        (product.generic_name || '').toLowerCase().includes(searchTerm);
      
      const matchesCategory = categoryFilter === 'all' || (product.category_name || '').toLowerCase() === categoryFilter.toLowerCase();

      return matchesSearch && matchesCategory;
    });

    // Calculate pagination
    const totalPages = Math.ceil(filteredProducts.length / recordsPerPage);
    const startIndex = (archivedCurrentPage - 1) * recordsPerPage;
    const endIndex = startIndex + recordsPerPage;
    const paginatedProducts = filteredProducts.slice(startIndex, endIndex);

    // Populate table
    if (!archivedBody) return;
    archivedBody.innerHTML = '';

    if (filteredProducts.length === 0) {
      const tr = document.createElement('tr');
      tr.innerHTML = '<td colspan="9" style="text-align: center; padding: 40px; color: var(--muted);">No archived products found.</td>';
      archivedBody.appendChild(tr);
    } else {
      // Fill with actual data or placeholders to maintain 6 rows
      for (let i = 0; i < recordsPerPage; i++) {
        const row = document.createElement('tr');
        
        if (i < paginatedProducts.length) {
          // Actual product data
          const p = paginatedProducts[i];
          row.dataset.categoryName = p.category_name || '';
          const unitPriceDisplay = (p.price_per_unit !== undefined && p.price_per_unit !== null) 
            ? (typeof formatCurrency === 'function' ? formatCurrency(p.price_per_unit) : '₱' + Number(p.price_per_unit).toFixed(2))
            : '';
          const archiveReason = p.archive_reason || p.reason || '';
          const archivedDate = p.archived_at || p.archived_date || p.updated_at || p.date_archived || '';

          row.innerHTML = `
            <td>${p.product_id || ''}</td>
            <td class="truncate-cell truncate-200" title="${p.brand_name || ''}">${truncateText(p.brand_name, 32)}</td>
            <td class="truncate-cell truncate-200" title="${p.generic_name || ''}">${truncateText(p.generic_name, 32)}</td>
            <td class="truncate-cell truncate-160" title="${p.category_name || ''}">${truncateText(p.category_name, 24)}</td>
            <td class="truncate-cell truncate-160" title="${p.subcategory_name || ''}">${truncateText(p.subcategory_name, 24)}</td>
            <td>${unitPriceDisplay} / ${p.unit_of_measurement || ''}</td>
            <td class="truncate-cell truncate-200" title="${archiveReason}">${truncateText(archiveReason, 28)}</td>
            <td class="truncate-cell truncate-140" title="${archivedDate}">${truncateText(archivedDate, 22)}</td>
            <td class="actions-cell">
              <div class="op-buttons">
                <button class="action-btn edit-btn"><i class="bi bi-pencil"></i> Edit</button>
                <button class="action-btn unarchive-btn"><i class="fas fa-box-open"></i> Unarchive</button>
              </div>
            </td>
          `;

            const populateEditModal = (product) => {
              currentEditProductId = product.product_id || product.productId || null;
              const setIf = (selector, value) => {
                const el = document.querySelector(selector);
                if (el) el.value = value ?? '';
              };
              setIf('#editBrandName', product.brand_name || '');
              setIf('#editGenericName', product.generic_name || '');
              setIf('#editPrice', product.price_per_unit ?? '');
              setIf('#editUnitOfMeasurement', product.unit_of_measurement || '');
              setIf('#editLowStockThreshold', product.low_stock_threshold ?? '');
              setIf('#editExpiryThreshold', product.expiry_threshold_days ?? '');
              setIf('#editNotificationRecipient', product.notification_recipient || '');

              const editCategory = document.getElementById('editCategory');
              const editSubcategory = document.getElementById('editSubcategory');
              const categoryVal = product.category_id || product.category || '';
              const subcategoryVal = product.subcategory_id || product.subcategory || '';

              if (editCategory) {
                editCategory.value = categoryVal;
                populateSubSelectForCategory(editSubcategory, categoryVal);
              }

              if (editSubcategory) {
                if (!categoryVal) editSubcategory.innerHTML = '<option value="">Select Subcategory</option>';
                editSubcategory.value = subcategoryVal;
              }

              if (editProductModal) editProductModal.style.display = 'flex';
            };

          row.querySelector('.edit-btn')?.addEventListener('click', () => populateEditModal(p));
          row.querySelector('.unarchive-btn')?.addEventListener('click', function () {
            const id = p.product_id || p.productId || null;
            if (!id) return alert('Product id missing');
            if (!unarchiveModal) return alert('Unarchive modal not found');
            unarchiveModal.dataset.targetApi = `/api/products/unarchive/?id=${id}`;
            unarchiveModal.style.display = 'flex';
          });
        } else {
          // Empty placeholder row
          row.classList.add('placeholder-row');
          row.innerHTML = `
            <td class="placeholder-value">-</td>
            <td class="truncate-cell truncate-200 placeholder-value">-</td>
            <td class="truncate-cell truncate-200 placeholder-value">-</td>
            <td class="truncate-cell truncate-160 placeholder-value">-</td>
            <td class="truncate-cell truncate-160 placeholder-value">-</td>
            <td class="placeholder-value">-</td>
            <td class="truncate-cell truncate-200 placeholder-value">-</td>
            <td class="truncate-cell truncate-140 placeholder-value">-</td>
            <td class="actions-cell">
              <div class="op-buttons placeholder-buttons">
                <span>-</span>
              </div>
            </td>
          `;
        }
        
        archivedBody.appendChild(row);
      }
    }

    // Update pagination buttons
    updatePaginationButtons(archivedCurrentPage, totalPages, true);
    // Reapply frontend permissions (disable/archive buttons) after rendering archived rows
    if (window.userPermissions && typeof window.userPermissions.applyPermissions === 'function') {
      try { window.userPermissions.applyPermissions(); } catch (err) { console.error('Error applying user permissions:', err); }
    }
  }

  // Update pagination buttons
  function updatePaginationButtons(current, total, isArchived) {
    const paginationContainer = isArchived 
      ? document.querySelector('#archivedProductsContent .pagination')
      : document.querySelector('#activeProductsContent .pagination');
    
    if (!paginationContainer) return;

    const prevBtn = paginationContainer.querySelector('.pagination-btn:first-child');
    const nextBtn = paginationContainer.querySelector('.pagination-btn:last-child');

    if (prevBtn && nextBtn) {
      prevBtn.disabled = current === 1;
      nextBtn.disabled = current === total || total === 0;

      prevBtn.style.opacity = current === 1 ? '0.5' : '1';
      nextBtn.style.opacity = (current === total || total === 0) ? '0.5' : '1';
      prevBtn.style.cursor = current === 1 ? 'not-allowed' : 'pointer';
      nextBtn.style.cursor = (current === total || total === 0) ? 'not-allowed' : 'pointer';
    }
  }

  // Pagination event listeners for active products
  const activePaginationContainer = document.querySelector('#activeProductsContent .pagination');
  if (activePaginationContainer) {
    const prevBtn = activePaginationContainer.querySelector('.pagination-btn:first-child');
    const nextBtn = activePaginationContainer.querySelector('.pagination-btn:last-child');

    if (prevBtn) {
      prevBtn.addEventListener('click', function() {
        if (activeCurrentPage > 1) {
          activeCurrentPage--;
          displayActiveProducts();
        }
      });
    }

    if (nextBtn) {
      nextBtn.addEventListener('click', function() {
        const searchTerm = document.getElementById('activeSearchInput')?.value.trim().toLowerCase() || '';
        const categoryFilter = document.getElementById('categoryFilter')?.value || 'all';
        
        let filteredProducts = allActiveProducts.filter(product => {
          const matchesSearch = 
            (product.product_id || '').toLowerCase().includes(searchTerm) ||
            (product.brand_name || '').toLowerCase().includes(searchTerm) ||
            (product.generic_name || '').toLowerCase().includes(searchTerm);
          
          const matchesCategory = categoryFilter === 'all' || (product.category_name || '').toLowerCase() === categoryFilter.toLowerCase();

          return matchesSearch && matchesCategory;
        });

        const totalPages = Math.ceil(filteredProducts.length / recordsPerPage);
        if (activeCurrentPage < totalPages) {
          activeCurrentPage++;
          displayActiveProducts();
        }
      });
    }
  }

  // Pagination event listeners for archived products
  const archivedPaginationContainer = document.querySelector('#archivedProductsContent .pagination');
  if (archivedPaginationContainer) {
    const prevBtn = archivedPaginationContainer.querySelector('.pagination-btn:first-child');
    const nextBtn = archivedPaginationContainer.querySelector('.pagination-btn:last-child');

    if (prevBtn) {
      prevBtn.addEventListener('click', function() {
        if (archivedCurrentPage > 1) {
          archivedCurrentPage--;
          displayArchivedProducts();
        }
      });
    }

    if (nextBtn) {
      nextBtn.addEventListener('click', function() {
        const searchTerm = document.getElementById('archivedSearchInput')?.value.trim().toLowerCase() || '';
        const categoryFilter = document.getElementById('archivedCategoryFilter')?.value || 'all';
        
        let filteredProducts = allArchivedProducts.filter(product => {
          const matchesSearch = 
            (product.product_id || '').toLowerCase().includes(searchTerm) ||
            (product.brand_name || '').toLowerCase().includes(searchTerm) ||
            (product.generic_name || '').toLowerCase().includes(searchTerm);
          
          const matchesCategory = categoryFilter === 'all' || (product.category_name || '').toLowerCase() === categoryFilter.toLowerCase();

          return matchesSearch && matchesCategory;
        });

        const totalPages = Math.ceil(filteredProducts.length / recordsPerPage);
        if (archivedCurrentPage < totalPages) {
          archivedCurrentPage++;
          displayArchivedProducts();
        }
      });
    }
  }

  // Populate category and subcategory selects
  async function populateProductDropdowns() {
    try {
      const [catsRes, subsRes] = await Promise.all([
        fetch('/api/categories/'),
        fetch('/api/subcategories/')
      ]);
      if (!catsRes.ok || !subsRes.ok) throw new Error('Failed to load categories/subcategories');
      const cats = await catsRes.json();
      const subs = await subsRes.json();

      // normalize caches to arrays
      categoriesCache = Array.isArray(cats) ? cats : (cats.results || []);
      subcategoriesCache = Array.isArray(subs) ? subs : (subs.results || []);

  const catSelects = [document.getElementById('category'), document.getElementById('editCategory')];
  const catFilterSelects = [document.getElementById('categoryFilter'), document.getElementById('archivedCategoryFilter')];
  const subSelects = [document.getElementById('subcategory'), document.getElementById('editSubcategory')];

      // Populate add/edit category selects (values = ids) and filter selects (values = names)
      catSelects.forEach(sel => {
        if (!sel) return;
        sel.innerHTML = '<option value="">Select Category</option>';
        categoriesCache.forEach(c => {
          const opt = document.createElement('option');
          opt.value = c.category_id || c.categoryId || c.id || c.category_name;
          opt.textContent = c.category_name || opt.value;
          sel.appendChild(opt);
        });

        sel.addEventListener('change', function () {
          const selected = this.value;
          subSelects.forEach(ss => {
            if (!ss) return;
            ss.innerHTML = '<option value="">Select Subcategory</option>';
            const filtered = subcategoriesCache.filter(s => ((s.category || s.category_id || '').toString() === selected.toString()));
            filtered.forEach(s => {
              const o = document.createElement('option');
              o.value = s.subcategory_id || s.subcategoryId || s.id || s.subcategory_name;
              o.textContent = s.subcategory_name || o.value;
              ss.appendChild(o);
            });
          });
        });
      });

      // Populate filter selects (use category_name as value for easy matching)
      catFilterSelects.forEach(sel => {
        if (!sel) return;
        sel.innerHTML = '<option value="all">Filter by Category</option>';
        categoriesCache.forEach(c => {
          const opt = document.createElement('option');
          opt.value = c.category_name || (c.category_id || c.categoryId || c.id);
          opt.textContent = c.category_name || opt.value;
          sel.appendChild(opt);
        });

        // add change handler to filter rows in the appropriate table
        sel.addEventListener('change', function () {
          // When category changes, reapply all filters
          if (this.id === 'categoryFilter') {
            applyCurrentFilters(tableBody, activeSearchInput);
          } else if (this.id === 'archivedCategoryFilter') {
            applyCurrentFilters(archivedBody, archivedSearchInput);
          }
        });
      });

      // initialize subcategory lists empty
      subSelects.forEach(ss => { if (ss) ss.innerHTML = '<option value="">Select Subcategory</option>'; });

    } catch (err) {
      console.error('Error populating product dropdowns:', err);
    }
  }

  // Helper to populate a single subcategory select based on a category value
  function populateSubSelectForCategory(targetSelect, categoryValue) {
    if (!targetSelect) return;
    targetSelect.innerHTML = '<option value="">Select Subcategory</option>';
    if (!categoryValue) return;
    const filtered = subcategoriesCache.filter(s => ((s.category || s.category_id || '').toString() === categoryValue.toString()));
    filtered.forEach(s => {
      const o = document.createElement('option');
      o.value = s.subcategory_id || s.subcategoryId || s.id || s.subcategory_name;
      o.textContent = s.subcategory_name || o.value;
      targetSelect.appendChild(o);
    });
  }

  // Initialize product status tabs and their click handlers
  function initializeProductTabs() {
    try {
      console.log('Initializing product tabs...');
      const productTabs = document.querySelectorAll('.product-tab');
      const productTabContents = document.querySelectorAll('.product-tab-content');
      
      console.log('Found product tabs:', productTabs.length);
      console.log('Found tab contents:', productTabContents.length);

      productTabs.forEach((tab) => {
        console.log('Setting up tab:', tab.getAttribute('data-product-tab'));
        tab.addEventListener('click', async function () {
          const tabId = this.getAttribute('data-product-tab');
          console.log('Product tab clicked:', tabId);

          // Remove active class from all tabs and contents
          productTabs.forEach((t) => t.classList.remove('active'));
          productTabContents.forEach((c) => c.classList.remove('active'));

          // Add active class to clicked tab and corresponding content
          this.classList.add('active');
          const contentEl = document.getElementById(tabId === 'active' ? 'activeProductsContent' : 'archivedProductsContent');
          if (contentEl) contentEl.classList.add('active');

          // If switching to archived, refresh archived data
          if (tabId === 'archived') {
            console.log('Switching to archived tab: refreshing archived products');
            if (archivedBody) archivedBody.innerHTML = '<tr><td colspan="9">Loading archived products...</td></tr>';
            try {
              await loadProductsList();
            } catch (err) {
              console.error('Error refreshing archived products on tab switch', err);
              if (archivedBody) archivedBody.innerHTML = '<tr><td colspan="9">Error loading archived products.</td></tr>';
            }
          }
        });
      });
    } catch (err) {
      console.error('Error initializing product tabs', err);
    }
  }

  // Add product
  const saveBtn = document.getElementById('saveProductBtn');
  saveBtn?.addEventListener('click', async function () {
    try {
      const data = {
        brand_name: document.getElementById('brandName')?.value.trim(),
        generic_name: document.getElementById('genericName')?.value.trim(),
        category: document.getElementById('category')?.value || null,
        subcategory: document.getElementById('subcategory')?.value || null,
        price_per_unit: parseFloat(document.getElementById('price')?.value) || 0,
        unit_of_measurement: document.getElementById('unitOfMeasurement')?.value.trim() || '',
        low_stock_threshold: parseInt(document.getElementById('lowStockThreshold')?.value) || 0,
        expiry_threshold_days: parseInt(document.getElementById('expiryThreshold')?.value) || 0,
      };

      const res = await fetch('/api/products/', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify(data)
      });

      if (res.ok) {
        alert('Product added successfully');
        if (addProductModal) addProductModal.style.display = 'none';
        await loadProductsList();
        // Refresh Supplier Management product dropdowns
        if (typeof window.populateSupplierProductDropdown === 'function') {
          await window.populateSupplierProductDropdown();
        }
      } else {
        const err = await res.json();
        alert('Error saving product: ' + JSON.stringify(err));
      }
    } catch (err) {
      alert('Network error: ' + err);
    }
  });

  // Update product
  const updateBtn = document.getElementById('updateProductBtn');
  updateBtn?.addEventListener('click', async function () {
    if (!currentEditProductId) return alert('No product selected');
    try {
      const data = {
        brand_name: document.getElementById('editBrandName')?.value.trim(),
        generic_name: document.getElementById('editGenericName')?.value.trim(),
        category: document.getElementById('editCategory')?.value || null,
        subcategory: document.getElementById('editSubcategory')?.value || null,
        price_per_unit: parseFloat(document.getElementById('editPrice')?.value) || 0,
        unit_of_measurement: document.getElementById('editUnitOfMeasurement')?.value.trim() || '',
        low_stock_threshold: parseInt(document.getElementById('editLowStockThreshold')?.value) || 0,
        expiry_threshold_days: parseInt(document.getElementById('editExpiryThreshold')?.value) || 0,
      };

      const res = await fetch(`/api/products/${currentEditProductId}/`, {
        method: 'PATCH',
        headers: { 
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify(data)
      });

      if (res.ok) {
        alert('Product updated successfully');
        if (editProductModal) editProductModal.style.display = 'none';
        currentEditProductId = null;
        await loadProductsList();
      } else {
        const err = await res.json();
        alert('Error updating product: ' + JSON.stringify(err));
      }
    } catch (err) {
      alert('Network error: ' + err);
    }
  });

  // Confirm archive button handling (shared archive modal in page)
  const confirmArchiveBtn = document.getElementById('confirmArchiveBtn');
  confirmArchiveBtn?.addEventListener('click', async function () {
    if (!archiveModal) return;
    const apiUrl = archiveModal.dataset.targetApi;
    if (!apiUrl) return alert('No archive target');

    const archiveReason = document.getElementById('archiveReason')?.value.trim();
    if (!archiveReason) {
      alert('Please provide a reason for archiving');
      return;
    }

    archiveModal.style.display = 'none';

    try {
      const response = await fetch(apiUrl, {
        method: 'PATCH',
        headers: { 
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({ 
          status: 'Archived',
          archive_reason: archiveReason
        })
      });

      if (response.ok) {
        alert('Record archived!');
        await loadProductsList();
        // Clear the archive reason field after successful archive
        const archiveReasonField = document.getElementById('archiveReason');
        if (archiveReasonField) archiveReasonField.value = '';
      } else {
        const errorData = await response.json();
        alert('Error: ' + JSON.stringify(errorData))
      }
    } catch (error) {
      alert('Network error: ' + error);
    }

    delete archiveModal.dataset.targetApi;
  });

  // Cancel archive
  document.getElementById('cancelArchiveBtn')?.addEventListener('click', function () {
    if (archiveModal) {
      archiveModal.style.display = 'none';
      delete archiveModal.dataset.targetApi;
      // Clear the archive reason field
      const archiveReasonField = document.getElementById('archiveReason');
      if (archiveReasonField) archiveReasonField.value = '';
    }
  });

  // Confirm unarchive button handling (shared unarchive modal in page)
  const confirmUnarchiveBtn = document.getElementById('confirmUnarchiveBtn');
  confirmUnarchiveBtn?.addEventListener('click', async function () {
    if (!unarchiveModal) return;
    const apiUrl = unarchiveModal.dataset.targetApi;
    console.log('Unarchiving product with URL:', apiUrl);
    if (!apiUrl) return alert('No unarchive target');

    try {
      console.log('Sending unarchive request to:', apiUrl);
      const response = await fetch(apiUrl, {
        method: 'POST',  // Changed to POST since we're targeting the list endpoint
        headers: { 
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({ action: 'unarchive' })
      });

      if (response.ok) {
        unarchiveModal.style.display = 'none';  // Close modal after successful response
        alert('Record unarchived!');
        await loadProductsList();
      } else {
        const errorData = await response.json();
        console.error('Unarchive error:', errorData);
        alert('Failed to unarchive record: ' + JSON.stringify(errorData));
      }
    } catch (error) {
      alert('Network error: ' + error);
    }

    delete unarchiveModal.dataset.targetApi;
  });

  // Cancel unarchive
  document.getElementById('cancelUnarchiveBtn')?.addEventListener('click', function () {
    if (unarchiveModal) unarchiveModal.style.display = 'none';
    if (unarchiveModal) delete unarchiveModal.dataset.targetApi;
  });

  // Search functionality
  let activeSearchTimeout = null;
  let archivedSearchTimeout = null;
  const activeSearchInput = document.getElementById('activeSearchInput');
  const archivedSearchInput = document.getElementById('archivedSearchInput');

  // Helper function to reapply all current filters
  function applyCurrentFilters(targetTableBody, searchInput) {
    const searchQuery = searchInput ? searchInput.value.trim().toLowerCase() : '';
    filterProducts(targetTableBody, searchQuery);
  }

  // Update search event listeners to reset to page 1 and redisplay
  if (activeSearchInput) {
    activeSearchInput.addEventListener('input', function() {
      clearTimeout(activeSearchTimeout);
      activeSearchTimeout = setTimeout(() => {
        activeCurrentPage = 1;
        displayActiveProducts();
      }, 300);
    });
  }

  if (archivedSearchInput) {
    archivedSearchInput.addEventListener('input', function() {
      clearTimeout(archivedSearchTimeout);
      archivedSearchTimeout = setTimeout(() => {
        archivedCurrentPage = 1;
        displayArchivedProducts();
      }, 300);
    });
  }

  // Update category filter listeners
  const categoryFilterEl = document.getElementById('categoryFilter');
  const archivedCategoryFilterEl = document.getElementById('archivedCategoryFilter');

  if (categoryFilterEl) {
    categoryFilterEl.addEventListener('change', function() {
      activeCurrentPage = 1;
      displayActiveProducts();
    });
  }

  if (archivedCategoryFilterEl) {
    archivedCategoryFilterEl.addEventListener('change', function() {
      archivedCurrentPage = 1;
      displayArchivedProducts();
    });
  }

  // Initialize
  (async function init() {
    console.log('Initializing Product Management page');
    // Ensure both tab contents show loading messages so users see feedback immediately
    if (tableBody) tableBody.innerHTML = '<tr><td colspan="10">Loading products...</td></tr>';
    if (archivedBody) archivedBody.innerHTML = '<tr><td colspan="9">Loading archived products...</td></tr>';

    // Wire up tabs before loading data so clicks work immediately
    initializeProductTabs();

    await populateProductDropdowns();
    await loadProductsList();
  })();

  // Listen for currency changes to refresh the display
  window.addEventListener('currencyChanged', function() {
    loadProductsList();
  });

  // Expose loader so other scripts (or manual triggers) can refresh lists
  window.loadProductsList = loadProductsList;

  // Expose dropdown refresh function so Category Management can refresh dropdowns after adding categories/subcategories
  window.populateProductDropdowns = populateProductDropdowns;

  // Tab switching is handled by initializeProductTabs() above

});
