/**
 * VCODER macOS Design System — Screen 3: Detail Drawer Controller (Mockup docs/3.png)
 * Slide-out Inspector Panel, Row Selection, AJAX Loader, Tabs & Keyboard Bindings
 */
(function (window, document, $) {
  'use strict';

  var DRAWER_ID = 'submission-detail-drawer';
  var DRAWER_CONTENT_ID = 'submission-detail-drawer-content';
  var BACKDROP_ID = 'submission-drawer-backdrop';
  var ENDPOINT_URL = '/widgets/submission_drawer';

  var state = {
    isOpen: false,
    activeSubmissionId: null,
    isLoading: false,
    xhr: null,
  };

  /**
   * DOM Elements Helper Cache
   */
  function getElements() {
    return {
      drawer: document.getElementById(DRAWER_ID),
      drawerContent: document.getElementById(DRAWER_CONTENT_ID),
      backdrop: document.getElementById(BACKDROP_ID),
      tableWrap: document.getElementById('submissions-table-pane') || document.getElementById('submissions-table'),
    };
  }

  /**
   * Render loading skeleton while fetching submission data
   */
  function renderSkeleton(submissionId) {
    var els = getElements();
    if (!els.drawerContent) return;

    els.drawerContent.innerHTML =
      '<div class="drawer-inner">' +
        '<div class="drawer-header">' +
          '<div class="drawer-header-top">' +
            '<h2 class="drawer-submission-id">#' + submissionId + '</h2>' +
            '<button type="button" class="drawer-close-btn" id="drawer-close-btn" aria-label="Close">' +
              '<i class="fa fa-times"></i>' +
            '</button>' +
          '</div>' +
          '<div class="drawer-loading-skeleton">' +
            '<div class="skeleton-header"></div>' +
            '<div class="skeleton-card"></div>' +
            '<div class="skeleton-grid">' +
              '<div class="skeleton-box"></div>' +
              '<div class="skeleton-box"></div>' +
              '<div class="skeleton-box"></div>' +
              '<div class="skeleton-box"></div>' +
            '</div>' +
          '</div>' +
        '</div>' +
      '</div>';

    // Bind close button on skeleton
    var closeBtn = document.getElementById('drawer-close-btn');
    if (closeBtn) {
      closeBtn.addEventListener('click', function (e) {
        e.preventDefault();
        close();
      });
    }
  }

  /**
   * Update active row highlight in submissions table
   */
  function highlightTableRow(submissionId) {
    // Clear existing active rows
    var prevActive = document.querySelectorAll('.submission-row.active-drawer-row, tr.active-drawer-row');
    prevActive.forEach(function (el) {
      el.classList.remove('active-drawer-row');
    });

    if (!submissionId) return;

    // Find row by data-submission-id or id
    var selector = '[data-submission-id="' + submissionId + '"], #sub-' + submissionId + ', #' + submissionId;
    var row = document.querySelector(selector);
    if (row) {
      row.classList.add('active-drawer-row');
      // Scroll into view if needed
      if (typeof row.scrollIntoViewIfNeeded === 'function') {
        row.scrollIntoViewIfNeeded(false);
      }
    }
  }

  /**
   * Bind event handlers inside freshly rendered drawer content
   */
  function bindDrawerInteractions() {
    // 1. Close button
    var closeBtn = document.getElementById('drawer-close-btn');
    if (closeBtn) {
      closeBtn.addEventListener('click', function (e) {
        e.preventDefault();
        close();
      });
    }

    // 2. Tab switching (Source Code / Compile Log / Execution Log)
    var tabBtns = document.querySelectorAll('.drawer-tab-btn');
    tabBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var targetTab = this.getAttribute('data-tab');

        // Update active tab buttons
        tabBtns.forEach(function (b) {
          b.classList.remove('active');
          b.setAttribute('aria-selected', 'false');
        });
        this.classList.add('active');
        this.setAttribute('aria-selected', 'true');

        // Toggle pane visibility
        var panes = document.querySelectorAll('.drawer-tab-pane');
        panes.forEach(function (pane) {
          pane.classList.remove('active');
          pane.style.display = 'none';
        });

        var activePane = document.getElementById('pane-' + targetTab);
        if (activePane) {
          activePane.classList.add('active');
          activePane.style.display = 'block';
        }
      });
    });

    // 3. One-click Copy Code button
    var copyBtn = document.getElementById('btn-copy-code');
    if (copyBtn) {
      copyBtn.addEventListener('click', function () {
        var code = this.getAttribute('data-code');
        if (!code) {
          var codeEl = document.querySelector('.code-viewer-pre code');
          if (codeEl) code = codeEl.innerText;
        }

        if (!code) return;

        var btn = this;
        var copyText = btn.querySelector('.copy-text');
        var originalText = copyText ? copyText.textContent : 'Copy';

        function showCopied() {
          btn.classList.add('copied');
          if (copyText) copyText.textContent = 'Copied!';
          setTimeout(function () {
            btn.classList.remove('copied');
            if (copyText) copyText.textContent = originalText;
          }, 2000);
        }

        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(code).then(showCopied).catch(function () {
            fallbackCopy(code, showCopied);
          });
        } else {
          fallbackCopy(code, showCopied);
        }
      });
    }

    // 4. Testcase items click / diagnostics
    var testcaseItems = document.querySelectorAll('.testcase-item');
    testcaseItems.forEach(function (item) {
      item.addEventListener('click', function () {
        var caseNum = this.getAttribute('data-case-number');
        // Switch to Execution Log tab and scroll to corresponding row
        var execTabBtn = document.querySelector('.drawer-tab-btn[data-tab="execution"]');
        if (execTabBtn) {
          execTabBtn.click();
          var execRow = document.querySelector('.execution-table tr.exec-row-case-' + caseNum);
          if (execRow && typeof execRow.scrollIntoView === 'function') {
            execRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
            execRow.classList.add('highlight-row');
            setTimeout(function () {
              execRow.classList.remove('highlight-row');
            }, 1500);
          }
        }
      });
    });
  }

  /**
   * Clipboard fallback for legacy browsers
   */
  function fallbackCopy(text, callback) {
    var textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.top = '-9999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    try {
      document.execCommand('copy');
      if (typeof callback === 'function') callback();
    } catch (e) {
      console.warn('Fallback copy failed:', e);
    }
    document.body.removeChild(textArea);
  }

  /**
   * Open the detail drawer for a given submission ID
   */
  function open(submissionId) {
    if (!submissionId) return;

    var els = getElements();
    if (!els.drawer) {
      console.warn('[SubmissionDrawer] Drawer element #' + DRAWER_ID + ' not found in DOM.');
      return;
    }

    state.activeSubmissionId = submissionId;
    state.isOpen = true;

    // Highlight row in submissions table
    highlightTableRow(submissionId);

    // Slide open drawer
    els.drawer.classList.remove('closed');
    els.drawer.classList.add('open');
    els.drawer.setAttribute('aria-hidden', 'false');

    // Show backdrop if responsive width (< 1024px)
    if (els.backdrop && window.innerWidth < 1024) {
      els.backdrop.classList.add('active');
      els.backdrop.setAttribute('aria-hidden', 'false');
    }

    // Cancel ongoing XHR if any
    if (state.xhr && typeof state.xhr.abort === 'function') {
      state.xhr.abort();
    }

    // Render skeleton
    renderSkeleton(submissionId);
    state.isLoading = true;

    // Fetch submission drawer content via AJAX
    var requestUrl = ENDPOINT_URL + '?id=' + encodeURIComponent(submissionId);

    if (window.$ && typeof $.ajax === 'function') {
      state.xhr = $.ajax({
        url: requestUrl,
        type: 'GET',
        dataType: 'html',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
      }).done(function (html) {
        state.isLoading = false;
        if (state.activeSubmissionId === submissionId && els.drawerContent) {
          els.drawerContent.innerHTML = html;
          bindDrawerInteractions();
        }
      }).fail(function (xhr, status, error) {
        if (status === 'abort') return;
        state.isLoading = false;
        if (els.drawerContent) {
          els.drawerContent.innerHTML =
            '<div class="drawer-empty-state">' +
              '<div class="empty-icon"><i class="fa fa-exclamation-triangle text-warning"></i></div>' +
              '<div class="empty-title">Failed to load submission #' + submissionId + '</div>' +
              '<div class="empty-desc">Could not retrieve submission details. Please try again.</div>' +
            '</div>';
        }
      });
    } else {
      // Native fetch fallback
      fetch(requestUrl, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
      })
        .then(function (res) {
          if (!res.ok) throw new Error('Network error ' + res.status);
          return res.text();
        })
        .then(function (html) {
          state.isLoading = false;
          if (state.activeSubmissionId === submissionId && els.drawerContent) {
            els.drawerContent.innerHTML = html;
            bindDrawerInteractions();
          }
        })
        .catch(function (err) {
          state.isLoading = false;
          if (els.drawerContent) {
            els.drawerContent.innerHTML =
              '<div class="drawer-empty-state">' +
                '<div class="empty-icon"><i class="fa fa-exclamation-triangle"></i></div>' +
                '<div class="empty-title">Error loading submission</div>' +
                '<div class="empty-desc">' + err.message + '</div>' +
              '</div>';
          }
        });
    }
  }

  /**
   * Close the detail drawer
   */
  function close() {
    var els = getElements();
    state.isOpen = false;
    state.activeSubmissionId = null;

    if (els.drawer) {
      els.drawer.classList.remove('open');
      els.drawer.classList.add('closed');
      els.drawer.setAttribute('aria-hidden', 'true');
    }

    if (els.backdrop) {
      els.backdrop.classList.remove('active');
      els.backdrop.setAttribute('aria-hidden', 'true');
    }

    // Remove active highlight from all rows
    highlightTableRow(null);

    // Cancel ongoing XHR
    if (state.xhr && typeof state.xhr.abort === 'function') {
      state.xhr.abort();
    }
  }

  /**
   * Toggle detail drawer
   */
  function toggle(submissionId) {
    if (state.isOpen && state.activeSubmissionId === submissionId) {
      close();
    } else {
      open(submissionId);
    }
  }

  /**
   * WebSocket live update hook
   * If the submission currently displayed in the drawer receives a live grading event,
   * dynamically update testcase pills and status without destroying user selection.
   */
  function handleLiveEvent(message) {
    if (!state.isOpen || !state.activeSubmissionId) return;
    if (String(message.submission || message.id) !== String(state.activeSubmissionId)) return;

    // Refresh drawer content smoothly
    if (message.type === 'update-submission' || message.type === 'done-submission' || message.type === 'test-case') {
      open(state.activeSubmissionId);
    }
  }

  /**
   * Bind global table click delegation and keyboard shortcuts
   */
  function init() {
    // 1. Row click delegation on submissions table
    document.addEventListener('click', function (e) {
      // Ignore clicks on links, buttons, inputs or their children
      var interactiveEl = e.target.closest('a, button, input, select, label, form, .sub-prop, .copy-btn');
      if (interactiveEl) {
        // If clicking close button inside drawer, handled separately
        return;
      }

      // Check if click was inside a submission row
      var row = e.target.closest('.submission-row, tr[data-submission-id], .submissions-table-row');
      if (row) {
        var subId = row.getAttribute('data-submission-id') || row.getAttribute('id');
        if (subId) {
          subId = subId.replace(/^sub-/, '');
          if (/^\d+$/.test(subId)) {
            e.preventDefault();
            toggle(parseInt(subId, 10));
          }
        }
      }
    });

    // 2. Backdrop click dismisses drawer
    var els = getElements();
    if (els.backdrop) {
      els.backdrop.addEventListener('click', function () {
        close();
      });
    }

    // 3. Escape key dismisses drawer
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' || e.keyCode === 27) {
        if (state.isOpen) {
          close();
        }
      }
    });

    // 4. Window resize handler
    window.addEventListener('resize', function () {
      var els = getElements();
      if (!els.backdrop) return;
      if (window.innerWidth >= 1024 && els.backdrop.classList.contains('active')) {
        els.backdrop.classList.remove('active');
      } else if (window.innerWidth < 1024 && state.isOpen) {
        els.backdrop.classList.add('active');
      }
    });
  }

  // Self-initialize on DOMContentLoaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Public API Export
  window.SubmissionDrawer = {
    open: open,
    close: close,
    toggle: toggle,
    isOpen: function () {
      return state.isOpen;
    },
    getActiveId: function () {
      return state.activeSubmissionId;
    },
    handleLiveEvent: handleLiveEvent,
  };

})(window, document, window.jQuery || null);
