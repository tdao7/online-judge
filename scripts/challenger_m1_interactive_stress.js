/**
 * scripts/challenger_m1_interactive_stress.js
 * Empirical Challenger Adversarial Stress Harness: App Shell Interactive Controllers
 *
 * Verifies resources/app-shell-controller.js:
 * 1. Mobile navigation drawer toggle, swipe, resize, and backdrop dismissal.
 * 2. Global ⌘K search modal trigger, platform keycaps, keyboard navigation, input sanitization, and category filters.
 * 3. User profile dropdown toggle, outside click, and ESC dismissal.
 * 4. Notification bell popover toggle and dismissal.
 * 5. window.DmojAppShell exported API and state reflection.
 * 6. Fault tolerance and defensive degradation with missing DOM elements.
 *
 * Runs natively in Node.js (zero external dependencies).
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const REPO_ROOT = path.resolve(__dirname, '..');
const SCRIPT_PATH = path.join(REPO_ROOT, 'resources', 'app-shell-controller.js');
const scriptSource = fs.readFileSync(SCRIPT_PATH, 'utf-8');

console.log('======================================================================');
console.log('CHALLENGER 2: APP SHELL INTERACTIVE CONTROLLER ADVERSARIAL STRESS HARNESS');
console.log('======================================================================\n');

let passed = 0;
let failed = 0;
const findings = [];

function check(testName, condition, detail = '') {
  if (condition) {
    passed++;
    console.log(`  [PASS] ${testName}`);
  } else {
    failed++;
    const msg = `  [FAIL] ${testName}${detail ? ' - ' + detail : ''}`;
    console.error(msg);
    findings.push(msg);
  }
}

// Lightweight, resilient DOM Node mock
class MockNode {
  constructor(tag, attrs = {}) {
    this.tagName = (tag || 'DIV').toUpperCase();
    this.attributes = { ...attrs };
    this.id = attrs.id || '';
    this.style = {};
    this.children = [];
    this.parentNode = null;
    this.eventListeners = {};
    this.value = attrs.value || '';
    this.textContentInternal = attrs.text || '';
    this.innerHTMLInternal = attrs.html || '';

    const classNames = attrs.class ? attrs.class.trim().split(/\s+/) : [];
    this._classes = new Set(classNames.filter(Boolean));

    this.classList = {
      add: (...cls) => cls.forEach(c => this._classes.add(c)),
      remove: (...cls) => cls.forEach(c => this._classes.delete(c)),
      contains: (c) => this._classes.has(c),
      toggle: (c) => {
        if (this._classes.has(c)) {
          this._classes.delete(c);
          return false;
        } else {
          this._classes.add(c);
          return true;
        }
      }
    };
  }

  get className() {
    return Array.from(this._classes).join(' ');
  }

  set className(val) {
    this._classes = new Set(val.trim().split(/\s+/).filter(Boolean));
  }

  getAttribute(attr) {
    if (attr === 'class') return this.className;
    if (attr === 'id') return this.id;
    return this.attributes[attr] !== undefined ? String(this.attributes[attr]) : null;
  }

  setAttribute(attr, val) {
    const sVal = String(val);
    this.attributes[attr] = sVal;
    if (attr === 'id') this.id = sVal;
    if (attr === 'class') this.className = sVal;
  }

  removeAttribute(attr) {
    delete this.attributes[attr];
    if (attr === 'class') this._classes.clear();
    if (attr === 'id') this.id = '';
  }

  get innerHTML() {
    return this.innerHTMLInternal !== '' ? this.innerHTMLInternal : this.textContentInternal;
  }

  set innerHTML(html) {
    this.innerHTMLInternal = html;
    this.textContentInternal = html.replace(/<[^>]*>/g, '');
    this.children = this._parseHtmlChildren(html);
  }

  get textContent() {
    return this.textContentInternal;
  }

  set textContent(text) {
    this.textContentInternal = String(text);
    // Standard browser DOM behavior: setting textContent encodes HTML entities in innerHTML
    this.innerHTMLInternal = String(text)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
    this.children = [];
  }

  appendChild(child) {
    child.parentNode = this;
    this.children.push(child);
    return child;
  }

  contains(other) {
    if (!other) return false;
    if (other === this) return true;
    for (const c of this.children) {
      if (c.contains(other)) return true;
    }
    return false;
  }

  focus() {
    if (this.ownerDocument) {
      this.ownerDocument.activeElement = this;
    }
  }

  scrollIntoView() {}

  addEventListener(type, handler) {
    if (!this.eventListeners[type]) this.eventListeners[type] = [];
    this.eventListeners[type].push(handler);
  }

  removeEventListener(type, handler) {
    if (!this.eventListeners[type]) return;
    this.eventListeners[type] = this.eventListeners[type].filter(h => h !== handler);
  }

  dispatchEvent(event) {
    event.target = event.target || this;
    event.currentTarget = this;
    const handlers = this.eventListeners[event.type] || [];
    for (const h of handlers) {
      h.call(this, event);
    }
    if (event.bubbles && this.parentNode && !event.propagationStopped) {
      this.parentNode.dispatchEvent(event);
    }
    return !event.defaultPrevented;
  }

  click() {
    const evt = new MockEvent('click', { bubbles: true });
    evt.target = this;
    this.dispatchEvent(evt);
  }

  querySelector(selector) {
    return this._matchSelector(selector, false);
  }

  querySelectorAll(selector) {
    return this._matchSelector(selector, true);
  }

  _parseHtmlChildren(html) {
    const list = [];
    // Regex extracting tags: <tag ...>...</tag> or self-closing
    const regex = /<([a-z0-9]+)([^>]*)>(.*?)<\/\1>|<([a-z0-9]+)([^>]*)\/?>/gis;
    let match;
    while ((match = regex.exec(html)) !== null) {
      const tag = match[1] || match[4];
      const rawAttrs = match[2] || match[5] || '';
      const inner = match[3] || '';
      const node = new MockNode(tag);
      node.ownerDocument = this.ownerDocument;

      const attrRegex = /([a-z0-9_-]+)(?:=["']([^"']*)["'])?/gi;
      let aMatch;
      while ((aMatch = attrRegex.exec(rawAttrs)) !== null) {
        if (aMatch[1] && aMatch[1] !== '/') {
          node.setAttribute(aMatch[1], aMatch[2] || '');
        }
      }
      if (inner) {
        node.innerHTML = inner;
      }
      node.parentNode = this;
      list.push(node);
    }
    return list;
  }

  _matchSelector(selector, returnAll = false) {
    const results = [];
    const parts = selector.split(',').map(s => s.trim());

    const testNode = (node) => {
      for (const part of parts) {
        if (this._matchesSingle(node, part)) {
          if (!returnAll) return node;
          results.push(node);
          break;
        }
      }
      for (const child of node.children) {
        const found = testNode(child);
        if (!returnAll && found) return found;
      }
      return null;
    };

    for (const child of this.children) {
      const found = testNode(child);
      if (!returnAll && found) return found;
    }
    return returnAll ? results : null;
  }

  _matchesSingle(node, sel) {
    if (sel.startsWith('#')) {
      return node.id === sel.slice(1);
    }
    if (sel.startsWith('.')) {
      return node.classList.contains(sel.slice(1));
    }
    if (sel.includes('.')) {
      const [tag, cls] = sel.split('.');
      return (!tag || node.tagName === tag.toUpperCase()) && node.classList.contains(cls);
    }
    if (sel.startsWith('[') && sel.endsWith(']')) {
      const inner = sel.slice(1, -1);
      const [k, v] = inner.split('=');
      if (!v) return node.getAttribute(k) !== null;
      return node.getAttribute(k) === v.replace(/["']/g, '');
    }
    if (sel.includes('[') && sel.endsWith(']')) {
      const bracketIdx = sel.indexOf('[');
      const baseSel = sel.slice(0, bracketIdx);
      const attrPart = sel.slice(bracketIdx);
      return this._matchesSingle(node, baseSel) && this._matchesSingle(node, attrPart);
    }
    if (sel.includes(' ')) {
      // Descendant selector
      const subparts = sel.split(/\s+/);
      const last = subparts[subparts.length - 1];
      if (!this._matchesSingle(node, last)) return false;
      let curr = node.parentNode;
      for (let i = subparts.length - 2; i >= 0; i--) {
        const ancestorSel = subparts[i];
        let matched = false;
        while (curr) {
          if (this._matchesSingle(curr, ancestorSel)) {
            matched = true;
            curr = curr.parentNode;
            break;
          }
          curr = curr.parentNode;
        }
        if (!matched) return false;
      }
      return true;
    }
    return node.tagName === sel.toUpperCase();
  }
}

class MockEvent {
  constructor(type, options = {}) {
    this.type = type;
    this.bubbles = !!options.bubbles;
    this.defaultPrevented = false;
    this.propagationStopped = false;
    this.target = null;
    this.currentTarget = null;
    Object.assign(this, options);
  }

  preventDefault() {
    this.defaultPrevented = true;
  }

  stopPropagation() {
    this.propagationStopped = true;
  }
}

class MockDocument extends MockNode {
  constructor() {
    super('#document');
    this.ownerDocument = this;
    this.activeElement = null;
    this.readyState = 'complete';

    this.body = new MockNode('BODY');
    this.body.ownerDocument = this;
    this.body.parentNode = this;
    this.children.push(this.body);
    this.activeElement = this.body;
  }

  createElement(tag) {
    const el = new MockNode(tag);
    el.ownerDocument = this;
    return el;
  }

  getElementById(id) {
    return this.querySelector('#' + id);
  }
}

function buildMockEnvironment(os = 'mac') {
  const doc = new MockDocument();
  const win = {
    innerWidth: 1280,
    innerHeight: 800,
    navigator: {
      platform: os === 'mac' ? 'MacIntel' : (os === 'win' ? 'Win32' : 'Linux x86_64'),
      userAgent: os === 'mac' ? 'Macintosh' : (os === 'win' ? 'Windows' : 'Linux'),
    },
    location: { href: 'http://localhost:8000/' },
    eventListeners: {},
    addEventListener(type, handler) {
      if (!this.eventListeners[type]) this.eventListeners[type] = [];
      this.eventListeners[type].push(handler);
    },
    removeEventListener(type, handler) {
      if (!this.eventListeners[type]) return;
      this.eventListeners[type] = this.eventListeners[type].filter(h => h !== handler);
    },
    dispatchEvent(event) {
      const handlers = this.eventListeners[event.type] || [];
      for (const h of handlers) {
        h.call(this, event);
      }
      return !event.defaultPrevented;
    },
    setTimeout: (fn, ms) => {
      return setTimeout(fn, ms);
    },
    clearTimeout: (id) => clearTimeout(id),
    Event: MockEvent,
    KeyboardEvent: MockEvent,
    MouseEvent: MockEvent,
    CustomEvent: MockEvent,
  };

  doc.defaultView = win;

  // Populate Redesigned App Shell DOM matching templates/base.html
  const appLayout = doc.createElement('div');
  appLayout.setAttribute('id', 'app-layout');
  appLayout.setAttribute('class', 'app-layout');
  doc.body.appendChild(appLayout);

  // 1. Navbar
  const navbar = doc.createElement('header');
  navbar.setAttribute('id', 'app-navbar');
  navbar.setAttribute('class', 'app-navbar');
  appLayout.appendChild(navbar);

  const navToggle = doc.createElement('button');
  navToggle.setAttribute('id', 'mobile-nav-toggle');
  navToggle.setAttribute('class', 'mobile-nav-toggle');
  navToggle.setAttribute('aria-expanded', 'false');
  navbar.appendChild(navToggle);

  const searchTrigger = doc.createElement('div');
  searchTrigger.setAttribute('id', 'global-search-trigger');
  searchTrigger.setAttribute('class', 'header-search-pill');
  navbar.appendChild(searchTrigger);

  const searchBadge = doc.createElement('span');
  searchBadge.setAttribute('id', 'search-kbd-badge');
  searchBadge.setAttribute('class', 'kbd-badge');
  searchTrigger.appendChild(searchBadge);

  const notifBtn = doc.createElement('button');
  notifBtn.setAttribute('id', 'notification-bell');
  notifBtn.setAttribute('class', 'notification-bell-btn');
  navbar.appendChild(notifBtn);

  const notifDropdown = doc.createElement('div');
  notifDropdown.setAttribute('id', 'notification-dropdown');
  notifDropdown.setAttribute('class', 'notification-dropdown-menu');
  navbar.appendChild(notifDropdown);

  const userDropdownContainer = doc.createElement('div');
  userDropdownContainer.setAttribute('id', 'user-pill-dropdown');
  userDropdownContainer.setAttribute('class', 'user-pill-dropdown');
  navbar.appendChild(userDropdownContainer);

  const userTrigger = doc.createElement('button');
  userTrigger.setAttribute('id', 'user-pill-trigger');
  userTrigger.setAttribute('class', 'user-pill-trigger');
  userTrigger.setAttribute('aria-expanded', 'false');
  userDropdownContainer.appendChild(userTrigger);

  const userMenu = doc.createElement('ul');
  userMenu.setAttribute('id', 'user-dropdown-menu');
  userMenu.setAttribute('class', 'user-dropdown-menu');
  userDropdownContainer.appendChild(userMenu);

  // 2. Mobile Drawer & Backdrop
  const sidebar = doc.createElement('aside');
  sidebar.setAttribute('id', 'navigation');
  sidebar.setAttribute('class', 'mobile-drawer app-sidebar');
  appLayout.appendChild(sidebar);

  const sidebarClose = doc.createElement('button');
  sidebarClose.setAttribute('id', 'sidebar-close-btn');
  sidebarClose.setAttribute('class', 'drawer-close-btn');
  sidebar.appendChild(sidebarClose);

  const navList = doc.createElement('ul');
  sidebar.appendChild(navList);

  const linkProblems = doc.createElement('a');
  linkProblems.setAttribute('class', 'sidebar-nav-link nav-problems');
  linkProblems.setAttribute('href', '/problems/');
  navList.appendChild(linkProblems);

  const sidebarBackdrop = doc.createElement('div');
  sidebarBackdrop.setAttribute('id', 'sidebar-backdrop');
  sidebarBackdrop.setAttribute('class', 'sidebar-backdrop drawer-backdrop');
  appLayout.appendChild(sidebarBackdrop);

  // 3. Search Modal Dialog
  const searchModal = doc.createElement('div');
  searchModal.setAttribute('id', 'global-search-modal');
  searchModal.setAttribute('class', 'modal-backdrop search-modal-root');
  searchModal.style.display = 'none';
  doc.body.appendChild(searchModal);

  const searchDialog = doc.createElement('div');
  searchDialog.setAttribute('class', 'search-modal-dialog');
  searchModal.appendChild(searchDialog);

  const searchInput = doc.createElement('input');
  searchInput.setAttribute('id', 'modal-search-input');
  searchInput.setAttribute('class', 'modal-search-input');
  searchDialog.appendChild(searchInput);

  const searchClose = doc.createElement('button');
  searchClose.setAttribute('id', 'modal-search-close');
  searchClose.setAttribute('class', 'modal-search-close');
  searchDialog.appendChild(searchClose);

  const tabChipAll = doc.createElement('button');
  tabChipAll.setAttribute('class', 'search-tab-chip active');
  tabChipAll.setAttribute('data-tab', 'all');
  searchDialog.appendChild(tabChipAll);

  const tabChipProblem = doc.createElement('button');
  tabChipProblem.setAttribute('class', 'search-tab-chip');
  tabChipProblem.setAttribute('data-tab', 'problem');
  searchDialog.appendChild(tabChipProblem);

  const searchResults = doc.createElement('div');
  searchResults.setAttribute('id', 'modal-search-results');
  searchResults.setAttribute('class', 'search-modal-body');
  searchDialog.appendChild(searchResults);

  // 4. Main canvas inputs
  const sampleInput = doc.createElement('input');
  sampleInput.setAttribute('id', 'sample-input');
  doc.body.appendChild(sampleInput);

  const sampleTextarea = doc.createElement('textarea');
  sampleTextarea.setAttribute('id', 'sample-textarea');
  doc.body.appendChild(sampleTextarea);

  // Override global navigator for environment initialization
  const origNav = globalThis.navigator;
  const mockNav = {
    platform: os === 'mac' ? 'MacIntel' : (os === 'win' ? 'Win32' : 'Linux x86_64'),
    userAgent: os === 'mac' ? 'Macintosh' : (os === 'win' ? 'Windows' : 'Linux'),
  };
  try {
    Object.defineProperty(globalThis, 'navigator', { value: mockNav, configurable: true, writable: true });
  } catch (e) {}

  // Execute controller
  const runFn = new Function('window', 'document', scriptSource);
  runFn(win, doc);

  try {
    Object.defineProperty(globalThis, 'navigator', { value: origNav, configurable: true, writable: true });
  } catch (e) {}

  return { doc, win, elements: {
    navbar, navToggle, searchTrigger, searchBadge, notifBtn, notifDropdown,
    userDropdownContainer, userTrigger, userMenu, sidebar, sidebarClose,
    linkProblems, sidebarBackdrop, searchModal, searchDialog, searchInput,
    searchClose, searchResults, tabChipAll, tabChipProblem, sampleInput, sampleTextarea
  }};
}

// ---------------------------------------------------------------------------
// SUITE 1: Mobile Navigation Drawer Controller
// ---------------------------------------------------------------------------
console.log('--- Suite 1: Mobile Navigation Drawer Controller ---');
{
  const { doc, win, elements } = buildMockEnvironment('mac');
  const { navToggle, sidebar, sidebarBackdrop, sidebarClose, linkProblems } = elements;

  // 1.1 Initial state
  check('1.1: Mobile drawer initially closed and aria-expanded is false',
    !sidebar.classList.contains('mobile-open') &&
    !sidebarBackdrop.classList.contains('show') &&
    !doc.body.classList.contains('sidebar-open') &&
    navToggle.getAttribute('aria-expanded') === 'false'
  );

  // 1.2 Click hamburger opens drawer
  navToggle.click();
  check('1.2: Clicking hamburger opens drawer and sets aria-expanded true',
    sidebar.classList.contains('mobile-open') &&
    sidebarBackdrop.classList.contains('show') &&
    doc.body.classList.contains('sidebar-open') &&
    navToggle.getAttribute('aria-expanded') === 'true'
  );

  // 1.3 Click hamburger toggles closed
  navToggle.click();
  check('1.3: Clicking hamburger again toggles drawer closed',
    !sidebar.classList.contains('mobile-open') &&
    !sidebarBackdrop.classList.contains('show') &&
    !doc.body.classList.contains('sidebar-open') &&
    navToggle.getAttribute('aria-expanded') === 'false'
  );

  // 1.4 Backdrop click dismisses drawer
  navToggle.click();
  sidebarBackdrop.click();
  check('1.4: Clicking backdrop closes mobile drawer',
    !sidebar.classList.contains('mobile-open') &&
    !sidebarBackdrop.classList.contains('show')
  );

  // 1.5 Sidebar close button dismisses drawer
  navToggle.click();
  sidebarClose.click();
  check('1.5: Clicking sidebar close button closes mobile drawer',
    !sidebar.classList.contains('mobile-open')
  );

  // 1.6 Escape key dismisses drawer
  navToggle.click();
  win.dispatchEvent(new MockEvent('keydown', { key: 'Escape', bubbles: true }));
  check('1.6: Pressing Escape dismisses mobile drawer',
    !sidebar.classList.contains('mobile-open')
  );

  // 1.7 Clicking nav link on mobile (< 768px) closes drawer
  navToggle.click();
  win.innerWidth = 500;
  linkProblems.click();
  check('1.7: Clicking nav link on mobile (<768px) automatically closes drawer',
    !sidebar.classList.contains('mobile-open')
  );

  // 1.8 Clicking nav link on tablet/desktop (>= 768px) does NOT close drawer
  navToggle.click();
  win.innerWidth = 800;
  linkProblems.click();
  check('1.8: Clicking nav link on viewport >=768px keeps drawer open',
    sidebar.classList.contains('mobile-open')
  );
  sidebarClose.click();

  // 1.9 Touch swipe-left gesture dismisses drawer
  navToggle.click();
  const touchStartEvt = new MockEvent('touchstart', { bubbles: true });
  touchStartEvt.changedTouches = [{ screenX: 250, screenY: 150 }];
  sidebar.dispatchEvent(touchStartEvt);

  const touchEndEvt = new MockEvent('touchend', { bubbles: true });
  touchEndEvt.changedTouches = [{ screenX: 120, screenY: 160 }]; // deltaX = -130 (< -50), deltaY = 10 (< 80)
  sidebar.dispatchEvent(touchEndEvt);
  check('1.9: Touch swipe-left gesture dismisses drawer',
    !sidebar.classList.contains('mobile-open')
  );

  // 1.10 Touch swipe-right gesture does NOT close drawer
  navToggle.click();
  const touchStartR = new MockEvent('touchstart', { bubbles: true });
  touchStartR.changedTouches = [{ screenX: 50, screenY: 150 }];
  sidebar.dispatchEvent(touchStartR);

  const touchEndR = new MockEvent('touchend', { bubbles: true });
  touchEndR.changedTouches = [{ screenX: 200, screenY: 150 }]; // deltaX = 150 (> 0)
  sidebar.dispatchEvent(touchEndR);
  check('1.10: Touch swipe-right does NOT close drawer',
    sidebar.classList.contains('mobile-open')
  );

  // 1.11 Vertical scroll does NOT close drawer
  const touchStartV = new MockEvent('touchstart', { bubbles: true });
  touchStartV.changedTouches = [{ screenX: 250, screenY: 100 }];
  sidebar.dispatchEvent(touchStartV);

  const touchEndV = new MockEvent('touchend', { bubbles: true });
  touchEndV.changedTouches = [{ screenX: 180, screenY: 300 }]; // deltaX = -70, deltaY = 200 (> 80)
  sidebar.dispatchEvent(touchEndV);
  check('1.11: Vertical scroll gesture does NOT close drawer',
    sidebar.classList.contains('mobile-open')
  );
  sidebarClose.click();

  // 1.12 Rapid 100x toggling stress test
  for (let i = 0; i < 100; i++) {
    navToggle.click();
  }
  check('1.12: 100x rapid toggles maintain clean binary state',
    !sidebar.classList.contains('mobile-open') &&
    navToggle.getAttribute('aria-expanded') === 'false'
  );
}

// ---------------------------------------------------------------------------
// SUITE 2: Global ⌘K Quick Search Modal Controller
// ---------------------------------------------------------------------------
console.log('\n--- Suite 2: Global ⌘K Quick Search Modal Controller ---');
{
  // 2.1 Platform keycaps
  const { elements: elMac } = buildMockEnvironment('mac');
  check('2.1a: Mac environment formats ⌘K badge',
    elMac.searchBadge.innerHTML.includes('⌘') && elMac.searchBadge.innerHTML.includes('K')
  );

  const { elements: elWin } = buildMockEnvironment('win');
  check('2.1b: Windows environment formats Ctrl+K badge',
    elWin.searchBadge.innerHTML.includes('Ctrl') && elWin.searchBadge.innerHTML.includes('K')
  );

  // 2.2 Modal Opening Keyboard Shortcuts
  const { doc, win, elements } = buildMockEnvironment('mac');
  const { searchModal, searchTrigger, searchClose, searchInput, searchResults,
          tabChipAll, tabChipProblem, sampleInput, sampleTextarea } = elements;

  // 2.2a ⌘K on Mac opens modal
  win.dispatchEvent(new MockEvent('keydown', { key: 'k', metaKey: true, bubbles: true }));
  check('2.2a: ⌘K opens search modal (display: flex, class: is-open, aria-hidden: false)',
    searchModal.style.display === 'flex' &&
    searchModal.classList.contains('is-open') &&
    searchModal.getAttribute('aria-hidden') === 'false' &&
    doc.body.classList.contains('modal-open')
  );

  // 2.2b ⌘K toggles closed
  win.dispatchEvent(new MockEvent('keydown', { key: 'k', metaKey: true, bubbles: true }));
  check('2.2b: ⌘K toggles search modal closed',
    searchModal.style.display === 'none' &&
    !searchModal.classList.contains('is-open') &&
    searchModal.getAttribute('aria-hidden') === 'true' &&
    !doc.body.classList.contains('modal-open')
  );

  // 2.2c Ctrl+K on Windows opens modal
  const envWin = buildMockEnvironment('win');
  envWin.win.dispatchEvent(new MockEvent('keydown', { key: 'k', ctrlKey: true, bubbles: true }));
  check('2.2c: Ctrl+K on Windows opens search modal',
    envWin.elements.searchModal.style.display === 'flex'
  );

  // 2.2d '/' outside input opens modal
  doc.activeElement = doc.body;
  win.dispatchEvent(new MockEvent('keydown', { key: '/', bubbles: true }));
  check('2.2d: "/" key outside text inputs opens modal',
    searchModal.style.display === 'flex'
  );
  searchClose.click();

  // 2.2e '/' inside input does NOT trigger modal
  sampleInput.focus();
  win.dispatchEvent(new MockEvent('keydown', { key: '/', bubbles: true }));
  check('2.2e: "/" key inside <input> does NOT trigger search modal',
    searchModal.style.display === 'none'
  );

  // 2.2f '/' inside textarea does NOT trigger modal
  sampleTextarea.focus();
  win.dispatchEvent(new MockEvent('keydown', { key: '/', bubbles: true }));
  check('2.2f: "/" key inside <textarea> does NOT trigger search modal',
    searchModal.style.display === 'none'
  );

  // 2.2g Clicking search pill opens modal
  searchTrigger.click();
  check('2.2g: Clicking header search pill opens modal',
    searchModal.style.display === 'flex'
  );

  // 2.3 Dismissal
  searchClose.click();
  check('2.3a: Clicking close button dismisses modal',
    searchModal.style.display === 'none'
  );

  searchTrigger.click();
  win.dispatchEvent(new MockEvent('keydown', { key: 'Escape', bubbles: true }));
  check('2.3b: Pressing Escape dismisses modal',
    searchModal.style.display === 'none'
  );

  searchTrigger.click();
  searchModal.click();
  check('2.3c: Clicking modal backdrop dismisses modal',
    searchModal.style.display === 'none'
  );

  // 2.4 Search results rendering & filtering
  searchTrigger.click();
  check('2.4a: Initial empty search displays Quick Navigation section',
    searchResults.innerHTML.includes('Quick Navigation')
  );

  searchInput.value = 'A Plus B';
  searchInput.dispatchEvent(new MockEvent('input', { bubbles: true }));
  check('2.4b: Typing problem query filters and highlights match with <mark>',
    searchResults.textContent.includes('A Plus B') &&
    searchResults.innerHTML.includes('<mark>A Plus B</mark>')
  );

  searchInput.value = 'monthly';
  searchInput.dispatchEvent(new MockEvent('input', { bubbles: true }));
  check('2.4c: Typing contest query finds DMOJ Monthly Contest',
    searchResults.textContent.includes('Monthly')
  );

  searchInput.value = 'tourist';
  searchInput.dispatchEvent(new MockEvent('input', { bubbles: true }));
  check('2.4d: Typing user query finds tourist',
    searchResults.textContent.includes('tourist')
  );

  searchInput.value = 'nonexistent_impossible_query_999';
  searchInput.dispatchEvent(new MockEvent('input', { bubbles: true }));
  check('2.4e: Zero results renders graceful empty state',
    searchResults.innerHTML.includes('No matching results found')
  );

  // 2.5 Category tab filtering
  searchInput.value = '';
  searchInput.dispatchEvent(new MockEvent('input', { bubbles: true }));
  tabChipProblem.click();
  check('2.5: Category tab filter sets activeTab to problem',
    win.DmojAppShell.getState().activeTab === 'problem' &&
    tabChipProblem.classList.contains('active')
  );

  // 2.6 Keyboard navigation in search results
  const resultRows = searchResults.querySelectorAll('.search-result-row');
  check('2.6a: Initial search item is selected',
    resultRows.length > 0 && resultRows[0].classList.contains('is-selected')
  );

  win.dispatchEvent(new MockEvent('keydown', { key: 'ArrowDown', bubbles: true }));
  check('2.6b: ArrowDown navigates selection to second item',
    win.DmojAppShell.getState().selectedIndex === 1 &&
    resultRows[1].classList.contains('is-selected')
  );

  win.dispatchEvent(new MockEvent('keydown', { key: 'ArrowUp', bubbles: true }));
  check('2.6c: ArrowUp navigates selection back to first item',
    win.DmojAppShell.getState().selectedIndex === 0 &&
    resultRows[0].classList.contains('is-selected')
  );

  // 2.7 Enter key navigation
  win.dispatchEvent(new MockEvent('keydown', { key: 'Enter', bubbles: true }));
  check('2.7: Enter key navigates window.location.href to selected item URL',
    win.location.href.includes('/problem/')
  );

  // 2.8 Adversarial injection stress
  searchInput.value = '<script>alert("xss")</script> [.*+?^${}()|[\\]\\\\]';
  let injectionThrew = false;
  try {
    searchInput.dispatchEvent(new MockEvent('input', { bubbles: true }));
  } catch (err) {
    injectionThrew = true;
  }
  check('2.8a: HTML tags & regex metacharacters sanitized without runtime error',
    !injectionThrew && !searchResults.innerHTML.includes('<script>alert')
  );

  // 2.9 Wrap-around navigation
  win.DmojAppShell.openSearch();
  searchInput.value = '';
  tabChipAll.click();
  const allRows = searchResults.querySelectorAll('.search-result-row');
  check('2.9a: Initial index is 0', win.DmojAppShell.getState().selectedIndex === 0);
  win.dispatchEvent(new MockEvent('keydown', { key: 'ArrowUp', bubbles: true }));
  check(`2.9b: ArrowUp from index 0 wraps to last item (index ${allRows.length - 1})`,
    win.DmojAppShell.getState().selectedIndex === allRows.length - 1
  );
  win.dispatchEvent(new MockEvent('keydown', { key: 'ArrowDown', bubbles: true }));
  check('2.9c: ArrowDown from last item wraps back to index 0',
    win.DmojAppShell.getState().selectedIndex === 0
  );

  // 2.10 Navigation with empty results
  searchInput.value = 'zzz_no_match';
  searchInput.dispatchEvent(new MockEvent('input', { bubbles: true }));
  let emptyNavThrew = false;
  try {
    win.dispatchEvent(new MockEvent('keydown', { key: 'ArrowDown', bubbles: true }));
    win.dispatchEvent(new MockEvent('keydown', { key: 'ArrowUp', bubbles: true }));
    win.dispatchEvent(new MockEvent('keydown', { key: 'Enter', bubbles: true }));
  } catch (err) {
    emptyNavThrew = true;
  }
  check('2.10: ArrowDown/Up/Enter on empty search results does not throw', !emptyNavThrew);
  win.DmojAppShell.closeSearch();
}

// ---------------------------------------------------------------------------
// SUITE 3: User Profile Dropdown Menu Controller
// ---------------------------------------------------------------------------
console.log('\n--- Suite 3: User Profile Dropdown Menu Controller ---');
{
  const { doc, win, elements } = buildMockEnvironment('mac');
  const { userTrigger, userMenu, userDropdownContainer } = elements;

  // 3.1 Initial state
  check('3.1: User dropdown initially hidden and aria-expanded is false',
    !userMenu.classList.contains('show') &&
    !userDropdownContainer.classList.contains('dropdown-open') &&
    userTrigger.getAttribute('aria-expanded') === 'false'
  );

  // 3.2 Click trigger opens menu
  userTrigger.click();
  check('3.2: Clicking trigger opens menu, sets .show, .dropdown-open and aria-expanded true',
    userMenu.classList.contains('show') &&
    userDropdownContainer.classList.contains('dropdown-open') &&
    userTrigger.getAttribute('aria-expanded') === 'true'
  );

  // 3.3 Click trigger toggles closed
  userTrigger.click();
  check('3.3: Clicking trigger again closes menu',
    !userMenu.classList.contains('show') &&
    !userDropdownContainer.classList.contains('dropdown-open') &&
    userTrigger.getAttribute('aria-expanded') === 'false'
  );

  // 3.4 Outside click dismisses menu
  userTrigger.click();
  doc.dispatchEvent(new MockEvent('click', { bubbles: true, target: doc.body }));
  check('3.4: Clicking outside dismisses user dropdown menu',
    !userMenu.classList.contains('show')
  );

  // 3.5 Escape key dismisses menu
  userTrigger.click();
  win.dispatchEvent(new MockEvent('keydown', { key: 'Escape', bubbles: true }));
  check('3.5: Pressing Escape dismisses user dropdown menu',
    !userMenu.classList.contains('show')
  );

  // 3.6 Opening drawer closes user dropdown
  userTrigger.click();
  elements.navToggle.click();
  check('3.6: Opening mobile drawer automatically closes user dropdown',
    !userMenu.classList.contains('show')
  );
  elements.navToggle.click();

  // 3.7 Opening search modal closes user dropdown
  userTrigger.click();
  elements.searchTrigger.click();
  check('3.7: Opening search modal automatically closes user dropdown',
    !userMenu.classList.contains('show')
  );
}

// ---------------------------------------------------------------------------
// SUITE 4: Notification Bell Popover Controller
// ---------------------------------------------------------------------------
console.log('\n--- Suite 4: Notification Bell Popover Controller ---');
{
  const { doc, win, elements } = buildMockEnvironment('mac');
  const { notifBtn, notifDropdown, userTrigger, userMenu } = elements;

  // 4.1 Initial state
  check('4.1: Notification popover initially hidden',
    !notifDropdown.classList.contains('show')
  );

  // 4.2 Click notification bell opens popover
  notifBtn.click();
  check('4.2: Clicking notification bell opens popover and sets aria-expanded true',
    notifDropdown.classList.contains('show') &&
    notifBtn.getAttribute('aria-expanded') === 'true'
  );

  // 4.3 Click again closes popover
  notifBtn.click();
  check('4.3: Clicking notification bell again closes popover',
    !notifDropdown.classList.contains('show') &&
    notifBtn.getAttribute('aria-expanded') === 'false'
  );

  // 4.4 Click outside dismisses popover
  notifBtn.click();
  doc.dispatchEvent(new MockEvent('click', { bubbles: true, target: doc.body }));
  check('4.4: Clicking outside dismisses notification popover',
    !notifDropdown.classList.contains('show')
  );

  // 4.5 Opening notification popover closes user dropdown
  userTrigger.click();
  check('4.5a: User dropdown opened', userMenu.classList.contains('show'));
  notifBtn.click();
  check('4.5b: Opening notification popover closes user dropdown',
    !userMenu.classList.contains('show') &&
    notifDropdown.classList.contains('show')
  );
}

// ---------------------------------------------------------------------------
// SUITE 5: Global API & Window Export (window.DmojAppShell)
// ---------------------------------------------------------------------------
console.log('\n--- Suite 5: Global API & Window Export (window.DmojAppShell) ---');
{
  const { doc, win, elements } = buildMockEnvironment('mac');
  const api = win.DmojAppShell;

  check('5.1: window.DmojAppShell is exported',
    typeof api === 'object' && api !== null
  );

  // Search API
  api.openSearch();
  check('5.2a: DmojAppShell.openSearch() opens modal',
    api.getState().searchModalOpen === true &&
    elements.searchModal.style.display === 'flex'
  );

  api.closeSearch();
  check('5.2b: DmojAppShell.closeSearch() closes modal',
    api.getState().searchModalOpen === false &&
    elements.searchModal.style.display === 'none'
  );

  // Drawer API
  api.openDrawer();
  check('5.3a: DmojAppShell.openDrawer() opens drawer',
    api.getState().drawerOpen === true &&
    elements.sidebar.classList.contains('mobile-open')
  );

  api.closeDrawer();
  check('5.3b: DmojAppShell.closeDrawer() closes drawer',
    api.getState().drawerOpen === false &&
    !elements.sidebar.classList.contains('mobile-open')
  );

  api.toggleDrawer();
  check('5.3c: DmojAppShell.toggleDrawer() toggles drawer open',
    api.getState().drawerOpen === true
  );
  api.toggleDrawer();
  check('5.3d: DmojAppShell.toggleDrawer() toggles drawer closed',
    api.getState().drawerOpen === false
  );

  // User menu API
  api.toggleUserMenu();
  check('5.4a: DmojAppShell.toggleUserMenu() toggles menu open',
    api.getState().userDropdownOpen === true &&
    elements.userMenu.classList.contains('show')
  );
  api.toggleUserMenu();
  check('5.4b: DmojAppShell.toggleUserMenu() toggles menu closed',
    api.getState().userDropdownOpen === false
  );

  // 5.5 State immutability check
  const stateCopy = api.getState();
  stateCopy.drawerOpen = true;
  stateCopy.searchModalOpen = true;
  check('5.5: getState() returns an immutable copy (mutations do not corrupt internal state)',
    api.getState().drawerOpen === false &&
    api.getState().searchModalOpen === false
  );
}

// ---------------------------------------------------------------------------
// SUITE 6: Fault Tolerance & Missing DOM Elements
// ---------------------------------------------------------------------------
console.log('\n--- Suite 6: Fault Tolerance & Missing Elements ---');
{
  const emptyDoc = new MockDocument();
  const emptyWin = {
    innerWidth: 1024,
    innerHeight: 768,
    navigator: { platform: 'Linux', userAgent: 'Linux' },
    location: { href: 'http://localhost/' },
    eventListeners: {},
    addEventListener(type, h) { (this.eventListeners[type] = this.eventListeners[type] || []).push(h); },
    removeEventListener() {},
    dispatchEvent(e) {
      (this.eventListeners[e.type] || []).forEach(h => h.call(this, e));
      return true;
    },
    setTimeout: (fn) => setTimeout(fn, 0),
    clearTimeout: () => {},
    Event: MockEvent,
    KeyboardEvent: MockEvent,
    MouseEvent: MockEvent,
    CustomEvent: MockEvent,
  };

  let initThrew = false;
  try {
    const runFn = new Function('window', 'document', scriptSource);
    runFn(emptyWin, emptyDoc);
  } catch (err) {
    initThrew = true;
    console.error('Crash on empty DOM:', err);
  }
  check('6.1: Initializing script on completely empty DOM does not crash', !initThrew);

  let eventsThrew = false;
  try {
    emptyWin.dispatchEvent(new MockEvent('keydown', { key: 'Escape', bubbles: true }));
    emptyWin.dispatchEvent(new MockEvent('keydown', { key: 'k', metaKey: true, bubbles: true }));
    emptyWin.dispatchEvent(new MockEvent('keydown', { key: '/', bubbles: true }));
    emptyDoc.dispatchEvent(new MockEvent('click', { bubbles: true }));
    emptyWin.DmojAppShell.openSearch();
    emptyWin.DmojAppShell.closeSearch();
    emptyWin.DmojAppShell.openDrawer();
    emptyWin.DmojAppShell.closeDrawer();
    emptyWin.DmojAppShell.toggleDrawer();
    emptyWin.DmojAppShell.toggleUserMenu();
  } catch (err) {
    eventsThrew = true;
    console.error('Crash during events on empty DOM:', err);
  }
  check('6.2: Calling handlers and triggering keyboard/click events with missing DOM does not throw', !eventsThrew);
}

// ---------------------------------------------------------------------------
// SUITE 7: Asynchronous Interaction Timing & Delegation
// ---------------------------------------------------------------------------
async function runAsyncSuite() {
  console.log('\n--- Suite 7: Asynchronous Interaction Timing & Delegation ---');
  const { doc, win, elements } = buildMockEnvironment('mac');
  const { navToggle, sidebar, userTrigger, userMenu, userDropdownContainer } = elements;

  // 7.1 Debounced resize auto-closing open drawer
  win.innerWidth = 700;
  navToggle.click();
  check('7.1a: Drawer open on mobile width (700px)', sidebar.classList.contains('mobile-open'));

  win.innerWidth = 1200;
  win.dispatchEvent(new MockEvent('resize'));
  // Drawer still open before debounce elapses
  check('7.1b: Drawer immediately remains open before debounce timeout', sidebar.classList.contains('mobile-open'));

  // Wait 150ms for resize debounce (100ms) to trigger
  await new Promise(r => setTimeout(r, 150));
  check('7.1c: Drawer auto-closes after resize debounce timeout elapses on >=1024px',
    !sidebar.classList.contains('mobile-open') && win.DmojAppShell.getState().drawerOpen === false
  );

  // 7.2 Event delegation on child elements inside triggers
  const childSpan = doc.createElement('span');
  childSpan.setAttribute('class', 'user-pill-name');
  childSpan.textContent = 'tourist';
  userTrigger.appendChild(childSpan);

  // Click child element directly
  childSpan.click();
  check('7.2a: Clicking child element inside userTrigger successfully opens dropdown',
    userMenu.classList.contains('show') && userDropdownContainer.classList.contains('dropdown-open')
  );

  childSpan.click();
  check('7.2b: Clicking child element inside userTrigger again successfully closes dropdown',
    !userMenu.classList.contains('show')
  );

  // 7.3 Click inside open menu does NOT close menu
  userTrigger.click();
  const menuItem = doc.createElement('li');
  userMenu.appendChild(menuItem);
  menuItem.click();
  check('7.3: Clicking inside user dropdown menu does not dismiss dropdown',
    userMenu.classList.contains('show')
  );
  doc.dispatchEvent(new MockEvent('click', { bubbles: true, target: doc.body }));
  check('7.4: Clicking document body dismisses dropdown',
    !userMenu.classList.contains('show')
  );
}

runAsyncSuite().then(() => {
  console.log('\n======================================================================');
  console.log(`TOTAL TESTS: ${passed + failed} | PASSED: ${passed} | FAILED: ${failed}`);
  console.log('======================================================================\n');

  if (failed > 0) {
    process.exit(1);
  } else {
    process.exit(0);
  }
}).catch(err => {
  console.error('Async suite error:', err);
  process.exit(1);
});
