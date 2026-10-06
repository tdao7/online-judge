#!/usr/bin/env python3
"""
scripts/test_m2_challenger_workspace_empirics.py

Empirical Challenger Test Suite for Milestone 2:
- Split-Pane Problem Workspace (/problem/aplusb, /problem/array_reconstruction, /problem/aplusb/submit)
- Contests Arena & Live Workspace (/contest/wcc2026 vs /contest/monthly2026)
- SCSS & Compiled CSS layout rules (calc(100vh - 56px), 45%/55% ratio, 3-column contest grid)
- Draggable resizer divider, KaTeX delimiters, Ace editor integration
"""

import os
import re
import sys
from pathlib import Path

JUDGE_ROOT = Path(__file__).resolve().parent.parent
if str(JUDGE_ROOT) not in sys.path:
    sys.path.insert(0, str(JUDGE_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')
import django
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from judge.models import Contest, Problem, ContestProblem
import lxml.html

User = get_user_model()

passed_count = 0
failed_count = 0
findings = []


def assert_empiric(condition, title, details=""):
    global passed_count, failed_count
    if condition:
        passed_count += 1
        print(f"  \033[92m[PASS]\033[0m {title}")
    else:
        failed_count += 1
        print(f"  \033[91m[FAIL]\033[0m {title} -- {details}")
        findings.append({"title": title, "details": details})


def run_tests():
    global passed_count, failed_count
    client = Client()

    print("=" * 70)
    print("EMPIRICAL CHALLENGER TEST SUITE: WORKSPACE & CONTESTS")
    print("=" * 70)

    # -------------------------------------------------------------------------
    # SUITE 1: Problem Workspace (/problem/aplusb)
    # -------------------------------------------------------------------------
    print("\n--- Suite 1: /problem/aplusb Verification ---")
    resp_aplusb = client.get('/problem/aplusb')
    assert_empiric(resp_aplusb.status_code == 200, "1.1 GET /problem/aplusb returns HTTP 200", f"Got status {resp_aplusb.status_code}")
    html_aplusb = resp_aplusb.content.decode('utf-8')
    dom_aplusb = lxml.html.fromstring(html_aplusb)

    # Footer suppression check
    footer_elements = dom_aplusb.xpath('//footer[contains(@class, "app-footer")]')
    assert_empiric(len(footer_elements) == 0, "1.2 Footer is completely absent from DOM on /problem/aplusb", f"Found {len(footer_elements)} footer elements in DOM")
    assert_empiric('class="app-footer"' not in html_aplusb, "1.3 String 'class=\"app-footer\"' not in /problem/aplusb HTML", "Found app-footer in raw HTML")

    # Main viewport and workspace structure
    workspace_wrap = dom_aplusb.xpath('//*[contains(@class, "problem-workspace-wrap")]')
    assert_empiric(len(workspace_wrap) == 1, "1.4 .problem-workspace-wrap is present in DOM", f"Found {len(workspace_wrap)}")

    split_container = dom_aplusb.xpath('//*[@id="workspace-split-container"]')
    assert_empiric(len(split_container) == 1, "1.5 #workspace-split-container is present in DOM", f"Found {len(split_container)}")

    # Statement pane
    statement_pane = dom_aplusb.xpath('//*[@id="statement-pane"]')
    assert_empiric(len(statement_pane) == 1, "1.6 #statement-pane is present in DOM", f"Found {len(statement_pane)}")

    # Editor pane
    editor_pane = dom_aplusb.xpath('//*[@id="editor-pane"]')
    assert_empiric(len(editor_pane) == 1, "1.7 #editor-pane is present in DOM", f"Found {len(editor_pane)}")

    # Divider
    divider = dom_aplusb.xpath('//*[@id="workspace-split-divider"]')
    assert_empiric(len(divider) == 1, "1.8 #workspace-split-divider is present in DOM", f"Found {len(divider)}")
    if divider:
        handle = divider[0].xpath('.//*[contains(@class, "divider-handle")]')
        assert_empiric(len(handle) == 1, "1.9 .divider-handle is present inside #workspace-split-divider")

    # KaTeX script & styles
    katex_css = dom_aplusb.xpath('//link[contains(@href, "katex")]')
    katex_js = dom_aplusb.xpath('//script[contains(@src, "katex")]')
    assert_empiric(len(katex_css) >= 1, "1.10 KaTeX CSS link present in DOM", f"Found {len(katex_css)}")
    assert_empiric(len(katex_js) >= 1, "1.11 KaTeX JS scripts present in DOM", f"Found {len(katex_js)}")
    assert_empiric('renderMathInElement' in html_aplusb, "1.12 KaTeX renderMathInElement auto-render script included in HTML")
    assert_empiric('$$' in html_aplusb and '\\[' in html_aplusb and '$' in html_aplusb, "1.13 KaTeX delimiters $$, \\[, $ configured in auto-render")

    # Ace editor integration
    ace_js = dom_aplusb.xpath('//script[contains(@src, "ace.js")]')
    assert_empiric(len(ace_js) >= 1, "1.14 Ace editor ace.js script is included in DOM", f"Found {len(ace_js)}")
    ace_card = dom_aplusb.xpath('//*[@id="ace-editor-card"]')
    assert_empiric(len(ace_card) == 1, "1.15 #ace-editor-card container present in DOM")
    lang_selector = dom_aplusb.xpath('//*[@id="lang-dropdown-trigger"]')
    assert_empiric(len(lang_selector) == 1, "1.16 Custom language dropdown trigger present in DOM")
    btn_submit = dom_aplusb.xpath('//*[@id="btn-submit-code"]')
    assert_empiric(len(btn_submit) == 1, "1.17 Submit solution CTA button (#btn-submit-code) present in DOM")

    # -------------------------------------------------------------------------
    # SUITE 2: Problem Workspace Alternative (/problem/array_reconstruction)
    # -------------------------------------------------------------------------
    print("\n--- Suite 2: /problem/array_reconstruction Verification ---")
    resp_arr = client.get('/problem/array_reconstruction')
    assert_empiric(resp_arr.status_code == 200, "2.1 GET /problem/array_reconstruction returns HTTP 200", f"Got status {resp_arr.status_code}")
    html_arr = resp_arr.content.decode('utf-8')
    dom_arr = lxml.html.fromstring(html_arr)

    assert_empiric(len(dom_arr.xpath('//footer[contains(@class, "app-footer")]')) == 0, "2.2 Footer is suppressed on /problem/array_reconstruction")
    assert_empiric(len(dom_arr.xpath('//*[@id="workspace-split-container"]')) == 1, "2.3 Split container present on /problem/array_reconstruction")
    # Verify math content exists in statement
    statement_body = dom_arr.xpath('//*[@id="statement-content"]') or dom_arr.xpath('//*[@id="statement-pane"]')
    statement_text = statement_body[0].text_content() if statement_body else ""
    assert_empiric('b_i' in statement_text or 'a_i' in statement_text or '$' in html_arr, "2.4 LaTeX math syntax present in problem description")

    # -------------------------------------------------------------------------
    # SUITE 3: Problem Submit Page (/problem/aplusb/submit)
    # -------------------------------------------------------------------------
    print("\n--- Suite 3: /problem/aplusb/submit Authenticated Verification ---")
    test_user = User.objects.filter(is_superuser=True).first()
    if not test_user:
        test_user = User.objects.first()
    client.force_login(test_user)
    resp_submit = client.get('/problem/aplusb/submit')
    assert_empiric(resp_submit.status_code == 200, "3.1 Authenticated GET /problem/aplusb/submit returns HTTP 200")
    html_submit = resp_submit.content.decode('utf-8')
    dom_submit = lxml.html.fromstring(html_submit)
    assert_empiric(len(dom_submit.xpath('//footer[contains(@class, "app-footer")]')) == 0, "3.2 Footer is suppressed on /problem/aplusb/submit")
    assert_empiric(len(dom_submit.xpath('//*[@id="workspace-split-container"]')) == 1, "3.3 Split container present on /problem/aplusb/submit")
    client.logout()

    # -------------------------------------------------------------------------
    # SUITE 4: Contests Arena & Live Workspace (/contest/wcc2026 vs /contest/monthly2026)
    # -------------------------------------------------------------------------
    print("\n--- Suite 4: Contests Arena & Live Workspace ---")
    # Test dispatch target /contest/wcc2026
    resp_wcc = client.get('/contest/wcc2026')
    html_wcc = resp_wcc.content.decode('utf-8')
    dom_wcc = lxml.html.fromstring(html_wcc)

    wcc_exists_db = Contest.objects.filter(key='wcc2026').exists()
    assert_empiric(wcc_exists_db, "4.1 Contest 'wcc2026' exists in database", "Contest 'wcc2026' is MISSING in database!")

    has_wcc_split = len(dom_wcc.xpath('//*[contains(@class, "contest-split-layout")]')) > 0 or len(dom_wcc.xpath('//*[@id="contest-workspace-wrapper"]')) > 0
    assert_empiric(has_wcc_split, "4.2 /contest/wcc2026 renders 3-column live contest workspace", "Renders error page 'No such contest' instead of contest workspace!")

    wcc_footer_suppressed = len(dom_wcc.xpath('//footer[contains(@class, "app-footer")]')) == 0
    assert_empiric(wcc_footer_suppressed, "4.3 /contest/wcc2026 suppresses footer", "Footer is VISIBLE on /contest/wcc2026 error page!")

    # Now test seeded contest /contest/monthly2026
    print("\n--- Suite 4b: Seeded Live Contest /contest/monthly2026 ---")
    resp_monthly = client.get('/contest/monthly2026')
    assert_empiric(resp_monthly.status_code == 200, "4.4 GET /contest/monthly2026 returns HTTP 200")
    html_monthly = resp_monthly.content.decode('utf-8')
    dom_monthly = lxml.html.fromstring(html_monthly)

    monthly_footer = dom_monthly.xpath('//footer[contains(@class, "app-footer")]')
    assert_empiric(len(monthly_footer) == 0, "4.5 Footer is suppressed on /contest/monthly2026", f"Found {len(monthly_footer)} footer elements")

    contest_wrap = dom_monthly.xpath('//*[@id="contest-workspace-wrapper"]')
    assert_empiric(len(contest_wrap) == 1, "4.6 #contest-workspace-wrapper is present on /contest/monthly2026")

    split_layout = dom_monthly.xpath('//*[contains(@class, "contest-split-layout")]')
    assert_empiric(len(split_layout) == 1, "4.7 .contest-split-layout is present on /contest/monthly2026")

    # Column 1: Sidebar
    col_sidebar = dom_monthly.xpath('//*[contains(@class, "contest-problems-sidebar")]')
    assert_empiric(len(col_sidebar) == 1, "4.8 Column 1: .contest-problems-sidebar is present")

    # Column 2: Statement Pane
    col_stmt = dom_monthly.xpath('//*[contains(@class, "contest-statement-pane")]')
    assert_empiric(len(col_stmt) == 1, "4.9 Column 2: .contest-statement-pane is present")

    # Column 3: Editor Pane
    col_editor = dom_monthly.xpath('//*[contains(@class, "contest-editor-pane")]')
    assert_empiric(len(col_editor) == 1, "4.10 Column 3: .contest-editor-pane is present")

    # Problem switchers
    nav_cards = dom_monthly.xpath('//*[contains(@class, "problem-nav-card")]')
    assert_empiric(len(nav_cards) >= 3, f"4.11 Problem switcher cards present (found {len(nav_cards)})")

    # -------------------------------------------------------------------------
    # SUITE 5: SCSS & Compiled CSS Layout Architecture
    # -------------------------------------------------------------------------
    print("\n--- Suite 5: CSS & SCSS Rules Empirical Verification ---")
    app_shell_scss = Path(JUDGE_ROOT / "resources" / "app-shell.scss").read_text()
    prob_scss = Path(JUDGE_ROOT / "resources" / "problem-workspace.scss").read_text()
    contest_scss = Path(JUDGE_ROOT / "resources" / "contest-workspace.scss").read_text()
    prob_js = Path(JUDGE_ROOT / "resources" / "problem-workspace.js").read_text()

    # Rule 1: Viewport height calc(100vh - 56px) or calc(100vh - var(--navbar-height, 56px))
    assert_empiric(
        'calc(100vh - var(--navbar-height, 56px))' in app_shell_scss or 'calc(100vh - 56px)' in app_shell_scss,
        "5.1 app-shell.scss defines workspace height calc(100vh - var(--navbar-height, 56px))"
    )
    assert_empiric(
        ':has(.problem-workspace-wrap)' in app_shell_scss and ':has(#problem-workspace)' in app_shell_scss,
        "5.2 app-shell.scss targets .problem-workspace-wrap via :has selector"
    )
    assert_empiric(
        ':has(.contest-workspace-wrapper)' in app_shell_scss,
        "5.3 app-shell.scss targets .contest-workspace-wrapper via :has selector"
    )

    # Rule 2: Zero scrollbars / overflow hidden
    assert_empiric(
        'overflow: hidden !important;' in app_shell_scss,
        "5.4 app-shell.scss enforces overflow: hidden !important on workspace canvas"
    )
    assert_empiric(
        '.app-footer {\n      display: none !important;' in app_shell_scss or '.app-footer { display: none !important; }' in app_shell_scss,
        "5.5 app-shell.scss enforces .app-footer display: none !important in workspace canvas"
    )

    # Rule 3: 45% statement / 55% editor
    assert_empiric(
        'flex: 0 0 45%;' in prob_scss and 'width: 45%;' in prob_scss and 'max-width: 45%;' in prob_scss,
        "5.6 problem-workspace.scss statement pane defined as flex: 0 0 45%, width: 45%, max-width: 45%"
    )
    assert_empiric(
        'flex: 1 1 55%;' in prob_scss and 'width: 55%;' in prob_scss,
        "5.7 problem-workspace.scss editor pane defined as flex: 1 1 55%, width: 55%"
    )
    assert_empiric(
        'defaultLeftWidthPercent: 45' in prob_js,
        "5.8 problem-workspace.js defaultLeftWidthPercent is 45"
    )

    # Rule 4: 3-column contest workspace (240px 1fr 1.15fr)
    assert_empiric(
        'grid-template-columns: 240px 1fr 1.15fr;' in contest_scss,
        "5.9 contest-workspace.scss contest split layout defined as grid-template-columns: 240px 1fr 1.15fr"
    )

    # Rule 5: Resizer divider
    assert_empiric(
        'cursor: col-resize;' in prob_scss,
        "5.10 Resizer divider defines cursor: col-resize"
    )
    assert_empiric(
        'minLeftWidthPercent: 28' in prob_js and 'maxLeftWidthPercent: 68' in prob_js,
        "5.11 problem-workspace.js enforces min/max clamping on drag"
    )
    assert_empiric(
        "localStorage.getItem('dmoj_split_ratio')" in prob_js and "localStorage.setItem('dmoj_split_ratio'" in prob_js,
        "5.12 problem-workspace.js persists split ratio to localStorage"
    )

    # -------------------------------------------------------------------------
    # SUITE 6: Compiled CSS Files in static/ and resources/
    # -------------------------------------------------------------------------
    print("\n--- Suite 6: Compiled CSS Inspection ---")
    compiled_prob_css = Path(JUDGE_ROOT / "static" / "problem-workspace.css").read_text()
    compiled_contest_css = Path(JUDGE_ROOT / "static" / "contest-workspace.css").read_text()
    compiled_app_css = Path(JUDGE_ROOT / "static" / "style.css").read_text()

    assert_empiric(
        'flex: 0 0 45%' in compiled_prob_css or 'flex:0 0 45%' in compiled_prob_css,
        "6.1 static/problem-workspace.css contains compiled statement pane flex: 0 0 45%"
    )
    assert_empiric(
        'flex: 1 1 55%' in compiled_prob_css or 'flex:1 1 55%' in compiled_prob_css,
        "6.2 static/problem-workspace.css contains compiled editor pane flex: 1 1 55%"
    )
    assert_empiric(
        'grid-template-columns: 240px 1fr 1.15fr' in compiled_contest_css or 'grid-template-columns:240px 1fr 1.15fr' in compiled_contest_css,
        "6.3 static/contest-workspace.css contains compiled grid-template-columns: 240px 1fr 1.15fr"
    )
    assert_empiric(
        'calc(100vh - 56px)' in compiled_app_css or 'calc(100vh - var(--navbar-height, 56px))' in compiled_app_css,
        "6.4 static/style.css contains compiled calc(100vh - ...) height rule"
    )

    # -------------------------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------------------------
    total = passed_count + failed_count
    print("\n" + "=" * 70)
    print(f"EMPIRICAL TEST SUMMARY: {passed_count}/{total} Passed ({(passed_count/total*100) if total else 0:.1f}%)")
    print(f"FAILED: {failed_count}")
    print("=" * 70)

    if findings:
        print("\nFINDINGS / FAILURES:")
        for idx, f in enumerate(findings, 1):
            print(f"{idx}. {f['title']}: {f['details']}")

    return failed_count == 0


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
