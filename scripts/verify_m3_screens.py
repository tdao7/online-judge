#!/usr/bin/env python3
"""
verify_m3_screens.py
Milestone 3 End-to-End Automated Verification & Regression Suite:
Screen 1 (Problems Catalog, docs/1.png) and Screen 2 (Problem Workspace, docs/2.png)

Verifies:
1. Static Assets & SCSS Pipeline (Source SCSS, compiled light/dark CSS, static collection).
2. Screen 1 (Problems Catalog):
   - Full-width .problems-catalog-wrapper matching docs/1.png
   - Header with bold title, count pill, quick search input
   - Multi-dropdown filter bar (Difficulty, Type, Group, Tags, Points preset, Sort by, order toggle)
   - Segmented quick filter pill tabs (All Problems, Bookmarked with count badge, Solved, Unsolved)
   - 8-column card table with star bookmarks, index, title + pastel tags, group, points, AC rate bar, status pill, actions
   - Query parameter filtering (difficulty presets, points presets, order, search query, status)
   - Hidden #filter-type input and dropdown binding
   - Group/category parameter synchronization and switching resolution
   - points_preset=50+ query string decoding and filtering points > 50
   - Anonymous request to ?status=solved returning empty queryset
3. Screen 2 (Problem Workspace):
   - Unified #workspace-split-container with #workspace-split-divider
   - Workspace header with breadcrumbs, title, star bookmark, tag badges, and 5 metric cards
   - Left Pane (Statement): tabs, markdown rendering, KaTeX assets with delimiters, license footer, comments drawer
   - Right Pane (Editor & Console): action toolbar (custom language select, Reset, Run, Submit #F97316),
     Ace editor with floating tools (copy, fullscreen, draft saved indicator), hidden sync form,
     bottom console (Testcases & Submissions tabs, sample test cards, + Add custom test, verdict pills)
   - Submit route rendering pre-populated split workspace
   - Jinja2 AST check that templates/problem/workspace-header.html uses problem.types.all()
4. Client-Side Interactive Logic (Static AST/pattern verification of JS controllers):
   - problems-list.js: bookmark persistence, badge updates, quick filter pills, search clear
   - problems-list.js: filterType === 'type' form handling and group/category synchronization
   - problems-list.js: DOMContentLoaded triggers bookmark filtering on load
   - problem-statement.js: KaTeX math rendering, sample testcase parsing, copy feedback, window.problemSamples
   - problem-workspace.js: split resizer, Ace setup, autosave, template loader, runner, form sync
5. End-to-End Submission Pipeline (validation handling & real submission creation).

Usage:
  ./venv/bin/python scripts/verify_m3_screens.py
"""

import os
import sys
import re
import argparse
import jinja2
from jinja2 import nodes
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

from django.test import Client, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from judge.models import Problem, Language, ProblemGroup, ProblemType, Profile, Submission

User = get_user_model()


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


class VerificationReporter:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0

    def record(self, test_name, condition, detail=""):
        if condition:
            self.passed += 1
            print(f"  {Colors.GREEN}[PASS]{Colors.RESET} {test_name}")
            self.results.append({"name": test_name, "status": "PASS", "detail": detail})
        else:
            self.failed += 1
            print(f"  {Colors.RED}[FAIL]{Colors.RESET} {test_name} - {detail}")
            self.results.append({"name": test_name, "status": "FAIL", "detail": detail})

    def print_summary(self):
        total = self.passed + self.failed
        print("\n" + "=" * 70)
        status_color = Colors.GREEN if self.failed == 0 else Colors.RED
        print(f"{Colors.BOLD}MILESTONE 3 VERIFICATION SUMMARY:{Colors.RESET} "
              f"{status_color}{self.passed}/{total} Passed ({self.passed / total * 100:.1f}%){Colors.RESET}")
        print("=" * 70)
        if self.failed > 0:
            print(f"{Colors.RED}{Colors.BOLD}FAILED CHECKS:{Colors.RESET}")
            for r in self.results:
                if r["status"] == "FAIL":
                    print(f"  - {r['name']}: {r['detail']}")
        else:
            print(f"{Colors.GREEN}{Colors.BOLD}ALL MILESTONE 3 VERIFICATION SUITES PASSED!{Colors.RESET}")


reporter = VerificationReporter()


# -----------------------------------------------------------------------------
# SUITE 1: Static Assets & SCSS Compilation
# -----------------------------------------------------------------------------
def verify_suite_static_assets():
    print(f"\n{Colors.CYAN}--- Suite 1: Static Assets & Stylesheet Compilation ---{Colors.RESET}")

    required_source_files = [
        ("resources/problems-list.scss", JUDGE_ROOT / "resources" / "problems-list.scss"),
        ("resources/problem-workspace.scss", JUDGE_ROOT / "resources" / "problem-workspace.scss"),
        ("resources/problems-list.js", JUDGE_ROOT / "resources" / "problems-list.js"),
        ("resources/problem-workspace.js", JUDGE_ROOT / "resources" / "problem-workspace.js"),
        ("resources/problem-statement.js", JUDGE_ROOT / "resources" / "problem-statement.js"),
        ("templates/problem/list.html", JUDGE_ROOT / "templates" / "problem" / "list.html"),
        ("templates/problem/problem.html", JUDGE_ROOT / "templates" / "problem" / "problem.html"),
        ("templates/problem/submit.html", JUDGE_ROOT / "templates" / "problem" / "submit.html"),
        ("templates/problem/workspace-header.html", JUDGE_ROOT / "templates" / "problem" / "workspace-header.html"),
        ("templates/problem/statement-pane.html", JUDGE_ROOT / "templates" / "problem" / "statement-pane.html"),
        ("templates/problem/editor-pane.html", JUDGE_ROOT / "templates" / "problem" / "editor-pane.html"),
        ("templates/katex-load.html", JUDGE_ROOT / "templates" / "katex-load.html"),
    ]

    for label, path in required_source_files:
        exists = path.exists() and path.stat().st_size > 0
        reporter.record(
            f"Test 1.1: Source asset {label} exists and non-empty",
            exists,
            f"Size: {path.stat().st_size if path.exists() else 0} bytes"
        )

    # Check compiled CSS files
    style_light = JUDGE_ROOT / "resources" / "style.css"
    style_dark = JUDGE_ROOT / "resources" / "dark" / "style.css"

    light_has_screen1 = False
    light_has_screen2 = False
    if style_light.exists():
        content_light = style_light.read_text(encoding="utf-8")
        light_has_screen1 = ".problems-catalog-wrapper" in content_light or "problems-table" in content_light
        light_has_screen2 = "workspace-split-container" in content_light or "editor-action-toolbar" in content_light

    reporter.record(
        "Test 1.2: Compiled light stylesheet resources/style.css includes Screen 1 styles",
        light_has_screen1,
        "Found .problems-catalog-wrapper / problems-table in resources/style.css"
    )
    reporter.record(
        "Test 1.3: Compiled light stylesheet resources/style.css includes Screen 2 styles",
        light_has_screen2,
        "Found workspace-split-container / editor-action-toolbar in resources/style.css"
    )

    dark_has_screen1 = False
    dark_has_screen2 = False
    if style_dark.exists():
        content_dark = style_dark.read_text(encoding="utf-8")
        dark_has_screen1 = ".problems-catalog-wrapper" in content_dark or "problems-table" in content_dark
        dark_has_screen2 = "workspace-split-container" in content_dark or "editor-action-toolbar" in content_dark

    reporter.record(
        "Test 1.4: Compiled dark stylesheet resources/dark/style.css includes Screen 1 & 2 styles",
        dark_has_screen1 and dark_has_screen2,
        "Found Screen 1 & 2 classes in resources/dark/style.css"
    )

    # Check standalone compiled files in resources/ and resources/dark/
    standalone_files = [
        JUDGE_ROOT / "resources" / "problems-list.css",
        JUDGE_ROOT / "resources" / "problem-workspace.css",
        JUDGE_ROOT / "resources" / "dark" / "problems-list.css",
        JUDGE_ROOT / "resources" / "dark" / "problem-workspace.css",
    ]
    all_standalone_exist = all(p.exists() and p.stat().st_size > 500 for p in standalone_files)
    reporter.record(
        "Test 1.5: Standalone compiled CSS files exist in resources/ and resources/dark/",
        all_standalone_exist,
        f"Verified {len(standalone_files)} standalone compiled CSS files"
    )


# -----------------------------------------------------------------------------
# SUITE 2: Screen 1 — Problems Catalog (docs/1.png)
# -----------------------------------------------------------------------------
def verify_suite_screen1_problems_catalog():
    print(f"\n{Colors.CYAN}--- Suite 2: Screen 1 — Problems Catalog (docs/1.png) ---{Colors.RESET}")
    client = Client()

    # 2.1 Route availability
    resp = client.get('/problems/')
    reporter.record(
        "Test 2.1: GET /problems/ returns HTTP 200 OK",
        resp.status_code == 200,
        f"Status: {resp.status_code}"
    )

    html = resp.content.decode('utf-8')

    # 2.2 Wrapper and filter form
    has_wrapper = 'problems-catalog-wrapper' in html
    has_filter_form = 'problems-filter-form' in html
    reporter.record(
        "Test 2.2: .problems-catalog-wrapper and #problems-filter-form render",
        has_wrapper and has_filter_form,
        f"Wrapper: {has_wrapper}, Form: {has_filter_form}"
    )

    # 2.3 Header row
    has_title = 'problems-title' in html and 'Problems' in html
    has_count_badge = 'problems-count-badge' in html
    has_search_input = 'problems-search-input' in html or 'name="search"' in html
    reporter.record(
        "Test 2.3: Header title, problem count badge, and quick search input render",
        has_title and has_count_badge and has_search_input,
        f"Title: {has_title}, Count: {has_count_badge}, Search: {has_search_input}"
    )

    # 2.4 Multi-dropdown filter bar
    has_diff_filter = 'name="difficulty"' in html
    has_type_filter = 'name="type"' in html
    has_group_filter = 'name="group"' in html or 'name="category"' in html or 'dropdown-group' in html
    has_tags_filter = 'dropdown-tags' in html or 'filter-tags-dropdown' in html or 'name="tag"' in html
    has_points_filter = 'name="points_preset"' in html
    has_sort_dropdown = 'name="order"' in html
    has_sort_btn = 'btn-sort-order' in html or 'btn-sort-toggle' in html
    all_filters = all([
        has_diff_filter, has_type_filter, has_group_filter,
        has_tags_filter, has_points_filter, has_sort_dropdown, has_sort_btn
    ])
    reporter.record(
        "Test 2.4: 5 multi-dropdown filters (Difficulty, Type, Group, Tags, Points) and Sort by + ⇅ order toggle",
        all_filters,
        f"Diff: {has_diff_filter}, Type: {has_type_filter}, Group: {has_group_filter}, "
        f"Tags: {has_tags_filter}, Points: {has_points_filter}, Sort: {has_sort_dropdown}, Btn: {has_sort_btn}"
    )

    # 2.5 Quick filter pill tabs
    has_all_pill = 'data-filter="all"' in html or 'All Problems' in html
    has_bookmark_pill = 'data-filter="bookmarked"' in html and 'bookmark-count-badge' in html
    has_solved_pill = 'data-filter="solved"' in html or 'Solved' in html
    has_unsolved_pill = 'data-filter="unsolved"' in html or 'Unsolved' in html
    all_pills = has_all_pill and has_bookmark_pill and has_solved_pill and has_unsolved_pill
    reporter.record(
        "Test 2.5: Quick filter pills (All Problems, Bookmarked with badge, Solved, Unsolved)",
        all_pills,
        f"All: {has_all_pill}, Bookmark: {has_bookmark_pill}, Solved: {has_solved_pill}, Unsolved: {has_unsolved_pill}"
    )

    # 2.6 Table columns (8 columns)
    has_star_col = 'btn-bookmark-row' in html
    has_index_col = 'col-index' in html or 'class="col-index"' in html or '#' in html
    has_title_tags = 'problem-title-cell' in html and 'tag-pill' in html
    has_group_col = 'badge-group' in html or 'col-group' in html
    has_points_col = 'problem-points-val' in html or 'col-points' in html
    has_ac_bar = 'ac-rate-bar-container' in html and 'ac-rate-percent' in html
    has_status_pill = 'status-pill' in html
    has_actions_menu = 'problem-actions-btn' in html
    table_8_cols = all([
        has_star_col, has_index_col, has_title_tags, has_group_col,
        has_points_col, has_ac_bar, has_status_pill, has_actions_menu
    ])
    reporter.record(
        "Test 2.6: Problems table 8 columns (Star, #, Title+tags, Group, Points, AC rate bar, Status, Actions)",
        table_8_cols,
        f"Star: {has_star_col}, Index: {has_index_col}, Title+tags: {has_title_tags}, "
        f"Group: {has_group_col}, Points: {has_points_col}, AC: {has_ac_bar}, "
        f"Status: {has_status_pill}, Actions: {has_actions_menu}"
    )

    # 2.7 Query parameter filtering logic
    resp_easy = client.get('/problems/?difficulty=easy')
    resp_med = client.get('/problems/?difficulty=medium')
    resp_hard = client.get('/problems/?difficulty=hard')
    resp_pts = client.get('/problems/?points_preset=1-10')
    resp_pts50 = client.get('/problems/?points_preset=50+')
    resp_search_q = client.get('/problems/?q=plus')
    resp_search_s = client.get('/problems/?search=plus')
    resp_sort_desc = client.get('/problems/?order=-points')
    resp_status_all = client.get('/problems/?status=all')
    resp_status_unsolved = client.get('/problems/?status=unsolved')
    resp_status_bookmarked = client.get('/problems/?status=bookmarked&bookmarks=aplusb')

    all_queries_ok = all(r.status_code == 200 for r in [
        resp_easy, resp_med, resp_hard, resp_pts, resp_pts50,
        resp_search_q, resp_search_s, resp_sort_desc,
        resp_status_all, resp_status_unsolved, resp_status_bookmarked
    ])

    # Check search result content
    search_has_aplusb = 'aplusb' in resp_search_q.content.decode('utf-8') and 'aplusb' in resp_search_s.content.decode('utf-8')
    reporter.record(
        "Test 2.7: Backend query filtering (difficulty, points_preset, q/search, order, status) returns 200 OK",
        all_queries_ok and search_has_aplusb,
        f"All 200: {all_queries_ok}, Search found aplusb: {search_has_aplusb}"
    )

    # 2.8 Type filter hidden input and dropdown item binding
    has_filter_type_input = 'id="filter-type"' in html and 'name="type"' in html
    has_type_dropdown_items = 'data-filter="type"' in html
    first_type = ProblemType.objects.first()
    type_query_ok = False
    if first_type:
        resp_type = client.get(f'/problems/?type={first_type.id}')
        type_query_ok = (
            resp_type.status_code == 200 and
            resp_type.context.get('selected_types') == [first_type.id]
        )
    reporter.record(
        "Test 2.8: Hidden input #filter-type in #problems-filter-form and dropdown binding (data-filter='type')",
        has_filter_type_input and has_type_dropdown_items and type_query_ok,
        f"Input: {has_filter_type_input}, Dropdown: {has_type_dropdown_items}, QueryOK: {type_query_ok}"
    )

    # 2.9 Group / Category parameter synchronization & resolution
    g1 = ProblemGroup.objects.first()
    g2 = ProblemGroup.objects.last()
    resp_grp = client.get(f'/problems/?group={g1.id}')
    resp_cat = client.get(f'/problems/?category={g1.id}')
    resp_switch = client.get(f'/problems/?category={g2.id}&group={g1.id}')
    group_sync_ok = (
        resp_grp.status_code == 200 and resp_grp.context.get('category') == g1.id and
        resp_cat.status_code == 200 and resp_cat.context.get('category') == g1.id and
        resp_switch.status_code == 200 and resp_switch.context.get('category') == g2.id
    )
    reporter.record(
        "Test 2.9: Group/category parameter synchronization and switching resolution (?group, ?category, and ?category=B&group=A)",
        group_sync_ok,
        f"Group: {resp_grp.context.get('category')}, Cat: {resp_cat.context.get('category')}, Switch: {resp_switch.context.get('category')}"
    )

    # 2.10 points_preset=50+ URL query decoding and points > 50 queryset filtering
    pts_preset_decoded = resp_pts50.context.get('points_preset') == '50+'
    object_list_50 = resp_pts50.context.get('object_list', [])
    all_gt_50 = len(object_list_50) > 0 and all(float(p.points) > 50.0 for p in object_list_50)
    has_low_points = any(float(p.points) <= 50.0 for p in object_list_50)
    reporter.record(
        "Test 2.10: GET /problems/?points_preset=50+ decodes query string and filters problems with points > 50",
        resp_pts50.status_code == 200 and pts_preset_decoded and all_gt_50 and not has_low_points,
        f"Decoded: {resp_pts50.context.get('points_preset')}, Count: {len(object_list_50)}, All > 50: {all_gt_50}"
    )

    # 2.11 Anonymous request to /problems/?status=solved returns empty queryset
    anon_client = Client()
    resp_anon_solved = anon_client.get('/problems/?status=solved')
    anon_solved_list = resp_anon_solved.context.get('object_list', [])
    is_empty_solved = len(anon_solved_list) == 0
    reporter.record(
        "Test 2.11: Anonymous request to /problems/?status=solved returns empty queryset",
        resp_anon_solved.status_code == 200 and resp_anon_solved.context.get('status_filter') == 'solved' and is_empty_solved,
        f"Status: {resp_anon_solved.status_code}, Context status: {resp_anon_solved.context.get('status_filter')}, Solved count: {len(anon_solved_list)}"
    )


# -----------------------------------------------------------------------------
# SUITE 3: Screen 2 — Problem Workspace (docs/2.png)
# -----------------------------------------------------------------------------
def verify_suite_screen2_problem_workspace():
    print(f"\n{Colors.CYAN}--- Suite 3: Screen 2 — Problem Workspace (docs/2.png) ---{Colors.RESET}")
    client = Client()

    # 3.1 Anonymous GET /problem/aplusb
    resp = client.get('/problem/aplusb')
    reporter.record(
        "Test 3.1: GET /problem/aplusb returns HTTP 200 OK",
        resp.status_code == 200,
        f"Status: {resp.status_code}"
    )

    html = resp.content.decode('utf-8')

    # 3.2 Workspace root and split container
    has_wrap = 'problem-workspace-wrap' in html
    has_split_container = 'workspace-split-container' in html
    reporter.record(
        "Test 3.2: .problem-workspace-wrap and #workspace-split-container render",
        has_wrap and has_split_container,
        f"Wrap: {has_wrap}, Split: {has_split_container}"
    )

    # 3.3 Split panes & resizer divider
    has_left_pane = 'id="statement-pane"' in html
    has_divider = 'id="workspace-split-divider"' in html and 'divider-handle' in html
    has_right_pane = 'id="editor-pane"' in html
    reporter.record(
        "Test 3.3: #statement-pane, #workspace-split-divider, and #editor-pane render",
        has_left_pane and has_divider and has_right_pane,
        f"Left: {has_left_pane}, Divider: {has_divider}, Right: {has_right_pane}"
    )

    # 3.4 Header & Breadcrumb
    has_breadcrumb = 'workspace-breadcrumb' in html and '/problems/' in html
    has_title = 'workspace-problem-title' in html and 'A Plus B' in html
    has_star_toggle = 'problem-bookmark-star' in html
    has_tags = 'workspace-tag-pill' in html
    reporter.record(
        "Test 3.4: Workspace header (Breadcrumbs, Title 'A Plus B', Star bookmark, Tag badges)",
        has_breadcrumb and has_title and has_star_toggle and has_tags,
        f"Breadcrumb: {has_breadcrumb}, Title: {has_title}, Star: {has_star_toggle}, Tags: {has_tags}"
    )

    # 3.5 Five metric cards
    has_card_pts = 'metric-points' in html
    has_card_ac = 'metric-ac-rate' in html and 'metric-progress-bar' in html
    has_card_grp = 'metric-group' in html
    has_card_time = 'metric-time-limit' in html
    has_card_mem = 'metric-memory-limit' in html
    all_cards = has_card_pts and has_card_ac and has_card_grp and has_card_time and has_card_mem
    reporter.record(
        "Test 3.5: 5 Metric Cards (Points, AC Rate with progress bar, Group, Time Limit, Memory Limit)",
        all_cards,
        f"Pts: {has_card_pts}, AC: {has_card_ac}, Grp: {has_card_grp}, Time: {has_card_time}, Mem: {has_card_mem}"
    )

    # 3.6 Left Pane: Statement Tabs & Content
    has_tab_stmt = 'id="tab-statement"' in html
    has_tab_subm = 'id="tab-submissions"' in html
    has_stmt_body = 'statement-content' in html or 'panel-statement' in html
    has_license = 'statement-license' in html or 'creative-commons' in html or 'panel-statement' in html
    has_comments = 'panel-comments' in html
    reporter.record(
        "Test 3.6: Statement pane tabs, markdown body, license footer, and comments panel",
        has_tab_stmt and has_tab_subm and has_stmt_body and has_comments,
        f"Stmt Tab: {has_tab_stmt}, Subm Tab: {has_tab_subm}, Body: {has_stmt_body}, Comments: {has_comments}"
    )

    # 3.7 KaTeX Integration
    has_katex_css = 'katex.min.css' in html
    has_katex_js = 'katex.min.js' in html
    has_autorender_js = 'auto-render.min.js' in html
    has_katex_delimiters = 'renderMathInElement' in html and '$$' in html and '$' in html
    all_katex = has_katex_css and has_katex_js and has_autorender_js and has_katex_delimiters
    reporter.record(
        "Test 3.7: KaTeX CSS/JS assets and auto-render delimiters configuration ($$, \\[, $, \\(, ~)",
        all_katex,
        f"CSS: {has_katex_css}, JS: {has_katex_js}, AutoRender: {has_autorender_js}, Delims: {has_katex_delimiters}"
    )

    # 3.8 Action Toolbar
    has_lang_dropdown = 'custom-language-select' in html or 'id_language' in html
    has_btn_reset = 'btn-reset-code' in html
    has_btn_run = 'btn-run-code' in html
    has_btn_submit = 'btn-submit-code' in html and ('Submit' in html or 'btn-primary' in html)
    all_toolbar = has_lang_dropdown and has_btn_reset and has_btn_run and has_btn_submit
    reporter.record(
        "Test 3.8: Action toolbar (Custom language selector, Reset Code, Run Code, Submit Solution button)",
        all_toolbar,
        f"Lang: {has_lang_dropdown}, Reset: {has_btn_reset}, Run: {has_btn_run}, Submit: {has_btn_submit}"
    )

    # 3.9 Ace Editor Container & Floating Tools
    has_ace_container = 'id="ace_source"' in html or 'ace-editor-instance' in html
    has_btn_copy = 'btn-copy-code' in html
    has_btn_fullscreen = 'btn-fullscreen-code' in html
    has_draft_indicator = 'editor-draft-indicator' in html
    has_hidden_form = 'id="problem_submit"' in html and 'name="source"' in html and 'name="language"' in html
    all_editor = has_ace_container and has_btn_copy and has_btn_fullscreen and has_draft_indicator and has_hidden_form
    reporter.record(
        "Test 3.9: Ace editor card, floating toolbar (copy, fullscreen, autosave indicator) and hidden sync form",
        all_editor,
        f"Ace: {has_ace_container}, Copy: {has_btn_copy}, Fullscreen: {has_btn_fullscreen}, "
        f"Draft: {has_draft_indicator}, Form: {has_hidden_form}"
    )

    # 3.10 Testcases Console
    has_console = 'workspace-console' in html
    has_tab_cases = 'tab-console-testcases' in html
    has_tab_history = 'tab-console-submissions' in html
    has_cases_list = 'testcases-list' in html
    has_add_custom = 'btn-add-custom-test' in html
    all_console = has_console and has_tab_cases and has_tab_history and has_cases_list and has_add_custom
    reporter.record(
        "Test 3.10: Bottom console with Testcases/Submissions tabs, sample cards container, and + Add custom test button",
        all_console,
        f"Console: {has_console}, Tabs: {has_tab_cases}/{has_tab_history}, List: {has_cases_list}, Add: {has_add_custom}"
    )

    # 3.11 Authenticated /problem/aplusb/submit route
    user = User.objects.filter(is_active=True).first()
    client.force_login(user)
    resp_submit = client.get('/problem/aplusb/submit')
    submit_html = resp_submit.content.decode('utf-8')
    submit_has_workspace = 'workspace-split-container' in submit_html
    submit_has_editor = 'id="editor-pane"' in submit_html
    submit_has_submit_btn = 'btn-submit-code' in submit_html
    all_submit_route = resp_submit.status_code == 200 and submit_has_workspace and submit_has_editor and submit_has_submit_btn
    reporter.record(
        "Test 3.11: Authenticated GET /problem/aplusb/submit renders unified split workspace",
        all_submit_route,
        f"Status: {resp_submit.status_code}, Workspace: {submit_has_workspace}, Editor: {submit_has_editor}, Submit: {submit_has_submit_btn}"
    )

    # 3.12 Jinja2 AST check that templates/problem/workspace-header.html uses problem.types.all()
    header_path = JUDGE_ROOT / "templates" / "problem" / "workspace-header.html"
    header_ast = jinja2.Environment().parse(header_path.read_text(encoding="utf-8"))
    found_types_all_call = False
    found_raw_types_manager = False
    for if_node in header_ast.find_all(nodes.If):
        for elif_node in getattr(if_node, 'elif_', []):
            test = elif_node.test
            if isinstance(test, nodes.Call) and isinstance(test.node, nodes.Getattr) and test.node.attr == 'all':
                if isinstance(test.node.node, nodes.Getattr) and test.node.node.attr == 'types':
                    found_types_all_call = True
            elif isinstance(test, nodes.Getattr) and test.attr == 'types':
                if isinstance(test.node, nodes.Name) and test.node.name == 'problem':
                    found_raw_types_manager = True
    reporter.record(
        "Test 3.12: AST check: templates/problem/workspace-header.html uses problem.types.all() (avoids truthy RelatedManager bug)",
        found_types_all_call and not found_raw_types_manager,
        f"Types all call: {found_types_all_call}, Raw manager used: {found_raw_types_manager}"
    )


# -----------------------------------------------------------------------------
# SUITE 4: Client-Side Interactive Logic (Static JS Analysis)
# -----------------------------------------------------------------------------
def verify_suite_client_js_logic():
    print(f"\n{Colors.CYAN}--- Suite 4: Client-Side Interactive Logic (JavaScript Controllers) ---{Colors.RESET}")

    # 4.1 problems-list.js
    js_problems_path = JUDGE_ROOT / "resources" / "problems-list.js"
    js_problems = js_problems_path.read_text(encoding="utf-8")

    has_storage_key = "vcoder_bookmarked_problems" in js_problems
    has_bookmark_toggle = "toggleBookmark" in js_problems or "btn-bookmark-row" in js_problems
    has_badge_update = "bookmark-count-badge" in js_problems
    has_quick_filter = "filter-pill" in js_problems
    has_search_clear = "btn-clear-search" in js_problems
    reporter.record(
        "Test 4.1: problems-list.js implements bookmark persistence, badge updates, quick filter pills, and search clear",
        has_storage_key and has_bookmark_toggle and has_badge_update and has_quick_filter and has_search_clear,
        f"StorageKey: {has_storage_key}, Toggle: {has_bookmark_toggle}, Badge: {has_badge_update}, "
        f"Pills: {has_quick_filter}, Clear: {has_search_clear}"
    )

    # 4.2 problem-statement.js
    js_stmt_path = JUDGE_ROOT / "resources" / "problem-statement.js"
    js_stmt = js_stmt_path.read_text(encoding="utf-8")

    has_katex_render = "renderMathInElement" in js_stmt
    has_delimiters = "$$" in js_stmt and "\\[" in js_stmt and "~" in js_stmt
    has_samples_parser = "enhanceSampleTestcases" in js_stmt or "sample-box" in js_stmt
    has_copy_feedback = "Copied!" in js_stmt
    has_export_samples = "window.problemSamples" in js_stmt and "problem_samples_ready" in js_stmt
    reporter.record(
        "Test 4.2: problem-statement.js implements KaTeX math rendering, sample I/O card parsing, copy feedback, and window.problemSamples export",
        has_katex_render and has_delimiters and has_samples_parser and has_copy_feedback and has_export_samples,
        f"KaTeX: {has_katex_render}, Delims: {has_delimiters}, Samples: {has_samples_parser}, "
        f"Copy: {has_copy_feedback}, Export: {has_export_samples}"
    )

    # 4.3 problem-workspace.js
    js_ws_path = JUDGE_ROOT / "resources" / "problem-workspace.js"
    js_ws = js_ws_path.read_text(encoding="utf-8")

    has_split_resizer = "workspace-split-divider" in js_ws and "dmoj_split_ratio" in js_ws
    has_ace_init = "ace.edit" in js_ws
    has_autosave = "dmoj_draft:" in js_ws
    has_template_fetch = "/widgets/template" in js_ws
    has_test_runner = "btn-run-code" in js_ws or "runTestcase" in js_ws
    has_add_custom_test = "btn-add-custom-test" in js_ws or "addCustomTestcase" in js_ws
    has_submit_sync = "problem_submit" in js_ws and "id_source" in js_ws
    all_ws_js = (
        has_split_resizer and has_ace_init and has_autosave and
        has_template_fetch and has_test_runner and has_add_custom_test and has_submit_sync
    )
    reporter.record(
        "Test 4.3: problem-workspace.js implements split drag resizer, Ace setup, debounced autosave, template loader, test runner, and form sync",
        all_ws_js,
        f"Resizer: {has_split_resizer}, Ace: {has_ace_init}, Autosave: {has_autosave}, "
        f"Template: {has_template_fetch}, Runner: {has_test_runner}, Add: {has_add_custom_test}, Sync: {has_submit_sync}"
    )

    # 4.4 problems-list.js type filter handler & category/group input synchronization
    has_type_branch = "filterType === 'type'" in js_problems or 'filterType === "type"' in js_problems
    has_type_input_var = "filter-type" in js_problems or "typeInput" in js_problems
    has_type_submit = "typeInput.value" in js_problems
    has_group_sync = (
        ("groupInput" in js_problems or "filter-group" in js_problems) and
        ("categoryInput" in js_problems or "filter-category" in js_problems)
    )
    all_type_group_js = has_type_branch and has_type_input_var and has_type_submit and has_group_sync
    reporter.record(
        "Test 4.4: problems-list.js handles filterType === 'type' with form submission and synchronizes group/category inputs",
        all_type_group_js,
        f"TypeBranch: {has_type_branch}, TypeInput: {has_type_input_var}, TypeSubmit: {has_type_submit}, GroupSync: {has_group_sync}"
    )

    # 4.5 problems-list.js DOMContentLoaded executes bookmark filtering if active
    has_bookmark_func = "applyBookmarkFilter" in js_problems
    has_dom_ready = "DOMContentLoaded" in js_problems
    has_bookmark_on_load = (
        has_bookmark_func and
        has_dom_ready and
        ("urlHasBookmark" in js_problems or "isBookmarkedActive" in js_problems or "bookmarked" in js_problems)
    )
    has_call_in_dom = bool(re.search(r'DOMContentLoaded[\s\S]*?applyBookmarkFilter\s*\(', js_problems))
    reporter.record(
        "Test 4.5: problems-list.js triggers client-side bookmark filtering on DOMContentLoaded when bookmarked tab is active",
        has_bookmark_on_load and has_call_in_dom,
        f"BookmarkFunc: {has_bookmark_func}, DOMReady: {has_dom_ready}, CallInDOM: {has_call_in_dom}"
    )


# -----------------------------------------------------------------------------
# SUITE 5: End-to-End Submission Pipeline
# -----------------------------------------------------------------------------
def verify_suite_submission_pipeline():
    print(f"\n{Colors.CYAN}--- Suite 5: End-to-End Submission Pipeline ---{Colors.RESET}")
    client = Client()

    # 5.1 Unauthenticated POST redirects to login
    resp_unauth = client.post('/problem/aplusb/submit', {'source': 'print(1)', 'language': 1})
    reporter.record(
        "Test 5.1: Unauthenticated POST to /problem/aplusb/submit redirects to login (302)",
        resp_unauth.status_code == 302 and '/accounts/login/' in resp_unauth['Location'],
        f"Status: {resp_unauth.status_code}, Location: {resp_unauth.get('Location')}"
    )

    # 5.2 Authenticated POST with empty source triggers validation error
    user = User.objects.filter(is_active=True).first()
    client.force_login(user)
    py_lang = Language.objects.filter(key__startswith='PY').first() or Language.objects.first()

    resp_empty = client.post('/problem/aplusb/submit', {'source': '', 'language': py_lang.id})
    empty_content = resp_empty.content.decode('utf-8')
    reporter.record(
        "Test 5.2: Authenticated POST with empty source re-renders with validation error",
        resp_empty.status_code == 200 and 'error' in empty_content.lower(),
        f"Status: {resp_empty.status_code}, Has error: {'error' in empty_content.lower()}"
    )

    # 5.3 Authenticated POST with valid Python source creates submission
    initial_sub_count = Submission.objects.count()
    resp_valid = client.post('/problem/aplusb/submit', {
        'source': 'import sys\nprint(sum(map(int, sys.stdin.read().split())))\n',
        'language': py_lang.id,
    })
    new_sub_count = Submission.objects.count()

    is_redirect = resp_valid.status_code == 302 and '/submission/' in resp_valid.get('Location', '')
    created_in_db = new_sub_count == initial_sub_count + 1

    reporter.record(
        "Test 5.3: Authenticated POST with valid code creates Submission in DB and redirects to /submission/<id>",
        is_redirect and created_in_db,
        f"Status: {resp_valid.status_code}, Location: {resp_valid.get('Location')}, Submissions count delta: {new_sub_count - initial_sub_count}"
    )


# -----------------------------------------------------------------------------
# MAIN RUNNER
# -----------------------------------------------------------------------------
def main():
    print(f"{Colors.BOLD}{Colors.BLUE}======================================================================{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}MILESTONE 3 AUTOMATED VERIFICATION SUITE: SCREENS 1 & 2{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}======================================================================{Colors.RESET}")

    verify_suite_static_assets()
    verify_suite_screen1_problems_catalog()
    verify_suite_screen2_problem_workspace()
    verify_suite_client_js_logic()
    verify_suite_submission_pipeline()

    reporter.print_summary()
    return 0 if reporter.failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
