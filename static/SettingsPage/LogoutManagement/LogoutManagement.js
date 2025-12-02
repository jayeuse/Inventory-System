// Logout Management
// Handles logout functionality across all pages with sidebar

let notifyLoader;

document.addEventListener("DOMContentLoaded", function () {
  // Wait for sidebar to load before attaching handlers
  setTimeout(initializeLogout, 100);
});

function loadNotificationsModule() {
  if (typeof window.customConfirm === 'function') {
    return Promise.resolve();
  }

  if (notifyLoader) {
    return notifyLoader;
  }

  notifyLoader = new Promise((resolve) => {
    const existing = document.querySelector('script[data-notify-script="true"]');
    if (existing) {
      existing.addEventListener('load', () => resolve(), { once: true });
      existing.addEventListener('error', () => resolve(), { once: true });
      return;
    }

    const script = document.createElement('script');
    script.src = '/static/utils/notifications.js';
    script.async = true;
    script.setAttribute('data-notify-script', 'true');
    script.onload = () => resolve();
    script.onerror = () => resolve();
    document.body.appendChild(script);
  });

  return notifyLoader;
}

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
  await loadNotificationsModule();

  const confirmHandler = typeof window.customConfirm === 'function'
    ? (options) => window.customConfirm(options)
    : () => Promise.resolve(window.confirm("Are you sure you want to log out?"));

  const wantsToLogout = await confirmHandler({
    title: 'Confirm Logout',
    message: 'Are you sure you want to sign out of your session?',
    confirmText: 'Logout',
    cancelText: 'Stay signed in',
    tone: 'danger'
  });

  if (!wantsToLogout) {
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
