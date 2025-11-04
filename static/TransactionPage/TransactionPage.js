document.addEventListener("DOMContentLoaded", function () {
  console.log("Transaction page loaded");

  // Sample hardcoded data
  const sampleTransactions = [
    {
      transaction_id: 'TXN-2025-00001',
      type: 'adjust',
      product_id: 'PRD001',
      product_name: 'Biogesic (Paracetamol)',
      batch_id: 'BTH-001',
      quantity_change: '+50',
      on_hand: 150,
      remarks: 'Restocked from supplier',
      performed_by: 'Admin User',
      date: '2025-11-04 10:30 AM'
    }
  ];

  const tableBody = document.getElementById('transactions_tableBody');
  const pageSize = 8;

  function renderTransactions(transactions = []) {
    if (!tableBody) return;
    tableBody.innerHTML = '';

    for (let i = 0; i < pageSize; i++) {
      const tr = document.createElement('tr');
      
      if (i < transactions.length) {
        // Actual transaction data
        const t = transactions[i];
        const typeBadgeClass = getTypeBadgeClass(t.type);
        const typeBadgeText = getTypeBadgeText(t.type);
        
        tr.innerHTML = `
          <td>${t.transaction_id}</td>
          <td><span class="${typeBadgeClass}">${typeBadgeText}</span></td>
          <td>${t.product_name}</td>
          <td>${t.batch_id}</td>
          <td>${t.quantity_change}</td>
          <td>${t.on_hand}</td>
          <td>${t.remarks}</td>
          <td>${t.performed_by}</td>
          <td>${t.date}</td>
        `;
      } else {
        // Empty placeholder row
        tr.innerHTML = `
          <td>-</td>
          <td>-</td>
          <td>-</td>
          <td>-</td>
          <td>-</td>
          <td>-</td>
          <td>-</td>
          <td>-</td>
          <td>-</td>
        `;
        tr.style.opacity = '0.4';
      }
      
      tableBody.appendChild(tr);
    }
  }

  // Render sample data on page load
  renderTransactions(sampleTransactions);
});

function getTypeBadgeClass(type) {
  const lowerType = (type || '').toLowerCase();
  if (lowerType === 'in' || lowerType === 'stock in') return 'type-badge type-badge-in';
  if (lowerType === 'out' || lowerType === 'stock out') return 'type-badge type-badge-out';
  if (lowerType === 'adjust' || lowerType === 'adjustment') return 'type-badge type-badge-adjust';
  return 'type-badge';
}

function getTypeBadgeText(type) {
  const lowerType = (type || '').toLowerCase();
  if (lowerType === 'in' || lowerType === 'stock in') return 'Stock In';
  if (lowerType === 'out' || lowerType === 'stock out') return 'Stock Out';
  if (lowerType === 'adjust' || lowerType === 'adjustment') return 'Adjust';
  return type;
}