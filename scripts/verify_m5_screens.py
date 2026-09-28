#!/usr/bin/env python3
"""
scripts/verify_m5_screens.py
Milestone 5 End-to-End Automated Verification & Regression Suite:
Screen 4: Contests Overview & Featured Hero (docs/4.png)
Screen 5: Live Contest Workspace & Problem Switcher (docs/5.png)

Usage:
  ./venv/bin/python scripts/verify_m5_screens.py
  ./venv/bin/python scripts/verify_m5_screens.py --remote http://100.107.199.45:8090
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
from django.contrib.auth.models import AnonymousUser, User
from judge.models import Contest, Problem, ContestProblem, Profile, Language


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
    runner.check((JUDGE_ROOT / "resources" / "contests-list.scss").exists(), "1.1 resources/contests-list.scss exists")
    runner.check((JUDGE_ROOT / "resources" / "contest-workspace.scss").exists(), "1.2 resources/contest-workspace.scss exists")
    runner.check((JUDGE_ROOT / "resources" / "contests-list.js").exists(), "1.3 resources/contests-list.js exists")
    runner.check((JUDGE_ROOT / "resources" / "contest-workspace.js").exists(), "1.4 resources/contest-workspace.js exists")
    runner.check((JUDGE_ROOT / "templates" / "contest" / "list.html").exists(), "1.5 templates/contest/list.html exists")
    runner.check((JUDGE_ROOT / "templates" / "contest" / "contest.html").exists(), "1.6 templates/contest/contest.html exists")

    # 1.2 Compiled CSS Files Exist
    runner.check((JUDGE_ROOT / "resources" / "contests-list.css").exists(), "1.7 resources/contests-list.css compiled")
    runner.check((JUDGE_ROOT / "resources" / "contest-workspace.css").exists(), "1.8 resources/contest-workspace.css compiled")
    runner.check((JUDGE_ROOT / "resources" / "dark" / "contests-list.css").exists(), "1.9 dark/contests-list.css compiled")
    runner.check((JUDGE_ROOT / "resources" / "dark" / "contest-workspace.css").exists(), "1.10 dark/contest-workspace.css compiled")

    # 1.3 Static Directory Collected
    runner.check((JUDGE_ROOT / "static" / "contests-list.css").exists(), "1.11 static/contests-list.css collected")
    runner.check((JUDGE_ROOT / "static" / "contest-workspace.css").exists(), "1.12 static/contest-workspace.css collected")
    runner.check((JUDGE_ROOT / "static" / "contests-list.js").exists(), "1.13 static/contests-list.js collected")
    runner.check((JUDGE_ROOT / "static" / "contest-workspace.js").exists(), "1.14 static/contest-workspace.js collected")

    print("\n" + "=" * 60)
    print("STAGE 2: Screen 4 — Contests Overview & Featured Hero (docs/4.png)")
    print("=" * 60)

    # 2.1 ContestList View Execution
    resp = runner.client.get('/contests/')
    runner.check(resp.status_code == 200, "2.1 ContestList HTTP 200 OK")

    html = resp.content.decode('utf-8')

    # 2.2 Header Elements
    runner.check("contests-catalog-wrapper" in html, "2.2 Main catalog wrapper present")
    runner.check("Contests" in html and "contests-main-title" in html, "2.3 Contests header title present")
    runner.check("contests-count-pill" in html, "2.4 Contests count pill badge present")
    runner.check("contests-search-input" in html, "2.5 Search input present")

    # 2.3 Filter Tab Pills
    runner.check("contest-status-pills" in html, "2.6 Status filter tab group present")
    runner.check('data-tab="all"' in html, "2.7 'All Contests' filter pill present")
    runner.check('data-tab="ongoing"' in html, "2.8 'Ongoing' filter pill present")
    runner.check('data-tab="upcoming"' in html, "2.9 'Upcoming' filter pill present")
    runner.check('data-tab="past"' in html, "2.10 'Past' filter pill present")

    # 2.4 Featured Contest Hero Card
    runner.check("featured-contest-hero" in html, "2.11 Featured contest hero card present")
    runner.check("FEATURED CONTEST" in html, "2.12 Featured contest star badge present")
    runner.check("featured-countdown-timer" in html, "2.13 Featured countdown timer container present")
    runner.check("timer-days" in html and "timer-hours" in html, "2.14 Timer days/hours digit blocks present")
    runner.check("btn-hero-primary" in html, "2.15 Hero CTA primary action button present")

    # 2.5 Contest Sections / Tables
    runner.check("contests-grid-layout" in html, "2.16 Two-column grid layout present")
    runner.check("section-past" in html or "table-past" in html, "2.17 Past contests section present")
    runner.check("contests-sidebar-col" in html, "2.18 Desktop sidebar column present")

    # 2.6 Desktop Sidebar Widgets
    runner.check("widget-calendar" in html and "mini-contest-calendar" in html, "2.19 Mini Contest Calendar widget present")
    runner.check("widget-leaders" in html and "Rating Leaders" in html, "2.20 Rating Leaders widget present")
    runner.check("widget-rules" in html and "Competition Rules" in html, "2.21 Competition Rules widget present")

    print("\n" + "=" * 60)
    print("STAGE 3: Screen 5 — Live Contest Workspace (docs/5.png)")
    print("=" * 60)

    # Find a contest to test
    contest = Contest.objects.filter(key='monthly2026').first() or Contest.objects.first()
    runner.check(contest is not None, "3.1 Test contest exists in database")

    if contest:
        resp = runner.client.get(f'/contest/{contest.key}')
        runner.check(resp.status_code == 200, f"3.2 ContestDetail for '{contest.key}' HTTP 200 OK")

        c_html = resp.content.decode('utf-8')

        # 3.3 Top Header Bar
        runner.check("contest-workspace-header" in c_html, "3.3 Contest workspace header container present")
        runner.check("contest-breadcrumb" in c_html, "3.4 Breadcrumb navigation present")
        runner.check(contest.name in c_html, "3.5 Contest title rendered accurately")
        runner.check("contest-status-pill" in c_html, "3.6 Status pill present (Live/Upcoming/Ended)")

        # 3.4 Top Right 3 Metric Cards
        runner.check("card-time" in c_html and "Time Remaining" in c_html, "3.7 Card 1: Time Remaining present")
        runner.check("contest-countdown-display" in c_html, "3.8 Countdown timer display element present")
        runner.check("card-score" in c_html and "My Score" in c_html, "3.9 Card 2: My Score present")
        runner.check("score-progress-fill" in c_html, "3.10 Score progress bar track present")
        runner.check("card-rank" in c_html and "Rank" in c_html, "3.11 Card 3: Rank card present")

        # 3.5 Contest Navigation Tabs
        runner.check("contest-nav-tabs" in c_html, "3.12 Navigation tabs bar present")
        runner.check("btn-tab-problems" in c_html and "Problems" in c_html, "3.13 Problems tab present")
        runner.check("btn-tab-submissions" in c_html and "Submissions" in c_html, "3.14 Submissions tab present")
        runner.check("btn-tab-standings" in c_html and "Standings" in c_html, "3.15 Standings tab present")
        runner.check("btn-tab-clarifications" in c_html and "Clarifications" in c_html, "3.16 Clarifications tab present")

        # 3.6 Split Layout & Problem Switcher Sidebar
        runner.check("contest-split-layout" in c_html, "3.17 Three-column split workspace container present")
        runner.check("contest-problems-sidebar" in c_html, "3.18 Contest problems sidebar present")
        runner.check("problem-letter-box" in c_html, "3.19 Problem letter badges (A, B, C...) present")
        runner.check("badge-pts" in c_html, "3.20 Problem points badge present")

        # 3.7 Problem Statement Pane
        runner.check("contest-statement-pane" in c_html, "3.21 Problem statement pane present")
        runner.check("statement-problem-title" in c_html, "3.22 Problem title rendered with letter prefix")
        runner.check("btn-star-bookmark" in c_html, "3.23 Problem bookmark star button present")
        runner.check("statement-meta-pills" in c_html, "3.24 Meta pills (points, time, memory) present")
        runner.check("statement-body-markdown" in c_html, "3.25 Statement markdown body present")

        # 3.8 Coding Workspace & Testcases Console
        runner.check("contest-editor-pane" in c_html, "3.26 Code editor pane present")
        runner.check("contest-language-select" in c_html, "3.27 Language dropdown select present")
        runner.check("btn-contest-submit" in c_html and "Ctrl+Enter" in c_html, "3.28 Orange Submit (Ctrl+Enter) button present")
        runner.check("contest-ace-editor" in c_html, "3.29 Ace editor container #contest-ace-editor present")
        runner.check("editor-console-drawer" in c_html, "3.30 Console drawer present")
        runner.check("Test Cases" in c_html and "Sample Test" in c_html, "3.31 Test Cases console panel with sample test rows present")
        runner.check("verdict-ac" in c_html, "3.32 AC verdict badge in test cases present")

        # 3.9 Clarifications Panel
        runner.check("contest-clarifications-panel" in c_html, "3.33 Clarifications drawer present")

        # 3.10 Problem Switcher by query param
        resp_prob_b = runner.client.get(f'/contest/{contest.key}?problem=good_subarrays')
        b_html = resp_prob_b.content.decode('utf-8')
        runner.check("Good Subarrays" in b_html and "B." in b_html, "3.34 Problem switcher loads Problem B (Good Subarrays)")

        resp_prob_c = runner.client.get(f'/contest/{contest.key}?problem=tree_queries')
        c2_html = resp_prob_c.content.decode('utf-8')
        runner.check("Tree Queries" in c2_html and "C." in c2_html, "3.35 Problem switcher loads Problem C (Tree Queries)")

    print("\n" + "=" * 60)
    print("STAGE 4: Client-side Interactive Logic (contests-list.js & contest-workspace.js)")
    print("=" * 60)

    # 4.1 contests-list.js Logic Analysis
    list_js = (JUDGE_ROOT / "resources" / "contests-list.js").read_text()
    runner.check("initCountdownTimer" in list_js, "4.1 Countdown timer initializer defined")
    runner.check("initFilterTabs" in list_js, "4.2 Filter tab switcher defined")
    runner.check("initMiniCalendar" in list_js, "4.3 Mini calendar generator defined")
    runner.check("initLiveSearch" in list_js, "4.4 Client-side live search defined")

    # 4.2 contest-workspace.js Logic Analysis
    ws_js = (JUDGE_ROOT / "resources" / "contest-workspace.js").read_text()
    runner.check("initContestCountdown" in ws_js, "4.5 Workspace countdown timer defined")
    runner.check("initAceEditor" in ws_js, "4.6 Ace editor setup and modes defined")
    runner.check("initConsoleTabs" in ws_js, "4.7 Console tabs switching logic defined")
    runner.check("initClarificationsToggle" in ws_js, "4.8 Clarifications toggle logic defined")
    runner.check("initBookmarkStar" in ws_js, "4.9 Bookmark star toggle logic defined")
    runner.check("Ctrl-Enter" in ws_js or "Command-Enter" in ws_js, "4.10 Keyboard shortcut Ctrl+Enter defined")

    # Remote checks if requested
    if runner.remote_url:
        print("\n" + "=" * 60)
        print(f"STAGE 5: Remote Production Server Verification ({runner.remote_url})")
        print("=" * 60)
        import urllib.request
        try:
            req_contests = urllib.request.urlopen(f"{runner.remote_url}/contests/", timeout=10)
            remote_contests_html = req_contests.read().decode('utf-8')
            runner.check(req_contests.status == 200, "5.1 Remote /contests/ HTTP 200 OK")
            runner.check("contests-catalog-wrapper" in remote_contests_html, "5.2 Remote /contests/ has contests-catalog-wrapper")
            runner.check("featured-contest-hero" in remote_contests_html, "5.3 Remote /contests/ has featured-contest-hero")

            req_contest = urllib.request.urlopen(f"{runner.remote_url}/contest/monthly2026", timeout=10)
            remote_contest_html = req_contest.read().decode('utf-8')
            runner.check(req_contest.status == 200, "5.4 Remote /contest/monthly2026 HTTP 200 OK")
            runner.check("contest-workspace-wrapper" in remote_contest_html, "5.5 Remote /contest/monthly2026 has contest-workspace-wrapper")
            runner.check("contest-split-layout" in remote_contest_html, "5.6 Remote /contest/monthly2026 has contest-split-layout")
            runner.check("contest-ace-editor" in remote_contest_html, "5.7 Remote /contest/monthly2026 has contest-ace-editor")
        except Exception as e:
            runner.check(False, "5.x Remote HTTP request error", str(e))

    runner.print_summary()
    return runner.failed == 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Verify Milestone 5 Screens 4 & 5")
    parser.add_argument('--remote', help="Remote base URL, e.g. http://100.107.199.45:8090", default=None)
    args = parser.parse_args()

    success = run_tests(remote_url=args.remote)
    sys.exit(0 if success else 1)
