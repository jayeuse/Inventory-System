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
        // DI KO ULET ALAM PANO AUTO-LOAD
      } else {
        const errorData = await response.json();
        alert('Error: ' + JSON.stringify(errorData))
      }
    } catch (error) {
      console.error('Network Error: ', error)
    }
  });

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
        // DI KO ALAM PANO MAG AUTO-LOAD
      } else {
        const errorData = await response.json();
        alert('Error: ' + JSON.stringify(errorData))
      }

    } catch (error){
      console.error('Network Error: ', error)
    }
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