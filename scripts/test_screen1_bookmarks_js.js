/**
 * Empirical Stress Harness for Screen 1 Client-Side JavaScript
 * Tests resources/problems-list.js behavior in a simulated DOM & localStorage environment.
 */
const fs = require('fs');
const path = require('path');
const assert = require('assert');

console.log('\n======================================================================');
console.log('SCREEN 1 JAVASCRIPT & BOOKMARKING EMPIRICAL TEST HARNESS');
console.log('======================================================================\n');

let passed = 0;
let failed = 0;

function check(title, condition, detail = '') {
  if (condition) {
    passed++;
    console.log(`  [PASS] ${title}${detail ? ' (' + detail + ')' : ''}`);
  } else {
    failed++;
    console.error(`  [FAIL] ${title}${detail ? ' (' + detail + ')' : ''}`);
  }
}

// 1. Mock localStorage
const mockStorage = {};
const localStorageMock = {
  getItem: (key) => (key in mockStorage ? mockStorage[key] : null),
  setItem: (key, val) => { mockStorage[key] = String(val); },
  removeItem: (key) => { delete mockStorage[key]; },
  clear: () => { Object.keys(mockStorage).forEach(k => delete mockStorage[k]); }
};

// 2. Minimal Mock DOM Elements
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
    this.textContent = attrs.text || '';
    this._listeners = {};
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

// 3. Setup simulated Document & Window
const docListeners = {};
const mockDoc = {
  addEventListener: (event, fn) => {
    docListeners[event] = docListeners[event] || [];
    docListeners[event].push(fn);
  },
  getElementById: (id) => mockElementsById[id] || null,
  querySelectorAll: (selector) => {
    const list = [];
    for (const el of allMockElements) {
      if (el.matches && el.matches(selector)) list.push(el);
    }
    return list;
  },
  querySelector: (selector) => mockDoc.querySelectorAll(selector)[0] || null
};

const allMockElements = [];
const mockElementsById = {};

function registerMockEl(el, id) {
  if (id) {
    el.setAttribute('id', id);
    mockElementsById[id] = el;
  }
  allMockElements.push(el);
  return el;
}

// Construct Screen 1 Mock DOM Elements
const filterForm = registerMockEl(new MockElement('form'), 'problems-filter-form');
let formSubmitted = false;
filterForm.submit = () => { formSubmitted = true; };

const statusInput = registerMockEl(new MockElement('input', { value: 'all' }), 'filter-status');
const orderInput = registerMockEl(new MockElement('input', { value: 'code' }), 'filter-order');
const diffInput = registerMockEl(new MockElement('input', { value: '' }), 'filter-difficulty');
const catInput = registerMockEl(new MockElement('input', { value: '' }), 'filter-category');
const pointsInput = registerMockEl(new MockElement('input', { value: '' }), 'filter-points-preset');
const searchInput = registerMockEl(new MockElement('input', { value: 'initial' }), 'search');
const badge = registerMockEl(new MockElement('span', { text: '0' }), 'bookmark-count-badge');
badge.style.display = 'none';

const btnSortToggle = registerMockEl(new MockElement('button', { class: 'btn-sort-toggle btn-sort-order' }), 'btn-sort-toggle');
const clearBtn = registerMockEl(new MockElement('button', { class: 'btn-clear-search' }), 'btn-clear-search');

const pillAll = registerMockEl(new MockElement('button', { class: 'pill-tab-item filter-pill active', 'data-status': 'all' }));
const pillBookmarked = registerMockEl(new MockElement('button', { class: 'pill-tab-item filter-pill', 'data-status': 'bookmarked' }), 'pill-bookmarked');
const pillSolved = registerMockEl(new MockElement('button', { class: 'pill-tab-item filter-pill', 'data-status': 'solved' }));
const pillUnsolved = registerMockEl(new MockElement('button', { class: 'pill-tab-item filter-pill', 'data-status': 'unsolved' }));

// 3 problem rows
function createRow(code, id) {
  const row = registerMockEl(new MockElement('tr', { class: 'problem-row', 'data-code': code, 'data-id': id }));
  const tdStar = new MockElement('td', { class: 'col-star' });
  const starBtn = registerMockEl(new MockElement('button', { class: 'btn-star btn-bookmark-row', 'data-code': code }));
  tdStar.appendChild(starBtn);
  row.appendChild(tdStar);
  return { row, starBtn };
}

const p1 = createRow('aplusb', '1');
const p2 = createRow('fibonacci', '2');
const p3 = createRow('primes', '3');

// Load and evaluate resources/problems-list.js
const jsPath = path.resolve(__dirname, '../resources/problems-list.js');
const jsCode = fs.readFileSync(jsPath, 'utf-8');

// Function wrapper injecting mocks
const runController = (windowMock, docMock) => {
  const sandbox = new Function('window', 'document', 'localStorage', jsCode);
  sandbox(windowMock, docMock, localStorageMock);
};

const windowMock = {
  localStorage: localStorageMock
};

// Run the script
runController(windowMock, mockDoc);

// Trigger DOMContentLoaded
if (docListeners['DOMContentLoaded']) {
  docListeners['DOMContentLoaded'].forEach(fn => fn());
}

// -----------------------------------------------------------------------------
// Test 1: Initial state without bookmarks
// -----------------------------------------------------------------------------
check('Initial bookmark count is 0', badge.style.display === 'none', `display=${badge.style.display}`);
check('Star buttons unpressed initially', !p1.starBtn.classList.contains('active'));

// -----------------------------------------------------------------------------
// Test 2: Star bookmark click toggles state
// -----------------------------------------------------------------------------
function fireDocClick(target) {
  const e = {
    target: target,
    preventDefault: () => {},
    stopPropagation: () => {}
  };
  if (docListeners['click']) {
    docListeners['click'].forEach(fn => fn(e));
  }
}

// Click star on p1 ('aplusb')
fireDocClick(p1.starBtn);
const bList1 = JSON.parse(localStorageMock.getItem('vcoder_bookmarked_problems') || '[]');
check('Star click adds problem code to localStorage', bList1.includes('aplusb'), `stored: ${JSON.stringify(bList1)}`);
check('Star button has active class', p1.starBtn.classList.contains('active'));
check('Star button aria-pressed is true', p1.starBtn.getAttribute('aria-pressed') === 'true');
check('Badge shows count 1 and is visible', badge.style.display === 'inline-block' && String(badge.textContent) === '1', `badge: ${badge.textContent}, display: ${badge.style.display}`);

// Click star on p2 ('fibonacci')
fireDocClick(p2.starBtn);
const bList2 = JSON.parse(localStorageMock.getItem('vcoder_bookmarked_problems') || '[]');
check('Star click adds second problem', bList2.length === 2 && bList2.includes('fibonacci'));
check('Badge updates to count 2', String(badge.textContent) === '2');

// Click star on p1 again to untoggle
fireDocClick(p1.starBtn);
const bList3 = JSON.parse(localStorageMock.getItem('vcoder_bookmarked_problems') || '[]');
check('Star click untoggles problem', !bList3.includes('aplusb') && bList3.length === 1);
check('Star button removes active class', !p1.starBtn.classList.contains('active'));
check('Badge updates to count 1', String(badge.textContent) === '1');

// -----------------------------------------------------------------------------
// Test 3: Corrupted localStorage recovery
// -----------------------------------------------------------------------------
localStorageMock.setItem('vcoder_bookmarked_problems', '{{INVALID JSON!!]');
// Trigger star click
fireDocClick(p1.starBtn);
const bList4 = JSON.parse(localStorageMock.getItem('vcoder_bookmarked_problems') || '[]');
check('Corrupted localStorage gracefully handled and reset', Array.isArray(bList4) && bList4.includes('aplusb'));

// -----------------------------------------------------------------------------
// Test 4: Quick Filter Pill - Bookmarked tab filtering
// -----------------------------------------------------------------------------
// Currently bList4 has ['aplusb']
// Fire click on pillBookmarked
const pillClickListeners = pillBookmarked._listeners['click'] || [];
pillClickListeners.forEach(fn => fn({ preventDefault: () => {} }));

check('Pill Bookmarked receives active class', pillBookmarked.classList.contains('active'));
check('Pill All loses active class', !pillAll.classList.contains('active'));
check('Bookmarked problem (aplusb) row remains visible', p1.row.style.display === '', `display: '${p1.row.style.display}'`);
check('Non-bookmarked problem (fibonacci) row is hidden', p2.row.style.display === 'none', `display: '${p2.row.style.display}'`);
check('Non-bookmarked problem (primes) row is hidden', p3.row.style.display === 'none', `display: '${p3.row.style.display}'`);

// Untoggle aplusb while on bookmarked tab -> row should disappear
fireDocClick(p1.starBtn);
check('Untoggling while on bookmarked tab hides the row dynamically', p1.row.style.display === 'none');

// -----------------------------------------------------------------------------
// Test 5: Quick Filter Pill - Solved tab triggers form submission
// -----------------------------------------------------------------------------
formSubmitted = false;
const pillSolvedListeners = pillSolved._listeners['click'] || [];
pillSolvedListeners.forEach(fn => fn({ preventDefault: () => {} }));
check('Solved pill updates status input to "solved"', statusInput.value === 'solved');
check('Solved pill triggers filterForm.submit()', formSubmitted === true);

// -----------------------------------------------------------------------------
// Test 6: Sort Order Toggle (⇅)
// -----------------------------------------------------------------------------
orderInput.value = 'points';
formSubmitted = false;
const sortBtnListeners = btnSortToggle._listeners['click'] || [];
sortBtnListeners.forEach(fn => fn({ preventDefault: () => {} }));
check('Sort toggle inverts points to -points', orderInput.value === '-points');
check('Sort toggle triggers filterForm.submit()', formSubmitted === true);

// Toggle again
formSubmitted = false;
sortBtnListeners.forEach(fn => fn({ preventDefault: () => {} }));
check('Sort toggle inverts -points to points', orderInput.value === 'points');
check('Sort toggle triggers filterForm.submit()', formSubmitted === true);

// -----------------------------------------------------------------------------
// Test 7: Clear Search Button
// -----------------------------------------------------------------------------
searchInput.value = 'needle';
formSubmitted = false;
const clearBtnListeners = clearBtn._listeners['click'] || [];
clearBtnListeners.forEach(fn => fn({ preventDefault: () => {} }));
check('Clear search button resets search input to empty', searchInput.value === '');
check('Clear search triggers filterForm.submit()', formSubmitted === true);

// Summary
console.log('\n======================================================================');
console.log(`JAVASCRIPT EMPIRICAL SUMMARY: Passed: ${passed} | Failed: ${failed}`);
console.log('======================================================================\n');

if (failed > 0) {
  process.exit(1);
} else {
  process.exit(0);
}
