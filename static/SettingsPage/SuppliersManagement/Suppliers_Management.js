document.addEventListener("DOMContentLoaded", function() {
  // Fetching Suppliers Data

  async function loadSuppliers() {
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
          <td>${supplier.product_name}</td>
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
        // DI KO MA AUTO-LOAD YUNG SUPPLIER TABLE PAG SUCCESSFUL YUNG ADD SUPPLIER -cj
      } else {
        const errorData = await response.json();
        alert('Error: ' + JSON.stringify(errorData))
      }
    } catch (error){
      alert('Network error: ' + error);
    }
  });
})