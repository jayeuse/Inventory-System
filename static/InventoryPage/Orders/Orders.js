
document.addEventListener('DOMContentLoaded', function() {
    // Set current date
    const currentDate = new Date();
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    document.getElementById('currentDate').textContent = currentDate.toLocaleDateString('en-US', options);

    // Modal functionality for orders
    const addOrderModal = document.getElementById("addOrderModal");
    const addOrderBtn = document.getElementById("addOrderBtn");
    const cancelOrderBtn = document.getElementById("cancelOrderBtn");
    
    const receiveOrderModal = document.getElementById("receiveOrderModal");
    const cancelReceiveBtn = document.getElementById("cancelReceiveBtn");
    
    addOrderBtn.addEventListener("click", () => (addOrderModal.style.display = "flex"));
    cancelOrderBtn.addEventListener("click", () => (addOrderModal.style.display = "none"));
    cancelReceiveBtn.addEventListener("click", () => (receiveOrderModal.style.display = "none"));
    
    window.onclick = (e) => {
        if (e.target === addOrderModal) addOrderModal.style.display = "none";
        if (e.target === receiveOrderModal) receiveOrderModal.style.display = "none";
    };
});

function initializeOrders() {
    // Set current date
    const currentDate = new Date();
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    document.getElementById('currentDate').textContent = currentDate.toLocaleDateString('en-US', options);

    // Modal functionality for orders
    const addOrderModal = document.getElementById("addOrderModal");
    const addOrderBtn = document.getElementById("addOrderBtn");
    const cancelOrderBtn = document.getElementById("cancelOrderBtn");
    
    const receiveOrderModal = document.getElementById("receiveOrderModal");
    const cancelReceiveBtn = document.getElementById("cancelReceiveBtn");
    
    addOrderBtn.addEventListener("click", () => (addOrderModal.style.display = "flex"));
    cancelOrderBtn.addEventListener("click", () => (addOrderModal.style.display = "none"));
    cancelReceiveBtn.addEventListener("click", () => (receiveOrderModal.style.display = "none"));
    
    window.onclick = (e) => {
        if (e.target === addOrderModal) addOrderModal.style.display = "none";
        if (e.target === receiveOrderModal) receiveOrderModal.style.display = "none";
    };
}

function toggleOrderItems(button) {
    const row = button.closest('tr');
    const orderItemsRow = row.nextElementSibling;
    
    // Toggle the visibility of the order items row
    orderItemsRow.classList.toggle('hidden');
    
    // Update button text and icon based on state
    if (orderItemsRow.classList.contains('hidden')) {
        button.innerHTML = '<i class="bi bi-eye"></i> View';
    } else {
        button.innerHTML = '<i class="bi bi-eye-slash"></i> Hide';
    }
}

function openReceiveOrderModal(orderId) {
    // Sample data for demonstration
    const orderData = {
        'ORD-001': {
            orderId: 'ORD-001',
            orderedBy: 'John Smith',
            dateOrdered: '2023-10-15',
            items: [
                { id: 'OI-001', name: 'Paracetamol 500mg (P-1001)', orderedQty: 100, receivedQty: 0 },
                { id: 'OI-002', name: 'Amoxicillin 250mg (P-1002)', orderedQty: 50, receivedQty: 0 }
            ]
        },
        'ORD-002': {
            orderId: 'ORD-002',
            orderedBy: 'Maria Garcia',
            dateOrdered: '2023-10-18',
            items: [
                { id: 'OI-003', name: 'MediCare Face Mask', orderedQty: 200, receivedQty: 200 },
                { id: 'OI-004', name: 'Green Cross Alcohol', orderedQty: 150, receivedQty: 150 }
            ]
        },
        'ORD-003': {
            orderId: 'ORD-003',
            orderedBy: 'Robert Johnson',
            dateOrdered: '2023-10-20',
            items: [
                { id: 'OI-005', name: 'Betadine Solution', orderedQty: 80, receivedQty: 40 },
                { id: 'OI-006', name: 'Band-Aid Adhesive', orderedQty: 120, receivedQty: 120 },
                { id: 'OI-007', name: 'Vicks Inhaler', orderedQty: 60, receivedQty: 0 }
            ]
        },
        'ORD-004': {
            orderId: 'ORD-004',
            orderedBy: 'Sarah Williams',
            dateOrdered: '2023-10-22',
            items: [
                { id: 'OI-008', name: 'Babyflo Cotton Buds', orderedQty: 100, receivedQty: 0 }
            ]
        }
    };
    
    const order = orderData[orderId];
    if (!order) return;
    
    const receiveOrderContent = document.getElementById('receiveOrderContent');
    
    // Calculate total ordered quantity
    const totalOrdered = order.items.reduce((sum, item) => sum + item.orderedQty, 0);
    
    // Build the receipt-style form
    let formHTML = `
        <div class="receipt-header">
            <div class="receipt-title">ORDER RECEIVING DOCUMENT</div>
            <div class="receipt-subtitle">Pharmacy Inventory System</div>
        </div>
        
        <div class="receipt-divider"></div>
        
        <div class="receipt-info">
            <div class="receipt-info-row">
                <span class="receipt-info-label">Order ID:</span>
                <span>${order.orderId}</span>
            </div>
            <div class="receipt-info-row">
                <span class="receipt-info-label">Ordered By:</span>
                <span>${order.orderedBy}</span>
            </div>
            <div class="receipt-info-row">
                <span class="receipt-info-label">Date Ordered:</span>
                <span>${order.dateOrdered}</span>
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
            <tbody>
    `;
    
    // Add rows for each order item
    order.items.forEach((item, index) => {
        formHTML += `
            <tr>
                <td>${item.id}</td>
                <td>${item.name}</td>
                <td>${item.orderedQty}</td>
                <td>
                    <input type="number" id="receivedQty${index}" 
                            value="${item.receivedQty}" min="0" max="${item.orderedQty}">
                </td>
            </tr>
        `;
    });
    
    // Continue with the rest of the receipt
    formHTML += `
            </tbody>
        </table>
        
        <div class="receipt-divider"></div>
        
        <div class="receipt-summary">
            <div class="receipt-info-row">
                <span class="receipt-info-label">Total Items Ordered:</span>
                <span>${order.items.length}</span>
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
                <span><input type="text" id="receivedBy" placeholder="Enter name" style="border: none; border-bottom: 1px solid var(--border); width: 150px; text-align: right; font-family: 'Poppins', sans-serif;"></span>
            </div>
            <div class="receipt-info-row">
                <span class="receipt-info-label">Date Received:</span>
                <span><input type="date" id="dateReceived" value="${new Date().toISOString().split('T')[0]}" style="border: none; border-bottom: 1px solid var(--border); width: 150px; text-align: right; font-family: 'Poppins', sans-serif;"></span>
            </div>
        </div>
        
        <div class="receipt-footer">
            <div>Thank you for your business!</div>
            <div>Generated on ${new Date().toLocaleDateString()}</div>
        </div>
    `;
    
    receiveOrderContent.innerHTML = formHTML;
    
    document.getElementById('receiveOrderModal').style.display = 'flex';
}