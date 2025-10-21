document.addEventListener("DOMContentLoaded", function () {
  // Tab navigation functionality
  const tabs = document.querySelectorAll(".tab");
  const pages = document.querySelectorAll(".page-content");

  // Function to switch pages
  function switchPage(pageId) {
    // Update URL without page reload
    history.pushState({ page: pageId }, "", `#${pageId}`);

    // Update active tab
    tabs.forEach((tab) => {
      if (tab.getAttribute("data-page") === pageId) {
        tab.classList.add("active");
      } else {
        tab.classList.remove("active");
      }
    });

    // Show active page
    pages.forEach((page) => {
      if (page.id === `${pageId}-page`) {
        page.classList.add("active");
      } else {
        page.classList.remove("active");
      }
    });
  }

  // Tab click event
  tabs.forEach((tab) => {
    tab.addEventListener("click", function () {
      const pageId = this.getAttribute("data-page");
      switchPage(pageId);
    });
  });

  // Handle browser back/forward buttons
  window.addEventListener("popstate", function (event) {
    const pageId = event.state ? event.state.page : "products";
    switchPage(pageId);
  });

  // Check URL hash on page load
  const initialPage = window.location.hash.substring(1) || "products";
  switchPage(initialPage);

  // Products List functionality
  const prevBtn = document.getElementById("productslist_prevBtn");
  const nextBtn = document.getElementById("productslist_nextBtn");

  if (prevBtn) {
    prevBtn.addEventListener("click", function () {
      console.log("Previous page clicked");
      // Backend will handle pagination logic
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener("click", function () {
      console.log("Next page clicked");
      // Backend will handle pagination logic
    });
  }

  // Manage Products button - redirect to Product Management
  const manageProductBtn = document.getElementById(
    "productslist_manageProductBtn"
  );

  if (manageProductBtn) {
    manageProductBtn.addEventListener("click", function () {
      // Redirect to Product Management page
      window.location.href =
        "/static/SettingsPage/System_Settings.html#products";
    });
  }

  // Search functionality for products
  const searchInput = document.getElementById("productslist_searchInput");
  const categoryFilter = document.getElementById("productslist_categoryFilter");

  if (searchInput) {
    searchInput.addEventListener("input", function () {
      console.log("Searching for:", this.value);
      // Implement search functionality
    });
  }

  if (categoryFilter) {
    categoryFilter.addEventListener("change", function () {
      console.log("Category filter changed to:", this.value);
      // Implement category filtering
    });
  }
});
