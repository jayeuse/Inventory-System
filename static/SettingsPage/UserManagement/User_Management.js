document.addEventListener("DOMContentLoaded", function() {

  let allActiveUsers = [];
  let allInactiveUsers = [];
  let currentPage = 1;
  let inactiveCurrentPage = 1;
  const recordsPerPage = 8;
  let currentEditUserId = null;
  let userToDeactivate = null;
  let userToActivate = null;

  const truncateText = (text, maxLength = 30) => {
    if (!text) return '-';
    return text.length > maxLength ? `${text.slice(0, maxLength)}...` : text;
  };

  // Fetching Users Data
  async function loadUsers() {
    console.log("Loading Users...");
    try {
      const response = await fetch('/api/users/');
      const allUsers = await response.json();
      
      // Separate active and inactive users
      allActiveUsers = allUsers.filter(u => u.user && u.user.is_active);
      allInactiveUsers = allUsers.filter(u => u.user && !u.user.is_active);

      currentPage = 1;
      inactiveCurrentPage = 1;
      displayUsers();
      displayInactiveUsers();
    } catch (error) {
      console.error('Error fetching Users:', error);
    }
  }

  // Display active users
  function displayUsers() {
    const searchTerm = document.getElementById('userSearchInput')?.value.toLowerCase() || '';
    const roleFilter = document.getElementById('roleFilter')?.value || 'all';

    // Filter users
    let filteredUsers = allActiveUsers.filter(userInfo => {
      const user = userInfo.user || {};
      const fullName = userInfo.full_name || `${user.first_name || ''} ${user.last_name || ''}`;
      
      const matchesSearch = 
        fullName.toLowerCase().includes(searchTerm) ||
        (user.username || '').toLowerCase().includes(searchTerm) ||
        (user.email || '').toLowerCase().includes(searchTerm) ||
        (userInfo.user_info_id || '').toLowerCase().includes(searchTerm);
      
      const matchesRole = roleFilter === 'all' || userInfo.role === roleFilter;

      return matchesSearch && matchesRole;
    });

    // Calculate pagination
    const totalPages = Math.ceil(filteredUsers.length / recordsPerPage);
    const startIndex = (currentPage - 1) * recordsPerPage;
    const endIndex = startIndex + recordsPerPage;
    const paginatedUsers = filteredUsers.slice(startIndex, endIndex);

    // Populate table
    const tbody = document.getElementById('users-table-body');
    if (!tbody) return;
    
    tbody.innerHTML = '';

    if (filteredUsers.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 40px; color: var(--muted);">No users found</td></tr>';
    } else {
      for (let i = 0; i < recordsPerPage; i++) {
        const row = document.createElement('tr');
        
        if (i < paginatedUsers.length) {
          const userInfo = paginatedUsers[i];
          const user = userInfo.user || {};
          const fullName = userInfo.full_name || `${user.first_name || ''} ${user.last_name || ''}`.trim() || '-';
          
          row.innerHTML = `
            <td class="truncate-cell truncate-140" title="${userInfo.user_info_id || ''}">${truncateText(userInfo.user_info_id, 15)}</td>
            <td class="truncate-cell truncate-200" title="${fullName}">${truncateText(fullName, 25)}</td>
            <td class="truncate-cell truncate-160" title="${user.username || ''}">${truncateText(user.username, 18)}</td>
            <td class="email-cell" title="${user.email || ''}">${truncateText(user.email, 28)}</td>
            <td><span class="status ${getRoleClass(userInfo.role)}">${userInfo.role || '-'}</span></td>
            <td class="truncate-cell truncate-160" title="${userInfo.created_at_formatted || ''}">${truncateText(userInfo.created_at_formatted, 18)}</td>
            <td class="actions-cell">
              <div class="op-buttons">
                <button class="action-btn edit-btn user-edit-btn" data-user-id="${userInfo.user_info_id}">
                  <i class="bi bi-pencil"></i> Edit
                </button>
                <button class="action-btn archive-btn user-deactivate-btn" data-user-id="${userInfo.user_info_id}" data-user-name="${fullName}">
                  <i class="fas fa-user-slash"></i> Deactivate
                </button>
              </div>
            </td>
          `;
        } else {
          row.classList.add('placeholder-row');
          row.innerHTML = `
            <td class="truncate-cell truncate-140 placeholder-value">-</td>
            <td class="truncate-cell truncate-200 placeholder-value">-</td>
            <td class="truncate-cell truncate-160 placeholder-value">-</td>
            <td class="email-cell placeholder-value">-</td>
            <td class="placeholder-value">-</td>
            <td class="truncate-cell truncate-160 placeholder-value">-</td>
            <td class="actions-cell">
              <div class="op-buttons placeholder-buttons">
                <span>-</span>
              </div>
            </td>
          `;
        }
        
        tbody.appendChild(row);
      }
    }

    updateUserPaginationButtons(currentPage, totalPages, false);
    attachUserActionListeners();
  }

  // Display inactive users
  function displayInactiveUsers() {
    const totalPages = Math.ceil(allInactiveUsers.length / recordsPerPage);
    const startIndex = (inactiveCurrentPage - 1) * recordsPerPage;
    const endIndex = startIndex + recordsPerPage;
    const paginatedUsers = allInactiveUsers.slice(startIndex, endIndex);

    const tbody = document.getElementById('inactiveUsersTableBody');
    if (!tbody) return;
    
    tbody.innerHTML = '';

    if (allInactiveUsers.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 40px; color: var(--muted);">No inactive users</td></tr>';
    } else {
      for (let i = 0; i < recordsPerPage; i++) {
        const row = document.createElement('tr');
        
        if (i < paginatedUsers.length) {
          const userInfo = paginatedUsers[i];
          const user = userInfo.user || {};
          const fullName = userInfo.full_name || `${user.first_name || ''} ${user.last_name || ''}`.trim() || '-';
          
          row.innerHTML = `
            <td class="truncate-cell truncate-140" title="${userInfo.user_info_id || ''}">${truncateText(userInfo.user_info_id, 15)}</td>
            <td class="truncate-cell truncate-200" title="${fullName}">${truncateText(fullName, 25)}</td>
            <td class="truncate-cell truncate-160" title="${user.username || ''}">${truncateText(user.username, 18)}</td>
            <td class="email-cell" title="${user.email || ''}">${truncateText(user.email, 28)}</td>
            <td><span class="status ${getRoleClass(userInfo.role)}">${userInfo.role || '-'}</span></td>
            <td class="truncate-cell truncate-160" title="${userInfo.created_at_formatted || ''}">${truncateText(userInfo.created_at_formatted, 18)}</td>
            <td class="actions-cell">
              <div class="op-buttons">
                <button class="action-btn unarchive-btn user-activate-btn" data-user-id="${userInfo.user_info_id}" data-user-name="${fullName}">
                  <i class="fas fa-user-check"></i> Activate
                </button>
              </div>
            </td>
          `;
        } else {
          row.classList.add('placeholder-row');
          row.innerHTML = `
            <td class="truncate-cell truncate-140 placeholder-value">-</td>
            <td class="truncate-cell truncate-200 placeholder-value">-</td>
            <td class="truncate-cell truncate-160 placeholder-value">-</td>
            <td class="email-cell placeholder-value">-</td>
            <td class="placeholder-value">-</td>
            <td class="truncate-cell truncate-160 placeholder-value">-</td>
            <td class="actions-cell">
              <div class="op-buttons placeholder-buttons">
                <span>-</span>
              </div>
            </td>
          `;
        }
        
        tbody.appendChild(row);
      }
    }

    updateUserPaginationButtons(inactiveCurrentPage, totalPages, true);
    attachUserActionListeners();
  }

  // Helper function to get role-based CSS class
  function getRoleClass(role) {
    switch(role) {
      case 'Admin': return 'admin-role';
      case 'Staff': return 'active';
      case 'Clerk': return 'clerk-role';
      default: return '';
    }
  }

  // Update pagination buttons
  function updateUserPaginationButtons(current, total, isInactive) {
    const prevBtn = document.getElementById(isInactive ? 'inactivePrevBtn' : 'userPrevBtn');
    const nextBtn = document.getElementById(isInactive ? 'inactiveNextBtn' : 'userNextBtn');

    if (prevBtn && nextBtn) {
      prevBtn.disabled = current === 1;
      nextBtn.disabled = current === total || total === 0;

      prevBtn.style.opacity = current === 1 ? '0.5' : '1';
      nextBtn.style.opacity = (current === total || total === 0) ? '0.5' : '1';
    }
  }

  // Attach action listeners for user buttons
  function attachUserActionListeners() {
    // Edit buttons
    document.querySelectorAll('.user-edit-btn').forEach(btn => {
      btn.addEventListener('click', async function() {
        const userId = this.getAttribute('data-user-id');
        await openEditUserModal(userId);
      });
    });

    // Deactivate buttons
    document.querySelectorAll('.user-deactivate-btn').forEach(btn => {
      btn.addEventListener('click', function() {
        userToDeactivate = this.getAttribute('data-user-id');
        const userName = this.getAttribute('data-user-name');
        document.getElementById('deactivateUserName').textContent = userName;
        document.getElementById('deactivateUserModal').style.display = 'flex';
      });
    });

    // Activate buttons
    document.querySelectorAll('.user-activate-btn').forEach(btn => {
      btn.addEventListener('click', function() {
        userToActivate = this.getAttribute('data-user-id');
        const userName = this.getAttribute('data-user-name');
        document.getElementById('activateUserName').textContent = userName;
        document.getElementById('activateUserModal').style.display = 'flex';
      });
    });
  }

  // Open Edit User Modal
  async function openEditUserModal(userId) {
    try {
      const response = await fetch(`/api/users/${userId}/`);
      if (!response.ok) throw new Error('Failed to fetch user');
      
      const userInfo = await response.json();
      const user = userInfo.user || {};
      
      currentEditUserId = userId;
      
      document.getElementById('editUserUsername').value = user.username || '';
      document.getElementById('editUserEmail').value = user.email || '';
      document.getElementById('editUserFirstName').value = user.first_name || '';
      document.getElementById('editUserLastName').value = user.last_name || '';
      document.getElementById('editUserMiddleName').value = userInfo.middle_name || '';
      document.getElementById('editUserPhone').value = userInfo.phone_number || '';
      document.getElementById('editUserAddress').value = userInfo.address || '';
      document.getElementById('editUserRole').value = userInfo.role || 'Staff';
      document.getElementById('editUserPassword').value = '';
      
      document.getElementById('editUserModal').style.display = 'flex';
    } catch (error) {
      console.error('Error loading user:', error);
      alert('Error loading user data');
    }
  }

  // Pagination event listeners
  document.getElementById('userPrevBtn')?.addEventListener('click', function() {
    if (currentPage > 1) {
      currentPage--;
      displayUsers();
    }
  });

  document.getElementById('userNextBtn')?.addEventListener('click', function() {
    const totalPages = Math.ceil(allActiveUsers.length / recordsPerPage);
    if (currentPage < totalPages) {
      currentPage++;
      displayUsers();
    }
  });

  // Search and filter event listeners
  document.getElementById('userSearchInput')?.addEventListener('input', function() {
    currentPage = 1;
    displayUsers();
  });

  document.getElementById('roleFilter')?.addEventListener('change', function() {
    currentPage = 1;
    displayUsers();
  });

  // User toggle functionality
  const userToggle = document.getElementById('userToggle');
  if (userToggle) {
    const toggleOptions = userToggle.querySelectorAll('.toggle-option');
    const activeUsersWrapper = document.getElementById('activeUsersWrapper');
    const inactiveUsersWrapper = document.getElementById('inactiveUsersWrapper');
    const addUserBtn = document.getElementById('addUserBtn');

    toggleOptions.forEach(option => {
      option.addEventListener('click', function() {
        toggleOptions.forEach(opt => opt.classList.remove('active'));
        this.classList.add('active');

        const type = this.getAttribute('data-type');
        if (type === 'active') {
          if (activeUsersWrapper) activeUsersWrapper.style.display = 'block';
          if (inactiveUsersWrapper) inactiveUsersWrapper.style.display = 'none';
          if (addUserBtn) addUserBtn.style.display = 'inline-flex';
        } else {
          if (activeUsersWrapper) activeUsersWrapper.style.display = 'none';
          if (inactiveUsersWrapper) inactiveUsersWrapper.style.display = 'block';
          if (addUserBtn) addUserBtn.style.display = 'none';
        }
      });
    });
  }

  // Add User Modal
  const addUserModal = document.getElementById('addUserModal');
  const addUserBtn = document.getElementById('addUserBtn');
  const closeAddUserBtn = document.getElementById('closeAddUserBtn');
  const cancelAddUserBtn = document.getElementById('cancelAddUserBtn');

  addUserBtn?.addEventListener('click', () => {
    addUserModal.style.display = 'flex';
  });

  closeAddUserBtn?.addEventListener('click', () => {
    addUserModal.style.display = 'none';
    clearAddUserForm();
  });

  cancelAddUserBtn?.addEventListener('click', () => {
    addUserModal.style.display = 'none';
    clearAddUserForm();
  });

  // Edit User Modal
  const editUserModal = document.getElementById('editUserModal');
  const closeEditUserBtn = document.getElementById('closeEditUserBtn');
  const cancelEditUserBtn = document.getElementById('cancelEditUserBtn');

  closeEditUserBtn?.addEventListener('click', () => {
    editUserModal.style.display = 'none';
    currentEditUserId = null;
  });

  cancelEditUserBtn?.addEventListener('click', () => {
    editUserModal.style.display = 'none';
    currentEditUserId = null;
  });

  // Deactivate User Modal
  const deactivateUserModal = document.getElementById('deactivateUserModal');
  const cancelDeactivateUserBtn = document.getElementById('cancelDeactivateUserBtn');
  const confirmDeactivateUserBtn = document.getElementById('confirmDeactivateUserBtn');

  cancelDeactivateUserBtn?.addEventListener('click', () => {
    deactivateUserModal.style.display = 'none';
    userToDeactivate = null;
  });

  confirmDeactivateUserBtn?.addEventListener('click', async () => {
    if (!userToDeactivate) return;

    try {
      const response = await fetch(`/api/users/${userToDeactivate}/deactivate/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken()
        }
      });

      if (response.ok) {
        alert('User deactivated successfully!');
        deactivateUserModal.style.display = 'none';
        userToDeactivate = null;
        await loadUsers();
      } else {
        const errorData = await response.json();
        alert('Error: ' + JSON.stringify(errorData));
      }
    } catch (error) {
      console.error('Error deactivating user:', error);
      alert('Network error: ' + error);
    }
  });

  // Activate User Modal
  const activateUserModal = document.getElementById('activateUserModal');
  const cancelActivateUserBtn = document.getElementById('cancelActivateUserBtn');
  const confirmActivateUserBtn = document.getElementById('confirmActivateUserBtn');

  cancelActivateUserBtn?.addEventListener('click', () => {
    activateUserModal.style.display = 'none';
    userToActivate = null;
  });

  confirmActivateUserBtn?.addEventListener('click', async () => {
    if (!userToActivate) return;

    try {
      const response = await fetch(`/api/users/${userToActivate}/activate/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken()
        }
      });

      if (response.ok) {
        alert('User activated successfully!');
        activateUserModal.style.display = 'none';
        userToActivate = null;
        await loadUsers();
      } else {
        const errorData = await response.json();
        alert('Error: ' + JSON.stringify(errorData));
      }
    } catch (error) {
      console.error('Error activating user:', error);
      alert('Network error: ' + error);
    }
  });

  // Save new user
  document.getElementById('saveUserBtn')?.addEventListener('click', async function() {
    const username = document.getElementById('userUsername').value.trim();
    const email = document.getElementById('userEmail').value.trim();
    const firstName = document.getElementById('userFirstName').value.trim();
    const lastName = document.getElementById('userLastName').value.trim();
    const middleName = document.getElementById('userMiddleName').value.trim();
    const phone = document.getElementById('userPhone').value.trim();
    const address = document.getElementById('userAddress').value.trim();
    const role = document.getElementById('userRole').value;
    const password = document.getElementById('userPassword').value;
    const passwordConfirm = document.getElementById('userPasswordConfirm').value;

    // Validation
    if (!username || !email || !firstName || !lastName || !password) {
      alert('Please fill in all required fields');
      return;
    }

    // Password validation
    if (password !== passwordConfirm) {
      alert('Passwords do not match!');
      return;
    }

    if (password.length < 6) {
      alert('Password must be at least 6 characters!');
      return;
    }

    const data = {
      username: username,
      email: email,
      first_name: firstName,
      last_name: lastName,
      middle_name: middleName || null,
      phone_number: phone || null,
      address: address || null,
      role: role,
      password: password
    };

    try {
      const response = await fetch('/api/users/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify(data)
      });

      if (response.ok) {
        alert('User created successfully!');
        addUserModal.style.display = 'none';
        clearAddUserForm();
        await loadUsers();
      } else {
        const errorData = await response.json();
        alert('Error: ' + JSON.stringify(errorData));
      }
    } catch (error) {
      console.error('Error creating user:', error);
      alert('Network error: ' + error);
    }
  });

  // Update user
  document.getElementById('updateUserBtn')?.addEventListener('click', async function() {
    if (!currentEditUserId) {
      console.log("No user selected for editing");
      return;
    }

    const username = document.getElementById('editUserUsername').value.trim();
    const email = document.getElementById('editUserEmail').value.trim();
    const firstName = document.getElementById('editUserFirstName').value.trim();
    const lastName = document.getElementById('editUserLastName').value.trim();
    const middleName = document.getElementById('editUserMiddleName').value.trim();
    const phone = document.getElementById('editUserPhone').value.trim();
    const address = document.getElementById('editUserAddress').value.trim();
    const role = document.getElementById('editUserRole').value;
    const password = document.getElementById('editUserPassword').value;

    // Validation
    if (!username || !email || !firstName || !lastName) {
      alert('Please fill in all required fields');
      return;
    }

    const data = {
      username: username,
      email: email,
      first_name: firstName,
      last_name: lastName,
      middle_name: middleName || null,
      phone_number: phone || null,
      address: address || null,
      role: role
    };

    // Only include password if it was provided
    if (password) {
      data.password = password;
    }

    try {
      const response = await fetch(`/api/users/${currentEditUserId}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify(data)
      });

      if (response.ok) {
        alert('User updated successfully!');
        editUserModal.style.display = 'none';
        currentEditUserId = null;
        await loadUsers();
      } else {
        const errorData = await response.json();
        alert('Error: ' + JSON.stringify(errorData));
      }
    } catch (error) {
      console.error('Error updating user:', error);
      alert('Network error: ' + error);
    }
  });

  // Clear add user form
  function clearAddUserForm() {
    document.getElementById('userUsername').value = '';
    document.getElementById('userEmail').value = '';
    document.getElementById('userFirstName').value = '';
    document.getElementById('userLastName').value = '';
    document.getElementById('userMiddleName').value = '';
    document.getElementById('userPhone').value = '';
    document.getElementById('userAddress').value = '';
    document.getElementById('userRole').value = 'Staff';
    document.getElementById('userPassword').value = '';
    document.getElementById('userPasswordConfirm').value = '';
  }

  // Close modals when clicking outside
  window.addEventListener('click', function(e) {
    if (e.target === addUserModal) {
      addUserModal.style.display = 'none';
      clearAddUserForm();
    }
    if (e.target === editUserModal) {
      editUserModal.style.display = 'none';
      currentEditUserId = null;
    }
    if (e.target === deactivateUserModal) {
      deactivateUserModal.style.display = 'none';
      userToDeactivate = null;
    }
    if (e.target === activateUserModal) {
      activateUserModal.style.display = 'none';
      userToActivate = null;
    }
  });

  // Load users on page load
  loadUsers();

});
