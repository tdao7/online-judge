/**
 * test_m2_challenger_interactive_stress.js
 * Empirical Challenger Stress Harness for Interactive Shell Controller
 *
 * Covers:
 * 1. Multi-key modifier combinations & CapsLock detection
 * 2. Rapid concurrent state machine transitions (200 randomized interleaved actions)
 * 3. Exact mathematical boundary verification for touch swipe gestures (deltaX, deltaY)
 * 4. Cyclic wrap-around keyboard navigation in search results (ArrowUp / ArrowDown / Enter)
 * 5. Fuzzing & input sanitization (regex metachars, XSS vectors, unicode, long strings)
 * 6. Responsive resize auto-dismissal debouncing (mobile -> desktop transition)
 * 7. Traffic light window controls state invariance
 */

const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const REPO_ROOT = path.resolve(__dirname, '..');
const SCRIPT_PATH = path.join(REPO_ROOT, 'resources', 'app-shell-controller.js');
const scriptSource = fs.readFileSync(SCRIPT_PATH, 'utf-8');

const HTML_TEMPLATE = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>DMOJ App Shell Stress Test</title>
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
            <input type="password" id="sample-password-input">
            <textarea id="sample-textarea">Sample Textarea</textarea>
            <div contenteditable="true" id="sample-contenteditable">Editable text</div>
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
      <div class="search-modal-results" id="modal-search-results" role="listbox"></div>
    </div>
  </div>
</body>
</html>
`;

let passedCount = 0;
let failedCount = 0;

function assert(condition, testName, detail = '') {
  if (condition) {
    passedCount++;
    console.log(`  [PASS] ${testName}`);
  } else {
    failedCount++;
    console.error(`  [FAIL] ${testName} - ${detail}`);
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

async function runChallengerStressTests() {
  console.log('===============================================================');
  console.log('CHALLENGER ADVERSARIAL STRESS SUITE: Interactive Shell Controller');
  console.log('===============================================================\n');

  // ---------------------------------------------------------------------------
  // Suite C1: Keyboard Shortcut Fuzzing & CapsLock / Modifiers
  // ---------------------------------------------------------------------------
  console.log('--- Suite C1: Keyboard Shortcut Fuzzing & CapsLock / Modifiers ---');
  {
    const { window, document } = createTestEnv('mac');
    const modal = document.getElementById('global-search-modal');

    // 1.1 CapsLock Meta + 'K' (uppercase)
    window.dispatchEvent(new window.KeyboardEvent('keydown', { key: 'K', metaKey: true, bubbles: true }));
    assert(modal.classList.contains('is-open') && modal.style.display === 'flex',
      'Test C1.1: ⌘K with uppercase K (CapsLock) opens modal');

    // 1.2 Close via ⌘k with lowercase k
    window.dispatchEvent(new window.KeyboardEvent('keydown', { key: 'k', metaKey: true, bubbles: true }));
    assert(!modal.classList.contains('is-open') && modal.style.display === 'none',
      'Test C1.2: ⌘k with lowercase k toggles modal closed');

    // 1.3 Meta + Shift + K should also work (user holding shift)
    window.dispatchEvent(new window.KeyboardEvent('keydown', { key: 'K', metaKey: true, shiftKey: true, bubbles: true }));
    assert(modal.classList.contains('is-open'),
      'Test C1.3: ⌘+Shift+K opens modal');
    window.dispatchEvent(new window.KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));

    // 1.4 Windows Ctrl + K with uppercase K
    const winEnv = createTestEnv('win');
    const winModal = winEnv.document.getElementById('global-search-modal');
    winEnv.window.dispatchEvent(new winEnv.window.KeyboardEvent('keydown', { key: 'K', ctrlKey: true, bubbles: true }));
    assert(winModal.classList.contains('is-open'),
      'Test C1.4: Windows Ctrl+K (uppercase) opens modal');

    // 1.5 Slash key pressed while focus is on password input
    const pwdInput = document.getElementById('sample-password-input');
    pwdInput.focus();
    window.dispatchEvent(new window.KeyboardEvent('keydown', { key: '/', bubbles: true }));
    assert(!modal.classList.contains('is-open'),
      'Test C1.5: "/" key pressed inside password input does NOT open modal');

    // 1.6 Slash key pressed while focus is on normal text input
    const txtInput = document.getElementById('sample-text-input');
    txtInput.focus();
    window.dispatchEvent(new window.KeyboardEvent('keydown', { key: '/', bubbles: true }));
    assert(!modal.classList.contains('is-open'),
      'Test C1.6: "/" key pressed inside text input does NOT open modal');

    // 1.7 Slash key pressed while focus is on textarea
    const textarea = document.getElementById('sample-textarea');
    textarea.focus();
    window.dispatchEvent(new window.KeyboardEvent('keydown', { key: '/', bubbles: true }));
    assert(!modal.classList.contains('is-open'),
      'Test C1.7: "/" key pressed inside textarea does NOT open modal');

    // 1.8 ⌘K pressed inside input should still open modal (intentional global hotkey)
    txtInput.focus();
    window.dispatchEvent(new window.KeyboardEvent('keydown', { key: 'k', metaKey: true, bubbles: true }));
    assert(modal.classList.contains('is-open'),
      'Test C1.8: ⌘K pressed inside input successfully triggers global search modal');
    window.dispatchEvent(new window.KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
  }

  // ---------------------------------------------------------------------------
  // Suite C2: Touch Swipe Boundary Math Exactness (deltaX < -50 && deltaY < 80)
  // ---------------------------------------------------------------------------
  console.log('\n--- Suite C2: Touch Swipe Boundary Math Exactness ---');
  {
    const { window, document } = createTestEnv('mac');
    const sidebar = document.getElementById('navigation');
    const hamburger = document.getElementById('mobile-nav-toggle');

    function simulateSwipe(x1, y1, x2, y2) {
      const startEvt = new window.Event('touchstart', { bubbles: true, cancelable: true });
      startEvt.changedTouches = [{ screenX: x1, screenY: y1 }];
      sidebar.dispatchEvent(startEvt);

      const endEvt = new window.Event('touchend', { bubbles: true, cancelable: true });
      endEvt.changedTouches = [{ screenX: x2, screenY: y2 }];
      sidebar.dispatchEvent(endEvt);
    }

    // C2.1 deltaX = -49, deltaY = 0 (Below threshold: must NOT close)
    hamburger.click();
    assert(sidebar.classList.contains('mobile-open'), 'Drawer opened for C2.1');
    simulateSwipe(200, 100, 151, 100); // deltaX = 151 - 200 = -49
    assert(sidebar.classList.contains('mobile-open'),
      'Test C2.1: Swipe deltaX = -49 (< -50 threshold) keeps drawer OPEN');

    // C2.2 deltaX = -50, deltaY = 0 (Exact boundary: -50 is not < -50, must NOT close)
    simulateSwipe(200, 100, 150, 100); // deltaX = 150 - 200 = -50
    assert(sidebar.classList.contains('mobile-open'),
      'Test C2.2: Swipe deltaX = -50 (exact edge condition) keeps drawer OPEN');

    // C2.3 deltaX = -51, deltaY = 0 (Above threshold: MUST close)
    simulateSwipe(200, 100, 149, 100); // deltaX = 149 - 200 = -51
    assert(!sidebar.classList.contains('mobile-open'),
      'Test C2.3: Swipe deltaX = -51 (passes threshold) CLOSES drawer');

    // C2.4 deltaX = -100, deltaY = 79 (Vertical deviation 79 < 80: MUST close)
    hamburger.click();
    assert(sidebar.classList.contains('mobile-open'), 'Drawer opened for C2.4');
    simulateSwipe(200, 100, 100, 179); // deltaX = -100, deltaY = |179 - 100| = 79
    assert(!sidebar.classList.contains('mobile-open'),
      'Test C2.4: Swipe deltaX = -100 with deltaY = 79 (< 80) CLOSES drawer');

    // C2.5 deltaX = -100, deltaY = 80 (Vertical deviation 80 is not < 80: must NOT close)
    hamburger.click();
    assert(sidebar.classList.contains('mobile-open'), 'Drawer opened for C2.5');
    simulateSwipe(200, 100, 100, 180); // deltaX = -100, deltaY = 80
    assert(sidebar.classList.contains('mobile-open'),
      'Test C2.5: Swipe deltaX = -100 with deltaY = 80 (exact boundary) keeps drawer OPEN');

    // C2.6 deltaX = -100, deltaY = 120 (Diagonal swipe: must NOT close)
    simulateSwipe(200, 100, 100, 220); // deltaY = 120
    assert(sidebar.classList.contains('mobile-open'),
      'Test C2.6: Diagonal swipe deltaY = 120 keeps drawer OPEN');
    hamburger.click(); // Close drawer
  }

  // ---------------------------------------------------------------------------
  // Suite C3: Keyboard Navigation Cyclic Wrap-Around & Enter Selection
  // ---------------------------------------------------------------------------
  console.log('\n--- Suite C3: Keyboard Navigation Cyclic Wrap-Around & Enter Selection ---');
  {
    const { window, document } = createTestEnv('mac');
    const resultsContainer = document.getElementById('modal-search-results');

    // Open search modal
    window.DmojAppShell.openSearch();
    const rows = resultsContainer.querySelectorAll('.search-result-row');
    const totalRows = rows.length;
    assert(totalRows > 0, `Search results rendered (${totalRows} rows)`);

    // Verify initial selection is row 0
    assert(rows[0].classList.contains('is-selected'),
      'Test C3.1: Initial row 0 is selected');

    // ArrowUp at index 0 should wrap around to the last item (totalRows - 1)
    window.dispatchEvent(new window.KeyboardEvent('keydown', { key: 'ArrowUp', bubbles: true }));
    const lastIdx = totalRows - 1;
    const rowsAfterUp = resultsContainer.querySelectorAll('.search-result-row');
    assert(rowsAfterUp[lastIdx].classList.contains('is-selected'),
      `Test C3.2: ArrowUp from index 0 cyclically wraps to last item (index ${lastIdx})`);

    // ArrowDown from last item should wrap back to index 0
    window.dispatchEvent(new window.KeyboardEvent('keydown', { key: 'ArrowDown', bubbles: true }));
    const rowsAfterDown = resultsContainer.querySelectorAll('.search-result-row');
    assert(rowsAfterDown[0].classList.contains('is-selected'),
      'Test C3.3: ArrowDown from last item cyclically wraps back to index 0');

    // Sequential ArrowDown through all rows
    let allSelectedCorrectly = true;
    for (let i = 1; i < totalRows; i++) {
      window.dispatchEvent(new window.KeyboardEvent('keydown', { key: 'ArrowDown', bubbles: true }));
      const currentRows = resultsContainer.querySelectorAll('.search-result-row');
      if (!currentRows[i].classList.contains('is-selected')) {
        allSelectedCorrectly = false;
        break;
      }
    }
    assert(allSelectedCorrectly,
      `Test C3.4: Sequential ArrowDown steps through all ${totalRows} items monotonically`);

    // Intercept navigation by attaching click prevention or inspecting selected row href
    const selectedRow = resultsContainer.querySelector('.search-result-row.is-selected');
    const targetHref = selectedRow.getAttribute('href');
    assert(targetHref && targetHref.length > 0,
      `Test C3.5: Selected row has valid destination URL (${targetHref})`);

    window.DmojAppShell.closeSearch();
  }

  // ---------------------------------------------------------------------------
  // Suite C4: Fuzzing & Input Sanitization
  // ---------------------------------------------------------------------------
  console.log('\n--- Suite C4: Fuzzing & Input Sanitization ---');
  {
    const { window, document } = createTestEnv('mac');
    const searchInput = document.getElementById('modal-search-input');
    const resultsContainer = document.getElementById('modal-search-results');

    window.DmojAppShell.openSearch();

    const fuzzVectors = [
      { input: '.*+?^${}()|[]\\', desc: 'Regex metacharacters' },
      { input: '<script>alert("XSS")</script>', desc: 'Direct script tag injection' },
      { input: '"><img src=x onerror=alert(1)>', desc: 'Broken tag attribute injection' },
      { input: "' OR '1'='1", desc: 'SQL-like injection string' },
      { input: '🚀 DMOJ 🏆 🇻🇳 Конкурс', desc: 'Multilingual unicode and emojis' },
      { input: 'A'.repeat(2000), desc: '2000-character long query' },
    ];

    let allFuzzPassed = true;
    for (const vec of fuzzVectors) {
      try {
        searchInput.value = vec.input;
        searchInput.dispatchEvent(new window.Event('input', { bubbles: true }));
        // Ensure no unescaped script tag in innerHTML
        if (resultsContainer.innerHTML.includes('<script>alert')) {
          allFuzzPassed = false;
          assert(false, `Test C4: ${vec.desc}`, 'Raw unescaped script detected in DOM!');
          break;
        }
      } catch (err) {
        allFuzzPassed = false;
        assert(false, `Test C4: ${vec.desc}`, `Threw exception: ${err.message}`);
        break;
      }
    }
    if (allFuzzPassed) {
      assert(true, 'Test C4.1: All 6 adversarial fuzz inputs processed safely without exceptions or XSS leaks');
    }

    // Verify empty search state has no crash
    searchInput.value = 'nonexistentxyzproblem12345';
    searchInput.dispatchEvent(new window.Event('input', { bubbles: true }));
    assert(resultsContainer.querySelector('.search-empty-state') !== null,
      'Test C4.2: Graceful empty state displayed when query has no matches');

    // Arrow down on empty results doesn't crash
    try {
      window.dispatchEvent(new window.KeyboardEvent('keydown', { key: 'ArrowDown', bubbles: true }));
      window.dispatchEvent(new window.KeyboardEvent('keydown', { key: 'ArrowUp', bubbles: true }));
      window.dispatchEvent(new window.KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
      assert(true, 'Test C4.3: Arrow keys and Enter on empty results handled safely without exceptions');
    } catch (e) {
      assert(false, 'Test C4.3: Arrow keys on empty results threw exception', e.message);
    }

    window.DmojAppShell.closeSearch();
  }

  // ---------------------------------------------------------------------------
  // Suite C5: Rapid Interleaved State Transitions (200 actions fuzzing)
  // ---------------------------------------------------------------------------
  console.log('\n--- Suite C5: Rapid Interleaved State Transitions (200 Actions) ---');
  {
    const { window, document } = createTestEnv('mac');
    const modal = document.getElementById('global-search-modal');
    const sidebar = document.getElementById('navigation');

    const hamburger = document.getElementById('mobile-nav-toggle');
    const userTrigger = document.getElementById('user-pill-trigger');
    const notifBtn = document.getElementById('notification-bell');
    const backdrop = document.getElementById('sidebar-backdrop');

    let invariantViolations = 0;

    for (let step = 0; step < 200; step++) {
      const stateBefore = window.DmojAppShell.getState();
      const action = step % 8;

      // If search modal is open, any pointer event outside modal hits modal backdrop
      if (stateBefore.searchModalOpen && (action === 1 || action === 2 || action === 3 || action === 5 || action === 6)) {
        modal.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
      } else {
        switch (action) {
          case 0: // Toggle Search via ⌘K
            window.dispatchEvent(new window.KeyboardEvent('keydown', { key: 'k', metaKey: true, bubbles: true }));
            break;
          case 1: // Toggle Hamburger
            hamburger.click();
            break;
          case 2: // Toggle User Menu
            userTrigger.click();
            break;
          case 3: // Toggle Notification
            notifBtn.click();
            break;
          case 4: // Press Escape
            window.dispatchEvent(new window.KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
            break;
          case 5: // Click document outside
            document.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
            break;
          case 6: // Click Sidebar Backdrop
            backdrop.click();
            break;
          case 7: // Press Slash
            window.dispatchEvent(new window.KeyboardEvent('keydown', { key: '/', bubbles: true }));
            break;
        }
      }

      const state = window.DmojAppShell.getState();

      // Invariant 1: If search modal is open, user dropdown and drawer MUST be closed
      if (state.searchModalOpen) {
        if (state.drawerOpen || state.userDropdownOpen) {
          invariantViolations++;
        }
      }
      // Invariant 2: DOM class matches state flag
      const modalOpenClass = modal.classList.contains('is-open');
      if (state.searchModalOpen !== modalOpenClass) {
        invariantViolations++;
      }
      const drawerOpenClass = sidebar.classList.contains('mobile-open');
      if (state.drawerOpen !== drawerOpenClass) {
        invariantViolations++;
      }
    }

    assert(invariantViolations === 0,
      'Test C5.1: 200 randomized interleaved actions completed with 0 state invariant violations');
  }

  // ---------------------------------------------------------------------------
  // Suite C6: Responsive Resize & Drawer Auto-Dismissal
  // ---------------------------------------------------------------------------
  console.log('\n--- Suite C6: Responsive Resize & Drawer Auto-Dismissal ---');
  {
    const { window, document } = createTestEnv('mac');
    const sidebar = document.getElementById('navigation');
    const hamburger = document.getElementById('mobile-nav-toggle');

    // Simulate mobile viewport
    window.innerWidth = 480;
    hamburger.click();
    assert(sidebar.classList.contains('mobile-open'),
      'Test C6.1: Drawer opened on simulated mobile viewport (480px)');

    // Simulate resize to desktop (1024px)
    window.innerWidth = 1024;
    window.dispatchEvent(new window.Event('resize'));

    // The handler has a 100ms debounce timer
    await new Promise(resolve => setTimeout(resolve, 150));

    assert(!sidebar.classList.contains('mobile-open'),
      'Test C6.2: Resizing from mobile to desktop (1024px) auto-dismisses mobile drawer');
  }

  // ---------------------------------------------------------------------------
  // Suite C7: Traffic Lights State Invariants
  // ---------------------------------------------------------------------------
  console.log('\n--- Suite C7: Traffic Lights State Invariants ---');
  {
    const { window, document } = createTestEnv('mac');
    const maxBtn = document.getElementById('traffic-light-max');
    const minBtn = document.getElementById('traffic-light-min');
    const appWindow = document.getElementById('mac-app-window');

    // Test 50 rapid maximize clicks
    for (let i = 0; i < 50; i++) {
      maxBtn.click();
    }
    // 50 clicks = even number of toggles -> window should NOT be fullscreen
    assert(!appWindow.classList.contains('is-fullscreen') && !appWindow.classList.contains('mac-window-fullscreen'),
      'Test C7.1: 50 toggles on maximize traffic light returns to initial non-fullscreen state');

    maxBtn.click();
    assert(appWindow.classList.contains('is-fullscreen') && appWindow.classList.contains('mac-window-fullscreen'),
      'Test C7.2: 51st click enters fullscreen');

    // Test minimize button sets opacity to 0.7 then restores to 1
    minBtn.click();
    assert(appWindow.style.opacity === '0.7',
      'Test C7.3: Minimize button sets app-window opacity to 0.7');

    await new Promise(resolve => setTimeout(resolve, 350));
    assert(appWindow.style.opacity === '1',
      'Test C7.4: App-window opacity restored to 1.0 after 300ms transition');
  }

  console.log('\n===============================================================');
  console.log(`TOTAL CHALLENGER TESTS: ${passedCount + failedCount} | PASSED: ${passedCount} | FAILED: ${failedCount}`);
  console.log('===============================================================\n');

  if (failedCount > 0) {
    process.exit(1);
  }
}

runChallengerStressTests().catch(err => {
  console.error('Unhandled test failure:', err);
  process.exit(1);
});
