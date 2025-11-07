
document.addEventListener('DOMContentLoaded', function() {
    initializeOrders();
});

let ordersCache = [];

function initializeOrders() {
    // Set current date
    const currentDate = new Date();
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    const dateEl = document.getElementById('currentDate');
    if (dateEl) dateEl.textContent = currentDate.toLocaleDateString('en-US', options);

    // Modal buttons
    const addOrderModal = document.getElementById("addOrderModal");
    const addOrderBtn = document.getElementById("addOrderBtn");
    const cancelOrderBtn = document.getElementById("cancelOrderBtn");
    const receiveOrderModal = document.getElementById("receiveOrderModal");
    const cancelReceiveBtn = document.getElementById("cancelReceiveBtn");

    if (addOrderBtn && addOrderModal) addOrderBtn.addEventListener("click", () => (addOrderModal.style.display = "flex"));
    if (cancelOrderBtn && addOrderModal) cancelOrderBtn.addEventListener("click", () => (addOrderModal.style.display = "none"));
    if (cancelReceiveBtn && receiveOrderModal) cancelReceiveBtn.addEventListener("click", () => (receiveOrderModal.style.display = "none"));

    window.onclick = (e) => {
        if (e.target === addOrderModal) addOrderModal.style.display = "none";
        if (e.target === receiveOrderModal) receiveOrderModal.style.display = "none";
    };

    // Filters and search
    const searchInput = document.getElementById('orderSearchInput');
    const statusFilter = document.getElementById('orderStatusFilter');

    if (searchInput) searchInput.addEventListener('input', renderFilteredOrders);
    if (statusFilter) statusFilter.addEventListener('change', renderFilteredOrders);

    // Load orders from API
    loadOrders();
    // Load products to populate Add Order modal select
    loadProducts();
}

async function loadProducts() {
    try {
        const res = await fetch('/api/products/');
        if (!res.ok) return console.error('Failed to load products', res.status);

        const data = await res.json();
        const products = Array.isArray(data) ? data : (data.results || []);

        const productSelect = document.getElementById('productName');
        const productIdInput = document.getElementById('productId');
        if (!productSelect) return;

        // Clear existing hardcoded options
        productSelect.innerHTML = '';

        const placeholder = document.createElement('option');
        placeholder.value = '';
        placeholder.textContent = 'Brandname & Generic name';
        productSelect.appendChild(placeholder);

        products.forEach(p => {
            const opt = document.createElement('option');
            const label = p.product_name || ((p.brand_name || '') + (p.generic_name ? ' (' + p.generic_name + ')' : ''));
            opt.value = p.product_id || p.productId || '';
            opt.textContent = label + (opt.value ? ` — ${opt.value}` : '');
            productSelect.appendChild(opt);
        });

        // Sync productId input when selection changes
        productSelect.addEventListener('change', function () {
            if (productIdInput) productIdInput.value = this.value || '';
        });
    } catch (err) {
        console.error('Error loading products:', err);
    }
}

async function loadOrders() {
    try {
        const res = await fetch('/api/orders/');
        if (!res.ok) {
            console.error('Failed to fetch orders', res.status);
            return;
        }

        const data = await res.json();
        // If API returns paginated results (results field) use it
        ordersCache = Array.isArray(data) ? data : (data.results || []);

        renderOrders(ordersCache);
        updateSummaryCounts(ordersCache);
    } catch (err) {
        console.error('Error loading orders:', err);
    }
}

function getStatusBadgeClass(status) {
    if (!status) return '';
    const s = status.toString().toLowerCase();
    switch (s) {
        case 'pending': return 'order-status pending';
        case 'received': return 'order-status received';
        case 'partially received':
        case 'partial': return 'order-status partial';
        case 'cancelled': return 'order-status cancelled';
        default: return 'order-status';
    }
}

function formatDateOnly(dateStr) {
    if (!dateStr) return '-';
    // If ISO datetime
    if (typeof dateStr === 'string' && dateStr.includes('T')) return dateStr.split('T')[0];

    const d = new Date(dateStr);
    if (!isNaN(d)) {
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        return d.toLocaleDateString('en-US', options);
    }

    // Fallback: strip trailing time (e.g. 'Oct 15, 2023 05:00 PM' -> 'Oct 15, 2023')
    const m = String(dateStr).match(/.*\d{4}/);
    if (m) return m[0].trim();
    return String(dateStr);
}

function renderFilteredOrders() {
    const searchInput = document.getElementById('orderSearchInput');
    const statusFilter = document.getElementById('orderStatusFilter');
    const q = searchInput ? searchInput.value.trim().toLowerCase() : '';
    const status = statusFilter ? statusFilter.value : 'all';

    const filtered = ordersCache.filter(o => {
        const matchesSearch = !q || (o.order_id && o.order_id.toLowerCase().includes(q)) || (o.ordered_by && o.ordered_by.toLowerCase().includes(q));
        const s = (o.status || '').toString().toLowerCase();
        const matchesStatus = status === 'all' || (status === 'partial' ? s.includes('partial') : s === status);
        return matchesSearch && matchesStatus;
    });

    renderOrders(filtered);
}

function renderOrders(orders) {
    const tbody = document.getElementById('orderTableBody');
    if (!tbody) return;
    tbody.innerHTML = '';

    if (!orders || orders.length === 0) {
        const emptyRow = document.createElement('tr');
        emptyRow.className = 'empty-row';
        emptyRow.innerHTML = '<td colspan="6">No orders found</td>';
        tbody.appendChild(emptyRow);
        return;
    }

    orders.forEach(order => {
        const tr = document.createElement('tr');
            const dateReceived = formatDateOnly(order.date_received);
        const statusBadge = `<span class="${getStatusBadgeClass(order.status)}">${order.status || '-'}</span>`;

        tr.innerHTML = `
            <td>${order.order_id || '-'}</td>
            <td>${order.ordered_by || '-'}</td>
                <td>${formatDateOnly(order.date_ordered)}</td>
            <td>${statusBadge}</td>
                <td>${dateReceived || '-'}</td>
            <td>
                <div class="op-buttons">
                    <button class="action-btn view-btn" onclick="toggleOrderItems(this)">
                        <i class="bi bi-eye"></i> View
                    </button>
                    <button class="action-btn receive-btn" onclick="openReceiveOrderModal('${order.order_id}')">
                        <i class="fas fa-truck-loading"></i> Receive Order
                    </button>
                </div>
            </td>
        `;

        tbody.appendChild(tr);

        // Order items row
        const itemsRow = document.createElement('tr');
        itemsRow.className = 'order-items-row hidden';
        const itemsTable = document.createElement('table');
        itemsTable.className = 'order-items-table';

        let itemsHTML = `
            <thead>
                <tr>
                    <th>Order Item ID</th>
                    <th>Product ID</th>
                    <th>Product Name</th>
                    <th>Quantity Ordered</th>
                </tr>
            </thead>
            <tbody>`;

        (order.items || []).forEach(item => {
            itemsHTML += `
                <tr>
                    <td>${item.order_item_id || '-'}</td>
                    <td>${item.product_id || '-'}</td>
                    <td>${item.product_name || (item.brand_name ? item.brand_name + ' ' + (item.generic_name || '') : '-')}</td>
                    <td>${item.quantity_ordered || '-'}</td>
                </tr>`;
        });

        itemsHTML += '</tbody>';
        itemsTable.innerHTML = itemsHTML;

        const td = document.createElement('td');
        td.colSpan = 6;
        td.appendChild(itemsTable);
        itemsRow.appendChild(td);

        tbody.appendChild(itemsRow);
    });
}

function toggleOrderItems(button) {
    const row = button.closest('tr');
    const orderItemsRow = row.nextElementSibling;
    if (!orderItemsRow) return;

    // Toggle the visibility of the order items row
    orderItemsRow.classList.toggle('hidden');

    // Update button text and icon based on state
    if (orderItemsRow.classList.contains('hidden')) {
        button.innerHTML = '<i class="bi bi-eye"></i> View';
    } else {
        button.innerHTML = '<i class="bi bi-eye-slash"></i> Hide';
    }
}

function updateSummaryCounts(orders) {
    const pendingEl = document.getElementById('pendingOrdersCount');
    const receivedEl = document.getElementById('receivedOrdersCount');

    const pending = (orders || []).filter(o => (o.status || '').toLowerCase() === 'pending').length;
    const received = (orders || []).filter(o => (o.status || '').toLowerCase() === 'received').length;

    if (pendingEl) pendingEl.textContent = String(pending).padStart(2, '0');
    if (receivedEl) receivedEl.textContent = String(received).padStart(2, '0');
}

function openReceiveOrderModal(orderId) {
    const order = ordersCache.find(o => o.order_id === orderId);
    if (!order) {
        // try fetching single order
        fetch(`/api/orders/${orderId}/`).then(r => r.json()).then(d => {
            if (d) showReceiveModal(d);
        }).catch(err => console.error('Failed to load order:', err));
        return;
    }

    showReceiveModal(order);
}

function showReceiveModal(order) {
    const receiveOrderContent = document.getElementById('receiveOrderContent');
    if (!receiveOrderContent) return;

    // items from serializer include order_item_id, product_name, quantity_ordered
    const items = order.items || [];
    const totalOrdered = items.reduce((sum, it) => sum + (it.quantity_ordered || 0), 0);

    let formHTML = `
        <div class="receipt-header">
            <div class="receipt-title">ORDER RECEIVING DOCUMENT</div>
            <div class="receipt-subtitle">Inventory System</div>
        </div>
        <div class="receipt-divider"></div>
        <div class="receipt-info">
            <div class="receipt-info-row">
                <span class="receipt-info-label">Order ID:</span>
                <span>${order.order_id || '-'}</span>
            </div>
            <div class="receipt-info-row">
                <span class="receipt-info-label">Ordered By:</span>
                <span>${order.ordered_by || '-'}</span>
            </div>
            <div class="receipt-info-row">
                <span class="receipt-info-label">Date Ordered:</span>
                    <span>${formatDateOnly(order.date_ordered)}</span>
            </div>
        </div>
        <div class="receipt-divider"></div>
        <table class="receipt-table">
            <thead>
                <tr>
                    <th>Item ID</th>
                    <th>Product</th>
                    <th>Ordered</th>
                    <th>Received</th>
                </tr>
            </thead>
            <tbody>`;

    items.forEach((item, index) => {
        formHTML += `
            <tr>
                <td>${item.order_item_id || '-'}</td>
                <td>${item.product_name || (item.brand_name ? item.brand_name + ' ' + (item.generic_name || '') : '-')}</td>
                <td>${item.quantity_ordered || 0}</td>
                <td>
                    <input type="number" id="receivedQty${index}" value="0" min="0" max="${item.quantity_ordered || 0}">
                </td>
            </tr>`;
    });

    formHTML += `
            </tbody>
        </table>
        <div class="receipt-divider"></div>
        <div class="receipt-summary">
            <div class="receipt-info-row">
                <span class="receipt-info-label">Total Items Ordered:</span>
                <span>${items.length}</span>
            </div>
            <div class="receipt-info-row">
                <span class="receipt-info-label receipt-total">Total Quantity Ordered:</span>
                <span class="receipt-total">${totalOrdered}</span>
            </div>
        </div>
        <div class="receipt-divider"></div>
        <div class="receipt-info">
            <div class="receipt-info-row">
                <span class="receipt-info-label">Received By:</span>
                <span><input type="text" id="receivedBy" placeholder="Enter name" style="border: none; border-bottom: 1px solid var(--border); width: 150px; text-align: right;"></span>
            </div>
            <div class="receipt-info-row">
                <span class="receipt-info-label">Date Received:</span>
                <span><input type="date" id="dateReceived" value="${new Date().toISOString().split('T')[0]}" style="border: none; border-bottom: 1px solid var(--border); width: 150px; text-align: right;"></span>
            </div>
        </div>
        <div class="receipt-footer">
            <div>Generated on ${new Date().toLocaleDateString()}</div>
        </div>`;

    receiveOrderContent.innerHTML = formHTML;
    document.getElementById('receiveOrderModal').style.display = 'flex';
}