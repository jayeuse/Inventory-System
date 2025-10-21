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

  // Close modals when clicking outside
  window.onclick = (e) => {
    if (e.target === supplierModal) supplierModal.style.display = "none";
    if (e.target === productModal) productModal.style.display = "none";
  };
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
