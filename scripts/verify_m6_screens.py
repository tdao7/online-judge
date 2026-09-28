#!/usr/bin/env python3
"""
scripts/verify_m6_screens.py
Milestone 6 End-to-End Automated Verification & Regression Suite:
Screen 6: Rankings & Global Leaderboard (docs/6.png)
Screen 7: User Profile (docs/7.png)

Usage:
  ./venv/bin/python scripts/verify_m6_screens.py
  ./venv/bin/python scripts/verify_m6_screens.py --remote http://100.107.199.45:8090
"""

import os
import sys
import argparse
from pathlib import Path

# Setup Django environment
JUDGE_ROOT = Path(__file__).resolve().parent.parent
if not (JUDGE_ROOT / "dmoj").exists():
    JUDGE_ROOT = Path("/Users/ryanx/workspace/vcoderlog-workspace/vcoderlog-judge")

if str(JUDGE_ROOT) not in sys.path:
    sys.path.insert(0, str(JUDGE_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')
import django
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from judge.models import Profile, Organization

User = get_user_model()


class TestRunner:
    def __init__(self, remote_url=None):
        self.remote_url = remote_url.rstrip('/') if remote_url else None
        self.passed = 0
        self.failed = 0
        self.client = Client()

    def check(self, condition, test_name, detail=""):
        if condition:
            print(f"  \033[92m✔ PASS\033[0m: {test_name}")
            self.passed += 1
            return True
        else:
            print(f"  \033[91m✖ FAIL\033[0m: {test_name} - {detail}")
            self.failed += 1
            return False

    def print_summary(self):
        total = self.passed + self.failed
        pct = (self.passed / total * 100) if total > 0 else 0
        print("\n" + "=" * 60)
        print(f"VERIFICATION SUMMARY: {self.passed}/{total} Passed ({pct:.1f}%)")
        print("=" * 60)
        if self.failed == 0:
            print("\033[92mALL TESTS PASSED SUCCESSFULLY!\033[0m\n")
        else:
            print(f"\033[91m{self.failed} TESTS FAILED!\033[0m\n")


def run_tests(remote_url=None):
    runner = TestRunner(remote_url=remote_url)

    print("\n" + "=" * 60)
    print("STAGE 1: Static Files, SCSS Compilation & Asset Pipeline")
    print("=" * 60)

    # 1.1 Source Files Exist
    runner.check((JUDGE_ROOT / "resources" / "rankings-list.scss").exists(), "1.1 resources/rankings-list.scss exists")
    runner.check((JUDGE_ROOT / "resources" / "user-profile.scss").exists(), "1.2 resources/user-profile.scss exists")
    runner.check((JUDGE_ROOT / "resources" / "rankings-list.js").exists(), "1.3 resources/rankings-list.js exists")
    runner.check((JUDGE_ROOT / "resources" / "user-profile.js").exists(), "1.4 resources/user-profile.js exists")
    runner.check((JUDGE_ROOT / "templates" / "user" / "list.html").exists(), "1.5 templates/user/list.html exists")
    runner.check((JUDGE_ROOT / "templates" / "user" / "user-base.html").exists(), "1.6 templates/user/user-base.html exists")
    runner.check((JUDGE_ROOT / "templates" / "user" / "user-about.html").exists(), "1.7 templates/user/user-about.html exists")

    # 1.2 Compiled CSS Files Exist
    runner.check((JUDGE_ROOT / "resources" / "rankings-list.css").exists(), "1.8 resources/rankings-list.css compiled")
    runner.check((JUDGE_ROOT / "resources" / "user-profile.css").exists(), "1.9 resources/user-profile.css compiled")
    runner.check((JUDGE_ROOT / "resources" / "dark" / "rankings-list.css").exists(), "1.10 dark/rankings-list.css compiled")
    runner.check((JUDGE_ROOT / "resources" / "dark" / "user-profile.css").exists(), "1.11 dark/user-profile.css compiled")

    # 1.3 Static Directory Collected
    runner.check((JUDGE_ROOT / "static" / "rankings-list.css").exists(), "1.12 static/rankings-list.css collected")
    runner.check((JUDGE_ROOT / "static" / "user-profile.css").exists(), "1.13 static/user-profile.css collected")
    runner.check((JUDGE_ROOT / "static" / "rankings-list.js").exists(), "1.14 static/rankings-list.js collected")
    runner.check((JUDGE_ROOT / "static" / "user-profile.js").exists(), "1.15 static/user-profile.js collected")

    print("\n" + "=" * 60)
    print("STAGE 2: Screen 6 — Rankings & Global Leaderboard (docs/6.png)")
    print("=" * 60)

    # 2.1 Route availability
    resp = runner.client.get('/users/')
    runner.check(resp.status_code == 200, "2.1 GET /users/ HTTP 200 OK")

    html = resp.content.decode('utf-8')

    # 2.2 Header and filters
    runner.check("rankings-catalog-wrapper" in html, "2.2 Main rankings catalog wrapper present")
    runner.check("Rankings" in html and "rankings-main-title" in html, "2.3 Header title 'Rankings' present")
    runner.check("rankings-filters-bar" in html, "2.4 Filter pills bar present")
    runner.check("filter-scope" in html and "Global" in html, "2.5 Scope filter 'Global' present")
    runner.check("filter-timeframe" in html and "Monthly" in html, "2.6 Timeframe filter 'Monthly' present")
    runner.check("filter-contest-type" in html and "All Contests" in html, "2.7 Contest filter 'All Contests' present")
    runner.check("filter-country" in html and "All Countries" in html, "2.8 Country filter 'All Countries' present")

    # 2.3 Top 3 Podium Cards
    runner.check("rankings-podium-section" in html, "2.9 Top 3 podium section present")
    runner.check("card-rank-1" in html and "badge-gold" in html, "2.10 Rank 1 Gold card present")
    runner.check("card-rank-2" in html and "badge-silver" in html, "2.11 Rank 2 Silver card present")
    runner.check("card-rank-3" in html and "badge-bronze" in html, "2.12 Rank 3 Bronze card present")
    runner.check("podium-avatar" in html, "2.13 Podium avatars present")
    runner.check("podium-metrics-row" in html, "2.14 Podium rating/solved metrics present")

    # 2.4 Leaderboard Table
    runner.check("rankings-table-card" in html and "rankings-table" in html, "2.15 Leaderboard table card present")
    runner.check("ranking-row" in html, "2.16 Ranking table rows present")
    runner.check("trend-sparkline" in html, "2.17 Trend sparkline SVG present")
    runner.check("user-badges-list" in html or "badge-pill" in html, "2.18 Competitor badge pills present")

    # 2.5 Desktop Sidebar Panels
    runner.check("panel-insights" in html and "Ranking Insights" in html, "2.19 Ranking Insights panel present")
    runner.check("Total Rated Users" in html, "2.20 Total Rated Users insight present")
    runner.check("panel-distribution" in html and "Rating Distribution" in html, "2.21 Rating Distribution histogram present")
    runner.check("bars-container" in html and "hist-bar-fill" in html, "2.22 Histogram bars present")
    runner.check("panel-organizations" in html and "Top Organizations" in html, "2.23 Top Organizations panel present")

    print("\n" + "=" * 60)
    print("STAGE 3: Screen 7 — User Profile (docs/7.png)")
    print("=" * 60)

    # 3.1 Route availability
    target_user = User.objects.filter(username__in=['tourist', 'admin', 'ecnerwala']).first() or User.objects.first()
    runner.check(target_user is not None, "3.1 Target profile user exists in database")

    if target_user:
        resp_p = runner.client.get(f'/user/{target_user.username}')
        runner.check(resp_p.status_code == 200, f"3.2 GET /user/{target_user.username} HTTP 200 OK")

        p_html = resp_p.content.decode('utf-8')

        # 3.2 Top Bar Breadcrumbs & Follow Action
        runner.check("profile-top-bar" in p_html, "3.3 Profile top bar present")
        runner.check("profile-breadcrumb" in p_html and target_user.username in p_html, "3.4 Breadcrumb navigation present")
        runner.check("btn-follow-user" in p_html and "Follow" in p_html, "3.5 Follow action button present")

        # 3.3 User Hero Card
        runner.check("user-hero-card" in p_html, "3.6 User hero header card present")
        runner.check("user-hero-avatar" in p_html, "3.7 Large circular avatar present")
        runner.check("verified-badge-icon" in p_html, "3.8 Verified contestant badge icon present")
        runner.check("user-bio-text" in p_html, "3.9 User bio text present")
        runner.check("user-links-row" in p_html, "3.10 Location and website link items present")

        # 3.4 4 Stat Cards
        runner.check("card-rating" in p_html and "Rating" in p_html, "3.11 Stat Card 1: Rating present")
        runner.check("card-rank" in p_html and "Rank" in p_html, "3.12 Stat Card 2: Rank present")
        runner.check("card-solved" in p_html and "Solved Problems" in p_html, "3.13 Stat Card 3: Solved Problems present")
        runner.check("card-contests" in p_html and "Contests" in p_html, "3.14 Stat Card 4: Contests present")

        # 3.5 Profile Navigation Tabs
        runner.check("profile-nav-tabs" in p_html, "3.15 Profile navigation tabs present")
        runner.check("Overview" in p_html, "3.16 Overview tab present")
        runner.check("Problems" in p_html, "3.17 Problems tab present")

        # 3.6 2x2 Content Grid
        runner.check("profile-overview-grid" in p_html, "3.18 2x2 profile overview grid container present")

        # Card 1: Rating History
        runner.check("card-rating-history" in p_html and "Rating History" in p_html, "3.19 Card 1: Rating History present")
        runner.check("chart-timerange-pills" in p_html and "3M" in p_html, "3.20 Time range pills (1M, 3M, 6M, 1Y, All) present")
        runner.check("rating-chart-svg" in p_html, "3.21 Rating chart SVG area graph present")
        runner.check("chart-x-axis" in p_html, "3.22 Chart X axis months labels present")

        # Card 2: Topic Strengths
        runner.check("card-topic-strengths" in p_html and "Topic Strengths" in p_html, "3.23 Card 2: Topic Strengths present")
        runner.check("topics-bars-stack" in p_html and "topic-progress-fill" in p_html, "3.24 Topic strength progress bars present")
        runner.check("Dynamic Programming" in p_html, "3.25 Topic row 'Dynamic Programming' present")

        # Card 3: Recent Submissions
        runner.check("card-recent-submissions" in p_html and "Recent Submissions" in p_html, "3.26 Card 3: Recent Submissions table present")
        runner.check("verdict-tag" in p_html or "tag-ac" in p_html, "3.27 Submission verdict tags present")

        # Card 4: Recent Contests
        runner.check("card-recent-contests" in p_html and "Recent Contests" in p_html, "3.28 Card 4: Recent Contests table present")
        runner.check("col-contest-delta" in p_html or "delta-badge" in p_html, "3.29 Contest rating change delta badges present")

    print("\n" + "=" * 60)
    print("STAGE 4: Client-side Interactive Logic (rankings-list.js & user-profile.js)")
    print("=" * 60)

    # 4.1 rankings-list.js Logic Analysis
    rk_js = (JUDGE_ROOT / "resources" / "rankings-list.js").read_text()
    runner.check("initFilterPills" in rk_js, "4.1 Filter pills interactive logic defined")
    runner.check("initTableRowClicks" in rk_js, "4.2 Table row click delegation logic defined")

    # 4.2 user-profile.js Logic Analysis
    prof_js = (JUDGE_ROOT / "resources" / "user-profile.js").read_text()
    runner.check("initFollowButton" in prof_js, "4.3 Follow user button toggle logic defined")
    runner.check("initTimeRangePills" in prof_js, "4.4 Rating chart timeframe switcher defined")

    # Remote checks if requested
    if runner.remote_url:
        print("\n" + "=" * 60)
        print(f"STAGE 5: Remote Production Server Verification ({runner.remote_url})")
        print("=" * 60)
        import urllib.request
        try:
            req_rankings = urllib.request.urlopen(f"{runner.remote_url}/users/", timeout=10)
            remote_rk_html = req_rankings.read().decode('utf-8')
            runner.check(req_rankings.status == 200, "5.1 Remote /users/ HTTP 200 OK")
            runner.check("rankings-catalog-wrapper" in remote_rk_html, "5.2 Remote /users/ has rankings-catalog-wrapper")
            runner.check("rankings-podium-section" in remote_rk_html, "5.3 Remote /users/ has rankings-podium-section")
            runner.check("card-rank-1" in remote_rk_html, "5.4 Remote /users/ has podium Rank 1 card")

            req_prof = urllib.request.urlopen(f"{runner.remote_url}/user/tourist", timeout=10)
            remote_prof_html = req_prof.read().decode('utf-8')
            runner.check(req_prof.status == 200, "5.5 Remote /user/tourist HTTP 200 OK")
            runner.check("user-hero-card" in remote_prof_html, "5.6 Remote /user/tourist has user-hero-card")
            runner.check("profile-overview-grid" in remote_prof_html, "5.7 Remote /user/tourist has 2x2 overview grid")
            runner.check("card-rating-history" in remote_prof_html, "5.8 Remote /user/tourist has rating history card")
        except Exception as e:
            runner.check(False, "5.x Remote HTTP request error", str(e))

    runner.print_summary()
    return runner.failed == 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Verify Milestone 6 Screens 6 & 7")
    parser.add_argument('--remote', help="Remote base URL, e.g. http://100.107.199.45:8090", default=None)
    args = parser.parse_args()

    success = run_tests(remote_url=args.remote)
    sys.exit(0 if success else 1)
