function truncateText(text, maxLength = 50) {
  if (!text) return '-';
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
}

document.addEventListener("DOMContentLoaded", function(){

  let allActiveCategories = [];
  let allArchivedCategories = [];
  let currentPage = 1;
  let archivedCurrentPage = 1;
  const recordsPerPage = 8;

  // Fetching Categories + Subcategories Data
  async function loadCategories(){
    try {
      // Fetch active categories (default endpoint)
      const response = await fetch('/api/categories/');
      allActiveCategories = await response.json();

      // Fetch all categories including archived
      const archivedResponse = await fetch('/api/categories/?show_archived=true');
      const allCategories = await archivedResponse.json();
      allArchivedCategories = allCategories.filter(c => c.status === 'Archived');

      currentPage = 1;
      archivedCurrentPage = 1;
      displayCategories();
      displayArchivedCategories();
      attachActionButtonListeners();
    } catch (error) {
      console.error('Error fetching Categories: ', error);
    }
  }

  // Display active categories with pagination, search, and filter
  function displayCategories() {
    const searchTerm = document.getElementById('categorySearchInput')?.value.toLowerCase() || '';
    const statusFilter = document.getElementById('categoryStatusFilter')?.value || 'all';

    // Filter categories
    let filteredCategories = allActiveCategories.filter(category => {
      const matchesSearch = 
        category.category_name.toLowerCase().includes(searchTerm) ||
        category.category_id.toLowerCase().includes(searchTerm) ||
        (category.category_description && category.category_description.toLowerCase().includes(searchTerm));
      
      const matchesStatus = statusFilter === 'all' || category.status.toLowerCase() === statusFilter.toLowerCase();

      return matchesSearch && matchesStatus;
    });

    // Calculate pagination
    const totalPages = Math.ceil(filteredCategories.length / recordsPerPage);
    const startIndex = (currentPage - 1) * recordsPerPage;
    const endIndex = startIndex + recordsPerPage;
    const paginatedCategories = filteredCategories.slice(startIndex, endIndex);

    // Populate active categories table
    const tbody = document.getElementById('category-table-body');
    tbody.innerHTML = '';

    if (paginatedCategories.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">No categories found</td></tr>';
    } else {
      paginatedCategories.forEach(category => {
        const row = document.createElement('tr');

        row.innerHTML = `
          <td>${category.category_id}</td>
          <td>${category.category_name}</td>
          <td title="${category.category_description || ''}">${truncateText(category.category_description)}</td>
          <td>${category.product_count}</td>
          <td class="op-buttons">
            <button class="action-btn view-btn">
              <i class="bi bi-eye"></i> View
            </button>
            <button class="action-btn edit-btn">
              <i class="bi bi-pencil"></i> Edit
            </button>
            <button class="action-btn archive-btn">
              <i class="bi bi-archive"></i> Archive
            </button>
          </td>
        `;

        tbody.appendChild(row);

        // Subcategory row (hidden by default)
        const subcatRow = document.createElement('tr');
        subcatRow.className = 'subcategory-row hidden';
        subcatRow.innerHTML = `
          <td colspan="5">
            <table class="subcategory-table">
              <thead>
                <tr>
                  <th>Subcategory ID</th>
                  <th>Subcategory Name</th>
                  <th>Description</th>
                  <th>Product Count</th>
                </tr>
              </thead>
              <tbody class="subcategory-table-body" data-category-id="${category.category_id}">
                <!-- Subcategories will be loaded here -->
              </tbody>
            </table>
          </td>
        `;
        tbody.appendChild(subcatRow);
      });

      // Add event listeners for view buttons
      tbody.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', function(){
          toggleSubcategories(this);
        });
      });
    }

    // Update pagination buttons
    updatePaginationButtons(currentPage, totalPages, false);
  }

  // Display archived categories with pagination
  function displayArchivedCategories() {
    const totalPages = Math.ceil(allArchivedCategories.length / recordsPerPage);
    const startIndex = (archivedCurrentPage - 1) * recordsPerPage;
    const endIndex = startIndex + recordsPerPage;
    const paginatedCategories = allArchivedCategories.slice(startIndex, endIndex);

    const archivedTbody = document.getElementById('archivedCategoriesTableBody');
    if (archivedTbody) {
      archivedTbody.innerHTML = '';

      if (paginatedCategories.length === 0) {
        archivedTbody.innerHTML = '<tr><td colspan="7" style="text-align: center;">No archived categories</td></tr>';
      } else {
        paginatedCategories.forEach(category => {
          const row = document.createElement('tr');

          row.innerHTML = `
            <td>${category.category_id}</td>
            <td>${category.category_name}</td>
            <td title="${category.category_description || ''}">${truncateText(category.category_description)}</td>
            <td>${category.product_count}</td>
            <td title="${category.archive_reason || ''}">${truncateText(category.archive_reason, 30)}</td>
            <td>${category.archived_at || '-'}</td>
            <td class="op-buttons">
              <button class="action-btn view-btn">
                <i class="bi bi-eye"></i> View
              </button>
              <button class="action-btn unarchive-btn">
                <i class="fas fa-undo"></i> Unarchive
              </button>
            </td>
          `;

          archivedTbody.appendChild(row);

          // Subcategory row for archived categories
          const subcatRow = document.createElement('tr');
          subcatRow.className = 'subcategory-row hidden';
          subcatRow.innerHTML = `
            <td colspan="7">
              <table class="subcategory-table">
                <thead>
                  <tr>
                    <th>Subcategory ID</th>
                    <th>Subcategory Name</th>
                    <th>Description</th>
                    <th>Product Count</th>
                  </tr>
                </thead>
                <tbody class="subcategory-table-body" data-category-id="${category.category_id}">
                  <!-- Subcategories will be loaded here -->
                </tbody>
              </table>
            </td>
          `;
          archivedTbody.appendChild(subcatRow);
        });

        // Add event listeners for view buttons
        archivedTbody.querySelectorAll('.view-btn').forEach(btn => {
          btn.addEventListener('click', function(){
            toggleSubcategories(this);
          });
        });
      }
    }

    updatePaginationButtons(archivedCurrentPage, totalPages, true);
  }

  // Update pagination buttons
function updatePaginationButtons(current, total, isArchived) {
  // For now, use the same pagination buttons for both active and archived
  // Since your HTML doesn't have separate archived pagination buttons yet
  const paginationContainer = document.querySelector('#categories-content .pagination');
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

// Pagination event listeners
const categoryPaginationContainer = document.querySelector('#categories-content .pagination');
if (categoryPaginationContainer) {
  const prevBtn = categoryPaginationContainer.querySelector('.pagination-btn:first-child');
  const nextBtn = categoryPaginationContainer.querySelector('.pagination-btn:last-child');

  if (prevBtn) {
    prevBtn.addEventListener('click', function() {
      // Check which table is currently visible
      const activeCategoriesTable = document.getElementById('activeCategoriesTable');
      const isActiveVisible = activeCategoriesTable && activeCategoriesTable.style.display !== 'none';

      if (isActiveVisible) {
        if (currentPage > 1) {
          currentPage--;
          displayCategories();
          attachActionButtonListeners();
        }
      } else {
        if (archivedCurrentPage > 1) {
          archivedCurrentPage--;
          displayArchivedCategories();
          attachActionButtonListeners();
        }
      }
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', function() {
      // Check which table is currently visible
      const activeCategoriesTable = document.getElementById('activeCategoriesTable');
      const isActiveVisible = activeCategoriesTable && activeCategoriesTable.style.display !== 'none';

      if (isActiveVisible) {
        const searchTerm = document.getElementById('categorySearchInput')?.value.toLowerCase() || '';
        const statusFilter = document.getElementById('categoryStatusFilter')?.value || 'all';
        
        let filteredCategories = allActiveCategories.filter(category => {
          const matchesSearch = 
            category.category_name.toLowerCase().includes(searchTerm) ||
            category.category_id.toLowerCase().includes(searchTerm) ||
            (category.category_description && category.category_description.toLowerCase().includes(searchTerm));
          
          const matchesStatus = statusFilter === 'all' || category.status.toLowerCase() === statusFilter.toLowerCase();

          return matchesSearch && matchesStatus;
        });

        const totalPages = Math.ceil(filteredCategories.length / recordsPerPage);
        if (currentPage < totalPages) {
          currentPage++;
          displayCategories();
          attachActionButtonListeners();
        }
      } else {
        const totalPages = Math.ceil(allArchivedCategories.length / recordsPerPage);
        if (archivedCurrentPage < totalPages) {
          archivedCurrentPage++;
          displayArchivedCategories();
          attachActionButtonListeners();
        }
      }
    });
  }
}

  // Search and filter event listeners
  document.getElementById('categorySearchInput')?.addEventListener('input', function() {
    currentPage = 1;
    displayCategories();
    attachActionButtonListeners();
  });

  document.getElementById('categoryStatusFilter')?.addEventListener('change', function() {
    currentPage = 1;
    displayCategories();
    attachActionButtonListeners();
  });

  loadCategories();

  async function populateCategoriesDropdown(){
    try {
      const response = await fetch('/api/categories/');
      const categories = await response.json();
      const categorySelect = document.getElementById('category-classification');
      categorySelect.innerHTML = `
        <option value="">Select a Category Classification</option>
      `;

      categories.forEach(category =>{
        categorySelect.innerHTML += `
          <option value=${category.category_id}>${category.category_name}</option>
        `;
      });
    } catch (error){
      console.error('Error loading Categories: ', error);
    }
  }

  populateCategoriesDropdown();

  // Inserting Categories
  document.getElementById('addCategoryBtn').addEventListener('click', async function() {
    const categoryName = document.getElementById('category-name').value;
    const categoryDescription = document.getElementById('category-description').value;

    const data = {
      category_name: categoryName,
      category_description: categoryDescription
    }

    try {
      const response = await fetch('/api/categories/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)

      });

      if (response.ok){
        alert('Category added Succesfully!');
        await loadCategories();
      } else {
        const errorData = await response.json();
        alert('Error: ' + JSON.stringify(errorData))
      }
    } catch (error) {
      console.error('Network Error: ', error)
    }
  });

  // Inserting Subcategories
  document.getElementById('addSubCategoryBtn').addEventListener('click', async function() {
    const subCategoryClassfication = document.getElementById('category-classification').value;
    const subCategoryName = document.getElementById('subcategory-name').value;
    const subCategoryDescription = document.getElementById('subcategory-description').value;

    const data = {
      subcategory_name: subCategoryName,
      subcategory_description: subCategoryDescription,
      category: subCategoryClassfication
    }
    
    try {
      const response = await fetch('/api/subcategories/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });

      if (response.ok){
        alert("Subcategory added Successfully!")
        await loadSubCategories();
      } else {
        const errorData = await response.json();
        alert('Error: ' + JSON.stringify(errorData))
      }

    } catch (error){
      console.error('Network Error: ', error)
    }
  });

  // Updating Categories
  document.getElementById('updateCategoryEditBtn').addEventListener('click', async function (){
    const editCategoryName = document.getElementById('editCategoryName').value;
    const editCategoryDescription = document.getElementById('editCategoryDescription').value;

    const data = {
      category_name: editCategoryName,
      category_description: editCategoryDescription
    }

    try {
      const response = await fetch (`/api/categories/${currentEditCategoryId}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });

      if (response.ok){
        alert("Category updated Successfully!")
        await loadCategories();
      } else {
        const errorData = await response.json();
        console.error("Error: " + JSON.stringify(errorData))
      }
    } catch (error){
      console.error("Network Error: ", error)
    }
  })

  // Archiving Categories

  document.getElementById('categoryConfirmArchiveBtn').addEventListener('click', async function(){
    if (!archiveTarget) return;

    const archiveReason = document.getElementById('categoryArchiveReason').value;

    if (!archiveReason){
      alert("Please provide a reason for archiving.");
      return;
    }
    
    document.getElementById('categoryArchiveModal').style.display = 'none';
    
    try {
      const response = await fetch(archiveTarget.apiUrl, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'Archived', archive_reason: archiveReason })
      });
      
      if (response.ok) {
        alert("Category Archived Successfully!");
        document.getElementById('categoryArchiveReason').value = '';
        await loadCategories();
      } else {
        const errorData = await response.json();
        alert('Error: ' + JSON.stringify(errorData))
      }
    } catch (error) {
      console.error("Error:", error);
    }
    
    archiveTarget = null;
  })

  document.getElementById('categoryCancelArchiveBtn').addEventListener('click', function(){
    document.getElementById('categoryArchiveModal').style.display = 'none';
    document.getElementById('categoryArchiveReason').value = '';
    archiveTarget = null;
  })

  document.getElementById('categoryConfirmUnarchiveBtn').addEventListener('click', async function(){
    if (!archiveTarget) return;

    const unarchiveReason = document.getElementById('categoryUnarchiveReason').value;

    if (!unarchiveReason){
      alert("Please provide a reason for unarchiving.");
      return;
    }
    
    document.getElementById('categoryUnarchiveModal').style.display = 'none';
    
    try {
      const response = await fetch(`${archiveTarget.apiUrl}?show_archived=true`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'Active', unarchive_reason: unarchiveReason })
      });
      
      if (response.ok) {
        alert("Category Unarchived Successfully!");
        document.getElementById('categoryUnarchiveReason').value = '';
        await loadCategories();
      } else {
        const errorData = await response.json();
        alert('Error: ' + JSON.stringify(errorData));
      }
    } catch (error) {
      console.error("Error:", error);
    }
    
    archiveTarget = null;
  })

  document.getElementById('categoryCancelUnarchiveBtn').addEventListener('click', function(){
    document.getElementById('categoryUnarchiveModal').style.display = 'none';
    document.getElementById('categoryUnarchiveReason').value = '';
    archiveTarget = null;
  })
})

async function loadSubCategories(categoryId, tbody) {
  try {
    const response = await fetch ('/api/subcategories/');
    const data = await response.json();
    
    if (!tbody) {
      console.warn('Subcategory tbody not found!');
      return;
    }

    tbody.innerHTML = ``;

    const filtered = data.filter(subcategory => subcategory.category === categoryId);
    filtered.forEach(subcategory =>{
      const row = document.createElement('tr');
      
      row.innerHTML = `
        <td>${subcategory.subcategory_id}</td>
        <td>${subcategory.subcategory_name}</td>
        <td title="${subcategory.subcategory_description || ''}">${truncateText(subcategory.subcategory_description)}</td>
        <td>${subcategory.product_count}</td>
      `;

      tbody.appendChild(row);
    })
  } catch (error){
    console.error('Error fetching Subcategories: ', error)
  }
}