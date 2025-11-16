// Logout Management
// Handles logout functionality across all pages with sidebar

document.addEventListener("DOMContentLoaded", function () {
  // Wait for sidebar to load before attaching handlers
  setTimeout(initializeLogout, 100);
});

function initializeLogout() {
  const logoutIcon = document.querySelector(".sidebar-component .logout-icon");
  const logoutLabel = document.querySelector(".sidebar-component .logout-label");

  if (logoutIcon) {
    logoutIcon.addEventListener("click", handleLogout);
  }

  if (logoutLabel) {
    logoutLabel.addEventListener("click", handleLogout);
  }
}

async function handleLogout() {
  if (!confirm("Are you sure you want to log out?")) {
    return;
  }

  try {
    const response = await fetch('/api/auth/logout/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
      }
    });

    if (response.ok) {
      // Redirect to login page
      window.location.href = '/login/';
    } else {
      alert('Logout failed. Please try again.');
    }
  } catch (error) {
    console.error('Logout error:', error);
    alert('An error occurred during logout.');
  }
}
