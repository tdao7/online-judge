/**
 * scripts/challenger2_client_controller_stress.js
 * Milestone 3 Iteration 2 Challenger 2: Screen 1 Client-Side Controller Adversarial Stress Harness
 *
 * Tests:
 * 1. Empty localStorage variations (null, empty string, empty array).
 * 2. LocalStorage corruption & edge-case values (malformed JSON, 'null', '{}', '123', 'true').
 * 3. LocalStorage throwing exceptions (QuotaExceededError, SecurityError / Private Browsing).
 * 4. Bookmarked tab row unstarring behavior (dynamic row hiding, badge decrementing, tab persistence).
 * 5. Rapid toggle stress & deduplication under concurrency.
 * 6. Edge-case problem codes (special chars, dashes, underscores).
 * 7. DOM resilience when elements are missing.
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

console.log('\n======================================================================');
console.log('CHALLENGER 2: SCREEN 1 CLIENT-SIDE CONTROLLER ADVERSARIAL STRESS HARNESS');
console.log('======================================================================\n');

let passed = 0;
let failed = 0;
const findings = [];

function check(title, condition, detail = '') {
  if (condition) {
    passed++;
    console.log(`  [PASS] ${title}${detail ? ' (' + detail + ')' : ''}`);
  } else {
    failed++;
    const msg = `  [FAIL] ${title}${detail ? ' (' + detail + ')' : ''}`;
    console.error(msg);
    findings.push(msg);
  }
}

// Minimal DOM Mock supporting queries and event bubbling
class MockElement {
  constructor(tag, attrs = {}) {
    this.tagName = tag.toUpperCase();
    this.attrs = { ...attrs };
    this.classList = {
      _set: new Set(attrs.class ? attrs.class.split(/\s+/) : []),
      add: (c) => this.classList._set.add(c),
      remove: (c) => this.classList._set.delete(c),
      contains: (c) => this.classList._set.has(c),
      toggle: (c) => {
        if (this.classList._set.has(c)) {
          this.classList._set.delete(c);
          return false;
        } else {
          this.classList._set.add(c);
          return true;
        }
      }
    };
    this.style = {};
    this.children = [];
    this.parentElement = null;
    this.value = attrs.value || '';
    this._textContent = attrs.text !== undefined ? String(attrs.text) : '';
    this._listeners = {};
  }

  get textContent() {
    return this._textContent;
  }

  set textContent(val) {
    this._textContent = String(val);
  }

  getAttribute(k) { return this.attrs[k] !== undefined ? this.attrs[k] : null; }
  setAttribute(k, v) { this.attrs[k] = String(v); }
  removeAttribute(k) { delete this.attrs[k]; }

  appendChild(el) {
    el.parentElement = this;
    this.children.push(el);
    return el;
  }

  addEventListener(event, fn) {
    this._listeners[event] = this._listeners[event] || [];
    this._listeners[event].push(fn);
  }

  closest(selector) {
    let cur = this;
    while (cur) {
      if (cur.matches && cur.matches(selector)) return cur;
      cur = cur.parentElement;
    }
    return null;
  }

  matches(selector) {
    const parts = selector.split(',').map(s => s.trim());
    for (const part of parts) {
      if (part.startsWith('.')) {
        const classes = part.split('.').filter(Boolean);
        if (classes.every(c => this.classList.contains(c))) return true;
      } else if (part.startsWith('#')) {
        if (this.attrs.id === part.substring(1)) return true;
      } else if (part.toLowerCase() === this.tagName.toLowerCase()) {
        return true;
      }
    }
    return false;
  }

  querySelectorAll(selector) {
    const results = [];
    function walk(node) {
      if (node.children) {
        for (const child of node.children) {
          if (child.matches && child.matches(selector)) results.push(child);
          walk(child);
        }
      }
    }
    walk(this);
    return results;
  }

  querySelector(selector) {
    return this.querySelectorAll(selector)[0] || null;
  }
}

function createHarness(initialStorage = {}, options = {}) {
  const mockStorage = { ...initialStorage };
  const storageThrowOnGet = options.throwOnGet || false;
  const storageThrowOnSet = options.throwOnSet || false;

  const localStorageMock = {
    getItem: (key) => {
      if (storageThrowOnGet) throw new Error('Storage access denied (SecurityError)');
      return key in mockStorage ? mockStorage[key] : null;
    },
    setItem: (key, val) => {
      if (storageThrowOnSet) throw new Error('Quota exceeded (QuotaExceededError)');
      mockStorage[key] = String(val);
    },
    removeItem: (key) => { delete mockStorage[key]; },
    clear: () => { Object.keys(mockStorage).forEach(k => delete mockStorage[k]); }
  };

  const docListeners = {};
  const allElements = [];
  const elementsById = {};

  const registerEl = (el, id) => {
    if (id) {
      el.setAttribute('id', id);
      elementsById[id] = el;
    }
    allElements.push(el);
    return el;
  };

  const mockDoc = {
    addEventListener: (event, fn) => {
      docListeners[event] = docListeners[event] || [];
      docListeners[event].push(fn);
    },
    getElementById: (id) => elementsById[id] || null,
    querySelectorAll: (selector) => {
      const list = [];
      for (const el of allElements) {
        if (el.matches && el.matches(selector)) list.push(el);
      }
      return list;
    },
    querySelector: (selector) => mockDoc.querySelectorAll(selector)[0] || null
  };

  const filterForm = registerEl(new MockElement('form'), 'problems-filter-form');
  filterForm.submit = () => { harness.formSubmitted = true; };

  const statusInput = registerEl(new MockElement('input', { value: options.statusInputValue || 'all' }), 'filter-status');
  const orderInput = registerEl(new MockElement('input', { value: 'code' }), 'filter-order');
  const diffInput = registerEl(new MockElement('input', { value: '' }), 'filter-difficulty');
  const typeInput = registerEl(new MockElement('input', { value: '' }), 'filter-type');
  const catInput = registerEl(new MockElement('input', { value: '' }), 'filter-category');
  const groupInput = registerEl(new MockElement('input', { value: '' }), 'filter-group');
  const pointsInput = registerEl(new MockElement('input', { value: '' }), 'filter-points-preset');
  const searchInput = registerEl(new MockElement('input', { value: '' }), 'search');
  const badge = registerEl(new MockElement('span', { text: '0' }), 'bookmark-count-badge');
  badge.style.display = 'none';

  const btnSortToggle = registerEl(new MockElement('button', { class: 'btn-sort-toggle' }), 'btn-sort-toggle');
  const clearBtn = registerEl(new MockElement('button', { class: 'btn-clear-search' }), 'btn-clear-search');

  const pillAll = registerEl(new MockElement('button', {
    class: `pill-tab-item filter-pill ${options.activePill === 'all' ? 'active' : ''}`,
    'data-status': 'all'
  }));
  const pillBookmarked = registerEl(new MockElement('button', {
    class: `pill-tab-item filter-pill ${options.activePill === 'bookmarked' ? 'active' : ''}`,
    'data-status': 'bookmarked'
  }), 'pill-bookmarked');
  const pillSolved = registerEl(new MockElement('button', {
    class: `pill-tab-item filter-pill ${options.activePill === 'solved' ? 'active' : ''}`,
    'data-status': 'solved'
  }));
  const pillUnsolved = registerEl(new MockElement('button', {
    class: `pill-tab-item filter-pill ${options.activePill === 'unsolved' ? 'active' : ''}`,
    'data-status': 'unsolved'
  }));

  const rows = [];
  const makeRow = (code, id) => {
    const tr = registerEl(new MockElement('tr', { class: 'problem-row', 'data-code': code, 'data-id': id }));
    const tdStar = new MockElement('td', { class: 'col-star' });
    const starBtn = registerEl(new MockElement('button', { class: 'btn-star btn-bookmark-row', 'data-code': code }));
    tdStar.appendChild(starBtn);
    tr.appendChild(tdStar);
    const rowObj = { tr, starBtn, code };
    rows.push(rowObj);
    return rowObj;
  };

  const windowMock = {
    localStorage: localStorageMock,
    location: {
      search: options.locationSearch || '',
      href: `http://localhost/problems/${options.locationSearch || ''}`
    },
    history: {
      replaceState: (state, title, url) => {
        windowMock.location.href = url;
        const qIdx = url.indexOf('?');
        windowMock.location.search = qIdx !== -1 ? url.substring(qIdx) : '';
      }
    }
  };

  const jsPath = path.resolve(__dirname, '../resources/problems-list.js');
  const jsCode = fs.readFileSync(jsPath, 'utf-8');

  const sandbox = new Function('window', 'document', 'localStorage', jsCode);
  sandbox(windowMock, mockDoc, localStorageMock);

  const harness = {
    mockStorage,
    localStorageMock,
    mockDoc,
    docListeners,
    windowMock,
    filterForm,
    statusInput,
    badge,
    pillAll,
    pillBookmarked,
    pillSolved,
    pillUnsolved,
    rows,
    makeRow,
    formSubmitted: false,
    fireClick: (target) => {
      const e = {
        target,
        preventDefault: () => {},
        stopPropagation: () => {}
      };
      if (docListeners['click']) {
        docListeners['click'].forEach(fn => fn(e));
      }
    },
    triggerDOMContentLoaded: () => {
      if (docListeners['DOMContentLoaded']) {
        docListeners['DOMContentLoaded'].forEach(fn => fn());
      }
    }
  };

  return harness;
}

// ============================================================================
// STRESS TEST SECTION 1: Empty localStorage Variations
// ============================================================================
console.log('--- SECTION 1: Empty localStorage Variations ---');

// 1.1: Completely uninitialized localStorage (getItem returns null)
{
  const h = createHarness({});
  const r1 = h.makeRow('aplusb', '1');
  h.triggerDOMContentLoaded();

  check('Empty localStorage: initial bookmark count badge is hidden', h.badge.style.display === 'none');
  check('Empty localStorage: star button is not active', !r1.starBtn.classList.contains('active'));
  check('Empty localStorage: star button aria-pressed is false', r1.starBtn.getAttribute('aria-pressed') === 'false');

  // Star a problem
  h.fireClick(r1.starBtn);
  check('Empty localStorage: clicking star activates button', r1.starBtn.classList.contains('active'));
  check('Empty localStorage: clicking star sets badge to 1', h.badge.textContent === '1' && h.badge.style.display === 'inline-block');
  const stored = JSON.parse(h.mockStorage['vcoder_bookmarked_problems']);
  check('Empty localStorage: persists ["aplusb"] to storage', Array.isArray(stored) && stored[0] === 'aplusb');
}

// 1.2: LocalStorage containing empty array string "[]"
{
  const h = createHarness({ vcoder_bookmarked_problems: '[]' });
  const r1 = h.makeRow('aplusb', '1');
  h.triggerDOMContentLoaded();
  check('localStorage="[]": badge is hidden', h.badge.style.display === 'none');
  check('localStorage="[]": star button inactive', !r1.starBtn.classList.contains('active'));
}

// 1.3: LocalStorage containing empty string ""
{
  const h = createHarness({ vcoder_bookmarked_problems: '' });
  const r1 = h.makeRow('aplusb', '1');
  h.triggerDOMContentLoaded();
  check('localStorage="": fallback to "[]" keeps badge hidden', h.badge.style.display === 'none');
  check('localStorage="": star button inactive', !r1.starBtn.classList.contains('active'));
}

// ============================================================================
// STRESS TEST SECTION 2: LocalStorage Corruption Variations
// ============================================================================
console.log('\n--- SECTION 2: LocalStorage Corruption Variations ---');

// 2.1: Malformed JSON strings
const corruptions = [
  '{broken_json',
  '{{undefined}}',
  '[1, 2, ',
  '{"key": invalid}',
  'NaN',
  '<<<not json>>>'
];

corruptions.forEach((badVal, idx) => {
  const h = createHarness({ vcoder_bookmarked_problems: badVal });
  const r1 = h.makeRow('aplusb', '1');
  let err = null;
  try {
    h.triggerDOMContentLoaded();
  } catch (e) {
    err = e;
  }
  check(`Malformed JSON #${idx + 1} (${badVal.substring(0, 12)}): DOMContentLoaded recovers without error`, err === null, err ? err.message : '');
  check(`Malformed JSON #${idx + 1}: badge hidden on recovery`, h.badge.style.display === 'none');

  // Verify clicking star heals localStorage
  h.fireClick(r1.starBtn);
  const healed = JSON.parse(h.mockStorage['vcoder_bookmarked_problems']);
  check(`Malformed JSON #${idx + 1}: star click safely resets and persists valid array`, Array.isArray(healed) && healed.includes('aplusb'));
});

// 2.2: Valid JSON that is NOT an Array of strings
// Note: JSON.parse('null') -> null. If getBookmarks() does not check Array.isArray,
// null.indexOf() or obj.indexOf() throws TypeError.
const nonArrayJson = [
  { label: 'JSON null ("null")', raw: 'null' },
  { label: 'JSON object ("{}")', raw: '{}' },
  { label: 'JSON number ("42")', raw: '42' },
  { label: 'JSON boolean ("true")', raw: 'true' }
];

nonArrayJson.forEach(item => {
  const h = createHarness({ vcoder_bookmarked_problems: item.raw });
  const r1 = h.makeRow('aplusb', '1');
  let loadErr = null;
  try {
    h.triggerDOMContentLoaded();
  } catch (e) {
    loadErr = e;
  }

  // Check if non-array causes crash or if handled gracefully
  let clickErr = null;
  try {
    h.fireClick(r1.starBtn);
  } catch (e) {
    clickErr = e;
  }

  check(`Non-array ${item.label}: DOMContentLoaded handles without crash`, loadErr === null, loadErr ? loadErr.message : '');
  check(`Non-array ${item.label}: Star click handles without crash`, clickErr === null, clickErr ? clickErr.message : '');
});

// ============================================================================
// STRESS TEST SECTION 3: Storage Access Throwing (Safari Private Mode / Quota)
// ============================================================================
console.log('\n--- SECTION 3: Storage Access Throwing Exceptions ---');

// 3.1: getItem throws SecurityError (Private browsing)
{
  const h = createHarness({}, { throwOnGet: true });
  const r1 = h.makeRow('aplusb', '1');
  let err = null;
  try {
    h.triggerDOMContentLoaded();
  } catch (e) {
    err = e;
  }
  check('Private browsing (throw on getItem): DOMContentLoaded does not crash', err === null, err ? err.message : '');
  check('Private browsing: badge remains hidden', h.badge.style.display === 'none');
}

// 3.2: setItem throws QuotaExceededError
{
  const h = createHarness({}, { throwOnSet: true });
  const r1 = h.makeRow('aplusb', '1');
  h.triggerDOMContentLoaded();
  let clickErr = null;
  try {
    h.fireClick(r1.starBtn);
  } catch (e) {
    clickErr = e;
  }
  check('QuotaExceeded (throw on setItem): clicking star does not crash', clickErr === null, clickErr ? clickErr.message : '');
}

// ============================================================================
// STRESS TEST SECTION 4: Bookmarked Tab Row Unstarring Behavior
// ============================================================================
console.log('\n--- SECTION 4: Bookmarked Tab Row Unstarring & Dynamic Filtering ---');

{
  // 5 problems, 3 initially bookmarked: p1, p2, p3
  const initial = ['prob1', 'prob2', 'prob3'];
  const h = createHarness(
    { vcoder_bookmarked_problems: JSON.stringify(initial) },
    { activePill: 'bookmarked', locationSearch: '?status=bookmarked', statusInputValue: 'bookmarked' }
  );

  const r1 = h.makeRow('prob1', '1');
  const r2 = h.makeRow('prob2', '2');
  const r3 = h.makeRow('prob3', '3');
  const r4 = h.makeRow('prob4', '4');
  const r5 = h.makeRow('prob5', '5');

  h.triggerDOMContentLoaded();

  // On page load with ?status=bookmarked:
  check('Initial load on Bookmarked tab: badge shows 3', h.badge.textContent === '3');
  check('Row prob1 is visible', r1.tr.style.display === '');
  check('Row prob2 is visible', r2.tr.style.display === '');
  check('Row prob3 is visible', r3.tr.style.display === '');
  check('Row prob4 is hidden', r4.tr.style.display === 'none');
  check('Row prob5 is hidden', r5.tr.style.display === 'none');

  // User unstars prob2 while on the bookmarked tab
  h.fireClick(r2.starBtn);
  check('Unstarring prob2: prob2 row is immediately hidden (display: none)', r2.tr.style.display === 'none');
  check('Unstarring prob2: prob1 remains visible', r1.tr.style.display === '');
  check('Unstarring prob2: prob3 remains visible', r3.tr.style.display === '');
  check('Unstarring prob2: badge count decrements to 2', h.badge.textContent === '2');
  check('Unstarring prob2: localStorage updated to length 2', JSON.parse(h.mockStorage['vcoder_bookmarked_problems']).length === 2);

  // User unstars prob1
  h.fireClick(r1.starBtn);
  check('Unstarring prob1: prob1 row is immediately hidden', r1.tr.style.display === 'none');
  check('Unstarring prob1: badge count decrements to 1', h.badge.textContent === '1');

  // User unstars prob3 (all bookmarked problems now unstarred)
  h.fireClick(r3.starBtn);
  check('Unstarring prob3: prob3 row is immediately hidden', r3.tr.style.display === 'none');
  check('All unstarred: all 5 rows now hidden', [r1, r2, r3, r4, r5].every(r => r.tr.style.display === 'none'));
  check('All unstarred: badge display is none', h.badge.style.display === 'none');
  check('All unstarred: localStorage holds empty array []', JSON.parse(h.mockStorage['vcoder_bookmarked_problems']).length === 0);

  // Switching tab from Bookmarked to "All Problems"
  h.formSubmitted = false;
  const allListeners = h.pillAll._listeners['click'] || [];
  allListeners.forEach(fn => fn({ preventDefault: () => {} }));
  check('Switching to All Problems: sets status input to "all"', h.statusInput.value === 'all');
  check('Switching to All Problems: triggers filterForm.submit()', h.formSubmitted === true);
}

// ============================================================================
// STRESS TEST SECTION 5: Rapid Toggling & Idempotency Stress
// ============================================================================
console.log('\n--- SECTION 5: Rapid Toggling & Idempotency Stress ---');

{
  const h = createHarness({});
  const r1 = h.makeRow('stress_prob', '100');
  h.triggerDOMContentLoaded();

  // Rapidly toggle 50 times
  for (let i = 0; i < 50; i++) {
    h.fireClick(r1.starBtn);
  }
  // After 50 toggles (even number), problem should be UNBOOKMARKED
  const listAfterEven = JSON.parse(h.mockStorage['vcoder_bookmarked_problems'] || '[]');
  check('50 rapid toggles (even): problem is unbookmarked', !listAfterEven.includes('stress_prob') && listAfterEven.length === 0);
  check('50 rapid toggles: star button active class is false', !r1.starBtn.classList.contains('active'));
  check('50 rapid toggles: badge display is none', h.badge.style.display === 'none');

  // 1 more toggle -> 51 (odd) -> BOOKMARKED
  h.fireClick(r1.starBtn);
  const listAfterOdd = JSON.parse(h.mockStorage['vcoder_bookmarked_problems'] || '[]');
  check('51st toggle (odd): problem is bookmarked', listAfterOdd.includes('stress_prob') && listAfterOdd.length === 1);
  check('51st toggle: star button active class is true', r1.starBtn.classList.contains('active'));
  check('51st toggle: badge text is 1', h.badge.textContent === '1');
}

// ============================================================================
// STRESS TEST SECTION 6: Edge Case Problem Codes
// ============================================================================
console.log('\n--- SECTION 6: Edge Case Problem Codes ---');

{
  const h = createHarness({});
  const specialCodes = [
    'prob-with-hyphens',
    'prob_with_underscores',
    'prob.with.dots',
    'UPPER_CASE_CODE',
    '123456',
    'code with spaces',
    'code"quote\'apostrophe'
  ];

  const rows = specialCodes.map((code, idx) => h.makeRow(code, String(idx)));
  h.triggerDOMContentLoaded();

  specialCodes.forEach((code, idx) => {
    h.fireClick(rows[idx].starBtn);
  });

  const stored = JSON.parse(h.mockStorage['vcoder_bookmarked_problems']);
  check('Special problem codes: all 7 codes stored', stored.length === specialCodes.length);
  specialCodes.forEach(code => {
    check(`Special code '${code}' stored accurately`, stored.includes(code));
  });
  check('Badge reflects 7 items', h.badge.textContent === '7');
}

// ============================================================================
// STRESS TEST SECTION 7: Missing DOM Elements Resilience
// ============================================================================
console.log('\n--- SECTION 7: Missing DOM Elements Resilience ---');

{
  // Test when badge is missing from DOM
  const h = createHarness({});
  // Remove badge from DOM lookup
  delete h.mockDoc.getElementById('bookmark-count-badge');
  h.badge.setAttribute('id', 'removed');

  const r1 = h.makeRow('aplusb', '1');
  let err = null;
  try {
    h.triggerDOMContentLoaded();
    h.fireClick(r1.starBtn);
  } catch (e) {
    err = e;
  }
  check('Missing #bookmark-count-badge: does not throw on star click', err === null, err ? err.message : '');
}

console.log('\n======================================================================');
console.log(`CHALLENGER 2 JS SUMMARY: Passed: ${passed} | Failed: ${failed}`);
console.log('======================================================================\n');

if (findings.length > 0) {
  console.log('CHALLENGE FINDINGS:');
  findings.forEach(f => console.log('  ' + f));
}

process.exit(failed > 0 ? 1 : 0);
