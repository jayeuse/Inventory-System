const tabs = document.querySelectorAll(".tab");
const productTableBody = document.getElementById("productTableBody");

// Tab switching
tabs.forEach(tab => {
  tab.addEventListener("click", () => {
    tabs.forEach(t => t.classList.remove("active"));
    tab.classList.add("active");

    const card = document.querySelector('.card');
    if (tab.dataset.tab === 'products') {
      card.style.background = 'rgba(255, 255, 255, 0.85)';
      card.style.borderColor = 'rgba(255, 255, 255, 0.5)';
    } else {
      card.style.background = 'rgba(255, 255, 255, 0.85)';
      card.style.borderColor = 'rgba(255, 255, 255, 0.5)';
    }
  });
});

// Edit button functionality
document.addEventListener("click", (e) => {
  if (e.target.closest(".edit-btn")) {
    const row = e.target.closest("tr");
    
    // Extract data from the row
    const productData = {
      id: row.cells[0].textContent,
      name: row.cells[1].textContent,
      category: row.cells[2].textContent,
      sku: row.cells[3].textContent,
      price: row.cells[4].textContent,
      onHand: row.cells[5].textContent,
      reserved: row.cells[6].textContent,
      status: row.cells[7].querySelector('.status').textContent.toLowerCase().replace(/\s+/g, '-'),
      lastUpdate: row.cells[8].textContent
    };
    
    openProductModal(productData);
  }
});

// ========== MODAL FUNCTIONS (Transfer this section to modal_product_details.js later) ==========

const modal = document.getElementById("productDetailsModal");
const closeModalBtn = document.getElementById("closeModalBtn");
const cancelModalBtn = document.getElementById("cancelModalBtn");
const saveModalBtn = document.getElementById("saveModalBtn");

// Open modal with product data
function openProductModal(productData) {
  if (!modal) {
    console.error("Modal not found");
    return;
  }

  // Populate product information
  document.getElementById("modalProductId").value = productData.id || '';
  document.getElementById("modalSku").value = productData.sku || '';
  document.getElementById("modalProductName").value = productData.name || '';
  document.getElementById("modalCategory").value = productData.category || '';
  document.getElementById("modalPrice").value = productData.price || '';
  document.getElementById("modalTotalOnHand").value = productData.onHand || '';
  document.getElementById("modalTotalReserved").value = productData.reserved || '';
  document.getElementById("modalStatus").value = productData.status || 'normal';
  document.getElementById("modalLastUpdate").value = productData.lastUpdate || '';
  
  // Show modal
  modal.style.display = "flex";
}

// Close modal
function closeProductModal() {
  if (modal) {
    modal.style.display = "none";
  }
}

// Close modal event listeners
if (closeModalBtn) {
  closeModalBtn.addEventListener("click", closeProductModal);
}

if (cancelModalBtn) {
  cancelModalBtn.addEventListener("click", closeProductModal);
}

// Close modal when clicking outside
window.addEventListener("click", (e) => {
  if (e.target === modal) {
    closeProductModal();
  }
});

// Save changes (placeholder for backend integration)
if (saveModalBtn) {
  saveModalBtn.addEventListener("click", () => {
    // Collect all form data
    const productData = {
      productId: document.getElementById("modalProductId").value,
      sku: document.getElementById("modalSku").value,
      productName: document.getElementById("modalProductName").value,
      category: document.getElementById("modalCategory").value,
      price: document.getElementById("modalPrice").value,
      status: document.getElementById("modalStatus").value,
      expiryThreshold: document.getElementById("expiryThreshold").value,
      stockThreshold: document.getElementById("stockThreshold").value,
      notificationEmails: document.getElementById("notificationEmails").value,
      notifyExpiry: document.getElementById("notifyExpiry").checked,
      notifyLowStock: document.getElementById("notifyLowStock").checked,
      notifyOutOfStock: document.getElementById("notifyOutOfStock").checked
    };
    
    console.log("Saving product data:", productData);
    alert("Save functionality will be implemented with backend integration.");
    closeProductModal();
  });
}

// ========== END MODAL FUNCTIONS ==========
