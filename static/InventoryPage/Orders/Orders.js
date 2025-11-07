
document.addEventListener('DOMContentLoaded', function() {
    initializeOrders();
});

let ordersCache = [];
let ordersNext = null;
let ordersPrev = null;
let filteredOrders = null;
let pageSize = 5;
let currentPage = 1;

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

    // Load orders from API (5 per page)
    loadOrders();
    // Load products to populate Add Order modal select
    loadProducts();

    // Make summary counts clickable to filter the list
    const pendingEl = document.getElementById('pendingOrdersCount');
    const receivedEl = document.getElementById('receivedOrdersCount');
    const partialEl = document.getElementById('partialOrdersCount');
    if (pendingEl) pendingEl.addEventListener('click', () => applySummaryFilter('pending'));
    if (receivedEl) receivedEl.addEventListener('click', () => applySummaryFilter('received'));
    if (partialEl) partialEl.addEventListener('click', () => applySummaryFilter('partial'));

    // Also make the entire stat card clickable (not just the number)
    try {
        if (pendingEl) {
            const pCard = pendingEl.closest('.massive-stat-item');
            if (pCard) {
                pCard.tabIndex = 0;
                pCard.setAttribute('role', 'button');
                pCard.addEventListener('click', () => applySummaryFilter('pending'));
                pCard.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') applySummaryFilter('pending'); });
            }
        }
        if (receivedEl) {
            const rCard = receivedEl.closest('.massive-stat-item');
            if (rCard) {
                rCard.tabIndex = 0;
                rCard.setAttribute('role', 'button');
                rCard.addEventListener('click', () => applySummaryFilter('received'));
                rCard.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') applySummaryFilter('received'); });
            }
        }
        if (partialEl) {
            const paCard = partialEl.closest('.massive-stat-item');
            if (paCard) {
                paCard.tabIndex = 0;
                paCard.setAttribute('role', 'button');
                paCard.addEventListener('click', () => applySummaryFilter('partial'));
                paCard.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') applySummaryFilter('partial'); });
            }
        }
    } catch (err) {
        // defensive: if DOM shape differs, ignore
        console.warn('Could not attach stat card handlers', err);
    }

    // Clicking the header restores default (no filter)
    const summaryAll = document.getElementById('summaryAll');
    if (summaryAll) {
        summaryAll.addEventListener('click', () => applySummaryFilter('all'));
        summaryAll.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') applySummaryFilter('all'); });
    }
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
    // Fetch all orders from the API by following paginated 'next' links.
    try {
        let url = '/api/orders/';
        let all = [];

        while (url) {
            const res = await fetch(url);
            if (!res.ok) {
                console.error('Failed to fetch orders', res.status);
                return;
            }

            const data = await res.json();
            if (Array.isArray(data)) {
                all = data;
                url = null;
            } else {
                all = all.concat(data.results || []);
                url = data.next || null;
            }
        }

        ordersCache = all;
        filteredOrders = null;
        currentPage = 1;

        updateSummaryCounts(ordersCache);
    renderPage();
    // default highlight: show all
    setActiveSummaryHighlight('all');
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

    // Try parsing as a Date for most formats (ISO, locale strings, etc.)
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

    filteredOrders = ordersCache.filter(o => {
        const matchesSearch = !q || (o.order_id && o.order_id.toLowerCase().includes(q)) || (o.ordered_by && o.ordered_by.toLowerCase().includes(q));
        const s = (o.status || '').toString().toLowerCase();
        const matchesStatus = status === 'all' || (status === 'partial' ? s.includes('partial') : s === status);
        return matchesSearch && matchesStatus;
    });

    currentPage = 1;
    renderPage();
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

function renderPage() {
    const list = filteredOrders || ordersCache || [];
    const total = list.length;
    const totalPages = Math.max(1, Math.ceil(total / pageSize));

    if (currentPage < 1) currentPage = 1;
    if (currentPage > totalPages) currentPage = totalPages;

    const start = (currentPage - 1) * pageSize;
    const pageItems = list.slice(start, start + pageSize);

    renderOrders(pageItems);
    updatePaginationControls(totalPages);
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
    const partial = (orders || []).filter(o => (o.status || '').toString().toLowerCase().includes('partial')).length;

    if (pendingEl) pendingEl.textContent = String(pending).padStart(2, '0');
    if (receivedEl) receivedEl.textContent = String(received).padStart(2, '0');
    const partialEl = document.getElementById('partialOrdersCount');
    if (partialEl) partialEl.textContent = String(partial).padStart(2, '0');
}

function applySummaryFilter(status) {
    const searchInput = document.getElementById('orderSearchInput');
    const statusFilter = document.getElementById('orderStatusFilter');
    if (searchInput) searchInput.value = '';
    if (statusFilter) statusFilter.value = status;
    renderFilteredOrders();
}

// Enhance applySummaryFilter to also set visual active state
const originalApplySummaryFilter = applySummaryFilter;
applySummaryFilter = function(status) {
    // call original behavior
    originalApplySummaryFilter(status);
    // set active highlight
    setActiveSummaryHighlight(status);
};

function clearActiveSummaryHighlight() {
    document.querySelectorAll('.massive-stat-item').forEach(el => el.classList.remove('active-summary'));
    const header = document.getElementById('summaryAll');
    if (header) header.classList.remove('active-summary');
}

function setActiveSummaryHighlight(status) {
    clearActiveSummaryHighlight();
    if (status === 'all') {
        const header = document.getElementById('summaryAll');
        if (header) header.classList.add('active-summary');
        return;
    }

    const idMap = {
        'pending': 'pendingOrdersCount',
        'received': 'receivedOrdersCount',
        'partial': 'partialOrdersCount'
    };
    const el = document.getElementById(idMap[status]);
    if (el) {
        const parent = el.closest('.massive-stat-item');
        if (parent) parent.classList.add('active-summary');
    }
}

function openReceiveOrderModal(orderId) {
    const list = filteredOrders || ordersCache || [];
    const order = list.find(o => o.order_id === orderId) || ordersCache.find(o => o.order_id === orderId);
    if (order) {
        showReceiveModal(order);
        return;
    }

    // fallback: fetch single order
    fetch(`/api/orders/${orderId}/`).then(r => {
        if (!r.ok) throw new Error('Failed to fetch order');
        return r.json();
    }).then(d => {
        if (d) showReceiveModal(d);
    }).catch(err => console.error('Failed to load order:', err));
}

function showReceiveModal(order) {
    const receiveOrderContent = document.getElementById('receiveOrderContent');
    if (!receiveOrderContent) return;

    // items from serializer include order_item_id, product_name, quantity_ordered
    const items = order.items || [];
    const totalOrdered = items.reduce((sum, it) => sum + (it.quantity_ordered || 0), 0);
    const dateReceivedDisplay = order.date_received ? formatDateOnly(order.date_received) : '-';
    // Determine ISO value for date input (YYYY-MM-DD)
    let dateReceivedInputVal = new Date().toISOString().split('T')[0];
    if (order.date_received) {
        const d = new Date(order.date_received);
        if (!isNaN(d)) dateReceivedInputVal = d.toISOString().split('T')[0];
    }

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
                <span class="receipt-info-value">${dateReceivedDisplay}</span>
                <span><input type="date" id="dateReceived" value="${dateReceivedInputVal}" style="border: none; border-bottom: 1px solid var(--border); width: 150px; text-align: right;"></span>
            </div>
        </div>
        <div class="receipt-footer">
            <div>Generated on ${new Date().toLocaleDateString()}</div>
        </div>`;

    receiveOrderContent.innerHTML = formHTML;
    document.getElementById('receiveOrderModal').style.display = 'flex';
}

function updatePaginationControls(totalPages) {
    const prevBtn = document.getElementById('orderPrevBtn');
    const nextBtn = document.getElementById('orderNextBtn');
    const pageIndicator = document.getElementById('orderPageIndicator');

    if (prevBtn) {
        prevBtn.disabled = currentPage <= 1;
        prevBtn.onclick = function () {
            if (currentPage > 1) {
                currentPage -= 1;
                renderPage();
            }
        };
    }

    if (nextBtn) {
        nextBtn.disabled = currentPage >= totalPages;
        nextBtn.onclick = function () {
            if (currentPage < totalPages) {
                currentPage += 1;
                renderPage();
            }
        };
    }

    if (pageIndicator) {
        pageIndicator.textContent = `Page ${currentPage} / ${totalPages}`;
    }
}