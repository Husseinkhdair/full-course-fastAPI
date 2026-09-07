/**
 * Aura Platform - SaaS Client Application Logic
 * Integrates directly with FastAPI Authentication & User Management backend
 */

(function () {
  'use strict';

  // API Base URL (defaults to current window origin if served from FastAPI, or 127.0.0.1:8000)
  const API_BASE = (window.location.origin.startsWith('http') && !window.location.origin.includes(':5500'))
    ? window.location.origin
    : 'http://127.0.0.1:8000';

  // Application State
  const STATE = {
    user: JSON.parse(localStorage.getItem('aura_user') || 'null'),
    token: localStorage.getItem('aura_token') || null,
    theme: localStorage.getItem('aura_theme') || 'dark'
  };

  // DOM Elements Cache
  const DOM = {
    // Theme
    btnThemeToggle: document.getElementById('btn-theme-toggle'),

    // Nav
    navVisitorActions: document.getElementById('nav-visitor-actions'),
    navUserProfile: document.getElementById('nav-user-profile'),
    navUserAvatar: document.getElementById('nav-user-avatar'),
    navUserName: document.getElementById('nav-user-name'),
    navItemPortalLink: document.getElementById('nav-item-portal-link'),
    btnNavViewDashboard: document.getElementById('btn-nav-view-dashboard'),
    btnNavDashboard: document.getElementById('btn-nav-dashboard'),
    btnOpenLogin: document.getElementById('btn-open-login'),
    btnOpenRegister: document.getElementById('btn-open-register'),
    btnLogout: document.getElementById('btn-logout'),

    // Views
    publicLandingView: document.getElementById('public-landing-view'),
    memberDashboard: document.getElementById('member-dashboard'),
    btnHeroCtaRegister: document.getElementById('btn-hero-cta-register'),
    planButtons: document.querySelectorAll('.btn-open-reg-plan'),
    btnDashToPublic: document.getElementById('btn-dash-to-public'),

    // Dashboard Items
    dashAvatar: document.getElementById('dash-avatar'),
    dashUserName: document.getElementById('dash-user-name'),
    dashUserEmail: document.getElementById('dash-user-email'),
    dashBadgeRole: document.getElementById('dash-badge-role'),
    dashBadgeStatus: document.getElementById('dash-badge-status'),
    dashMemberSince: document.getElementById('dash-member-since'),
    dashValId: document.getElementById('dash-val-id'),
    dashValName: document.getElementById('dash-val-name'),
    dashValEmail: document.getElementById('dash-val-email'),
    dashValRole: document.getElementById('dash-val-role'),
    dashValCreated: document.getElementById('dash-val-created'),
    dashValUpdated: document.getElementById('dash-val-updated'),
    dashTokenBox: document.getElementById('dash-token-box'),
    btnCopyToken: document.getElementById('btn-copy-token'),
    btnDashRefresh: document.getElementById('btn-dash-refresh'),

    // Member Directory Search
    dashLookupType: document.getElementById('dash-lookup-type'),
    dashLookupInput: document.getElementById('dash-lookup-input'),
    btnDashLookup: document.getElementById('btn-dash-lookup'),
    dashLookupResult: document.getElementById('dash-lookup-result'),
    lookupResAvatar: document.getElementById('lookup-res-avatar'),
    lookupResName: document.getElementById('lookup-res-name'),
    lookupResEmail: document.getElementById('lookup-res-email'),
    lookupResRole: document.getElementById('lookup-res-role'),
    lookupResStatus: document.getElementById('lookup-res-status'),

    // Auth Modal
    authModal: document.getElementById('auth-modal'),
    btnCloseAuthModal: document.getElementById('btn-close-auth-modal'),
    modalTabLogin: document.getElementById('modal-tab-login'),
    modalTabRegister: document.getElementById('modal-tab-register'),
    authFormLogin: document.getElementById('auth-form-login'),
    authFormRegister: document.getElementById('auth-form-register'),
    inputLoginEmail: document.getElementById('input-login-email'),
    inputLoginPassword: document.getElementById('input-login-password'),
    btnToggleLoginEye: document.getElementById('btn-toggle-login-eye'),
    btnSubmitLogin: document.getElementById('btn-submit-login'),
    inputRegName: document.getElementById('input-reg-name'),
    inputRegEmail: document.getElementById('input-reg-email'),
    inputRegPassword: document.getElementById('input-reg-password'),
    btnToggleRegEye: document.getElementById('btn-toggle-reg-eye'),
    btnSubmitRegister: document.getElementById('btn-submit-register'),

    // Delete Modal
    deleteConfirmModal: document.getElementById('delete-confirm-modal'),
    btnOpenDeleteModal: document.getElementById('btn-open-delete-modal'),
    btnCancelDelete: document.getElementById('btn-cancel-delete'),
    btnConfirmDelete: document.getElementById('btn-confirm-delete'),

    // Toasts
    toastContainer: document.getElementById('toast-container')
  };

  // --- Toast Notification Engine ---
  function showToast(title, message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    let iconSvg = '';
    if (type === 'success') {
      iconSvg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:18px;height:18px;"><polyline points="20 6 9 17 4 12"></polyline></svg>';
    } else if (type === 'error') {
      iconSvg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:18px;height:18px;"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>';
    } else {
      iconSvg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:18px;height:18px;"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>';
    }

    toast.innerHTML = `
      <div class="toast-icon">${iconSvg}</div>
      <div class="toast-content">
        <div class="toast-title">${escapeHtml(title)}</div>
        <div class="toast-msg">${escapeHtml(message)}</div>
      </div>
      <button class="toast-close" title="Dismiss">✕</button>
    `;

    toast.querySelector('.toast-close').addEventListener('click', () => toast.remove());
    DOM.toastContainer.appendChild(toast);

    setTimeout(() => {
      if (toast.parentNode) {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
      }
    }, 4000);
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // --- API Client ---
  async function apiCall(path, options = {}) {
    const url = `${API_BASE}${path.startsWith('/') ? path : '/' + path}`;
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...(options.headers || {})
    };

    if (STATE.token && !headers['Authorization']) {
      headers['Authorization'] = `Bearer ${STATE.token}`;
    }

    try {
      const response = await fetch(url, {
        method: options.method || 'GET',
        headers,
        body: options.body ? JSON.stringify(options.body) : undefined
      });

      let data;
      const contentType = response.headers.get('content-type') || '';
      if (contentType.includes('application/json')) {
        data = await response.json();
      } else {
        const text = await response.text();
        try { data = JSON.parse(text); } catch { data = text; }
      }

      return { ok: response.ok, status: response.status, data };
    } catch (error) {
      console.error('API Error:', error);
      return { ok: false, status: 0, data: { detail: 'Unable to connect to backend service.' } };
    }
  }

  // --- UI State Management ---
  function updateUI() {
    if (STATE.user && STATE.token) {
      // Authenticated state
      DOM.navVisitorActions.style.display = 'none';
      DOM.navUserProfile.style.display = 'flex';
      DOM.navItemPortalLink.style.display = 'block';

      const initial = (STATE.user.name || 'U').charAt(0).toUpperCase();
      DOM.navUserAvatar.textContent = initial;
      DOM.navUserName.textContent = STATE.user.name || 'Member';

      // Populate Member Dashboard
      DOM.dashAvatar.textContent = initial;
      DOM.dashUserName.textContent = STATE.user.name || 'Member';
      DOM.dashUserEmail.textContent = STATE.user.email || '';

      const role = (STATE.user.role || 'user').toLowerCase();
      DOM.dashBadgeRole.className = `badge badge-role-${role}`;
      DOM.dashBadgeRole.textContent = role;
      DOM.dashBadgeStatus.textContent = STATE.user.status || 'active';

      if (STATE.user.created_at) {
        DOM.dashMemberSince.textContent = `Member since: ${STATE.user.created_at.split(' ')[0] || STATE.user.created_at}`;
      }

      DOM.dashValId.textContent = STATE.user.user_id || STATE.user.id || '-';
      DOM.dashValName.textContent = STATE.user.name || '-';
      DOM.dashValEmail.textContent = STATE.user.email || '-';
      DOM.dashValRole.textContent = (STATE.user.role || 'USER').toUpperCase();
      DOM.dashValCreated.textContent = STATE.user.created_at || '-';
      DOM.dashValUpdated.textContent = STATE.user.updated_at || '-';

      DOM.dashTokenBox.textContent = STATE.token;
    } else {
      // Logged out / Visitor state
      DOM.navVisitorActions.style.display = 'flex';
      DOM.navUserProfile.style.display = 'none';
      DOM.navItemPortalLink.style.display = 'none';

      showPublicLanding();
    }
  }

  function showDashboard() {
    if (!STATE.user) {
      openAuthModal('login');
      return;
    }
    DOM.publicLandingView.style.display = 'none';
    DOM.memberDashboard.style.display = 'block';
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function showPublicLanding() {
    DOM.publicLandingView.style.display = 'block';
    DOM.memberDashboard.style.display = 'none';
  }

  function setSession(userData, token) {
    STATE.user = userData;
    STATE.token = token || (userData && userData.token) || null;

    localStorage.setItem('aura_user', JSON.stringify(STATE.user));
    if (STATE.token) {
      localStorage.setItem('aura_token', STATE.token);
    }
    updateUI();
    showDashboard();
  }

  function logout() {
    STATE.user = null;
    STATE.token = null;
    localStorage.removeItem('aura_user');
    localStorage.removeItem('aura_token');
    updateUI();
    showPublicLanding();
    showToast('Signed Out', 'You have been safely signed out.', 'info');
  }

  // --- Auth Modal Control ---
  function openAuthModal(mode = 'login') {
    DOM.authModal.classList.add('open');
    if (mode === 'register') {
      DOM.modalTabRegister.click();
    } else {
      DOM.modalTabLogin.click();
    }
  }

  function closeAuthModal() {
    DOM.authModal.classList.remove('open');
    DOM.authFormLogin.reset();
    DOM.authFormRegister.reset();
  }

  // --- Event Handlers Setup ---
  function setupEvents() {
    // Theme Toggle
    DOM.btnThemeToggle.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme') || 'dark';
      const next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      STATE.theme = next;
      localStorage.setItem('aura_theme', next);
    });

    // Modal Switchers
    DOM.modalTabLogin.addEventListener('click', () => {
      DOM.modalTabLogin.classList.add('active');
      DOM.modalTabRegister.classList.remove('active');
      DOM.authFormLogin.style.display = 'block';
      DOM.authFormRegister.style.display = 'none';
    });

    DOM.modalTabRegister.addEventListener('click', () => {
      DOM.modalTabRegister.classList.add('active');
      DOM.modalTabLogin.classList.remove('active');
      DOM.authFormLogin.style.display = 'none';
      DOM.authFormRegister.style.display = 'block';
    });

    // Open/Close Modal
    DOM.btnOpenLogin.addEventListener('click', () => openAuthModal('login'));
    DOM.btnOpenRegister.addEventListener('click', () => openAuthModal('register'));
    DOM.btnHeroCtaRegister.addEventListener('click', () => openAuthModal('register'));
    DOM.planButtons.forEach(btn => btn.addEventListener('click', () => openAuthModal('register')));

    DOM.btnCloseAuthModal.addEventListener('click', closeAuthModal);
    DOM.authModal.addEventListener('click', (e) => {
      if (e.target === DOM.authModal) closeAuthModal();
    });

    // Password Eyes
    DOM.btnToggleLoginEye.addEventListener('click', () => {
      const isPwd = DOM.inputLoginPassword.type === 'password';
      DOM.inputLoginPassword.type = isPwd ? 'text' : 'password';
    });

    DOM.btnToggleRegEye.addEventListener('click', () => {
      const isPwd = DOM.inputRegPassword.type === 'password';
      DOM.inputRegPassword.type = isPwd ? 'text' : 'password';
    });

    // Nav Switchers
    DOM.btnNavDashboard.addEventListener('click', showDashboard);
    DOM.btnNavViewDashboard.addEventListener('click', (e) => {
      e.preventDefault();
      showDashboard();
    });
    DOM.btnDashToPublic.addEventListener('click', showPublicLanding);
    DOM.btnLogout.addEventListener('click', logout);

    // ==========================================
    // AUTH ACTIONS (Calling real API endpoints)
    // ==========================================

    // Sign In: POST /auth/login
    DOM.authFormLogin.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = DOM.inputLoginEmail.value.trim();
      const password = DOM.inputLoginPassword.value;

      if (!email || !password) {
        showToast('Required', 'Please enter email and password.', 'error');
        return;
      }

      DOM.btnSubmitLogin.disabled = true;
      DOM.btnSubmitLogin.textContent = 'Authenticating...';

      const res = await apiCall('/auth/login', {
        method: 'POST',
        body: { email, password }
      });

      DOM.btnSubmitLogin.disabled = false;
      DOM.btnSubmitLogin.textContent = 'Sign In to Aura';

      if (res.ok && res.data) {
        setSession(res.data, res.data.token);
        closeAuthModal();
        showToast('Welcome Back', `Successfully signed in as ${res.data.name}!`, 'success');
      } else {
        const msg = (res.data && res.data.detail) || 'Invalid email or password.';
        showToast('Authentication Error', msg, 'error');
      }
    });

    // Register: POST /auth/register
    DOM.authFormRegister.addEventListener('submit', async (e) => {
      e.preventDefault();
      const name = DOM.inputRegName.value.trim();
      const email = DOM.inputRegEmail.value.trim();
      const password = DOM.inputRegPassword.value;

      if (!name || !email || !password) {
        showToast('Required', 'All fields are required.', 'error');
        return;
      }

      DOM.btnSubmitRegister.disabled = true;
      DOM.btnSubmitRegister.textContent = 'Creating Account...';

      const res = await apiCall('/auth/register', {
        method: 'POST',
        body: { name, email, password }
      });

      DOM.btnSubmitRegister.disabled = false;
      DOM.btnSubmitRegister.textContent = 'Register & Launch Dashboard';

      if (res.ok && res.data) {
        setSession(res.data, res.data.token);
        closeAuthModal();
        showToast('Account Created', `Welcome to Aura, ${res.data.name}!`, 'success');
      } else {
        const msg = (res.data && res.data.detail) || 'Registration failed. Email might already exist.';
        showToast('Registration Error', msg, 'error');
      }
    });

    // Sync / Refresh User Profile: GET /auth/user/id/{user_id}
    DOM.btnDashRefresh.addEventListener('click', async () => {
      if (!STATE.user) return;
      const userId = STATE.user.user_id || STATE.user.id;
      DOM.btnDashRefresh.disabled = true;

      const res = await apiCall(`/auth/user/id/${userId}`);
      DOM.btnDashRefresh.disabled = false;

      if (res.ok && res.data) {
        setSession({ ...res.data, token: STATE.token }, STATE.token);
        showToast('Profile Synced', 'Latest account details loaded from database.', 'success');
      } else {
        showToast('Sync Failed', 'Could not refresh profile details.', 'error');
      }
    });

    // Copy Bearer Token
    DOM.btnCopyToken.addEventListener('click', () => {
      if (!STATE.token) return;
      navigator.clipboard.writeText(STATE.token).then(() => {
        showToast('Token Copied', 'Bearer JWT copied to clipboard.', 'info');
      });
    });

    // Member Directory Search: GET /auth/user/email/{email} or /auth/user/id/{id}
    DOM.btnDashLookup.addEventListener('click', async () => {
      const type = DOM.dashLookupType.value;
      const query = DOM.dashLookupInput.value.trim();

      if (!query) {
        showToast('Query Required', 'Please enter an Email or User ID to search.', 'error');
        return;
      }

      DOM.btnDashLookup.disabled = true;
      DOM.btnDashLookup.textContent = 'Searching...';

      const path = type === 'email'
        ? `/auth/user/email/${encodeURIComponent(query)}`
        : `/auth/user/id/${encodeURIComponent(query)}`;

      const res = await apiCall(path);
      DOM.btnDashLookup.disabled = false;
      DOM.btnDashLookup.textContent = 'Find';

      if (res.ok && res.data) {
        DOM.dashLookupResult.style.display = 'block';
        DOM.lookupResAvatar.textContent = (res.data.name || '?').charAt(0).toUpperCase();
        DOM.lookupResName.textContent = res.data.name || 'Unknown';
        DOM.lookupResEmail.textContent = res.data.email || '';
        DOM.lookupResRole.textContent = (res.data.role || 'user').toLowerCase();
        DOM.lookupResStatus.textContent = res.data.status || 'active';
        showToast('Member Found', `Found user record for ${res.data.name}`, 'success');
      } else {
        DOM.dashLookupResult.style.display = 'none';
        showToast('Not Found', 'No user matches this query in the database.', 'error');
      }
    });

    // Delete Account: DELETE /auth/user/id/{user_id}
    DOM.btnOpenDeleteModal.addEventListener('click', () => {
      DOM.deleteConfirmModal.classList.add('open');
    });

    DOM.btnCancelDelete.addEventListener('click', () => {
      DOM.deleteConfirmModal.classList.remove('open');
    });

    DOM.btnConfirmDelete.addEventListener('click', async () => {
      DOM.deleteConfirmModal.classList.remove('open');
      if (!STATE.user) return;
      const userId = STATE.user.user_id || STATE.user.id;

      const res = await apiCall(`/auth/user/id/${userId}`, { method: 'DELETE' });

      if (res.ok && (res.data === true || res.data.detail === undefined)) {
        showToast('Account Deleted', 'Your account has been deleted permanently.', 'info');
        logout();
      } else {
        const msg = (res.data && res.data.detail) || 'Failed to delete account.';
        showToast('Error', msg, 'error');
      }
    });
  }

  // Application Startup
  function init() {
    document.documentElement.setAttribute('data-theme', STATE.theme);
    setupEvents();
    updateUI();

    // If user has an active session on load, launch directly into their Dashboard
    if (STATE.user && STATE.token) {
      showDashboard();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
