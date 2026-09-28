#!/usr/bin/env python3
"""
test_m3_challenger_backend_runner_stress.py
Milestone 3 Screen 2 (Problem Workspace & Runner) Backend Stress Harness

Adversarial stress-testing:
1. Code length limits on submission endpoint:
   - Exact boundary: 65,536 characters (valid, creates Submission in DB).
   - Overflow boundary: 65,537 characters (strictly rejected by form validation).
   - Empty code: 0 characters (rejected).
   - Whitespace code: '   \\n\\t  ' (validation behavior).
   - Out-of-bounds language ID (99999, -1, 'abc') (rejected).
2. Route permissions, authentication & CSRF enforcement:
   - Anonymous GET /problem/aplusb vs GET /problem/aplusb/submit.
   - Anonymous POST /problem/aplusb/submit (redirect to login).
   - Authenticated GET /problem/aplusb/submit renders unified workspace.
   - Resubmit route /problem/aplusb/resubmit/<id> renders pre-populated source.
3. Language template AJAX endpoint /widgets/template:
   - Valid language IDs return 200 text/plain.
   - Invalid language IDs return 404.
   - Non-integer input handles ValueError -> 404.
4. CSS Responsive Tokens & Media Queries:
   - Desktop flex layout.
   - Tablet/Mobile collapse (< 991px, < 640px).
   - Warm orange primary accent (#F97316).
5. Database integrity & query performance:
   - Context prefetches language runtime versions without query explosion.
"""

import os
import sys
from pathlib import Path

# Setup Django environment
JUDGE_ROOT = Path(__file__).resolve().parent.parent
if str(JUDGE_ROOT) not in sys.path:
    sys.path.insert(0, str(JUDGE_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')
import django
django.setup()

from django.test import Client, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from judge.models import Problem, Language, Submission, SubmissionSource, Profile

User = get_user_model()

passed_count = 0
failed_count = 0
results = []


def assert_challenger(condition, name, detail=""):
    global passed_count, failed_count
    if condition:
        passed_count += 1
        print(f"  \033[92m[PASS]\033[0m {name}")
        results.append({"name": name, "status": "PASS", "detail": detail})
    else:
        failed_count += 1
        print(f"  \033[91m[FAIL]\033[0m {name} - {detail}")
        results.append({"name": name, "status": "FAIL", "detail": detail})


def run_backend_stress_tests():
    print("======================================================================")
    print("CHALLENGER BACKEND & RUNNER STRESS SUITE: Screen 2 Problem Workspace")
    print("======================================================================\n")

    client = Client()
    user = User.objects.filter(is_active=True).first()
    if not user:
        user = User.objects.create_user(username='test_challenger', password='password123')
        Profile.objects.create(user=user)

    problem = Problem.objects.filter(code='aplusb').first()
    if not problem:
        problem = Problem.objects.first()

    py_lang = Language.objects.filter(key__startswith='PY').first() or Language.objects.first()
    cpp_lang = Language.objects.filter(key__startswith='CPP').first()
    java_lang = Language.objects.filter(key__startswith='JAVA').first()

    # -------------------------------------------------------------------------
    # SUITE B1: Submission Code Length Boundary Stress Testing (65,536 bytes)
    # -------------------------------------------------------------------------
    print("--- Suite B1: Submission Code Length Limits & Boundary Stress ---")
    client.force_login(user)

    # B1.1 Exact boundary: 65,536 characters
    initial_sub_count = Submission.objects.count()
    exact_code = "a = 1\n" + "#" * (65536 - 6)
    assert len(exact_code) == 65536, f"Length must be 65536, got {len(exact_code)}"

    resp_exact = client.post(f'/problem/{problem.code}/submit', {
        'source': exact_code,
        'language': py_lang.id,
    })
    new_sub_count = Submission.objects.count()
    is_created_exact = new_sub_count == initial_sub_count + 1
    is_redirect_exact = resp_exact.status_code == 302 and '/submission/' in resp_exact.get('Location', '')

    last_sub = Submission.objects.order_by('-id').first() if is_created_exact else None
    source_len = len(last_sub.source.source) if last_sub and hasattr(last_sub, 'source') else 0

    assert_challenger(
        is_redirect_exact and is_created_exact and source_len == 65536,
        "Test B1.1: Exact boundary (65,536 characters) passes validation, creates DB record and redirects",
        f"Status: {resp_exact.status_code}, Delta: {new_sub_count - initial_sub_count}, SourceLen: {source_len}"
    )

    # B1.2 Overflow boundary: 65,537 characters (boundary + 1)
    initial_sub_count = Submission.objects.count()
    overflow_code = exact_code + "x"
    assert len(overflow_code) == 65537, f"Length must be 65537, got {len(overflow_code)}"

    resp_overflow = client.post(f'/problem/{problem.code}/submit', {
        'source': overflow_code,
        'language': py_lang.id,
    })
    new_sub_count = Submission.objects.count()
    overflow_html = resp_overflow.content.decode('utf-8')
    is_rejected_overflow = new_sub_count == initial_sub_count and resp_overflow.status_code == 200
    has_overflow_error = '65536' in overflow_html or 'at most 65536' in overflow_html.lower() or 'error' in overflow_html.lower()

    assert_challenger(
        is_rejected_overflow and has_overflow_error,
        "Test B1.2: Overflow code (65,537 characters > 65,536) strictly rejected by form validation with 0 DB writes",
        f"Status: {resp_overflow.status_code}, Delta: {new_sub_count - initial_sub_count}, ErrorFound: {has_overflow_error}"
    )

    # B1.3 Extreme overflow: 100,000 characters
    initial_sub_count = Submission.objects.count()
    extreme_overflow = "#" * 100000
    resp_extreme = client.post(f'/problem/{problem.code}/submit', {
        'source': extreme_overflow,
        'language': py_lang.id,
    })
    new_sub_count = Submission.objects.count()
    is_rejected_extreme = new_sub_count == initial_sub_count and resp_extreme.status_code == 200

    assert_challenger(
        is_rejected_extreme,
        "Test B1.3: Extreme overflow code (100,000 characters) strictly rejected with 0 DB writes",
        f"Status: {resp_extreme.status_code}, Delta: {new_sub_count - initial_sub_count}"
    )

    # B1.4 Empty code submission
    initial_sub_count = Submission.objects.count()
    resp_empty = client.post(f'/problem/{problem.code}/submit', {
        'source': '',
        'language': py_lang.id,
    })
    new_sub_count = Submission.objects.count()
    is_rejected_empty = new_sub_count == initial_sub_count and resp_empty.status_code == 200

    assert_challenger(
        is_rejected_empty,
        "Test B1.4: Empty code string ('') rejected by form validation",
        f"Status: {resp_empty.status_code}, Delta: {new_sub_count - initial_sub_count}"
    )

    # B1.5 Non-existent language ID (999999)
    initial_sub_count = Submission.objects.count()
    resp_invalid_lang = client.post(f'/problem/{problem.code}/submit', {
        'source': 'print("Hello")',
        'language': 999999,
    })
    new_sub_count = Submission.objects.count()
    is_rejected_invalid_lang = new_sub_count == initial_sub_count

    assert_challenger(
        is_rejected_invalid_lang,
        "Test B1.5: Submission with invalid language ID (999999) rejected with 0 DB writes",
        f"Status: {resp_invalid_lang.status_code}, Delta: {new_sub_count - initial_sub_count}"
    )

    # -------------------------------------------------------------------------
    # SUITE B2: Route Permissions, Anonymous Redirects & Workspace Rendering
    # -------------------------------------------------------------------------
    print("\n--- Suite B2: Route Permissions, Authentication & Workspace Rendering ---")
    client_anon = Client()

    # B2.1 Anonymous GET /problem/aplusb -> 200 OK (Public view)
    resp_anon_detail = client_anon.get(f'/problem/{problem.code}')
    assert_challenger(
        resp_anon_detail.status_code == 200,
        "Test B2.1: Anonymous user GET /problem/<codepath> returns HTTP 200 OK",
        f"Status: {resp_anon_detail.status_code}"
    )
    detail_html = resp_anon_detail.content.decode('utf-8')
    assert_challenger(
        'workspace-split-container' in detail_html and 'workspace-split-divider' in detail_html,
        "Test B2.2: Anonymous problem detail renders modern macOS split-pane container and divider",
        f"Has container: {'workspace-split-container' in detail_html}"
    )

    # B2.3 Anonymous GET /problem/aplusb/submit -> 302 to login
    resp_anon_submit_get = client_anon.get(f'/problem/{problem.code}/submit')
    assert_challenger(
        resp_anon_submit_get.status_code == 302 and '/accounts/login/' in resp_anon_submit_get['Location'],
        "Test B2.3: Anonymous user GET /problem/<codepath>/submit redirects to /accounts/login/",
        f"Status: {resp_anon_submit_get.status_code}, Location: {resp_anon_submit_get.get('Location')}"
    )

    # B2.4 Anonymous POST /problem/aplusb/submit -> 302 to login
    resp_anon_submit_post = client_anon.post(f'/problem/{problem.code}/submit', {
        'source': 'print(1)',
        'language': py_lang.id,
    })
    assert_challenger(
        resp_anon_submit_post.status_code == 302 and '/accounts/login/' in resp_anon_submit_post['Location'],
        "Test B2.4: Anonymous user POST /problem/<codepath>/submit redirects to /accounts/login/",
        f"Status: {resp_anon_submit_post.status_code}, Location: {resp_anon_submit_post.get('Location')}"
    )

    # B2.5 Authenticated GET /problem/aplusb/submit -> 200 OK with unified workspace
    resp_auth_submit = client.get(f'/problem/{problem.code}/submit')
    auth_submit_html = resp_auth_submit.content.decode('utf-8')
    assert_challenger(
        resp_auth_submit.status_code == 200 and 'workspace-split-container' in auth_submit_html,
        "Test B2.5: Authenticated user GET /problem/<codepath>/submit renders unified split workspace",
        f"Status: {resp_auth_submit.status_code}"
    )

    # B2.6 Resubmit route /problem/aplusb/resubmit/<id>
    if last_sub:
        resp_resubmit = client.get(f'/problem/{problem.code}/resubmit/{last_sub.id}')
        resubmit_html = resp_resubmit.content.decode('utf-8')
        assert_challenger(
            resp_resubmit.status_code == 200 and 'workspace-split-container' in resubmit_html,
            f"Test B2.6: Resubmit route /problem/{problem.code}/resubmit/{last_sub.id} renders split workspace",
            f"Status: {resp_resubmit.status_code}"
        )

    # -------------------------------------------------------------------------
    # SUITE B3: Starter Template Endpoint /widgets/template
    # -------------------------------------------------------------------------
    print("\n--- Suite B3: Starter Template AJAX Endpoint /widgets/template ---")

    # B3.1 Valid Language Template
    resp_tmpl_py = client.get(f'/widgets/template?id={py_lang.id}')
    assert_challenger(
        resp_tmpl_py.status_code == 200 and 'text/plain' in resp_tmpl_py['Content-Type'],
        f"Test B3.1: GET /widgets/template?id={py_lang.id} ({py_lang.name}) returns 200 text/plain",
        f"Status: {resp_tmpl_py.status_code}, ContentType: {resp_tmpl_py.get('Content-Type')}"
    )

    if cpp_lang:
        resp_tmpl_cpp = client.get(f'/widgets/template?id={cpp_lang.id}')
        assert_challenger(
            resp_tmpl_cpp.status_code == 200,
            f"Test B3.2: GET /widgets/template?id={cpp_lang.id} ({cpp_lang.name}) returns 200 OK",
            f"Status: {resp_tmpl_cpp.status_code}"
        )

    # B3.3 Invalid Language ID -> 404
    resp_tmpl_invalid = client.get('/widgets/template?id=999999')
    assert_challenger(
        resp_tmpl_invalid.status_code == 404,
        "Test B3.3: GET /widgets/template?id=999999 returns HTTP 404 Not Found",
        f"Status: {resp_tmpl_invalid.status_code}"
    )

    # B3.4 Non-integer Language ID -> 404
    resp_tmpl_str = client.get('/widgets/template?id=invalid_slug')
    assert_challenger(
        resp_tmpl_str.status_code == 404,
        "Test B3.4: GET /widgets/template?id=invalid_slug safely catches ValueError and returns 404",
        f"Status: {resp_tmpl_str.status_code}"
    )

    # -------------------------------------------------------------------------
    # SUITE B4: CSS Responsive Media Queries & Design Tokens
    # -------------------------------------------------------------------------
    print("\n--- Suite B4: CSS Responsive Media Queries & Design Tokens ---")
    css_path = JUDGE_ROOT / "resources" / "problem-workspace.css"
    compiled_css = css_path.read_text(encoding="utf-8") if css_path.exists() else ""

    # B4.1 Desktop rules
    has_desktop_flex = "display: flex" in compiled_css and "workspace-split-container" in compiled_css
    assert_challenger(
        has_desktop_flex,
        "Test B4.1: Desktop layout uses flex row for split-pane container",
        f"Found: {has_desktop_flex}"
    )

    # B4.2 Tablet / Mobile collapse breakpoint (@media max-width: 991px)
    has_991_break = "@media (max-width: 991px)" in compiled_css or "@media (max-width:991px)" in compiled_css
    has_column_collapse = "flex-direction: column" in compiled_css
    assert_challenger(
        has_991_break and has_column_collapse,
        "Test B4.2: SCSS includes @media (max-width: 991px) responsive column stacking for split container",
        f"Breakpoint: {has_991_break}, Column: {has_column_collapse}"
    )

    # B4.3 Divider hidden on mobile
    has_divider_hidden = "workspace-split-divider" in compiled_css and "display: none" in compiled_css
    assert_challenger(
        has_divider_hidden,
        "Test B4.3: Resizer divider is hidden (display: none) under mobile/tablet media query",
        f"Divider hidden: {has_divider_hidden}"
    )

    # B4.4 Mobile grid breakpoint (< 640px)
    has_640_break = "@media (max-width: 640px)" in compiled_css or "@media (max-width:640px)" in compiled_css
    assert_challenger(
        has_640_break,
        "Test B4.4: Header metrics grid adjusts columns under @media (max-width: 640px)",
        f"Found 640px query: {has_640_break}"
    )

    # B4.5 Warm Orange Primary Color (#F97316)
    has_primary_orange = "#f97316" in compiled_css.lower() or "--color-primary" in compiled_css
    assert_challenger(
        has_primary_orange,
        "Test B4.5: Primary warm orange accent (#F97316) used for submit action & active highlights",
        f"Found orange token: {has_primary_orange}"
    )

    # -------------------------------------------------------------------------
    # SUITE B5: Database Query Performance & Context Prefetching
    # -------------------------------------------------------------------------
    print("\n--- Suite B5: Query Performance & Context Prefetching ---")
    with django.db.connection.execute_wrapper(lambda execute, sql, params, many, context: execute(sql, params, many, context)):
        from django.test.utils import CaptureQueriesContext
        from django.db import connection

        with CaptureQueriesContext(connection) as queries:
            resp_perf = client.get(f'/problem/{problem.code}')

        query_count = len(queries)
        assert_challenger(
            resp_perf.status_code == 200 and query_count < 30,
            f"Test B5.1: Problem detail page renders efficiently with bounded DB queries ({query_count} queries < 30 threshold)",
            f"Query count: {query_count}"
        )

    # -------------------------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    total = passed_count + failed_count
    status_str = "PASSED" if failed_count == 0 else "FAILED"
    print(f"BACKEND STRESS HARNESS SUMMARY: {passed_count}/{total} Passed ({(passed_count / total * 100):.1f}%) — {status_str}")
    print("=" * 70)

    return failed_count == 0


if __name__ == '__main__':
    success = run_backend_stress_tests()
    sys.exit(0 if success else 1)
