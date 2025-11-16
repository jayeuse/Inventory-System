document.addEventListener("DOMContentLoaded", function () {
      const icons = document.querySelectorAll(".nav-icon");
      const labels = document.querySelectorAll(".nav-label");
      const logoutLabel = document.querySelector(".logout-label");
      const logoutIcon = document.querySelector(".logout-icon");

      function setActive(itemName) {
        icons.forEach(icon => icon.classList.remove("active"));
        labels.forEach(label => label.classList.remove("active"));
        if (logoutLabel) logoutLabel.classList.remove("active");
        if (logoutIcon) logoutIcon.classList.remove("active");

        if (itemName === "logout") {
          if (logoutLabel) logoutLabel.classList.add("active");
          if (logoutIcon) logoutIcon.classList.add("active");
        } else {
          document.querySelectorAll(`[data-item="${itemName}"]`).forEach(el => el.classList.add("active"));
        }
      }

      // Add click handlers for navigation items only
      [...icons, ...labels].forEach(el => {
        el.addEventListener("click", () => {
          const itemName = el.dataset.item;
          if (itemName !== "logout") {
            setActive(itemName);
          }
        });
      });
      
      // Note: Logout handlers are in LogoutManagement.js
    });