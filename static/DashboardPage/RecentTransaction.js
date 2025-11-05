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

            document.getElementById('timeFilter').addEventListener('change', function() {
                console.log('Time filter changed to:', this.value);
            });

            document.getElementById('typeFilter').addEventListener('change', function() {
                console.log('Type filter changed to:', this.value);
            });
        });