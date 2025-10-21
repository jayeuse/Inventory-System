document.addEventListener("DOMContentLoaded", function () {
  // Tab navigation functionality
  const tabs = document.querySelectorAll(".tab");
  const pages = document.querySelectorAll(".page-content");

  // Function to switch pages
  function switchPage(pageId) {
    // Update URL without page reload
    history.pushState({ page: pageId }, "", `#${pageId}`);

    // Update active tab
    tabs.forEach((tab) => {
      if (tab.getAttribute("data-page") === pageId) {
        tab.classList.add("active");
      } else {
        tab.classList.remove("active");
      }
    });

    // Show active page
    pages.forEach((page) => {
      if (page.id === `${pageId}-page`) {
        page.classList.add("active");
      } else {
        page.classList.remove("active");
      }
    });
  }

  // Tab click event
  tabs.forEach((tab) => {
    tab.addEventListener("click", function () {
      const pageId = this.getAttribute("data-page");
      switchPage(pageId);
    });
  });

  // Handle browser back/forward buttons
  window.addEventListener("popstate", function (event) {
    const pageId = event.state ? event.state.page : "products";
    switchPage(pageId);
  });

  // Check URL hash on page load
  const initialPage = window.location.hash.substring(1) || "products";
  switchPage(initialPage);

  // Products List functionality
  const prevBtn = document.getElementById("productslist_prevBtn");
  const nextBtn = document.getElementById("productslist_nextBtn");
  // Client-side pagination and filtering state
  let currentPage = 1;
  let pageSize = 10;
  let totalPages = 1;
  let productsCache = []; // full list from API
  let lastQuery = '';

  if (prevBtn) {
    prevBtn.addEventListener("click", function () {
      if (currentPage > 1) {
        currentPage -= 1;
        renderCurrentView();
      }
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener("click", function () {
      if (currentPage < totalPages) {
        currentPage += 1;
        renderCurrentView();
      }
    });
  }

  // Manage Products button - redirect to Product Management
  const manageProductBtn = document.getElementById(
    "productslist_manageProductBtn"
  );

  if (manageProductBtn) {
    manageProductBtn.addEventListener("click", function () {
      // Redirect to Product Management page
      window.location.href =
        "/static/SettingsPage/System_Settings.html#products";
    });
  }

  // Search functionality for products
  const searchInput = document.getElementById("productslist_searchInput");
  const categoryFilter = document.getElementById("productslist_categoryFilter");

  // Debounce input
  let searchTimeout = null;
  if (searchInput) {
    searchInput.addEventListener("input", function () {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        currentPage = 1;
        lastQuery = this.value.trim();
        renderCurrentView();
      }, 300);
    });
  }

  if (categoryFilter) {
    categoryFilter.addEventListener("change", function () {
      console.log("Category filter changed to:", this.value);
      currentPage = 1;
      renderCurrentView();
    });
  }

  // Populate categories dropdown from API
  async function populateCategoriesDropdown() {
    if (!categoryFilter) return;
    try {
      const res = await fetch('/api/categories/');
      if (!res.ok) throw new Error('Failed to load categories');
      const data = await res.json();

      // Replace options with 'all' + categories
      categoryFilter.innerHTML = '';
      const allOption = document.createElement('option');
      allOption.value = 'all';
      allOption.textContent = 'Filter by Category';
      categoryFilter.appendChild(allOption);

      data.forEach(cat => {
        const opt = document.createElement('option');
        opt.value = cat.category_id || cat.categoryId || cat.id || cat.category_name;
        opt.textContent = cat.category_name || cat.name || opt.value;
        categoryFilter.appendChild(opt);
      });
    } catch (err) {
      console.error('Error loading categories:', err);
      // leave existing static options if present
    }
  }

  // Product table body
  const tableBody = document.getElementById('productslist_tableBody');

  async function fetchAllProducts() {
    try {
      const res = await fetch('/api/products/');
      if (!res.ok) throw new Error(`Failed to fetch products: ${res.status}`);
      const data = await res.json();
      productsCache = Array.isArray(data) ? data : (data.results || []);
      currentPage = 1;
      renderCurrentView();
    } catch (err) {
      console.error('Error loading products:', err);
      if (tableBody) tableBody.innerHTML = `<tr><td colspan="7">Error loading products.</td></tr>`;
    }
  }

  function renderCurrentView() {
    const search = lastQuery.toLowerCase();
    const category = (categoryFilter && categoryFilter.value) ? categoryFilter.value.toLowerCase() : 'all';

    // Filter
    let filtered = productsCache.filter(p => {
      // search against product_id, brand_name, generic_name
      const matchesSearch = !search || [p.product_id, p.brand_name, p.generic_name, p.product_name].some(f => (f || '').toLowerCase().includes(search));

    // Products from API may include a category id field or nested category.
    const productCategoryId = (p.category || p.category_id || '').toString().toLowerCase();
    const productCategoryName = (p.category_name || '').toLowerCase();
    const matchesCategory = (category === 'all') || (productCategoryId === category) || (productCategoryName.includes(category));

      return matchesSearch && matchesCategory;
    });

    totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
    if (currentPage > totalPages) currentPage = totalPages;

    const start = (currentPage - 1) * pageSize;
    const pageItems = filtered.slice(start, start + pageSize);

    // Render
    if (!tableBody) return;
    tableBody.innerHTML = '';

    if (pageItems.length === 0) {
      const tr = document.createElement('tr');
      tr.innerHTML = `<td colspan="7">No products found.</td>`;
      tableBody.appendChild(tr);
    } else {
      for (const p of pageItems) {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${p.product_id || ''}</td>
          <td>${p.brand_name || ''}</td>
          <td>${p.generic_name || ''}</td>
          <td>${p.category_name || ''}</td>
          <td>${p.subcategory_name || ''}</td>
          <td>₱${(p.price_per_unit !== undefined && p.price_per_unit !== null) ? Number(p.price_per_unit).toFixed(2) : ''} / ${p.unit_of_measurement || ''}</td>
          <td>-</td>
        `;
        tableBody.appendChild(tr);
      }
    }

    if (prevBtn) prevBtn.disabled = currentPage <= 1;
    if (nextBtn) nextBtn.disabled = currentPage >= totalPages;
  }

  // Initial fetch
  // Populate categories and fetch products
  populateCategoriesDropdown();
  fetchAllProducts();
});
