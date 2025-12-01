// ChartsManagement.js
// Responsible for fetching dashboard aggregate data and updating Chart.js instances.
// Uses the project's CSRF helpers for consistent fetch headers.

document.addEventListener('DOMContentLoaded', function() {
	// Wait until chart update functions / instances are available
	waitForChartsReady(5000).then(() => {
		fetchAndUpdateAllCharts();
	}).catch(() => {
		console.warn('Charts did not initialize in time; skipping initial fetch.');
	});
});

function waitForChartsReady(timeoutMs = 5000) {
	const start = Date.now();
	return new Promise((resolve, reject) => {
		const iv = setInterval(() => {
			const ready = typeof window.dashboard_updateCategoryChart === 'function'
				&& typeof window.dashboard_updateSuppliersChart === 'function'
				&& typeof window.dashboard_updateStockStatusChart === 'function';

			// Also ensure that chart instances exist (they are set by dashboard_setChartInstances)
			const instancesReady = window.dashboard_categoryChart || window.dashboard_suppliersChart || window.dashboard_stockStatusChart;

			if (ready && instancesReady) {
				clearInterval(iv);
				resolve();
			}

			if (Date.now() - start > timeoutMs) {
				clearInterval(iv);
				reject(new Error('timeout'));
			}
		}, 200);
	});
}

async function fetchAndUpdateAllCharts() {
	try {
		await Promise.all([
			fetchDashboardStats(),
			fetchCategoryDistribution(),
			fetchTopSuppliers(),
			fetchStockStatus()
		]);
	} catch (err) {
		console.error('Failed to update one or more charts:', err);
	}
}

function getHeaders() {
	try {
		// Use the same explicit header format used across the project files
		// (Content-Type + X-CSRFToken via getCSRFToken()) so requests are consistent.
		return {
			'Content-Type': 'application/json',
			'X-CSRFToken': getCSRFToken()
		};
	} catch (e) {
		// Fallback: no csrf helper available
		return { 'Content-Type': 'application/json' };
	}
}

async function fetchDashboardStats() {
	const url = '/api/dashboard/stats/';
	try {
		const res = await fetch(url, { method: 'GET', headers: getHeaders(), cache: 'no-cache' });
		if (!res.ok) throw new Error(`HTTP ${res.status}`);
		const data = await res.json();
		// Expected: { total_products, pending_orders }
		const stats = {
			totalProducts: Number(data.total_products || 0),
			pendingOrders: Number(data.pending_orders || 0)
		};
		window.dashboard_updateStats(stats);
	} catch (err) {
		console.error('Error fetching dashboard stats:', err);
	}
}

async function fetchCategoryDistribution() {
	const url = '/api/dashboard/categories/';
	try {
		const res = await fetch(url, { method: 'GET', headers: getHeaders(), cache: 'no-cache' });
		if (!res.ok) throw new Error(`HTTP ${res.status}`);
		const data = await res.json();
		// Expected: [{ category_name, count }, ...]
		const mapped = (Array.isArray(data) ? data : []).map(item => ({
			category: item.category_name || 'Uncategorized',
			quantity: Number(item.count || 0)
		}));
		window.dashboard_updateCategoryChart(mapped);
	} catch (err) {
		console.error('Error fetching category distribution:', err);
	}
}

async function fetchTopSuppliers() {
	const url = '/api/dashboard/top-suppliers/?top=3';
	try {
		const res = await fetch(url, { method: 'GET', headers: getHeaders(), cache: 'no-cache' });
		if (!res.ok) throw new Error(`HTTP ${res.status}`);
		const data = await res.json();
		// Expected: [{ supplier_name, products_supplied }, ...]
		const mapped = (Array.isArray(data) ? data : []).map(item => ({
			supplier: item.supplier_name || 'Unknown',
			productCount: Number(item.products_supplied || 0)
		}));
		window.dashboard_updateSuppliersChart(mapped);
	} catch (err) {
		console.error('Error fetching top suppliers:', err);
	}
}

async function fetchStockStatus() {
	const url = '/api/dashboard/stock-status/';
	try {
		const res = await fetch(url, { method: 'GET', headers: getHeaders(), cache: 'no-cache' });
		if (!res.ok) throw new Error(`HTTP ${res.status}`);
		const data = await res.json();
		// Expected: [{ status_label, count }, ...]
		const mapping = {
			normal: 0,
			lowStock: 0,
			outOfStock: 0,
			nearExpiry: 0,
			expired: 0,
		};

		(Array.isArray(data) ? data : []).forEach(item => {
			const label = (item.status_label || '').toLowerCase();
			const c = Number(item.count || 0);
			if (label.includes('normal')) mapping.normal += c;
			else if (label.includes('near')) mapping.nearExpiry += c;
			else if (label.includes('expired')) mapping.expired += c;
			else if (label.includes('low')) mapping.lowStock += c;
			else if (label.includes('out')) mapping.outOfStock += c;
			else mapping.normal += c; // fallback
		});

		window.dashboard_updateStockStatusChart(mapping);
	} catch (err) {
		console.error('Error fetching stock status:', err);
	}
}

// Optionally expose a manual refresh function
window.ChartsManagement = {
	refresh: fetchAndUpdateAllCharts
};

