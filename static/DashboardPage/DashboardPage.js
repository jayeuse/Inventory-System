// Dashboard JavaScript
let dashboard_categoryChart, dashboard_suppliersChart, dashboard_stockStatusChart;

document.addEventListener("DOMContentLoaded", function () {
  console.log("Dashboard initialized");
  dashboard_initializeInteractions();
});

function dashboard_initializeInteractions() {
  // Add smooth fade-in animation on load
  const cards = document.querySelectorAll(".stat-card, .chart-card, .table-wrapper");
  cards.forEach((card, index) => {
    card.style.opacity = "0";
    card.style.transform = "translateY(20px)";
    setTimeout(() => {
      card.style.transition = "opacity 0.5s ease, transform 0.5s ease";
      card.style.opacity = "1";
      card.style.transform = "translateY(0)";
    }, index * 100);
  });

  // Add click listeners to stat cards
  const statCards = document.querySelectorAll(".stat-card");
  statCards.forEach((card) => {
    card.style.cursor = "pointer";
    card.addEventListener("click", function () {
      const label = (this.querySelector(".stat-label").textContent || '').toLowerCase();
      // Navigate to Inventory main page when clicking product-related card
      if (label.includes('product')) {
        window.location.href = '/inventory/';
        return;
      }

      // Navigate to Orders tab inside Inventory when clicking pending orders
      if (label.includes('pending') && label.includes('order')) {
        // Use URL param so Inventory page can read and open Orders tab
        window.location.href = '/inventory/?tab=orders';
        return;
      }

      // Fallback: go to Inventory main page
      window.location.href = '/inventory/';
    });
  });
}

// ==================== UPDATE FUNCTIONS ====================

// Update stat cards: dashboard_updateStats({ totalProducts: 1247, pendingOrders: 12 })
function dashboard_updateStats(stats) {
  const totalProductsEl = document.getElementById('dashboard_totalProducts');
  const pendingOrdersEl = document.getElementById('dashboard_pendingOrders');
  
  if (stats.totalProducts !== undefined && totalProductsEl) {
    totalProductsEl.textContent = stats.totalProducts.toLocaleString();
    totalProductsEl.classList.remove('stat-loading');
  }
  if (stats.pendingOrders !== undefined && pendingOrdersEl) {
    pendingOrdersEl.textContent = stats.pendingOrders.toLocaleString();
    pendingOrdersEl.classList.remove('stat-loading');
  }
}

// Update category chart: dashboard_updateCategoryChart([{ category: "Name", quantity: 123 }, ...])
function dashboard_updateCategoryChart(data) {
  if (!dashboard_categoryChart) return;
  dashboard_categoryChart.data.labels = data.map(item => item.category);
  dashboard_categoryChart.data.datasets[0].data = data.map(item => item.quantity);
  dashboard_categoryChart.update();
}

// Update suppliers chart: dashboard_updateSuppliersChart([{ supplier: "Name", productCount: 123 }, ...])
function dashboard_updateSuppliersChart(data) {
  if (!dashboard_suppliersChart) return;
  dashboard_suppliersChart.data.labels = data.map(item => item.supplier);
  dashboard_suppliersChart.data.datasets[0].data = data.map(item => item.productCount);
  dashboard_suppliersChart.update();
}

// Update stock status chart: dashboard_updateStockStatusChart({ normal: 856, lowStock: 124, outOfStock: 35, nearExpiry: 89, expired: 18 })
function dashboard_updateStockStatusChart(data) {
  if (!dashboard_stockStatusChart) return;
  dashboard_stockStatusChart.data.datasets[0].data = [
    data.normal, 
    data.lowStock, 
    data.outOfStock, 
    data.nearExpiry, 
    data.expired
  ];
  dashboard_stockStatusChart.update();
}

// Update activity table: dashboard_updateActivityTable([{ type: "in", product: "Name", quantity: "500", date: "2025-10-21" }, ...])
function dashboard_updateActivityTable(activities) {
  const tbody = document.getElementById("dashboard_activityTableBody");
  if (!tbody) return;
  
  tbody.innerHTML = "";
  activities.forEach(activity => {
    const badgeClass = activity.type === "in" ? "badge-in" : "badge-out";
    const badgeText = activity.type === "in" ? "Stock In" : "Stock Out";
    const row = `
      <tr>
        <td><span class="activity-badge ${badgeClass}">${badgeText}</span></td>
        <td>${activity.product}</td>
        <td>${activity.quantity}</td>
        <td>${activity.date}</td>
      </tr>
    `;
    tbody.innerHTML += row;
  });
}

// Store chart instances (called from HTML after chart creation)
function dashboard_setChartInstances(categoryChart, suppliersChart, stockStatusChart) {
  dashboard_categoryChart = categoryChart;
  dashboard_suppliersChart = suppliersChart;
  dashboard_stockStatusChart = stockStatusChart;
}

