document.addEventListener("DOMContentLoaded", function() {
  // Fetching Suppliers Data

  async function loadSuppliers() {
    console.log("Reloading Suppliers...");
    try {
      // Fetch active suppliers
      const response = await fetch('/api/suppliers/');
      const activeSuppliers = await response.json();

      // Fetch archived suppliers
      const archivedResponse = await fetch('/api/suppliers/?show_archived=true');
      const allSuppliers = await archivedResponse.json();
      const archivedSuppliers = allSuppliers.filter(s => s.status === 'Archived');

      // Populate active suppliers table
      const tbody = document.getElementById('suppliers-table-body');
      tbody.innerHTML = '';

      activeSuppliers.forEach(supplier => {
        const row = document.createElement('tr');

        row.innerHTML = `
          <td>${supplier.supplier_id}</td>
          <td>${supplier.supplier_name}</td>
          <td>${supplier.contact_person}</td>
          <td>${supplier.address}</td>
          <td>${supplier.email}</td>
          <td>${supplier.phone_number}</td>
          <td>${supplier.status}</td>
          <td data-product-id="${supplier.product_id}">${supplier.product_name}</td>
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
      });

      // Populate archived suppliers table
      const archivedTbody = document.getElementById('archivedSupplierTableBody');
      if (archivedTbody) {
        archivedTbody.innerHTML = '';

        archivedSuppliers.forEach(supplier => {
          const row = document.createElement('tr');

          row.innerHTML = `
            <td>${supplier.supplier_id}</td>
            <td>${supplier.supplier_name}</td>
            <td>${supplier.contact_person}</td>
            <td>${supplier.address}</td>
            <td>${supplier.email}</td>
            <td>${supplier.phone_number}</td>
            <td>${supplier.status}</td>
            <td data-product-id="${supplier.product_id}">${supplier.product_name}</td>
            <td>${supplier.archive_reason || '-'}</td>
            <td>${supplier.archived_at || '-'}</td>
            <td>
              <div class="op-buttons">
                <button class="action-btn unarchive-btn">
                  <i class="fas fa-undo"></i> Unarchive
                </button>
              </div>
            </td>
          `;

          archivedTbody.appendChild(row);
        });
      }

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
    } catch (error){
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

    const archiveReason = document.getElementById('supplierArchiveReason').value;

    if (!archiveReason){
      alert("Please provide a reason for archiving.");
      return;
    }
    
    document.getElementById('supplierArchiveModal').style.display = 'none';
    
    try {
      const response = await fetch(archiveTarget.apiUrl, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'Archived', archive_reason: archiveReason })
      });
      
      if (response.ok) {
        alert("Supplier Archived Successfully!");
        document.getElementById('supplierArchiveReason').value = '';
        await loadSuppliers();
      } else {
        const errorData = await response.json();
        alert('Error: ' + JSON.stringify(errorData))
      }
    } catch (error) {
      console.error("Error:", error);
    }
    
    archiveTarget = null;
  })

  document.getElementById('supplierCancelArchiveBtn').addEventListener('click', function(){
    document.getElementById('supplierArchiveModal').style.display = 'none';
    console.log("Cancel Archive Button");
    document.getElementById('supplierArchiveReason').value = '';
    archiveTarget = null;
  })

  document.getElementById('supplierConfirmUnarchiveBtn').addEventListener('click', async function(){
    if (!archiveTarget) return;

    const unarchiveReason = document.getElementById('supplierUnarchiveReason').value;

    if (!unarchiveReason){
      alert("Please provide a reason for unarchiving.");
      return;
    }
    
    document.getElementById('supplierUnarchiveModal').style.display = 'none';
    
    try {
      const response = await fetch(`${archiveTarget.apiUrl}?show_archived=true`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'Active', unarchive_reason: unarchiveReason })
      });
      
      if (response.ok) {
        alert("Supplier Unarchived Successfully!");
        document.getElementById('supplierUnarchiveReason').value = '';
        await loadSuppliers();
      } else {
        const errorData = await response.json();
        alert('Error: ' + JSON.stringify(errorData));
      }
    } catch (error) {
      console.error("Error:", error);
    }
    
    archiveTarget = null;
  })

  document.getElementById('supplierCancelUnarchiveBtn').addEventListener('click', function(){
    document.getElementById('supplierUnarchiveModal').style.display = 'none';
    document.getElementById('supplierUnarchiveReason').value = '';
    archiveTarget = null;
  })

})