document.addEventListener('DOMContentLoaded', function() {
    // Product Status Tab navigation functionality
    const productTabs = document.querySelectorAll('.product-tab');
    const productTabContents = document.querySelectorAll('.product-tab-content');
    
    productTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const tabId = this.getAttribute('data-product-tab');
            
            // Remove active class from all tabs and contents
            productTabs.forEach(t => t.classList.remove('active'));
            productTabContents.forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked tab and corresponding content
            this.classList.add('active');
            document.getElementById(`productmanagement_${tabId}ProductsContent`).classList.add('active');
        });
    });

    // System Settings Tab navigation functionality
    const tabs = document.querySelectorAll('.tab');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const url = this.getAttribute('data-url');
            
            // If the tab has a URL, navigate to it
            if (url) {
                window.location.href = url;
            }
        });
    });

    // Add Product button functionality
    const addProductBtn = document.getElementById('productmanagement_addProductBtn');
    const addModal = document.getElementById('productmanagement_addProductModal');
    const closeModalBtn = document.getElementById('productmanagement_closeModalBtn');
    const cancelBtn = document.getElementById('productmanagement_cancelBtn');
    
    if (addProductBtn) {
        addProductBtn.addEventListener('click', function() {
            addModal.style.display = 'flex';
        });
    }

    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', function() {
            addModal.style.display = 'none';
        });
    }

    if (cancelBtn) {
        cancelBtn.addEventListener('click', function() {
            addModal.style.display = 'none';
        });
    }

    // Save Product button
    const saveProductBtn = document.getElementById('productmanagement_saveProductBtn');
    if (saveProductBtn) {
        saveProductBtn.addEventListener('click', function() {
            // Save logic will be implemented here
        });
    }

    // Edit Product Modal functionality
    const editModal = document.getElementById('productmanagement_editProductModal');
    const closeEditModalBtn = document.getElementById('productmanagement_closeEditModalBtn');
    const cancelEditBtn = document.getElementById('productmanagement_cancelEditBtn');
    
    if (closeEditModalBtn) {
        closeEditModalBtn.addEventListener('click', function() {
            editModal.style.display = 'none';
        });
    }

    if (cancelEditBtn) {
        cancelEditBtn.addEventListener('click', function() {
            editModal.style.display = 'none';
        });
    }

    // Update Product button
    const updateProductBtn = document.getElementById('productmanagement_updateProductBtn');
    if (updateProductBtn) {
        updateProductBtn.addEventListener('click', function() {
            // Update logic will be implemented here
        });
    }

    // Close modals when clicking outside
    window.onclick = function(event) {
        if (event.target === addModal) {
            addModal.style.display = 'none';
        }
        if (event.target === editModal) {
            editModal.style.display = 'none';
        }
    };

    // Edit button functionality
    const editButtons = document.querySelectorAll('.edit-btn');
    editButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const row = this.closest('tr');
            const productId = row.cells[0].textContent;
            const brandName = row.cells[1].textContent;
            const genericName = row.cells[2].textContent;
            const category = row.cells[3].textContent;
            const subcategory = row.cells[4].textContent;
            const unitPrice = row.cells[5].textContent; // e.g., "₱10.00 / piece"
            const lowStockThreshold = row.cells[6].textContent; // e.g., "50 units"
            const expiryThreshold = row.cells[7].textContent; // e.g., "30 days"
            
            // Parse unit price to extract price and unit
            const priceMatch = unitPrice.match(/₱([\d.]+)\s*\/\s*(.+)/);
            const price = priceMatch ? priceMatch[1] : '';
            const unit = priceMatch ? priceMatch[2].trim() : '';
            
            // Parse thresholds to extract numeric values
            const lowStockMatch = lowStockThreshold.match(/(\d+)/);
            const lowStock = lowStockMatch ? lowStockMatch[1] : '';
            const expiryMatch = expiryThreshold.match(/(\d+)/);
            const expiry = expiryMatch ? expiryMatch[1] : '';
            
            // Populate the edit modal with current values
            document.getElementById('productmanagement_editBrandName').value = brandName;
            document.getElementById('productmanagement_editGenericName').value = genericName;
            document.getElementById('productmanagement_editPrice').value = price;
            
            // Set unit of measurement text input
            const unitInput = document.getElementById('productmanagement_editUnitOfMeasurement');
            if (unitInput) {
                unitInput.value = unit;
            }
            
            // Set notification settings
            document.getElementById('productmanagement_editLowStockThreshold').value = lowStock;
            document.getElementById('productmanagement_editExpiryThreshold').value = expiry;
            
            // Open edit modal
            editModal.style.display = 'flex';
        });
    });

    // Archive button functionality
    const archiveModal = document.getElementById('productmanagement_archiveModal');
    const closeArchiveModalBtn = document.getElementById('productmanagement_closeArchiveModalBtn');
    const cancelArchiveBtn = document.getElementById('productmanagement_cancelArchiveBtn');
    const confirmArchiveBtn = document.getElementById('productmanagement_confirmArchiveBtn');
    const archiveReasonInput = document.getElementById('productmanagement_archiveReason');
    const archiveProductNameSpan = document.getElementById('productmanagement_archiveProductName');
    
    // Unarchive Modal Elements
    const unarchiveModal = document.getElementById('productmanagement_unarchiveModal');
    const closeUnarchiveModalBtn = document.getElementById('productmanagement_closeUnarchiveModalBtn');
    const cancelUnarchiveBtn = document.getElementById('productmanagement_cancelUnarchiveBtn');
    const confirmUnarchiveBtn = document.getElementById('productmanagement_confirmUnarchiveBtn');
    const unarchiveProductNameSpan = document.getElementById('productmanagement_unarchiveProductName');
    
    let currentArchiveProductId = null;
    let currentArchiveProductName = null;
    let currentUnarchiveProductId = null;
    let currentUnarchiveProductName = null;
    
    const archiveButtons = document.querySelectorAll('.archive-btn');
    archiveButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const row = this.closest('tr');
            currentArchiveProductId = row.cells[0].textContent;
            currentArchiveProductName = row.cells[1].textContent;
            
            // Set product name in modal
            archiveProductNameSpan.textContent = `${currentArchiveProductName} (${currentArchiveProductId})`;
            
            // Clear previous reason
            archiveReasonInput.value = '';
            
            // Open archive modal
            archiveModal.style.display = 'flex';
        });
    });

    if (closeArchiveModalBtn) {
        closeArchiveModalBtn.addEventListener('click', function() {
            archiveModal.style.display = 'none';
        });
    }

    if (cancelArchiveBtn) {
        cancelArchiveBtn.addEventListener('click', function() {
            archiveModal.style.display = 'none';
        });
    }

    if (confirmArchiveBtn) {
        confirmArchiveBtn.addEventListener('click', function() {
            const reason = archiveReasonInput.value.trim();
            
            if (!reason) {
                alert('Please provide a reason for archiving.');
                archiveReasonInput.focus();
                return;
            }
            
            // Archive logic will be implemented here
            
            archiveModal.style.display = 'none';
        });
    }

    // Unarchive button functionality
    const unarchiveButtons = document.querySelectorAll('.unarchive-btn');
    unarchiveButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const row = this.closest('tr');
            currentUnarchiveProductId = row.cells[0].textContent;
            currentUnarchiveProductName = row.cells[1].textContent;
            
            // Set product name in modal
            unarchiveProductNameSpan.textContent = `${currentUnarchiveProductName} (${currentUnarchiveProductId})`;
            
            // Open unarchive modal
            unarchiveModal.style.display = 'flex';
        });
    });

    if (closeUnarchiveModalBtn) {
        closeUnarchiveModalBtn.addEventListener('click', function() {
            unarchiveModal.style.display = 'none';
        });
    }

    if (cancelUnarchiveBtn) {
        cancelUnarchiveBtn.addEventListener('click', function() {
            unarchiveModal.style.display = 'none';
        });
    }

    if (confirmUnarchiveBtn) {
        confirmUnarchiveBtn.addEventListener('click', function() {
            // Unarchive logic will be implemented here
            
            unarchiveModal.style.display = 'none';
        });
    }

    // Pagination functionality
    const prevBtn = document.getElementById('productmanagement_prevBtn');
    const nextBtn = document.getElementById('productmanagement_nextBtn');
    const archivedPrevBtn = document.getElementById('productmanagement_archivedPrevBtn');
    const archivedNextBtn = document.getElementById('productmanagement_archivedNextBtn');

    if (prevBtn) {
        prevBtn.addEventListener('click', function() {
            // Previous page logic will be implemented here
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', function() {
            // Next page logic will be implemented here
        });
    }

    if (archivedPrevBtn) {
        archivedPrevBtn.addEventListener('click', function() {
            // Previous page logic will be implemented here
        });
    }

    if (archivedNextBtn) {
        archivedNextBtn.addEventListener('click', function() {
            // Next page logic will be implemented here
        });
    }

    // Close modals when clicking outside
    window.onclick = function(event) {
        if (event.target === addModal) {
            addModal.style.display = 'none';
        }
        if (event.target === editModal) {
            editModal.style.display = 'none';
        }
        if (event.target === archiveModal) {
            archiveModal.style.display = 'none';
        }
        if (event.target === unarchiveModal) {
            unarchiveModal.style.display = 'none';
        }
    };
});
