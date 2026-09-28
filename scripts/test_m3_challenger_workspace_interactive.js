/**
 * test_m3_challenger_workspace_interactive.js
 * Milestone 3 Screen 2 (Problem Workspace) Challenger Interactive Stress Harness
 *
 * Empirical stress testing covering:
 * 1. Split-pane divider dragging, boundary clamping (<25%, >75%), double-click reset, localStorage persistence.
 * 2. Ace editor integration, language selector filtering, mode switching, template fetching, draft saving.
 * 3. 65,536 bytes code limit (boundary, overflow rejection, empty rejection).
 * 4. KaTeX math delimiter configuration ($$, \\[, $, \\(, ~) and element exclusions.
 * 5. Sample I/O card parsing, copy button feedback animation, and sample sync.
 * 6. Custom testcase runner: adding/removing custom tests, detail toggle, AC/WA verdict evaluation.
 */

const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const REPO_ROOT = path.resolve(__dirname, '..');
const JQUERY_PATH = path.join(REPO_ROOT, 'resources', 'libs', 'jquery-3.4.1.min.js');
const STATEMENT_JS_PATH = path.join(REPO_ROOT, 'resources', 'problem-statement.js');
const WORKSPACE_JS_PATH = path.join(REPO_ROOT, 'resources', 'problem-workspace.js');

const jquerySource = fs.readFileSync(JQUERY_PATH, 'utf-8');
const statementJsSource = fs.readFileSync(STATEMENT_JS_PATH, 'utf-8');
const workspaceJsSource = fs.readFileSync(WORKSPACE_JS_PATH, 'utf-8');

const HTML_FIXTURE = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Screen 2 Workspace Stress Test</title>
</head>
<body data-problem-code="aplusb">
<div class="problem-workspace-wrap" id="problem-workspace-wrap">
  <!-- Header Bar -->
  <header class="problem-workspace-header" id="problem-workspace-header">
    <div class="header-left">
      <div class="problem-breadcrumb workspace-breadcrumb">
        <a href="/problems/" class="breadcrumb-link">Problems</a>
        <span class="breadcrumb-sep">/</span>
        <span class="breadcrumb-current">A Plus B</span>
      </div>
      <div class="problem-title-row">
        <h1 class="problem-title-text workspace-problem-title">A Plus B</h1>
        <button type="button" class="problem-bookmark-btn" id="problem-bookmark-star" data-problem-code="aplusb" title="Bookmark">
          <i class="fa fa-star-o"></i>
        </button>
      </div>
      <div class="problem-tags-row">
        <span class="problem-tag-pill workspace-tag-pill tag-math">Math</span>
        <span class="problem-tag-pill workspace-tag-pill tag-simulation">Simulation</span>
      </div>
    </div>
    <div class="header-right">
      <div class="problem-metrics-grid">
        <div class="metric-card metric-points">
          <div class="metric-header"><i class="fa fa-star"></i> Points</div>
          <div class="metric-value">3</div>
        </div>
        <div class="metric-card metric-ac-rate">
          <div class="metric-header"><i class="fa fa-pie-chart"></i> AC Rate</div>
          <div class="metric-value">78.4%</div>
          <div class="metric-progress"><div class="progress-bar-fill metric-progress-bar" style="width: 78.4%;"></div></div>
        </div>
        <div class="metric-card metric-group">
          <div class="metric-header"><i class="fa fa-folder"></i> Group</div>
          <div class="metric-value">Simple Math</div>
        </div>
        <div class="metric-card metric-time-limit">
          <div class="metric-header"><i class="fa fa-clock-o"></i> Time Limit</div>
          <div class="metric-value">1.0s</div>
        </div>
        <div class="metric-card metric-memory-limit">
          <div class="metric-header"><i class="fa fa-microchip"></i> Memory Limit</div>
          <div class="metric-value">64 MB</div>
        </div>
      </div>
    </div>
  </header>

  <!-- Split Container -->
  <div id="workspace-split-container" class="workspace-split-container">
    <!-- Statement Pane -->
    <section id="statement-pane" class="workspace-pane statement-pane" aria-label="Problem Statement">
      <div class="statement-tabs-bar" role="tablist">
        <button type="button" class="statement-tab-item active" id="tab-statement" role="tab" aria-selected="true">
          <i class="fa fa-th"></i> <span>Statement</span>
        </button>
        <a href="/problem/aplusb/submissions" class="statement-tab-item" id="tab-submissions" role="tab">
          <i class="fa fa-history"></i> <span>Submissions</span>
        </a>
        <button type="button" class="statement-tab-item" id="tab-comments" role="tab">
          <i class="fa fa-comment-o"></i> <span>Comments (2)</span>
        </button>
      </div>

      <div class="statement-panel-body" id="panel-statement" role="tabpanel">
        <div class="statement-content" id="statement-content">
          <p>Given two integers $A$ and $B$ ($-10^9 \\le A, B \\le 10^9$), calculate their sum $$A + B$$.</p>
          <p>Formula display: \\[S = \\sum_{i=1}^N i\\]</p>
          <p>Tilde notation: ~A \\le 100~</p>

          <h3>Sample Input 1</h3>
          <pre><code>1 2</code></pre>

          <h3>Sample Output 1</h3>
          <pre><code>3</code></pre>

          <h3>Sample Input 2</h3>
          <pre><code>1000000000 1000000000</code></pre>

          <h3>Sample Output 2</h3>
          <pre><code>2000000000</code></pre>

          <div class="statement-license">
            <a href="/license/cc-by-sa-4.0"><i class="fa fa-creative-commons"></i> CC BY-SA 4.0</a>
          </div>
        </div>
      </div>

      <div class="statement-comments-drawer" id="panel-comments" style="display: none;" role="tabpanel">
        <div class="comments-drawer-header">
          <h3>Community Discussion</h3>
          <button type="button" class="btn-close-comments" id="btn-close-comments">&times;</button>
        </div>
        <div class="comments-drawer-content">Comments content</div>
      </div>
    </section>

    <!-- Resizer Divider -->
    <div id="workspace-split-divider" class="workspace-split-divider" title="Drag to resize, double-click to reset">
      <div class="divider-handle"></div>
    </div>

    <!-- Editor Pane -->
    <section class="workspace-pane editor-pane" id="editor-pane" aria-label="Coding Workspace">
      <!-- Toolbar -->
      <div class="editor-action-toolbar" id="editor-action-toolbar">
        <div class="toolbar-left">
          <div class="lang-selector-wrap" id="lang-selector-wrap">
            <button type="button" class="lang-trigger-btn" id="lang-dropdown-trigger" aria-haspopup="listbox" aria-expanded="false">
              <span class="lang-brand-icon"><i class="fa fa-code" id="lang-icon"></i></span>
              <span class="lang-display-name" id="current-lang-name">Python 3</span>
              <i class="fa fa-chevron-down caret-icon"></i>
            </button>
            <div class="lang-dropdown-menu" id="lang-dropdown-menu" role="listbox" style="display: none;">
              <div class="lang-search-wrap">
                <input type="text" class="lang-search-input" id="lang-search-input" placeholder="Filter languages...">
              </div>
              <ul class="lang-options-list" id="lang-options-list">
                <li class="lang-option-item selected" role="option" data-id="1" data-name="Python 3" data-ace="python" aria-selected="true">
                  <span class="lang-opt-name">Python 3</span>
                </li>
                <li class="lang-option-item" role="option" data-id="2" data-name="C++ 17" data-ace="c_cpp" aria-selected="false">
                  <span class="lang-opt-name">C++ 17</span>
                </li>
                <li class="lang-option-item" role="option" data-id="3" data-name="Java 17" data-ace="java" aria-selected="false">
                  <span class="lang-opt-name">Java 17</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div class="toolbar-right">
          <button type="button" class="btn btn-outline btn-reset" id="btn-reset-code"><i class="fa fa-undo"></i> <span>Reset</span></button>
          <button type="button" class="btn btn-outline btn-run" id="btn-run-code"><i class="fa fa-play"></i> <span>Run</span></button>
          <button type="button" class="btn btn-primary btn-submit" id="btn-submit-code"><i class="fa fa-upload"></i> <span>Submit</span></button>
        </div>
      </div>

      <!-- Ace Card -->
      <div class="ace-editor-card" id="ace-editor-card">
        <div class="editor-floating-tools">
          <span class="draft-indicator editor-draft-indicator" id="draft-save-status"><i class="fa fa-check"></i> Draft saved</span>
          <button type="button" class="editor-tool-btn" id="btn-copy-code" title="Copy code"><i class="fa fa-clone"></i></button>
          <button type="button" class="editor-tool-btn" id="btn-fullscreen-code" title="Toggle Fullscreen"><i class="fa fa-arrows-alt"></i></button>
        </div>

        <form id="problem_submit" action="/problem/aplusb/submit" method="post" class="editor-form-inner">
          <select id="id_language" name="language" style="display: none;">
            <option value="1" data-id="1" data-name="Python 3" data-ace="python" selected>Python 3</option>
            <option value="2" data-id="2" data-name="C++ 17" data-ace="c_cpp">C++ 17</option>
            <option value="3" data-id="3" data-name="Java 17" data-ace="java">Java 17</option>
          </select>
          <textarea id="id_source" name="source" style="display: none;"></textarea>
          <input type="hidden" id="id_judge" name="judge" value="">
          <div id="ace_source" class="django-ace-widget" data-mode="python" data-theme="github"><div></div></div>
        </form>
      </div>

      <!-- Testcase Console -->
      <div class="testcase-console workspace-console" id="testcase-console">
        <div class="console-nav-bar">
          <div class="console-tabs" role="tablist">
            <button type="button" class="console-tab-btn tab-console-testcases active" id="tab-btn-testcases" role="tab" aria-selected="true" data-tab="testcases">
              <i class="fa fa-check-square-o"></i> Testcases
            </button>
            <button type="button" class="console-tab-btn tab-console-submissions" id="tab-btn-submissions" role="tab" aria-selected="false" data-tab="submissions">
              <i class="fa fa-history"></i> Submissions
            </button>
          </div>
          <div class="console-actions">
            <button type="button" class="btn-add-testcase btn-add-custom-test" id="btn-add-testcase">
              <i class="fa fa-plus"></i> <span>Add custom test</span>
            </button>
          </div>
        </div>

        <div class="console-tab-pane active" id="console-pane-testcases" role="tabpanel">
          <div class="testcases-list" id="testcases-list">
            <div class="testcase-row" data-testcase-id="1">
              <div class="testcase-main-bar">
                <button type="button" class="testcase-toggle-btn"><i class="fa fa-chevron-right toggle-icon"></i></button>
                <span class="testcase-number">#1</span>
                <div class="testcase-field-box">
                  <span class="testcase-field-label">Sample Input 1</span>
                  <input type="text" class="testcase-field-input input-sample-data" value="1 2">
                </div>
                <div class="testcase-field-box">
                  <span class="testcase-field-label">Expected Output</span>
                  <input type="text" class="testcase-field-input expected-sample-data" value="3">
                </div>
                <div class="testcase-verdict-slot">
                  <span class="verdict-pill verdict-idle" id="verdict-pill-1">Ready</span>
                </div>
              </div>
              <div class="testcase-expanded-details" style="display: none;">
                <div class="detail-row"><span class="detail-tag">Actual Output:</span><code class="actual-output-val">—</code></div>
              </div>
            </div>

            <div class="testcase-row" data-testcase-id="2">
              <div class="testcase-main-bar">
                <button type="button" class="testcase-toggle-btn"><i class="fa fa-chevron-right toggle-icon"></i></button>
                <span class="testcase-number">#2</span>
                <div class="testcase-field-box">
                  <span class="testcase-field-label">Sample Input 2</span>
                  <input type="text" class="testcase-field-input input-sample-data" value="1000000000 1000000000">
                </div>
                <div class="testcase-field-box">
                  <span class="testcase-field-label">Expected Output</span>
                  <input type="text" class="testcase-field-input expected-sample-data" value="2000000000">
                </div>
                <div class="testcase-verdict-slot">
                  <span class="verdict-pill verdict-idle" id="verdict-pill-2">Ready</span>
                </div>
              </div>
              <div class="testcase-expanded-details" style="display: none;">
                <div class="detail-row"><span class="detail-tag">Actual Output:</span><code class="actual-output-val">—</code></div>
              </div>
            </div>
          </div>
        </div>

        <div class="console-tab-pane" id="console-pane-submissions" role="tabpanel" style="display: none;">
          <div class="submissions-history-wrap" id="submissions-history-wrap">
            <div class="submissions-loading">Loading your submissions...</div>
          </div>
        </div>
      </div>
    </section>
  </div>
</div>
</body>
</html>
`;

let passedCount = 0;
let failedCount = 0;
const results = [];

function assert(condition, name, detail = '') {
  if (condition) {
    passedCount++;
    console.log(`  [PASS] ${name}`);
    results.push({ name, status: 'PASS', detail });
  } else {
    failedCount++;
    console.error(`  [FAIL] ${name} - ${detail}`);
    results.push({ name, status: 'FAIL', detail });
  }
}

/**
 * Creates a JSDOM testing sandbox with full jQuery, Ace mocks, and localStorage
 */
async function createWorkspaceEnv(initialLocalStorage = {}, viewportWidth = 1200) {
  const dom = new JSDOM(HTML_FIXTURE, {
    url: 'http://localhost:8000/problem/aplusb',
    runScripts: 'dangerously',
  });

  const { window } = dom;
  const { document } = window;

  // Set viewport width
  window.innerWidth = viewportWidth;

  // Setup localStorage with initial values
  if (initialLocalStorage) {
    Object.keys(initialLocalStorage).forEach((k) => {
      window.localStorage.setItem(k, initialLocalStorage[k]);
    });
  }

  // Mock navigator.clipboard
  let clipboardText = '';
  Object.defineProperty(window.navigator, 'clipboard', {
    value: {
      writeText: (txt) => {
        clipboardText = txt;
        return Promise.resolve();
      },
      readText: () => Promise.resolve(clipboardText),
    },
    configurable: true,
  });
  window.isSecureContext = true;

  // Mock alert and confirm
  let lastAlert = null;
  window.alert = (msg) => { lastAlert = msg; };
  window._getLastAlert = () => lastAlert;

  let confirmResult = true;
  window.confirm = () => confirmResult;
  window._setConfirmResult = (val) => { confirmResult = val; };

  // Mock KaTeX renderMathInElement
  let lastKaTeXTarget = null;
  let lastKaTeXOptions = null;
  window.renderMathInElement = (target, opts) => {
    lastKaTeXTarget = target;
    lastKaTeXOptions = opts;
  };
  window._getKaTeXCall = () => ({ target: lastKaTeXTarget, opts: lastKaTeXOptions });

  // Mock Ace editor
  let mockAceValue = '';
  let mockAceMode = 'ace/mode/python';
  const changeListeners = [];
  const commands = {};

  const mockSession = {
    setMode: (mode) => { mockAceMode = mode; },
    getMode: () => mockAceMode,
    setValue: (val) => {
      mockAceValue = val;
      changeListeners.forEach((fn) => fn());
    },
    getValue: () => mockAceValue,
    setTheme: () => {},
    setFontSize: () => {},
    setShowPrintMargin: () => {},
    setUseWrapMode: () => {},
    setTabSize: () => {},
    setUseSoftTabs: () => {},
    on: (evt, fn) => {
      if (evt === 'change') changeListeners.push(fn);
    },
  };

  const mockEditor = {
    getSession: () => mockSession,
    setTheme: () => {},
    setFontSize: () => {},
    setShowPrintMargin: () => {},
    resize: () => {},
    focus: () => {},
    commands: {
      addCommand: (cmd) => { commands[cmd.name] = cmd; },
    },
    container: { style: {} },
    _triggerChange: () => { changeListeners.forEach((fn) => fn()); },
    _commands: commands,
  };

  window.ace = {
    edit: () => mockEditor,
  };

  // Mock getBoundingClientRect on container
  const container = document.getElementById('workspace-split-container');
  container.getBoundingClientRect = () => ({
    left: 0,
    top: 0,
    width: 1000,
    height: 600,
    right: 1000,
    bottom: 600,
  });

  // Inject jQuery as script element
  function addScript(src) {
    const el = document.createElement('script');
    el.textContent = src;
    document.head.appendChild(el);
  }

  addScript(jquerySource);

  // Mock $.get for starter template and submissions
  window.$.get = function (url, data) {
    const d = window.$.Deferred();
    if (url === '/widgets/template') {
      if (data && String(data.id) === '2') {
        d.resolve('#include <iostream>\nusing namespace std;\n\nint main() {\n    int a, b;\n    if (cin >> a >> b) cout << a + b << endl;\n    return 0;\n}');
      } else if (data && String(data.id) === '1') {
        d.resolve('import sys\n\ndef main():\n    lines = sys.stdin.read().split()\n    if lines:\n        print(int(lines[0]) + int(lines[1]))\n\nif __name__ == "__main__":\n    main()\n');
      } else {
        d.resolve('');
      }
    } else if (url === '/api/v2/submissions') {
      d.resolve({
        data: {
          objects: [
            { id: 1234, result: 'AC', language: 'Python 3', time: 0.05 },
            { id: 1235, result: 'WA', language: 'Python 3', time: 0.04 },
          ],
        },
      });
    } else {
      d.reject();
    }
    return d.promise();
  };

  // Inject problem-statement.js and problem-workspace.js
  addScript(statementJsSource);
  addScript(workspaceJsSource);

  // Wait for jQuery $(function() { ... }) to execute
  await new Promise((r) => setTimeout(r, 60));

  return { dom, window, document, mockEditor, mockSession, localStorage: window.localStorage };
}

async function runAllChallengerTests() {
  console.log('======================================================================');
  console.log('CHALLENGER STRESS HARNESS: Screen 2 Problem Workspace (docs/2.png)');
  console.log('======================================================================\n');

  // ==========================================================================
  // SUITE 1: Split-Pane Workspace Resizer & Drag Boundary Clamping
  // ==========================================================================
  console.log('--- Suite 1: Split-Pane Workspace Resizer & Boundary Stress Testing ---');
  {
    const { window, document, localStorage } = await createWorkspaceEnv();
    const divider = document.getElementById('workspace-split-divider');
    const statementPane = document.getElementById('statement-pane');
    const editorPane = document.getElementById('editor-pane');

    // 1.1 Initial default layout (42% / 58%)
    assert(
      statementPane !== null && editorPane !== null && divider !== null,
      'Test 1.1: DOM elements for split panes and divider exist'
    );

    // 1.2 Mouse down initiates drag
    divider.dispatchEvent(new window.MouseEvent('mousedown', { bubbles: true, clientX: 420 }));
    assert(
      document.body.classList.contains('is-resizing-split'),
      'Test 1.2: Divider mousedown sets body.is-resizing-split'
    );

    // 1.3 Boundary Clamping: Drag < 25% (clientX = 150px -> 15% on 1000px container)
    // Minimum percent is 28%
    document.dispatchEvent(new window.MouseEvent('mousemove', { bubbles: true, clientX: 150 }));
    assert(
      statementPane.style.width === '28%',
      'Test 1.3: Drag < 25% (150px) strictly clamps to minLeftWidthPercent 28%',
      `Actual statement width: ${statementPane.style.width}`
    );
    assert(
      editorPane.style.width === '72%',
      'Test 1.4: Editor pane width strictly matches 100 - clamped width (72%)',
      `Actual editor width: ${editorPane.style.width}`
    );

    // 1.5 Boundary Clamping: Extreme negative drag (clientX = -300px)
    document.dispatchEvent(new window.MouseEvent('mousemove', { bubbles: true, clientX: -300 }));
    assert(
      statementPane.style.width === '28%',
      'Test 1.5: Extreme negative drag (-300px) strictly clamps to 28%',
      `Actual: ${statementPane.style.width}`
    );

    // 1.6 Valid Interior Drag: 50% (clientX = 500px)
    document.dispatchEvent(new window.MouseEvent('mousemove', { bubbles: true, clientX: 500 }));
    assert(
      statementPane.style.width === '50%',
      'Test 1.6: Valid drag to 50% (500px) applies exact 50% to statement pane',
      `Actual: ${statementPane.style.width}`
    );
    assert(
      editorPane.style.width === '50%',
      'Test 1.7: Valid drag to 50% applies exact 50% to editor pane',
      `Actual: ${editorPane.style.width}`
    );

    // 1.8 Boundary Clamping: Drag > 75% (clientX = 850px -> 85% on 1000px container)
    // Maximum percent is 68%
    document.dispatchEvent(new window.MouseEvent('mousemove', { bubbles: true, clientX: 850 }));
    assert(
      statementPane.style.width === '68%',
      'Test 1.8: Drag > 75% (850px) strictly clamps to maxLeftWidthPercent 68%',
      `Actual statement width: ${statementPane.style.width}`
    );
    assert(
      editorPane.style.width === '32%',
      'Test 1.9: Editor pane width strictly matches 100 - clamped max (32%)',
      `Actual editor width: ${editorPane.style.width}`
    );

    // 1.10 Extreme positive drag (clientX = 2500px)
    document.dispatchEvent(new window.MouseEvent('mousemove', { bubbles: true, clientX: 2500 }));
    assert(
      statementPane.style.width === '68%',
      'Test 1.10: Extreme positive drag (2500px) strictly clamps to 68%',
      `Actual: ${statementPane.style.width}`
    );

    // 1.11 Mouseup ends drag & persists to localStorage
    document.dispatchEvent(new window.MouseEvent('mouseup', { bubbles: true }));
    assert(
      !document.body.classList.contains('is-resizing-split'),
      'Test 1.11: Mouseup removes body.is-resizing-split'
    );
    assert(
      localStorage.getItem('dmoj_split_ratio') === '68.00',
      'Test 1.12: Mouseup persists clamped ratio (68.00) in localStorage["dmoj_split_ratio"]',
      `Stored: ${localStorage.getItem('dmoj_split_ratio')}`
    );

    // 1.13 Double-click reset to default 42% / 58%
    divider.dispatchEvent(new window.MouseEvent('dblclick', { bubbles: true }));
    assert(
      statementPane.style.width === '42%',
      'Test 1.13: Double-click reset restores statement pane width to 42%',
      `Actual statement width: ${statementPane.style.width}`
    );
    assert(
      editorPane.style.width === '58%',
      'Test 1.14: Double-click reset restores editor pane width to 58%',
      `Actual editor width: ${editorPane.style.width}`
    );
    assert(
      localStorage.getItem('dmoj_split_ratio') === null,
      'Test 1.15: Double-click reset removes dmoj_split_ratio from localStorage'
    );

    // 1.16 Page reload restoration from localStorage
    const envWithSavedRatio = await createWorkspaceEnv({ dmoj_split_ratio: '55.00' }, 1200);
    const stmtPane2 = envWithSavedRatio.document.getElementById('statement-pane');
    const editPane2 = envWithSavedRatio.document.getElementById('editor-pane');
    assert(
      stmtPane2.style.width === '55%',
      'Test 1.16: Split-pane on load restores valid ratio (55%) from localStorage on desktop (>991px)',
      `Restored width: ${stmtPane2.style.width}`
    );
    assert(
      editPane2.style.width === '45%',
      'Test 1.17: Split-pane on load restores matching editor pane width (45%) on desktop',
      `Restored editor width: ${editPane2.style.width}`
    );

    // 1.18 Responsive Mobile Viewport (< 991px) ignores saved split ratio
    const envMobile = await createWorkspaceEnv({ dmoj_split_ratio: '55.00' }, 768);
    const stmtMobile = envMobile.document.getElementById('statement-pane');
    assert(
      stmtMobile.style.width === '',
      'Test 1.18: Mobile viewport (768px <= 991px) does not apply inline split width, preserving responsive stack',
      `Mobile statement width: "${stmtMobile.style.width}"`
    );

    // 1.19 Page reload with corrupt / out-of-bounds ratio in localStorage (e.g. 99)
    const envCorrupt = await createWorkspaceEnv({ dmoj_split_ratio: '99.00' }, 1200);
    const stmtCorrupt = envCorrupt.document.getElementById('statement-pane');
    assert(
      stmtCorrupt.style.width !== '99%',
      'Test 1.19: Corrupted out-of-bounds ratio (99%) is rejected and not applied'
    );
  }

  // ==========================================================================
  // SUITE 2: Ace Editor, Language Switching, Templates & Code Limit Validation
  // ==========================================================================
  console.log('\n--- Suite 2: Ace Editor, Language Selector, Templates & Code Limit ---');
  {
    const { window, document, mockEditor, mockSession, localStorage } = await createWorkspaceEnv();

    // 2.1 Ace editor baseline mode
    assert(
      mockSession.getMode() === 'ace/mode/python',
      'Test 2.1: Ace editor initialized with ace/mode/python for Python 3',
      `Current mode: ${mockSession.getMode()}`
    );

    // 2.2 Language Selector Dropdown Open/Close
    const triggerBtn = document.getElementById('lang-dropdown-trigger');
    const dropdownMenu = document.getElementById('lang-dropdown-menu');

    triggerBtn.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
    assert(
      dropdownMenu.style.display === 'block',
      'Test 2.2: Clicking language trigger opens dropdown menu (display: block)'
    );
    assert(
      triggerBtn.getAttribute('aria-expanded') === 'true',
      'Test 2.3: Language trigger has aria-expanded="true"'
    );

    // 2.4 Search Filter Input inside Dropdown
    const searchInput = document.getElementById('lang-search-input');
    searchInput.value = 'c++';
    searchInput.dispatchEvent(new window.Event('input', { bubbles: true }));

    const cppOption = dropdownMenu.querySelector('.lang-option-item[data-id="2"]');
    const pyOption = dropdownMenu.querySelector('.lang-option-item[data-id="1"]');
    assert(
      cppOption.style.display !== 'none',
      'Test 2.4: Searching "c++" keeps C++ option visible'
    );
    assert(
      pyOption.style.display === 'none',
      'Test 2.5: Searching "c++" hides Python option'
    );

    // Search "java"
    searchInput.value = 'java';
    searchInput.dispatchEvent(new window.Event('input', { bubbles: true }));
    const javaOption = dropdownMenu.querySelector('.lang-option-item[data-id="3"]');
    assert(
      javaOption.style.display !== 'none' && cppOption.style.display === 'none',
      'Test 2.5b: Searching "java" keeps Java option visible and hides C++ option'
    );

    // Clear search
    searchInput.value = '';
    searchInput.dispatchEvent(new window.Event('input', { bubbles: true }));
    assert(
      pyOption.style.display !== 'none',
      'Test 2.6: Clearing search restores all language options'
    );

    // 2.7 Select C++ Language
    cppOption.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
    assert(
      dropdownMenu.style.display === 'none',
      'Test 2.7: Selecting language option closes dropdown menu'
    );
    assert(
      document.getElementById('current-lang-name').textContent === 'C++ 17',
      'Test 2.8: Current language display name updated to "C++ 17"',
      `Display: ${document.getElementById('current-lang-name').textContent}`
    );
    assert(
      document.getElementById('id_language').value === '2',
      'Test 2.9: Hidden #id_language select value updated to "2"'
    );
    assert(
      mockSession.getMode() === 'ace/mode/c_cpp',
      'Test 2.10: Ace editor mode switched to "ace/mode/c_cpp"',
      `Mode: ${mockSession.getMode()}`
    );

    // 2.11 Starter template loaded for C++
    await new Promise((r) => setTimeout(r, 60));
    assert(
      mockSession.getValue().includes('#include <iostream>'),
      'Test 2.11: C++ starter template loaded into Ace editor',
      `Value preview: ${mockSession.getValue().slice(0, 30)}`
    );

    // 2.12 Draft saving & debounced autosave
    const draftStatus = document.getElementById('draft-save-status');
    mockSession.setValue('// My test C++ solution\nint main() {}');
    assert(
      draftStatus.classList.contains('saving'),
      'Test 2.12: Typing in editor adds "saving" class to draft status'
    );

    // Advance timers for 500ms debounce
    await new Promise((r) => setTimeout(r, 600));
    assert(
      !draftStatus.classList.contains('saving'),
      'Test 2.13: After 500ms debounce, "saving" class is removed'
    );
    assert(
      localStorage.getItem('dmoj_draft:aplusb:2') === '// My test C++ solution\nint main() {}',
      'Test 2.14: Code autosaved to localStorage["dmoj_draft:aplusb:2"]',
      `Saved: ${localStorage.getItem('dmoj_draft:aplusb:2')}`
    );

    // 2.15 Reset Code action
    const resetBtn = document.getElementById('btn-reset-code');
    window._setConfirmResult(true);
    resetBtn.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
    await new Promise((r) => setTimeout(r, 50));
    assert(
      localStorage.getItem('dmoj_draft:aplusb:2') === null,
      'Test 2.15: Reset Code removes draft from localStorage'
    );

    // 2.16 Code Length Limit Validation (65,536 bytes boundary)
    const submitBtn = document.getElementById('btn-submit-code');
    const form = document.getElementById('problem_submit');
    let formSubmitted = false;
    form.submit = () => { formSubmitted = true; };

    // Case A: Empty code -> blocked
    mockSession.setValue('   ');
    formSubmitted = false;
    submitBtn.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
    assert(
      !formSubmitted,
      'Test 2.16: Empty code submission blocked'
    );
    assert(
      window._getLastAlert() && window._getLastAlert().includes('Please enter source code'),
      'Test 2.17: Empty code triggers alert prompt'
    );

    // Case B: Overflow code (65,537 bytes) -> blocked
    const overflowCode = 'a'.repeat(65537);
    mockSession.setValue(overflowCode);
    formSubmitted = false;
    submitBtn.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
    assert(
      !formSubmitted,
      'Test 2.18: Overflow code (65,537 chars > 65,536) strictly blocked'
    );
    assert(
      window._getLastAlert() && window._getLastAlert().includes('65536'),
      'Test 2.19: Overflow triggers alert with 65536 limit'
    );

    // Case C: Exact boundary code (65,536 bytes) -> permitted!
    const exactMaxCode = 'b'.repeat(65536);
    mockSession.setValue(exactMaxCode);
    formSubmitted = false;
    submitBtn.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
    assert(
      formSubmitted,
      'Test 2.20: Exact boundary code (65,536 chars) permitted and submitted to form'
    );
    assert(
      document.getElementById('id_source').value.length === 65536,
      'Test 2.21: Hidden textarea #id_source synced with exact 65,536 characters'
    );
  }

  // ==========================================================================
  // SUITE 3: KaTeX Delimiters, Sample I/O Card Parsing & Feedback
  // ==========================================================================
  console.log('\n--- Suite 3: KaTeX Delimiters & Sample I/O Parsing & Copy Feedback ---');
  {
    const { window, document } = await createWorkspaceEnv();

    // 3.1 KaTeX call options
    const katexCall = window._getKaTeXCall();
    assert(
      katexCall.target !== null,
      'Test 3.1: renderMathInElement called on statement container'
    );

    const delims = (katexCall.opts && katexCall.opts.delimiters) || [];
    const delimStrings = delims.map((d) => d.left);
    assert(
      delimStrings.includes('$$') && delimStrings.includes('\\[') &&
      delimStrings.includes('$') && delimStrings.includes('\\(') &&
      delimStrings.includes('~'),
      'Test 3.2: KaTeX configured with all 5 required delimiters ($$, \\[, $, \\(, ~)',
      `Delimiters: ${JSON.stringify(delimStrings)}`
    );

    const ignoredTags = (katexCall.opts && katexCall.opts.ignoredTags) || [];
    assert(
      ignoredTags.includes('pre') && ignoredTags.includes('code'),
      'Test 3.3: KaTeX ignoredTags excludes "pre" and "code" blocks',
      `Ignored tags: ${JSON.stringify(ignoredTags)}`
    );

    const ignoredClasses = (katexCall.opts && katexCall.opts.ignoredClasses) || [];
    assert(
      ignoredClasses.includes('ace_editor') && ignoredClasses.includes('sample-box-code'),
      'Test 3.4: KaTeX ignoredClasses excludes "ace_editor" and "sample-box-code"',
      `Ignored classes: ${JSON.stringify(ignoredClasses)}`
    );

    // 3.5 Sample testcase card conversion
    const sampleCards = document.querySelectorAll('.sample-testcase-card');
    assert(
      sampleCards.length === 4,
      'Test 3.5: enhanceSampleTestcases transformed 2 inputs + 2 outputs into 4 sample cards',
      `Count: ${sampleCards.length}`
    );

    const inputCard = document.querySelector('.sample-input-card');
    assert(
      inputCard !== null && inputCard.querySelector('.sample-copy-btn') !== null,
      'Test 3.6: Sample input card contains one-click copy button'
    );

    // 3.7 window.problemSamples extraction
    assert(
      Array.isArray(window.problemSamples) && window.problemSamples.length === 2,
      'Test 3.7: window.problemSamples extracted 2 sample pairs',
      `Length: ${window.problemSamples ? window.problemSamples.length : 0}`
    );
    assert(
      window.problemSamples[0].input.trim() === '1 2' && window.problemSamples[0].output.trim() === '3',
      'Test 3.8: Sample #1 pair accurately extracted (Input: "1 2", Output: "3")'
    );
    assert(
      window.problemSamples[1].input.trim() === '1000000000 1000000000' && window.problemSamples[1].output.trim() === '2000000000',
      'Test 3.9: Sample #2 pair accurately extracted (Input: "1000000000...", Output: "2000000000")'
    );

    // 3.10 Copy Button Interaction & Animated "Copied!" Feedback
    const copyBtn = inputCard.querySelector('.sample-copy-btn');
    copyBtn.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));

    await new Promise((r) => setTimeout(r, 50));
    assert(
      copyBtn.classList.contains('copied'),
      'Test 3.10: Clicking sample copy button adds .copied class'
    );
    assert(
      copyBtn.innerHTML.includes('Copied!'),
      'Test 3.11: Copy button text updates to "Copied!" with check icon',
      `HTML: ${copyBtn.innerHTML}`
    );

    // Advance 2100ms for revert
    await new Promise((r) => setTimeout(r, 2100));
    assert(
      !copyBtn.classList.contains('copied'),
      'Test 3.12: After 2000ms timeout, .copied class is removed'
    );
    assert(
      copyBtn.innerHTML.includes('Copy'),
      'Test 3.13: Copy button reverts to original "Copy" label'
    );

    // 3.14 Floating Editor Copy Button
    const editorCopyBtn = document.getElementById('btn-copy-code');
    editorCopyBtn.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
    await new Promise((r) => setTimeout(r, 50));
    assert(
      editorCopyBtn.innerHTML.includes('fa-check'),
      'Test 3.14: In-editor copy button updates to check icon upon click'
    );
  }

  // ==========================================================================
  // SUITE 4: Custom Testcase Console & Verdict Evaluation Runner
  // ==========================================================================
  console.log('\n--- Suite 4: Custom Testcase Console & Verdict Evaluation Runner ---');
  {
    const { window, document } = await createWorkspaceEnv();

    // 4.1 Console Tabs Navigation
    const tabCases = document.getElementById('tab-btn-testcases');
    const tabSubs = document.getElementById('tab-btn-submissions');
    const paneCases = document.getElementById('console-pane-testcases');
    const paneSubs = document.getElementById('console-pane-submissions');

    tabSubs.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
    assert(
      tabSubs.classList.contains('active'),
      'Test 4.1: Clicking Submissions console tab activates it'
    );
    assert(
      paneSubs.style.display === 'block' && paneCases.style.display === 'none',
      'Test 4.2: Submissions pane displayed and Testcases pane hidden'
    );

    await new Promise((r) => setTimeout(r, 50));
    const subsTable = document.querySelector('.console-subs-table');
    assert(
      subsTable !== null,
      'Test 4.3: Submissions history table populated via API'
    );

    // Switch back to Testcases tab
    tabCases.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
    assert(
      paneCases.style.display === 'block',
      'Test 4.4: Switching back to Testcases tab displays testcases list'
    );

    // 4.5 Add Custom Testcase
    const addTestBtn = document.getElementById('btn-add-testcase');
    const testcasesList = document.getElementById('testcases-list');
    const initialRowsCount = testcasesList.querySelectorAll('.testcase-row').length;

    addTestBtn.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
    const newRowsCount = testcasesList.querySelectorAll('.testcase-row').length;
    assert(
      newRowsCount === initialRowsCount + 1,
      'Test 4.5: Clicking "+ Add custom test" appends new testcase row',
      `Rows before: ${initialRowsCount}, after: ${newRowsCount}`
    );

    const customRow = testcasesList.querySelector('.testcase-row.is-custom-test');
    assert(
      customRow !== null,
      'Test 4.6: New row has .is-custom-test class'
    );
    assert(
      customRow.querySelector('.testcase-number').textContent === '#3',
      'Test 4.7: New row has sequential #3 number badge'
    );
    assert(
      customRow.querySelector('.testcase-remove-btn') !== null,
      'Test 4.8: Custom testcase row includes remove button'
    );

    // 4.9 Toggle Details in Custom Testcase
    const toggleBtn = customRow.querySelector('.testcase-toggle-btn');
    const details = customRow.querySelector('.testcase-expanded-details');
    assert(
      details.style.display === 'none',
      'Test 4.9: Expanded details hidden initially'
    );

    toggleBtn.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
    assert(
      details.style.display === 'block',
      'Test 4.10: Clicking toggle button expands testcase details (display: block)'
    );

    // 4.11 Run Code Evaluation on Testcases (AC and WA checks)
    // Configure inputs for testcases:
    // Row 1: input "5 10", expected "15" -> should be AC
    const row1 = document.querySelector('.testcase-row[data-testcase-id="1"]');
    row1.querySelector('.input-sample-data').value = '5 10';
    row1.querySelector('.expected-sample-data').value = '15';

    // Custom Row: input "7 8", expected "99" -> should be WA (since 7+8=15 != 99)
    customRow.querySelector('.input-sample-data').value = '7 8';
    customRow.querySelector('.expected-sample-data').value = '99';

    const runBtn = document.getElementById('btn-run-code');
    const submitBtn = document.getElementById('btn-submit-code');

    runBtn.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
    assert(
      runBtn.disabled && submitBtn.disabled,
      'Test 4.11: Run Code disables both Run and Submit buttons during evaluation'
    );
    assert(
      row1.querySelector('.verdict-pill').classList.contains('verdict-running'),
      'Test 4.12: Testcase pills transition to "verdict-running"'
    );

    // Wait for evaluation timeout (600ms in problem-workspace.js)
    await new Promise((r) => setTimeout(r, 700));

    assert(
      !runBtn.disabled && !submitBtn.disabled,
      'Test 4.13: Run and Submit buttons re-enabled after evaluation completes'
    );

    const pill1 = row1.querySelector('.verdict-pill');
    assert(
      pill1.classList.contains('verdict-ac') && pill1.textContent.includes('AC'),
      'Test 4.14: Testcase #1 (5 + 10 = 15) evaluated as verdict-ac (AC)',
      `Pill class: ${pill1.className}, text: ${pill1.textContent.trim()}`
    );

    const customPill = customRow.querySelector('.verdict-pill');
    assert(
      customPill.classList.contains('verdict-wa') && customPill.textContent.includes('WA'),
      'Test 4.15: Custom Testcase (7 + 8 = 15 != expected 99) evaluated as verdict-wa (WA)',
      `Pill class: ${customPill.className}, text: ${customPill.textContent.trim()}`
    );
    assert(
      customRow.querySelector('.actual-output-val').textContent === '15',
      'Test 4.16: Actual output correctly recorded as "15"',
      `Actual: ${customRow.querySelector('.actual-output-val').textContent}`
    );

    // 4.17 Remove Custom Testcase
    const removeBtn = customRow.querySelector('.testcase-remove-btn');
    removeBtn.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
    assert(
      document.querySelector('.testcase-row.is-custom-test') === null,
      'Test 4.17: Clicking remove button deletes custom testcase row from DOM'
    );
  }

  // ==========================================================================
  // Summary
  // ==========================================================================
  console.log('\n======================================================================');
  const total = passedCount + failedCount;
  console.log(`INTERACTIVE HARNESS SUMMARY: ${passedCount}/${total} Passed (${(passedCount / total * 100).toFixed(1)}%)`);
  console.log('======================================================================');
  if (failedCount === 0) {
    console.log('ALL SCREEN 2 INTERACTIVE STRESS TESTS PASSED!');
  }

  return failedCount === 0;
}

runAllChallengerTests().then((ok) => {
  process.exit(ok ? 0 : 1);
}).catch((err) => {
  console.error('Fatal error running tests:', err);
  process.exit(1);
});
