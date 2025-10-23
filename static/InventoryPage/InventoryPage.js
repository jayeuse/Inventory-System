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

// Toggle batch details function
function toggleBatches(stockId) {
  const batchRow = document.getElementById(`stockslist_batches-${stockId}`);
  const icon = document.getElementById(`stockslist_icon-${stockId}`);
  const expandBtn = icon.closest(".expand-btn");

  if (batchRow.style.display === "none" || batchRow.style.display === "") {
    batchRow.style.display = "table-row";
    expandBtn.classList.add("expanded");
  } else {
    batchRow.style.display = "none";
    expandBtn.classList.remove("expanded");
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

// Save Batch Edit
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
