/**
 * VCODER macOS Design System — Screen 1 Controller
 * Problems Catalog: multi-dropdowns, client-side bookmarking, quick filter pills.
 */
(function (window, document) {
  'use strict';

  var BOOKMARK_STORAGE_KEY = 'vcoder_bookmarked_problems';

  function getBookmarks() {
    try {
      return JSON.parse(localStorage.getItem(BOOKMARK_STORAGE_KEY) || '[]');
    } catch (e) {
      return [];
    }
  }

  function setBookmarks(bookmarks) {
    try {
      localStorage.setItem(BOOKMARK_STORAGE_KEY, JSON.stringify(bookmarks));
    } catch (e) {}
  }

  function toggleBookmark(code) {
    var list = getBookmarks();
    var idx = list.indexOf(code);
    if (idx === -1) {
      list.push(code);
    } else {
      list.splice(idx, 1);
    }
    setBookmarks(list);
    return idx === -1; // true if now bookmarked
  }

  function updateBookmarkUI() {
    var bookmarks = getBookmarks();
    var starButtons = document.querySelectorAll('.btn-star');
    starButtons.forEach(function (btn) {
      var code = btn.getAttribute('data-code');
      if (bookmarks.indexOf(code) !== -1) {
        btn.classList.add('active');
        btn.setAttribute('aria-pressed', 'true');
      } else {
        btn.classList.remove('active');
        btn.setAttribute('aria-pressed', 'false');
      }
    });

    var badge = document.getElementById('bookmark-count-badge');
    if (badge) {
      if (bookmarks.length > 0) {
        badge.textContent = bookmarks.length;
        badge.style.display = 'inline-block';
      } else {
        badge.style.display = 'none';
      }
    }
  }

  function applyBookmarkFilter() {
    var bookmarks = getBookmarks();
    var pillButtons = document.querySelectorAll('.pill-tab-item, .filter-pill');
    pillButtons.forEach(function (p) {
      var s = p.getAttribute('data-status') || p.getAttribute('data-filter');
      if (s === 'bookmarked') {
        p.classList.add('active');
      } else {
        p.classList.remove('active');
      }
    });

    var rows = document.querySelectorAll('.problem-row');
    rows.forEach(function (row) {
      var code = row.getAttribute('data-code');
      if (bookmarks.indexOf(code) !== -1) {
        row.style.display = '';
      } else {
        row.style.display = 'none';
      }
    });

    var statusInput = document.getElementById('filter-status');
    if (statusInput) {
      statusInput.value = 'bookmarked';
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    var filterForm = document.getElementById('problems-filter-form');
    var statusInput = document.getElementById('filter-status');
    var orderInput = document.getElementById('filter-order');
    var difficultyInput = document.getElementById('filter-difficulty');
    var typeInput = document.getElementById('filter-type');
    var categoryInput = document.getElementById('filter-category');
    var groupInput = document.getElementById('filter-group');
    var pointsInput = document.getElementById('filter-points-preset');

    // Initialize bookmark states
    updateBookmarkUI();

    // Check if Bookmarked tab should be active on page load
    var urlHasBookmark = false;
    try {
      if (window.location && window.location.search) {
        if (typeof URLSearchParams !== 'undefined') {
          urlHasBookmark = new URLSearchParams(window.location.search).get('status') === 'bookmarked';
        } else {
          urlHasBookmark = window.location.search.indexOf('status=bookmarked') !== -1;
        }
      }
    } catch (e) {}

    var activePill = document.querySelector('.pill-tab-item.active, .filter-pill.active');
    var isBookmarkedActive = (activePill && (activePill.getAttribute('data-status') === 'bookmarked' || activePill.getAttribute('data-filter') === 'bookmarked')) || (statusInput && statusInput.value === 'bookmarked');

    if (urlHasBookmark || isBookmarkedActive) {
      applyBookmarkFilter();
    }

    // Bookmark star toggle click listener
    document.addEventListener('click', function (e) {
      var starBtn = e.target.closest('.btn-star');
      if (starBtn) {
        e.preventDefault();
        var code = starBtn.getAttribute('data-code');
        toggleBookmark(code);
        updateBookmarkUI();

        // If currently on Bookmarked filter tab, toggle row visibility
        var curPill = document.querySelector('.pill-tab-item.active, .filter-pill.active');
        if (curPill && (curPill.getAttribute('data-status') === 'bookmarked' || curPill.getAttribute('data-filter') === 'bookmarked')) {
          var row = starBtn.closest('tr');
          if (row) {
            row.style.display = getBookmarks().indexOf(code) === -1 ? 'none' : '';
          }
        }
      }
    });

    // Dropdown toggle listeners
    var dropdowns = document.querySelectorAll('.filter-dropdown, .actions-dropdown');
    document.addEventListener('click', function (e) {
      var clickedTrigger = e.target.closest('.filter-dropdown-btn, .btn-actions-toggle');
      if (clickedTrigger) {
        e.preventDefault();
        e.stopPropagation();
        var parentDropdown = clickedTrigger.closest('.filter-dropdown, .actions-dropdown');
        dropdowns.forEach(function (d) {
          if (d !== parentDropdown) d.classList.remove('open');
        });
        parentDropdown.classList.toggle('open');
      } else if (!e.target.closest('.filter-dropdown-menu, .actions-menu')) {
        dropdowns.forEach(function (d) {
          d.classList.remove('open');
        });
      }
    });

    // Dropdown option selection
    document.addEventListener('click', function (e) {
      var option = e.target.closest('.dropdown-item');
      if (option && filterForm) {
        var filterType = option.getAttribute('data-filter');
        var sortVal = option.getAttribute('data-sort');
        var val = option.getAttribute('data-value');

        if (filterType === 'difficulty' && difficultyInput) {
          difficultyInput.value = val;
          filterForm.submit();
        } else if (filterType === 'type' && typeInput) {
          typeInput.value = val;
          var tagCheckboxes = document.querySelectorAll('#tags-list input[type="checkbox"][name="type"]');
          tagCheckboxes.forEach(function (cb) {
            cb.checked = (val !== '' && cb.value === String(val));
          });
          filterForm.submit();
        } else if (filterType === 'category') {
          if (categoryInput) categoryInput.value = val;
          if (groupInput) groupInput.value = val;
          filterForm.submit();
        } else if (filterType === 'points_preset' && pointsInput) {
          pointsInput.value = val;
          filterForm.submit();
        } else if (sortVal && orderInput) {
          orderInput.value = sortVal;
          filterForm.submit();
        }
      }
    });

    // Sort order direction toggle button (⇅)
    var btnSortToggle = document.getElementById('btn-sort-toggle');
    if (btnSortToggle && orderInput && filterForm) {
      btnSortToggle.addEventListener('click', function (e) {
        e.preventDefault();
        var curOrder = orderInput.value || 'code';
        if (curOrder.startsWith('-')) {
          orderInput.value = curOrder.substring(1);
        } else {
          orderInput.value = '-' + curOrder;
        }
        filterForm.submit();
      });
    }

    // Quick filter pills listener
    var pillButtons = document.querySelectorAll('.pill-tab-item, .filter-pill');
    pillButtons.forEach(function (pill) {
      pill.addEventListener('click', function (e) {
        e.preventDefault();
        var status = pill.getAttribute('data-status') || pill.getAttribute('data-filter');
        if (status === 'bookmarked') {
          applyBookmarkFilter();
          try {
            if (window.history && window.history.replaceState && window.location) {
              var url = new URL(window.location.href);
              url.searchParams.set('status', 'bookmarked');
              window.history.replaceState(null, '', url.toString());
            }
          } catch (err) {}
        } else {
          if (statusInput && filterForm) {
            statusInput.value = status;
            filterForm.submit();
          }
        }
      });
    });

    // Apply button for Tags dropdown: disable single type input so tag checkboxes submit cleanly
    var btnApplyTags = document.querySelector('.btn-apply-filters');
    if (btnApplyTags && typeInput) {
      btnApplyTags.addEventListener('click', function () {
        typeInput.disabled = true;
      });
    }

    // Tag search filter inside tag dropdown
    var tagSearchInput = document.getElementById('tag-filter-search');
    if (tagSearchInput) {
      tagSearchInput.addEventListener('input', function () {
        var query = this.value.toLowerCase().trim();
        var items = document.querySelectorAll('.tag-checkbox-item');
        items.forEach(function (item) {
          var label = item.textContent.toLowerCase();
          item.style.display = label.indexOf(query) !== -1 ? 'flex' : 'none';
        });
      });
    }

    // Clear search button
    var clearBtn = document.getElementById('btn-clear-search');
    if (clearBtn) {
      clearBtn.addEventListener('click', function () {
        var searchInput = document.getElementById('search');
        if (searchInput && filterForm) {
          searchInput.value = '';
          filterForm.submit();
        }
      });
    }
  });
})(window, document);
