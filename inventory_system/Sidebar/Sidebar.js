document.addEventListener("DOMContentLoaded", function () {
      const icons = document.querySelectorAll(".nav-icon");
      const labels = document.querySelectorAll(".nav-label");
      const logoutLabel = document.querySelector(".logout-label");
      const logoutIcon = document.querySelector(".logout-icon");

      function setActive(itemName) {
        icons.forEach(icon => icon.classList.remove("active"));
        labels.forEach(label => label.classList.remove("active"));
        logoutLabel.classList.remove("active");
        logoutIcon.classList.remove("active");

        if (itemName === "Logout") {
          logoutLabel.classList.add("active");
          logoutIcon.classList.add("active");
        } else {
          document.querySelectorAll(`[data-item="${itemName}"]`).forEach(el => el.classList.add("active"));
        }
      }

      [...icons, ...labels, logoutLabel, logoutIcon].forEach(el =>
        el.addEventListener("click", () => setActive(el.dataset.item))
      );
    });