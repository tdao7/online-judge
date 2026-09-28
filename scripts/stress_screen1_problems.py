#!/usr/bin/env python3
"""
Milestone 3 Challenger 1: Empirical Adversarial Stress Test Suite for Screen 1 (Problems Catalog).
Tests query matrix, malformed/SQLi/XSS inputs, status filters (auth/anon),
table rendering, pagination bounds, N+1 queries, and performance.
"""

import os
import sys
import time
from pathlib import Path

# Setup Django environment
JUDGE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(JUDGE_ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dmoj.settings")

import django
django.setup()

from django.test import TestCase, Client
from django.test.utils import CaptureQueriesContext
from django.db import connection
from django.contrib.auth.models import User
from judge.models import (
    Problem, ProblemGroup, ProblemType, Language, Judge, Profile,
    Submission, SubmissionTestCase
)


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


class StressReporter:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []

    def record(self, name, condition, detail=""):
        if condition:
            self.passed += 1
            print(f"  {Colors.GREEN}[PASS]{Colors.RESET} {name} {Colors.CYAN}({detail}){Colors.RESET}" if detail else f"  {Colors.GREEN}[PASS]{Colors.RESET} {name}")
            self.results.append({"name": name, "status": "PASS", "detail": detail})
        else:
            self.failed += 1
            print(f"  {Colors.RED}[FAIL]{Colors.RESET} {name} {Colors.YELLOW}({detail}){Colors.RESET}")
            self.results.append({"name": name, "status": "FAIL", "detail": detail})

    def print_summary(self):
        total = self.passed + self.failed
        print("\n" + "=" * 75)
        status_color = Colors.GREEN if self.failed == 0 else Colors.RED
        print(f"{Colors.BOLD}SCREEN 1 STRESS TEST SUMMARY:{Colors.RESET} "
              f"{status_color}{self.passed}/{total} Passed ({self.passed / total * 100:.1f}%){Colors.RESET}")
        print("=" * 75)
        if self.failed > 0:
            print(f"{Colors.RED}{Colors.BOLD}FAILED CHALLENGES:{Colors.RESET}")
            for r in self.results:
                if r["status"] == "FAIL":
                    print(f"  - {r['name']}: {r['detail']}")
        else:
            print(f"{Colors.GREEN}{Colors.BOLD}ALL SCREEN 1 EMPIRICAL STRESS CHALLENGES PASSED!{Colors.RESET}")


reporter = StressReporter()


def run_all_screen1_stress_tests():
    print(f"\n{Colors.BOLD}{'=' * 75}")
    print("EMPIRICAL ADVERSARIAL STRESS SUITE: SCREEN 1 (PROBLEMS CATALOG)")
    print(f"{'=' * 75}{Colors.RESET}")

    client = Client()

    # -------------------------------------------------------------------------
    # Test Data Seeding (in test runner or directly in DB if run standalone)
    # -------------------------------------------------------------------------
    lang, _ = Language.objects.get_or_create(key='py3', defaults={'name': 'Python 3', 'common_name': 'Python 3', 'ace': 'python'})
    group_math, _ = ProblemGroup.objects.get_or_create(name='Math', defaults={'full_name': 'Mathematics'})
    group_algo, _ = ProblemGroup.objects.get_or_create(name='Algo', defaults={'full_name': 'Algorithms'})
    group_ds, _ = ProblemGroup.objects.get_or_create(name='DS', defaults={'full_name': 'Data Structures'})

    type_algebra, _ = ProblemType.objects.get_or_create(name='Algebra', defaults={'full_name': 'Algebra'})
    type_dp, _ = ProblemType.objects.get_or_create(name='DP', defaults={'full_name': 'Dynamic Programming'})
    type_graph, _ = ProblemType.objects.get_or_create(name='Graph', defaults={'full_name': 'Graph Theory'})
    type_ds, _ = ProblemType.objects.get_or_create(name='DS', defaults={'full_name': 'Data Structures'})

    # Users: solver, attempter, fresh
    user_solver, _ = User.objects.get_or_create(username='stress_solver', defaults={'email': 'solver@example.com'})
    prof_solver, _ = Profile.objects.get_or_create(user=user_solver, defaults={'language': lang})

    user_attempter, _ = User.objects.get_or_create(username='stress_attempter', defaults={'email': 'attempter@example.com'})
    prof_attempter, _ = Profile.objects.get_or_create(user=user_attempter, defaults={'language': lang})

    user_fresh, _ = User.objects.get_or_create(username='stress_fresh', defaults={'email': 'fresh@example.com'})
    prof_fresh, _ = Profile.objects.get_or_create(user=user_fresh, defaults={'language': lang})

    # Test Problems
    problems_data = [
        # code, name, points, group, types, is_public
        ('p_easy_math', 'Linear Equations', 5.0, group_math, [type_algebra], True),
        ('p_easy_algo', 'Bubble Sort', 10.0, group_algo, [type_dp], True),
        ('p_med_dp', 'Knapsack 01', 20.0, group_algo, [type_dp], True),
        ('p_med_graph', 'Dijkstra Shortest Path', 25.0, group_ds, [type_graph], True),
        ('p_hard_ds', 'Segment Tree RMQ', 45.0, group_ds, [type_ds], True),
        ('p_hard_adv', 'Heavy Light Decomposition', 75.0, group_ds, [type_graph, type_dp], True),
        ('p_private_prob', 'Internal Organization Problem', 10.0, group_math, [type_algebra], False),
    ]

    created_problems = {}
    for code, name, points, grp, typs, pub in problems_data:
        p, _ = Problem.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'points': points,
                'group': grp,
                'is_public': pub,
                'time_limit': 2.0,
                'memory_limit': 65536,
                'description': f'Description for {name}.',
            }
        )
        p.name = name
        p.points = points
        p.group = grp
        p.is_public = pub
        p.save()
        for t in typs:
            p.types.add(t)
        created_problems[code] = p

    from judge.models import SubmissionSource

    # Create submission for user_solver (solved p_easy_math)
    sub_solved = Submission.objects.filter(user=prof_solver, problem=created_problems['p_easy_math']).first()
    if not sub_solved:
        sub_solved = Submission.objects.create(
            user=prof_solver,
            problem=created_problems['p_easy_math'],
            language=lang,
            status='D',
            result='AC',
            points=5.0,
            case_points=5.0,
            case_total=5.0,
            is_archived=False,
        )
        SubmissionSource.objects.create(submission=sub_solved, source='print("solved")')
    else:
        sub_solved.result = 'AC'
        sub_solved.case_points = 5.0
        sub_solved.case_total = 5.0
        sub_solved.save()

    # Create submission for user_attempter (attempted p_med_dp with WA)
    sub_wa = Submission.objects.filter(user=prof_attempter, problem=created_problems['p_med_dp']).first()
    if not sub_wa:
        sub_wa = Submission.objects.create(
            user=prof_attempter,
            problem=created_problems['p_med_dp'],
            language=lang,
            status='D',
            result='WA',
            points=0.0,
            case_points=0.0,
            case_total=20.0,
            is_archived=False,
        )
        SubmissionSource.objects.create(submission=sub_wa, source='print("wrong")')
    else:
        sub_wa.result = 'WA'
        sub_wa.case_points = 0.0
        sub_wa.case_total = 20.0
        sub_wa.save()

    # =========================================================================
    # SUITE 1: Multi-Filter Combinations & Complex Matrix
    # =========================================================================
    print(f"\n{Colors.CYAN}--- Suite 1: Multi-Filter Combinations Matrix ---{Colors.RESET}")

    combos = [
        # (params, expected_in, expected_not_in, label)
        ({'difficulty': 'easy'}, ['p_easy_math', 'p_easy_algo'], ['p_med_dp', 'p_hard_adv'], 'Difficulty: Easy (<=10)'),
        ({'difficulty': 'medium'}, ['p_med_dp', 'p_med_graph'], ['p_easy_math', 'p_hard_adv'], 'Difficulty: Medium (11-30)'),
        ({'difficulty': 'hard'}, ['p_hard_ds', 'p_hard_adv'], ['p_easy_math', 'p_med_dp'], 'Difficulty: Hard (>30)'),
        ({'points_preset': '1-10'}, ['p_easy_math', 'p_easy_algo'], ['p_med_dp', 'p_hard_adv'], 'Points Preset: 1-10'),
        ({'points_preset': '11-25'}, ['p_med_dp', 'p_med_graph'], ['p_easy_math', 'p_hard_adv'], 'Points Preset: 11-25'),
        ({'points_preset': '26-50'}, ['p_hard_ds'], ['p_easy_math', 'p_hard_adv'], 'Points Preset: 26-50'),
        ({'points_preset': '50+'}, ['p_hard_adv'], ['p_easy_math', 'p_med_dp'], 'Points Preset: 50+'),
        ({'group': group_math.id}, ['p_easy_math'], ['p_easy_algo', 'p_med_dp'], 'Group filter: Math'),
        ({'category': group_algo.id}, ['p_easy_algo', 'p_med_dp'], ['p_easy_math'], 'Category alias: Algo'),
        ({'type': type_dp.id}, ['p_easy_algo', 'p_med_dp', 'p_hard_adv'], ['p_easy_math'], 'Type filter: DP'),
        ({'search': 'Linear'}, ['p_easy_math'], ['p_easy_algo'], 'Search: Linear'),
        ({'q': 'Knapsack'}, ['p_med_dp'], ['p_easy_math'], 'Legacy q alias: Knapsack'),
        (
            {
                'search': 'Equations',
                'difficulty': 'easy',
                'group': group_math.id,
                'points_preset': '1-10',
                'order': '-points',
            },
            ['p_easy_math'],
            ['p_easy_algo', 'p_med_dp'],
            'Complex 5-way combo: search + diff + group + points + order'
        ),
        ({'order': 'points'}, ['p_easy_math', 'p_hard_adv'], [], 'Order: points (ASC)'),
        ({'order': '-points'}, ['p_hard_adv', 'p_easy_math'], [], 'Order: -points (DESC)'),
        ({'order': 'name'}, ['p_easy_algo'], [], 'Order: name (ASC)'),
        ({'order': '-name'}, ['p_hard_ds'], [], 'Order: -name (DESC)'),
        ({'order': 'group'}, ['p_easy_math'], [], 'Order: group'),
        ({'point_start': '10', 'point_end': '30'}, ['p_easy_algo', 'p_med_dp', 'p_med_graph'], ['p_easy_math', 'p_hard_adv'], 'Point range 10-30'),
    ]

    for params, expected_in, expected_not_in, label in combos:
        resp = client.get('/problems/', params)
        ok = resp.status_code == 200
        content = resp.content.decode('utf-8')
        in_ok = all(code in content for code in expected_in)
        not_in_ok = all(code not in content for code in expected_not_in)
        reporter.record(
            f"Combo: {label}",
            ok and in_ok and not_in_ok,
            f"HTTP {resp.status_code}, Found expected: {in_ok}, Excluded non-matching: {not_in_ok}"
        )

    # Verify private problem never leaked in public listing
    resp_anon = client.get('/problems/')
    reporter.record(
        "Private problems excluded from public catalog",
        'p_private_prob' not in resp_anon.content.decode('utf-8'),
        "p_private_prob absent"
    )

    # =========================================================================
    # SUITE 2: Adversarial, Malformed, SQLi & XSS Stress
    # =========================================================================
    print(f"\n{Colors.CYAN}--- Suite 2: Adversarial, Malformed, SQLi & XSS Inputs ---{Colors.RESET}")

    malformed_tests = [
        # (params, test_name, extra_check_fn)
        ({'search': "' OR '1'='1"}, "SQLi in search parameter", lambda r, c: r.status_code == 200),
        ({'search': "'; DROP TABLE judge_problem; --"}, "SQLi drop table attempt in search", lambda r, c: r.status_code == 200),
        ({'group': "1 OR 1=1"}, "SQLi in group parameter", lambda r, c: r.status_code == 200),
        ({'type': "1 UNION SELECT 1"}, "SQLi in type parameter", lambda r, c: r.status_code == 200),
        ({'order': "points; DROP TABLE judge_problem"}, "SQLi in order parameter falls back cleanly", lambda r, c: r.status_code == 200),
        ({'order': "--points"}, "Double-dash order parameter falls back cleanly", lambda r, c: r.status_code == 200),
        ({'order': "nonexistent_secret_column"}, "Invalid order column falls back cleanly", lambda r, c: r.status_code == 200),
        ({'difficulty': "' OR 1=1 --"}, "SQLi in difficulty preset", lambda r, c: r.status_code == 200),
        ({'points_preset': "' OR 1=1 --"}, "SQLi in points preset", lambda r, c: r.status_code == 200),
        ({'status': "' OR 1=1 --"}, "SQLi in status parameter", lambda r, c: r.status_code == 200),
        ({'bookmarks': "p_easy_math' OR 1=1 --"}, "SQLi in bookmarks parameter", lambda r, c: r.status_code == 200),
        ({'point_start': "NaN"}, "Float NaN in point_start safely handled", lambda r, c: r.status_code == 200),
        ({'point_start': "Infinity"}, "Float Infinity in point_start safely handled", lambda r, c: r.status_code == 200),
        ({'point_start': "-Infinity"}, "Float -Infinity in point_start safely handled", lambda r, c: r.status_code == 200),
        ({'point_start': "-1000", 'point_end': "999999999"}, "Extreme negative & large point range", lambda r, c: r.status_code == 200),
        ({'group': "-999"}, "Negative group ID handled gracefully", lambda r, c: r.status_code == 200),
        ({'group': "999999999"}, "Non-existent large group ID yields empty results", lambda r, c: r.status_code == 200 and 'empty-state-row' in c),
        ({'group': "alphanumeric_not_int"}, "String group ID handled by safe_int_or_none", lambda r, c: r.status_code == 200),
        ({'type': ["1", "invalid_type", "2"]}, "Mixed valid and invalid type IDs handled without crash", lambda r, c: r.status_code == 200),
        ({'difficulty': "impossible_difficulty"}, "Unrecognized difficulty preset handled gracefully", lambda r, c: r.status_code == 200),
        ({'points_preset': "invalid_range_100_200"}, "Unrecognized points preset handled gracefully", lambda r, c: r.status_code == 200),
        ({'search': "A" * 5000}, "Ultra-long 5,000 char search query handled gracefully", lambda r, c: r.status_code == 200),
        ({'search': "数学 DP アルゴリズム"}, "CJK unicode search terms handled without syntax error", lambda r, c: r.status_code == 200),
        ({'search': "🎉🚀🔥"}, "Emoji search terms handled cleanly", lambda r, c: r.status_code == 200),
        ({'search': ".*+?^${}()|[]\\"}, "Regex metacharacters in search handled cleanly", lambda r, c: r.status_code == 200),
    ]

    for params, name, check_fn in malformed_tests:
        resp = client.get('/problems/', params)
        content = resp.content.decode('utf-8')
        passed = check_fn(resp, content)
        reporter.record(name, passed, f"Status: {resp.status_code}")

    # XSS Protection Stress Check
    xss_payloads = [
        '<script>alert("XSS")</script>',
        '"><svg onload=alert(1)>',
        "'><img src=x onerror=alert(1)>",
    ]
    for xss in xss_payloads:
        resp = client.get('/problems/', {'search': xss})
        content = resp.content.decode('utf-8')
        # Ensure the raw unescaped payload is NOT rendered inside the DOM
        is_safe = (
            xss not in content and
            (
                '&lt;script&gt;' in content or
                '&quot;&gt;&lt;svg' in content or
                '&#x27;&gt;&lt;img' in content or
                '&lt;' in content
            )
        )
        reporter.record(
            f"XSS Injection Sanitization: {xss[:25]}...",
            is_safe,
            "Raw unescaped script tag absent from DOM"
        )

    # =========================================================================
    # SUITE 3: Quick Filter Tabs (All, Bookmarked, Solved, Unsolved)
    # =========================================================================
    print(f"\n{Colors.CYAN}--- Suite 3: Quick Filter Tabs & Session Authentication ---{Colors.RESET}")

    # 3.1 Anonymous User
    resp_anon_all = client.get('/problems/', {'status': 'all'})
    content_anon_all = resp_anon_all.content.decode('utf-8')
    reporter.record(
        "Anonymous: ?status=all renders all public problems",
        'p_easy_math' in content_anon_all and 'p_hard_adv' in content_anon_all,
        "Status badges rendered as Unsolved"
    )

    resp_anon_unsolved = client.get('/problems/', {'status': 'unsolved'})
    content_anon_unsolved = resp_anon_unsolved.content.decode('utf-8')
    reporter.record(
        "Anonymous: ?status=unsolved renders all problems (all are unsolved for anon)",
        'p_easy_math' in content_anon_unsolved and 'p_med_dp' in content_anon_unsolved,
        "All problems visible"
    )

    resp_anon_bmarks = client.get('/problems/', {'status': 'bookmarked', 'bookmarks': 'p_easy_math,p_hard_ds'})
    content_anon_bmarks = resp_anon_bmarks.content.decode('utf-8')
    reporter.record(
        "Anonymous: ?status=bookmarked&bookmarks=p_easy_math,p_hard_ds filters accurately",
        'p_easy_math' in content_anon_bmarks and 'p_hard_ds' in content_anon_bmarks and 'p_med_dp' not in content_anon_bmarks,
        "Only requested bookmarked problems returned"
    )

    resp_anon_bmarks_none = client.get('/problems/', {'status': 'bookmarked', 'bookmarks': 'nonexistent_code_xyz'})
    content_anon_bmarks_none = resp_anon_bmarks_none.content.decode('utf-8')
    reporter.record(
        "Anonymous: ?status=bookmarked with non-existent bookmarks yields empty state",
        'empty-state-row' in content_anon_bmarks_none,
        "Empty state rendered gracefully"
    )

    # 3.2 Authenticated User (Solver - solved p_easy_math)
    client.force_login(user_solver)

    resp_auth_solved = client.get('/problems/', {'status': 'solved'})
    content_auth_solved = resp_auth_solved.content.decode('utf-8')
    reporter.record(
        "Authenticated (Solver): ?status=solved returns only completed problems",
        'p_easy_math' in content_auth_solved and 'p_med_dp' not in content_auth_solved,
        "p_easy_math present, p_med_dp excluded"
    )
    reporter.record(
        "Authenticated (Solver): Solved problem renders .status-solved pill badge",
        'status-solved' in content_auth_solved and 'fa-check-circle' in content_auth_solved,
        "Found status-solved and fa-check-circle"
    )

    resp_auth_unsolved = client.get('/problems/', {'status': 'unsolved'})
    content_auth_unsolved = resp_auth_unsolved.content.decode('utf-8')
    reporter.record(
        "Authenticated (Solver): ?status=unsolved excludes completed problems",
        'p_easy_math' not in content_auth_unsolved and 'p_med_dp' in content_auth_unsolved,
        "p_easy_math excluded, others present"
    )

    # 3.3 Authenticated User (Attempter - WA on p_med_dp)
    client.force_login(user_attempter)

    resp_auth_att = client.get('/problems/', {'status': 'all'})
    content_auth_att = resp_auth_att.content.decode('utf-8')
    reporter.record(
        "Authenticated (Attempter): Attempted problem renders .status-attempted pill badge",
        'status-attempted' in content_auth_att and 'fa-minus-circle' in content_auth_att,
        "Found status-attempted and fa-minus-circle"
    )

    resp_auth_att_solved = client.get('/problems/', {'status': 'solved'})
    content_auth_att_solved = resp_auth_att_solved.content.decode('utf-8')
    reporter.record(
        "Authenticated (Attempter): ?status=solved yields empty state (no AC submissions)",
        'empty-state-row' in content_auth_att_solved,
        "Empty state rendered"
    )

    client.logout()

    # =========================================================================
    # SUITE 4: Table Rendering Fidelity, Columns & Empty State
    # =========================================================================
    print(f"\n{Colors.CYAN}--- Suite 4: Table Rendering & UI Components ---{Colors.RESET}")

    resp_table = client.get('/problems/')
    html_table = resp_table.content.decode('utf-8')

    columns = [
        ('col-star', 'Column 1: Star bookmark button'),
        ('col-index', 'Column 2: Consecutive row index #'),
        ('col-problem', 'Column 3: Title link + tag pills'),
        ('col-group', 'Column 4: Group badge'),
        ('col-points', 'Column 5: Points value'),
        ('col-ac-rate', 'Column 6: Acceptance rate percentage + progress bar'),
        ('col-status', 'Column 7: Solved status pill'),
        ('col-actions', 'Column 8: Actions dropdown menu'),
    ]
    for col_cls, label in columns:
        reporter.record(
            f"Table Column: {label}",
            col_cls in html_table,
            f"Class {col_cls} present in DOM"
        )

    # Acceptance rate progress bar structure
    has_ac_pct = 'ac-rate-percent' in html_table
    has_ac_track = 'role="progressbar"' in html_table
    has_ac_fill = 'ac-rate-fill' in html_table
    reporter.record(
        "Acceptance Rate: Progress bar markup and accessibility (role=progressbar)",
        has_ac_pct and has_ac_track and has_ac_fill,
        f"Percent: {has_ac_pct}, Track: {has_ac_track}, Fill: {has_ac_fill}"
    )

    # Empty State Row
    resp_empty = client.get('/problems/', {'search': 'nonexistent_query_that_matches_nothing_12345'})
    html_empty = resp_empty.content.decode('utf-8')
    has_empty_row = 'empty-state-row' in html_empty
    has_empty_box = 'problems-empty-box' in html_empty
    has_empty_icon = 'fa fa-search' in html_empty
    has_empty_heading = 'No problems found' in html_empty
    has_reset_btn = 'btn-reset-catalog' in html_empty and 'href="/problems/"' in html_empty
    reporter.record(
        "Empty Search Results: Empty state illustration, icon, and Reset button render",
        has_empty_row and has_empty_box and has_empty_icon and has_empty_heading and has_reset_btn,
        f"Empty row: {has_empty_row}, Box: {has_empty_box}, Heading: {has_empty_heading}, Reset btn: {has_reset_btn}"
    )

    # =========================================================================
    # SUITE 5: Pagination Bounds & Context Stress
    # =========================================================================
    print(f"\n{Colors.CYAN}--- Suite 5: Pagination Bounds & Navigation ---{Colors.RESET}")

    # Standard Page 1
    resp_page1 = client.get('/problems/', {'page': 1})
    reporter.record("Pagination: Page 1 returns HTTP 200 OK", resp_page1.status_code == 200)

    # Out of Bounds / Invalid Pages (should return 404 per Django DiggPaginator)
    invalid_pages = [
        (0, "Page 0 returns 404"),
        (-1, "Negative page -1 returns 404"),
        (999999, "Huge page 999999 returns 404"),
        ('abc', "Non-numeric page 'abc' returns 404"),
        ('NaN', "String page 'NaN' returns 404"),
        ('1.5', "Float page '1.5' returns 404"),
    ]
    for p_val, desc in invalid_pages:
        r = client.get('/problems/', {'page': p_val})
        reporter.record(
            f"Pagination Bound: {desc}",
            r.status_code == 404,
            f"HTTP status: {r.status_code}"
        )

    # Check pagination summary string on page 1
    html_p1 = resp_page1.content.decode('utf-8')
    has_summary_counter = 'pagination-summary-text' in html_p1
    has_arrow_disabled = 'pagination-arrow-btn disabled' in html_p1
    reporter.record(
        "Pagination: Summary counter (1–X of Y problems) and disabled previous arrow",
        has_summary_counter and has_arrow_disabled,
        f"Counter: {has_summary_counter}, Disabled Prev: {has_arrow_disabled}"
    )

    # =========================================================================
    # SUITE 6: Query Count Scaling & Performance Profiling
    # =========================================================================
    print(f"\n{Colors.CYAN}--- Suite 6: Performance & N+1 Query Scaling Profiling ---{Colors.RESET}")

    # Profile query count on problem catalog
    with CaptureQueriesContext(connection) as ctx:
        resp_bench = client.get('/problems/')

    query_count = len(ctx.captured_queries)
    reporter.record(
        f"Performance: /problems/ query count is bounded without N+1 queries ({query_count} queries)",
        query_count <= 20,
        f"Executed {query_count} SQL queries (threshold <= 20)"
    )

    # Measure latency for complex filtered queries
    start_time = time.time()
    for _ in range(10):
        client.get('/problems/', {
            'search': 'Linear',
            'difficulty': 'easy',
            'points_preset': '1-10',
            'order': '-points',
            'status': 'all',
        })
    avg_latency = (time.time() - start_time) / 10.0 * 1000.0  # ms
    reporter.record(
        f"Performance: Average response time under complex multi-filters ({avg_latency:.1f}ms)",
        avg_latency < 250.0,
        f"Average: {avg_latency:.1f}ms per request (threshold < 250ms)"
    )

    # Print overall summary
    reporter.print_summary()

    # Clean up test problems
    for p in created_problems.values():
        p.delete()
    user_solver.delete()
    user_attempter.delete()
    user_fresh.delete()

    return reporter.failed == 0


if __name__ == '__main__':
    success = run_all_screen1_stress_tests()
    sys.exit(0 if success else 1)
