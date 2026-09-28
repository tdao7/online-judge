/**
 * VCODER Design System — User Profile Controller (Mockup docs/7.png)
 * Handles Follow toggle and rating chart timeframe pills.
 */

(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        initFollowButton();
        initTimeRangePills();
    });

    /**
     * 1. Follow User Button Toggle
     */
    function initFollowButton() {
        const followBtn = document.getElementById('btn-follow-user');
        if (!followBtn) return;

        const pathParts = window.location.pathname.split('/');
        const username = pathParts[pathParts.length - 1] || 'user';
        const storageKey = 'following_user_' + username;

        if (localStorage.getItem(storageKey) === 'true') {
            setFollowingState(followBtn);
        }

        followBtn.addEventListener('click', function () {
            const isFollowing = localStorage.getItem(storageKey) === 'true';
            if (isFollowing) {
                localStorage.setItem(storageKey, 'false');
                setUnfollowingState(followBtn);
            } else {
                localStorage.setItem(storageKey, 'true');
                setFollowingState(followBtn);
            }
        });

        function setFollowingState(btn) {
            btn.innerHTML = '<i class="fa fa-check"></i> <span>Following</span>';
            btn.style.backgroundColor = '#E5E7EB';
            btn.style.color = '#374151';
            btn.style.boxShadow = 'none';
        }

        function setUnfollowingState(btn) {
            btn.innerHTML = '<i class="fa fa-plus"></i> <span>Follow</span>';
            btn.style.backgroundColor = '';
            btn.style.color = '';
            btn.style.boxShadow = '';
        }
    }

    /**
     * 2. Rating Chart Timeframe Range Switcher
     */
    function initTimeRangePills() {
        const pills = document.querySelectorAll('#chart-timerange-pills .btn-range-pill');
        pills.forEach(pill => {
            pill.addEventListener('click', function () {
                pills.forEach(p => p.classList.remove('active'));
                this.classList.add('active');
            });
        });
    }

})();
