/**
 * Data Export Utility Module
 * Handles exporting data to CSV format for the Inventory System
 */

// Export status tracking
let isExporting = false;

/**
 * Convert array of objects to CSV string
 * @param {Array} data - Array of objects to convert
 * @param {Array} columns - Column definitions [{key: 'fieldName', header: 'Display Name'}]
 * @returns {string} CSV formatted string
 */
function arrayToCSV(data, columns) {
    if (!data || data.length === 0) {
        return columns.map(c => c.header).join(',') + '\n';
    }
    
    // Create header row
    const headers = columns.map(c => `"${c.header}"`).join(',');
    
    // Create data rows
    const rows = data.map(item => {
        return columns.map(col => {
            let value = item[col.key];
            
            // Handle null/undefined
            if (value === null || value === undefined) {
                value = '';
            }
            
            // Handle nested properties (e.g., 'category.name')
            if (col.key.includes('.')) {
                const keys = col.key.split('.');
                value = keys.reduce((obj, key) => obj?.[key], item) || '';
            }
            
            // Format specific types
            if (col.formatter) {
                value = col.formatter(value, item);
            }
            
            // Escape quotes and wrap in quotes
            value = String(value).replace(/"/g, '""');
            return `"${value}"`;
        }).join(',');
    });
    
    return headers + '\n' + rows.join('\n');
}

/**
 * Download CSV file
 * @param {string} csvContent - CSV string content
 * @param {string} filename - Name of the file to download
 */
function downloadCSV(csvContent, filename) {
    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
}

/**
 * Get current date string for filename
 * @returns {string} Date string in YYYY-MM-DD format
 */
function getDateString() {
    const now = new Date();
    return now.toISOString().split('T')[0];
}

/**
 * Show export status message
 * @param {string} message - Message to display
 * @param {string} type - 'success', 'error', or 'loading'
 */
function showExportStatus(message, type = 'loading') {
    // Remove existing status
    const existing = document.getElementById('exportStatus');
    if (existing) existing.remove();
    
    const status = document.createElement('div');
    status.id = 'exportStatus';
    status.className = `export-status export-status-${type}`;
    
    let icon = '';
    if (type === 'loading') icon = '<i class="bi bi-arrow-repeat spinning"></i>';
    else if (type === 'success') icon = '<i class="bi bi-check-circle"></i>';
    else if (type === 'error') icon = '<i class="bi bi-exclamation-circle"></i>';
    
    status.innerHTML = `${icon} <span>${message}</span>`;
    document.body.appendChild(status);
    
    // Auto-hide success/error messages after 3 seconds
    if (type !== 'loading') {
        setTimeout(() => {
            status.classList.add('fade-out');
            setTimeout(() => status.remove(), 300);
        }, 3000);
    }
}

/**
 * Hide export status
 */
function hideExportStatus() {
    const existing = document.getElementById('exportStatus');
    if (existing) existing.remove();
}

// ========== EXPORT FUNCTIONS ==========

/**
 * Export Products to CSV
 */
async function exportProducts() {
    if (isExporting) return;
    isExporting = true;
    
    showExportStatus('Exporting products...', 'loading');
    
    try {
        const response = await fetch('/api/products/');
        if (!response.ok) throw new Error('Failed to fetch products');
        
        const data = await response.json();
        const products = Array.isArray(data) ? data : (data.results || []);
        
        const columns = [
            { key: 'product_id', header: 'Product ID' },
            { key: 'brand_name', header: 'Brand Name' },
            { key: 'generic_name', header: 'Generic Name' },
            { key: 'category_name', header: 'Category' },
            { key: 'subcategory_name', header: 'Subcategory' },
            { key: 'price_per_unit', header: 'Price (PHP)', formatter: (v) => v ? Number(v).toFixed(2) : '0.00' },
            { key: 'unit_of_measurement', header: 'Unit' },
            { key: 'low_stock_threshold', header: 'Low Stock Threshold' },
            { key: 'expiry_threshold_days', header: 'Expiry Threshold (Days)' },
            { key: 'status', header: 'Status' },
            { key: 'last_updated', header: 'Last Updated' }
        ];
        
        const csv = arrayToCSV(products, columns);
        downloadCSV(csv, `products_${getDateString()}.csv`);
        
        showExportStatus(`Successfully exported ${products.length} products!`, 'success');
    } catch (error) {
        console.error('Export error:', error);
        showExportStatus('Failed to export products. Please try again.', 'error');
    } finally {
        isExporting = false;
    }
}

/**
 * Export Suppliers to CSV
 */
async function exportSuppliers() {
    if (isExporting) return;
    isExporting = true;
    
    showExportStatus('Exporting suppliers...', 'loading');
    
    try {
        const response = await fetch('/api/suppliers/');
        if (!response.ok) throw new Error('Failed to fetch suppliers');
        
        const data = await response.json();
        const suppliers = Array.isArray(data) ? data : (data.results || []);
        
        const columns = [
            { key: 'supplier_id', header: 'Supplier ID' },
            { key: 'supplier_name', header: 'Supplier Name' },
            { key: 'contact_number', header: 'Contact Number' },
            { key: 'email', header: 'Email' },
            { key: 'address', header: 'Address' },
            { key: 'status', header: 'Status' },
            { key: 'product_count', header: 'Products Supplied' }
        ];
        
        const csv = arrayToCSV(suppliers, columns);
        downloadCSV(csv, `suppliers_${getDateString()}.csv`);
        
        showExportStatus(`Successfully exported ${suppliers.length} suppliers!`, 'success');
    } catch (error) {
        console.error('Export error:', error);
        showExportStatus('Failed to export suppliers. Please try again.', 'error');
    } finally {
        isExporting = false;
    }
}

/**
 * Export Categories to CSV
 */
async function exportCategories() {
    if (isExporting) return;
    isExporting = true;
    
    showExportStatus('Exporting categories...', 'loading');
    
    try {
        const response = await fetch('/api/categories/');
        if (!response.ok) throw new Error('Failed to fetch categories');
        
        const data = await response.json();
        const categories = Array.isArray(data) ? data : (data.results || []);
        
        const columns = [
            { key: 'category_id', header: 'Category ID' },
            { key: 'category_name', header: 'Category Name' },
            { key: 'description', header: 'Description' },
            { key: 'product_count', header: 'Product Count' },
            { key: 'status', header: 'Status' }
        ];
        
        const csv = arrayToCSV(categories, columns);
        downloadCSV(csv, `categories_${getDateString()}.csv`);
        
        showExportStatus(`Successfully exported ${categories.length} categories!`, 'success');
    } catch (error) {
        console.error('Export error:', error);
        showExportStatus('Failed to export categories. Please try again.', 'error');
    } finally {
        isExporting = false;
    }
}

/**
 * Export Inventory/Stock to CSV
 */
async function exportInventory() {
    if (isExporting) return;
    isExporting = true;
    
    showExportStatus('Exporting inventory...', 'loading');
    
    try {
        const response = await fetch('/api/inventory/stocks/');
        if (!response.ok) throw new Error('Failed to fetch inventory');
        
        const data = await response.json();
        const stocks = Array.isArray(data) ? data : (data.results || []);
        
        const columns = [
            { key: 'stock_id', header: 'Stock ID' },
            { key: 'product_id', header: 'Product ID' },
            { key: 'product_name', header: 'Product Name' },
            { key: 'brand_name', header: 'Brand Name' },
            { key: 'batch_number', header: 'Batch Number' },
            { key: 'quantity', header: 'Quantity' },
            { key: 'unit_of_measurement', header: 'Unit' },
            { key: 'expiry_date', header: 'Expiry Date' },
            { key: 'status', header: 'Status' },
            { key: 'date_received', header: 'Date Received' }
        ];
        
        const csv = arrayToCSV(stocks, columns);
        downloadCSV(csv, `inventory_${getDateString()}.csv`);
        
        showExportStatus(`Successfully exported ${stocks.length} stock records!`, 'success');
    } catch (error) {
        console.error('Export error:', error);
        showExportStatus('Failed to export inventory. Please try again.', 'error');
    } finally {
        isExporting = false;
    }
}

/**
 * Export Orders to CSV
 */
async function exportOrders() {
    if (isExporting) return;
    isExporting = true;
    
    showExportStatus('Exporting orders...', 'loading');
    
    try {
        const response = await fetch('/api/orders/');
        if (!response.ok) throw new Error('Failed to fetch orders');
        
        const data = await response.json();
        const orders = Array.isArray(data) ? data : (data.results || []);
        
        const columns = [
            { key: 'order_id', header: 'Order ID' },
            { key: 'order_date', header: 'Order Date' },
            { key: 'ordered_by', header: 'Ordered By' },
            { key: 'total_items', header: 'Total Items' },
            { key: 'status', header: 'Status' },
            { key: 'remarks', header: 'Remarks' }
        ];
        
        const csv = arrayToCSV(orders, columns);
        downloadCSV(csv, `orders_${getDateString()}.csv`);
        
        showExportStatus(`Successfully exported ${orders.length} orders!`, 'success');
    } catch (error) {
        console.error('Export error:', error);
        showExportStatus('Failed to export orders. Please try again.', 'error');
    } finally {
        isExporting = false;
    }
}

/**
 * Export Transactions to CSV
 */
async function exportTransactions() {
    if (isExporting) return;
    isExporting = true;
    
    showExportStatus('Exporting transactions...', 'loading');
    
    try {
        const response = await fetch('/api/transactions/');
        if (!response.ok) throw new Error('Failed to fetch transactions');
        
        const data = await response.json();
        const transactions = Array.isArray(data) ? data : (data.results || []);
        
        const columns = [
            { key: 'transaction_id', header: 'Transaction ID' },
            { key: 'transaction_type', header: 'Type' },
            { key: 'product_name', header: 'Product' },
            { key: 'quantity', header: 'Quantity' },
            { key: 'performed_by', header: 'Performed By' },
            { key: 'transaction_date', header: 'Date' },
            { key: 'remarks', header: 'Remarks' }
        ];
        
        const csv = arrayToCSV(transactions, columns);
        downloadCSV(csv, `transactions_${getDateString()}.csv`);
        
        showExportStatus(`Successfully exported ${transactions.length} transactions!`, 'success');
    } catch (error) {
        console.error('Export error:', error);
        showExportStatus('Failed to export transactions. Please try again.', 'error');
    } finally {
        isExporting = false;
    }
}

/**
 * Export All Data (Full Backup)
 */
async function exportAllData() {
    if (isExporting) return;
    isExporting = true;
    
    showExportStatus('Creating full data export...', 'loading');
    
    try {
        // Fetch all data in parallel
        const [productsRes, suppliersRes, categoriesRes, stocksRes, ordersRes] = await Promise.all([
            fetch('/api/products/').then(r => r.json()).catch(() => []),
            fetch('/api/suppliers/').then(r => r.json()).catch(() => []),
            fetch('/api/categories/').then(r => r.json()).catch(() => []),
            fetch('/api/inventory/stocks/').then(r => r.json()).catch(() => []),
            fetch('/api/orders/').then(r => r.json()).catch(() => [])
        ]);
        
        const backup = {
            exportDate: new Date().toISOString(),
            exportedBy: 'System Export',
            data: {
                products: Array.isArray(productsRes) ? productsRes : (productsRes.results || []),
                suppliers: Array.isArray(suppliersRes) ? suppliersRes : (suppliersRes.results || []),
                categories: Array.isArray(categoriesRes) ? categoriesRes : (categoriesRes.results || []),
                inventory: Array.isArray(stocksRes) ? stocksRes : (stocksRes.results || []),
                orders: Array.isArray(ordersRes) ? ordersRes : (ordersRes.results || [])
            },
            summary: {
                totalProducts: (Array.isArray(productsRes) ? productsRes : (productsRes.results || [])).length,
                totalSuppliers: (Array.isArray(suppliersRes) ? suppliersRes : (suppliersRes.results || [])).length,
                totalCategories: (Array.isArray(categoriesRes) ? categoriesRes : (categoriesRes.results || [])).length,
                totalStockRecords: (Array.isArray(stocksRes) ? stocksRes : (stocksRes.results || [])).length,
                totalOrders: (Array.isArray(ordersRes) ? ordersRes : (ordersRes.results || [])).length
            }
        };
        
        // Download as JSON
        const jsonContent = JSON.stringify(backup, null, 2);
        const blob = new Blob([jsonContent], { type: 'application/json' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        
        link.setAttribute('href', url);
        link.setAttribute('download', `inventory_backup_${getDateString()}.json`);
        link.style.visibility = 'hidden';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        URL.revokeObjectURL(url);
        
        const totalRecords = Object.values(backup.summary).reduce((a, b) => a + b, 0);
        showExportStatus(`Full backup created! ${totalRecords} total records exported.`, 'success');
    } catch (error) {
        console.error('Export error:', error);
        showExportStatus('Failed to create backup. Please try again.', 'error');
    } finally {
        isExporting = false;
    }
}

// Export functions to global scope
window.exportProducts = exportProducts;
window.exportSuppliers = exportSuppliers;
window.exportCategories = exportCategories;
window.exportInventory = exportInventory;
window.exportOrders = exportOrders;
window.exportTransactions = exportTransactions;
window.exportAllData = exportAllData;
