document.addEventListener('DOMContentLoaded', function() {
            const tabs = document.querySelectorAll('.tab');
            const tabContents = document.querySelectorAll('.tab-content');
            
            tabs.forEach(tab => {
                tab.addEventListener('click', function() {
                    const tabId = this.getAttribute('data-tab');
                    
                    tabs.forEach(t => t.classList.remove('active'));
                    tabContents.forEach(c => c.classList.remove('active'));
                    
                   
                    this.classList.add('active');
                    document.getElementById(`${tabId}-content`).classList.add('active');
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