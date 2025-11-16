// CSRF Token Utility Functions

/**
 * Get CSRF token from cookie
 * Django sets the CSRF token in a cookie named 'csrftoken'
 */
function getCSRFToken() {
  const name = 'csrftoken';
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

/**
 * Create headers object with CSRF token for fetch requests
 * @param {Object} additionalHeaders - Any additional headers to include
 * @returns {Object} Headers object with CSRF token and Content-Type
 */
function getCSRFHeaders(additionalHeaders = {}) {
  return {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCSRFToken(),
    ...additionalHeaders
  };
}

/**
 * Wrapper for fetch with automatic CSRF token inclusion for state-changing methods
 * @param {string} url - The URL to fetch
 * @param {Object} options - Fetch options (method, body, headers, etc.)
 * @returns {Promise} Fetch promise
 */
async function csrfFetch(url, options = {}) {
  const method = (options.method || 'GET').toUpperCase();
  
  // Add CSRF token for state-changing methods (POST, PUT, PATCH, DELETE)
  if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
    options.headers = {
      ...options.headers,
      'X-CSRFToken': getCSRFToken()
    };
    
    // Ensure Content-Type is set for JSON data
    if (options.body && typeof options.body === 'string') {
      options.headers['Content-Type'] = options.headers['Content-Type'] || 'application/json';
    }
  }
  
  return fetch(url, options);
}
