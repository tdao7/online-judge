/**
 * VCODER macOS Design System — Screen 3 Controller
 * Submissions Catalog: Multi-filter dropdowns, active row selection highlight,
 * drawer state coordination, and real-time live WebSocket update integration.
 */
(function (window, document) {
  'use strict';

  function initSubmissionsController() {
    var filterForm = document.getElementById('submissions-filter-form');
    var pageLayout = document.getElementById('submissions-page-layout');
    var btnCloseDrawer = document.getElementById('btn-close-drawer');
    var drawerTitle = document.getElementById('submission-drawer-title');

    // ------------------------------------------------------------------------
    // 1. Dropdown Toggle Listeners (with Outside Click Closure)
    // ------------------------------------------------------------------------
    var dropdowns = document.querySelectorAll('.filter-dropdown');
    document.addEventListener('click', function (e) {
      var clickedTrigger = e.target.closest('.filter-dropdown-btn');
      if (clickedTrigger) {
        e.preventDefault();
        e.stopPropagation();
        var parentDropdown = clickedTrigger.closest('.filter-dropdown');
        dropdowns.forEach(function (d) {
          if (d !== parentDropdown) d.classList.remove('open');
        });
        parentDropdown.classList.toggle('open');
      } else if (!e.target.closest('.filter-dropdown-menu')) {
        dropdowns.forEach(function (d) {
          d.classList.remove('open');
        });
      }
    });

    // ------------------------------------------------------------------------
    // 2. Dropdown Item Selection -> Form Submission
    // ------------------------------------------------------------------------
    document.addEventListener('click', function (e) {
      var item = e.target.closest('.dropdown-item');
      if (item && filterForm) {
        var filterType = item.getAttribute('data-filter');
        var val = item.getAttribute('data-value');

        if (filterType) {
          var targetInput = document.getElementById('filter-' + filterType);
          if (targetInput) {
            targetInput.value = val;
            filterForm.submit();
          }
        }
      }
    });

    // ------------------------------------------------------------------------
    // 3. Problem Dropdown Real-Time Search Filter
    // ------------------------------------------------------------------------
    var problemSearchInput = document.getElementById('problem-filter-search');
    if (problemSearchInput) {
      problemSearchInput.addEventListener('input', function () {
        var q = this.value.toLowerCase().trim();
        var problemItems = document.querySelectorAll('#problem-options-list .dropdown-item');
        problemItems.forEach(function (item) {
          var label = (item.getAttribute('data-label') || item.textContent || '').toLowerCase();
          if (!q || label.indexOf(q) !== -1) {
            item.style.display = '';
          } else {
            item.style.display = 'none';
          }
        });
      });
    }

    // ------------------------------------------------------------------------
    // 4. Submissions Table Row Click Selection & Drawer Coordination
    // ------------------------------------------------------------------------
    var tbody = document.getElementById('submissions-tbody');
    if (tbody) {
      tbody.addEventListener('click', function (e) {
        // Do not intercept clicks on links or interactive buttons inside the row
        if (e.target.closest('a') || e.target.closest('button')) {
          return;
        }

        var row = e.target.closest('tr.submission-row');
        if (row) {
          var submissionId = row.getAttribute('data-submission-id');
          if (!submissionId) return;

          // Toggle selection: if already selected, close; otherwise select
          var isAlreadySelected = row.classList.contains('selected');
          document.querySelectorAll('tr.submission-row').forEach(function (r) {
            r.classList.remove('selected', 'active');
          });

          if (isAlreadySelected && pageLayout && pageLayout.classList.contains('drawer-open')) {
            pageLayout.classList.remove('drawer-open');
            window.dispatchEvent(new CustomEvent('vcoder:drawer-closed'));
          } else {
            row.classList.add('selected', 'active');
            if (drawerTitle) {
              drawerTitle.textContent = '#' + submissionId;
            }
            if (pageLayout) {
              pageLayout.classList.add('drawer-open');
            }

            // Emit custom selection event for Drawer Controller (Screen 3 Drawer / Explorer 2)
            window.dispatchEvent(new CustomEvent('vcoder:submission-selected', {
              detail: {
                id: submissionId,
                problemCode: row.getAttribute('data-problem-code'),
                user: row.getAttribute('data-user'),
                row: row
              }
            }));
          }
        }
      });
    }

    // ------------------------------------------------------------------------
    // 5. Drawer Close Action
    // ------------------------------------------------------------------------
    if (btnCloseDrawer) {
      btnCloseDrawer.addEventListener('click', function () {
        if (pageLayout) {
          pageLayout.classList.remove('drawer-open');
        }
        document.querySelectorAll('tr.submission-row').forEach(function (r) {
          r.classList.remove('selected', 'active');
        });
        window.dispatchEvent(new CustomEvent('vcoder:drawer-closed'));
      });
    }

    // ------------------------------------------------------------------------
    // 6. External Event Listeners & Keyboard Accessibility (Esc to close)
    // ------------------------------------------------------------------------
    window.addEventListener('vcoder:close-submission-drawer', function () {
      if (pageLayout) {
        pageLayout.classList.remove('drawer-open');
      }
      document.querySelectorAll('tr.submission-row').forEach(function (r) {
        r.classList.remove('selected', 'active');
      });
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        if (pageLayout && pageLayout.classList.contains('drawer-open')) {
          pageLayout.classList.remove('drawer-open');
          document.querySelectorAll('tr.submission-row').forEach(function (r) {
            r.classList.remove('selected', 'active');
          });
          window.dispatchEvent(new CustomEvent('vcoder:drawer-closed'));
        }
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSubmissionsController);
  } else {
    initSubmissionsController();
  }
})(window, document);
