document.addEventListener('DOMContentLoaded', async function(){
  loadTransactions();
});

async function loadTransactions(){
  try{
    const response = await fetch('/api/transactions/');
    const data = await response.json();

    const tbody = document.getElementById('transactions_tableBody');
    tbody.innerHTML = '';

    data.forEach(transaction => {
      const row = document.createElement('tr');
      const typeBadgeClass = getTypeBadgeClass(transaction.transaction_type);
      const typeBadgeText = getTypeBadgeText(transaction.transaction_type);

      row.innerHTML = `
        <td>${transaction.transaction_id || '-'}</td>
        <td><span class="${typeBadgeClass}">${typeBadgeText}</span></td>
        <td>${transaction.product_name || '-'}</td>
        <td>${transaction.batch_id || '-'}</td>
        <td>${transaction.quantity_change || '-'}</td>
        <td>${transaction.on_hand || '-'}</td>
        <td title="${transaction.remarks || '-'}">${truncateText(transaction.remarks)}</td>
        <td>${transaction.performed_by || '-'}</td>
        <td>${transaction.date_of_transaction || '-'}</td>
      `;

      tbody.appendChild(row);
    });

    if (!response.ok){
      const errorData = await response.json();
      alert('Error: ' + JSON.stringify(errorData))
    }
    } catch (error){
        console.error('Error fetching Transactions:', error);
    }
}

function truncateText(text, maxLength = 15) {
  if (!text) return '-';
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
}