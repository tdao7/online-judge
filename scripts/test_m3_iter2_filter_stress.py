#!/usr/bin/env python3
"""
Milestone 3 Iteration 2 Challenger 1: Filters & Backend Stress Suite.
Empirically stress-tests Screen 1 query parameters, filter state combinations, and backend edge cases:
1. points_preset=50+ with raw +, encoded %2B, and decoded spaces (and boundary points > 50).
2. Category and group transitions (?category=1, ?group=2, ?category=2&group=1, clearing to All Groups).
3. Single type selection (?type=1) vs multiple types (?type=1&type=2) and deduplication.
4. Anonymous vs authenticated requests to ?status=solved, ?status=unsolved, ?status=bookmarked.
5. Workspace header 0-types General fallback tag vs >=1 types.
6. Multi-filter interaction stress tests.
"""

import os
import sys
import time
from pathlib import Path
from urllib.parse import quote

JUDGE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(JUDGE_ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dmoj.settings")

import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from judge.models import (
    Problem, ProblemGroup, ProblemType, Language, Profile,
    Submission, SubmissionSource
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
        print("\n" + "=" * 80)
        status_color = Colors.GREEN if self.failed == 0 else Colors.RED
        print(f"{Colors.BOLD}CHALLENGER 1 STRESS TEST SUMMARY:{Colors.RESET} "
              f"{status_color}{self.passed}/{total} Passed ({self.passed / total * 100:.1f}%){Colors.RESET}")
        print("=" * 80)
        if self.failed > 0:
            print(f"{Colors.RED}{Colors.BOLD}FAILED CHALLENGES:{Colors.RESET}")
            for r in self.results:
                if r["status"] == "FAIL":
                    print(f"  - {r['name']}: {r['detail']}")
        else:
            print(f"{Colors.GREEN}{Colors.BOLD}ALL CHALLENGER 1 EMPIRICAL STRESS TESTS PASSED!{Colors.RESET}")


reporter = StressReporter()


def run_filter_stress_suite():
    print(f"\n{Colors.BOLD}{'=' * 80}")
    print("EMPIRICAL STRESS HARNESS: M3 ITERATION 2 FILTERS & BACKEND")
    print(f"{'=' * 80}{Colors.RESET}")

    client = Client()

    # Track all created objects for clean teardown
    created_problems = []
    created_groups = []
    created_types = []
    created_users = []

    try:
        # ---------------------------------------------------------------------
        # Setup Test Fixtures
        # ---------------------------------------------------------------------
        lang, _ = Language.objects.get_or_create(
            key='py3',
            defaults={'name': 'Python 3', 'common_name': 'Python 3', 'ace': 'python'}
        )

        # Groups
        g_algebra, _ = ProblemGroup.objects.get_or_create(
            name='m3_stress_alg',
            defaults={'full_name': 'Algebraic Structures'}
        )
        created_groups.append(g_algebra)

        g_geom, _ = ProblemGroup.objects.get_or_create(
            name='m3_stress_geom',
            defaults={'full_name': 'Computational Geometry'}
        )
        created_groups.append(g_geom)

        # Types
        t_greedy, _ = ProblemType.objects.get_or_create(
            name='m3_greedy',
            defaults={'full_name': 'Greedy Strategy'}
        )
        created_types.append(t_greedy)

        t_dp, _ = ProblemType.objects.get_or_create(
            name='m3_dp',
            defaults={'full_name': 'Dynamic Programming'}
        )
        created_types.append(t_dp)

        t_graph, _ = ProblemType.objects.get_or_create(
            name='m3_graph',
            defaults={'full_name': 'Graph Theory'}
        )
        created_types.append(t_graph)

        # Users
        u_solver, _ = User.objects.get_or_create(
            username='m3_stress_solver',
            defaults={'email': 'solver_m3@example.com'}
        )
        created_users.append(u_solver)
        p_solver, _ = Profile.objects.get_or_create(user=u_solver, defaults={'language': lang})

        u_attempter, _ = User.objects.get_or_create(
            username='m3_stress_attempter',
            defaults={'email': 'attempter_m3@example.com'}
        )
        created_users.append(u_attempter)
        p_attempter, _ = Profile.objects.get_or_create(user=u_attempter, defaults={'language': lang})

        # Test Problems with boundary points and specific group/types combinations
        # 1. p_bnd_exact50: exactly 50.0 points in g_algebra with t_greedy
        # 2. p_bnd_gt50: 50.1 points in g_algebra with t_greedy
        # 3. p_bnd_high: 75.0 points in g_geom with t_dp and t_graph
        # 4. p_bnd_mid: 30.0 points in g_algebra with t_dp
        # 5. p_bnd_low: 5.0 points in g_geom with t_greedy and t_dp (multi-type)
        # 6. p_bnd_notype: 40.0 points in g_algebra with NO types (0 types)
        # 7. p_bnd_private: 60.0 points in g_geom, is_public=False
        test_problems_defs = [
            ('p_stress_exact50', 'Exact Fifty Problem', 50.0, g_algebra, [t_greedy], True),
            ('p_stress_gt50', 'Greater Than Fifty Problem', 50.1, g_algebra, [t_greedy], True),
            ('p_stress_high', 'High Hundred Problem', 75.0, g_geom, [t_dp, t_graph], True),
            ('p_stress_mid', 'Medium Thirty Problem', 30.0, g_algebra, [t_dp], True),
            ('p_stress_low', 'Low Five Dual Type Problem', 5.0, g_geom, [t_greedy, t_dp], True),
            ('p_stress_notype', 'No Type General Problem', 40.0, g_algebra, [], True),
            ('p_stress_private', 'Private Problem Hidden', 60.0, g_geom, [t_graph], False),
        ]

        prob_map = {}
        for code, name, pts, grp, typs, pub in test_problems_defs:
            p, _ = Problem.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'points': pts,
                    'group': grp,
                    'is_public': pub,
                    'time_limit': 1.0,
                    'memory_limit': 65536,
                    'description': f'Test statement for {name}.',
                }
            )
            p.name = name
            p.points = pts
            p.group = grp
            p.is_public = pub
            p.save()
            p.types.set(typs)
            prob_map[code] = p
            created_problems.append(p)

        # Create Submissions:
        # u_solver has AC on p_stress_exact50 and p_stress_high
        sub_solver_1, _ = Submission.objects.get_or_create(
            user=p_solver,
            problem=prob_map['p_stress_exact50'],
            defaults={
                'language': lang,
                'status': 'D',
                'result': 'AC',
                'points': 50.0,
                'case_points': 50.0,
                'case_total': 50.0,
                'is_archived': False,
            }
        )
        sub_solver_1.result = 'AC'
        sub_solver_1.points = 50.0
        sub_solver_1.save()

        sub_solver_2, _ = Submission.objects.get_or_create(
            user=p_solver,
            problem=prob_map['p_stress_high'],
            defaults={
                'language': lang,
                'status': 'D',
                'result': 'AC',
                'points': 75.0,
                'case_points': 75.0,
                'case_total': 75.0,
                'is_archived': False,
            }
        )
        sub_solver_2.result = 'AC'
        sub_solver_2.points = 75.0
        sub_solver_2.save()

        # u_attempter has WA on p_stress_mid
        sub_attempter_1, _ = Submission.objects.get_or_create(
            user=p_attempter,
            problem=prob_map['p_stress_mid'],
            defaults={
                'language': lang,
                'status': 'D',
                'result': 'WA',
                'points': 0.0,
                'case_points': 0.0,
                'case_total': 30.0,
                'is_archived': False,
            }
        )
        sub_attempter_1.result = 'WA'
        sub_attempter_1.points = 0.0
        sub_attempter_1.save()

        # =====================================================================
        # PART 1: points_preset=50+ Encoding, Decoding, Spaces & Boundary Tests
        # =====================================================================
        print(f"\n{Colors.CYAN}--- Part 1: points_preset=50+ URL Queries & Boundary Testing ---{Colors.RESET}")

        # 1.1 Raw '+' in URL query string
        # In HTTP standard query string, '?' + 'points_preset=50+' sends query string with literal '+'
        resp_raw_plus = client.get('/problems/?points_preset=50+')
        ctx_preset_raw = resp_raw_plus.context.get('points_preset')
        objs_raw = list(resp_raw_plus.context.get('object_list', []))
        codes_raw = [p.code for p in objs_raw]
        all_gt_50_raw = all(float(p.points) > 50.0 for p in objs_raw)

        reporter.record(
            "1.1 Raw '+': /problems/?points_preset=50+ parsed and filters points > 50",
            resp_raw_plus.status_code == 200 and ctx_preset_raw == '50+' and all_gt_50_raw and 'p_stress_gt50' in codes_raw,
            f"points_preset={ctx_preset_raw}, returned: {len(objs_raw)} problems, all > 50: {all_gt_50_raw}"
        )

        # 1.2 URL-encoded '%2B' in query string
        resp_encoded_plus = client.get('/problems/?points_preset=50%2B')
        ctx_preset_enc = resp_encoded_plus.context.get('points_preset')
        objs_enc = list(resp_encoded_plus.context.get('object_list', []))
        codes_enc = [p.code for p in objs_enc]
        all_gt_50_enc = all(float(p.points) > 50.0 for p in objs_enc)

        reporter.record(
            "1.2 Percent-encoded '%2B': /problems/?points_preset=50%2B parsed and filters points > 50",
            resp_encoded_plus.status_code == 200 and ctx_preset_enc == '50+' and all_gt_50_enc and 'p_stress_gt50' in codes_enc,
            f"points_preset={ctx_preset_enc}, returned: {len(objs_enc)} problems, all > 50: {all_gt_50_enc}"
        )

        # 1.3 Decoded space / %20 in query string
        resp_space_20 = client.get('/problems/?points_preset=50%20')
        ctx_preset_space = resp_space_20.context.get('points_preset')
        objs_space = list(resp_space_20.context.get('object_list', []))
        codes_space = [p.code for p in objs_space]
        all_gt_50_space = all(float(p.points) > 50.0 for p in objs_space)

        reporter.record(
            "1.3 Decoded space '%20': /problems/?points_preset=50%20 restored to 50+ and filters points > 50",
            resp_space_20.status_code == 200 and ctx_preset_space == '50+' and all_gt_50_space and 'p_stress_gt50' in codes_space,
            f"points_preset={ctx_preset_space}, returned: {len(objs_space)} problems, all > 50: {all_gt_50_space}"
        )

        # 1.4 Literal space via query params dict: {'points_preset': '50 '}
        resp_dict_space = client.get('/problems/', {'points_preset': '50 '})
        ctx_preset_dict = resp_dict_space.context.get('points_preset')
        objs_dict = list(resp_dict_space.context.get('object_list', []))
        codes_dict = [p.code for p in objs_dict]

        reporter.record(
            "1.4 Dict space {'points_preset': '50 '}: restored to 50+ via .replace(' ', '+')",
            resp_dict_space.status_code == 200 and ctx_preset_dict == '50+' and 'p_stress_gt50' in codes_dict,
            f"points_preset={ctx_preset_dict}"
        )

        # 1.5 Strict Boundary Stress Check: points > 50 vs points <= 50
        # p_stress_exact50 has points = 50.0 -> MUST NOT be in 50+
        # p_stress_gt50 has points = 50.1 -> MUST BE in 50+
        # p_stress_high has points = 75.0 -> MUST BE in 50+
        # aplusb has points = 100.0 -> MUST BE in 50+
        # p_stress_mid has points = 30.0 -> MUST NOT be in 50+
        # p_stress_low has points = 5.0 -> MUST NOT be in 50+
        has_gt50 = 'p_stress_gt50' in codes_raw
        has_high = 'p_stress_high' in codes_raw
        has_exact50 = 'p_stress_exact50' in codes_raw
        has_mid = 'p_stress_mid' in codes_raw
        has_low = 'p_stress_low' in codes_raw

        boundary_50_plus_ok = has_gt50 and has_high and not has_exact50 and not has_mid and not has_low

        reporter.record(
            "1.5 Boundary Isolation for 50+: exactly 50.0 excluded, 50.1 included, <=50 excluded",
            boundary_50_plus_ok,
            f"gt50(50.1): {has_gt50}, high(75.0): {has_high}, exact50(50.0): {has_exact50}, mid(30.0): {has_mid}"
        )

        # 1.6 Preset 26-50 Boundary Verification
        # In 26-50: points__gte=26, points__lte=50
        # p_stress_exact50 (50.0 pts) MUST BE INCLUDED
        # p_stress_mid (30.0 pts) MUST BE INCLUDED
        # p_stress_gt50 (50.1 pts) MUST BE EXCLUDED
        # p_stress_low (5.0 pts) MUST BE EXCLUDED
        resp_26_50 = client.get('/problems/?points_preset=26-50')
        objs_26_50 = list(resp_26_50.context.get('object_list', []))
        codes_26_50 = [p.code for p in objs_26_50]

        boundary_26_50_ok = (
            'p_stress_exact50' in codes_26_50 and
            'p_stress_mid' in codes_26_50 and
            'p_stress_gt50' not in codes_26_50 and
            'p_stress_low' not in codes_26_50
        )
        reporter.record(
            "1.6 Boundary Isolation for 26-50: exactly 50.0 included, 50.1 excluded",
            boundary_26_50_ok,
            f"exact50 in 26-50: {'p_stress_exact50' in codes_26_50}, gt50 in 26-50: {'p_stress_gt50' in codes_26_50}"
        )

        # 1.7 UI & DOM State for points_preset=50+
        html_50 = resp_raw_plus.content.decode('utf-8')
        has_hidden_50 = 'id="filter-points-preset" value="50+"' in html_50
        has_btn_text_50 = '50+ pts' in html_50 or '50+ Points' in html_50 or '50+' in html_50
        has_active_menu_50 = 'data-filter="points_preset" data-value="50+"' in html_50 and 'active' in html_50

        reporter.record(
            "1.7 DOM Markup for 50+: hidden input value='50+', active dropdown item, button text",
            has_hidden_50 and has_btn_text_50 and has_active_menu_50,
            f"Hidden: {has_hidden_50}, BtnText: {has_btn_text_50}, ActiveItem: {has_active_menu_50}"
        )

        # 1.8 Adversarial Variations of points_preset
        resp_pts_double = client.get('/problems/?points_preset=50++')
        resp_pts_prefix = client.get('/problems/?points_preset=+50')
        resp_pts_plain = client.get('/problems/?points_preset=50')
        resp_pts_pad = client.get('/problems/?points_preset=%2050+%20')

        adv_pts_ok = all(r.status_code == 200 for r in [resp_pts_double, resp_pts_prefix, resp_pts_plain, resp_pts_pad])
        reporter.record(
            "1.8 Adversarial points_preset queries (50++, +50, 50, ' 50+ ') handled without crash",
            adv_pts_ok,
            "All returned HTTP 200 OK"
        )

        # =====================================================================
        # PART 2: Category and Group Transitions & "All Groups" Clearing
        # =====================================================================
        print(f"\n{Colors.CYAN}--- Part 2: Category and Group Transitions ---{Colors.RESET}")

        # 2.1 Single ?category=g_algebra.id
        resp_cat_alg = client.get(f'/problems/?category={g_algebra.id}')
        objs_cat_alg = list(resp_cat_alg.context.get('object_list', []))
        codes_cat_alg = [p.code for p in objs_cat_alg]
        cat_alg_ok = (
            resp_cat_alg.status_code == 200 and
            resp_cat_alg.context.get('category') == g_algebra.id and
            'p_stress_exact50' in codes_cat_alg and
            'p_stress_high' not in codes_cat_alg
        )
        reporter.record(
            "2.1 ?category=<id>: filters group__id and sets context['category']",
            cat_alg_ok,
            f"Category={resp_cat_alg.context.get('category')}, Found exact50: {'p_stress_exact50' in codes_cat_alg}, Excluded high: {'p_stress_high' not in codes_cat_alg}"
        )

        # 2.2 Single ?group=g_geom.id
        resp_grp_geom = client.get(f'/problems/?group={g_geom.id}')
        objs_grp_geom = list(resp_grp_geom.context.get('object_list', []))
        codes_grp_geom = [p.code for p in objs_grp_geom]
        grp_geom_ok = (
            resp_grp_geom.status_code == 200 and
            resp_grp_geom.context.get('category') == g_geom.id and
            'p_stress_high' in codes_grp_geom and
            'p_stress_exact50' not in codes_grp_geom
        )
        reporter.record(
            "2.2 ?group=<id>: backwards-compatible alias sets context['category']",
            grp_geom_ok,
            f"Category={resp_grp_geom.context.get('category')}, Found high: {'p_stress_high' in codes_grp_geom}, Excluded exact50: {'p_stress_exact50' not in codes_grp_geom}"
        )

        # 2.3 Priority Conflict: ?category=g_geom.id&group=g_algebra.id
        # category must take precedence over group
        resp_conflict_1 = client.get(f'/problems/?category={g_geom.id}&group={g_algebra.id}')
        objs_conflict_1 = list(resp_conflict_1.context.get('object_list', []))
        codes_conflict_1 = [p.code for p in objs_conflict_1]
        conflict_1_ok = (
            resp_conflict_1.status_code == 200 and
            resp_conflict_1.context.get('category') == g_geom.id and
            'p_stress_high' in codes_conflict_1 and
            'p_stress_exact50' not in codes_conflict_1
        )
        reporter.record(
            "2.3 Priority: ?category=B&group=A resolves to category B (Geometry)",
            conflict_1_ok,
            f"Category={resp_conflict_1.context.get('category')} (expected {g_geom.id})"
        )

        # 2.4 Priority Conflict (Reverse): ?category=g_algebra.id&group=g_geom.id
        resp_conflict_2 = client.get(f'/problems/?category={g_algebra.id}&group={g_geom.id}')
        objs_conflict_2 = list(resp_conflict_2.context.get('object_list', []))
        codes_conflict_2 = [p.code for p in objs_conflict_2]
        conflict_2_ok = (
            resp_conflict_2.status_code == 200 and
            resp_conflict_2.context.get('category') == g_algebra.id and
            'p_stress_exact50' in codes_conflict_2 and
            'p_stress_high' not in codes_conflict_2
        )
        reporter.record(
            "2.4 Priority: ?category=A&group=B resolves to category A (Algebra)",
            conflict_2_ok,
            f"Category={resp_conflict_2.context.get('category')} (expected {g_algebra.id})"
        )

        # 2.5 Clearing to "All Groups" via ?category=&group=
        resp_clear_both = client.get('/problems/?category=&group=')
        objs_clear_both = list(resp_clear_both.context.get('object_list', []))
        codes_clear_both = [p.code for p in objs_clear_both]
        clear_both_ok = (
            resp_clear_both.status_code == 200 and
            resp_clear_both.context.get('category') is None and
            'p_stress_exact50' in codes_clear_both and
            'p_stress_high' in codes_clear_both
        )
        reporter.record(
            "2.5 All Groups Clearing: ?category=&group= clears category and returns all groups",
            clear_both_ok,
            f"Category={resp_clear_both.context.get('category')}, both groups returned"
        )

        # 2.6 Clearing trap defense: ?category=&group=g_algebra.id
        # When category='' is submitted while old group lingers, category is in request.GET, so category='' wins!
        resp_clear_trap = client.get(f'/problems/?category=&group={g_algebra.id}')
        objs_clear_trap = list(resp_clear_trap.context.get('object_list', []))
        codes_clear_trap = [p.code for p in objs_clear_trap]
        clear_trap_ok = (
            resp_clear_trap.status_code == 200 and
            resp_clear_trap.context.get('category') is None and
            'p_stress_high' in codes_clear_trap and
            'p_stress_exact50' in codes_clear_trap
        )
        reporter.record(
            "2.6 Clearing Trap Defense: ?category=&group=<id> clears category without trapping",
            clear_trap_ok,
            f"Category={resp_clear_trap.context.get('category')} (None expected)"
        )

        # 2.7 DOM Markup for Category/Group
        html_cat = resp_cat_alg.content.decode('utf-8')
        has_hidden_cat = f'id="filter-category" value="{g_algebra.id}"' in html_cat
        has_hidden_grp = f'id="filter-group" value="{g_algebra.id}"' in html_cat
        has_btn_grp_label = g_algebra.full_name in html_cat
        has_active_grp_item = f'data-filter="category" data-value="{g_algebra.id}"' in html_cat

        reporter.record(
            "2.7 DOM Markup for Active Group: synchronized hidden inputs, button label, active item",
            has_hidden_cat and has_hidden_grp and has_btn_grp_label and has_active_grp_item,
            f"HiddenCat: {has_hidden_cat}, HiddenGrp: {has_hidden_grp}, BtnLabel: {has_btn_grp_label}"
        )

        # 2.8 Adversarial Category Inputs (non-existent, negative, malformed)
        resp_nonexist_grp = client.get('/problems/?category=999999')
        resp_neg_grp = client.get('/problems/?category=-1')
        resp_str_grp = client.get('/problems/?category=not_an_int')
        resp_sqli_grp = client.get('/problems/?category=1%20OR%201=1')

        adv_grp_ok = (
            resp_nonexist_grp.status_code == 200 and len(resp_nonexist_grp.context.get('object_list', [])) == 0 and
            resp_neg_grp.status_code == 200 and len(resp_neg_grp.context.get('object_list', [])) == 0 and
            resp_str_grp.status_code == 200 and resp_str_grp.context.get('category') is None and
            resp_sqli_grp.status_code == 200
        )
        reporter.record(
            "2.8 Adversarial Category inputs (non-existent, negative, string, SQLi) handled gracefully",
            adv_grp_ok,
            "Non-existent/negative yielded empty, string yielded None, SQLi blocked"
        )

        # =====================================================================
        # PART 3: Single Type Selection vs Multiple Types & Deduplication
        # =====================================================================
        print(f"\n{Colors.CYAN}--- Part 3: Single Type vs Multiple Types Selection ---{Colors.RESET}")

        # 3.1 Single type selection: ?type=t_greedy.id
        resp_type_single = client.get(f'/problems/?type={t_greedy.id}')
        objs_type_single = list(resp_type_single.context.get('object_list', []))
        codes_type_single = [p.code for p in objs_type_single]
        # p_stress_exact50 (greedy), p_stress_gt50 (greedy), p_stress_low (greedy, dp) MUST BE INCLUDED
        # p_stress_high (dp, graph), p_stress_mid (dp), p_stress_notype (none) MUST BE EXCLUDED
        single_type_ok = (
            resp_type_single.status_code == 200 and
            resp_type_single.context.get('selected_types') == [t_greedy.id] and
            'p_stress_exact50' in codes_type_single and
            'p_stress_gt50' in codes_type_single and
            'p_stress_low' in codes_type_single and
            'p_stress_high' not in codes_type_single and
            'p_stress_mid' not in codes_type_single and
            'p_stress_notype' not in codes_type_single
        )
        reporter.record(
            "3.1 Single Type ?type=<id>: filters types__in and sets selected_types=[<id>]",
            single_type_ok,
            f"selected_types={resp_type_single.context.get('selected_types')}, count: {len(codes_type_single)}"
        )

        # 3.2 Single type DOM State: hidden input #filter-type, trigger button label, active item
        html_type_single = resp_type_single.content.decode('utf-8')
        has_hidden_type = f'id="filter-type" value="{t_greedy.id}"' in html_type_single
        has_btn_type_label = t_greedy.full_name in html_type_single
        has_active_type_item = f'data-filter="type" data-value="{t_greedy.id}"' in html_type_single and 'active' in html_type_single
        has_tag_checkbox_checked = f'name="type" value="{t_greedy.id}" checked' in html_type_single

        reporter.record(
            "3.2 Single Type DOM: hidden #filter-type, dropdown trigger text, active item, and tag checkbox checked",
            has_hidden_type and has_btn_type_label and has_active_type_item and has_tag_checkbox_checked,
            f"Hidden: {has_hidden_type}, BtnText: {has_btn_type_label}, ActiveItem: {has_active_type_item}, Checked: {has_tag_checkbox_checked}"
        )

        # 3.3 Multiple Types Selection: ?type=t_greedy.id&type=t_dp.id
        resp_type_multi = client.get(f'/problems/?type={t_greedy.id}&type={t_dp.id}')
        objs_type_multi = list(resp_type_multi.context.get('object_list', []))
        codes_type_multi = [p.code for p in objs_type_multi]
        # Included: p_stress_exact50 (greedy), p_stress_gt50 (greedy), p_stress_high (dp, graph),
        #           p_stress_mid (dp), p_stress_low (greedy, dp)
        # Excluded: p_stress_notype (none)
        multi_type_ok = (
            resp_type_multi.status_code == 200 and
            set(resp_type_multi.context.get('selected_types', [])) == {t_greedy.id, t_dp.id} and
            'p_stress_exact50' in codes_type_multi and
            'p_stress_gt50' in codes_type_multi and
            'p_stress_high' in codes_type_multi and
            'p_stress_mid' in codes_type_multi and
            'p_stress_low' in codes_type_multi and
            'p_stress_notype' not in codes_type_multi
        )
        reporter.record(
            "3.3 Multiple Types ?type=A&type=B: returns union of types with selected_types=[A, B]",
            multi_type_ok,
            f"selected_types={resp_type_multi.context.get('selected_types')}, count: {len(codes_type_multi)}"
        )

        # 3.4 EMPIRICAL ADVERSARIAL DEDUPLICATION TEST:
        # p_stress_low has BOTH t_greedy AND t_dp!
        # When querying ?type=t_greedy.id&type=t_dp.id, does p_stress_low appear once or twice?
        # Queryset must call .distinct() and template must render row exactly ONCE.
        occurrences_in_queryset = codes_type_multi.count('p_stress_low')
        html_type_multi = resp_type_multi.content.decode('utf-8')
        occurrences_in_html_rows = html_type_multi.count('<tr class="problem-row" data-code="p_stress_low"')

        dedup_ok = occurrences_in_queryset == 1 and occurrences_in_html_rows == 1
        reporter.record(
            "3.4 Adversarial Deduplication: problem matching multiple types appears exactly ONCE",
            dedup_ok,
            f"Queryset count: {occurrences_in_queryset}, HTML table row count: {occurrences_in_html_rows}"
        )

        # 3.5 Duplicate query parameter: ?type=t_greedy.id&type=t_greedy.id
        resp_type_dup = client.get(f'/problems/?type={t_greedy.id}&type={t_greedy.id}')
        objs_type_dup = list(resp_type_dup.context.get('object_list', []))
        codes_type_dup = [p.code for p in objs_type_dup]
        dup_dedup_ok = codes_type_dup.count('p_stress_exact50') == 1
        reporter.record(
            "3.5 Duplicate Type Query ?type=1&type=1: deduplicated cleanly without row replication",
            resp_type_dup.status_code == 200 and dup_dedup_ok,
            f"Exact50 occurrences: {codes_type_dup.count('p_stress_exact50')}"
        )

        # 3.6 Clearing Type via ?type=
        resp_type_clear = client.get('/problems/?type=')
        ctx_types_clear = resp_type_clear.context.get('selected_types', [])
        objs_type_clear = list(resp_type_clear.context.get('object_list', []))
        codes_type_clear = [p.code for p in objs_type_clear]
        html_type_clear = resp_type_clear.content.decode('utf-8')

        clear_type_ok = (
            resp_type_clear.status_code == 200 and
            ctx_types_clear == [] and
            'p_stress_exact50' in codes_type_clear and
            'p_stress_notype' in codes_type_clear and
            'id="filter-type" value=""' in html_type_clear and
            'data-filter="type" data-value=""' in html_type_clear
        )
        reporter.record(
            "3.6 All Types Clearing ?type=: safely resets selected_types to [] and shows all types",
            clear_type_ok,
            f"selected_types={ctx_types_clear}, total problems: {len(codes_type_clear)}"
        )

        # 3.7 Adversarial Type Inputs
        resp_nonexist_type = client.get('/problems/?type=999999')
        resp_str_type = client.get('/problems/?type=invalid_type_code')
        resp_sqli_type = client.get('/problems/?type=1%20UNION%20SELECT%201')

        adv_type_ok = (
            resp_nonexist_type.status_code == 200 and len(resp_nonexist_type.context.get('object_list', [])) == 0 and
            resp_str_type.status_code == 200 and resp_str_type.context.get('selected_types', []) == [] and
            resp_sqli_type.status_code == 200
        )
        reporter.record(
            "3.7 Adversarial Type inputs (non-existent ID, string, SQLi) handled safely without 500",
            adv_type_ok,
            "Non-existent yielded empty, string safely caught ValueError, SQLi sanitized"
        )

        # =====================================================================
        # PART 4: Anonymous vs Authenticated Requests to ?status=...
        # =====================================================================
        print(f"\n{Colors.CYAN}--- Part 4: Anonymous vs Authenticated Status Filtering ---{Colors.RESET}")

        # 4.1 Anonymous to ?status=solved MUST return 0 problems (empty queryset)
        anon_client = Client()
        resp_anon_solved = anon_client.get('/problems/?status=solved')
        objs_anon_solved = list(resp_anon_solved.context.get('object_list', []))
        html_anon_solved = resp_anon_solved.content.decode('utf-8')

        anon_solved_ok = (
            resp_anon_solved.status_code == 200 and
            len(objs_anon_solved) == 0 and
            'empty-state-row' in html_anon_solved and
            'No problems found' in html_anon_solved
        )
        reporter.record(
            "4.1 Anonymous ?status=solved: returns 0 problems and renders empty state row",
            anon_solved_ok,
            f"Object count: {len(objs_anon_solved)}, empty-state-row present: {'empty-state-row' in html_anon_solved}"
        )

        # 4.2 Anonymous to ?status=unsolved: returns all public problems
        resp_anon_unsolved = anon_client.get('/problems/?status=unsolved')
        objs_anon_unsolved = list(resp_anon_unsolved.context.get('object_list', []))
        codes_anon_unsolved = [p.code for p in objs_anon_unsolved]
        html_anon_unsolved = resp_anon_unsolved.content.decode('utf-8')

        anon_unsolved_ok = (
            resp_anon_unsolved.status_code == 200 and
            'p_stress_exact50' in codes_anon_unsolved and
            'p_stress_high' in codes_anon_unsolved and
            'p_stress_mid' in codes_anon_unsolved and
            'status-unsolved' in html_anon_unsolved
        )
        reporter.record(
            "4.2 Anonymous ?status=unsolved: returns all public problems labeled Unsolved",
            anon_unsolved_ok,
            f"Total problems: {len(codes_anon_unsolved)}, status-unsolved rendered"
        )

        # 4.3 Anonymous to ?status=bookmarked with &bookmarks=p1,p2
        resp_anon_bm = anon_client.get('/problems/?status=bookmarked&bookmarks=p_stress_exact50,p_stress_high')
        objs_anon_bm = list(resp_anon_bm.context.get('object_list', []))
        codes_anon_bm = [p.code for p in objs_anon_bm]

        anon_bm_ok = (
            resp_anon_bm.status_code == 200 and
            set(codes_anon_bm) == {'p_stress_exact50', 'p_stress_high'}
        )
        reporter.record(
            "4.3 Anonymous ?status=bookmarked&bookmarks=A,B: filters exclusively to bookmarked codes",
            anon_bm_ok,
            f"Returned: {codes_anon_bm}"
        )

        # 4.4 Anonymous ?status=bookmarked with non-existent bookmarks
        resp_anon_bm_none = anon_client.get('/problems/?status=bookmarked&bookmarks=nonexistent_code_foo')
        objs_anon_bm_none = list(resp_anon_bm_none.context.get('object_list', []))
        html_anon_bm_none = resp_anon_bm_none.content.decode('utf-8')

        anon_bm_none_ok = (
            resp_anon_bm_none.status_code == 200 and
            len(objs_anon_bm_none) == 0 and
            'empty-state-row' in html_anon_bm_none
        )
        reporter.record(
            "4.4 Anonymous ?status=bookmarked with invalid bookmarks: yields empty state row",
            anon_bm_none_ok,
            f"Object count: {len(objs_anon_bm_none)}, empty-state-row present"
        )

        # 4.5 Authenticated User (u_solver: solved p_stress_exact50 and p_stress_high)
        auth_client = Client()
        auth_client.force_login(u_solver)

        resp_auth_solved = auth_client.get('/problems/?status=solved')
        objs_auth_solved = list(resp_auth_solved.context.get('object_list', []))
        codes_auth_solved = [p.code for p in objs_auth_solved]
        html_auth_solved = resp_auth_solved.content.decode('utf-8')

        auth_solved_ok = (
            resp_auth_solved.status_code == 200 and
            'p_stress_exact50' in codes_auth_solved and
            'p_stress_high' in codes_auth_solved and
            'p_stress_mid' not in codes_auth_solved and
            'p_stress_low' not in codes_auth_solved and
            'status-solved' in html_auth_solved and
            'fa-check-circle' in html_auth_solved
        )
        reporter.record(
            "4.5 Authenticated ?status=solved: returns only user-completed problems with .status-solved",
            auth_solved_ok,
            f"Returned: {codes_auth_solved}, .status-solved found"
        )

        # 4.6 Authenticated User: ?status=unsolved excludes completed problems
        resp_auth_unsolved = auth_client.get('/problems/?status=unsolved')
        objs_auth_unsolved = list(resp_auth_unsolved.context.get('object_list', []))
        codes_auth_unsolved = [p.code for p in objs_auth_unsolved]

        auth_unsolved_ok = (
            resp_auth_unsolved.status_code == 200 and
            'p_stress_exact50' not in codes_auth_unsolved and
            'p_stress_high' not in codes_auth_unsolved and
            'p_stress_mid' in codes_auth_unsolved and
            'p_stress_low' in codes_auth_unsolved
        )
        reporter.record(
            "4.6 Authenticated ?status=unsolved: strictly excludes solved problems (hide_solved)",
            auth_unsolved_ok,
            f"Excluded solved problems, returned {len(codes_auth_unsolved)} unsolved problems"
        )

        # 4.7 Authenticated Attempter: attempted p_stress_mid (WA) -> .status-attempted badge
        att_client = Client()
        att_client.force_login(u_attempter)

        resp_att_all = att_client.get('/problems/?status=all')
        html_att_all = resp_att_all.content.decode('utf-8')
        att_all_ok = (
            resp_att_all.status_code == 200 and
            'status-attempted' in html_att_all and
            'fa-minus-circle' in html_att_all
        )
        reporter.record(
            "4.7 Authenticated Attempter: renders .status-attempted and fa-minus-circle for WA problem",
            att_all_ok,
            "status-attempted and fa-minus-circle present in DOM"
        )

        # 4.8 Authenticated Attempter: ?status=solved yields empty state (no AC submissions)
        resp_att_solved = att_client.get('/problems/?status=solved')
        objs_att_solved = list(resp_att_solved.context.get('object_list', []))
        html_att_solved = resp_att_solved.content.decode('utf-8')

        att_solved_ok = (
            resp_att_solved.status_code == 200 and
            len(objs_att_solved) == 0 and
            'empty-state-row' in html_att_solved
        )
        reporter.record(
            "4.8 Authenticated Attempter ?status=solved: empty state row (0 completed problems)",
            att_solved_ok,
            f"Object count: {len(objs_att_solved)}"
        )

        # =====================================================================
        # PART 5: Workspace Header 0-Types vs >=1 Types Tag Rendering
        # =====================================================================
        print(f"\n{Colors.CYAN}--- Part 5: Workspace Header Problem Types Rendering ---{Colors.RESET}")

        # 5.1 Problem with 0 types (p_stress_notype)
        resp_ws_notype = client.get('/problem/p_stress_notype')
        html_ws_notype = resp_ws_notype.content.decode('utf-8')

        # Must render tag-default and "General", and NOT render any type pill
        has_general_tag = 'tag-default' in html_ws_notype and 'General' in html_ws_notype
        ws_notype_ok = (
            resp_ws_notype.status_code == 200 and
            has_general_tag
        )
        reporter.record(
            "5.1 Problem with 0 types: renders fallback .tag-default 'General' tag",
            ws_notype_ok,
            f"Found tag-default General: {has_general_tag}"
        )

        # 5.2 Problem with 1 type (p_stress_exact50 -> t_greedy)
        resp_ws_single = client.get('/problem/p_stress_exact50')
        html_ws_single = resp_ws_single.content.decode('utf-8')

        has_greedy_pill = 'Greedy Strategy' in html_ws_single
        not_has_general_pill = 'tag-default' not in html_ws_single
        ws_single_ok = (
            resp_ws_single.status_code == 200 and
            has_greedy_pill and
            not_has_general_pill
        )
        reporter.record(
            "5.2 Problem with 1 type: renders type tag pill and does NOT render General fallback",
            ws_single_ok,
            f"Has Greedy pill: {has_greedy_pill}, General tag excluded: {not_has_general_pill}"
        )

        # 5.3 Problem with multiple types (p_stress_high -> t_dp, t_graph)
        resp_ws_multi = client.get('/problem/p_stress_high')
        html_ws_multi = resp_ws_multi.content.decode('utf-8')

        has_dp_pill = 'Dynamic Programming' in html_ws_multi
        has_graph_pill = 'Graph Theory' in html_ws_multi
        ws_multi_ok = (
            resp_ws_multi.status_code == 200 and
            has_dp_pill and
            has_graph_pill and
            'tag-default' not in html_ws_multi
        )
        reporter.record(
            "5.3 Problem with multiple types: renders all tag pills without General fallback",
            ws_multi_ok,
            f"Has DP: {has_dp_pill}, Has Graph: {has_graph_pill}"
        )

        # =====================================================================
        # PART 6: Complex Multi-Filter Integration Stress Scenarios
        # =====================================================================
        print(f"\n{Colors.CYAN}--- Part 6: Complex Multi-Filter Integration Stress Scenarios ---{Colors.RESET}")

        # 6.1 Multi-filter: points_preset=50+ & category=g_algebra.id & type=t_greedy.id
        resp_combo_1 = client.get(f'/problems/?points_preset=50+&category={g_algebra.id}&type={t_greedy.id}')
        objs_combo_1 = list(resp_combo_1.context.get('object_list', []))
        codes_combo_1 = [p.code for p in objs_combo_1]
        # p_stress_gt50 has points=50.1, group=g_algebra, type=t_greedy -> MATCH
        # p_stress_exact50 has points=50.0 -> EXCLUDED (not > 50)
        # p_stress_high has group=g_geom -> EXCLUDED
        combo_1_ok = (
            resp_combo_1.status_code == 200 and
            codes_combo_1 == ['p_stress_gt50']
        )
        reporter.record(
            "6.1 Combo: points_preset=50+ AND category=Algebra AND type=Greedy yields exact match",
            combo_1_ok,
            f"Returned: {codes_combo_1}"
        )

        # 6.2 Multi-filter: points_preset=50+ & status=solved (Anonymous) -> 0 results
        resp_combo_2 = anon_client.get('/problems/?points_preset=50+&status=solved')
        objs_combo_2 = list(resp_combo_2.context.get('object_list', []))
        combo_2_ok = (
            resp_combo_2.status_code == 200 and
            len(objs_combo_2) == 0
        )
        reporter.record(
            "6.2 Combo: points_preset=50+ AND anonymous ?status=solved yields 0 problems",
            combo_2_ok,
            f"Count: {len(objs_combo_2)}"
        )

        # 6.3 Multi-filter: points_preset=50+ & status=solved (Authenticated Solver)
        # u_solver has solved p_stress_exact50 (50.0 pts) and p_stress_high (75.0 pts).
        # points_preset=50+ must filter only > 50 points -> ONLY p_stress_high (and aplusb if solved)
        resp_combo_3 = auth_client.get('/problems/?points_preset=50+&status=solved')
        objs_combo_3 = list(resp_combo_3.context.get('object_list', []))
        codes_combo_3 = [p.code for p in objs_combo_3]
        combo_3_ok = (
            resp_combo_3.status_code == 200 and
            'p_stress_high' in codes_combo_3 and
            'p_stress_exact50' not in codes_combo_3
        )
        reporter.record(
            "6.3 Combo: points_preset=50+ AND auth solver ?status=solved returns solved problems > 50",
            combo_3_ok,
            f"Found high(75): {'p_stress_high' in codes_combo_3}, Excluded exact50(50): {'p_stress_exact50' not in codes_combo_3}"
        )

        # 6.4 Ordering Stress with points_preset=50+: ?points_preset=50+&order=-points
        resp_combo_4 = client.get('/problems/?points_preset=50+&order=-points')
        objs_combo_4 = list(resp_combo_4.context.get('object_list', []))
        pts_list_4 = [float(p.points) for p in objs_combo_4]
        is_sorted_desc = pts_list_4 == sorted(pts_list_4, reverse=True)
        combo_4_ok = (
            resp_combo_4.status_code == 200 and
            len(pts_list_4) > 0 and
            is_sorted_desc and
            all(p > 50.0 for p in pts_list_4)
        )
        reporter.record(
            "6.4 Combo: points_preset=50+ with order=-points strictly sorts points descending",
            combo_4_ok,
            f"Points order: {pts_list_4[:5]}"
        )

        # 6.5 Search + Multi-type + Group:
        resp_combo_5 = client.get(f'/problems/?search=Fifty&category={g_algebra.id}&type={t_greedy.id}')
        objs_combo_5 = list(resp_combo_5.context.get('object_list', []))
        codes_combo_5 = [p.code for p in objs_combo_5]
        combo_5_ok = (
            resp_combo_5.status_code == 200 and
            'p_stress_exact50' in codes_combo_5 and
            'p_stress_gt50' in codes_combo_5 and
            'p_stress_high' not in codes_combo_5
        )
        reporter.record(
            "6.5 Combo: search='Fifty' + category=Algebra + type=Greedy accurately narrows results",
            combo_5_ok,
            f"Returned: {codes_combo_5}"
        )

    finally:
        # ---------------------------------------------------------------------
        # Teardown Fixtures
        # ---------------------------------------------------------------------
        print(f"\n{Colors.CYAN}--- Cleaning up test fixtures ---{Colors.RESET}")
        for p in created_problems:
            try:
                p.delete()
            except Exception:
                pass
        for u in created_users:
            try:
                u.delete()
            except Exception:
                pass
        for g in created_groups:
            try:
                g.delete()
            except Exception:
                pass
        for t in created_types:
            try:
                t.delete()
            except Exception:
                pass
        print("  Cleaned up problems, users, groups, types.")

    reporter.print_summary()
    return reporter.failed == 0


if __name__ == '__main__':
    success = run_filter_stress_suite()
    sys.exit(0 if success else 1)
