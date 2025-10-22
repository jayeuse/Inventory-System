// Product management: load, render, add, edit, archive

document.addEventListener('DOMContentLoaded', function () {
  console.log('Product Management script loaded');
  let currentEditProductId = null;
  // caches for categories/subcategories so other handlers can reuse them
  let categoriesCache = [];
  let subcategoriesCache = [];
  
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

  // Fetch and render products
  async function loadProductsList() {
    try {
      // Fetch active (default) and archived lists in parallel
      const [activeRes, archivedRes] = await Promise.all([
        fetch('/api/products/'),
        fetch('/api/products/?show_archived=true')
      ]);

      if (!activeRes.ok) throw new Error('Failed to fetch active products');
      if (!archivedRes.ok) throw new Error('Failed to fetch archived products');

      const activeData = await activeRes.json();
      const archivedData = await archivedRes.json();

      const activeProducts = Array.isArray(activeData) ? activeData : (activeData.results || []);
      const archivedProducts = Array.isArray(archivedData) ? archivedData : (archivedData.results || []);

      if (tableBody) tableBody.innerHTML = '';
      if (archivedBody) archivedBody.innerHTML = '';
      
      console.log('Active products:', activeProducts);
      console.log('Archived products:', archivedProducts);
      // Log product IDs specifically
      console.log('Archived Product IDs:', archivedProducts.map(p => p.product_id));
      console.debug('loadProductsList: activeProducts count=', activeProducts.length, 'archivedProducts count=', archivedProducts.length);
      console.debug('archivedBody element found:', !!archivedBody);

      // Add active products counter
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

      // Ensure archived count element exists in the archived tab header area
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

      if (activeCountEl) activeCountEl.textContent = `(${activeProducts.length})`;
      if (archivedCountEl) archivedCountEl.textContent = `(${archivedProducts.length})`;

      // Helper to populate edit modal
      const populateEditModal = (p) => {
        currentEditProductId = p.product_id || p.productId || null;
        const setIf = (selector, value) => {
          const el = document.querySelector(selector);
          if (el) el.value = value ?? '';
        };
        setIf('#editBrandName', p.brand_name || '');
        setIf('#editGenericName', p.generic_name || '');
        setIf('#editPrice', p.price_per_unit ?? '');
        setIf('#editUnitOfMeasurement', p.unit_of_measurement || '');
        setIf('#editLowStockThreshold', p.low_stock_threshold ?? '');
        setIf('#editExpiryThreshold', p.expiry_threshold_days ?? '');
        setIf('#editNotificationRecipient', p.notification_recipient || '');

        const editCategory = document.getElementById('editCategory');
        const editSubcategory = document.getElementById('editSubcategory');
        const categoryVal = p.category_id || p.category || '';
        const subcategoryVal = p.subcategory_id || p.subcategory || '';

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

      // Render active products
      activeProducts.forEach(p => {
  const row = document.createElement('tr');
  row.dataset.categoryName = p.category_name || '';
        row.innerHTML = `
          <td>${p.product_id || ''}</td>
          <td>${p.brand_name || ''}</td>
          <td>${p.generic_name || ''}</td>
          <td>${p.category_name || ''}</td>
          <td>${p.subcategory_name || ''}</td>
          <td>₱${(p.price_per_unit !== undefined && p.price_per_unit !== null) ? Number(p.price_per_unit).toFixed(2) : ''} / ${p.unit_of_measurement || ''}</td>
          <td>${p.low_stock_threshold || ''} units</td>
          <td>${p.expiry_threshold_days || ''} days</td>
          <td>-</td>
          <td>
            <div class="op-buttons">
              <button class="action-btn edit-btn"><i class="bi bi-pencil"></i> Edit</button>
              <button class="action-btn archive-btn"><i class="fas fa-archive"></i> Archive</button>
            </div>
          </td>
        `;

        row.querySelector('.edit-btn')?.addEventListener('click', () => populateEditModal(p));

        row.querySelector('.archive-btn')?.addEventListener('click', function () {
          const id = p.product_id || p.productId || null;
          if (!id) return alert('Product id missing');
          if (!archiveModal) return alert('Archive modal not found');
          archiveModal.dataset.targetApi = `/api/products/${id}/`;
          archiveModal.dataset.targetAction = 'archive';
          archiveModal.style.display = 'flex';
        });

        tableBody?.appendChild(row);
      });

      // Render archived products (match archived table's 9 columns)
      console.log('Starting to render archived products...');
      archivedProducts.forEach(p => {
        try {
          console.log('Rendering archived product:', p);
          const row = document.createElement('tr');
          row.dataset.categoryName = p.category_name || '';
          // archived table headers: Product ID, Brand, Generic, Category, Subcategory, Unit Price, Archive Reason, Archived Date, Action
          const unitPrice = (p.price_per_unit !== undefined && p.price_per_unit !== null) ? Number(p.price_per_unit).toFixed(2) : '';
          const archiveReason = p.archive_reason || p.reason || '';
          const archivedDate = p.archived_at || p.archived_date || p.updated_at || p.date_archived || '';
          console.log('Created row with data:', { unitPrice, archiveReason, archivedDate });

          row.innerHTML = `
            <td>${p.product_id || ''}</td>
            <td>${p.brand_name || ''}</td>
            <td>${p.generic_name || ''}</td>
            <td>${p.category_name || ''}</td>
            <td>${p.subcategory_name || ''}</td>
            <td>₱${unitPrice} / ${p.unit_of_measurement || ''}</td>
            <td>${archiveReason}</td>
            <td>${archivedDate}</td>
            <td>
              <div class="op-buttons">
                <button class="action-btn edit-btn"><i class="bi bi-pencil"></i> Edit</button>
                <button class="action-btn unarchive-btn"><i class="fas fa-box-open"></i> Unarchive</button>
              </div>
            </td>
          `;

          row.querySelector('.edit-btn')?.addEventListener('click', () => populateEditModal(p));

          row.querySelector('.unarchive-btn')?.addEventListener('click', function () {
            const id = p.product_id || p.productId || null;
            if (!id) return alert('Product id missing');
            if (!unarchiveModal) return alert('Unarchive modal not found');
            // Use the unarchive action endpoint
            unarchiveModal.dataset.targetApi = `/api/products/unarchive/?id=${id}`;
            console.log('Setting unarchive URL:', unarchiveModal.dataset.targetApi);
            console.log('Product ID for unarchive:', id);
            unarchiveModal.style.display = 'flex';
          });

          if (archivedBody) {
            archivedBody.appendChild(row);
            console.log('Successfully appended row to archivedBody');
          } else {
            console.error('Failed to find archivedTableBody element');
          }
        } catch (errRow) {
          console.error('Error rendering archived product row', p, errRow);
        }
      });

    } catch (err) {
      console.error('Error loading products:', err);
      if (tableBody) tableBody.innerHTML = '<tr><td colspan="10">Error loading products.</td></tr>';
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
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      if (res.ok) {
        alert('Product added successfully');
        if (addProductModal) addProductModal.style.display = 'none';
        await loadProductsList();
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
        headers: { 'Content-Type': 'application/json' },
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

    archiveModal.style.display = 'none';

    try {
      const response = await fetch(apiUrl, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'Archived' })
      });

      if (response.ok) {
        alert('Record archived!');
        await loadProductsList();
      } else {
        alert('Failed to archive record.');
      }
    } catch (error) {
      alert('Network error: ' + error);
    }

    delete archiveModal.dataset.targetApi;
  });

  // Cancel archive
  document.getElementById('cancelArchiveBtn')?.addEventListener('click', function () {
    if (archiveModal) archiveModal.style.display = 'none';
    if (archiveModal) delete archiveModal.dataset.targetApi;
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
        headers: { 'Content-Type': 'application/json' },
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

  if (activeSearchInput) {
    activeSearchInput.addEventListener('input', function() {
      clearTimeout(activeSearchTimeout);
      activeSearchTimeout = setTimeout(() => {
        applyCurrentFilters(tableBody, this);
      }, 300);
    });
  }

  if (archivedSearchInput) {
    archivedSearchInput.addEventListener('input', function() {
      clearTimeout(archivedSearchTimeout);
      archivedSearchTimeout = setTimeout(() => {
        applyCurrentFilters(archivedBody, this);
      }, 300);
    });
  }

  function filterProducts(targetTableBody, searchQuery) {
    if (!targetTableBody) return;
    
    // Get the current category filter value for active or archived table
    const isArchivedTable = targetTableBody.id === 'archivedTableBody';
    const categoryFilter = document.getElementById(isArchivedTable ? 'archivedCategoryFilter' : 'categoryFilter');
    const selectedCategory = categoryFilter ? categoryFilter.value : 'all';
    
    const rows = Array.from(targetTableBody.querySelectorAll('tr'));
    rows.forEach(row => {
      const productId = (row.cells[0]?.textContent || '').toLowerCase();
      const brandName = (row.cells[1]?.textContent || '').toLowerCase();
      const genericName = (row.cells[2]?.textContent || '').toLowerCase();
      const categoryName = (row.cells[3]?.textContent || '').toLowerCase();
      
      // Check if the row matches both search query and category filter
      const matchesSearch = !searchQuery || [productId, brandName, genericName].some(field => field.includes(searchQuery));
      const matchesCategory = selectedCategory === 'all' || categoryName === selectedCategory.toLowerCase();
      
      // Only show the row if it matches both conditions
      row.style.display = (matchesSearch && matchesCategory) ? '' : 'none';
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

  // Expose loader so other scripts (or manual triggers) can refresh lists
  window.loadProductsList = loadProductsList;

  // Tab switching is handled by initializeProductTabs() above

});
