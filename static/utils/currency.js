/**
 * Currency Utility Module
 * Handles display-only currency conversion for the Inventory System
 * Base currency: PHP (Philippine Peso) - all prices stored in PHP
 */

// Exchange rates relative to PHP (updated rates - these can be adjusted as needed)
const EXCHANGE_RATES = {
    PHP: 1,
    USD: 0.0175,    // 1 PHP = 0.0175 USD (1 USD ≈ 57 PHP)
    EUR: 0.0161,    // 1 PHP = 0.0161 EUR (1 EUR ≈ 62 PHP)
    GBP: 0.0138,    // 1 PHP = 0.0138 GBP (1 GBP ≈ 72 PHP)
    JPY: 2.63,      // 1 PHP = 2.63 JPY (1 JPY ≈ 0.38 PHP)
    KRW: 23.68,     // 1 PHP = 23.68 KRW
    CNY: 0.127,     // 1 PHP = 0.127 CNY
    SGD: 0.0234     // 1 PHP = 0.0234 SGD
};

// Currency symbols and configurations
const CURRENCY_CONFIG = {
    PHP: { symbol: '₱', code: 'PHP', name: 'Philippine Peso', decimals: 2, position: 'before' },
    USD: { symbol: '$', code: 'USD', name: 'US Dollar', decimals: 2, position: 'before' },
    EUR: { symbol: '€', code: 'EUR', name: 'Euro', decimals: 2, position: 'before' },
    GBP: { symbol: '£', code: 'GBP', name: 'British Pound', decimals: 2, position: 'before' },
    JPY: { symbol: '¥', code: 'JPY', name: 'Japanese Yen', decimals: 0, position: 'before' },
    KRW: { symbol: '₩', code: 'KRW', name: 'Korean Won', decimals: 0, position: 'before' },
    CNY: { symbol: '¥', code: 'CNY', name: 'Chinese Yuan', decimals: 2, position: 'before' },
    SGD: { symbol: 'S$', code: 'SGD', name: 'Singapore Dollar', decimals: 2, position: 'before' }
};

// Current selected currency (default to PHP)
let currentCurrency = 'PHP';

/**
 * Initialize the currency system
 * Loads saved currency preference from localStorage
 */
function initializeCurrency() {
    const savedCurrency = localStorage.getItem('selectedCurrency');
    if (savedCurrency && CURRENCY_CONFIG[savedCurrency]) {
        currentCurrency = savedCurrency;
    }
    
    // Update any currency selectors on the page
    const currencySelect = document.getElementById('currencySelect');
    if (currencySelect) {
        currencySelect.value = currentCurrency;
        currencySelect.addEventListener('change', function() {
            setCurrency(this.value);
        });
    }
    
    return currentCurrency;
}

/**
 * Set the current display currency
 * @param {string} currencyCode - The currency code (e.g., 'USD', 'PHP')
 */
function setCurrency(currencyCode) {
    if (CURRENCY_CONFIG[currencyCode]) {
        currentCurrency = currencyCode;
        localStorage.setItem('selectedCurrency', currencyCode);
        
        // Dispatch custom event for components that need to update
        window.dispatchEvent(new CustomEvent('currencyChanged', { 
            detail: { currency: currencyCode } 
        }));
        
        console.log(`Currency changed to: ${currencyCode}`);
    } else {
        console.warn(`Invalid currency code: ${currencyCode}`);
    }
}

/**
 * Get the current currency code
 * @returns {string} Current currency code
 */
function getCurrentCurrency() {
    return currentCurrency;
}

/**
 * Get currency configuration
 * @param {string} currencyCode - Optional currency code, uses current if not provided
 * @returns {object} Currency configuration object
 */
function getCurrencyConfig(currencyCode = currentCurrency) {
    return CURRENCY_CONFIG[currencyCode] || CURRENCY_CONFIG.PHP;
}

/**
 * Convert amount from PHP to the target currency
 * @param {number} amountInPHP - Amount in Philippine Peso
 * @param {string} targetCurrency - Target currency code (uses current if not provided)
 * @returns {number} Converted amount
 */
function convertFromPHP(amountInPHP, targetCurrency = currentCurrency) {
    const rate = EXCHANGE_RATES[targetCurrency] || 1;
    return amountInPHP * rate;
}

/**
 * Convert amount from any currency to PHP
 * @param {number} amount - Amount in source currency
 * @param {string} sourceCurrency - Source currency code
 * @returns {number} Amount in PHP
 */
function convertToPHP(amount, sourceCurrency) {
    const rate = EXCHANGE_RATES[sourceCurrency] || 1;
    return amount / rate;
}

/**
 * Format a price amount for display
 * Converts from PHP (base currency) and formats with proper symbol
 * @param {number} amountInPHP - Amount in Philippine Peso (stored value)
 * @param {object} options - Formatting options
 * @param {string} options.currency - Override currency for this format
 * @param {boolean} options.showCode - Show currency code instead of/with symbol
 * @param {boolean} options.compact - Use compact notation for large numbers
 * @returns {string} Formatted price string
 */
function formatCurrency(amountInPHP, options = {}) {
    const targetCurrency = options.currency || currentCurrency;
    const config = CURRENCY_CONFIG[targetCurrency];
    
    if (amountInPHP === null || amountInPHP === undefined || isNaN(amountInPHP)) {
        return `${config.symbol}0.00`;
    }
    
    // Convert from PHP to target currency
    const convertedAmount = convertFromPHP(Number(amountInPHP), targetCurrency);
    
    // Format the number
    let formattedNumber;
    if (options.compact && Math.abs(convertedAmount) >= 1000) {
        formattedNumber = formatCompactNumber(convertedAmount, config.decimals);
    } else {
        formattedNumber = convertedAmount.toFixed(config.decimals);
        // Add thousand separators
        formattedNumber = Number(formattedNumber).toLocaleString('en-US', {
            minimumFractionDigits: config.decimals,
            maximumFractionDigits: config.decimals
        });
    }
    
    // Build the formatted string
    if (options.showCode) {
        return `${config.code} ${formattedNumber}`;
    }
    
    if (config.position === 'before') {
        return `${config.symbol}${formattedNumber}`;
    } else {
        return `${formattedNumber}${config.symbol}`;
    }
}

/**
 * Format number in compact notation (e.g., 1.2K, 3.5M)
 * @param {number} num - Number to format
 * @param {number} decimals - Number of decimal places
 * @returns {string} Compact formatted number
 */
function formatCompactNumber(num, decimals = 2) {
    const absNum = Math.abs(num);
    const sign = num < 0 ? '-' : '';
    
    if (absNum >= 1e9) {
        return sign + (absNum / 1e9).toFixed(decimals) + 'B';
    } else if (absNum >= 1e6) {
        return sign + (absNum / 1e6).toFixed(decimals) + 'M';
    } else if (absNum >= 1e3) {
        return sign + (absNum / 1e3).toFixed(decimals) + 'K';
    }
    return num.toFixed(decimals);
}

/**
 * Get display text showing the conversion rate
 * @returns {string} Rate display text (e.g., "1 PHP = 0.0175 USD")
 */
function getExchangeRateDisplay() {
    if (currentCurrency === 'PHP') {
        return 'Base currency (no conversion)';
    }
    const rate = EXCHANGE_RATES[currentCurrency];
    const config = CURRENCY_CONFIG[currentCurrency];
    return `1 PHP = ${rate} ${config.code}`;
}

/**
 * Get all available currencies
 * @returns {Array} Array of currency config objects
 */
function getAvailableCurrencies() {
    return Object.values(CURRENCY_CONFIG);
}

// Export functions to global scope
window.initializeCurrency = initializeCurrency;
window.setCurrency = setCurrency;
window.getCurrentCurrency = getCurrentCurrency;
window.getCurrencyConfig = getCurrencyConfig;
window.formatCurrency = formatCurrency;
window.convertFromPHP = convertFromPHP;
window.convertToPHP = convertToPHP;
window.getExchangeRateDisplay = getExchangeRateDisplay;
window.getAvailableCurrencies = getAvailableCurrencies;
