// VCoder Online Judge — Modern Dashboard Controller
// Milestone 7: Dashboard Workspace (R4)

(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        initHeroGreeting();
        initContestCountdowns();
    });

    function initHeroGreeting() {
        const hour = new Date().getHours();
        const badge = document.querySelector('.hero-badge-pill span');
        if (badge) {
            let greeting = 'Welcome to VCoder Judge';
            if (hour < 12) greeting = 'Good Morning — Ready to Code?';
            else if (hour < 18) greeting = 'Good Afternoon — Level Up Today';
            else greeting = 'Good Evening — Compete & Conquer';
            badge.textContent = greeting;
        }
    }

    function initContestCountdowns() {
        // Any countdown tags on the dashboard
        const countdownNodes = document.querySelectorAll('.sidebar-contest-countdown');
        countdownNodes.forEach(node => {
            const targetTimeStr = node.getAttribute('data-target-time');
            if (!targetTimeStr) return;

            const targetTime = new Date(targetTimeStr).getTime();
            function update() {
                const now = Date.now();
                const diff = targetTime - now;
                if (diff <= 0) {
                    node.textContent = 'Started';
                    return;
                }
                const hours = Math.floor(diff / (1000 * 60 * 60));
                const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                node.textContent = `${hours}h ${mins}m`;
            }
            update();
            setInterval(update, 60000);
        });
    }
})();
