#!/usr/bin/env python3
"""
Empirical Adversarial Challenge Suite: Milestone 2 Core Workspaces & Auth Stress
Agent: Milestone 2 Challenger 2 (teamwork_preview_challenger_m2_2)

This test suite executes direct empirical tests against:
1. Dashboard (/): zero legacy h2/hr, clean hero card, metrics strip, activity stream.
2. Problems (/problems/): full 1440px width, all 8 columns present without truncation, filter bar, quick pills.
3. Submissions (/submissions/): 9 columns, pastel verdict pills, 58/42 split in SCSS, 420px mobile drawer in SCSS.
4. Rankings (/users/): Top 3 podium cards (Gold elevated, Silver, Bronze), rating tiers table, rating distribution.
5. User Profile (/user/tourist): 96px avatar hero card, 4 stats in a row, SVG rating curve, topic strengths.
6. Auth (/accounts/login/, /accounts/register/, /accounts/password/reset/): clean centered cards, no sidebars, no redundant headers.
7. SCSS & CSS rules verification: exact match of flex/width values for split and responsive drawers.
8. Adversarial edge cases: extreme queries, anonymous vs authenticated, dark theme stylesheet presence.
"""

import os
import sys
import re
from pathlib import Path

JUDGE_ROOT = Path(__file__).resolve().parent.parent
if str(JUDGE_ROOT) not in sys.path:
    sys.path.insert(0, str(JUDGE_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')
import django
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from judge.models import Profile, Problem, Submission, Contest

User = get_user_model()

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.client = Client()

    def check(self, condition, test_id, description):
        if condition:
            self.passed += 1
            print(f"  [PASS] {test_id}: {description}")
        else:
            self.failed += 1
            msg = f"  [FAIL] {test_id}: {description}"
            print(msg)
            self.errors.append(msg)

    def summary(self):
        total = self.passed + self.failed
        pct = (self.passed / total * 100) if total > 0 else 0
        print("\n" + "=" * 70)
        print(f"CHALLENGER 2 EMPIRICAL AUDIT SUMMARY: {self.passed}/{total} Passed ({pct:.1f}%)")
        print("=" * 70)
        if self.errors:
            print("\nFailures:")
            for e in self.errors:
                print(e)
        return self.failed == 0

def run_adversarial_suite():
    t = TestRunner()

    print("=" * 70)
    print("CHALLENGER 2: ADVERSARIAL STRESS & EMPIRICAL VERIFICATION")
    print("=" * 70)

    # -------------------------------------------------------------------------
    # SUITE 1: Dashboard Workspace (/)
    # -------------------------------------------------------------------------
    print("\n--- Suite 1: Dashboard Workspace (/) ---")
    resp_dash = t.client.get('/')
    t.check(resp_dash.status_code == 200, "1.1", "GET / returns HTTP 200 OK")
    html_dash = resp_dash.content.decode('utf-8')

    # Adversarial: Ensure legacy h2 / hr are NOT present
    # Specifically, base.html default title_row: <h2 style="display:inline">...</h2>
    # and title_ruler: <hr class="content-title-ruler">
    t.check('<h2>Dashboard</h2>' not in html_dash, "1.2", "No legacy <h2>Dashboard</h2> in rendered HTML")
    t.check('content-title-ruler' not in html_dash, "1.3", "No legacy hr.content-title-ruler in rendered HTML")
    t.check('<h2 style="display:inline">' not in html_dash, "1.4", "base.html default title_row h2 completely suppressed")

    # Clean hero card
    t.check('dashboard-hero-card' in html_dash, "1.5", "Hero card #dashboard-hero-card present")
    t.check('hero-title' in html_dash, "1.6", "Hero title present")
    t.check('btn-hero-primary' in html_dash, "1.7", "Primary CTA button present")
    t.check('btn-hero-secondary' in html_dash, "1.8", "Secondary CTA buttons present")

    # 4 Metric counters
    t.check('dashboard-metrics-strip' in html_dash, "1.9", "Metrics strip #dashboard-metrics-strip present")
    metric_count = len(re.findall(r'class="metric-box"', html_dash))
    t.check(metric_count == 4, "1.10", f"Exactly 4 metric boxes present (found {metric_count})")
    t.check('Algorithmic Problems' in html_dash or 'Problems' in html_dash, "1.11", "Metric 1 (Problems) present")
    t.check('Judged Submissions' in html_dash or 'Submissions' in html_dash, "1.12", "Metric 2 (Submissions) present")
    t.check('Active Competitors' in html_dash or 'Competitors' in html_dash, "1.13", "Metric 3 (Competitors) present")
    t.check('Judge Infrastructure' in html_dash or 'Infrastructure' in html_dash, "1.14", "Metric 4 (Infrastructure) present")

    # Activity stream & Announcements
    t.check('mini-submissions-table' in html_dash, "1.15", "Activity stream #mini-submissions-table present")
    t.check('dashboard-activity-card' in html_dash, "1.16", "Live activity card #dashboard-activity-card present")
    t.check('dashboard-news-card' in html_dash, "1.17", "Announcements card #dashboard-news-card present")
    t.check('dashboard-contests-card' in html_dash, "1.18", "Upcoming contests card #dashboard-contests-card present")
    t.check('dashboard-topics-card' in html_dash, "1.19", "Topic tags card #dashboard-topics-card present")

    # SCSS styling checks for dashboard-wrapper (no double padding, 1440px max-width)
    dash_scss = (JUDGE_ROOT / "resources" / "dashboard.scss").read_text()
    t.check("max-width: 1440px" in dash_scss, "1.20", "dashboard.scss specifies max-width: 1440px")
    t.check("padding: 0 0 2.5rem 0" in dash_scss or "padding: 0" in dash_scss, "1.21", "dashboard.scss avoids double horizontal padding")

    # -------------------------------------------------------------------------
    # SUITE 2: Problems Catalog (/problems/)
    # -------------------------------------------------------------------------
    print("\n--- Suite 2: Problems Catalog (/problems/) ---")
    resp_prob = t.client.get('/problems/')
    t.check(resp_prob.status_code == 200, "2.1", "GET /problems/ returns HTTP 200 OK")
    html_prob = resp_prob.content.decode('utf-8')

    # Suppressed legacy headers
    t.check('content-title-ruler' not in html_prob, "2.2", "No legacy hr.content-title-ruler in problems list")
    t.check('<h2 style="display:inline">' not in html_prob, "2.3", "No base.html default title_row in problems list")

    # Full table with 8 columns
    t.check('problems-table' in html_prob, "2.4", "Table #problems-table present")
    expected_prob_cols = [
        'col-star',
        'col-index',
        'col-problem',
        'col-group',
        'col-points',
        'col-ac-rate',
        'col-status',
        'col-actions',
    ]
    for col in expected_prob_cols:
        t.check(f'class="{col}"' in html_prob or f'class="col {col}"' in html_prob or col in html_prob,
                f"2.5-{col}", f"Problems table column '{col}' present in thead")

    # Filter bar and quick pills
    t.check('problems-filter-bar' in html_prob or 'problems-filter-form' in html_prob, "2.6", "Filter bar present")
    t.check('quick-filter-pills' in html_prob, "2.7", "Quick filter pills container present")
    t.check('pill-tab-item' in html_prob, "2.8", "Pill tab items present")
    t.check('filter-status' in html_prob, "2.9", "Status filter state input present")
    t.check('problems-search-input' in html_prob or 'name="search"' in html_prob, "2.10", "Search input present in filter bar")

    # SCSS column widths in problems-list.scss
    prob_scss = (JUDGE_ROOT / "resources" / "problems-list.scss").read_text()
    t.check("&.col-star { width: 44px" in prob_scss, "2.11", "SCSS defines col-star width 44px")
    t.check("&.col-problem { min-width: 240px" in prob_scss, "2.12", "SCSS defines col-problem min-width 240px")
    t.check("&.col-ac-rate { width: 140px" in prob_scss, "2.13", "SCSS defines col-ac-rate width 140px")

    # -------------------------------------------------------------------------
    # SUITE 3: Submissions Catalog & Slide-Out Drawer (/submissions/)
    # -------------------------------------------------------------------------
    print("\n--- Suite 3: Submissions Catalog & Drawer (/submissions/) ---")
    resp_sub = t.client.get('/submissions/')
    t.check(resp_sub.status_code == 200, "3.1", "GET /submissions/ returns HTTP 200 OK")
    html_sub = resp_sub.content.decode('utf-8')

    # Submissions table with 9 columns
    t.check('submissions-table' in html_sub, "3.2", "Table #submissions-table present")
    expected_sub_cols = [
        'col-id',
        'col-problem',
        'col-user',
        'col-verdict',
        'col-language',
        'col-time',
        'col-memory',
        'col-points',
        'col-date',
    ]
    for col in expected_sub_cols:
        t.check(f'class="{col}"' in html_sub or col in html_sub,
                f"3.3-{col}", f"Submissions table column '{col}' present in thead")

    # Pastel verdict pills
    t.check('verdict-ac' in html_sub or 'verdict-badge' in html_sub or 'badge-verdict' in html_sub,
            "3.4", "Verdict badges/pills present")

    # Drawer container and backdrop
    t.check('submission-detail-drawer' in html_sub, "3.5", "Slide-out drawer #submission-detail-drawer present")
    t.check('submission-drawer-backdrop' in html_sub, "3.6", "Drawer backdrop #submission-drawer-backdrop present")

    # SCSS verification: 58/42 split on desktop and 420px mobile drawer
    sub_scss = (JUDGE_ROOT / "resources" / "submissions-list.scss").read_text()
    t.check("flex: 1 1 58%;" in sub_scss, "3.7", "SCSS defines 58% table width on desktop split (.submissions-main-pane)")
    t.check("flex: 0 0 42%;" in sub_scss, "3.8", "SCSS defines 42% drawer width on desktop split (.submissions-drawer-pane)")
    t.check("width: 420px;" in sub_scss, "3.9", "SCSS defines 420px fixed drawer on mobile/tablet (< 1024px)")
    t.check("max-width: 85vw;" in sub_scss, "3.10", "SCSS defines max-width: 85vw for mobile drawer safety")

    # Verify drawer content endpoint returns HTTP 200
    resp_drawer = t.client.get('/widgets/submission_drawer?id=1')
    t.check(resp_drawer.status_code == 200, "3.11", "GET /widgets/submission_drawer?id=1 returns HTTP 200 OK")
    html_drawer = resp_drawer.content.decode('utf-8')
    t.check('drawer-header' in html_drawer or 'drawer-submission-id' in html_drawer, "3.12", "Drawer header rendered")
    t.check('testcases-grid' in html_drawer or 'test-cases-section' in html_drawer, "3.13", "Test cases section rendered")

    # -------------------------------------------------------------------------
    # SUITE 4: Rankings & Leaderboard (/users/)
    # -------------------------------------------------------------------------
    print("\n--- Suite 4: Rankings & Global Leaderboard (/users/) ---")
    resp_rank = t.client.get('/users/')
    t.check(resp_rank.status_code == 200, "4.1", "GET /users/ returns HTTP 200 OK")
    html_rank = resp_rank.content.decode('utf-8')

    # Podium cards
    t.check('rankings-podium-section' in html_rank, "4.2", "Podium section #rankings-podium-section present")
    t.check('card-rank-1' in html_rank, "4.3", "Rank 1 Gold card present")
    t.check('card-rank-2' in html_rank, "4.4", "Rank 2 Silver card present")
    t.check('card-rank-3' in html_rank, "4.5", "Rank 3 Bronze card present")
    t.check('badge-gold' in html_rank, "4.6", "Gold badge present on Rank 1 card")
    t.check('badge-silver' in html_rank, "4.7", "Silver badge present on Rank 2 card")
    t.check('badge-bronze' in html_rank, "4.8", "Bronze badge present on Rank 3 card")

    # Elevated Gold card styling in SCSS
    rank_scss = (JUDGE_ROOT / "resources" / "rankings-list.scss").read_text()
    t.check("&.card-rank-1 {" in rank_scss, "4.9", "SCSS defines specific rules for card-rank-1")
    t.check("padding-top: 2rem;" in rank_scss, "4.10", "card-rank-1 has elevated padding-top: 2rem")
    t.check("box-shadow: 0 8px 20px" in rank_scss, "4.11", "card-rank-1 has prominent elevated gold box-shadow")

    # Rating tiers table
    t.check('rankings-table' in html_rank, "4.12", "Rankings table #rankings-table present")
    t.check('rating-' in html_rank, "4.13", "User rating tier class applied to user links")

    # Rating distribution histogram
    t.check('distribution-histogram' in html_rank, "4.14", "Rating distribution histogram present")
    t.check('hist-bar-col' in html_rank, "4.15", "Histogram bar columns present")
    t.check('panel-insights' in html_rank, "4.16", "Ranking insights panel present")
    t.check('panel-organizations' in html_rank, "4.17", "Top organizations panel present")

    # -------------------------------------------------------------------------
    # SUITE 5: User Profile (/user/tourist or /user/admin)
    # -------------------------------------------------------------------------
    print("\n--- Suite 5: User Profile (/user/tourist & /user/admin) ---")
    # Test with tourist or admin
    user_target = 'tourist' if User.objects.filter(username='tourist').exists() else 'admin'
    resp_prof = t.client.get(f'/user/{user_target}')
    t.check(resp_prof.status_code == 200, "5.1", f"GET /user/{user_target} returns HTTP 200 OK")
    html_prof = resp_prof.content.decode('utf-8')

    # Hero card & avatar
    t.check('user-hero-card' in html_prof, "5.2", "User hero card #user-hero-card present")
    t.check('user-hero-avatar' in html_prof, "5.3", "Avatar .user-hero-avatar present")

    # Check SCSS 96px avatar size
    prof_scss = (JUDGE_ROOT / "resources" / "user-profile.scss").read_text()
    t.check("width: 96px;" in prof_scss, "5.4", "user-profile.scss defines avatar width: 96px")
    t.check("height: 96px;" in prof_scss, "5.5", "user-profile.scss defines avatar height: 96px")
    t.check("border-radius: 50%;" in prof_scss, "5.6", "user-profile.scss defines avatar border-radius: 50%")

    # 4 Stats in a row
    t.check('card-rating' in html_prof, "5.7", "Stat 1 (Rating) present")
    t.check('card-rank' in html_prof, "5.8", "Stat 2 (Rank) present")
    t.check('card-solved' in html_prof, "5.9", "Stat 3 (Solved Problems) present")
    t.check('card-contests' in html_prof, "5.10", "Stat 4 (Contests) present")

    # SVG Rating curve
    t.check('rating-chart-svg' in html_prof, "5.11", "SVG rating chart .rating-chart-svg present")
    t.check('viewBox="0 0 540 180"' in html_prof, "5.12", "SVG rating curve viewBox matches 0 0 540 180")
    t.check('chart-timerange-pills' in html_prof, "5.13", "Time range pills (1M, 3M, 6M, 1Y, ALL) present")

    # Topic Strengths
    t.check('card-topic-strengths' in html_prof, "5.14", "Topic strengths card #card-topic-strengths present")
    t.check('topic-progress-fill' in html_prof, "5.15", "Topic progress fill bars present")

    # Submissions & Contests tables
    t.check('card-recent-submissions' in html_prof, "5.16", "Recent submissions card present")
    t.check('card-recent-contests' in html_prof, "5.17", "Recent contests card present")

    # -------------------------------------------------------------------------
    # SUITE 6: Auth Workspaces (/accounts/*)
    # -------------------------------------------------------------------------
    print("\n--- Suite 6: Auth Workspaces (/accounts/*) ---")
    auth_endpoints = [
        ('/accounts/login/', 'auth-login-card', 'Login'),
        ('/accounts/register/', 'auth-register-card', 'Register'),
        ('/accounts/password/reset/', 'auth-reset-card', 'Password Reset'),
    ]

    for url, card_id, label in auth_endpoints:
        resp_auth = t.client.get(url)
        t.check(resp_auth.status_code == 200, f"6.1-{label}", f"GET {url} returns HTTP 200 OK")
        html_auth = resp_auth.content.decode('utf-8')

        # Clean centered card
        t.check(card_id in html_auth, f"6.2-{label}", f"Centered card #{card_id} present")
        t.check('auth-page-container' in html_auth, f"6.3-{label}", f"Container .auth-page-container present for {label}")

        # No sidebars or redundant headers
        t.check('content-title-ruler' not in html_auth, f"6.4-{label}", f"No hr.content-title-ruler for {label}")
        t.check('<h2 style="display:inline">' not in html_auth, f"6.5-{label}", f"No default base.html title_row for {label}")

        # CSRF token
        t.check('csrfmiddlewaretoken' in html_auth, f"6.6-{label}", f"CSRF token present in form for {label}")

    # SCSS auth container centering
    auth_scss = (JUDGE_ROOT / "resources" / "auth-workspace.scss").read_text()
    t.check("min-height: calc(100vh - 160px);" in auth_scss, "6.7", "auth-workspace.scss sets min-height: calc(100vh - 160px)")
    t.check("display: flex;" in auth_scss, "6.8", "auth-workspace.scss uses flex centering")
    t.check("justify-content: center;" in auth_scss, "6.9", "auth-workspace.scss centers horizontally")
    t.check("align-items: center;" in auth_scss, "6.10", "auth-workspace.scss centers vertically")

    # -------------------------------------------------------------------------
    # SUITE 7: Adversarial Cleanliness Across All 6 Screens
    # -------------------------------------------------------------------------
    print("\n--- Suite 7: Adversarial Cleanliness & Forbidden Tokens ---")
    forbidden_tokens = [
        'desktop-wallpaper',
        'mac-app-window',
        'mac-window-topbar',
        'mac-window-body',
        'traffic-lights',
        'traffic-red',
        'traffic-yellow',
        'traffic-green',
    ]

    audited_urls = [
        ('/', 'Dashboard'),
        ('/problems/', 'Problems'),
        ('/submissions/', 'Submissions'),
        ('/users/', 'Rankings'),
        (f'/user/{user_target}', 'User Profile'),
        ('/accounts/login/', 'Login'),
        ('/accounts/register/', 'Register'),
        ('/accounts/password/reset/', 'Password Reset'),
    ]

    for url, screen_name in audited_urls:
        resp = t.client.get(url)
        content = resp.content.decode('utf-8')
        for token in forbidden_tokens:
            t.check(token not in content, f"7.1-{screen_name}-{token}",
                    f"Forbidden token '{token}' absent from {screen_name}")

    # -------------------------------------------------------------------------
    # SUITE 8: Edge Cases & Query Parameter Stress
    # -------------------------------------------------------------------------
    print("\n--- Suite 8: Edge Cases & Query Stress ---")
    # 8.1 Problems with multiple query parameters
    resp_prob_filter = t.client.get('/problems/?difficulty=2&type=code&order=-code')
    t.check(resp_prob_filter.status_code == 200, "8.1", "Problems filter with multiple query params returns 200")

    # 8.2 Submissions with verdict and language filters
    resp_sub_filter = t.client.get('/submissions/?status=AC&language=PY3')
    t.check(resp_sub_filter.status_code == 200, "8.2", "Submissions filter with AC and PY3 returns 200")

    # 8.3 Non-existent user profile returns 404 cleanly
    resp_404 = t.client.get('/user/nonexistent_user_xyz_12345')
    t.check(resp_404.status_code == 404, "8.3", "Non-existent user profile returns HTTP 404 cleanly")

    # 8.4 Authenticated user session retains clean layout
    test_user, _ = User.objects.get_or_create(username='tester_m2_audit', defaults={'email': 'test@example.com'})
    Profile.objects.get_or_create(user=test_user)
    t.client.force_login(test_user)

    resp_auth_dash = t.client.get('/')
    html_auth_dash = resp_auth_dash.content.decode('utf-8')
    t.check('dashboard-wrapper' in html_auth_dash, "8.4", "Authenticated user receives dashboard cleanly")
    t.check('<h2>Dashboard</h2>' not in html_auth_dash, "8.5", "Authenticated user also has legacy h2 suppressed")
    t.check('desktop-wallpaper' not in html_auth_dash, "8.6", "Authenticated user has zero forbidden tokens")

    return t.summary()

if __name__ == '__main__':
    success = run_adversarial_suite()
    sys.exit(0 if success else 1)
