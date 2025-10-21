document.addEventListener("DOMContentLoaded", function () {
  // Main Tab Navigation
  const tabs = document.querySelectorAll(".tab");
  const tabContents = document.querySelectorAll(".tab-content");

  tabs.forEach((tab) => {
    tab.addEventListener("click", function () {
      const tabId = this.getAttribute("data-tab");

      // Remove active class from all tabs and contents
      tabs.forEach((t) => t.classList.remove("active"));
      tabContents.forEach((c) => c.classList.remove("active"));

      // Add active class to clicked tab and corresponding content
      this.classList.add("active");
      document.getElementById(`${tabId}-content`).classList.add("active");
    });
  });

  // System Settings Theme Options
  const themeOptions = document.querySelectorAll(".theme-option");

  themeOptions.forEach((option) => {
    option.addEventListener("click", function () {
      themeOptions.forEach((opt) => opt.classList.remove("active"));
      this.classList.add("active");

      const theme = this.querySelector(".theme-name").textContent;
      console.log(`Theme changed to: ${theme}`);
    });
  });

  // Supplier Management Modal
  const supplierModal = document.getElementById("addSupplierModal");
  const addSupplierBtn = document.getElementById("addSupplierBtn");
  const cancelSupplierBtn = document.getElementById("cancelBtn");

  if (addSupplierBtn) {
    addSupplierBtn.addEventListener(
      "click",
      () => (supplierModal.style.display = "flex")
    );
  }

  if (cancelSupplierBtn) {
    cancelSupplierBtn.addEventListener(
      "click",
      () => (supplierModal.style.display = "none")
    );
  }

  // Product Management Tabs
  const productTabs = document.querySelectorAll(".product-tab");
  const productTabContents = document.querySelectorAll(".product-tab-content");

  productTabs.forEach((tab) => {
    tab.addEventListener("click", function () {
      const tabId = this.getAttribute("data-product-tab");

      // Remove active class from all tabs and contents
      productTabs.forEach((t) => t.classList.remove("active"));
      productTabContents.forEach((c) => c.classList.remove("active"));

      // Add active class to clicked tab and corresponding content
      this.classList.add("active");
      document
        .getElementById(`${tabId}ProductsContent`)
        .classList.add("active");
    });
  });

  // Product Management Modal
  const productModal = document.getElementById("addProductModal");
  const addProductBtn = document.getElementById("addProductBtn");
  const closeProductModalBtn = document.getElementById("closeModalBtn");
  const cancelProductBtn = document.getElementById("cancelProductBtn");

  if (addProductBtn) {
    addProductBtn.addEventListener(
      "click",
      () => (productModal.style.display = "flex")
    );
  }

  if (closeProductModalBtn) {
    closeProductModalBtn.addEventListener(
      "click",
      () => (productModal.style.display = "none")
    );
  }

  if (cancelProductBtn) {
    cancelProductBtn.addEventListener(
      "click",
      () => (productModal.style.display = "none")
    );
  }

  // JavaScript for collapsible forms
  document.addEventListener("DOMContentLoaded", function () {
    // Category form toggle
    const categoryFormContainer = document.getElementById(
      "categoryFormContainer"
    );
    const categoryFormContent = document.getElementById("categoryFormContent");
    const collapseCategoryBtn = document.getElementById("collapseCategoryBtn");
    const toggleCategoryFormBtn = document.getElementById("toggleCategoryForm");

    // Subcategory form toggle
    const subcategoryFormContainer = document.getElementById(
      "subcategoryFormContainer"
    );
    const subcategoryFormContent = document.getElementById(
      "subcategoryFormContent"
    );
    const collapseSubcategoryBtn = document.getElementById(
      "collapseSubcategoryBtn"
    );
    const toggleSubcategoryFormBtn = document.getElementById(
      "toggleSubcategoryForm"
    );

    // Toggle category form collapse
    collapseCategoryBtn.addEventListener("click", function () {
      categoryFormContainer.classList.toggle("collapsed");
    });

    // Toggle subcategory form collapse
    collapseSubcategoryBtn.addEventListener("click", function () {
      subcategoryFormContainer.classList.toggle("collapsed");
    });

    // Toggle category form from button
    toggleCategoryFormBtn.addEventListener("click", function () {
      categoryFormContainer.classList.remove("collapsed");
      // Scroll to the form if needed
      categoryFormContainer.scrollIntoView({
        behavior: "smooth",
        block: "nearest",
      });
    });

    // Toggle subcategory form from button
    toggleSubcategoryFormBtn.addEventListener("click", function () {
      subcategoryFormContainer.classList.remove("collapsed");
      // Scroll to the form if needed
      subcategoryFormContainer.scrollIntoView({
        behavior: "smooth",
        block: "nearest",
      });
    });
  });

  // ========== ADD THE NEW MODAL FUNCTIONALITY HERE ==========
  // Edit, Archive, and Unarchive Modals
  const editSupplierModal = document.getElementById("editSupplierModal");
  const archiveModal = document.getElementById("archiveModal");
  const unarchiveModal = document.getElementById("unarchiveModal");
  const editProductModal = document.getElementById("editProductModal");
  const editCategoryModal = document.getElementById("editCategoryModal");
  const editSubcategoryModal = document.getElementById("editSubcategoryModal");

  // Close buttons for new modals
  const cancelEditBtn = document.getElementById("cancelEditBtn");
  const cancelArchiveBtn = document.getElementById("cancelArchiveBtn");
  const cancelUnarchiveBtn = document.getElementById("cancelUnarchiveBtn");
  const cancelEditProductBtn = document.getElementById("cancelEditProductBtn");
  const cancelEditCategoryBtn = document.getElementById(
    "cancelEditCategoryBtn"
  );
  const cancelEditSubcategoryBtn = document.getElementById(
    "cancelEditSubcategoryBtn"
  );
  const closeEditModalBtn = document.getElementById("closeEditModalBtn");

  // Edit buttons functionality
  document.querySelectorAll(".edit-btn").forEach((btn) => {
    btn.addEventListener("click", function () {
      const row = this.closest("tr");
      if (row) {
        if (row.querySelector("td:nth-child(1)").textContent.includes("SUP")) {
          // Supplier edit
          editSupplierModal.style.display = "flex";
        } else if (
          row.querySelector("td:nth-child(1)").textContent.includes("PRD")
        ) {
          // Product edit
          editProductModal.style.display = "flex";
        } else if (
          row.querySelector("td:nth-child(1)").textContent.includes("PHARM")
        ) {
          // Category edit
          editCategoryModal.style.display = "flex";
        } else if (
          row.querySelector("td:nth-child(1)").textContent.includes("SUB")
        ) {
          // Subcategory edit
          editSubcategoryModal.style.display = "flex";
        }
      }
    });
  });

  // Archive buttons functionality
  document.querySelectorAll(".archive-btn").forEach((btn) => {
    btn.addEventListener("click", function () {
      archiveModal.style.display = "flex";
    });
  });

  // Unarchive buttons functionality
  document.querySelectorAll(".unarchive-btn").forEach((btn) => {
    btn.addEventListener("click", function () {
      unarchiveModal.style.display = "flex";
    });
  });

  // Close modal functions for new modals
  if (cancelEditBtn) {
    cancelEditBtn.addEventListener(
      "click",
      () => (editSupplierModal.style.display = "none")
    );
  }

  if (cancelArchiveBtn) {
    cancelArchiveBtn.addEventListener(
      "click",
      () => (archiveModal.style.display = "none")
    );
  }

  if (cancelUnarchiveBtn) {
    cancelUnarchiveBtn.addEventListener(
      "click",
      () => (unarchiveModal.style.display = "none")
    );
  }

  if (cancelEditProductBtn) {
    cancelEditProductBtn.addEventListener(
      "click",
      () => (editProductModal.style.display = "none")
    );
  }

  if (cancelEditCategoryBtn) {
    cancelEditCategoryBtn.addEventListener(
      "click",
      () => (editCategoryModal.style.display = "none")
    );
  }

  if (cancelEditSubcategoryBtn) {
    cancelEditSubcategoryBtn.addEventListener(
      "click",
      () => (editSubcategoryModal.style.display = "none")
    );
  }

  if (closeEditModalBtn) {
    closeEditModalBtn.addEventListener(
      "click",
      () => (editProductModal.style.display = "none")
    );
  }

  // Close all modals when clicking outside
  window.onclick = (e) => {
    if (e.target === supplierModal) supplierModal.style.display = "none";
    if (e.target === productModal) productModal.style.display = "none";
    if (e.target === editSupplierModal)
      editSupplierModal.style.display = "none";
    if (e.target === archiveModal) archiveModal.style.display = "none";
    if (e.target === unarchiveModal) unarchiveModal.style.display = "none";
    if (e.target === editProductModal) editProductModal.style.display = "none";
    if (e.target === editCategoryModal)
      editCategoryModal.style.display = "none";
    if (e.target === editSubcategoryModal)
      editSubcategoryModal.style.display = "none";
  };
  // ========== END OF NEW MODAL FUNCTIONALITY ==========

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
    } catch (error) {
      console.error('Error fetching suppliers:', error)
    }
  }

  loadSuppliers();
});

function toggleSubcategories(button) {
  const row = button.closest("tr");
  const subcategoryRow = row.nextElementSibling;

  // Toggle the visibility of the subcategory row
  subcategoryRow.classList.toggle("hidden");

  // Update button text and icon based on state
  if (subcategoryRow.classList.contains("hidden")) {
    button.innerHTML = '<i class="bi bi-eye"></i> View';
  } else {
    button.innerHTML = '<i class="bi bi-eye-slash"></i> Hide';
  }
}
