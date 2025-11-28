document.addEventListener("DOMContentLoaded", function () {
  // Tab navigation functionality
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

  // Stocks pagination functionality
  const prevBtn = document.getElementById("stockslist_prevBtn");
  const nextBtn = document.getElementById("stockslist_nextBtn");

  if (prevBtn) {
    prevBtn.addEventListener("click", function () {
      // Previous page logic will be implemented here
      console.log("Previous page clicked");
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener("click", function () {
      // Next page logic will be implemented here
      console.log("Next page clicked");
    });
  }
});

// Toggle batch details function with smooth animation
function toggleBatches(stockId) {
  const batchRow = document.getElementById(`stockslist_batches-${stockId}`);
  const batchContainer = batchRow.querySelector('.batch-container');
  const icon = document.getElementById(`stockslist_icon-${stockId}`);
  const expandBtn = icon.closest(".expand-btn");
  const stockRow = expandBtn.closest('tr');
  const tableContainer = document.querySelector('.table-container');

  const isExpanded = batchRow.style.display === "table-row";

  if (!isExpanded) {
    // Expanding
    batchRow.style.display = "table-row";
    expandBtn.classList.add("expanded");
    
    // Trigger reflow to enable transition
    void batchContainer.offsetHeight;
    
    batchContainer.classList.add("expanded");
    batchRow.classList.add("expanded");
    
    // Load batches if needed
    if (typeof loadBatches === 'function') {
      loadBatches(stockId);
    }
    
    // Smooth scroll to show the expanded content
    setTimeout(() => {
      const rowTop = stockRow.offsetTop;
      const containerScroll = tableContainer.scrollTop;
      const containerHeight = tableContainer.clientHeight;
      const batchHeight = batchRow.offsetHeight;
      
      // Check if batch details are not fully visible
      if (rowTop + batchHeight > containerScroll + containerHeight) {
        tableContainer.scrollTo({
          top: rowTop - 100,
          behavior: 'smooth'
        });
      }
    }, 100);
  } else {
    // Collapsing
    expandBtn.classList.remove("expanded");
    batchContainer.classList.remove("expanded");
    batchRow.classList.remove("expanded");
    
    // Wait for transition to complete before hiding
    setTimeout(() => {
      batchRow.style.display = "none";
    }, 400);
  }
}

// Open Edit Batch Modal
function stockslist_openEditBatchModal(batchId, onHand, sku, expiryDate) {
  const modal = document.getElementById("stockslist_editBatchModal");

  // Populate modal fields
  document.getElementById("stockslist_edit_batchId").value = batchId;
  document.getElementById("stockslist_edit_onHand").value = parseInt(onHand);
  document.getElementById("stockslist_edit_sku").value = sku;
  document.getElementById("stockslist_edit_expiryDate").value = expiryDate;
  document.getElementById("stockslist_edit_remarks").value = "";

  // Show modal
  modal.classList.add("active");
}

// Close Edit Batch Modal
function stockslist_closeEditBatchModal() {
  const modal = document.getElementById("stockslist_editBatchModal");
  modal.classList.remove("active");

  // Clear form
  document.getElementById("stockslist_edit_batchId").value = "";
  document.getElementById("stockslist_edit_onHand").value = "";
  document.getElementById("stockslist_edit_sku").value = "";
  document.getElementById("stockslist_edit_expiryDate").value = "";
  document.getElementById("stockslist_edit_remarks").value = "";
}

// Save Batch Edit (unused)
function stockslist_saveBatchEdit() {
  const batchId = document.getElementById("stockslist_edit_batchId").value;
  const onHand = document.getElementById("stockslist_edit_onHand").value;
  const sku = document.getElementById("stockslist_edit_sku").value;
  const expiryDate = document.getElementById(
    "stockslist_edit_expiryDate"
  ).value;
  const remarks = document
    .getElementById("stockslist_edit_remarks")
    .value.trim();

  // Validate required fields
  if (!onHand || !sku || !expiryDate) {
    alert("Please fill in all required fields.");
    return;
  }

  // Validate remarks
  if (!remarks) {
    alert("Please provide a reason/remarks for editing this batch.");
    return;
  }

  // Backend integration would go here
  // For now, just log and close
  console.log("Batch Edit:", {
    batchId: batchId,
    onHand: onHand,
    sku: sku,
    expiryDate: expiryDate,
    remarks: remarks,
  });

  alert("Batch details updated successfully!");
  stockslist_closeEditBatchModal();
}
