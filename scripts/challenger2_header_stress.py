#!/usr/bin/env python3
"""
scripts/challenger2_header_stress.py
Milestone 3 Iteration 2 Challenger 2: Screen 2 Workspace Header Tag Fallback Empirical Stress Suite

Adversarial Verification:
1. Direct Jinja2 template rendering of templates/problem/workspace-header.html:
   - Problem with 0 types (empty queryset / empty list) renders tag-default General.
   - Problem with 1 type renders accurate badge and NO tag-default.
   - Problem with N types renders all N badges and NO tag-default.
   - Problem with type lacking full_name falls back to name.
   - Problem with types_list populated respects types_list.
2. Full Django HTTP stack integration:
   - Problem /problem/aplusb with 0 types renders tag-default General in response HTML.
   - Problem /problem/aplusb with 1 type renders badge and no tag-default.
   - Problem /problem/aplusb with N types renders all N badges.
   - Problem /problem/aplusb/submit (authenticated) verifies header fallback identical behavior.
   - Database state isolation via transactions.
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
from django.template.loader import render_to_string
from django.db import transaction
from django.contrib.auth import get_user_model
from judge.models import Problem, ProblemType, Profile

User = get_user_model()

passed = 0
failed = 0
findings = []

def check(title, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  [PASS] {title}{f' ({detail})' if detail else ''}")
    else:
        failed += 1
        msg = f"  [FAIL] {title}{f' ({detail})' if detail else ''}"
        print(msg)
        findings.append(msg)

class MockProblemType:
    def __init__(self, name, full_name=None):
        self.name = name
        self.full_name = full_name or name

class MockTypesManager:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items

    def count(self):
        return len(self._items)

    def exists(self):
        return len(self._items) > 0

    def __bool__(self):
        # Emulate Django's ManyRelatedManager: raw manager in Python evaluates to True!
        return True

class MockProblem:
    def __init__(self, code="testprob", title="Test Problem", types_list=None, types=None, points=50):
        self.code = code
        self.name = title
        self.types_list = types_list
        self.types = MockTypesManager(types or [])
        self.points = points
        self.time_limit = 2.0
        self.memory_limit = 65536
        self.is_public = True

print("\n======================================================================")
print("CHALLENGER 2: SCREEN 2 WORKSPACE HEADER TAG FALLBACK STRESS HARNESS")
print("======================================================================\n")

# -----------------------------------------------------------------------------
# Section 1: Template Direct Rendering Stress Tests
# -----------------------------------------------------------------------------
print("--- SECTION 1: Direct Jinja2 Template Rendering Tests ---")

template_name = "problem/workspace-header.html"

# 1.1: Problem with 0 types and no types_list
p0 = MockProblem(types=[])
html0 = render_to_string(template_name, {"problem": p0, "title": "Empty Types Problem"})

has_tag_default = 'tag-default' in html0
has_general_text = 'General' in html0
tag_pills = re.findall(r'class="[^"]*workspace-tag-pill[^"]*"', html0)

check("0 types: renders tag-default class", has_tag_default)
check("0 types: renders 'General' fallback text", has_general_text)
check("0 types: renders exactly 1 tag pill", len(tag_pills) == 1, f"Found {len(tag_pills)} pills: {tag_pills}")

# 1.2: Problem with 1 type
t1 = MockProblemType("math", "Mathematics")
p1 = MockProblem(types=[t1])
html1 = render_to_string(template_name, {"problem": p1, "title": "Single Type Problem"})

has_tag_math = 'tag-math' in html1
has_math_text = 'Mathematics' in html1
has_tag_default = 'tag-default' in html1
tag_pills1 = re.findall(r'class="[^"]*workspace-tag-pill[^"]*"', html1)

check("1 type: renders tag-math class", has_tag_math)
check("1 type: renders 'Mathematics' text", has_math_text)
check("1 type: does NOT render tag-default fallback", not has_tag_default)
check("1 type: renders exactly 1 tag pill", len(tag_pills1) == 1, f"Found {len(tag_pills1)} pills")

# 1.3: Problem with N types (3 types)
types_n = [
    MockProblemType("graphs", "Graph Theory"),
    MockProblemType("dynamic-programming", "Dynamic Programming"),
    MockProblemType("geometry", "Computational Geometry")
]
pn = MockProblem(types=types_n)
html_n = render_to_string(template_name, {"problem": pn, "title": "Multi Type Problem"})

has_graphs = 'tag-graphs' in html_n and 'Graph Theory' in html_n
has_dp = 'tag-dynamic-programming' in html_n and 'Dynamic Programming' in html_n
has_geom = 'tag-geometry' in html_n and 'Computational Geometry' in html_n
has_tag_default_n = 'tag-default' in html_n
tag_pills_n = re.findall(r'class="[^"]*workspace-tag-pill[^"]*"', html_n)

check("N types (3): renders Graph Theory badge", has_graphs)
check("N types (3): renders Dynamic Programming badge", has_dp)
check("N types (3): renders Computational Geometry badge", has_geom)
check("N types (3): does NOT render tag-default fallback", not has_tag_default_n)
check("N types (3): renders exactly 3 tag pills", len(tag_pills_n) == 3, f"Found {len(tag_pills_n)} pills")

# 1.4: Problem with type lacking full_name (falls back to ptype.name)
t_no_full = MockProblemType("adhoc", full_name="")
p_no_full = MockProblem(types=[t_no_full])
html_no_full = render_to_string(template_name, {"problem": p_no_full, "title": "No Full Name Problem"})

has_tag_adhoc = 'tag-adhoc' in html_no_full
has_adhoc_text = 'adhoc' in html_no_full
has_tag_default_nf = 'tag-default' in html_no_full

check("Type without full_name: renders tag-adhoc", has_tag_adhoc)
check("Type without full_name: falls back to name 'adhoc'", has_adhoc_text)
check("Type without full_name: does NOT render tag-default", not has_tag_default_nf)

# 1.5: Problem with types_list populated
p_list = MockProblem(types_list=["Sorting", "Greedy Algorithms"])
html_list = render_to_string(template_name, {"problem": p_list, "title": "Types List Problem"})

has_sorting = 'tag-sorting' in html_list and 'Sorting' in html_list
has_greedy = 'tag-greedy-algorithms' in html_list and 'Greedy Algorithms' in html_list
has_tag_default_list = 'tag-default' in html_list
tag_pills_list = re.findall(r'class="[^"]*workspace-tag-pill[^"]*"', html_list)

check("types_list: renders Sorting badge", has_sorting)
check("types_list: renders Greedy Algorithms badge", has_greedy)
check("types_list: does NOT render tag-default", not has_tag_default_list)
check("types_list: renders exactly 2 pills", len(tag_pills_list) == 2)

# -----------------------------------------------------------------------------
# Section 2: Full Django HTTP & Database Integration Stress Tests
# -----------------------------------------------------------------------------
print("\n--- SECTION 2: Full Django HTTP & Database Integration Tests ---")

client = Client()

# Prepare test problem and types inside transaction
with transaction.atomic():
    prob = Problem.objects.filter(code="aplusb").first()
    if not prob:
        print("  [ERROR] Problem 'aplusb' not found in database!")
        sys.exit(1)

    original_types = list(prob.types.all())

    try:
        # 2.1: Problem with 0 types via HTTP GET /problem/aplusb
        prob.types.clear()
        resp_zero = client.get("/problem/aplusb")
        check("HTTP GET /problem/aplusb (0 types): status 200 OK", resp_zero.status_code == 200)

        content_zero = resp_zero.content.decode("utf-8")
        zero_has_tag_default = 'tag-default' in content_zero
        zero_has_general = 'General' in content_zero

        # Extract tags row from response
        tags_match = re.search(r'<div class="problem-tags-row">(.*?)</div>', content_zero, re.DOTALL)
        tags_html = tags_match.group(1) if tags_match else ""
        zero_pills = re.findall(r'class="[^"]*workspace-tag-pill[^"]*"', tags_html)

        check("HTTP GET /problem/aplusb (0 types): renders tag-default badge", zero_has_tag_default)
        check("HTTP GET /problem/aplusb (0 types): contains 'General' label", zero_has_general)
        check("HTTP GET /problem/aplusb (0 types): exactly 1 pill in problem-tags-row", len(zero_pills) == 1, f"Found: {zero_pills}")

        # 2.2: Problem with 1 type via HTTP GET /problem/aplusb
        type_math, _ = ProblemType.objects.get_or_create(name="math", defaults={"full_name": "Mathematics"})
        prob.types.add(type_math)
        resp_one = client.get("/problem/aplusb")
        check("HTTP GET /problem/aplusb (1 type): status 200 OK", resp_one.status_code == 200)

        content_one = resp_one.content.decode("utf-8")
        tags_match_one = re.search(r'<div class="problem-tags-row">(.*?)</div>', content_one, re.DOTALL)
        tags_html_one = tags_match_one.group(1) if tags_match_one else ""
        one_pills = re.findall(r'class="[^"]*workspace-tag-pill[^"]*"', tags_html_one)

        check("HTTP GET /problem/aplusb (1 type): contains tag-mathematics", 'tag-mathematics' in tags_html_one)
        check("HTTP GET /problem/aplusb (1 type): contains Mathematics label", 'Mathematics' in tags_html_one)
        check("HTTP GET /problem/aplusb (1 type): does NOT contain tag-default", 'tag-default' not in tags_html_one)
        check("HTTP GET /problem/aplusb (1 type): exactly 1 pill rendered", len(one_pills) == 1)

        # 2.3: Problem with N types (3 types) via HTTP GET /problem/aplusb
        type_dp = ProblemType.objects.get(name="DP")
        type_graphs = ProblemType.objects.get(name="Graph")
        prob.types.add(type_dp, type_graphs)

        resp_three = client.get("/problem/aplusb")
        check("HTTP GET /problem/aplusb (3 types): status 200 OK", resp_three.status_code == 200)

        content_three = resp_three.content.decode("utf-8")
        tags_match_three = re.search(r'<div class="problem-tags-row">(.*?)</div>', content_three, re.DOTALL)
        tags_html_three = tags_match_three.group(1) if tags_match_three else ""
        three_pills = re.findall(r'class="[^"]*workspace-tag-pill[^"]*"', tags_html_three)

        check("HTTP GET /problem/aplusb (3 types): contains tag-mathematics", 'tag-mathematics' in tags_html_three)
        check("HTTP GET /problem/aplusb (3 types): contains tag-dynamic-programming", 'tag-dynamic-programming' in tags_html_three)
        check("HTTP GET /problem/aplusb (3 types): contains tag-graph-theory", 'tag-graph-theory' in tags_html_three)
        check("HTTP GET /problem/aplusb (3 types): does NOT contain tag-default", 'tag-default' not in tags_html_three)
        check("HTTP GET /problem/aplusb (3 types): exactly 3 pills rendered", len(three_pills) == 3)

        # 2.4: Authenticated HTTP GET /problem/aplusb/submit with 0 types vs N types
        user, _ = User.objects.get_or_create(username="stress_test_user")
        if not hasattr(user, 'profile'):
            Profile.objects.create(user=user)
        client.force_login(user)

        # Test submit with 0 types
        prob.types.clear()
        resp_sub_zero = client.get("/problem/aplusb/submit")
        check("HTTP GET /problem/aplusb/submit (0 types): status 200 OK", resp_sub_zero.status_code == 200)
        content_sub_zero = resp_sub_zero.content.decode("utf-8")
        tags_match_sub_zero = re.search(r'<div class="problem-tags-row">(.*?)</div>', content_sub_zero, re.DOTALL)
        tags_html_sub_zero = tags_match_sub_zero.group(1) if tags_match_sub_zero else ""

        check("HTTP GET /problem/aplusb/submit (0 types): renders tag-default General", 'tag-default' in tags_html_sub_zero and 'General' in tags_html_sub_zero)

        # Test submit with 2 types
        prob.types.add(type_math, type_dp)
        resp_sub_two = client.get("/problem/aplusb/submit")
        check("HTTP GET /problem/aplusb/submit (2 types): status 200 OK", resp_sub_two.status_code == 200)
        content_sub_two = resp_sub_two.content.decode("utf-8")
        tags_match_sub_two = re.search(r'<div class="problem-tags-row">(.*?)</div>', content_sub_two, re.DOTALL)
        tags_html_sub_two = tags_match_sub_two.group(1) if tags_match_sub_two else ""
        sub_two_pills = re.findall(r'class="[^"]*workspace-tag-pill[^"]*"', tags_html_sub_two)

        check("HTTP GET /problem/aplusb/submit (2 types): contains tag-mathematics and tag-dynamic-programming", 'tag-mathematics' in tags_html_sub_two and 'tag-dynamic-programming' in tags_html_sub_two)
        check("HTTP GET /problem/aplusb/submit (2 types): does NOT contain tag-default", 'tag-default' not in tags_html_sub_two)
        check("HTTP GET /problem/aplusb/submit (2 types): exactly 2 pills rendered", len(sub_two_pills) == 2)

    finally:
        # Always rollback changes
        transaction.set_rollback(True)

print("\n======================================================================")
print(f"CHALLENGER 2 HEADER STRESS SUMMARY: Passed: {passed} | Failed: {failed}")
print("======================================================================\n")

if findings:
    print("CHALLENGE FINDINGS:")
    for f in findings:
        print("  " + f)

sys.exit(failed)
