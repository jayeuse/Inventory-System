document.addEventListener('DOMContentLoaded', function() {
            const tabs = document.querySelectorAll('.tab');
            const tabContents = document.querySelectorAll('.tab-content');
            
            // Check URL parameters for tab navigation
            const urlParams = new URLSearchParams(window.location.search);
            const tabParam = urlParams.get('tab');
            
            // Function to activate a specific tab
            function activateTab(tabId) {
                tabs.forEach(t => t.classList.remove('active'));
                tabContents.forEach(c => c.classList.remove('active'));
                
                const targetTab = document.querySelector(`[data-tab="${tabId}"]`);
                const targetContent = document.getElementById(`${tabId}-content`);
                
                if (targetTab && targetContent) {
                    targetTab.classList.add('active');
                    targetContent.classList.add('active');
                }
            }
            
            // If there's a tab parameter in URL, activate that tab
            if (tabParam) {
                activateTab(tabParam);
            }
            
            tabs.forEach(tab => {
                tab.addEventListener('click', function() {
                    const tabId = this.getAttribute('data-tab');
                    const url = this.getAttribute('data-url');
                    
                    // If tab has a URL, navigate to it
                    if (url) {
                        window.location.href = url;
                    } else {
                        activateTab(tabId);
                    }
                });
            });
            
           
            const themeOptions = document.querySelectorAll('.theme-option');
            
            themeOptions.forEach(option => {
                option.addEventListener('click', function() {
                   
                    themeOptions.forEach(opt => opt.classList.remove('active'));
                    
                    this.classList.add('active');
                    
                    const theme = this.querySelector('.theme-name').textContent;
                    console.log(`Theme changed to: ${theme}`);
                });
            });
            
            const modal = document.getElementById("addSupplierModal");
            const addBtn = document.getElementById("addSupplierBtn");
            const cancelBtn = document.getElementById("cancelBtn");
            
            addBtn.addEventListener("click", () => (modal.style.display = "flex"));
            cancelBtn.addEventListener("click", () => (modal.style.display = "none"));
            
            window.onclick = (e) => {
                if (e.target === modal) modal.style.display = "none";
            };
        });

        function toggleSubcategories(button) {
            const row = button.closest('tr');
            const subcategoryRow = row.nextElementSibling;
            
            // Toggle the visibility of the subcategory row
            subcategoryRow.classList.toggle('hidden');
            
            // Update button text and icon based on state
            if (subcategoryRow.classList.contains('hidden')) {
                button.innerHTML = '<i class="bi bi-eye"></i> View';
            } else {
                button.innerHTML = '<i class="bi bi-eye-slash"></i> Hide';
            }
        }