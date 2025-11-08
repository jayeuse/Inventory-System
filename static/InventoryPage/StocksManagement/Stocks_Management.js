document.addEventListener("DOMContentLoaded", function(){
  console.log("Stocks Management Script loaded");

  // Pagination variables
  let allStocks = [];
  let currentPage = 1;
  const recordsPerPage = 8;

  // Filter/Search variables
  let currentSearchTerm = '';
  let currentStatusFilter = 'all';


  async function loadStocks() {
    console.log("Reloading Stocks...");
    try{
      const response = await fetch('/api/product-stocks/');
      const data = await response.json();
      
      // Store all stocks
      allStocks = data;
      
      // Display current page
      displayStocks();
    } catch (error){
      console.error("Network Error: ", error)
    }
  }

  function displayStocks() {
    const tbody = document.getElementById("stocks-table-body");
    tbody.innerHTML = ``;

    // Apply search and filter
    let filteredStocks = allStocks.filter(stock => {
      // Search filter
      const matchesSearch = 
        stock.stock_id.toLowerCase().includes(currentSearchTerm.toLowerCase()) ||
        stock.product_id.toLowerCase().includes(currentSearchTerm.toLowerCase()) ||
        stock.product_name.toLowerCase().includes(currentSearchTerm.toLowerCase());
      
      // Status filter - normalize both values to compare
      const normalizedStockStatus = stock.status.toLowerCase().replace(/\s+/g, '-');
      const normalizedFilterStatus = currentStatusFilter.toLowerCase();
      const matchesStatus = currentStatusFilter === 'all' || 
        normalizedStockStatus === normalizedFilterStatus;
      
      return matchesSearch && matchesStatus;
    });

    // Calculate pagination based on filtered results
    const totalPages = Math.ceil(filteredStocks.length / recordsPerPage);
    const startIndex = (currentPage - 1) * recordsPerPage;
    const endIndex = startIndex + recordsPerPage;
    const paginatedStocks = filteredStocks.slice(startIndex, endIndex);

    // If no stocks match filter, show message
    if (filteredStocks.length === 0) {
      const row = document.createElement("tr");
      row.innerHTML = `<td colspan="6" style="text-align: center; padding: 40px; color: var(--muted);">No stocks found.</td>`;
      tbody.appendChild(row);
    } else {
      // Render exactly 8 rows (actual data + placeholders)
      for (let i = 0; i < recordsPerPage; i++) {
        if (i < paginatedStocks.length) {
          // Actual stock data
          const stock = paginatedStocks[i];
          const row = document.createElement("tr");
          row.classList.add("stock-row");

          row.innerHTML = `
            <td>
              <button class="expand-btn" onclick="toggleBatches('${stock.stock_id}')">
                <i class="fas fa-chevron-right" id="stockslist_icon-${stock.stock_id}"></i>
              </button>
            </td>
            <td>${stock.stock_id}</td>
            <td>${stock.product_id}</td>
            <td>${stock.product_name}</td>
            <td>${stock.total_on_hand}</td>
            <td>
              <span class="${getStockStatusClass(stock.status)}">${stock.status}</span>
            </td>
          `;

          tbody.appendChild(row);

          const batchRow = document.createElement("tr");
          batchRow.classList.add("batch-details");
          batchRow.id = `stockslist_batches-${stock.stock_id}`;
          batchRow.style.display = 'none';

          batchRow.innerHTML = `
            <td colspan="6">
              <div class="batch-container">
                <h4>Batch Details for ${stock.stock_id}</h4>
                <table class="batch-table">
                  <thead>
                    <tr>
                      <th>Batch ID</th>
                      <th>On Hand (per batch)</th>
                      <th>SKU</th>
                      <th>Expiry Date</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody id="batches-table-body">
                  <tr>
                    <td colspan="6">
                    <em>No batch data loaded.</em>
                    </td>
                  </tr>
                  </tbody>
                </table>
              </div>
            </td>
          `;

          tbody.appendChild(batchRow);
        } else {
          // Empty placeholder row
          const row = document.createElement("tr");
          row.classList.add("stock-row");
          row.innerHTML = `
            <td></td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
            <td>-</td>
          `;
          row.style.opacity = '0.4';
          tbody.appendChild(row);
        }
      }
    }

    // Update pagination buttons
    updatePaginationButtons(currentPage, totalPages);
  }

  function updatePaginationButtons(current, total) {
  const prevBtn = document.getElementById('stockslist_prevBtn');
  const nextBtn = document.getElementById('stockslist_nextBtn');

    if (prevBtn && nextBtn) {
      prevBtn.disabled = current === 1;
      nextBtn.disabled = current === total || total === 0;
    }
  }

  // Pagination event listeners
  document.getElementById('stockslist_prevBtn')?.addEventListener('click', function() {
    if (currentPage > 1) {
      currentPage--;
      displayStocks();
    }
  });

  document.getElementById('stockslist_nextBtn')?.addEventListener('click', function() {
    const totalPages = Math.ceil(allStocks.length / recordsPerPage);
    if (currentPage < totalPages) {
      currentPage++;
      displayStocks();
    }
  });

  loadStocks();

  // Search functionality
  const searchInput = document.getElementById('stockslist_searchInput');
  if (searchInput) {
    searchInput.addEventListener('input', function() {
      currentSearchTerm = this.value;
      currentPage = 1; // Reset to first page
      displayStocks();
    });
  }

  // Status filter functionality
  const statusFilter = document.getElementById('stockslist_statusFilter');
  if (statusFilter) {
    statusFilter.addEventListener('change', function() {
      currentStatusFilter = this.value;
      currentPage = 1; // Reset to first page
      displayStocks();
    });
  }

  document.getElementById("stockslist_saveBachEditBtn").addEventListener('click', async function() {
    const batch_id = document.getElementById("stockslist_edit_batchId").value;
    const on_hand = document.getElementById("stockslist_edit_onHand").value;
    const sku = document.getElementById("stockslist_edit_sku");
    const expiry_date = document.getElementById("stockslist_edit_expiryDate").value;
    const remarks = document.getElementById("stockslist_edit_remarks").value.trim();

    const data = {
      on_hand: on_hand,
      expiry_date: expiry_date
    }

    if (!on_hand || !sku || !expiry_date){
      alert("Please fill in all required fields.");
      return;
    }
    if (!remarks){
      alert("Please provide a reason/remarks for editing this batch.");
      return;
    }

    try {
      const response = await fetch(`/api/product-batches/${batch_id}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error("API Error:", response.status, response.statusText, errorData);
        console.log(batch_id);
        return;
      }

      if (response.ok){
        alert("Batch details updated Successfully!");
        stockslist_closeEditBatchModal();
        loadStocks();
      } else {
        const errorData = await response.json();
        console.error("Error: " + JSON.stringify(errorData));
      }
    } catch (error){
      console.error("Network Error: ", error)
    }

  });
})

async function loadBatches(stockId){
  console.log("Loading Batches for: ", stockId);

  try {
    const response = await fetch (`/api/product-batches/?stock_id=${stockId}`);
    const data = await response.json();

    const batchContainer = document.getElementById(`stockslist_batches-${stockId}`);
    const tbody = batchContainer.querySelector("#batches-table-body");  
    
    if (!tbody) {
      console.error("Could not find tbody for stock:", stockId);
      return;
    }
    tbody.innerHTML = ``;

    const filtered = data.filter(batch => batch.stock_id === stockId);
    filtered.forEach(batch => {
      const row = document.createElement("tr");

      row.innerHTML = `
        <td>${batch.batch_id}</td>
        <td>${batch.on_hand}</td>
        <td>SKU PLACEHOLDER</td>
        <td>${batch.expiry_date}</td>
        <td>
          <span class="${getBatchStatusClass(batch.status)}">${batch.status}</span>
        </td>
        <td>
          <button
            class="action-btn edit-btn" onclick="stockslist_openEditBatchModal('${batch.batch_id}', ${batch.on_hand}, 'SKU PLACEHOLDER', '${batch.expiry_date}')">
            <i class="bi bi-pencil"></i> Edit
          </button>
        </td>
      `;

      tbody.appendChild(row);
    })

    console.log(`Loaded ${data.length} batches for ${stockId}`);
  } catch (error){
    console.error("Network Error: ", error)

    const batchContainer = document.getElementById(`stockslist_batches-${stockId}`);
    const tbody = batchContainer.querySelector("#batches-table-body");
    
    if (tbody) {
      tbody.innerHTML = `
        <tr>
          <td colspan="6" style="text-align: center; color: red;">
            <em>Error loading batches. Please try again.</em>
          </td>
        </tr>
      `;
    }
  }
}

function getStockStatusClass(status) {
  switch (status.toLowerCase()) {
    case "normal":
      return "status-badge status-normal";
    case "low stock":
    case "low-stock":
      return "status-badge status-low-stock";
    case "near expiry":
    case "near-expiry":
      return "status-badge status-near-expiry";
    case "out of stock":
    case "out-of-stock":
      return "status-badge status-out-of-stock";
    case "expired":
      return "status-badge status-expired";
    default:
      return "status-badge";
  }
}

function getBatchStatusClass(status) {
  switch (status.toLowerCase()) {
    case "normal":
      return "batch-status status-normal";
    case "low stock":
    case "low-stock":
      return "batch-status status-low-stock";
    case "near expiry":
    case "near-expiry":
      return "batch-status status-near-expiry";
    case "out of stock":
    case "out-of-stock":
      return "batch-status status-out-of-stock";
    case "expired":
      return "batch-status status-expired";
    default:
      return "batch-status";
  }
}