// Export Stock List to PDF
async function exportStockListToPDF() {
  const { jsPDF } = window.jspdf;
  
  // Short bond paper size in mm (letter size: 8.5" x 11")
  const doc = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'letter'
  });

  // Get current filter values
  const searchInput = document.getElementById('stockslist_searchInput');
  const statusFilter = document.getElementById('stockslist_statusFilter');
  const searchTerm = searchInput ? searchInput.value : '';
  const statusValue = statusFilter ? statusFilter.options[statusFilter.selectedIndex].text : 'All';
  const currentStatusFilter = statusFilter ? statusFilter.value : 'all';

  // Fetch ALL stocks data from API
  let allStocks = [];
  try {
    const response = await fetch('/api/product-stocks/');
    allStocks = await response.json();
  } catch (error) {
    console.error('Error fetching stocks:', error);
    alert('Failed to fetch stock data. Please try again.');
    return;
  }

  // Apply the same filters as the table
  const filteredStocks = allStocks.filter(stock => {
    // Search filter
    const matchesSearch = !searchTerm || 
      stock.stock_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      stock.product_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      stock.product_name.toLowerCase().includes(searchTerm.toLowerCase());
    
    // Status filter - normalize both values to compare
    const normalizedStockStatus = stock.status.toLowerCase().replace(/\s+/g, '-');
    const normalizedFilterStatus = currentStatusFilter.toLowerCase();
    const matchesStatus = currentStatusFilter === 'all' || 
      normalizedStockStatus === normalizedFilterStatus;
    
    return matchesSearch && matchesStatus;
  });

  // Convert filtered stocks to table rows
  const tableRows = filteredStocks.map(stock => [
    stock.stock_id,
    stock.product_id,
    stock.product_name,
    stock.total_on_hand,
    stock.status
  ]);

  // Add title
  doc.setFontSize(18);
  doc.setFont('helvetica', 'bold');
  doc.text('Stock List Report', 105, 15, { align: 'center' });

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
  if (statusValue !== 'Filter by Status') {
    doc.text(`Status Filter: ${statusValue}`, 14, yPosition);
    yPosition += 5;
  }

  // Add table
  doc.autoTable({
    startY: yPosition + 5,
    head: [['Stock ID', 'Product ID', 'Product Name', 'Total On Hand', 'Status']],
    body: tableRows,
    theme: 'striped',
    headStyles: {
      fillColor: [139, 95, 191],
      textColor: 255,
      fontStyle: 'bold',
      fontSize: 10
    },
    bodyStyles: {
      fontSize: 9
    },
    alternateRowStyles: {
      fillColor: [245, 242, 249]
    },
    columnStyles: {
      0: { cellWidth: 30 },
      1: { cellWidth: 30 },
      2: { cellWidth: 70 },
      3: { cellWidth: 30 },
      4: { cellWidth: 30 }
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
  const filename = `Stock_List_Report_${new Date().toISOString().split('T')[0]}.pdf`;
  doc.save(filename);
}

// Add event listener for export button
document.addEventListener('DOMContentLoaded', function() {
  const exportBtn = document.getElementById('exportStockListBtn');
  if (exportBtn) {
    exportBtn.addEventListener('click', exportStockListToPDF);
  }
});
