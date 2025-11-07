
const sampleSuppliers = [
    {
        id: 'SUP001', name: 'MedLife Corp.', contact: 'John Smith', 
        email: 'john@techsolutions.com', phone: '+1 (353) 123-4567',
        status: 'active', supply: 'MedLife Corp.'
    },
    {
        id: 'SUP002', name: 'Global Supplies Co.', contact: 'Maria Garcia', 
        email: 'maria@globalsupplies.com', phone: '+1 (353) 987-6543',
        status: 'active', supply: 'Band-Aid (Adhesive Bandage)'
    },
    {
        id: 'SUP003', name: 'Quality Materials Ltd.', contact: 'Robert Johnson', 
        email: 'robert@qualitymaterials.com', phone: '+1 (353) 456-7890',
        status: 'inactive', supply: 'Betadine Solution (Antiseptic / Disinfectant)',
        archiveReason: 'Supplier no longer in business', archiveDate: '2023-09-15'
    },
    {
        id: 'SUP004', name: 'Support Life Care Warehouse', contact: 'Sarah Williams', 
        email: 'sarah@innovativeparts.com', phone: '+1 (353) 234-5678',
        status: 'active', supply: 'MediCare (Face Mask)'
    },
    {
        id: 'SUP005', name: 'MedCare Group', contact: 'Michael Brown', 
        email: 'michael@primecomponents.com', phone: '+1 (353) 876-5432',
        status: 'active', supply: 'Solmux (Carbocisteine – Expectorant)'
    },
    {
        id: 'SUP006', name: 'UniCare Corp.', contact: 'Jennifer Lee', 
        email: 'jennifer@advancedsystems.com', phone: '+1 (353) 345-6789',
        status: 'active', supply: 'Allerkid (Cetirizine Dihydrochloride – Antihistamine)'
    },
    {
        id: 'SUP007', name: 'Aider Kit Supplies', contact: 'David Wilson', 
        email: 'david@precisiontools.com', phone: '+1 (353) 654-3210',
        status: 'active', supply: 'Green Cross (Isopropyl Alcohol)'
    },
    {
        id: 'SUP008', name: 'Medik Corp.', contact: 'Lisa Anderson', 
        email: 'lisa@digitalinnovations.com', phone: '+1 (353) 789-0123',
        status: 'inactive', supply: 'Vicks Inhaler (Nasal Inhaler)',
        archiveReason: 'Poor quality products', archiveDate: '2023-10-05'
    },
    {
        id: 'SUP009', name: 'Oralkit Corp.', contact: 'James Miller', 
        email: 'james@futuretech.com', phone: '+1 (353) 210-9876',
        status: 'active', supply: 'Babyflo (Cotton Buds / Pads)'
    },
    {
        id: 'SUP010', name: 'SmartCare Team', contact: 'Patricia Taylor', 
        email: 'patricia@smartcomponents.com', phone: '+1 (353) 543-2109',
        status: 'active', supply: 'Biogesic (Paracetamol – Analgesic / Antipyretic)'
    }
];

const sampleCategories = [
    {
        id: 'PHARM-001', name: 'Medicine', description: 'Prescription and over-the-counter medications',
        products: 42, status: 'active',
        subcategories: [
            {id: 'SUB-MED-001', name: 'Antibiotics', classification: 'Prescription', description: 'Medications to treat bacterial infections', count: 12},
            {id: 'SUB-MED-002', name: 'Analgesics', classification: 'OTC', description: 'Pain relief medications', count: 8},
            {id: 'SUB-MED-003', name: 'Cardiovascular', classification: 'Prescription', description: 'Medications for heart and blood pressure', count: 10},
            {id: 'SUB-MED-004', name: 'Vitamins & Supplements', classification: 'OTC', description: 'Nutritional supplements and vitamins', count: 12}
        ]
    },
    {
        id: 'PHARM-002', name: 'Non-Medicine', description: 'Health and wellness products',
        products: 35, status: 'active',
        subcategories: [
            {id: 'SUB-NON-001', name: 'Personal Care', classification: 'Hygiene', description: 'Soaps, shampoos, and personal hygiene products', count: 15},
            {id: 'SUB-NON-002', name: 'First Aid', classification: 'Medical Supplies', description: 'Bandages, antiseptics, and first aid kits', count: 10},
            {id: 'SUB-NON-003', name: 'Medical Equipment', classification: 'Devices', description: 'Blood pressure monitors, thermometers', count: 5},
            {id: 'SUB-NON-004', name: 'Baby Care', classification: 'Infant Products', description: 'Diapers, baby lotions, and feeding supplies', count: 5}
        ]
    },
    {
        id: 'PHARM-003', name: 'Dermatological', description: 'Skin care and treatment products',
        products: 28, status: 'active',
        subcategories: [
            {id: 'SUB-DERM-001', name: 'Topical Creams', classification: 'Prescription', description: 'Medicated creams for skin conditions', count: 8},
            {id: 'SUB-DERM-002', name: 'Moisturizers', classification: 'OTC', description: 'Skin hydration and protection products', count: 10},
            {id: 'SUB-DERM-003', name: 'Acne Treatments', classification: 'OTC', description: 'Products for acne prevention and treatment', count: 6},
            {id: 'SUB-DERM-004', name: 'Sunscreens', classification: 'OTC', description: 'UV protection products', count: 4}
        ]
    },
    {
        id: 'PHARM-004', name: 'Respiratory', description: 'Medications and devices for respiratory conditions',
        products: 22, status: 'active',
        subcategories: [
            {id: 'SUB-RES-001', name: 'Inhalers', classification: 'Prescription', description: 'Asthma and COPD medications', count: 6},
            {id: 'SUB-RES-002', name: 'Decongestants', classification: 'OTC', description: 'Nasal and sinus relief products', count: 8},
            {id: 'SUB-RES-003', name: 'Allergy Medications', classification: 'OTC', description: 'Antihistamines and allergy relief', count: 5},
            {id: 'SUB-RES-004', name: 'Nebulizers', classification: 'Medical Equipment', description: 'Respiratory therapy devices', count: 3}
        ]
    },
    {
        id: 'PHARM-005', name: 'Gastrointestinal', description: 'Digestive health products and medications',
        products: 18, status: 'active',
        subcategories: [
            {id: 'SUB-GAST-001', name: 'Antacids', classification: 'OTC', description: 'Acid reflux and heartburn relief', count: 5},
            {id: 'SUB-GAST-002', name: 'Laxatives', classification: 'OTC', description: 'Constipation relief products', count: 4},
            {id: 'SUB-GAST-003', name: 'Anti-diarrheals', classification: 'OTC', description: 'Diarrhea treatment medications', count: 3},
            {id: 'SUB-GAST-004', name: 'Probiotics', classification: 'OTC', description: 'Digestive health supplements', count: 6}
        ]
    },
    {
        id: 'PHARM-006', name: 'Pediatric', description: 'Medications and products for children',
        products: 24, status: 'archived', archiveReason: 'Low demand category', archiveDate: '2023-08-10',
        subcategories: [
            {id: 'SUB-PED-001', name: 'Children\'s Analgesics', classification: 'OTC', description: 'Pain and fever relief for children', count: 6},
            {id: 'SUB-PED-002', name: 'Baby Formulas', classification: 'Nutrition', description: 'Infant nutrition products', count: 8},
            {id: 'SUB-PED-003', name: 'Pediatric Vitamins', classification: 'OTC', description: 'Vitamins and supplements for children', count: 5},
            {id: 'SUB-PED-004', name: 'Diaper Rash Creams', classification: 'OTC', description: 'Skin protection and treatment for infants', count: 5}
        ]
    },
    {
        id: 'PHARM-007', name: 'Ophthalmic', description: 'Eye care products and medications',
        products: 16, status: 'archived', archiveReason: 'Products moved to other categories', archiveDate: '2023-09-22',
        subcategories: [
            {id: 'SUB-OPH-001', name: 'Eye Drops', classification: 'OTC', description: 'Lubricating and medicated eye drops', count: 8},
            {id: 'SUB-OPH-002', name: 'Contact Lens Solutions', classification: 'OTC', description: 'Cleaning and storage solutions for contacts', count: 5},
            {id: 'SUB-OPH-003', name: 'Eye Ointments', classification: 'Prescription', description: 'Medicated ointments for eye conditions', count: 3}
        ]
    },
    {
        id: 'PHARM-008', name: 'Diabetic Care', description: 'Products for diabetes management',
        products: 20, status: 'archived', archiveReason: 'Merged with Medicine category', archiveDate: '2023-10-12',
        subcategories: [
            {id: 'SUB-DIA-001', name: 'Blood Glucose Monitors', classification: 'Medical Equipment', description: 'Devices to measure blood sugar levels', count: 6},
            {id: 'SUB-DIA-002', name: 'Test Strips', classification: 'Medical Supplies', description: 'Strips for glucose monitoring', count: 8},
            {id: 'SUB-DIA-003', name: 'Insulin', classification: 'Prescription', description: 'Diabetes medication', count: 4},
            {id: 'SUB-DIA-004', name: 'Diabetic Foot Care', classification: 'OTC', description: 'Specialized foot care products', count: 2}
        ]
    },
    {
        id: 'PHARM-009', name: 'Herbal & Natural', description: 'Natural and alternative health products',
        products: 30, status: 'archived', archiveReason: 'Discontinued product line', archiveDate: '2023-07-18',
        subcategories: [
            {id: 'SUB-HERB-001', name: 'Herbal Supplements', classification: 'OTC', description: 'Plant-based health supplements', count: 12},
            {id: 'SUB-HERB-002', name: 'Essential Oils', classification: 'OTC', description: 'Aromatherapy and topical oils', count: 10},
            {id: 'SUB-HERB-003', name: 'Homeopathic Remedies', classification: 'OTC', description: 'Alternative medicine products', count: 8}
        ]
    },
    {
        id: 'PHARM-010', name: 'Surgical Supplies', description: 'Medical supplies for procedures and wound care',
        products: 25, status: 'archived', archiveReason: 'Moved to Non-Medicine category', archiveDate: '2023-11-05',
        subcategories: [
            {id: 'SUB-SURG-001', name: 'Bandages & Dressings', classification: 'Medical Supplies', description: 'Wound care and protection products', count: 10},
            {id: 'SUB-SURG-002', name: 'Sutures & Staples', classification: 'Medical Supplies', description: 'Wound closure materials', count: 5},
            {id: 'SUB-SURG-003', name: 'Medical Gloves', classification: 'Medical Supplies', description: 'Protective gloves for medical use', count: 6},
            {id: 'SUB-SURG-004', name: 'Sterilization Products', classification: 'Medical Supplies', description: 'Products for equipment sterilization', count: 4}
        ]
    }
];
function renderTableWithMinimumRows(tableBody, data, columns, minRows = 8) {
    tableBody.innerHTML = '';
    
    // Add data rows
    data.forEach(item => {
        const row = document.createElement('tr');
        
        columns.forEach(col => {
            const cell = document.createElement('td');
            
            if (col === 'status') {
                cell.innerHTML = `<span class="status ${item[col]}">${item[col] === 'active' ? 'Active' : 'Inactive'}</span>`;
            } else if (col === 'actions') {
                cell.className = 'op-buttons';
                if (item.status === 'active') {
                    cell.innerHTML = `
                        <button class="action-btn view-btn" onclick="toggleSubcategories(this)"><i class="bi bi-eye"></i> View</button>
                        <button class="action-btn edit-btn"><i class="bi bi-pencil"></i> Edit</button>
                        <button class="action-btn archive-btn" onclick="openArchiveModal('${item.id}', '${item.name}', 'category')"><i class="bi bi-archive"></i> Archive</button>
                    `;
                } else {
                    cell.innerHTML = `
                        <button class="action-btn view-btn" onclick="toggleSubcategories(this)"><i class="bi bi-eye"></i> View</button>
                        <button class="action-btn edit-btn"><i class="bi bi-pencil"></i> Edit</button>
                        <button class="action-btn unarchive-btn" onclick="unarchiveItem('${item.id}', 'category')"><i class="fas fa-undo"></i> Unarchive</button>
                    `;
                }
            } else {
                cell.textContent = item[col] || '-';
            }
            
            row.appendChild(cell);
        });
        
        tableBody.appendChild(row);
        
        if (item.subcategories && item.subcategories.length > 0) {
            const subcategoryRow = document.createElement('tr');
            subcategoryRow.className = 'subcategory-row hidden';
            
            const subcategoryCell = document.createElement('td');
            subcategoryCell.colSpan = columns.length;
            
            let subcategoryHTML = `
                <table class="subcategory-table">
                    <thead>
                        <tr>
                            <th>Subcategory ID</th>
                            <th>Subcategory Name</th>
                            <th>Classification</th>
                            <th>Description</th>
                            <th>Product Count</th>
                        </tr>
                    </thead>
                    <tbody>
            `;
            
            item.subcategories.forEach(sub => {
                subcategoryHTML += `
                    <tr>
                        <td>${sub.id}</td>
                        <td>${sub.name}</td>
                        <td>${sub.classification}</td>
                        <td>${sub.description}</td>
                        <td>${sub.count}</td>
                    </tr>
                `;
            });
            
            subcategoryHTML += `
                    </tbody>
                </table>
            `;
            
            subcategoryCell.innerHTML = subcategoryHTML;
            subcategoryRow.appendChild(subcategoryCell);
            tableBody.appendChild(subcategoryRow);
        }
    });

    const emptyRowsNeeded = minRows - data.length;
    if (emptyRowsNeeded > 0) {
        for (let i = 0; i < emptyRowsNeeded; i++) {
            const emptyRow = document.createElement('tr');
            emptyRow.className = 'empty-row';
            
            columns.forEach(() => {
                const cell = document.createElement('td');
                cell.textContent = '-';
                cell.className = 'empty-cell';
                emptyRow.appendChild(cell);
            });
            
            tableBody.appendChild(emptyRow);
        }
    }
}


document.addEventListener('DOMContentLoaded', function() {

    const activeSuppliers = sampleSuppliers.filter(s => s.status === 'active');
    const archivedSuppliers = sampleSuppliers.filter(s => s.status === 'inactive');
    
    renderTableWithMinimumRows(
        document.getElementById('activeSupplierTableBody'),
        activeSuppliers,
        ['id', 'name', 'contact', 'email', 'phone', 'status', 'supply', 'actions']
    );
    
    renderTableWithMinimumRows(
        document.getElementById('archivedSupplierTableBody'),
        archivedSuppliers,
        ['id', 'name', 'contact', 'email', 'phone', 'status', 'supply', 'archiveReason', 'archiveDate', 'actions']
    );
    const activeCategories = sampleCategories.filter(c => c.status === 'active');
    const archivedCategories = sampleCategories.filter(c => c.status === 'archived');
    
    renderTableWithMinimumRows(
        document.getElementById('activeCategoriesTableBody'),
        activeCategories,
        ['id', 'name', 'description', 'products', 'actions']
    );
    
    renderTableWithMinimumRows(
        document.getElementById('archivedCategoriesTableBody'),
        archivedCategories,
        ['id', 'name', 'description', 'products', 'archiveReason', 'archiveDate', 'actions']
    );
    
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
    
    const categoryModal = document.getElementById("categoryModal");
    const categoryModalBtn = document.getElementById("categoryModalBtn");
    const cancelCategoryModalBtn = document.getElementById("cancelCategoryModalBtn");
    
    categoryModalBtn.addEventListener("click", () => (categoryModal.style.display = "flex"));
    cancelCategoryModalBtn.addEventListener("click", () => (categoryModal.style.display = "none"));
    document.getElementById("clearCategoryBtn").addEventListener("click", function() {
        document.getElementById("category-name").value = "";
        document.getElementById("category-description").value = "";
    });
    
    document.getElementById("clearSubcategoryBtn").addEventListener("click", function() {
        document.getElementById("category-classification").value = "";
        document.getElementById("subcategory-name").value = "";
        document.getElementById("subcategory-description").value = "";
    });
    
    // Archive modal
    const archiveModal = document.getElementById("archiveModal");
    const cancelArchiveBtn = document.getElementById("cancelArchiveBtn");
    
    cancelArchiveBtn.addEventListener("click", () => (archiveModal.style.display = "none"));
    
    window.onclick = (e) => {
        if (e.target === modal) modal.style.display = "none";
        if (e.target === archiveModal) archiveModal.style.display = "none";
        if (e.target === categoryModal) categoryModal.style.display = "none";
    };
    
    const supplierToggle = document.getElementById('supplierToggle');
    const supplierOptions = supplierToggle.querySelectorAll('.toggle-option');
    const activeSuppliersTable = document.getElementById('activeSuppliersTable');
    const archivedSuppliersTable = document.getElementById('archivedSuppliersTable');
    
    supplierOptions.forEach(option => {
        option.addEventListener('click', function() {
            supplierOptions.forEach(opt => opt.classList.remove('active'));
            this.classList.add('active');
            
            const type = this.getAttribute('data-type');
            
            if (type === 'active') {
                activeSuppliersTable.style.display = 'table';
                archivedSuppliersTable.style.display = 'none';
            } else {
                activeSuppliersTable.style.display = 'none';
                archivedSuppliersTable.style.display = 'table';
            }
        });
    });

    const categoryToggle = document.getElementById('categoryToggle');
    const categoryOptions = categoryToggle.querySelectorAll('.toggle-option');
    const activeCategoriesTable = document.getElementById('activeCategoriesTable');
    const archivedCategoriesTable = document.getElementById('archivedCategoriesTable');
    
    categoryOptions.forEach(option => {
        option.addEventListener('click', function() {
            categoryOptions.forEach(opt => opt.classList.remove('active'));
            this.classList.add('active');
            
            const type = this.getAttribute('data-type');
            
            if (type === 'active') {
                activeCategoriesTable.style.display = 'table';
                archivedCategoriesTable.style.display = 'none';
            } else {
                activeCategoriesTable.style.display = 'none';
                archivedCategoriesTable.style.display = 'table';
            }
        });
    });
});

function toggleSubcategories(button) {
    const row = button.closest('tr');
    const subcategoryRow = row.nextElementSibling;
    subcategoryRow.classList.toggle('hidden');
    if (subcategoryRow.classList.contains('hidden')) {
        button.innerHTML = '<i class="bi bi-eye"></i> View';
    } else {
        button.innerHTML = '<i class="bi bi-eye-slash"></i> Hide';
    }
}

let currentArchiveItem = null;
let currentArchiveType = null;

function openArchiveModal(id, name, type) {
    currentArchiveItem = id;
    currentArchiveType = type;
    
    const archiveMessage = document.getElementById('archiveMessage');
    archiveMessage.textContent = `Are you sure you want to archive ${name}?`;
    
    document.getElementById('archiveReason').value = '';
    document.getElementById('archiveModal').style.display = 'flex';
    document.getElementById('confirmArchiveBtn').onclick = function() {
        const reason = document.getElementById('archiveReason').value;
        if (!reason.trim()) {
            alert('Please provide a reason for archiving.');
            return;
        }
        console.log(`Archiving ${type} ${id} with reason: ${reason}`);
        document.getElementById('archiveModal').style.display = 'none';
        alert(`${name} has been archived successfully.`);
    };
}

function unarchiveItem(id, type) {
    console.log(`Unarchiving ${type} ${id}`);    
    alert(`Item has been unarchived successfully.`);
    
}