/**
 * VCODER Design System — Contests Overview Controller (Mockup docs/4.png)
 * Handles countdown timer, tab switching, and mini calendar rendering.
 */

(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        initCountdownTimer();
        initFilterTabs();
        initMiniCalendar();
        initLiveSearch();
    });

    /**
     * 1. Featured Contest Countdown Timer
     */
    function initCountdownTimer() {
        const timerContainer = document.getElementById('featured-countdown-timer');
        if (!timerContainer) return;

        const targetTimeStr = timerContainer.getAttribute('data-target-time');
        if (!targetTimeStr) return;

        const targetDate = new Date(targetTimeStr).getTime();
        const daysEl = document.getElementById('timer-days');
        const hoursEl = document.getElementById('timer-hours');
        const minsEl = document.getElementById('timer-minutes');
        const secsEl = document.getElementById('timer-seconds');

        function updateTimer() {
            const now = new Date().getTime();
            const diff = targetDate - now;

            if (diff <= 0) {
                if (daysEl) daysEl.textContent = '00';
                if (hoursEl) hoursEl.textContent = '00';
                if (minsEl) minsEl.textContent = '00';
                if (secsEl) secsEl.textContent = '00';
                return;
            }

            const days = Math.floor(diff / (1000 * 60 * 60 * 24));
            const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            const secs = Math.floor((diff % (1000 * 60)) / 1000);

            if (daysEl) daysEl.textContent = String(days).padStart(2, '0');
            if (hoursEl) hoursEl.textContent = String(hours).padStart(2, '0');
            if (minsEl) minsEl.textContent = String(mins).padStart(2, '0');
            if (secsEl) secsEl.textContent = String(secs).padStart(2, '0');
        }

        updateTimer();
        setInterval(updateTimer, 1000);
    }

    /**
     * 2. Filter Tab Navigation (All, Ongoing, Upcoming, Past)
     */
    function initFilterTabs() {
        const pillGroup = document.getElementById('contest-status-pills');
        if (!pillGroup) return;

        const buttons = pillGroup.querySelectorAll('.filter-pill-btn');
        const sectionOngoing = document.getElementById('section-ongoing');
        const sectionUpcoming = document.getElementById('section-upcoming');
        const sectionPast = document.getElementById('section-past');

        buttons.forEach(btn => {
            btn.addEventListener('click', function () {
                buttons.forEach(b => b.classList.remove('active'));
                this.classList.add('active');

                const tab = this.getAttribute('data-tab');

                if (tab === 'all') {
                    if (sectionOngoing) sectionOngoing.style.display = '';
                    if (sectionUpcoming) sectionUpcoming.style.display = '';
                    if (sectionPast) sectionPast.style.display = '';
                } else if (tab === 'ongoing') {
                    if (sectionOngoing) sectionOngoing.style.display = '';
                    if (sectionUpcoming) sectionUpcoming.style.display = 'none';
                    if (sectionPast) sectionPast.style.display = 'none';
                } else if (tab === 'upcoming') {
                    if (sectionOngoing) sectionOngoing.style.display = 'none';
                    if (sectionUpcoming) sectionUpcoming.style.display = '';
                    if (sectionPast) sectionPast.style.display = 'none';
                } else if (tab === 'past') {
                    if (sectionOngoing) sectionOngoing.style.display = 'none';
                    if (sectionUpcoming) sectionUpcoming.style.display = 'none';
                    if (sectionPast) sectionPast.style.display = '';
                }
            });
        });
    }

    /**
     * 3. Mini Contest Calendar Widget
     */
    function initMiniCalendar() {
        const calCellsContainer = document.getElementById('calendar-days-cells');
        if (!calCellsContainer) return;

        const now = new Date();
        const year = now.getFullYear();
        const month = now.getMonth();
        const todayDate = now.getDate();

        // First day of current month
        const firstDayIndex = new Date(year, month, 1).getDay();
        // Number of days in current month
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        // Days in previous month
        const prevDaysInMonth = new Date(year, month, 0).getDate();

        calCellsContainer.innerHTML = '';

        // Previous month trailing days
        for (let i = firstDayIndex - 1; i >= 0; i--) {
            const cell = document.createElement('div');
            cell.className = 'cal-day-cell other-month';
            cell.textContent = prevDaysInMonth - i;
            calCellsContainer.appendChild(cell);
        }

        // Current month days
        for (let day = 1; day <= daysInMonth; day++) {
            const cell = document.createElement('div');
            cell.className = 'cal-day-cell';
            cell.textContent = day;

            if (day === todayDate) {
                cell.classList.add('is-today');
            }

            // Mark contest days (e.g. today or near days)
            if (day === todayDate || day === todayDate + 2 || day === 15) {
                cell.classList.add('has-contest');
            }

            calCellsContainer.appendChild(cell);
        }

        // Next month leading days to complete grid
        const totalCells = calCellsContainer.children.length;
        const remainder = totalCells % 7;
        if (remainder !== 0) {
            const daysToAdd = 7 - remainder;
            for (let nextDay = 1; nextDay <= daysToAdd; nextDay++) {
                const cell = document.createElement('div');
                cell.className = 'cal-day-cell other-month';
                cell.textContent = nextDay;
                calCellsContainer.appendChild(cell);
            }
        }
    }

    /**
     * 4. Client-side Live Search Highlight
     */
    function initLiveSearch() {
        const searchInput = document.getElementById('contests-search-input');
        if (!searchInput) return;

        searchInput.addEventListener('input', function () {
            const query = this.value.trim().toLowerCase();
            const rows = document.querySelectorAll('.contests-table tbody tr.contest-row');

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (!query || text.includes(query)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

})();
