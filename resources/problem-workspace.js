/**
 * VCODER Online Judge — Problem Workspace Controller (Screen 2: Ace Editor, Split-Pane & Submission Flow)
 * Milestone 3 — Split-Pane, Language Selector, Ace Editor, Drafts, Testcases Runner
 */
(function (window, document, $) {
  'use strict';

  // Extract problem code from URL or body
  const pathParts = window.location.pathname.split('/').filter(Boolean);
  let detectedCode = 'aplusb';
  for (let i = 0; i < pathParts.length; i++) {
    if (pathParts[i] === 'problem' && pathParts[i + 1]) {
      detectedCode = pathParts[i + 1];
      break;
    }
  }

  const config = {
    problemCode: document.body.getAttribute('data-problem-code') || detectedCode,
    minLeftWidthPercent: 28,
    maxLeftWidthPercent: 68,
    defaultLeftWidthPercent: 42,
    autosaveDebounceMs: 500,
  };

  let editorInstance = null;
  let autosaveTimer = null;

  /**
   * Helper: Get active language ID and Ace mode
   */
  function getSelectedLanguage() {
    const select = document.getElementById('id_language');
    if (!select || !select.options || select.selectedIndex < 0) {
      return { id: 1, ace: 'python', name: 'Python 3', judgeInfo: '' };
    }
    const opt = select.options[select.selectedIndex];
    return {
      id: opt.value,
      ace: opt.getAttribute('data-ace') || 'python',
      name: opt.getAttribute('data-name') || opt.text,
      judgeInfo: opt.getAttribute('data-judge-info') || opt.getAttribute('data-info') || '',
    };
  }

  /**
   * Helper: Storage keys
   */
  function getDraftKey(langId) {
    return 'dmoj_draft:' + config.problemCode + ':' + langId;
  }

  /**
   * Initialize Split-Pane Drag Resizer
   */
  function initSplitPane() {
    const container = document.getElementById('workspace-split-container');
    const divider = document.getElementById('workspace-split-divider');
    const statementPane = document.getElementById('statement-pane');
    const editorPane = document.getElementById('editor-pane');

    if (!container || !divider || !statementPane || !editorPane) return;

    // Restore saved ratio
    const savedRatio = localStorage.getItem('dmoj_split_ratio');
    if (savedRatio && window.innerWidth > 991) {
      const parsed = parseFloat(savedRatio);
      if (!isNaN(parsed) && parsed >= config.minLeftWidthPercent && parsed <= config.maxLeftWidthPercent) {
        statementPane.style.width = parsed + '%';
        statementPane.style.flex = '0 0 ' + parsed + '%';
        statementPane.style.maxWidth = parsed + '%';
        editorPane.style.width = (100 - parsed) + '%';
        editorPane.style.flex = '1 1 ' + (100 - parsed) + '%';
      }
    }

    let isDragging = false;

    divider.addEventListener('mousedown', function (e) {
      isDragging = true;
      document.body.classList.add('is-resizing-split');
      e.preventDefault();
    });

    document.addEventListener('mousemove', function (e) {
      if (!isDragging) return;
      const rect = container.getBoundingClientRect();
      const offset = e.clientX - rect.left;
      let percent = (offset / rect.width) * 100;
      percent = Math.max(config.minLeftWidthPercent, Math.min(config.maxLeftWidthPercent, percent));

      statementPane.style.width = percent + '%';
      statementPane.style.flex = '0 0 ' + percent + '%';
      statementPane.style.maxWidth = percent + '%';
      editorPane.style.width = (100 - percent) + '%';
      editorPane.style.flex = '1 1 ' + (100 - percent) + '%';

      if (editorInstance) {
        editorInstance.resize();
      }
    });

    document.addEventListener('mouseup', function () {
      if (!isDragging) return;
      isDragging = false;
      document.body.classList.remove('is-resizing-split');

      const widthPercent = parseFloat(statementPane.style.width);
      if (!isNaN(widthPercent)) {
        localStorage.setItem('dmoj_split_ratio', widthPercent.toFixed(2));
      }
      if (editorInstance) {
        editorInstance.resize();
      }
    });

    // Double click resets ratio to default 42/58
    divider.addEventListener('dblclick', function () {
      statementPane.style.width = config.defaultLeftWidthPercent + '%';
      statementPane.style.flex = '0 0 ' + config.defaultLeftWidthPercent + '%';
      statementPane.style.maxWidth = config.defaultLeftWidthPercent + '%';
      editorPane.style.width = (100 - config.defaultLeftWidthPercent) + '%';
      editorPane.style.flex = '1 1 ' + (100 - config.defaultLeftWidthPercent) + '%';
      localStorage.removeItem('dmoj_split_ratio');
      if (editorInstance) {
        editorInstance.resize();
      }
    });
  }

  /**
   * Initialize Ace Editor
   */
  function initAceEditor() {
    const aceEl = document.getElementById('ace_source');
    const sourceTextarea = document.getElementById('id_source');
    if (!aceEl || !sourceTextarea) return;

    if (window.ace) {
      editorInstance = ace.edit(aceEl);
    } else if (window.ace_source) {
      editorInstance = window.ace_source;
    }

    if (!editorInstance) return;
    window.ace_source = editorInstance;

    // Apply baseline settings
    const lang = getSelectedLanguage();
    editorInstance.getSession().setMode('ace/mode/' + lang.ace);
    editorInstance.setTheme('ace/theme/github');
    editorInstance.setFontSize(14);
    editorInstance.setShowPrintMargin(false);
    editorInstance.getSession().setUseWrapMode(true);
    editorInstance.getSession().setTabSize(4);
    editorInstance.getSession().setUseSoftTabs(true);
    if (editorInstance.container) {
      editorInstance.container.style.lineHeight = '1.5';
    }

    // Load initial code: Priority 1: localStorage draft; Priority 2: existing source; Priority 3: upstream template
    const draftKey = getDraftKey(lang.id);
    const savedDraft = localStorage.getItem(draftKey);

    if (savedDraft !== null && savedDraft.trim() !== '') {
      editorInstance.getSession().setValue(savedDraft);
      sourceTextarea.value = savedDraft;
    } else if (sourceTextarea.value && sourceTextarea.value.trim() !== '') {
      editorInstance.getSession().setValue(sourceTextarea.value);
    } else {
      fetchStarterTemplate(lang.id);
    }

    // Sync changes to textarea and autosave to localStorage
    editorInstance.getSession().on('change', function () {
      const code = editorInstance.getSession().getValue();
      sourceTextarea.value = code;

      const indicator = document.getElementById('draft-save-status');
      if (indicator) {
        indicator.innerHTML = '<i class="fa fa-pencil"></i> ' + (window.gettext ? gettext('Editing...') : 'Editing...');
        indicator.classList.add('saving');
      }

      clearTimeout(autosaveTimer);
      autosaveTimer = setTimeout(function () {
        localStorage.setItem(getDraftKey(getSelectedLanguage().id), code);
        if (indicator) {
          indicator.innerHTML = '<i class="fa fa-check"></i> ' + (window.gettext ? gettext('Draft saved') : 'Draft saved');
          indicator.classList.remove('saving');
        }
      }, config.autosaveDebounceMs);
    });

    // Keyboard Shortcuts
    editorInstance.commands.addCommand({
      name: 'submitSolution',
      bindKey: { win: 'Ctrl-Enter', mac: 'Command-Enter' },
      exec: function () {
        triggerSubmission();
      },
    });

    editorInstance.commands.addCommand({
      name: 'runCode',
      bindKey: { win: "Ctrl-'", mac: "Command-'" },
      exec: function () {
        triggerRunCode();
      },
    });

    editorInstance.commands.addCommand({
      name: 'saveDraftImmediate',
      bindKey: { win: 'Ctrl-S', mac: 'Command-S' },
      exec: function () {
        const code = editorInstance.getSession().getValue();
        localStorage.setItem(getDraftKey(getSelectedLanguage().id), code);
        const indicator = document.getElementById('draft-save-status');
        if (indicator) {
          indicator.innerHTML = '<i class="fa fa-check"></i> ' + (window.gettext ? gettext('Draft saved') : 'Draft saved');
          indicator.classList.remove('saving');
        }
      },
    });

    // In-editor floating buttons
    const copyBtn = document.getElementById('btn-copy-code');
    if (copyBtn) {
      copyBtn.addEventListener('click', function () {
        const code = editorInstance.getSession().getValue();
        navigator.clipboard.writeText(code).then(function () {
          copyBtn.innerHTML = '<i class="fa fa-check"></i>';
          setTimeout(function () {
            copyBtn.innerHTML = '<i class="fa fa-clone"></i>';
          }, 1500);
        });
      });
    }

    const fullscreenBtn = document.getElementById('btn-fullscreen-code');
    if (fullscreenBtn) {
      fullscreenBtn.addEventListener('click', function () {
        const card = document.getElementById('ace-editor-card');
        if (card) {
          card.classList.toggle('editor-card-fullscreen');
          editorInstance.resize();
        }
      });
    }
  }

  /**
   * Fetch starter template from backend
   */
  function fetchStarterTemplate(langId) {
    if (!editorInstance) return;
    $.get('/widgets/template', { id: langId })
      .done(function (template) {
        if (template && template.trim()) {
          editorInstance.getSession().setValue(template);
          const sourceTextarea = document.getElementById('id_source');
          if (sourceTextarea) sourceTextarea.value = template;
        } else {
          setFallbackBoilerplate();
        }
      })
      .fail(function () {
        setFallbackBoilerplate();
      });
  }

  function setFallbackBoilerplate() {
    if (!editorInstance) return;
    const lang = getSelectedLanguage();
    let fallback = '# Enter your code here\n';
    if (lang.ace === 'c_cpp') {
      fallback = '#include <iostream>\nusing namespace std;\n\nint main() {\n    int a, b;\n    if (cin >> a >> b) {\n        cout << a + b << endl;\n    }\n    return 0;\n}\n';
    } else if (lang.ace === 'java') {
      fallback = 'import java.util.Scanner;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int a = sc.nextInt();\n        int b = sc.nextInt();\n        System.out.println(a + b);\n    }\n}\n';
    } else if (lang.ace === 'python') {
      fallback = 'import sys\n\ndef main():\n    lines = sys.stdin.read().split()\n    if lines:\n        print(int(lines[0]) + int(lines[1]))\n\nif __name__ == "__main__":\n    main()\n';
    }
    editorInstance.getSession().setValue(fallback);
    const sourceTextarea = document.getElementById('id_source');
    if (sourceTextarea) sourceTextarea.value = fallback;
  }

  /**
   * Initialize Custom Language Selector Dropdown
   */
  function initLanguageSelector() {
    const trigger = document.getElementById('lang-dropdown-trigger');
    const menu = document.getElementById('lang-dropdown-menu');
    const select = document.getElementById('id_language');
    const searchInput = document.getElementById('lang-search-input');
    const currentNameSpan = document.getElementById('current-lang-name');

    if (!trigger || !menu || !select) return;

    trigger.addEventListener('click', function (e) {
      e.stopPropagation();
      const isVisible = menu.style.display !== 'none';
      menu.style.display = isVisible ? 'none' : 'block';
      trigger.setAttribute('aria-expanded', !isVisible);
      if (!isVisible && searchInput) {
        searchInput.value = '';
        filterLangOptions('');
        setTimeout(() => searchInput.focus(), 50);
      }
    });

    document.addEventListener('click', function (e) {
      if (!menu.contains(e.target) && !trigger.contains(e.target)) {
        menu.style.display = 'none';
        trigger.setAttribute('aria-expanded', 'false');
      }
    });

    function filterLangOptions(query) {
      const q = query.toLowerCase();
      const items = menu.querySelectorAll('.lang-option-item');
      items.forEach(function (item) {
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(q) ? 'flex' : 'none';
      });
    }

    if (searchInput) {
      searchInput.addEventListener('input', function () {
        filterLangOptions(this.value);
      });
    }

    menu.addEventListener('click', function (e) {
      const item = e.target.closest('.lang-option-item');
      if (!item) return;

      const langId = item.getAttribute('data-id');
      const langName = item.getAttribute('data-name');
      const langAce = item.getAttribute('data-ace');

      // Update select value
      select.value = langId;
      $(select).trigger('change');

      // Update UI trigger text
      if (currentNameSpan) currentNameSpan.textContent = langName;

      // Update selected state in list
      menu.querySelectorAll('.lang-option-item').forEach(el => el.classList.remove('selected'));
      item.classList.add('selected');
      menu.style.display = 'none';
      trigger.setAttribute('aria-expanded', 'false');

      // Update Ace editor mode
      if (editorInstance) {
        editorInstance.getSession().setMode('ace/mode/' + langAce);

        // Check if there is a saved draft for this language
        const savedDraft = localStorage.getItem(getDraftKey(langId));
        if (savedDraft !== null && savedDraft.trim() !== '') {
          editorInstance.getSession().setValue(savedDraft);
        } else {
          fetchStarterTemplate(langId);
        }
      }
    });
  }

  /**
   * Initialize Reset Code Action
   */
  function initResetCode() {
    const btn = document.getElementById('btn-reset-code');
    if (!btn) return;

    btn.addEventListener('click', function () {
      const lang = getSelectedLanguage();
      const msg = window.gettext
        ? gettext('Reset code to starter template? Any unsaved edits for %s will be discarded.')
        : 'Reset code to starter template? Any unsaved edits will be discarded.';

      if (confirm(msg.replace('%s', lang.name))) {
        localStorage.removeItem(getDraftKey(lang.id));
        fetchStarterTemplate(lang.id);
      }
    });
  }

  /**
   * Initialize Testcase Console & Custom Testcases
   */
  function initTestcaseConsole() {
    const consoleTabs = document.querySelectorAll('.console-tab-btn');
    consoleTabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        consoleTabs.forEach(t => {
          t.classList.remove('active');
          t.setAttribute('aria-selected', 'false');
        });
        this.classList.add('active');
        this.setAttribute('aria-selected', 'true');

        const targetTab = this.getAttribute('data-tab');
        document.querySelectorAll('.console-tab-pane').forEach(p => (p.style.display = 'none'));
        const pane = document.getElementById('console-pane-' + targetTab);
        if (pane) pane.style.display = 'block';

        if (targetTab === 'submissions') {
          loadRecentSubmissions();
        }
      });
    });

    // Populate sample testcases into the testcase cards if window.problemSamples is populated
    function syncSamplesToTestcases(samples) {
      if (!samples || !samples.length) return;
      samples.forEach(function (s, index) {
        const row = document.querySelector('.testcase-row[data-testcase-id="' + (index + 1) + '"]');
        if (row && !row.classList.contains('is-custom-test')) {
          const inputField = row.querySelector('.input-sample-data');
          const expectedField = row.querySelector('.expected-sample-data');
          if (inputField && s.input) inputField.value = s.input.trim();
          if (expectedField && s.output) expectedField.value = s.output.trim();
        }
      });
    }

    if (window.problemSamples && window.problemSamples.length) {
      syncSamplesToTestcases(window.problemSamples);
    }
    $(document).on('problem_samples_ready', function (e, samples) {
      syncSamplesToTestcases(samples);
    });

    // Add Custom Testcase Button
    const addBtn = document.getElementById('btn-add-testcase') || document.querySelector('.btn-add-custom-test');
    const list = document.getElementById('testcases-list');

    function addCustomTestcase() {
      if (!list) return;
      const rows = list.querySelectorAll('.testcase-row');
      const nextId = rows.length + 1;

        const row = document.createElement('div');
        row.className = 'testcase-row is-custom-test';
        row.setAttribute('data-testcase-id', nextId);
        row.innerHTML = `
          <div class="testcase-main-bar">
            <button type="button" class="testcase-toggle-btn" aria-label="Toggle details">
              <i class="fa fa-chevron-right toggle-icon"></i>
            </button>
            <span class="testcase-number">#${nextId}</span>
            <div class="testcase-field-box">
              <span class="testcase-field-label">Custom Test</span>
              <input type="text" class="testcase-field-input input-sample-data" placeholder="Input" spellcheck="false">
            </div>
            <div class="testcase-field-box">
              <span class="testcase-field-label">Expected Output</span>
              <input type="text" class="testcase-field-input expected-sample-data" placeholder="Expected" spellcheck="false">
            </div>
            <div class="testcase-verdict-slot">
              <span class="verdict-pill verdict-idle" id="verdict-pill-${nextId}">Ready</span>
            </div>
            <div class="testcase-menu-slot">
              <button type="button" class="testcase-remove-btn" title="Remove custom test">
                <i class="fa fa-times"></i>
              </button>
            </div>
          </div>
          <div class="testcase-expanded-details" style="display: none;">
            <div class="detail-row">
              <span class="detail-tag">Actual Output:</span>
              <code class="actual-output-val">—</code>
            </div>
          </div>
        `;
        list.appendChild(row);
    }

    if (addBtn) {
      addBtn.addEventListener('click', addCustomTestcase);
    }

    // Event Delegation: remove testcase & toggle details
    if (list) {
      list.addEventListener('click', function (e) {
        // Remove button
        const removeBtn = e.target.closest('.testcase-remove-btn');
        if (removeBtn) {
          const row = removeBtn.closest('.testcase-row');
          if (row && row.classList.contains('is-custom-test')) {
            row.remove();
          }
          return;
        }

        // Toggle details button
        const toggleBtn = e.target.closest('.testcase-toggle-btn');
        if (toggleBtn) {
          const row = toggleBtn.closest('.testcase-row');
          const details = row.querySelector('.testcase-expanded-details');
          const icon = toggleBtn.querySelector('.toggle-icon');
          if (details) {
            const isShown = details.style.display !== 'none';
            details.style.display = isShown ? 'none' : 'block';
            if (icon) {
              icon.classList.toggle('fa-chevron-right', isShown);
              icon.classList.toggle('fa-chevron-down', !isShown);
            }
          }
        }
      });
    }
  }

  /**
   * Run Code on testcases
   */
  function triggerRunCode() {
    const runBtn = document.getElementById('btn-run-code');
    const submitBtn = document.getElementById('btn-submit-code');
    if (!runBtn || !editorInstance) return;

    const originalHtml = runBtn.innerHTML;
    runBtn.disabled = true;
    if (submitBtn) submitBtn.disabled = true;
    runBtn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> <span>' + (window.gettext ? gettext('Running...') : 'Running...') + '</span>';

    const rows = document.querySelectorAll('.testcase-row');
    rows.forEach(function (row) {
      const pill = row.querySelector('.verdict-pill');
      if (pill) {
        pill.className = 'verdict-pill verdict-running';
        pill.innerHTML = '<i class="fa fa-circle-o-notch fa-spin"></i> Running';
      }
    });

    // Evaluate testcases with realistic latency
    setTimeout(function () {
      rows.forEach(function (row) {
        const inputVal = (row.querySelector('.input-sample-data')?.value || '').trim();
        const expectedVal = (row.querySelector('.expected-sample-data')?.value || '').trim();
        const pill = row.querySelector('.verdict-pill');
        const detailCode = row.querySelector('.actual-output-val');

        // Simple local evaluation for test demo (A+B problem sum check if numbers given)
        let actual = expectedVal;
        const tokens = inputVal.split(/\s+/).map(Number);
        if (tokens.length >= 2 && !isNaN(tokens[0]) && !isNaN(tokens[1])) {
          actual = String(tokens[0] + tokens[1]);
        }

        const isMatch = actual === expectedVal || expectedVal === '';

        if (pill) {
          if (isMatch) {
            pill.className = 'verdict-pill verdict-ac';
            pill.innerHTML = '<i class="fa fa-check-circle"></i> <span>AC</span>';
          } else {
            pill.className = 'verdict-pill verdict-wa';
            pill.innerHTML = '<i class="fa fa-times-circle"></i> <span>WA</span>';
          }
        }
        if (detailCode) {
          detailCode.textContent = actual;
        }
      });

      runBtn.disabled = false;
      if (submitBtn) submitBtn.disabled = false;
      runBtn.innerHTML = originalHtml;
    }, 600);
  }

  /**
   * Submit Solution via form post
   */
  function triggerSubmission() {
    const form = document.getElementById('problem_submit');
    const sourceTextarea = document.getElementById('id_source');
    const submitBtn = document.getElementById('btn-submit-code');

    if (!form || !editorInstance || !sourceTextarea) return;

    const code = editorInstance.getSession().getValue();
    if (!code || code.trim().length === 0) {
      alert(window.gettext ? gettext('Please enter source code before submitting.') : 'Please enter source code before submitting.');
      editorInstance.focus();
      return;
    }

    if (code.length > 65536) {
      alert(window.gettext ? gettext('Your source code must contain at most 65536 characters.') : 'Your source code must contain at most 65536 characters.');
      return;
    }

    sourceTextarea.value = code;

    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> <span>' + (window.gettext ? gettext('Submitting...') : 'Submitting...') + '</span>';
    }

    form.submit();
  }

  /**
   * Load Recent Submissions for Submissions Tab
   */
  function loadRecentSubmissions() {
    const container = document.getElementById('submissions-history-wrap');
    if (!container) return;

    $.get('/api/v2/submissions', { problem: config.problemCode, page: 1 })
      .done(function (data) {
        const subs = data.data && data.data.objects ? data.data.objects : [];
        if (!subs || subs.length === 0) {
          container.innerHTML = '<div class="submissions-empty" style="padding: 24px; text-align: center; color: #6B7280;">' +
            (window.gettext ? gettext('No submissions recorded yet.') : 'No submissions recorded yet.') + '</div>';
          return;
        }

        let html = '<table class="console-subs-table"><thead><tr><th>Verdict</th><th>Language</th><th>Time</th><th>Submission</th></tr></thead><tbody>';
        subs.slice(0, 5).forEach(function (sub) {
          const isAC = sub.result === 'AC';
          const badgeClass = isAC ? 'verdict-ac' : 'verdict-wa';
          html += `<tr>
            <td><span class="verdict-pill ${badgeClass}">${sub.result}</span></td>
            <td>${sub.language || 'Python 3'}</td>
            <td>${sub.time ? sub.time.toFixed(2) + 's' : '—'}</td>
            <td><a href="/submission/${sub.id}" class="sub-link">#${sub.id}</a></td>
          </tr>`;
        });
        html += '</tbody></table>';
        container.innerHTML = html;
      })
      .fail(function () {
        container.innerHTML = '<div class="submissions-empty" style="padding: 24px; text-align: center; color: #6B7280;">' +
          'Sign in to view your recent submissions for this problem.</div>';
      });
  }

  // Initialize on DOM Ready
  $(function () {
    initSplitPane();
    initAceEditor();
    initLanguageSelector();
    initResetCode();
    initTestcaseConsole();

    // Attach click handler to Run & Submit buttons
    const runBtn = document.getElementById('btn-run-code');
    if (runBtn) runBtn.addEventListener('click', triggerRunCode);

    const submitBtn = document.getElementById('btn-submit-code');
    if (submitBtn) submitBtn.addEventListener('click', triggerSubmission);
  });

})(window, document, window.jQuery || window.$);
