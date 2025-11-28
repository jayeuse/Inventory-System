// Export Transactions to PDF
async function exportTransactionsToPDF() {
  // Check if jsPDF is loaded
  if (!window.jspdf) {
    console.error('jsPDF library is not loaded');
    alert('PDF library not loaded. Please refresh the page and try again.');
    return;
  }

  const { jsPDF } = window.jspdf;
  
  // Short bond paper size in mm (letter size: 8.5" x 11") - Portrait orientation
  const doc = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'letter'
  });

  // Get current filter values
  const searchInput = document.getElementById('transactions_searchInput');
  const typeFilter = document.getElementById('transactions_typeFilter');
  const searchTerm = searchInput ? searchInput.value : '';
  const typeValue = typeFilter ? typeFilter.options[typeFilter.selectedIndex].text : 'All';

  // Use the global filteredTransactions array
  let transactionsToExport = [];
  if (typeof filteredTransactions !== 'undefined' && filteredTransactions) {
    transactionsToExport = filteredTransactions;
  } else if (typeof allTransactions !== 'undefined' && allTransactions) {
    transactionsToExport = allTransactions;
  } else {
    alert('No transaction data available. Please refresh the page and try again.');
    return;
  }

  // Helper function to format transaction type
  function getTypeBadgeText(type) {
    const lowerType = (type || '').toLowerCase();
    if (lowerType === 'in' || lowerType === 'stock in') return 'Stock In';
    if (lowerType === 'out' || lowerType === 'stock out') return 'Stock Out';
    if (lowerType === 'adj' || lowerType === 'adjust' || lowerType === 'adjustment' || lowerType === 'stock adjustment') return 'Adjust';
    return type;
  }

  // Helper function to format date
  function formatDate(dateStr) {
    if (!dateStr || dateStr === '-') return '-';
    const d = new Date(dateStr);
    if (!isNaN(d)) {
      const options = { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      };
      return d.toLocaleDateString('en-US', options);
    }
    return String(dateStr);
  }

  // Convert transactions to table rows
  const tableRows = transactionsToExport.map(transaction => [
    transaction.transaction_id || '-',
    getTypeBadgeText(transaction.transaction_type),
    transaction.product_name || '-',
    transaction.batch_id || '-',
    transaction.quantity_change || '-',
    transaction.on_hand || '-',
    transaction.remarks || '-',
    transaction.performed_by || '-',
    formatDate(transaction.date_of_transaction)
  ]);

  // Add title
  doc.setFontSize(18);
  doc.setFont('helvetica', 'bold');
  doc.text('Transaction History Report', 105, 15, { align: 'center' });

  // Add generation date
  doc.setFontSize(10);
  doc.setFont('helvetica', 'normal');
  const today = new Date().toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });
  doc.text(`Generated: ${today}`, 105, 22, { align: 'center' });

  // Add filter information
  let yPosition = 30;
  doc.setFontSize(9);
  if (searchTerm) {
    doc.text(`Search Filter: "${searchTerm}"`, 14, yPosition);
    yPosition += 5;
  }
  if (typeValue !== 'Filter by Type') {
    doc.text(`Type Filter: ${typeValue}`, 14, yPosition);
    yPosition += 5;
  }

  // Add table
  doc.autoTable({
    startY: yPosition + 5,
    head: [['Txn ID', 'Type', 'Product Name', 'Batch ID', 'Qty Chg', 'On Hand', 'Remarks', 'By', 'Date']],
    body: tableRows,
    theme: 'striped',
    headStyles: {
      fillColor: [139, 95, 191],
      textColor: 255,
      fontStyle: 'bold',
      fontSize: 7
    },
    bodyStyles: {
      fontSize: 6
    },
    alternateRowStyles: {
      fillColor: [245, 242, 249]
    },
    columnStyles: {
      0: { cellWidth: 20 },
      1: { cellWidth: 15 },
      2: { cellWidth: 35 },
      3: { cellWidth: 18 },
      4: { cellWidth: 12 },
      5: { cellWidth: 12 },
      6: { cellWidth: 25 },
      7: { cellWidth: 18 },
      8: { cellWidth: 28 }
    },
    margin: { left: 14, right: 14 }
  });

  // Add footer with page numbers
  const pageCount = doc.internal.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    doc.setFontSize(8);
    doc.text(
      `Page ${i} of ${pageCount}`,
      105,
      doc.internal.pageSize.height - 10,
      { align: 'center' }
    );
  }

  // Save the PDF
  const filename = `Transaction_History_Report_${new Date().toISOString().split('T')[0]}.pdf`;
  doc.save(filename);
}

// Add event listener for export button
document.addEventListener('DOMContentLoaded', function() {
  const exportBtn = document.getElementById('exportTransactionsBtn');
  if (exportBtn) {
    exportBtn.addEventListener('click', exportTransactionsToPDF);
  }
});
