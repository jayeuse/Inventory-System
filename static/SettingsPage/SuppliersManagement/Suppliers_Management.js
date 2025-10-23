document.addEventListener("DOMContentLoaded", function() {
  // Fetching Suppliers Data

  async function loadSuppliers() {
    console.log("Reloading Suppliers...");
    try {
      const response = await fetch('/api/suppliers/');
      const data = await response.json();

      const tbody = document.getElementById('suppliers-table-body');
      tbody.innerHTML = '';

      data.forEach(supplier => {
        const row = document.createElement('tr');

        row.innerHTML = `
          <td>${supplier.supplier_id}</td>
          <td>${supplier.supplier_name}</td>
          <td>${supplier.contact_person}</td>
          <td>${supplier.address}</td>
          <td>${supplier.email}</td>
          <td>${supplier.phone_number}</td>
          <td data-product-id="${supplier.product_id}">${supplier.product_name}</td>
          <td>${supplier.status}</td>
          <td>
            <div class="op-buttons">
              <button class="action-btn edit-btn">
                <i class="bi bi-pencil"></i> Edit
              </button>
              <button class="action-btn archive-btn">
                <i class="fas fa-archive"></i> Archive
              </button>
            </div>
          </td>
        `;

        tbody.appendChild(row);
      })

      attachActionButtonListeners();
    } catch (error) {
      console.error('Error fetching Suppliers:', error);
    }
  }

  loadSuppliers();
  
  // Populate Supplier Product Dropdown
  async function populateProductDropdown() {
    try {
      const response = await fetch('/api/products/');
      const products = await response.json();
      const productSelect = document.getElementById('supplierProduct');
      productSelect.innerHTML = `
        <option value="">Select a Product</option>
      `;
      products.forEach(product => {
        productSelect.innerHTML += `
          <option value="${product.product_id}">${product.product_name}</option>
        `;
      });

      const editProductSelect = document.getElementById('editSupplierProduct');
      editProductSelect.innerHTML = `
      <option value="">Select a Product</option>
      `;
      products.forEach(product => {
        editProductSelect.innerHTML += `
          <option value="${product.product_id}">${product.product_name}</option>
        `;
      })
    } catch (errpr){
      console.error('Error loading products: ', error)
    }
  }

  populateProductDropdown();

  // Inserting Suppliers
  document.getElementById('saveSupplierBtn').addEventListener('click', async function () {

    const supplierName = document.getElementById('supplierName').value;
    const supplierContactPerson = document.getElementById('supplierContactPerson').value;
    const supplierAddress = document.getElementById('supplierAddress').value;
    const supplierEmail = document.getElementById('supplierEmail').value;
    const supplierPhoneNumber = document.getElementById('supplierPhoneNumber').value;
    const supplierProduct = document.getElementById('supplierProduct').value;
    const supplierStatus = document.getElementById('supplierStatus').value;

    const data = {
      supplier_name: supplierName,
      contact_person: supplierContactPerson,
      address: supplierAddress,
      email: supplierEmail,
      phone_number: supplierPhoneNumber,
      product: supplierProduct,
      status: supplierStatus
    };

    try {
      const response = await fetch('/api/suppliers/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });

      if (response.ok){
        alert('Supplier Added Successfully!')
        document.getElementById('addSupplierModal').style.display = 'none';
        await loadSuppliers();
      } else {
        const errorData = await response.json();
        alert('Error: ' + JSON.stringify(errorData))
      }
    } catch (error){
      alert('Network error: ' + error);
    }
  });


  // Editing Suppliers
  document.getElementById('updateSupplierEditBtn').addEventListener('click', async function(){
    if (!currentEditSupplierId){
      console.log("Supplier Id does not exist for editing");
      return
    }

    const editSupplierName = document.getElementById('editSupplierName').value;
    const editContactPerson = document.getElementById('editContactPerson').value;
    const editSupplierAddress = document.getElementById('editSupplierAddress').value;
    const editSupplierEmail = document.getElementById('editSupplierEmail').value;
    const editSupplierPhoneNumber = document.getElementById('editSupplierPhoneNumber').value;
    const editSupplierProduct = document.getElementById('editSupplierProduct').value;
    const editSupplierStatus = document.getElementById('editSupplierStatus').value;

    const data = {
      supplier_name: editSupplierName,
      contact_person: editContactPerson,
      address: editSupplierAddress,
      email: editSupplierEmail,
      phone_number: editSupplierPhoneNumber,
      product: editSupplierProduct,
      status: editSupplierStatus
    };

    try {
      const response = await fetch(`/api/suppliers/${currentEditSupplierId}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });

      if (response.ok){
        alert("Supplier updated Successfully!")
        document.getElementById('editSupplierModal').style.display = 'none';
        currentEditSupplierId = null;
        await loadSuppliers();
      } else {
        const errorData = await response.json()
        console.error("Error: " + JSON.stringify(errorData))
      }
    } catch (error){
      console.error("Network Error: ", error)
    }
  });

  document.getElementById('cancelSupplierEditBtn').addEventListener('click', function(){
    document.getElementById('editSupplierModal').style.display = 'none';
    currentEditSupplierId = null;
  })

  // Archiving Suppliers
  document.getElementById('supplierConfirmArchiveBtn').addEventListener('click', async function(){
    if (!archiveTarget) return;
    
    document.getElementById('supplierArchiveModal').style.display = 'none';
    
    try {
      const response = await fetch(archiveTarget.apiUrl, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'Archived' })
      });
      
      if (response.ok) {
        alert("Supplier Archived Successfully!");
        await loadSuppliers();
      }
    } catch (error) {
      console.error("Error:", error);
    }
    
    archiveTarget = null;
  })

  document.getElementById('supplierCancelArchiveBtn').addEventListener('click', function(){
    document.getElementById('supplierArchiveModal').style.display = 'none';
    console.log("Cancel Archive Button");
    archiveTarget = null;
  })

  document.getElementById('supplierConfirmUnarchiveBtn').addEventListener('click', async function(){
    if (!archiveTarget) return;
    
    document.getElementById('supplierUnarchiveModal').style.display = 'none';
    
    try {
      const response = await fetch(archiveTarget.apiUrl, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'Active' })
      });
      
      if (response.ok) {
        alert("Supplier Unarchived Successfully!");
        await loadSuppliers();
      }
    } catch (error) {
      console.error("Error:", error);
    }
    
    archiveTarget = null;
  })

  document.getElementById('supplierCancelUnarchiveBtn').addEventListener('click', function(){
    document.getElementById('supplierUnarchiveModal').style.display = 'none';
    archiveTarget = null;
  })

})