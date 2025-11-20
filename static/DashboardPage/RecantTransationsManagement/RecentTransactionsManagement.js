// Recent Transactions Management
// Fetch recent transactions from API and render timeline
(function () {
  async function fetchTransactions() {
    try {
      const url = '/api/transactions/?page_size=50';
      const res = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': (typeof getCSRFToken === 'function') ? getCSRFToken() : getCSRFToken()
        }
      });

      if (!res.ok) {
        console.error('Failed to fetch transactions', res.status);
        return [];
      }

      const data = await res.json();
      return Array.isArray(data) ? data : (data.results || []);
    } catch (err) {
      console.error('Error fetching transactions', err);
      return [];
    }
  }

  function formatTime(dt) {
    // API may return a pre-formatted date string (e.g. 'Oct 21, 2025 05:00 PM')
    if (!dt) return '';
    // Try native Date parse first (ISO strings)
    const d = new Date(dt);
    if (!isNaN(d)) {
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    // Fallback: extract time like '05:00 PM' from formatted string
    const m = String(dt).match(/(\d{1,2}:\d{2}\s?(AM|PM|am|pm))/);
    if (m) return m[0];
    // As a last resort, return the input after the comma (if present)
    const parts = String(dt).split(',');
    if (parts.length > 1) {
      const after = parts.slice(1).join(',').trim();
      const tokens = after.split(' ');
      return tokens.slice(-2).join(' ');
    }
    return String(dt);
  }

  function formatDate(dt) {
    if (!dt) return '';
    const d = new Date(dt);
    if (!isNaN(d)) {
      return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
    }

    // If API already returned formatted string like 'Oct 21, 2025 05:00 PM', extract date part
    const m = String(dt).match(/^[A-Za-z]{3,}\s+\d{1,2},\s*\d{4}/);
    if (m) return m[0];
    // Fallback to original string
    return String(dt);
  }

  function renderTimelineItems(items) {
    // Expect each item to have: product_name, quantity_change, date_of_transaction, transaction_id
    return items
      .map(t => {
        // Serializer returns quantity_change formatted (e.g. '+5' or '-3')
        const qtyRaw = t.quantity_change != null ? String(t.quantity_change) : '0';
        // Try to parse numeric value from the string to determine direction reliably
        const parsed = Number(qtyRaw.replace(/[^0-9\-\.\+]/g, ''));
        const hasNumeric = !isNaN(parsed);
        // Prefer numeric sign when available (handles ADJ correctly)
        let type;
        if (hasNumeric && parsed !== 0) {
          type = parsed > 0 ? 'in' : 'out';
        } else {
          const txType = (t.transaction_type || '').toString().toLowerCase();
          type = (txType.includes('receive') || txType.includes('in')) ? 'in' : 'out';
        }

        const txType = (t.transaction_type || '').toString().toLowerCase();
        const isAdjustment = txType.includes('adj') || txType.includes('adjust');
        const qtyDisplay = qtyRaw.replace(/^\+/, '');
        const product = t.product_name || t.product_id || '-';
        const note = t.remarks || t.performed_by || '';
        const time = formatTime(t.date_of_transaction);

        return `
          <article class="timeline-item">
            <time class="timeline-time">${time}</time>
            <span class="timeline-marker"></span>
            <section class="timeline-content">
              <div class="transaction-header">
                <div class="transaction-details">
                  <div class="transaction-icon ${type}">
                    <i class="fas ${type === 'in' ? 'fa-arrow-down' : 'fa-arrow-up'}"></i>
                  </div>
                  <div class="transaction-info">
                    <p class="transaction-units ${type}">${qtyDisplay} - ${product}</p>
                    <p class="transaction-product">${note}</p>
                  </div>
                </div>
                <span class="transaction-id">#${t.transaction_id || ''} · ${formatDate(t.date_of_transaction)}</span>
              </div>
            </section>
          </article>
        `;
      })
      .join('\n');
  }

  async function loadAndRender() {
    const container = document.getElementById('transactions-content') || document.querySelector('#transactions_page');
    if (!container) return;

    const timeline = container.querySelector('.timeline');
    if (!timeline) return;

    timeline.innerHTML = '<div class="loading">Loading recent transactions...</div>';

    const items = await fetchTransactions();

    if (!items || items.length === 0) {
      timeline.innerHTML = '<div class="card"><div class="card-body">No recent transactions found.</div></div>';
      return;
    }

    timeline.innerHTML = renderTimelineItems(items);
  }

  // Auto-run when page loads or when module is injected
  document.addEventListener('DOMContentLoaded', () => {
    // If the recent transactions HTML was loaded into a parent page, run after a short delay
    setTimeout(() => { loadAndRender(); }, 50);
  });

  // Expose for manual invocation
  window.RecentTransactionsManagement = {
    loadAndRender
  };
})();
