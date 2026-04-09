/**
 * predictor/static/predictor/script.js
 * Elytraa University Predictor — Frontend Logic
 *
 * Responsibilities:
 *   1. On page load: fetch /api/options/ → populate category, board dropdowns + course chips
 *   2. On form submit: POST /api/predict/ → render result cards
 *   3. Animations: staggered card reveal, score bar fill
 *   4. Reset: clear form and results
 */

'use strict';

// ── DOM references ─────────────────────────────────────────────────────── //
const rankInput          = document.getElementById('rank-input');
const categorySelect     = document.getElementById('category-select');
const boardSelect        = document.getElementById('board-select');
const minResultsSelect   = document.getElementById('min-results-select');
const courseCheckboxes   = document.getElementById('course-checkboxes');
const predictBtn         = document.getElementById('predict-btn');
const resetBtn           = document.getElementById('reset-btn');
const formError          = document.getElementById('form-error');
const loadingOverlay     = document.getElementById('loading-overlay');
const loadingCount       = document.getElementById('loading-count');
const resultsSection     = document.getElementById('results-section');
const resultsContainer   = document.getElementById('results-container');
const resultsSummaryText = document.getElementById('results-summary-text');

// ── Boot ────────────────────────────────────────────────────────────────── //
document.addEventListener('DOMContentLoaded', () => {
  loadOptions();
  predictBtn.addEventListener('click', handlePredict);
  resetBtn.addEventListener('click', handleReset);
});

// ── 1. Load dropdown options ─────────────────────────────────────────────── //
async function loadOptions() {
  try {
    const res  = await fetch('/api/options/');
    const json = await res.json();

    if (!json.success) {
      console.error('Options API error:', json.error);
      setSelectPlaceholder(categorySelect, 'GEN, SC, ST, OBC…');
      setSelectPlaceholder(boardSelect,   'GUJCET, JEE…');
      courseCheckboxes.innerHTML = '<span class="chip-placeholder" style="color:#94a3b8;">Could not load courses. Type your preference above.</span>';
      return;
    }

    // Category dropdown
    populateSelect(categorySelect, json.data.categories, 'All Categories (no filter)');

    // Board dropdown
    populateSelect(boardSelect, json.data.boards, 'All Boards (no filter)');

    // Course chips
    buildCourseChips(json.data.course_keywords);

  } catch (err) {
    console.error('Failed to load options:', err);
    setSelectPlaceholder(categorySelect, '— Error loading —');
    setSelectPlaceholder(boardSelect,   '— Error loading —');
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
    input.type      = 'checkbox';
    input.className = 'course-chip visually-hidden';
    input.value     = kw.toLowerCase();
    input.id        = id;

    const label = document.createElement('label');
    label.htmlFor   = id;
    label.className = 'course-chip-label';
    label.textContent = kw;

    courseCheckboxes.appendChild(input);
    courseCheckboxes.appendChild(label);
  });
}

// ── 2. Form submission ───────────────────────────────────────────────────── //
async function handlePredict() {
  clearError();

  // Client-side validation
  const rank = parseInt(rankInput.value, 10);
  if (!rank || rank <= 0) {
    showError('Please enter a valid rank (a positive whole number).');
    rankInput.focus();
    return;
  }

  const category   = categorySelect.value   || null;
  const board      = boardSelect.value      || null;
  const minResults = parseInt(minResultsSelect.value, 10) || 15;

  const checked = courseCheckboxes.querySelectorAll('input.course-chip:checked');
  const coursePrefs = checked.length > 0
    ? Array.from(checked).map(cb => cb.value)
    : null;

  // Show loading
  showLoading();
  predictBtn.disabled = true;

  const payload = {
    rank,
    category,
    board,
    course_preferences: coursePrefs,
    min_results: minResults,
  };

  try {
    const res  = await fetch('/api/predict/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const json = await res.json();

    if (!json.success) {
      const errMsg = typeof json.error === 'object'
        ? Object.values(json.error).flat().join(' ')
        : (json.error || 'Something went wrong. Please try again.');
      showError(errMsg);
      return;
    }

    if (!json.results || json.results.length === 0) {
      showError('No colleges found for your criteria. Try widening your search (change category, board, or add more course preferences).');
      return;
    }

    renderResults(json.results, rank, category, board);
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

  } catch (err) {
    console.error('Prediction fetch error:', err);
    showError('Network error. Is the server running? Please try again.');
  } finally {
    hideLoading();
    predictBtn.disabled = false;
  }
}

// ── 3. Render results ────────────────────────────────────────────────────── //
function renderResults(results, rank, category, board) {
  const safe     = results.filter(r => r.chance === 'Safe').length;
  const possible = results.filter(r => r.chance === 'Possible').length;
  const stretch  = results.filter(r => r.chance === 'Stretch').length;

  // Summary text
  const filters = [
    rank     ? `Rank ${rank.toLocaleString('en-IN')}` : null,
    category ? `Category: ${category}`              : null,
    board    ? `Board: ${board}`                    : null,
  ].filter(Boolean).join(' · ');

  resultsSummaryText.innerHTML =
    `${results.length} colleges found${filters ? ` for <strong>${filters}</strong>` : ''} — ` +
    `<span style="color:var(--safe)">${safe} Safe</span>, ` +
    `<span style="color:var(--possible)">${possible} Possible</span>, ` +
    `<span style="color:var(--stretch)">${stretch} Stretch</span>`;

  // Group by preferred_course
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

    colleges.forEach((college, i) => {
      group.appendChild(buildCard(college, i));
    });

    resultsContainer.appendChild(group);
  });

  // Staggered card reveal with IntersectionObserver
  const cards = resultsContainer.querySelectorAll('.result-card');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const card = entry.target;
        const delay = parseFloat(card.dataset.delay || 0);
        setTimeout(() => {
          card.classList.add('card-visible');
          // Animate score bar
          const fill = card.querySelector('.score-bar-fill');
          if (fill) fill.style.width = fill.dataset.width;
        }, delay);
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
  card.dataset.delay = Math.min(index * 60, 600); // max 600ms delay

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

// ── 4. Reset ─────────────────────────────────────────────────────────────── //
function handleReset() {
  rankInput.value = '';
  categorySelect.value = '';
  boardSelect.value = '';
  minResultsSelect.value = '15';
  courseCheckboxes.querySelectorAll('input.course-chip:checked')
    .forEach(cb => { cb.checked = false; });
  clearError();
  resultsSection.style.display = 'none';
  resultsContainer.innerHTML = '';
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ── Helpers ──────────────────────────────────────────────────────────────── //
function showLoading() {
  loadingOverlay.style.display = 'flex';
  // Animate counter
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
