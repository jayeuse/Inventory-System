document.addEventListener("DOMContentLoaded", function(){
  // Fetching Categories + Subcategories Data

  async function loadCategories(){
    try {
      const response = await fetch('/api/categories/');
      const data = await response.json();

      const tbody = document.getElementById('category-table-body');

      tbody.innerHTML = ``;

      data.forEach(category => {
        const row = document.createElement('tr');

        row.innerHTML = `
          <td>${category.category_id}</td>
          <td>${category.category_name}</td>
          <td>${category.category_description}</td>
          <td>${category.product_count}</td>
          <td class="op-buttons">
            <button
              class="action-btn view-btn">
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

      tbody.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', function(){
          toggleSubcategories(this);
        })
      })

      attachActionButtonListeners();
    } catch (error) {
      console.error('Error fetching Categories: ', error)
    }
  }

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
    
    document.getElementById('categoryUnarchiveModal').style.display = 'none';

    const unarchiveReason = document.getElementById('categoryUnarchiveReason').value;

    if (!unarchiveReason){
      alert("Please provide a reason for unarchiving.");
      return;
    }
    
    try {
      const response = await fetch(archiveTarget.apiUrl, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'Active', unarchive_reason: unarchiveReason })
      });
      
      if (response.ok) {
        alert("Category Unarchived Successfully!");
        document.getElementById('categoryUnarchiveReason').value = '';
        await loadCategories();
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
        <td>${subcategory.subcategory_description}</td>
        <td>${subcategory.product_count}</td>
      `;

      tbody.appendChild(row);
    })
  } catch (error){
    console.error('Error fetching Subcategories: ', error)
  }
}