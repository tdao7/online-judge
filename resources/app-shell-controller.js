/**
 * DMOJ Modern macOS Floating App Shell Controller
 * Milestone 2 — Design System & Interactive Shell Engine
 *
 * Provides vanilla JavaScript handlers for:
 * 1. Global ⌘K / Ctrl+K keyboard shortcut listener & quick search modal.
 * 2. Mobile hamburger drawer navigation & touch swipe-left closing.
 * 3. User profile avatar dropdown menu.
 * 4. Notification bell popover toggle.
 */
(function (window, document) {
  'use strict';

  // Defensive configuration & runtime state
  const state = {
    isMac: /Mac|iPod|iPhone|iPad/.test(navigator.platform || navigator.userAgent),
    searchModalOpen: false,
    drawerOpen: false,
    userDropdownOpen: false,
    lastFocusedElement: null,
    selectedIndex: 0,
    activeTab: 'all',
  };

  /**
   * Helper to query single element from multiple candidate selectors
   */
  function queryOne(selectors) {
    for (let i = 0; i < selectors.length; i++) {
      const el = document.querySelector(selectors[i]);
      if (el) return el;
    }
    return null;
  }

  /**
   * Helper to query all matching elements
   */
  function queryAll(selector) {
    return Array.from(document.querySelectorAll(selector));
  }

  /**
   * Lazy element resolver
   */
  function getElements() {
    return {
      // Topbar Search & Mobile Triggers
      globalSearchTrigger: queryOne(['#global-search-trigger', '.header-search-pill', '.search-pill']),
      mobileSearchBtn: queryOne(['#mobile-search-trigger', '#mobile-search-btn']),
      searchKbdBadge: queryOne(['#search-kbd-badge', '.kbd-badge', '.search-kbd', '.key-badge']),

      // Quick Search Modal Elements
      searchModalRoot: queryOne(['#global-search-modal', '#quick-search-modal', '.quick-search-modal-root']),
      searchBackdrop: queryOne(['#quick-search-backdrop', '.modal-backdrop', '.mac-modal-backdrop']),
      searchInput: queryOne(['#modal-search-input', '#quick-search-input']),
      searchResults: queryOne(['#modal-search-results', '#quick-search-results']),
      searchCloseBtn: queryOne(['#modal-search-close', '#quick-search-close-btn']),
      searchTabChips: queryAll('.search-tab-chip'),

      // Mobile Hamburger & Sidebar Drawer
      hamburgerBtn: queryOne(['#mobile-nav-toggle', '#mobile-hamburger', '.mobile-nav-toggle']),
      appSidebar: queryOne(['#navigation', '#app-sidebar', '.app-sidebar']),
      sidebarBackdrop: queryOne(['#sidebar-backdrop', '.sidebar-backdrop', '.drawer-backdrop']),
      sidebarCloseBtn: queryOne(['#sidebar-close-btn']),
      sidebarNavLinks: queryAll('.app-sidebar a, .sidebar-nav-link, .nav-item'),

      // User Profile Dropdown
      userMenuTrigger: queryOne(['#user-pill-trigger', '#user-menu-trigger', '.user-pill-trigger']),
      userMenuDropdown: queryOne(['#user-dropdown-menu', '#user-menu-dropdown', '.user-dropdown-menu']),
      userDropdownContainer: queryOne(['#user-pill-dropdown', '#user-menu-dropdown-container', '.user-pill-dropdown']),

      // Notification Bell
      notificationBtn: queryOne(['#notification-bell', '#notification-bell-btn']),
      notificationDropdown: queryOne(['#notification-dropdown']),
    };
  }

  /* ==========================================================================
     1. Platform-Aware Keycap Badge Formatting
     ========================================================================== */
  function updateKeycapPlatformBadge(elements) {
    if (elements.searchKbdBadge) {
      if (state.isMac) {
        elements.searchKbdBadge.innerHTML = '<kbd>⌘</kbd><kbd>K</kbd>';
      } else {
        elements.searchKbdBadge.innerHTML = '<kbd>Ctrl</kbd><kbd>K</kbd>';
      }
    }
  }

  /* ==========================================================================
     2. Quick Search (⌘K) Modal Controller
     ========================================================================== */
  const searchIndex = [
    { type: 'problem', title: 'A Plus B', code: 'aplusb', group: 'DMOJ', points: '3 pts', url: '/problem/aplusb', tags: ['math', 'implementation'] },
    { type: 'problem', title: 'Binary Search Tree Balancing', code: 'bstbalance', group: 'DMOPC', points: '30 pts', url: '/problem/bstbalance', tags: ['trees', 'data structures'] },
    { type: 'problem', title: 'Shortest Path In Wonderland', code: 'wonderland', group: 'COCI', points: '20 pts', url: '/problem/wonderland', tags: ['graphs', 'shortest-path'] },
    { type: 'problem', title: 'Dynamic Matrix Exponentiation', code: 'matrixexp', group: 'IOI', points: '100 pts', url: '/problem/matrixexp', tags: ['dp', 'matrix'] },
    { type: 'contest', title: 'DMOJ Monthly Contest #8', status: 'Upcoming', url: '/contests/', meta: 'Upcoming' },
    { type: 'contest', title: 'Weekly Practice Cup #42', status: 'Live', url: '/contests/', meta: '● Live Now' },
    { type: 'user', title: 'tourist (Gennady Korotkevich)', handle: 'tourist', rating: '3421', url: '/users/' },
    { type: 'user', title: 'ecnerwala (Andrew He)', handle: 'ecnerwala', rating: '3287', url: '/users/' },
    { type: 'nav', title: 'Browse Problems', url: '/problems/', badge: 'Navigation' },
    { type: 'nav', title: 'Recent Submissions', url: '/submissions/', badge: 'Navigation' },
    { type: 'nav', title: 'Programming Contests', url: '/contests/', badge: 'Navigation' },
    { type: 'nav', title: 'Global Rankings & Users', url: '/users/', badge: 'Navigation' },
  ];

  function openSearchModal() {
    const el = getElements();
    if (state.searchModalOpen || !el.searchModalRoot) return;

    closeUserDropdown();
    closeDrawer();

    state.lastFocusedElement = document.activeElement;
    state.searchModalOpen = true;
    state.selectedIndex = 0;

    el.searchModalRoot.style.display = 'flex';
    el.searchModalRoot.classList.add('is-open');
    el.searchModalRoot.setAttribute('aria-hidden', 'false');
    document.body.classList.add('modal-open');

    if (el.searchInput) {
      el.searchInput.value = '';
      setTimeout(() => el.searchInput.focus(), 50);
    }

    renderSearchResults('');
  }

  function closeSearchModal() {
    const el = getElements();
    if (!state.searchModalOpen || !el.searchModalRoot) return;

    state.searchModalOpen = false;
    el.searchModalRoot.style.display = 'none';
    el.searchModalRoot.classList.remove('is-open');
    el.searchModalRoot.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('modal-open');

    if (state.lastFocusedElement && typeof state.lastFocusedElement.focus === 'function') {
      state.lastFocusedElement.focus();
    }
  }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  function highlightMatch(text, query) {
    if (!query) return escapeHtml(text);
    const safeText = escapeHtml(text);
    const safeQuery = escapeHtml(query);
    const regex = new RegExp(`(${safeQuery.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    return safeText.replace(regex, '<mark>$1</mark>');
  }

  function renderSearchResults(query) {
    const el = getElements();
    if (!el.searchResults) return;

    const trimmed = query.trim().toLowerCase();
    let filtered = searchIndex.filter(item => {
      if (state.activeTab !== 'all' && item.type !== state.activeTab) {
        return false;
      }
      if (!trimmed) return true;
      const titleMatch = item.title && item.title.toLowerCase().includes(trimmed);
      const codeMatch = item.code && item.code.toLowerCase().includes(trimmed);
      const handleMatch = item.handle && item.handle.toLowerCase().includes(trimmed);
      const tagMatch = item.tags && item.tags.some(t => t.toLowerCase().includes(trimmed));
      return titleMatch || codeMatch || handleMatch || tagMatch;
    });

    if (filtered.length === 0) {
      el.searchResults.innerHTML = `
        <div class="search-empty-state" style="padding: 24px; text-align: center; color: var(--color-text-muted, #6B7280);">
          No matching results found for "<strong>${escapeHtml(query)}</strong>".
        </div>
      `;
      return;
    }

    filtered = filtered.slice(0, 10);

    let html = '';
    if (!trimmed) {
      html += '<div class="quick-links-title" style="padding: 6px 12px; font-size: 11px; font-weight: 700; color: var(--color-text-muted, #6B7280); text-transform: uppercase;">Quick Navigation</div>';
    }

    filtered.forEach((item, index) => {
      const isSelected = index === state.selectedIndex;
      let iconClass = 'fa-file-text-o';
      let badgeHtml = '';

      if (item.type === 'problem') {
        iconClass = 'fa-file-text-o';
        badgeHtml = `<span class="row-badge" style="margin-left: auto; font-size: 11px; padding: 2px 8px; border-radius: 9999px; background: #F3F4F6;">${escapeHtml(item.points || '')}</span>`;
      } else if (item.type === 'contest') {
        iconClass = 'fa-trophy';
        badgeHtml = `<span class="row-badge" style="margin-left: auto; font-size: 11px; padding: 2px 8px; border-radius: 9999px; background: #FFF7ED; color: #F97316;">${escapeHtml(item.status || '')}</span>`;
      } else if (item.type === 'user') {
        iconClass = 'fa-user-circle-o';
        badgeHtml = `<span class="row-badge" style="margin-left: auto; font-size: 11px; padding: 2px 8px; border-radius: 9999px; background: #ECFDF5; color: #059669;">${escapeHtml(item.rating || '')}</span>`;
      } else {
        iconClass = 'fa-compass';
        badgeHtml = '<span class="quick-link-arrow" style="margin-left: auto; color: #9CA3AF;">&rarr;</span>';
      }

      html += `
        <a href="${item.url}" class="quick-link-row search-result-row ${isSelected ? 'is-selected' : ''}" data-index="${index}" role="option" aria-selected="${isSelected}">
          <i class="fa ${iconClass} fa-fw" aria-hidden="true"></i>
          <span class="row-title" style="margin-left: 8px;">${highlightMatch(item.title, trimmed)}</span>
          ${badgeHtml}
        </a>
      `;
    });

    el.searchResults.innerHTML = html;

    const rows = el.searchResults.querySelectorAll('.search-result-row');
    rows.forEach(row => {
      row.addEventListener('mouseenter', () => {
        const idx = parseInt(row.getAttribute('data-index'), 10);
        setSelectedResultIndex(idx);
      });
    });
  }

  function setSelectedResultIndex(index) {
    const el = getElements();
    const rows = el.searchResults ? el.searchResults.querySelectorAll('.search-result-row') : [];
    if (!rows.length) return;

    if (index < 0) index = rows.length - 1;
    if (index >= rows.length) index = 0;

    state.selectedIndex = index;
    rows.forEach((r, i) => {
      if (i === index) {
        r.classList.add('is-selected');
        r.setAttribute('aria-selected', 'true');
        r.scrollIntoView({ block: 'nearest' });
      } else {
        r.classList.remove('is-selected');
        r.setAttribute('aria-selected', 'false');
      }
    });
  }

  function handleSearchKeyboardNav(e) {
    const el = getElements();
    const rows = el.searchResults ? el.searchResults.querySelectorAll('.search-result-row') : [];
    if (!rows.length) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedResultIndex(state.selectedIndex + 1);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedResultIndex(state.selectedIndex - 1);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      const selectedRow = rows[state.selectedIndex];
      if (selectedRow) {
        window.location.href = selectedRow.getAttribute('href');
      }
    }
  }

  /* ==========================================================================
     3. Mobile Navigation Drawer Controller
     ========================================================================== */
  function openDrawer() {
    const el = getElements();
    if (state.drawerOpen || !el.appSidebar) return;

    closeUserDropdown();
    state.drawerOpen = true;
    document.body.classList.add('sidebar-open');

    el.appSidebar.classList.add('mobile-open');
    if (el.sidebarBackdrop) {
      el.sidebarBackdrop.classList.add('show');
      el.sidebarBackdrop.setAttribute('aria-hidden', 'false');
    }
    if (el.hamburgerBtn) {
      el.hamburgerBtn.setAttribute('aria-expanded', 'true');
    }
  }

  function closeDrawer() {
    const el = getElements();
    if (!state.drawerOpen || !el.appSidebar) return;

    state.drawerOpen = false;
    document.body.classList.remove('sidebar-open');

    el.appSidebar.classList.remove('mobile-open');
    if (el.sidebarBackdrop) {
      el.sidebarBackdrop.classList.remove('show');
      el.sidebarBackdrop.setAttribute('aria-hidden', 'true');
    }
    if (el.hamburgerBtn) {
      el.hamburgerBtn.setAttribute('aria-expanded', 'false');
    }
  }

  function toggleDrawer() {
    if (state.drawerOpen) {
      closeDrawer();
    } else {
      openDrawer();
    }
  }

  let touchStartX = 0;
  let touchStartY = 0;

  function initTouchSwipe(sidebar) {
    if (!sidebar) return;

    sidebar.addEventListener('touchstart', (e) => {
      touchStartX = e.changedTouches[0].screenX;
      touchStartY = e.changedTouches[0].screenY;
    }, { passive: true });

    sidebar.addEventListener('touchend', (e) => {
      const touchEndX = e.changedTouches[0].screenX;
      const touchEndY = e.changedTouches[0].screenY;
      const deltaX = touchEndX - touchStartX;
      const deltaY = Math.abs(touchEndY - touchStartY);

      if (deltaX < -50 && deltaY < 80) {
        closeDrawer();
      }
    }, { passive: true });
  }

  /* ==========================================================================
     4. User Profile Dropdown Controller
     ========================================================================== */
  function toggleUserDropdown(e) {
    if (e) e.stopPropagation();
    if (state.userDropdownOpen) {
      closeUserDropdown();
    } else {
      openUserDropdown();
    }
  }

  function openUserDropdown() {
    const el = getElements();
    if (!el.userMenuDropdown) return;

    state.userDropdownOpen = true;
    if (el.userDropdownContainer) {
      el.userDropdownContainer.classList.add('dropdown-open');
    }
    el.userMenuDropdown.classList.add('show');
    el.userMenuDropdown.setAttribute('aria-hidden', 'false');
    if (el.userMenuTrigger) {
      el.userMenuTrigger.setAttribute('aria-expanded', 'true');
    }
  }

  function closeUserDropdown() {
    const el = getElements();
    if (!state.userDropdownOpen || !el.userMenuDropdown) return;

    state.userDropdownOpen = false;
    if (el.userDropdownContainer) {
      el.userDropdownContainer.classList.remove('dropdown-open');
    }
    el.userMenuDropdown.classList.remove('show');
    el.userMenuDropdown.setAttribute('aria-hidden', 'true');
    if (el.userMenuTrigger) {
      el.userMenuTrigger.setAttribute('aria-expanded', 'false');
    }
  }

  /* ==========================================================================
     5. Notification Bell Popover Controller
     ========================================================================== */
  function toggleNotificationPopover(e) {
    if (e) e.stopPropagation();
    const el = getElements();
    if (!el.notificationDropdown) return;

    const isShowing = el.notificationDropdown.classList.contains('show');
    if (isShowing) {
      el.notificationDropdown.classList.remove('show');
      el.notificationBtn?.setAttribute('aria-expanded', 'false');
    } else {
      closeUserDropdown();
      el.notificationDropdown.classList.add('show');
      el.notificationBtn?.setAttribute('aria-expanded', 'true');
    }
  }

  /* ==========================================================================
     6. Global Event Bindings & Listeners
     ========================================================================== */
  function bindEventListeners() {
    const el = getElements();

    updateKeycapPlatformBadge(el);

    // Global keyboard shortcuts
    window.addEventListener('keydown', (e) => {
      const isCmdK = (state.isMac ? e.metaKey : e.ctrlKey) && (e.key === 'k' || e.key === 'K');
      const isSlash = e.key === '/' && !['INPUT', 'TEXTAREA'].includes(document.activeElement?.tagName);

      if (isCmdK || isSlash) {
        e.preventDefault();
        if (state.searchModalOpen) {
          closeSearchModal();
        } else {
          openSearchModal();
        }
        return;
      }

      if (e.key === 'Escape') {
        if (state.searchModalOpen) {
          e.preventDefault();
          closeSearchModal();
          return;
        }
        if (state.drawerOpen) {
          e.preventDefault();
          closeDrawer();
          return;
        }
        if (state.userDropdownOpen) {
          e.preventDefault();
          closeUserDropdown();
          el.userMenuTrigger?.focus();
          return;
        }
      }

      if (state.searchModalOpen) {
        if (e.key === 'ArrowDown' || e.key === 'ArrowUp' || e.key === 'Enter') {
          handleSearchKeyboardNav(e);
        }
      }
    });

    // Search trigger events
    if (el.globalSearchTrigger) {
      el.globalSearchTrigger.addEventListener('click', openSearchModal);
    }
    if (el.mobileSearchBtn) {
      el.mobileSearchBtn.addEventListener('click', openSearchModal);
    }
    if (el.searchCloseBtn) {
      el.searchCloseBtn.addEventListener('click', closeSearchModal);
    }
    if (el.searchModalRoot) {
      el.searchModalRoot.addEventListener('click', (e) => {
        if (e.target === el.searchModalRoot || e.target === el.searchBackdrop) {
          closeSearchModal();
        }
      });
    }

    // Search input typing
    if (el.searchInput) {
      el.searchInput.addEventListener('input', (e) => {
        state.selectedIndex = 0;
        renderSearchResults(e.target.value);
      });
    }

    // Category tabs
    el.searchTabChips.forEach(chip => {
      chip.addEventListener('click', () => {
        el.searchTabChips.forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        state.activeTab = chip.getAttribute('data-tab') || 'all';
        state.selectedIndex = 0;
        renderSearchResults(el.searchInput ? el.searchInput.value : '');
      });
    });

    // Mobile Hamburger & Drawer
    if (el.hamburgerBtn) {
      el.hamburgerBtn.addEventListener('click', toggleDrawer);
    }
    if (el.sidebarBackdrop) {
      el.sidebarBackdrop.addEventListener('click', closeDrawer);
    }
    if (el.sidebarCloseBtn) {
      el.sidebarCloseBtn.addEventListener('click', closeDrawer);
    }
    el.sidebarNavLinks.forEach(link => {
      link.addEventListener('click', () => {
        if (window.innerWidth < 768) {
          closeDrawer();
        }
      });
    });

    // User Profile Dropdown
    if (el.userMenuTrigger) {
      el.userMenuTrigger.addEventListener('click', toggleUserDropdown);
    }

    // Notification button
    if (el.notificationBtn) {
      el.notificationBtn.addEventListener('click', toggleNotificationPopover);
    }

    // Top Language Switcher Dropdown
    const langTrigger = document.getElementById('top-lang-trigger');
    const langMenu = document.getElementById('top-lang-menu');
    const langInput = document.getElementById('top-lang-code');
    const langForm = document.getElementById('top-lang-form');

    if (langTrigger && langMenu && langInput && langForm) {
      langTrigger.addEventListener('click', (e) => {
        e.stopPropagation();
        const isShown = langMenu.classList.contains('show');
        langMenu.classList.toggle('show', !isShown);
        langTrigger.setAttribute('aria-expanded', !isShown ? 'true' : 'false');
      });

      langMenu.addEventListener('click', (e) => {
        const item = e.target.closest('.top-lang-item');
        if (item) {
          const langCode = item.getAttribute('data-lang');
          if (langCode) {
            langInput.value = langCode;
            langForm.submit();
          }
        }
      });
    }

    // Click outside to dismiss menus
    document.addEventListener('click', (e) => {
      if (state.userDropdownOpen && el.userDropdownContainer && !el.userDropdownContainer.contains(e.target)) {
        closeUserDropdown();
      }
      if (el.notificationDropdown && !el.notificationBtn?.contains(e.target) && !el.notificationDropdown.contains(e.target)) {
        el.notificationDropdown.classList.remove('show');
        el.notificationBtn?.setAttribute('aria-expanded', 'false');
      }
      if (langMenu && !langTrigger?.contains(e.target) && !langMenu.contains(e.target)) {
        langMenu.classList.remove('show');
        langTrigger?.setAttribute('aria-expanded', 'false');
      }
    });

    // Window resize: auto-close drawer when returning to desktop
    let resizeTimer;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => {
        if (window.innerWidth >= 1024 && state.drawerOpen) {
          closeDrawer();
        }
      }, 100);
    });

    // Touch Gestures
    initTouchSwipe(el.appSidebar);
  }

  // Initialize
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bindEventListeners);
  } else {
    bindEventListeners();
  }

  // Export on window for external telemetry or testing
  window.DmojAppShell = {
    openSearch: openSearchModal,
    closeSearch: closeSearchModal,
    openDrawer: openDrawer,
    closeDrawer: closeDrawer,
    toggleDrawer: toggleDrawer,
    toggleUserMenu: toggleUserDropdown,
    getState: () => ({ ...state }),
  };

})(window, document);
