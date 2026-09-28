/**
 * test_m2_interactive_shell.js
 * Empirical Challenger Test Harness for Milestone 2: App Shell Controller Interactions
 *
 * Runs in Node.js with JSDOM to test the exact script resources/app-shell-controller.js
 */

const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const REPO_ROOT = path.resolve(__dirname, '..');
const SCRIPT_PATH = path.join(REPO_ROOT, 'resources', 'app-shell-controller.js');
const scriptSource = fs.readFileSync(SCRIPT_PATH, 'utf-8');

// HTML template simulating base.html shell DOM
const HTML_TEMPLATE = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>DMOJ App Shell Test</title>
</head>
<body>
  <div class="desktop-wallpaper">
    <div class="mac-app-window mac-window" id="mac-app-window">
      <header class="mac-window-topbar" id="window-topbar">
        <div class="topbar-left">
          <div class="traffic-lights" aria-label="Window controls">
            <span class="traffic-light traffic-red" id="traffic-light-close" title="Close"></span>
            <span class="traffic-light traffic-yellow" id="traffic-light-min" title="Minimize"></span>
            <span class="traffic-light traffic-green" id="traffic-light-max" title="Maximize"></span>
          </div>
          <button type="button" class="mobile-nav-toggle" id="mobile-nav-toggle" aria-label="Toggle navigation">
            <i class="fa fa-bars"></i>
          </button>
        </div>

        <div class="topbar-right">
          <div class="header-search-wrap">
            <div class="header-search-pill" id="global-search-trigger" role="button" tabindex="0">
              <span class="kbd-badge" id="search-kbd-badge"><kbd>⌘</kbd><kbd>K</kbd></span>
            </div>
          </div>

          <div class="header-action-item">
            <button type="button" class="header-icon-btn notification-bell-btn" id="notification-bell">
              <i class="fa fa-bell-o"></i>
            </button>
            <div id="notification-dropdown" class="notification-dropdown-menu"></div>
          </div>

          <div id="user-links" class="header-user-menu">
            <div class="user-pill-dropdown" id="user-pill-dropdown">
              <button type="button" class="user-pill-trigger" id="user-pill-trigger" aria-haspopup="true" aria-expanded="false">
                <span class="user-pill-name">tourist</span>
              </button>
              <ul class="user-dropdown-menu" id="user-dropdown-menu" role="menu">
                <li><a href="/user/" class="dropdown-item">Profile</a></li>
                <li><a href="/user/edit/" class="dropdown-item">Edit profile</a></li>
              </ul>
            </div>
          </div>
        </div>
      </header>

      <div class="mac-window-body">
        <aside id="navigation" class="app-sidebar" role="navigation">
          <div class="sidebar-brand">
            <a href="/" class="sidebar-brand-link">DMOJ</a>
          </div>
          <ul id="nav-list" class="sidebar-nav-list">
            <li class="sidebar-nav-item"><a href="/" class="sidebar-nav-link nav-home">Dashboard</a></li>
            <li class="sidebar-nav-item"><a href="/problems/" class="sidebar-nav-link nav-problems">Problems</a></li>
            <li class="sidebar-nav-item"><a href="/submissions/" class="sidebar-nav-link nav-submissions">Submissions</a></li>
          </ul>
          <button id="sidebar-close-btn" class="sidebar-close-btn">Close</button>
        </aside>

        <div class="sidebar-backdrop" id="sidebar-backdrop" aria-hidden="true"></div>

        <div class="app-main-viewport" id="app-main-viewport">
          <main id="content" class="app-content-area">
            <input type="text" id="sample-text-input" placeholder="Sample Input">
            <textarea id="sample-textarea">Sample Textarea</textarea>
            <div id="content-body">Hello World</div>
          </main>
        </div>
      </div>
    </div>
  </div>

  <div id="global-search-modal" class="mac-modal-backdrop" style="display: none;" aria-hidden="true" role="dialog" aria-modal="true">
    <div class="mac-modal-dialog search-modal-dialog">
      <div class="search-modal-header">
        <input type="text" id="modal-search-input" class="modal-search-input" placeholder="Search...">
        <button type="button" class="modal-search-close" id="modal-search-close"><kbd>ESC</kbd></button>
      </div>
      <div class="search-modal-tabs">
        <button class="search-tab-chip active" data-tab="all">All</button>
        <button class="search-tab-chip" data-tab="problem">Problems</button>
        <button class="search-tab-chip" data-tab="contest">Contests</button>
        <button class="search-tab-chip" data-tab="user">Users</button>
      </div>
      <div class="search-modal-body" id="modal-search-results"></div>
    </div>
  </div>
</body>
</html>
`;

let passedCount = 0;
let failedCount = 0;
const results = [];

function assert(condition, testName, detail = '') {
  if (condition) {
    passedCount++;
    console.log(`  [PASS] ${testName}`);
    results.push({ name: testName, status: 'PASS', detail });
  } else {
    failedCount++;
    console.error(`  [FAIL] ${testName} - ${detail}`);
    results.push({ name: testName, status: 'FAIL', detail });
  }
}

function createTestEnv(os = 'mac') {
  const dom = new JSDOM(HTML_TEMPLATE, {
    runScripts: 'outside-only',
    url: 'http://localhost:8000/',
  });

  const { window } = dom;
  const { document } = window;

  const isMac = os === 'mac';
  Object.defineProperty(window.navigator, 'platform', {
    value: isMac ? 'MacIntel' : 'Win32',
    configurable: true,
  });
  Object.defineProperty(window.navigator, 'userAgent', {
    value: isMac
      ? 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
      : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    configurable: true,
  });

  // Mock Element.scrollIntoView which JSDOM doesn't implement
  window.Element.prototype.scrollIntoView = function () {};

  // Execute controller script inside window
  window.eval(scriptSource);

  // Trigger DOMContentLoaded
  document.dispatchEvent(new window.Event('DOMContentLoaded'));

  return { dom, window, document };
}

console.log('===============================================================');
console.log('RUNNING EMPIRICAL TESTS: resources/app-shell-controller.js');
console.log('===============================================================\n');

// ---------------------------------------------------------------------------
// SUITE 1: Keyboard Shortcuts & Quick Search Modal (⌘K, /, Escape)
// ---------------------------------------------------------------------------
console.log('--- Suite 1: Keyboard Shortcuts & Quick Search Modal ---');
{
  // Test 1.1: Platform keycap badge formatting on Mac
  const { document: docMac } = createTestEnv('mac');
  const badgeMac = docMac.getElementById('search-kbd-badge');
  assert(badgeMac.innerHTML.includes('⌘') && badgeMac.innerHTML.includes('K'),
    'Test 1.1: Mac displays ⌘K badge');

  // Test 1.2: Platform keycap badge formatting on Windows
  const { document: docWin } = createTestEnv('win');
  const badgeWin = docWin.getElementById('search-kbd-badge');
  assert(badgeWin.innerHTML.includes('Ctrl') && badgeWin.innerHTML.includes('K'),
    'Test 1.2: Windows displays Ctrl+K badge');

  // Test 1.3: ⌘K on Mac opens search modal
  const { window, document } = createTestEnv('mac');
  const modal = document.getElementById('global-search-modal');

  assert(modal.style.display === 'none', 'Test 1.3a: Search modal initially closed');

  window.dispatchEvent(new window.KeyboardEvent('keydown', {
    key: 'k',
    metaKey: true,
    bubbles: true,
  }));
  assert(modal.style.display === 'flex' && modal.classList.contains('is-open') && modal.getAttribute('aria-hidden') === 'false',
    'Test 1.3b: ⌘K opens search modal (display: flex, class: is-open, aria-hidden: false)');
  assert(document.body.classList.contains('modal-open'),
    'Test 1.3c: Body receives modal-open class when search modal opens');

  // Test 1.4: ⌘K while open closes search modal
  window.dispatchEvent(new window.KeyboardEvent('keydown', {
    key: 'k',
    metaKey: true,
    bubbles: true,
  }));
  assert(modal.style.display === 'none' && !modal.classList.contains('is-open'),
    'Test 1.4: ⌘K toggles search modal closed');

  // Test 1.5: Ctrl+K on Windows opens search modal
  const { window: winWindow, document: winDoc } = createTestEnv('win');
  const winModal = winDoc.getElementById('global-search-modal');
  winWindow.dispatchEvent(new winWindow.KeyboardEvent('keydown', {
    key: 'k',
    ctrlKey: true,
    bubbles: true,
  }));
  assert(winModal.style.display === 'flex' && winModal.classList.contains('is-open'),
    'Test 1.5: Ctrl+K on Windows opens search modal');

  // Test 1.6: '/' key opens modal when outside input
  window.dispatchEvent(new window.KeyboardEvent('keydown', {
    key: '/',
    bubbles: true,
  }));
  assert(modal.style.display === 'flex', 'Test 1.6a: "/" opens modal when outside inputs');

  // Test 1.7: Escape key closes modal
  window.dispatchEvent(new window.KeyboardEvent('keydown', {
    key: 'Escape',
    bubbles: true,
  }));
  assert(modal.style.display === 'none', 'Test 1.7: Escape dismisses modal');

  // Test 1.8: '/' inside input/textarea does NOT trigger search modal
  const sampleInput = document.getElementById('sample-text-input');
  sampleInput.focus();
  window.dispatchEvent(new window.KeyboardEvent('keydown', {
    key: '/',
    bubbles: true,
  }));
  assert(modal.style.display === 'none', 'Test 1.8a: "/" inside <input> does NOT trigger modal');

  const sampleTextarea = document.getElementById('sample-textarea');
  sampleTextarea.focus();
  window.dispatchEvent(new window.KeyboardEvent('keydown', {
    key: '/',
    bubbles: true,
  }));
  assert(modal.style.display === 'none', 'Test 1.8b: "/" inside <textarea> does NOT trigger modal');

  // Reset focus to body
  document.body.focus();

  // Test 1.9: Click on search pill opens modal
  const searchPill = document.getElementById('global-search-trigger');
  searchPill.click();
  assert(modal.style.display === 'flex', 'Test 1.9: Clicking header search pill opens modal');

  // Test 1.10: Click on modal close button closes modal
  const closeBtn = document.getElementById('modal-search-close');
  closeBtn.click();
  assert(modal.style.display === 'none', 'Test 1.10: Clicking close button (ESC) dismisses modal');

  // Test 1.11: Click on backdrop closes modal
  searchPill.click();
  assert(modal.style.display === 'flex', 'Test 1.11a: Modal re-opened');
  modal.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
  assert(modal.style.display === 'none', 'Test 1.11b: Clicking modal backdrop dismisses modal');
}

// ---------------------------------------------------------------------------
// SUITE 2: Search Input Filtering, Category Tabs & Keyboard Navigation
// ---------------------------------------------------------------------------
console.log('\n--- Suite 2: Search Input Filtering & Navigation ---');
{
  const { window, document } = createTestEnv('mac');
  const searchPill = document.getElementById('global-search-trigger');
  const searchInput = document.getElementById('modal-search-input');
  const searchResults = document.getElementById('modal-search-results');

  searchPill.click();

  // Test 2.1: Initial empty search displays default quick navigation
  assert(searchResults.innerHTML.includes('Quick Navigation'),
    'Test 2.1: Empty query displays Quick Navigation section');
  assert(searchResults.querySelectorAll('.search-result-row').length > 0,
    'Test 2.2: Initial search results rendered');

  // Test 2.3: Typing a problem title filters results and highlights query
  searchInput.value = 'binary search';
  searchInput.dispatchEvent(new window.Event('input', { bubbles: true }));
  const bstTextMatch = searchResults.textContent.includes('Binary Search Tree Balancing');
  const bstHighlightMatch = searchResults.innerHTML.includes('<mark>Binary Search</mark>');
  assert(bstTextMatch && bstHighlightMatch,
    'Test 2.3: Typing query filters matching problem and applies <mark> highlighting');

  // Test 2.4: Query with no results shows empty state
  searchInput.value = 'xyznonexistentquery999';
  searchInput.dispatchEvent(new window.Event('input', { bubbles: true }));
  assert(searchResults.innerHTML.includes('No matching results found'),
    'Test 2.4: No matches shows graceful empty state message');

  // Test 2.5: Category tab switching
  searchInput.value = '';
  searchInput.dispatchEvent(new window.Event('input', { bubbles: true }));

  const problemTab = document.querySelector('.search-tab-chip[data-tab="problem"]');
  problemTab.click();
  assert(window.DmojAppShell.getState().activeTab === 'problem',
    'Test 2.5a: Category tab switches activeTab to problem');

  // Test 2.6: Arrow down / Arrow up keyboard navigation
  const rows = searchResults.querySelectorAll('.search-result-row');
  assert(rows.length > 0, 'Test 2.6a: Search result rows exist');
  assert(rows[0].classList.contains('is-selected'), 'Test 2.6b: First item selected by default');

  window.dispatchEvent(new window.KeyboardEvent('keydown', { key: 'ArrowDown', bubbles: true }));
  assert(window.DmojAppShell.getState().selectedIndex === 1,
    'Test 2.6c: ArrowDown increments selectedIndex to 1');
  assert(rows[1].classList.contains('is-selected'), 'Test 2.6d: Second item receives is-selected class');

  window.dispatchEvent(new window.KeyboardEvent('keydown', { key: 'ArrowUp', bubbles: true }));
  assert(window.DmojAppShell.getState().selectedIndex === 0,
    'Test 2.6e: ArrowUp decrements selectedIndex back to 0');
  assert(rows[0].classList.contains('is-selected'), 'Test 2.6f: First item receives is-selected class');
}

// ---------------------------------------------------------------------------
// SUITE 3: Mobile Hamburger Drawer Navigation & Touch Dismissal
// ---------------------------------------------------------------------------
console.log('\n--- Suite 3: Mobile Hamburger Drawer Navigation ---');
{
  const { window, document } = createTestEnv('mac');
  const hamburger = document.getElementById('mobile-nav-toggle');
  const sidebar = document.getElementById('navigation');
  const backdrop = document.getElementById('sidebar-backdrop');

  // Test 3.1: Clicking hamburger opens drawer
  assert(!sidebar.classList.contains('mobile-open'), 'Test 3.1a: Sidebar initially closed');
  hamburger.click();
  assert(sidebar.classList.contains('mobile-open'), 'Test 3.1b: Sidebar receives mobile-open');
  assert(backdrop.classList.contains('show'), 'Test 3.1c: Backdrop receives show class');
  assert(document.body.classList.contains('sidebar-open'), 'Test 3.1d: Body receives sidebar-open');
  assert(hamburger.getAttribute('aria-expanded') === 'true', 'Test 3.1e: Hamburger aria-expanded is true');

  // Test 3.2: Clicking hamburger again toggles drawer closed
  hamburger.click();
  assert(!sidebar.classList.contains('mobile-open'), 'Test 3.2a: Sidebar mobile-open removed');
  assert(!backdrop.classList.contains('show'), 'Test 3.2b: Backdrop show removed');
  assert(!document.body.classList.contains('sidebar-open'), 'Test 3.2c: Body sidebar-open removed');
  assert(hamburger.getAttribute('aria-expanded') === 'false', 'Test 3.2d: Hamburger aria-expanded is false');

  // Test 3.3: Backdrop click dismisses drawer
  hamburger.click();
  assert(sidebar.classList.contains('mobile-open'), 'Test 3.3a: Drawer re-opened');
  backdrop.click();
  assert(!sidebar.classList.contains('mobile-open'), 'Test 3.3b: Backdrop click dismisses drawer');

  // Test 3.4: Sidebar close button dismisses drawer
  hamburger.click();
  const sidebarClose = document.getElementById('sidebar-close-btn');
  sidebarClose.click();
  assert(!sidebar.classList.contains('mobile-open'), 'Test 3.4: Sidebar close button dismisses drawer');

  // Test 3.5: Navigating via sidebar link in mobile view (< 768px) closes drawer
  hamburger.click();
  window.innerWidth = 600;
  const navLink = document.querySelector('.sidebar-nav-link.nav-problems');
  navLink.click();
  assert(!sidebar.classList.contains('mobile-open'), 'Test 3.5: Clicking nav link on mobile closes drawer');

  // Test 3.6: Touch swipe-left gesture dismisses drawer
  hamburger.click();
  assert(sidebar.classList.contains('mobile-open'), 'Test 3.6a: Drawer opened before swipe');

  // Simulate touchstart at screenX = 220, screenY = 200
  const touchStartEvt = new window.CustomEvent('touchstart', { bubbles: true });
  touchStartEvt.changedTouches = [{ screenX: 220, screenY: 200 }];
  sidebar.dispatchEvent(touchStartEvt);

  // Simulate touchend at screenX = 100 (deltaX = -120 < -50), screenY = 210 (deltaY = 10 < 80)
  const touchEndEvt = new window.CustomEvent('touchend', { bubbles: true });
  touchEndEvt.changedTouches = [{ screenX: 100, screenY: 210 }];
  sidebar.dispatchEvent(touchEndEvt);

  assert(!sidebar.classList.contains('mobile-open'),
    'Test 3.6b: Touch swipe-left gesture successfully dismisses mobile drawer');

  // Test 3.7: Touch swipe-right does NOT close drawer
  hamburger.click();
  assert(sidebar.classList.contains('mobile-open'), 'Test 3.7a: Drawer opened');
  const touchStartRight = new window.CustomEvent('touchstart', { bubbles: true });
  touchStartRight.changedTouches = [{ screenX: 100, screenY: 200 }];
  sidebar.dispatchEvent(touchStartRight);

  const touchEndRight = new window.CustomEvent('touchend', { bubbles: true });
  touchEndRight.changedTouches = [{ screenX: 200, screenY: 200 }];
  sidebar.dispatchEvent(touchEndRight);
  assert(sidebar.classList.contains('mobile-open'),
    'Test 3.7b: Touch swipe-right does NOT close drawer');
}

// ---------------------------------------------------------------------------
// SUITE 4: User Profile Dropdown & Outside Click Dismissal
// ---------------------------------------------------------------------------
console.log('\n--- Suite 4: User Profile Dropdown Menu ---');
{
  const { window, document } = createTestEnv('mac');
  const trigger = document.getElementById('user-pill-trigger');
  const menu = document.getElementById('user-dropdown-menu');
  const container = document.getElementById('user-pill-dropdown');

  // Test 4.1: Initial state
  assert(!menu.classList.contains('show'), 'Test 4.1a: Dropdown menu initially hidden');
  assert(trigger.getAttribute('aria-expanded') === 'false', 'Test 4.1b: Trigger aria-expanded is false');

  // Test 4.2: Click trigger opens menu
  trigger.click();
  assert(menu.classList.contains('show'), 'Test 4.2a: Dropdown menu receives show class');
  assert(container.classList.contains('dropdown-open'), 'Test 4.2b: Container receives dropdown-open class');
  assert(trigger.getAttribute('aria-expanded') === 'true', 'Test 4.2c: Trigger aria-expanded is true');

  // Test 4.3: Click trigger again closes menu
  trigger.click();
  assert(!menu.classList.contains('show'), 'Test 4.3a: Clicking trigger again closes menu');
  assert(!container.classList.contains('dropdown-open'), 'Test 4.3b: Container removes dropdown-open');
  assert(trigger.getAttribute('aria-expanded') === 'false', 'Test 4.3c: Trigger aria-expanded is false');

  // Test 4.4: Click outside closes menu
  trigger.click();
  assert(menu.classList.contains('show'), 'Test 4.4a: Menu opened');
  document.getElementById('content-body').click();
  assert(!menu.classList.contains('show'), 'Test 4.4b: Clicking outside dismisses user dropdown menu');

  // Test 4.5: Escape key closes menu
  trigger.click();
  assert(menu.classList.contains('show'), 'Test 4.5a: Menu opened');
  window.dispatchEvent(new window.KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
  assert(!menu.classList.contains('show'), 'Test 4.5b: Escape key dismisses user dropdown menu');
}

// ---------------------------------------------------------------------------
// SUITE 5: Traffic Light Window Controls (Green Maximize/Fullscreen)
// ---------------------------------------------------------------------------
console.log('\n--- Suite 5: Traffic Light Window Controls ---');
{
  const { window, document } = createTestEnv('mac');
  const maxBtn = document.getElementById('traffic-light-max');
  const minBtn = document.getElementById('traffic-light-min');
  const appWindow = document.getElementById('mac-app-window');

  // Test 5.1: Traffic light green button toggles fullscreen classes
  assert(!appWindow.classList.contains('is-fullscreen'), 'Test 5.1a: App window initially not fullscreen');
  maxBtn.click();
  assert(appWindow.classList.contains('is-fullscreen') && appWindow.classList.contains('mac-window-fullscreen'),
    'Test 5.1b: Green button toggles is-fullscreen and mac-window-fullscreen');

  maxBtn.click();
  assert(!appWindow.classList.contains('is-fullscreen') && !appWindow.classList.contains('mac-window-fullscreen'),
    'Test 5.1c: Green button second click toggles fullscreen off');

  // Test 5.2: Minimize button dims opacity
  minBtn.click();
  assert(appWindow.style.opacity === '0.7', 'Test 5.2: Minimize button animates opacity to 0.7');
}

// ---------------------------------------------------------------------------
// SUITE 6: Notification Bell Popover Toggle
// ---------------------------------------------------------------------------
console.log('\n--- Suite 6: Notification Bell Popover ---');
{
  const { window, document } = createTestEnv('mac');
  const notifBtn = document.getElementById('notification-bell');
  const notifDropdown = document.getElementById('notification-dropdown');

  assert(!notifDropdown.classList.contains('show'), 'Test 6.1a: Notification popover initially hidden');
  notifBtn.click();
  assert(notifDropdown.classList.contains('show'), 'Test 6.1b: Clicking notification bell opens popover');
  assert(notifBtn.getAttribute('aria-expanded') === 'true', 'Test 6.1c: Notification bell aria-expanded is true');

  notifBtn.click();
  assert(!notifDropdown.classList.contains('show'), 'Test 6.1d: Clicking notification bell again closes popover');

  notifBtn.click();
  assert(notifDropdown.classList.contains('show'), 'Test 6.1e: Popover re-opened');
  document.getElementById('content-body').click();
  assert(!notifDropdown.classList.contains('show'), 'Test 6.1f: Clicking outside dismisses notification popover');
}

// ---------------------------------------------------------------------------
// SUITE 7: Adversarial & Stress Testing
// ---------------------------------------------------------------------------
console.log('\n--- Suite 7: Adversarial & Stress Testing ---');
{
  // Test 7.1: Graceful degradation with missing DOM elements
  const minimalDom = new JSDOM('<!DOCTYPE html><html><body><div id="content"></div></body></html>', {
    runScripts: 'outside-only',
  });
  let threwError = false;
  try {
    minimalDom.window.eval(scriptSource);
    minimalDom.window.document.dispatchEvent(new minimalDom.window.Event('DOMContentLoaded'));
    // Trigger global events
    minimalDom.window.dispatchEvent(new minimalDom.window.KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
    minimalDom.window.dispatchEvent(new minimalDom.window.KeyboardEvent('keydown', { key: 'k', metaKey: true, bubbles: true }));
  } catch (err) {
    threwError = true;
    console.error('Error on minimal DOM:', err);
  }
  assert(!threwError, 'Test 7.1: Graceful execution with completely missing shell elements');

  // Test 7.2: Rapid 100x toggle stress test
  const { window, document } = createTestEnv('mac');
  const hamburger = document.getElementById('mobile-nav-toggle');
  const sidebar = document.getElementById('navigation');
  for (let i = 0; i < 100; i++) {
    hamburger.click();
  }
  // After 100 clicks (even number), drawer must be closed
  assert(!sidebar.classList.contains('mobile-open'),
    'Test 7.2: 100x rapid hamburger toggle maintains consistent binary state');

  // Test 7.3: XSS & Regex injection in search input
  const searchInput = document.getElementById('modal-search-input');
  const searchResults = document.getElementById('modal-search-results');
  const maliciousInput = '<script>alert("xss")</script> [.*+?^${}()|[\\]\\\\]';
  searchInput.value = maliciousInput;
  let searchThrew = false;
  try {
    searchInput.dispatchEvent(new window.Event('input', { bubbles: true }));
  } catch (err) {
    searchThrew = true;
  }
  assert(!searchThrew && !searchResults.innerHTML.includes('<script>alert'),
    'Test 7.3: Malicious query with regex metacharacters and HTML tags is sanitized without throwing');
}

console.log('\n===============================================================');
console.log(`TOTAL TESTS: ${passedCount + failedCount} | PASSED: ${passedCount} | FAILED: ${failedCount}`);
console.log('===============================================================');

if (failedCount > 0) {
  process.exit(1);
} else {
  process.exit(0);
}
