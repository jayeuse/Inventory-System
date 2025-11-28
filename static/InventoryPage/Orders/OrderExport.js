// Export Orders to PDF - Make it globally accessible
window.exportOrdersToPDF = function() {
  // Check if jsPDF is loaded
  if (!window.jspdf) {
    console.error('jsPDF library is not loaded');
    alert('PDF library not loaded. Please refresh the page and try again.');
    return;
  }
  
  const { jsPDF } = window.jspdf;
  
  // Short bond paper size in mm (letter size: 8.5" x 11")
  const doc = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'letter'
  });

  // Get current filter values
  const searchInput = document.getElementById('orderSearchInput');
  const statusFilter = document.getElementById('orderStatusFilter');
  const searchTerm = searchInput ? searchInput.value.trim().toLowerCase() : '';
  const statusValue = statusFilter ? statusFilter.options[statusFilter.selectedIndex].text : 'All';
  const currentStatusFilter = statusFilter ? statusFilter.value : 'all';

  // Use the global ordersCache or filteredOrders if available
  let ordersToExport = [];
  if (typeof window.filteredOrders !== 'undefined' && window.filteredOrders) {
    ordersToExport = window.filteredOrders;
  } else if (typeof window.ordersCache !== 'undefined' && window.ordersCache) {
    // Apply filters manually if filteredOrders is not available
    ordersToExport = window.ordersCache.filter(o => {
      const matchesSearch = !searchTerm || 
        (o.order_id && o.order_id.toLowerCase().includes(searchTerm)) || 
        (o.ordered_by && o.ordered_by.toLowerCase().includes(searchTerm));
      const s = (o.status || '').toString().toLowerCase();
      const matchesStatus = currentStatusFilter === 'all' || 
        (currentStatusFilter === 'partial' ? s.includes('partial') : s === currentStatusFilter);
      return matchesSearch && matchesStatus;
    });
  } else {
    alert('No orders data available. Please refresh the page and try again.');
    return;
  }

  // Helper function to format dates
  function formatDateOnly(dateStr) {
    if (!dateStr || dateStr === '-') return '-';
    const d = new Date(dateStr);
    if (!isNaN(d)) {
      const options = { year: 'numeric', month: 'long', day: 'numeric' };
      return d.toLocaleDateString('en-US', options);
    }
    return String(dateStr);
  }

  // Add title
  doc.setFontSize(18);
  doc.setFont('helvetica', 'bold');
  doc.text('Orders Report', 105, 15, { align: 'center' });

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

  // Process each order with its items
  yPosition += 10;

  ordersToExport.forEach((order, index) => {
    // Check if we need a new page
    if (yPosition > 240) {
      doc.addPage();
      yPosition = 20;
    }

    // Store start position for the box
    const boxStartY = yPosition;

    // Order header section
    doc.setFillColor(139, 95, 191);
    doc.rect(14, yPosition, 188, 8, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.text(`Order: ${order.order_id || '-'}`, 16, yPosition + 5.5);
    yPosition += 8;

    // Order details table
    doc.autoTable({
      startY: yPosition,
      head: [['Ordered By', 'Date Ordered', 'Status', 'Date Received']],
      body: [[
        order.ordered_by || '-',
        formatDateOnly(order.date_ordered),
        order.status || '-',
        formatDateOnly(order.date_received)
      ]],
      theme: 'plain',
      headStyles: {
        fillColor: [232, 226, 240],
        textColor: [30, 30, 30],
        fontStyle: 'bold',
        fontSize: 9
      },
      bodyStyles: {
        fontSize: 8,
        textColor: [50, 50, 50]
      },
      margin: { left: 14, right: 14 },
      tableWidth: 188
    });

    yPosition = doc.lastAutoTable.finalY + 2;

    // Order items table (indented)
    if (order.items && order.items.length > 0) {
      const itemRows = order.items.map(item => [
        item.order_item_id || '-',
        item.product_id || '-',
        item.product_name || (item.brand_name ? item.brand_name + ' ' + (item.generic_name || '') : '-'),
        item.quantity_ordered || '-',
        item.quantity_received || '0'
      ]);

      doc.autoTable({
        startY: yPosition,
        head: [['Order Item ID', 'Product ID', 'Product Name', 'Qty Ordered', 'Qty Received']],
        body: itemRows,
        theme: 'striped',
        headStyles: {
          fillColor: [184, 169, 209],
          textColor: 255,
          fontStyle: 'bold',
          fontSize: 8
        },
        bodyStyles: {
          fontSize: 7
        },
        alternateRowStyles: {
          fillColor: [245, 242, 249]
        },
        columnStyles: {
          0: { cellWidth: 32 },
          1: { cellWidth: 26 },
          2: { cellWidth: 70 },
          3: { cellWidth: 23 },
          4: { cellWidth: 23 }
        },
        margin: { left: 24, right: 14 }
      });

      yPosition = doc.lastAutoTable.finalY + 5;
    } else {
      doc.setTextColor(100, 100, 100);
      doc.setFontSize(8);
      doc.setFont('helvetica', 'italic');
      doc.text('No order items', 24, yPosition + 5);
      yPosition += 10;
    }

    // Draw border box around the entire order section
    const boxHeight = yPosition - boxStartY;
    doc.setDrawColor(139, 95, 191);
    doc.setLineWidth(0.5);
    doc.rect(14, boxStartY, 188, boxHeight);

    // Add spacing before next order
    yPosition += 5;

    // Reset text color for next order
    doc.setTextColor(0, 0, 0);
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
  const filename = `Orders_Report_${new Date().toISOString().split('T')[0]}.pdf`;
  doc.save(filename);
}

// Function to attach event listener - call this after Orders content is loaded
window.attachOrdersExportListener = function() {
  const exportBtn = document.getElementById('exportOrdersBtn');
  if (exportBtn) {
    // Remove any existing listeners to avoid duplicates
    exportBtn.replaceWith(exportBtn.cloneNode(true));
    const newBtn = document.getElementById('exportOrdersBtn');
    if (newBtn) {
      newBtn.addEventListener('click', window.exportOrdersToPDF);
      console.log('Orders export button listener attached');
    }
  } else {
    console.warn('Export orders button not found');
  }
}

// Try to attach on DOMContentLoaded (for direct page load)
document.addEventListener('DOMContentLoaded', function() {
  // Wait a bit for dynamic content to load
  setTimeout(function() {
    window.attachOrdersExportListener();
  }, 500);
});
