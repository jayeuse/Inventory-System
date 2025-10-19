document.addEventListener('DOMContentLoaded', function() {
    console.log('Point of Sale page loaded');
    
    // Tab navigation functionality
    const tabs = document.querySelectorAll('.tab');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const url = this.getAttribute('data-url');
            
            // If the tab has a URL, navigate to it
            if (url) {
                window.location.href = url;
            }
        });
    });
    
    // POS functionality will be implemented here
    // This is a placeholder for future development
});
