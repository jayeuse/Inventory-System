document.addEventListener('DOMContentLoaded', function() {
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

    // Pagination functionality (to be implemented by backend)
    const prevBtn = document.getElementById('productslist_prevBtn');
    const nextBtn = document.getElementById('productslist_nextBtn');

    if (prevBtn) {
        prevBtn.addEventListener('click', function() {
            console.log('Previous page clicked');
            // Backend will handle pagination logic
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', function() {
            console.log('Next page clicked');
            // Backend will handle pagination logic
        });
    }

    // Manage Products button - redirect to Product Management
    const manageProductBtn = document.getElementById('productslist_manageProductBtn');
    
    if (manageProductBtn) {
        manageProductBtn.addEventListener('click', function() {
            // Redirect to Product Management page
            window.location.href = '../../Settings + Supplier & Category/product_management/product_management.html';
        });
    }
});
