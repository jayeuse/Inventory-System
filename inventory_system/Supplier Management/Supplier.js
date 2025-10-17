      const modal = document.getElementById("addSupplierModal");
      const addBtn = document.getElementById("addSupplierBtn");
      const cancelBtn = document.getElementById("cancelBtn");
      const tabs = document.querySelectorAll(".tab");

   
      addBtn.addEventListener("click", () => (modal.style.display = "flex"));
      cancelBtn.addEventListener("click", () => (modal.style.display = "none"));

      tabs.forEach(tab => {
        tab.addEventListener("click", () => {
          tabs.forEach(t => t.classList.remove("active"));
          tab.classList.add("active");
  
          const card = document.querySelector('.card');
          if (tab.dataset.tab === 'suppliers') {
            card.style.background = 'rgba(255, 255, 255, 0.85)';
            card.style.borderColor = 'rgba(255, 255, 255, 0.5)';
          } else {
            card.style.background = 'rgba(255, 255, 255, 0.85)';
            card.style.borderColor = 'rgba(255, 255, 255, 0.5)';
          }
        });
      });

      window.onclick = (e) => {
        if (e.target === modal) modal.style.display = "none";
      };
