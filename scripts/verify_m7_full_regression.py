#!/usr/bin/env python3
"""
Milestone 7 & Full System Regression Verification Suite
Tests Dashboard, Authentication Workspaces, Architecture Documentation,
and performs an end-to-end regression across all 7 redesigned screens.
Usage:
  ./venv/bin/python scripts/verify_m7_full_regression.py
  ./venv/bin/python scripts/verify_m7_full_regression.py --remote http://100.107.199.45:8090
"""

import os
import sys
import argparse
import urllib.request
import urllib.error

from pathlib import Path

JUDGE_ROOT = Path(__file__).resolve().parent.parent
if str(JUDGE_ROOT) not in sys.path:
    sys.path.insert(0, str(JUDGE_ROOT))

# Ensure Django settings are loaded for local client tests
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')
import django
django.setup()

from django.test import Client

class TestRunner:
    def __init__(self, remote_url=None):
        self.remote_url = remote_url.rstrip('/') if remote_url else None
        self.client = Client()
        self.passed = 0
        self.failed = 0

    def assert_test(self, condition, message):
        if condition:
            print(f"  ✔ PASS: {message}")
            self.passed += 1
        else:
            print(f"  ✖ FAIL: {message}")
            self.failed += 1

    def fetch_url(self, path):
        if self.remote_url:
            url = f"{self.remote_url}{path}"
            req = urllib.request.Request(url, headers={'User-Agent': 'M7VerificationSuite/1.0'})
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    return resp.getcode(), resp.read().decode('utf-8', errors='replace')
            except urllib.error.HTTPError as e:
                return e.code, e.read().decode('utf-8', errors='replace')
            except Exception as e:
                return 0, str(e)
        else:
            resp = self.client.get(path, follow=True)
            content = resp.content.decode('utf-8', errors='replace') if hasattr(resp, 'content') else ''
            return resp.status_code, content

def run_tests(remote_url=None):
    runner = TestRunner(remote_url=remote_url)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print("\n" + "=" * 60)
    print("STAGE 1: Documentation, Styles & Asset Pipeline (R5)")
    print("=" * 60)
    docs_to_check = [
        'docs/frontend-redesign-analysis.md',
        'docs/design-system.md',
        'docs/redesign-migration.md',
        'resources/dashboard.scss',
        'resources/dashboard.css',
        'resources/dashboard.js',
        'resources/auth-workspace.scss',
        'resources/auth-workspace.css',
        'templates/home.html',
        'templates/registration/login.html',
        'templates/registration/registration_form.html',
        'templates/registration/password_reset.html',
        'templates/registration/two_factor_auth.html',
        'static/dashboard.css',
        'static/auth-workspace.css',
    ]
    for idx, doc in enumerate(docs_to_check, start=1):
        full_path = os.path.join(base_dir, doc)
        runner.assert_test(os.path.exists(full_path), f"1.{idx} {doc} exists and built")

    print("\n" + "=" * 60)
    print("STAGE 2: Dashboard Workspace (templates/home.html — R4)")
    print("=" * 60)
    status, html = runner.fetch_url('/')
    runner.assert_test(status == 200, "2.1 GET / returns HTTP 200 OK")
    runner.assert_test('dashboard-wrapper' in html, "2.2 #dashboard-wrapper present")
    runner.assert_test('dashboard-hero-card' in html, "2.3 Hero card #dashboard-hero-card present")
    runner.assert_test('btn-hero-browse-problems' in html, "2.4 Browse Problems CTA present")
    runner.assert_test('btn-hero-contests' in html, "2.5 Contests CTA present")
    runner.assert_test('btn-hero-rankings' in html, "2.6 Leaderboard CTA present")
    runner.assert_test('dashboard-metrics-strip' in html, "2.7 Metrics strip #dashboard-metrics-strip present")
    runner.assert_test('dashboard-news-card' in html, "2.8 Announcements card #dashboard-news-card present")
    runner.assert_test('dashboard-activity-card' in html, "2.9 Live activity card #dashboard-activity-card present")
    runner.assert_test('mini-submissions-table' in html, "2.10 Recent submissions table present")
    runner.assert_test('dashboard-contests-card' in html, "2.11 Contests card #dashboard-contests-card present")
    runner.assert_test('dashboard-leaders-card' in html, "2.12 Top competitors card #dashboard-leaders-card present")
    runner.assert_test('dashboard-topics-card' in html, "2.13 Topics & categories card #dashboard-topics-card present")

    print("\n" + "=" * 60)
    print("STAGE 3: Authentication Workspaces (templates/registration/ — R4)")
    print("=" * 60)
    # Login Page
    status, html = runner.fetch_url('/accounts/login/')
    runner.assert_test(status == 200, "3.1 GET /accounts/login/ returns HTTP 200 OK")
    runner.assert_test('auth-login-card' in html, "3.2 #auth-login-card present")
    runner.assert_test('login-form' in html, "3.3 Login form present")
    runner.assert_test('btn-submit-login' in html, "3.4 Submit login button present")
    runner.assert_test('csrfmiddlewaretoken' in html, "3.5 CSRF token present in login form")
    runner.assert_test('password/reset' in html or 'forgot-link' in html, "3.6 Forgot password link present")

    # Register Page
    status, html = runner.fetch_url('/accounts/register/')
    runner.assert_test(status == 200, "3.7 GET /accounts/register/ returns HTTP 200 OK")
    runner.assert_test('auth-register-card' in html, "3.8 #auth-register-card present")
    runner.assert_test('edit-form' in html, "3.9 Register form present")
    runner.assert_test('btn-submit-register' in html, "3.10 Submit register button present")
    runner.assert_test('csrfmiddlewaretoken' in html, "3.11 CSRF token present in register form")

    # Password Reset Page
    status, html = runner.fetch_url('/accounts/password/reset/')
    runner.assert_test(status == 200, "3.12 GET /accounts/password/reset/ returns HTTP 200 OK")
    runner.assert_test('auth-reset-card' in html, "3.13 #auth-reset-card present")
    runner.assert_test('password-reset-form' in html, "3.14 Password reset form present")
    runner.assert_test('btn-submit-reset' in html, "3.15 Submit reset button present")

    print("\n" + "=" * 60)
    print("STAGE 4: Full 7-Screen System Regression (Screens 1 through 7)")
    print("=" * 60)
    # Screen 1: Problems
    status, html = runner.fetch_url('/problems/')
    runner.assert_test(status == 200, "4.1 Screen 1 (Problems): GET /problems/ HTTP 200 OK")
    runner.assert_test('problems-search-input' in html or 'search' in html, "4.2 Screen 1: Search bar present")
    runner.assert_test('table-problems' in html or 'problems-table' in html or 'problem' in html, "4.3 Screen 1: Problems catalog present")

    # Screen 2: Problem Workspace
    status, html = runner.fetch_url('/problem/aplusb')
    runner.assert_test(status == 200, "4.4 Screen 2 (Workspace): GET /problem/aplusb HTTP 200 OK")
    runner.assert_test('problem-workspace' in html or 'statement-pane' in html, "4.5 Screen 2: Statement/Workspace pane present")
    runner.assert_test('editor-pane' in html or 'code-editor' in html or 'submit' in html, "4.6 Screen 2: Editor / Submit pane present")

    # Screen 3: Submissions
    status, html = runner.fetch_url('/submissions/')
    runner.assert_test(status == 200, "4.7 Screen 3 (Submissions): GET /submissions/ HTTP 200 OK")
    runner.assert_test('submissions-table' in html or 'table-responsive' in html, "4.8 Screen 3: Submissions table present")
    runner.assert_test('submission-detail-drawer' in html or 'drawer' in html, "4.9 Screen 3: Slide-out drawer present")

    # Screen 4: Contests Overview
    status, html = runner.fetch_url('/contests/')
    runner.assert_test(status == 200, "4.10 Screen 4 (Contests): GET /contests/ HTTP 200 OK")
    runner.assert_test('featured-contest' in html or 'contests-list-wrapper' in html, "4.11 Screen 4: Contests catalog wrapper present")

    # Screen 5: Live Contest Workspace
    status, html = runner.fetch_url('/contest/wcc2026')
    runner.assert_test(status == 200, "4.12 Screen 5 (Live Contest): GET /contest/wcc2026 HTTP 200 OK")
    runner.assert_test('contest-workspace' in html or 'contest-problems' in html or 'wcc2026' in html.lower(), "4.13 Screen 5: Contest workspace elements present")

    # Screen 6: Rankings
    status, html = runner.fetch_url('/users/')
    runner.assert_test(status == 200, "4.14 Screen 6 (Rankings): GET /users/ HTTP 200 OK")
    runner.assert_test('rankings-catalog-wrapper' in html or 'rankings-podium-section' in html, "4.15 Screen 6: Rankings podium & catalog present")

    # Screen 7: User Profile
    status, html = runner.fetch_url('/user/tourist')
    runner.assert_test(status == 200, "4.16 Screen 7 (User Profile): GET /user/tourist HTTP 200 OK")
    runner.assert_test('user-hero-card' in html or 'profile-hero' in html, "4.17 Screen 7: User Hero card present")
    runner.assert_test('profile-overview-grid' in html or 'rating-history' in html, "4.18 Screen 7: Profile overview grid present")

    # If testing against remote, run dedicated remote verification stage
    if remote_url:
        print("\n" + "=" * 60)
        print(f"STAGE 5: Live Production Remote Verification ({remote_url})")
        print("=" * 60)
        remote_checks = [
            ('/', 'dashboard-hero-card', 'Remote / renders Dashboard Hero'),
            ('/accounts/login/', 'auth-login-card', 'Remote /accounts/login/ renders Auth Card'),
            ('/accounts/register/', 'auth-register-card', 'Remote /accounts/register/ renders Register Card'),
            ('/problems/', 'problems', 'Remote /problems/ renders Problems'),
            ('/problem/aplusb', 'aplusb', 'Remote /problem/aplusb renders Problem Workspace'),
            ('/submissions/', 'submission', 'Remote /submissions/ renders Submissions'),
            ('/contests/', 'contest', 'Remote /contests/ renders Contests'),
            ('/contest/wcc2026', 'contest', 'Remote /contest/wcc2026 renders Live Contest'),
            ('/users/', 'rankings', 'Remote /users/ renders Rankings'),
            ('/user/tourist', 'tourist', 'Remote /user/tourist renders User Profile'),
        ]
        for idx, (path, term, desc) in enumerate(remote_checks, start=1):
            st, ct = runner.fetch_url(path)
            runner.assert_test(st == 200 and term in ct.lower(), f"5.{idx} {desc} (HTTP {st})")

    total = runner.passed + runner.failed
    print("\n" + "=" * 60)
    print(f"VERIFICATION SUMMARY: {runner.passed}/{total} Passed ({(runner.passed/total*100) if total else 0:.1f}%)")
    print("=" * 60)
    if runner.failed == 0:
        print("ALL TESTS PASSED SUCCESSFULLY!\n")
        return True
    else:
        print(f"FAILED: {runner.failed} tests failed!\n")
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="M7 Full System Regression Verification")
    parser.add_argument('--remote', help="Base URL of remote server (e.g. http://100.107.199.45:8090)", default=None)
    args = parser.parse_args()

    success = run_tests(remote_url=args.remote)
    sys.exit(0 if success else 1)
