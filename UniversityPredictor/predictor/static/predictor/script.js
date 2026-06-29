'use strict';

// ── DOM references ─────────────────────────────────────────────────── //
const rankInput          = document.getElementById('rank-input');
const categorySelect     = document.getElementById('category-select');
const boardSelect        = document.getElementById('board-select');
const minResultsSelect   = document.getElementById('min-results-select');
const roundSelect        = document.getElementById('round-select');
const courseCheckboxes   = document.getElementById('course-checkboxes');
const predictBtn         = document.getElementById('predict-btn');
const resetBtn           = document.getElementById('reset-btn');
const formError          = document.getElementById('form-error');
const loadingOverlay     = document.getElementById('loading-overlay');
const loadingCount       = document.getElementById('loading-count');
const resultsSection     = document.getElementById('results-section');
const resultsContainer   = document.getElementById('results-container');
const resultsSummaryText = document.getElementById('results-summary-text');
const navAuthArea        = document.getElementById('nav-auth-area');
const hamburgerToggle    = document.getElementById('hamburger-toggle');

// Auth modal elements
const authModal          = document.getElementById('auth-modal');
const authModalClose     = document.getElementById('auth-modal-close');
const authTabs           = document.querySelectorAll('.auth-tab');
const loginPanel         = document.getElementById('tab-login');
const registerPanel      = document.getElementById('tab-register');
const loginEmail         = document.getElementById('login-email');
const loginPassword      = document.getElementById('login-password');
const loginError         = document.getElementById('login-error');
const loginSubmit        = document.getElementById('login-submit');
const regEmail           = document.getElementById('reg-email');
const regPassword        = document.getElementById('reg-password');
const regConfirm         = document.getElementById('reg-confirm');
const registerError      = document.getElementById('register-error');
const registerSubmit     = document.getElementById('register-submit');

// ── Access tier state ──────────────────────────────────────────────── //
let userAccessFlags = null;
let isStaffUser = false;
let availableInstTypes = [];
let availableDistricts = [];

// CSRF token (read from cookie, set by Django)
function getCsrfToken() {
  const match = document.cookie.match(/csrftoken=([^;]+)/);
  return match ? match[1] : '';
}

// ── Boot ────────────────────────────────────────────────────────────── //
document.addEventListener('DOMContentLoaded', async () => {
  loadOptions();
  await checkAuthStatus();
  handleOAuthRedirect();
  predictBtn.addEventListener('click', handlePredict);
  resetBtn.addEventListener('click', handleReset);
  authModalClose.addEventListener('click', closeAuthModal);
  authModal.addEventListener('click', e => {
    if (e.target === authModal) closeAuthModal();
  });
  authTabs.forEach(tab => tab.addEventListener('click', () => switchTab(tab.dataset.tab)));
  document.querySelectorAll('[data-switch]').forEach(link => {
    link.addEventListener('click', e => {
      e.preventDefault();
      switchTab(link.dataset.switch);
    });
  });
  loginSubmit.addEventListener('click', handleLogin);
  registerSubmit.addEventListener('click', handleRegister);
  [loginEmail, loginPassword, regEmail, regPassword, regConfirm].forEach(el => {
    el.addEventListener('keydown', e => { if (e.key === 'Enter') el.closest('.auth-form-panel').querySelector('button').click(); });
  });

  // Listen for round/board selection changes to show inline warnings
  roundSelect.addEventListener('change', checkLockedSelection);
  boardSelect.addEventListener('change', checkLockedSelection);

  // Hamburger menu toggle
  if (hamburgerToggle) {
    hamburgerToggle.addEventListener('click', toggleMobileMenu);
  }

  // Close mobile menu on resize past 768px
  window.addEventListener('resize', () => {
    if (window.innerWidth > 768) {
      closeMobileMenu();
    }
  });
});

// ── Mobile menu toggle ───────────────────────────────────────────────── //
let _outsideClickHandler = null;

function toggleMobileMenu() {
  const authNav = document.querySelector('.auth-nav');
  if (!authNav) return;

  const isOpen = authNav.classList.contains('nav-menu-open');
  if (isOpen) {
    closeMobileMenu();
  } else {
    openMobileMenu();
  }
}

function openMobileMenu() {
  const authNav = document.querySelector('.auth-nav');
  if (!authNav) return;

  authNav.classList.add('nav-menu-open');
  hamburgerToggle.setAttribute('aria-expanded', 'true');

  // Close when clicking outside .auth-nav
  _outsideClickHandler = (e) => {
    if (!authNav.contains(e.target)) {
      closeMobileMenu();
    }
  };
  document.addEventListener('click', _outsideClickHandler);

  // Close when a link/button inside the menu is clicked
  const navArea = document.getElementById('nav-auth-area');
  if (navArea) {
    navArea.querySelectorAll('a, button').forEach(el => {
      el.addEventListener('click', closeMobileMenu, { once: true });
    });
  }
}

function closeMobileMenu() {
  const authNav = document.querySelector('.auth-nav');
  if (!authNav) return;

  authNav.classList.remove('nav-menu-open');
  if (hamburgerToggle) {
    hamburgerToggle.setAttribute('aria-expanded', 'false');
  }

  if (_outsideClickHandler) {
    document.removeEventListener('click', _outsideClickHandler);
    _outsideClickHandler = null;
  }
}

// ── Auth status ──────────────────────────────────────────────────────── //
async function checkAuthStatus() {
  try {
    const res  = await fetch('/api/auth/status/');
    const json = await res.json();
    renderNavAuth(json);
    if (json.authenticated) {
      isStaffUser = json.is_staff || false;
      await fetchAccessFlags();
      renderInstTypeFilter();
      renderDistrictFilter();
    } else {
      isStaffUser = false;
      userAccessFlags = null;
      updateLockIndicators();
      updatePredictionCounter();
      renderInstTypeFilter();
      renderDistrictFilter();
    }
  } catch (_) {
    renderNavAuth({ authenticated: false });
  }
}

// ── Access flags ─────────────────────────────────────────────────────── //
async function fetchAccessFlags() {
  try {
    const res = await fetch('/api/auth/access/');
    if (res.ok) {
      userAccessFlags = await res.json();
    } else {
      userAccessFlags = null;
    }
  } catch (_) {
    userAccessFlags = null;
  }
  updateLockIndicators();
  updatePredictionCounter();
}

function updateLockIndicators() {
  // Round dropdown
  const round2Opt = roundSelect.querySelector('option[value="2"]');
  const round3Opt = roundSelect.querySelector('option[value="3"]');

  if (round2Opt) {
    round2Opt.textContent = userAccessFlags && !userAccessFlags.can_access_round2
      ? 'Round 2 🔒 Premium' : 'Round 2';
  }
  if (round3Opt) {
    round3Opt.textContent = userAccessFlags && !userAccessFlags.can_access_round3
      ? 'Round 3 🔒 Premium' : 'Round 3';
  }

  // Board dropdown — find JEE option
  const boardOptions = boardSelect.querySelectorAll('option');
  boardOptions.forEach(opt => {
    if (opt.value.toUpperCase() === 'JEE') {
      opt.textContent = userAccessFlags && !userAccessFlags.can_access_jee
        ? 'JEE 🔒 Premium' : 'JEE';
    }
  });
}

function updatePredictionCounter() {
  let counter = document.getElementById('prediction-counter');
  if (!counter) {
    counter = document.createElement('div');
    counter.id = 'prediction-counter';
    counter.className = 'prediction-counter';
    // Insert after the buttons row
    const btnRow = predictBtn.closest('.d-flex');
    if (btnRow) btnRow.parentNode.insertBefore(counter, btnRow.nextSibling);
  }

  if (userAccessFlags) {
    const remaining = Math.max(0,
      userAccessFlags.daily_prediction_limit - userAccessFlags.predictions_used_today
    );
    counter.innerHTML =
      `<i class="fas fa-chart-bar me-1"></i> ` +
      `${remaining}/${userAccessFlags.daily_prediction_limit} predictions remaining today`;
    counter.style.display = 'block';
  } else {
    counter.style.display = 'none';
  }
}

function checkLockedSelection() {
  clearAccessNotification();
  if (!userAccessFlags) return;

  const roundVal = parseInt(roundSelect.value, 10);
  const boardVal = boardSelect.value;

  if (roundVal === 2 && !userAccessFlags.can_access_round2) {
    showAccessNotification('Round 2 predictions are not available for free users.');
    return;
  }
  if (roundVal === 3 && !userAccessFlags.can_access_round3) {
    showAccessNotification('Round 3 predictions are not available for free users.');
    return;
  }
  if (boardVal && boardVal.toUpperCase() === 'JEE' && !userAccessFlags.can_access_jee) {
    showAccessNotification('JEE board predictions are not available for free users.');
  }
}

// ── Access notifications ─────────────────────────────────────────────── //
function showAccessNotification(message) {
  clearAccessNotification();
  const el = document.createElement('div');
  el.id = 'access-notification';
  el.className = 'access-notification';
  el.innerHTML = `<i class="fas fa-lock me-2"></i>${escapeHtml(message)}`;
  // Insert after form-error
  formError.parentNode.insertBefore(el, formError.nextSibling);
}

function clearAccessNotification() {
  const existing = document.getElementById('access-notification');
  if (existing) existing.remove();
}

// ── OAuth redirect handler ───────────────────────────────────────────── //
function handleOAuthRedirect() {
  const params = new URLSearchParams(window.location.search);

  if (params.get('google_auth') === 'success') {
    window.history.replaceState({}, '', '/');
    checkAuthStatus();
    return;
  }

  if (params.has('google_auth_error')) {
    const errorMsg = params.get('google_auth_error') || 'Google sign-in failed. Please try again.';
    window.history.replaceState({}, '', '/');
    openAuthModal('login');
    showGoogleAuthError(errorMsg);
  }
}

function showGoogleAuthError(message) {
  loginError.textContent = message;
  loginError.style.display = 'block';
}

function renderNavAuth(status) {
  if (status.authenticated) {
    navAuthArea.innerHTML = `
      <span class="nav-user-email"><i class="fas fa-user-circle me-1"></i>${escapeHtml(status.email)}</span>
      <button class="btn-nav-logout" id="logout-btn"><i class="fas fa-sign-out-alt me-1"></i>Logout</button>
    `;
    document.getElementById('logout-btn').addEventListener('click', handleLogout);
  } else {
    navAuthArea.innerHTML = `
      <button class="btn-nav-login" id="nav-login-btn"><i class="fas fa-sign-in-alt me-1"></i>Sign In / Register</button>
    `;
    document.getElementById('nav-login-btn').addEventListener('click', openAuthModal);
  }
}

// ── Auth modal ───────────────────────────────────────────────────────── //
function openAuthModal(defaultTab = 'login') {
  switchTab(defaultTab);
  authModal.style.display = 'flex';
  document.body.style.overflow = 'hidden';
  setTimeout(() => loginEmail.focus(), 100);
}

function closeAuthModal() {
  authModal.style.display = 'none';
  document.body.style.overflow = '';
  clearAuthErrors();
}

function switchTab(tab) {
  authTabs.forEach(t => t.classList.toggle('active', t.dataset.tab === tab));
  loginPanel.style.display    = tab === 'login'    ? 'block' : 'none';
  registerPanel.style.display = tab === 'register' ? 'block' : 'none';
  clearAuthErrors();
}

function clearAuthErrors() {
  loginError.style.display = registerError.style.display = 'none';
  loginError.textContent = registerError.textContent = '';
}

// ── Login ────────────────────────────────────────────────────────────── //
async function handleLogin() {
  loginError.style.display = 'none';
  loginSubmit.disabled = true;
  loginSubmit.textContent = 'Signing in…';

  try {
    const res  = await fetch('/api/auth/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({
        email: loginEmail.value.trim(),
        password: loginPassword.value,
      }),
    });
    const json = await res.json();

    if (!json.success) {
      loginError.textContent = json.error;
      loginError.style.display = 'block';
      return;
    }

    closeAuthModal();
    renderNavAuth({ authenticated: true, email: json.email });
    loginEmail.value = loginPassword.value = '';
    await fetchAccessFlags();
  } catch (_) {
    loginError.textContent = 'Network error. Please try again.';
    loginError.style.display = 'block';
  } finally {
    loginSubmit.disabled = false;
    loginSubmit.innerHTML = '<i class="fas fa-sign-in-alt me-2"></i>Sign In';
  }
}

// ── Register ─────────────────────────────────────────────────────────── //
async function handleRegister() {
  registerError.style.display = 'none';
  registerSubmit.disabled = true;
  registerSubmit.textContent = 'Creating account…';

  try {
    const res  = await fetch('/api/auth/register/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({
        email: regEmail.value.trim(),
        password: regPassword.value,
        confirm_password: regConfirm.value,
      }),
    });
    const json = await res.json();

    if (!json.success) {
      registerError.textContent = json.error;
      registerError.style.display = 'block';
      return;
    }

    closeAuthModal();
    renderNavAuth({ authenticated: true, email: json.email });
    regEmail.value = regPassword.value = regConfirm.value = '';
    await fetchAccessFlags();
  } catch (_) {
    registerError.textContent = 'Network error. Please try again.';
    registerError.style.display = 'block';
  } finally {
    registerSubmit.disabled = false;
    registerSubmit.innerHTML = '<i class="fas fa-user-plus me-2"></i>Create Account';
  }
}

// ── Logout ───────────────────────────────────────────────────────────── //
async function handleLogout() {
  await fetch('/api/auth/logout/', {
    method: 'POST',
    headers: { 'X-CSRFToken': getCsrfToken() },
  });
  userAccessFlags = null;
  renderNavAuth({ authenticated: false });
  updateLockIndicators();
  updatePredictionCounter();
  clearAccessNotification();
  resultsSection.style.display = 'none';
  resultsContainer.innerHTML = '';
}

// ── 1. Load dropdown options ─────────────────────────────────────────── //
async function loadOptions() {
  try {
    const res  = await fetch('/api/options/');
    const json = await res.json();

    if (!json.success) {
      setSelectPlaceholder(categorySelect, 'GEN, SC, ST…');
      setSelectPlaceholder(boardSelect, 'GUJCET, JEE…');
      return;
    }

    populateSelect(categorySelect, json.data.categories, 'All Categories (no filter)');
    populateSelect(boardSelect, json.data.boards, 'All Boards (no filter)');
    buildCourseChips(json.data.course_keywords);
    availableInstTypes = json.data.inst_types || [];
    availableDistricts = json.data.districts || [];
    renderInstTypeFilter();
    renderDistrictFilter();
  } catch (err) {
    console.error('Failed to load options:', err);
  }
}

function populateSelect(selectEl, items, blankLabel) {
  selectEl.innerHTML = `<option value="">${blankLabel}</option>`;
  items.forEach(item => {
    const opt = document.createElement('option');
    opt.value = item;
    opt.textContent = item;
    selectEl.appendChild(opt);
  });
}

function setSelectPlaceholder(selectEl, text) {
  selectEl.innerHTML = `<option value="">${text}</option>`;
}

function buildCourseChips(keywords) {
  courseCheckboxes.innerHTML = '';
  keywords.forEach(kw => {
    const id    = `chip-${kw.toLowerCase().replace(/\s+/g, '-')}`;
    const input = document.createElement('input');
    input.type = 'checkbox';
    input.className = 'course-chip visually-hidden';
    input.value = kw.toLowerCase();
    input.id = id;

    const label = document.createElement('label');
    label.htmlFor = id;
    label.className = 'course-chip-label';
    label.textContent = kw;

    courseCheckboxes.appendChild(input);
    courseCheckboxes.appendChild(label);
  });

  // Check for overflow and toggle scroll indicator class
  if (courseCheckboxes.scrollHeight > courseCheckboxes.clientHeight) {
    courseCheckboxes.classList.add('has-overflow');
  } else {
    courseCheckboxes.classList.remove('has-overflow');
  }
}

// ── 2. Form submission ───────────────────────────────────────────────── //
async function handlePredict() {
  clearError();
  clearAccessNotification();

  // Check auth first
  const statusRes  = await fetch('/api/auth/status/');
  const statusJson = await statusRes.json();
  if (!statusJson.authenticated) {
    openAuthModal('login');
    return;
  }

  const rank = parseInt(rankInput.value, 10);
  if (!rank || rank <= 0) {
    showError('Please enter a valid rank (a positive whole number).');
    rankInput.focus();
    return;
  }

  const category   = categorySelect.value   || null;
  const board      = boardSelect.value      || null;
  const roundNum   = parseInt(roundSelect.value, 10);
  const minResults = parseInt(minResultsSelect.value, 10) || 15;
  const checked    = courseCheckboxes.querySelectorAll('input.course-chip:checked');
  const coursePrefs = checked.length > 0
    ? Array.from(checked).map(cb => cb.value)
    : null;

  showLoading();
  predictBtn.disabled = true;

  try {
    const res  = await fetch('/api/predict/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({
        rank, category, board,
        course_preferences: coursePrefs,
        min_results: minResults,
        round: roundNum,
        inst_types: getSelectedInstTypes(),
        districts: getSelectedDistricts(),
      }),
    });

    const json = await res.json();

    // Task 8.1: Handle 403 access-tier denials
    if (res.status === 403) {
      const errMsg = json.error || '';
      if (errMsg.includes('not available for free users')) {
        showAccessNotification(errMsg);
        return;
      }
      // Session expired / not authenticated
      renderNavAuth({ authenticated: false });
      openAuthModal('login');
      loginError.textContent = 'Please sign in to see your college predictions.';
      loginError.style.display = 'block';
      return;
    }

    // Task 8.1: Handle 429 rate limit
    if (res.status === 429) {
      const errMsg = json.error || 'Daily prediction limit reached. Please try again tomorrow.';
      showAccessNotification(errMsg);
      return;
    }

    if (!json.success) {
      const errMsg = typeof json.error === 'object'
        ? Object.values(json.error).flat().join(' ')
        : (json.error || 'Something went wrong. Please try again.');
      showError(errMsg);
      return;
    }

    if (!json.results || json.results.length === 0) {
      showError('No colleges found. Try widening your search.');
      return;
    }

    renderResults(json.results, rank, category, board);
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

    // Show export button for admin users
    showExportButton(rank, category, board, coursePrefs, minResults, roundNum);

    // Update prediction counter after successful prediction
    await fetchAccessFlags();

  } catch (err) {
    console.error('Prediction fetch error:', err);
    showError('Network error. Please try again.');
  } finally {
    hideLoading();
    predictBtn.disabled = false;
  }
}

// ── 3. Render results ────────────────────────────────────────────────── //
function renderResults(results, rank, category, board) {
  const safe     = results.filter(r => r.chance === 'Safe').length;
  const possible = results.filter(r => r.chance === 'Possible').length;
  const stretch  = results.filter(r => r.chance === 'Stretch').length;

  const filters = [
    rank     ? `Rank ${rank.toLocaleString('en-IN')}` : null,
    category ? `Category: ${category}` : null,
    board    ? `Board: ${board}` : null,
  ].filter(Boolean).join(' · ');

  resultsSummaryText.innerHTML =
    `${results.length} colleges found${filters ? ` for <strong>${filters}</strong>` : ''} — ` +
    `<span style="color:var(--safe)">${safe} Safe</span>, ` +
    `<span style="color:var(--possible)">${possible} Possible</span>, ` +
    `<span style="color:var(--stretch)">${stretch} Stretch</span>`;

  const grouped = {};
  results.forEach(r => {
    const key = r.preferred_course || 'General';
    if (!grouped[key]) grouped[key] = [];
    grouped[key].push(r);
  });

  resultsContainer.innerHTML = '';

  Object.entries(grouped).forEach(([courseName, colleges]) => {
    const group = document.createElement('div');
    group.className = 'course-group';

    const title = document.createElement('h3');
    title.className = 'course-group-title';
    title.innerHTML = `<i class="fas fa-layer-group me-2"></i>${courseName} <small style="font-size:0.7rem;color:var(--text-muted);font-weight:400;">(${colleges.length})</small>`;
    group.appendChild(title);

    colleges.forEach((college, i) => group.appendChild(buildCard(college, i)));
    resultsContainer.appendChild(group);
  });

  const cards = resultsContainer.querySelectorAll('.result-card');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const card = entry.target;
        setTimeout(() => {
          card.classList.add('card-visible');
          const fill = card.querySelector('.score-bar-fill');
          if (fill) fill.style.width = fill.dataset.width;
        }, parseFloat(card.dataset.delay || 0));
        observer.unobserve(card);
      }
    });
  }, { threshold: 0.1 });

  cards.forEach(card => observer.observe(card));
}

function buildCard(college, index) {
  const card = document.createElement('div');
  const chanceClass = college.chance.toLowerCase();
  card.className = `result-card ${chanceClass}-card`;
  card.dataset.delay = Math.min(index * 60, 600);

  const scoreWidth  = Math.min(Math.max(college.university_score * 10, 0), 100).toFixed(1);
  const openingDisp = college.opening_rank != null ? college.opening_rank.toLocaleString('en-IN') : 'N/A';
  const closingDisp = college.closing_rank.toLocaleString('en-IN');

  card.innerHTML = `
    <div class="card-top">
      <h4 class="inst-name">${escapeHtml(college.inst_name)}</h4>
      <span class="chance-badge badge-${chanceClass}">${college.chance}</span>
    </div>
    <div class="course-name-row">
      <i class="fas fa-book-open me-1"></i>${escapeHtml(college.course_name)}
    </div>
    <div class="rank-info">
      <span><i class="fas fa-arrow-up me-1"></i>Opening: <strong>${openingDisp}</strong></span>
      <span><i class="fas fa-arrow-down me-1"></i>Closing: <strong>${closingDisp}</strong></span>
      <span><i class="fas fa-tag me-1"></i>Category: <strong>${escapeHtml(college.category)}</strong></span>
      ${college.board ? `<span><i class="fas fa-th me-1"></i>Board: <strong>${escapeHtml(college.board)}</strong></span>` : ''}
      ${college.round ? `<span><i class="fas fa-circle-notch me-1"></i>Round: <strong>${college.round}</strong></span>` : ''}
      ${college.inst_type ? `<span><i class="fas fa-building me-1"></i>Type: <strong>${escapeInstType(college.inst_type)}</strong></span>` : ''}
    </div>
    <div class="score-row">
      <span class="score-label">Score</span>
      <div class="score-bar-track">
        <div class="score-bar-fill" data-width="${scoreWidth}%" style="width:0%"></div>
      </div>
      <span class="score-value">${college.university_score}</span>
    </div>
  `;
  return card;
}

// ── 4. Reset ─────────────────────────────────────────────────────────── //
function handleReset() {
  rankInput.value = '';
  categorySelect.value = '';
  boardSelect.value = '';
  roundSelect.value = '1';
  minResultsSelect.value = '15';
  courseCheckboxes.querySelectorAll('input.course-chip:checked')
    .forEach(cb => { cb.checked = false; });
  clearError();
  clearAccessNotification();
  resultsSection.style.display = 'none';
  resultsContainer.innerHTML = '';
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ── Helpers ──────────────────────────────────────────────────────────── //
function showLoading() {
  loadingOverlay.style.display = 'flex';
  let count = 0;
  const timer = setInterval(() => {
    count += Math.floor(Math.random() * 150) + 50;
    loadingCount.textContent = count.toLocaleString('en-IN');
  }, 300);
  loadingOverlay._timer = timer;
}

function hideLoading() {
  clearInterval(loadingOverlay._timer);
  loadingOverlay.style.display = 'none';
}

function showError(message) {
  formError.textContent = message;
  formError.style.display = 'block';
  formError.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function clearError() {
  formError.textContent = '';
  formError.style.display = 'none';
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function escapeInstType(type) {
  const labels = { govt_gia: 'Govt/GIA', self_finance: 'Self-Finance' };
  return labels[type] || escapeHtml(type);
}


// ── Institute Type Filter (staff only) ────────────────────────────────── //
const INST_TYPE_LABELS = {
  govt_gia: 'Government / GIA',
  self_finance: 'Self-Finance',
};

function renderInstTypeFilter() {
  const existing = document.getElementById('inst-type-filter');
  if (existing) existing.remove();

  // Only show for staff users who have inst_types available
  if (!isStaffUser || availableInstTypes.length === 0) return;

  const container = document.createElement('div');
  container.id = 'inst-type-filter';
  container.className = 'mb-4 inst-type-filter';
  container.innerHTML = `
    <label class="form-label">
      <i class="fas fa-building text-accent me-2"></i>
      Institute Type
      <span class="optional-tag">staff only — all if none selected</span>
    </label>
    <div id="inst-type-checkboxes" class="inst-type-checkboxes"></div>
  `;

  // Insert before the course preferences section
  const courseSection = courseCheckboxes.closest('.mb-4');
  if (courseSection) {
    courseSection.parentNode.insertBefore(container, courseSection);
  }

  const checkboxContainer = container.querySelector('#inst-type-checkboxes');
  availableInstTypes.forEach(type => {
    const id = `inst-type-${type}`;
    const label = INST_TYPE_LABELS[type] || type;

    const input = document.createElement('input');
    input.type = 'checkbox';
    input.className = 'inst-type-chip';
    input.value = type;
    input.id = id;

    const lbl = document.createElement('label');
    lbl.htmlFor = id;
    lbl.className = 'course-chip-label';
    lbl.textContent = label;

    checkboxContainer.appendChild(input);
    checkboxContainer.appendChild(lbl);
  });
}

function getSelectedInstTypes() {
  const container = document.getElementById('inst-type-checkboxes');
  if (!container) return null;
  const checked = container.querySelectorAll('input.inst-type-chip:checked');
  if (checked.length === 0) return null;
  return Array.from(checked).map(cb => cb.value);
}

function renderDistrictFilter() {
  const existing = document.getElementById('district-filter');
  if (existing) existing.remove();

  if (!isStaffUser || availableDistricts.length === 0) return;

  const container = document.createElement('div');
  container.id = 'district-filter';
  container.className = 'mb-4 inst-type-filter';
  container.innerHTML = `
    <label class="form-label">
      <i class="fas fa-map-marker-alt text-accent me-2"></i>
      District / City
      <span class="optional-tag">staff only — all if none selected</span>
    </label>
    <div id="district-checkboxes" class="inst-type-checkboxes district-checkboxes"></div>
  `;

  // Insert after inst-type-filter or before course preferences
  const instFilter = document.getElementById('inst-type-filter');
  const courseSection = courseCheckboxes.closest('.mb-4');
  if (instFilter) {
    instFilter.parentNode.insertBefore(container, instFilter.nextSibling);
  } else if (courseSection) {
    courseSection.parentNode.insertBefore(container, courseSection);
  }

  const checkboxContainer = container.querySelector('#district-checkboxes');
  availableDistricts.forEach(district => {
    const id = `district-${district.toLowerCase().replace(/\s+/g, '-')}`;

    const input = document.createElement('input');
    input.type = 'checkbox';
    input.className = 'district-chip';
    input.value = district;
    input.id = id;

    const lbl = document.createElement('label');
    lbl.htmlFor = id;
    lbl.className = 'course-chip-label';
    lbl.textContent = district;

    checkboxContainer.appendChild(input);
    checkboxContainer.appendChild(lbl);
  });
}

function getSelectedDistricts() {
  const container = document.getElementById('district-checkboxes');
  if (!container) return null;
  const checked = container.querySelectorAll('input.district-chip:checked');
  if (checked.length === 0) return null;
  return Array.from(checked).map(cb => cb.value);
}

// ── Export to Excel (admin only) ─────────────────────────────────────── //
function showExportButton(rank, category, board, coursePrefs, minResults, roundNum) {
  // Remove existing export button if any
  const existing = document.getElementById('export-btn');
  if (existing) existing.remove();

  // Only show for staff/admin users
  if (!isStaffUser) return;

  const btn = document.createElement('button');
  btn.id = 'export-btn';
  btn.className = 'btn-export';
  btn.innerHTML = '<i class="fas fa-file-excel me-2"></i>Export to Excel';
  btn.addEventListener('click', () => handleExport(rank, category, board, coursePrefs, minResults, roundNum));

  // Insert in the results summary bar
  const summaryBar = document.querySelector('.results-summary-bar');
  if (summaryBar) {
    summaryBar.appendChild(btn);
  }
}

async function handleExport(rank, category, board, coursePrefs, minResults, roundNum) {
  const btn = document.getElementById('export-btn');
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Exporting...';
  }

  try {
    const res = await fetch('/api/export/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({
        rank,
        category,
        board,
        course_preferences: coursePrefs,
        min_results: minResults,
        round: roundNum,
        inst_types: getSelectedInstTypes(),
        districts: getSelectedDistricts(),
      }),
    });

    if (!res.ok) {
      const json = await res.json();
      showError(json.error || 'Export failed.');
      return;
    }

    // Download the file
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Elytraa_Predictions_Rank_${rank}.xlsx`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } catch (err) {
    console.error('Export error:', err);
    showError('Export failed. Please try again.');
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '<i class="fas fa-file-excel me-2"></i>Export to Excel';
    }
  }
}
