let allTransactions = [];
let filteredTransactions = [];
let currentPage = 1;
const pageSize = 8;

document.addEventListener('DOMContentLoaded', async function(){
  await loadTransactions();
  setupEventListeners();
});

async function loadTransactions(){
  try{
    const response = await fetch('/api/transactions/');
    
    if (!response.ok){
      const errorData = await response.json();
      alert('Error: ' + JSON.stringify(errorData));
      return;
    }

    const data = await response.json();
    allTransactions = data;
    filteredTransactions = [...allTransactions];
    currentPage = 1;
    renderTransactions();
    
  } catch (error){
    console.error('Error fetching Transactions:', error);
  }
}

function setupEventListeners() {
  // Search input
  const searchInput = document.getElementById('transactions_searchInput');
  if (searchInput) {
    searchInput.addEventListener('input', handleSearchAndFilter);
  }

  // Type filter
  const typeFilter = document.getElementById('transactions_typeFilter');
  if (typeFilter) {
    typeFilter.addEventListener('change', handleSearchAndFilter);
  }

  // Pagination buttons
  const prevBtn = document.getElementById('transactions_prevBtn');
  const nextBtn = document.getElementById('transactions_nextBtn');
  
  if (prevBtn) {
    prevBtn.addEventListener('click', () => {
      if (currentPage > 1) {
        currentPage--;
        renderTransactions();
      }
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', () => {
      const totalPages = Math.ceil(filteredTransactions.length / pageSize);
      if (currentPage < totalPages) {
        currentPage++;
        renderTransactions();
      }
    });
  }
}

function handleSearchAndFilter() {
  const searchInput = document.getElementById('transactions_searchInput');
  const typeFilter = document.getElementById('transactions_typeFilter');
  
  const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
  const typeValue = typeFilter ? typeFilter.value : 'all';

  filteredTransactions = allTransactions.filter(transaction => {
    // Search filter
    const matchesSearch = 
      !searchTerm ||
      (transaction.transaction_id && transaction.transaction_id.toLowerCase().includes(searchTerm)) ||
      (transaction.product_id && transaction.product_id.toLowerCase().includes(searchTerm)) ||
      (transaction.product_name && transaction.product_name.toLowerCase().includes(searchTerm)) ||
      (transaction.batch_id && transaction.batch_id.toLowerCase().includes(searchTerm));

    // Type filter
    const matchesType = 
      typeValue === 'all' ||
      (transaction.transaction_type && transaction.transaction_type.toLowerCase() === typeValue);

    return matchesSearch && matchesType;
  });

  currentPage = 1;
  renderTransactions();
}

function renderTransactions() {
  const tbody = document.getElementById('transactions_tableBody');
  if (!tbody) return;

  tbody.innerHTML = '';

  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const paginatedTransactions = filteredTransactions.slice(startIndex, endIndex);

  // Render actual transactions
  paginatedTransactions.forEach(transaction => {
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

  // Fill remaining rows with placeholders
  const remainingRows = pageSize - paginatedTransactions.length;
  for (let i = 0; i < remainingRows; i++) {
    const row = document.createElement('tr');
    row.innerHTML = `
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
    row.style.opacity = '0.4';
    tbody.appendChild(row);
  }

  updatePaginationButtons();
}

function updatePaginationButtons() {
  const prevBtn = document.getElementById('transactions_prevBtn');
  const nextBtn = document.getElementById('transactions_nextBtn');
  const totalPages = Math.ceil(filteredTransactions.length / pageSize);

  if (prevBtn) {
    prevBtn.disabled = currentPage === 1;
    prevBtn.style.opacity = currentPage === 1 ? '0.5' : '1';
  }

  if (nextBtn) {
    nextBtn.disabled = currentPage >= totalPages || filteredTransactions.length === 0;
    nextBtn.style.opacity = (currentPage >= totalPages || filteredTransactions.length === 0) ? '0.5' : '1';
  }
}

function truncateText(text, maxLength = 15) {
  if (!text) return '-';
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
}

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