/**
 * VCODER Design System — Rankings & Global Leaderboard Controller (Mockup docs/6.png)
 * Handles filter pills, podium interactions, and table row highlighting.
 */

(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        initFilterPills();
        initTableRowClicks();
    });

    /**
     * 1. Filter Dropdown Pills Active State
     */
    function initFilterPills() {
        const filterPills = document.querySelectorAll('.rankings-filters-bar .filter-dropdown-pill');
        filterPills.forEach(pill => {
            pill.addEventListener('click', function () {
                filterPills.forEach(p => p.classList.remove('active'));
                this.classList.add('active');
            });
        });
    }

    /**
     * 2. Table Row Click Delegation
     */
    function initTableRowClicks() {
        const rows = document.querySelectorAll('.rankings-table tbody tr.ranking-row');
        rows.forEach(row => {
            row.addEventListener('click', function (e) {
                // If user didn't click directly on a link, navigate to user profile
                if (!e.target.closest('a')) {
                    const userLink = row.querySelector('.user-name-link');
                    if (userLink && userLink.href) {
                        window.location.href = userLink.href;
                    }
                }
            });
        });
    }

})();
