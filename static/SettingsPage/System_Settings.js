document.addEventListener("DOMContentLoaded", function () {
  // Main Tab Navigation
  const tabs = document.querySelectorAll(".tab");
  const tabContents = document.querySelectorAll(".tab-content");

  tabs.forEach((tab) => {
    tab.addEventListener("click", function () {
      const tabId = this.getAttribute("data-tab");
      console.log('Main tab clicked:', tabId);

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
  const closeAddSupplierBtn = document.getElementById("closeAddSupplierBtn");

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

  if (closeAddSupplierBtn) {
    closeAddSupplierBtn.addEventListener(
      "click",
      () => (supplierModal.style.display = "none")
    );
  }

  // Product Management Tabs
  console.log('Setting up product management tabs...');
  const productTabs = document.querySelectorAll(".product-tab");
  const productTabContents = document.querySelectorAll(".product-tab-content");
  
  console.log('Found product tabs:', productTabs.length);
  console.log('Found product tab contents:', productTabContents.length);

  productTabs.forEach((tab) => {
    tab.addEventListener("click", function () {
      const tabId = this.getAttribute("data-product-tab");
      console.log('Product tab clicked:', tabId, 'Target content:', `${tabId}ProductsContent`);

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

  const supplierArchiveModal = document.getElementById("supplierArchiveModal");
  const supplierUnarchiveModal = document.getElementById("supplierUnarchiveModal");
  const categoryArchiveModal = document.getElementById("categoryArchiveModal");
  const categoryUnarchiveModal = document.getElementById("categoryUnarchiveModal");

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

  // const supplierCancelArchiveBtn = document.getElementById("supplierCancelArchiveBtn");
  // const supplierConfirmArchiveBtn = document.getElementById("supplierConfirmArchiveBtn");
  // const supplierCancelUnarchiveBtn = document.getElementById("supplierCancelUnarchiveBtn")
  // const supplierConfirmUnarchiveBtn = document.getElementById("supplierConfirmUnarchiveBtn");

  // const categoryCancelArchiveBtn = document.getElementById("categoryCancelArchiveBtn");
  // const categoryConfirmArchiveBtn = document.getElementById("categoryConfirmArchiveBtn");
  // const categoryCancelUnarchiveBtn = document.getElementById("categoryCancelUnarchiveBtn");
  // const categoryConfirmUnarchiveBtn = document.getElementById("categoryConfirmUnarchiveBtn");

  // Edit buttons functionality
  document.querySelectorAll(".edit-btn").forEach((btn) => {
    btn.addEventListener("click", function () {
      const row = this.closest("tr");
      if (row) {
        if (row.querySelector("td:nth-child(1)").textContent.includes("SUP")) {
          // Supplier edit
          editSupplierModal.style.display = "flex";
        } else if (
          row.querySelector("td:nth-child(1)").textContent.includes("PROD")
        ) {
          // Product edit
          editProductModal.style.display = "flex";
        } else if (
          row.querySelector("td:nth-child(1)").textContent.includes("CAT")
        ) {
          // Category edit
          editCategoryModal.style.display = "flex";
        } else if (
          row.querySelector("td:nth-child(1)").textContent.includes("SUBCAT")
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

      const row = this.closest("tr");
      if (!row){
        return;
      }

      const idCell = row.querySelector("td:nth-child(1)");
      if (!idCell){
        return;
      }

      const id = idCell.textContent.trim();

      if(id.startsWith('SUP')){
        supplierArchiveModal.style.display = 'flex';
        archiveTarget = {apiUrl: `/api/suppliers/${id}/`, id}
      }
      if(id.startsWith('CAT')){
        categoryArchiveModal.style.display = 'flex';
        archiveTarget = {apiUrl: `/api/categories/${id}/`, id}
      }
    });
  });

  // Unarchive buttons functionality
  document.querySelectorAll(".unarchive-btn").forEach((btn) => {
    btn.addEventListener("click", function () {

      const row = this.closest("tr");
      if (!row){
        return;
      }

      const idCell = row.querySelector("td:nth-child(1)");
      if (!idCell){
        return;
      }

      const id = idCell.textContent.trim();

      if(id.startsWith('SUP')){
        supplierUnarchiveModal.style.display = 'flex';
        archiveTarget = {apiUrl: `/api/suppliers/${id}/`, id}
      }
      if(id.startsWith('CAT')){
        categoryUnarchiveModal.style.display = 'flex';
        archiveTarget = {apiUrl: `/api/categories/${id}/`, id}
      }
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
    if (e.target === editSupplierModal) editSupplierModal.style.display = "none";
    if (e.target === archiveModal) archiveModal.style.display = "none";
    if (e.target === unarchiveModal) unarchiveModal.style.display = "none";
    if (e.target === editProductModal) editProductModal.style.display = "none";
    if (e.target === editCategoryModal) editCategoryModal.style.display = "none";
    if (e.target === editSubcategoryModal) editSubcategoryModal.style.display = "none";
    if (e.target === supplierArchiveModal) supplierArchiveModal.style.display = "none";
    if (e.target === supplierUnarchiveModal) supplierUnarchiveModal.style.display = "none";
    if (e.target === categoryArchiveModal) categoryArchiveModal.style.display = "none";
    if (e.target === categoryUnarchiveModal) categoryUnarchiveModal.style.display = "none";
  };
  // ========== END OF NEW MODAL FUNCTIONALITY ==========

  // ...existing code...

  // Supplier toggle functionality
  const supplierToggle = document.getElementById('supplierToggle');
  if (supplierToggle) {
    const supplierToggleOptions = supplierToggle.querySelectorAll('.toggle-option');
    const activeSuppliersTable = document.getElementById('activeSuppliersTable');
    const archivedSuppliersTable = document.getElementById('archivedSuppliersTable');
    const activeSuppliersWrapper = document.getElementById('activeSuppliersWrapper');
    const archivedSuppliersWrapper = document.getElementById('archivedSuppliersWrapper');
    const addSupplierBtn = document.getElementById('addSupplierBtn');

    supplierToggleOptions.forEach(option => {
      option.addEventListener('click', function() {
        supplierToggleOptions.forEach(opt => opt.classList.remove('active'));
        this.classList.add('active');

        const type = this.getAttribute('data-type');
        if (type === 'active') {
          activeSuppliersTable.style.display = 'table';
          archivedSuppliersTable.style.display = 'none';
          if (activeSuppliersWrapper) activeSuppliersWrapper.style.display = 'block';
          if (archivedSuppliersWrapper) archivedSuppliersWrapper.style.display = 'none';
          addSupplierBtn.style.display = 'inline-flex'; // Show button
        } else {
          activeSuppliersTable.style.display = 'none';
          archivedSuppliersTable.style.display = 'table';
          if (activeSuppliersWrapper) activeSuppliersWrapper.style.display = 'none';
          if (archivedSuppliersWrapper) archivedSuppliersWrapper.style.display = 'block';
          addSupplierBtn.style.display = 'none'; // Hide button
        }
      });
    });
  }

  // Category toggle functionality
  const categoryToggle = document.getElementById('categoryToggle');
  if (categoryToggle) {
    const categoryToggleOptions = categoryToggle.querySelectorAll('.toggle-option');
    const activeCategoriesTable = document.getElementById('activeCategoriesTable');
    const archivedCategoriesTable = document.getElementById('archivedCategoriesTable');
    const activeCategoriesWrapper = document.getElementById('activeCategoriesWrapper');
    const archivedCategoriesWrapper = document.getElementById('archivedCategoriesWrapper');
    const formSection = document.querySelector('#categories-content .form-section');

    // Set initial state - show form section and active table
    if (formSection) formSection.style.display = 'block';
    if (activeCategoriesTable) activeCategoriesTable.style.display = 'table';
    if (archivedCategoriesTable) archivedCategoriesTable.style.display = 'none';
    if (activeCategoriesWrapper) activeCategoriesWrapper.style.display = 'block';
    if (archivedCategoriesWrapper) archivedCategoriesWrapper.style.display = 'none';

    categoryToggleOptions.forEach(option => {
      option.addEventListener('click', function() {
        categoryToggleOptions.forEach(opt => opt.classList.remove('active'));
        this.classList.add('active');

        const type = this.getAttribute('data-type');
        if (type === 'active') {
          activeCategoriesTable.style.display = 'table';
          archivedCategoriesTable.style.display = 'none';
          if (activeCategoriesWrapper) activeCategoriesWrapper.style.display = 'block';
          if (archivedCategoriesWrapper) archivedCategoriesWrapper.style.display = 'none';
          if (formSection) formSection.style.display = 'block'; // Show form section
        } else {
          activeCategoriesTable.style.display = 'none';
          archivedCategoriesTable.style.display = 'table';
          if (activeCategoriesWrapper) activeCategoriesWrapper.style.display = 'none';
          if (archivedCategoriesWrapper) archivedCategoriesWrapper.style.display = 'block';
          if (formSection) formSection.style.display = 'none'; // Hide form section when viewing archives
        }
      });
    });
  }

});


let archiveTarget = null;

function getEntityType(id){
  if (id.startsWith('CAT')){
    return 'categories';
  } 
  if (id.startsWith('SUBCAT')){
    return 'subcategories';
  } 
  if (id.startsWith('SUP')){
    return 'suppliers';
  }
  if (id.startsWith('PROD')){
    return 'products';
  }

  return 'entities';
}

let currentEditSupplierId = null;
let currentEditCategoryId = null;

function attachActionButtonListeners() {
  document.querySelectorAll(".edit-btn").forEach((btn) => {
    btn.addEventListener("click", function () {
      const row = this.closest("tr");
      if (row) {
        const idCell = row.querySelector("td:nth-child(1)");
        const id = idCell ? idCell.textContent.trim() : null;

        if(!id){
          return
        }

        if (id && id.includes("SUP")) {
          currentEditSupplierId = id;
          document.getElementById("editSupplierName").value = row.querySelector("td:nth-child(2)").textContent.trim();
          document.getElementById("editContactPerson").value = row.querySelector("td:nth-child(3)").textContent.trim();
          document.getElementById("editSupplierAddress").value = row.querySelector("td:nth-child(4)").textContent.trim();
          document.getElementById("editSupplierEmail").value = row.querySelector("td:nth-child(5)").textContent.trim();
          document.getElementById("editSupplierPhoneNumber").value = row.querySelector("td:nth-child(6)").textContent.trim();
          
          // Get product ID from data attribute instead of text content
          const productCell = row.querySelector("td:nth-child(7)");
          const productId = productCell.getAttribute("data-product-id");
          document.getElementById("editSupplierProduct").value = productId;
          
          document.getElementById("editSupplierStatus").value = row.querySelector("td:nth-child(8)").textContent.trim().toLowerCase();

          editSupplierModal.style.display = "flex";
        } else if (id && id.includes("CAT")) {
          currentEditCategoryId = id;
          document.getElementById("editCategoryName").value = row.querySelector("td:nth-child(2)").textContent.trim();
          document.getElementById("editCategoryDescription").value = row.querySelector("td:nth-child(3)").textContent.trim();
          editCategoryModal.style.display = "flex";
        }
      }
    });
  });

  document.querySelectorAll(".archive-btn").forEach((btn) => {
    btn.addEventListener("click", function () {

      const row = this.closest("tr");
      if (!row){
        return;
      }

      const idCell = row.querySelector("td:nth-child(1)");
      if (!idCell){
        return;
      }

      const id = idCell.textContent.trim();

      if(id.startsWith('SUP')){
        supplierArchiveModal.style.display = 'flex';
        archiveTarget = {apiUrl: `/api/suppliers/${id}/`, id}
      }
      if(id.startsWith('CAT')){
        categoryArchiveModal.style.display = 'flex';
        archiveTarget = {apiUrl: `/api/categories/${id}/`, id}
      }
    });
  });

  document.querySelectorAll(".unarchive-btn").forEach((btn) => {
    btn.addEventListener("click", function () {

      const row = this.closest("tr");
      if (!row){
        return;
      }

      const idCell = row.querySelector("td:nth-child(1)");
      if (!idCell){
        return;
      }

      const id = idCell.textContent.trim();

      if(id.startsWith('SUP')){
        supplierUnarchiveModal.style.display = 'flex';
        archiveTarget = {apiUrl: `/api/suppliers/${id}/`, id}
      }
      if(id.startsWith('CAT')){
        categoryUnarchiveModal.style.display = 'flex';
        archiveTarget = {apiUrl: `/api/categories/${id}/`, id}
      }
    });
  });
}

function toggleSubcategories(button) {
  const row = button.closest("tr");
  const subcategoryRow = row.nextElementSibling;

  // Toggle the visibility of the subcategory row
  subcategoryRow.classList.toggle("hidden");

  // Update button text and icon based on state
  if (subcategoryRow.classList.contains("hidden")) {
    button.innerHTML = '<i class="bi bi-eye"></i> View';
  } else {
    const categoryId = row.children[0].textContent;
    const subcatTbody = subcategoryRow.querySelector('.subcategory-table-body');
    button.innerHTML = '<i class="bi bi-eye-slash"></i> Hide';
    loadSubCategories(categoryId, subcatTbody);
  }

}