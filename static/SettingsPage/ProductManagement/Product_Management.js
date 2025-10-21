// Product management: load, render, add, edit, archive

document.addEventListener('DOMContentLoaded', function () {
  let currentEditProductId = null;

  // Scope queries to the products section to avoid ID collisions in the page
  const container = document.getElementById('products-content');
  if (!container) return; // nothing to do if products content isn't present

  const tableBody = container.querySelector('#tableBody');
  const archivedBody = container.querySelector('#archivedTableBody');
  const addProductModal = document.getElementById('addProductModal');
  const editProductModal = document.getElementById('editProductModal');
  const archiveModal = document.getElementById('archiveModal');
  const unarchiveModal = document.getElementById('unarchiveModal');

  // Fetch and render products
  async function loadProductsList() {
    try {
      const res = await fetch('/api/products/');
      if (!res.ok) throw new Error('Failed to fetch products');
      const data = await res.json();
      const products = Array.isArray(data) ? data : (data.results || []);

      if (tableBody) tableBody.innerHTML = '';
      if (archivedBody) archivedBody.innerHTML = '';

      products.forEach(p => {
        const isArchived = (p.status || '').toLowerCase() === 'archived';
        const row = document.createElement('tr');
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

        // Attach edit handler (scoped to container)
        row.querySelector('.edit-btn')?.addEventListener('click', function () {
          currentEditProductId = p.product_id || p.productId || null;

          // Populate edit modal fields (if present)
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

          // Set category/subcategory selects to returned ids if available
          const editCategory = document.getElementById('editCategory');
          const editSubcategory = document.getElementById('editSubcategory');
          if (editCategory) editCategory.value = p.category_id || p.category || '';
          if (editSubcategory) editSubcategory.value = p.subcategory_id || p.subcategory || '';

          if (editProductModal) editProductModal.style.display = 'flex';
        });

        // Attach archive handler
        row.querySelector('.archive-btn')?.addEventListener('click', function () {
          const id = p.product_id || p.productId || null;
          if (!id) return alert('Product id missing');

          if (!archiveModal) return alert('Archive modal not found');
          archiveModal.dataset.targetApi = `/api/products/${id}/`;
          archiveModal.style.display = 'flex';
        });

        if (isArchived) {
          archivedBody?.appendChild(row);
        } else {
          tableBody?.appendChild(row);
        }
      });

      // wire unarchive buttons in archived rows using delegation
      archivedBody?.querySelectorAll('.unarchive-btn').forEach(btn => {
        btn.addEventListener('click', function () {
          if (unarchiveModal) unarchiveModal.style.display = 'flex';
        });
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

      const catSelects = [document.getElementById('category'), document.getElementById('editCategory')];
      const subSelects = [document.getElementById('subcategory'), document.getElementById('editSubcategory')];

      catSelects.forEach(sel => {
        if (!sel) return;
        sel.innerHTML = '<option value="">Select Category</option>';
        (Array.isArray(cats) ? cats : (cats.results || [])).forEach(c => {
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
            const filtered = (Array.isArray(subs) ? subs : (subs.results || [])).filter(s => ((s.category || s.category_id || '').toString() === selected.toString()));
            filtered.forEach(s => {
              const o = document.createElement('option');
              o.value = s.subcategory_id || s.subcategoryId || s.id || s.subcategory_name;
              o.textContent = s.subcategory_name || o.value;
              ss.appendChild(o);
            });
          });
        });
      });

      // initialize subcategory lists empty
      subSelects.forEach(ss => { if (ss) ss.innerHTML = '<option value="">Select Subcategory</option>'; });

    } catch (err) {
      console.error('Error populating product dropdowns:', err);
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

  // Initialize
  (async function init() {
    if (tableBody) tableBody.innerHTML = '<tr><td colspan="10">Loading products...</td></tr>';
    if (archivedBody) archivedBody.innerHTML = '';

    await populateProductDropdowns();
    await loadProductsList();
  })();

});
