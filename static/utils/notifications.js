(function () {
  const TOAST_LIMIT = 4;
  const DEFAULT_DURATION = 4500;
  const state = {
    container: null,
    toastCount: 0,
    confirmOpen: false,
  };

  const ICONS = {
    success: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M9.55 16.2 5.7 12.35l1.4-1.4 2.45 2.45 6.35-6.35 1.4 1.4Z"/></svg>',
    info: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M11 17h2v-6h-2Zm0-8h2V7h-2Zm1-7a11 11 0 1 0 0 22 11 11 0 0 0 0-22Z"/></svg>',
    warning: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M1 21h22L12 2Zm12-3h-2v-2h2Zm0-3h-2v-4h2Z"/></svg>',
    danger: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="m12 10.586 4.95-4.95 1.414 1.414-4.95 4.95 4.95 4.95-1.414 1.414-4.95-4.95-4.95 4.95L5.636 16.95l4.95-4.95-4.95-4.95L7.05 5.636Z"/></svg>',
  };

  const TITLES = {
    success: 'Success',
    info: 'Heads up',
    warning: 'Check again',
    danger: 'Something went wrong',
  };

  function whenReady(callback) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', callback, { once: true });
    } else {
      callback();
    }
  }

  function ensureContainer() {
    if (state.container && document.body.contains(state.container)) {
      return state.container;
    }

    const container = document.createElement('div');
    container.id = 'notification-root';
    container.setAttribute('role', 'region');
    container.setAttribute('aria-live', 'polite');
    document.body.appendChild(container);
    state.container = container;
    return container;
  }

  function normalizeType(type) {
    if (!type) return 'info';
    const map = { error: 'danger', warn: 'warning' };
    const normalized = (type + '').toLowerCase();
    return map[normalized] || normalized;
  }

  function inferType(message) {
    if (!message) return 'info';
    const text = String(message).toLowerCase();
    if (text.includes('success')) return 'success';
    if (text.includes('warning') || text.includes('caution')) return 'warning';
    if (
      text.includes('error') ||
      text.includes('failed') ||
      text.includes('cannot') ||
      text.includes("can't")
    ) {
      return 'danger';
    }
    return 'info';
  }

  function removeToast(toast) {
    if (!toast) return;
    toast.classList.add('toast-leaving');
    const remove = () => toast.remove();
    toast.addEventListener('animationend', remove, { once: true });
  }

  function showToast({ title, message, type = 'info', duration = DEFAULT_DURATION } = {}) {
    whenReady(() => {
      const container = ensureContainer();
      const toastType = normalizeType(type);
      const toastTitle = title || TITLES[toastType] || 'Notice';
      const toastMessage = message || '';

      while (container.children.length >= TOAST_LIMIT) {
        removeToast(container.firstElementChild);
      }

      const toast = document.createElement('article');
      toast.className = `toast-card toast-${toastType}`;
      toast.setAttribute('role', 'alert');
      toast.setAttribute('aria-live', 'assertive');
      toast.dataset.toastId = `toast-${++state.toastCount}`;

      const icon = document.createElement('div');
      icon.className = 'toast-icon';
      icon.innerHTML = ICONS[toastType] || ICONS.info;

      const body = document.createElement('div');
      body.className = 'toast-body';

      const h4 = document.createElement('div');
      h4.className = 'toast-title';
      h4.textContent = toastTitle;

      const text = document.createElement('p');
      text.className = 'toast-message';
      text.textContent = toastMessage;

      body.appendChild(h4);
      body.appendChild(text);

      const close = document.createElement('button');
      close.className = 'toast-close';
      close.setAttribute('aria-label', 'Dismiss notification');
      close.innerHTML = '&times;';
      close.addEventListener('click', () => removeToast(toast));

      const progress = document.createElement('span');
      progress.className = 'toast-progress';
      progress.style.setProperty('--toast-duration', `${duration}ms`);

      toast.appendChild(icon);
      toast.appendChild(body);
      toast.appendChild(close);
      toast.appendChild(progress);

      container.appendChild(toast);

      setTimeout(() => removeToast(toast), duration);
    });
  }

  function confirmDialog({
    title = 'Please confirm',
    message = 'Are you sure?',
    confirmText = 'Confirm',
    cancelText = 'Cancel',
    tone = 'info',
  } = {}) {
    return new Promise((resolve) => {
      whenReady(() => {
        if (state.confirmOpen) {
          resolve(false);
          return;
        }
        state.confirmOpen = true;

        const previousFocus = document.activeElement;
        const overlay = document.createElement('div');
        overlay.id = 'confirm-overlay';

        const dialog = document.createElement('section');
        dialog.className = 'confirm-dialog';
        dialog.setAttribute('role', 'dialog');
        dialog.setAttribute('aria-modal', 'true');
        dialog.setAttribute('aria-label', title);

        const heading = document.createElement('h3');
        heading.className = 'confirm-title';
        heading.textContent = title;

        const copy = document.createElement('p');
        copy.className = 'confirm-message';
        copy.textContent = message;

        const actions = document.createElement('div');
        actions.className = 'confirm-actions';

        const cancelBtn = document.createElement('button');
        cancelBtn.className = 'confirm-btn cancel';
        cancelBtn.textContent = cancelText;

        const confirmBtn = document.createElement('button');
        confirmBtn.className = 'confirm-btn confirm';
        if (normalizeType(tone) === 'danger') {
          confirmBtn.classList.add('danger');
        }
        confirmBtn.textContent = confirmText;

        const cleanup = (result) => {
          overlay.remove();
          state.confirmOpen = false;
          if (previousFocus && typeof previousFocus.focus === 'function') {
            previousFocus.focus();
          }
          resolve(result);
        };

        cancelBtn.addEventListener('click', () => cleanup(false));
        confirmBtn.addEventListener('click', () => cleanup(true));
        overlay.addEventListener('click', (event) => {
          if (event.target === overlay) {
            cleanup(false);
          }
        });

        dialog.addEventListener('keydown', (event) => {
          if (event.key === 'Escape') {
            event.preventDefault();
            cleanup(false);
          }
          if (event.key === 'Tab') {
            const focusables = [cancelBtn, confirmBtn];
            const currentIndex = focusables.indexOf(document.activeElement);
            if (event.shiftKey) {
              event.preventDefault();
              const prev = currentIndex <= 0 ? focusables.length - 1 : currentIndex - 1;
              focusables[prev].focus();
            } else {
              event.preventDefault();
              const next = currentIndex === focusables.length - 1 ? 0 : currentIndex + 1;
              focusables[next].focus();
            }
          }
        });

        actions.appendChild(cancelBtn);
        actions.appendChild(confirmBtn);

        dialog.appendChild(heading);
        dialog.appendChild(copy);
        dialog.appendChild(actions);
        overlay.appendChild(dialog);
        document.body.appendChild(overlay);

        cancelBtn.focus();
      });
    });
  }

  const notify = {
    show: (options) => showToast(options),
    success: (message, options = {}) =>
      showToast({ ...options, message, type: 'success' }),
    info: (message, options = {}) => showToast({ ...options, message, type: 'info' }),
    warning: (message, options = {}) =>
      showToast({ ...options, message, type: 'warning' }),
    error: (message, options = {}) => showToast({ ...options, message, type: 'danger' }),
    confirm: (options) => confirmDialog(options),
  };

  window.notify = notify;

  if (!window.nativeAlert) {
    window.nativeAlert = window.alert.bind(window);
  }

  window.alert = function (message, options = {}) {
    const toastType = options.type || inferType(message);
    const title = options.title;
    notify.show({
      title,
      type: toastType,
      message: String(message ?? ''),
      duration: options.duration || DEFAULT_DURATION,
    });
  };

  window.customConfirm = function (options) {
    return notify.confirm(options);
  };
})();
