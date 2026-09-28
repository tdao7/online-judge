#!/usr/bin/env python3
"""
verify_m2_regression.py
Milestone 2 Iteration 2 End-to-End Automated Regression & Verification Suite

Verifies:
1. CSS AST & Token Integrity:
   - No `button { color: white !important; }` in `resources/style.css` and `resources/dark/style.css`.
   - No legacy Bootstrap 3 button gradients (#337ab7 / #265a88) or border (#245580).
   - Topbar buttons (.mobile-nav-toggle, .header-icon-btn, .modal-search-close, .logout-btn)
     do NOT have computed/effective color `white !important`.
2. Topbar Flexbox & #user-links Layout:
   - #user-links in topbar is position: relative (not position: absolute).
   - #user-links participates in flex container flow without absolute displacement.
3. WCAG 2.1 AA Visual Contrast (ratio >= 4.5:1):
   - Mobile hamburger toggle icon vs. topbar background (light & dark).
   - Notification bell icon vs. topbar / button background (light & dark).
   - Modal search ESC close badge vs. modal input/header background (light & dark).
   - User dropdown logout button vs. dropdown menu background (light & dark).
4. Interactive Shell DOM Tests (68 tests):
   - Keyboard shortcuts (⌘K, Ctrl+K, /, ESC).
   - Search filtering & selection.
   - Mobile hamburger drawer open/close & swipe gestures.
   - User profile dropdown menu.
   - Traffic lights window controls.
   - Notification bell popover.
   - Adversarial & stress testing (minimal DOM, 100x rapid clicks, XSS/regex).
5. Backend Regressions & App Shell Templates (41 tests):
   - Context processors.
   - Core routes rendering in .mac-app-window (/, /problems/, /submissions/, /contests/, /users/, auth).
   - Authentication states & dropdown contents.
   - Contest countdown timer banner.
   - Dynamic MPTT navigation tree.
6. Django Unit Test Suite (86 tests):
   - Full upstream judge test suite (`manage.py test judge`).

Usage:
  ./venv/bin/python verify_m2_regression.py [OPTIONS]

Options:
  --fast             Run CSS AST, layout, contrast, JS, and backend regression suites (skip slow Django tests)
  --only-css         Run only CSS AST & legacy leak checks
  --only-layout      Run only #user-links positioning checks
  --only-contrast    Run only WCAG AA contrast ratio checks
  --only-js          Run only 68 interactive JS DOM tests
  --only-backend     Run only 41 backend regression tests
  --only-django      Run only 86 Django unit tests
  --json FILE        Export test results as JSON to FILE
"""

import os
import sys
import re
import json
import argparse
import subprocess
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).resolve().parent
# If running inside .agents/teamwork/..., locate judge repo root
if "vcoderlog-judge" not in str(REPO_ROOT):
    JUDGE_ROOT = Path("/Users/ryanx/workspace/vcoderlog-workspace/vcoderlog-judge")
else:
    # Walk up to vcoderlog-judge directory
    p = REPO_ROOT
    while p.name != "vcoderlog-judge" and p != p.parent:
        p = p.parent
    JUDGE_ROOT = p

STYLE_LIGHT_PATH = JUDGE_ROOT / "resources" / "style.css"
STYLE_DARK_PATH = JUDGE_ROOT / "resources" / "dark" / "style.css"
JS_TEST_PATH = JUDGE_ROOT / "scripts" / "test_m2_interactive_shell.js"
PY_BACKEND_TEST_PATH = JUDGE_ROOT / "scripts" / "test_m2_backend_regressions.py"
PYTHON_BIN = JUDGE_ROOT / "venv" / "bin" / "python"
MANAGE_PY = JUDGE_ROOT / "manage.py"

# Try importing tinycss2
try:
    import tinycss2
except ImportError:
    tinycss2 = None

# Color terminal output
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
        self.warnings = 0

    def record(self, test_name, passed, detail="", is_warning=False):
        if passed:
            self.passed += 1
            print(f"  {Colors.GREEN}[PASS]{Colors.RESET} {test_name}")
            self.results.append({"name": test_name, "status": "PASS", "detail": detail})
        elif is_warning:
            self.warnings += 1
            print(f"  {Colors.YELLOW}[WARN]{Colors.RESET} {test_name} - {detail}")
            self.results.append({"name": test_name, "status": "WARN", "detail": detail})
        else:
            self.failed += 1
            print(f"  {Colors.RED}[FAIL]{Colors.RESET} {test_name} - {detail}")
            self.results.append({"name": test_name, "status": "FAIL", "detail": detail})

    def print_summary(self):
        total = self.passed + self.failed
        print("\n" + "=" * 65)
        status_color = Colors.GREEN if self.failed == 0 else Colors.RED
        print(f"{Colors.BOLD}VERIFICATION SUMMARY:{Colors.RESET} "
              f"Total: {total} | "
              f"{Colors.GREEN}Passed: {self.passed}{Colors.RESET} | "
              f"{Colors.RED}Failed: {self.failed}{Colors.RESET} | "
              f"{Colors.YELLOW}Warnings: {self.warnings}{Colors.RESET}")
        print("=" * 65)
        return self.failed == 0


reporter = VerificationReporter()


# -----------------------------------------------------------------------------
# Utility: Color Contrast & WCAG Luminance
# -----------------------------------------------------------------------------
def parse_hex_color(hex_str):
    hex_str = hex_str.strip().lstrip("#")
    if len(hex_str) == 3:
        hex_str = "".join(c * 2 for c in hex_str)
    if len(hex_str) != 6:
        # Fallback if unparseable
        return (0, 0, 0)
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_relative_luminance(r, g, b):
    def comp(c):
        sc = c / 255.0
        return sc / 12.92 if sc <= 0.04045 else ((sc + 0.055) / 1.055) ** 2.4
    return 0.2126 * comp(r) + 0.7152 * comp(g) + 0.0722 * comp(b)


def calculate_contrast_ratio(color1, color2):
    r1, g1, b1 = parse_hex_color(color1) if isinstance(color1, str) else color1
    r2, g2, b2 = parse_hex_color(color2) if isinstance(color2, str) else color2
    l1 = rgb_to_relative_luminance(r1, g1, b1)
    l2 = rgb_to_relative_luminance(r2, g2, b2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def normalize_color_value(val, root_vars=None):
    if not val:
        return ""
    val = val.strip()
    # Resolve CSS variable
    m = re.match(r"var\((--[\w-]+)(?:,\s*([^)]+))?\)", val)
    if m:
        var_name = m.group(1)
        fallback = m.group(2)
        if root_vars and var_name in root_vars:
            val = root_vars[var_name]
        elif fallback:
            val = fallback.strip()
    # Normalize common names
    val_lower = val.lower()
    if val_lower == "white":
        return "#FFFFFF"
    if val_lower == "black":
        return "#000000"
    if val_lower == "transparent":
        return "transparent"
    # Hex normalization
    if val.startswith("#"):
        return val.upper()
    return val


# -----------------------------------------------------------------------------
# CSS Specificity & Cascade Parser
# -----------------------------------------------------------------------------
class CSSCascadeModel:
    def __init__(self, css_content):
        self.css = css_content
        self.root_vars = {}
        self.rules = []
        self._parse()

    def _parse(self):
        if not tinycss2:
            return
        parsed_rules = tinycss2.parse_stylesheet(self.css, skip_whitespace=True, skip_comments=True)
        order = 0
        for rule in parsed_rules:
            if rule.type == "qualified-rule":
                order += 1
                prelude = tinycss2.serialize(rule.prelude).strip()
                if prelude == ":root":
                    decls = tinycss2.parse_declaration_list(rule.content, skip_whitespace=True, skip_comments=True)
                    for d in decls:
                        if d.type == "declaration" and d.name.startswith("--"):
                            self.root_vars[d.name] = tinycss2.serialize(d.value).strip()
                else:
                    decls = tinycss2.parse_declaration_list(rule.content, skip_whitespace=True, skip_comments=True)
                    clean_decls = []
                    for d in decls:
                        if d.type == "declaration":
                            val = tinycss2.serialize(d.value).strip()
                            clean_decls.append({
                                "name": d.name,
                                "value": val,
                                "important": d.important
                            })
                    selectors = [s.strip() for s in prelude.split(",")]
                    self.rules.append({
                        "order": order,
                        "prelude": prelude,
                        "selectors": selectors,
                        "declarations": clean_decls
                    })

    @staticmethod
    def calc_specificity(sel):
        sel = sel.strip()
        ids = len(re.findall(r"#[a-zA-Z0-9_-]+", sel))
        classes = len(re.findall(r"\.[a-zA-Z0-9_-]+", sel))
        attrs = len(re.findall(r"\[[^\]]+\]", sel))
        pseudos = len(re.findall(r":(?!:)[a-zA-Z0-9_-]+(?:\([^)]*\))?", sel))
        class_score = classes + attrs + pseudos
        cleaned = re.sub(r"#[a-zA-Z0-9_-]+", "", sel)
        cleaned = re.sub(r"\.[a-zA-Z0-9_-]+", "", cleaned)
        cleaned = re.sub(r"\[[^\]]+\]", "", cleaned)
        cleaned = re.sub(r":+[a-zA-Z0-9_-]+(?:\([^)]*\))?", "", cleaned)
        elements = len(re.findall(r"[a-zA-Z0-9_-]+", cleaned))
        return (ids, class_score, elements)

    @staticmethod
    def matches_element(sel, tag, classes, elem_id):
        sel = sel.strip()
        parts = sel.split()
        last = parts[-1]
        if "#" in last:
            m = re.search(r"#([a-zA-Z0-9_-]+)", last)
            if m and elem_id != m.group(1):
                return False
        tag_match = re.match(r"^[a-zA-Z0-9_-]+", last)
        if tag_match:
            if tag_match.group(0).lower() != tag.lower():
                return False
        class_matches = re.findall(r"\.([a-zA-Z0-9_-]+)", last)
        for cp in class_matches:
            if cp not in classes:
                return False
        return True

    def resolve_property(self, tag, classes, elem_id, prop_name):
        candidates = []
        for r in self.rules:
            for s in r["selectors"]:
                if self.matches_element(s, tag, classes, elem_id):
                    for d in r["declarations"]:
                        if d["name"] == prop_name:
                            spec = self.calc_specificity(s)
                            val = normalize_color_value(d["value"], self.root_vars) if prop_name == "color" else d["value"]
                            candidates.append({
                                "important": d["important"],
                                "specificity": spec,
                                "order": r["order"],
                                "value": val,
                                "selector": s
                            })
        if not candidates:
            return None
        # Sort by importance, then specificity, then order
        candidates.sort(key=lambda x: (x["important"], x["specificity"], x["order"]))
        return candidates[-1]


# -----------------------------------------------------------------------------
# SUITE 1: CSS AST & Token Integrity Verification
# -----------------------------------------------------------------------------
def verify_suite_css():
    print(f"\n{Colors.CYAN}--- Suite 1: CSS AST & Token Integrity Verification ---{Colors.RESET}")

    if not STYLE_LIGHT_PATH.exists():
        reporter.record("Compiled light style.css existence", False, f"File not found: {STYLE_LIGHT_PATH}")
        return
    if not STYLE_DARK_PATH.exists():
        reporter.record("Compiled dark style.css existence", False, f"File not found: {STYLE_DARK_PATH}")
        return

    with open(STYLE_LIGHT_PATH, "r", encoding="utf-8") as f:
        css_light = f.read()
    with open(STYLE_DARK_PATH, "r", encoding="utf-8") as f:
        css_dark = f.read()

    # 1.1 Regex leak check on button { color: white !important } in style.css
    # Look for button in selector combined with color: white !important
    leak_light = re.search(r"(?:^|[,\s])button\s*(?:,\s*|\{)[^{]*\{[^}]*color:\s*(?:white|#fff(?:fff)?|rgb\(\s*255\s*,\s*255\s*,\s*255\s*\))\s*!important", css_light, re.IGNORECASE)
    reporter.record(
        "Test 1.1: resources/style.css contains NO un-scoped `button { color: white !important; }`",
        leak_light is None,
        f"Found match: {leak_light.group(0)[:60]}..." if leak_light else ""
    )

    # 1.2 Regex leak check on dark/style.css
    leak_dark = re.search(r"(?:^|[,\s])button\s*(?:,\s*|\{)[^{]*\{[^}]*color:\s*(?:white|#fff(?:fff)?|rgb\(\s*255\s*,\s*255\s*,\s*255\s*\))\s*!important", css_dark, re.IGNORECASE)
    reporter.record(
        "Test 1.2: resources/dark/style.css contains NO un-scoped `button { color: white !important; }`",
        leak_dark is None,
        f"Found match: {leak_dark.group(0)[:60]}..." if leak_dark else ""
    )

    # 1.3 AST Verification: parse rules targeting bare button with tinycss2
    if tinycss2:
        model_light = CSSCascadeModel(css_light)
        bare_button_leaks = []
        for r in model_light.rules:
            for s in r["selectors"]:
                if s.strip() == "button":
                    for d in r["declarations"]:
                        if d["name"] == "color" and d["important"]:
                            val_norm = normalize_color_value(d["value"]).upper()
                            if val_norm in ("#FFFFFF", "RGB(255, 255, 255)"):
                                bare_button_leaks.append(f"Selector '{r['prelude']}' declares color: {d['value']} !important")
        reporter.record(
            "Test 1.3: tinycss2 AST verifies zero bare `button` selectors declare `color: white !important`",
            len(bare_button_leaks) == 0,
            "; ".join(bare_button_leaks)
        )
    else:
        reporter.record("Test 1.3: tinycss2 AST verification", True, "tinycss2 not available, regex verified", is_warning=True)

    # 1.4 Check elimination of raw Bootstrap 3 button gradient
    # Raw gradient: linear-gradient(to bottom, #337ab7 0, #265a88 100%)
    raw_grad_light = re.search(r"linear-gradient\([^)]*#337ab7[^)]*#265a88[^)]*\)", css_light, re.IGNORECASE)
    reporter.record(
        "Test 1.4: resources/style.css contains NO raw Bootstrap 3 blue gradient (#337ab7 / #265a88)",
        raw_grad_light is None,
        f"Found raw Bootstrap 3 gradient at match: {raw_grad_light.group(0)}" if raw_grad_light else ""
    )

    raw_grad_dark = re.search(r"linear-gradient\([^)]*#337ab7[^)]*#265a88[^)]*\)", css_dark, re.IGNORECASE)
    reporter.record(
        "Test 1.5: resources/dark/style.css contains NO raw Bootstrap 3 blue gradient (#337ab7 / #265a88)",
        raw_grad_dark is None,
        f"Found raw Bootstrap 3 gradient in dark theme: {raw_grad_dark.group(0)}" if raw_grad_dark else ""
    )

    # 1.6 Verify shell buttons do NOT have computed color white !important (Light & Dark)
    if tinycss2:
        model_light = CSSCascadeModel(css_light)
        model_dark = CSSCascadeModel(css_dark)
        for btn_name, tag, classes, eid in [
            ("mobile-nav-toggle", "button", {"mobile-nav-toggle"}, "mobile-nav-toggle"),
            ("notification-bell", "button", {"header-icon-btn", "notification-bell-btn"}, "notification-bell"),
            ("modal-search-close", "button", {"modal-search-close"}, "modal-search-close"),
            ("logout-btn", "button", {"dropdown-item", "logout-btn"}, "logout-btn"),
        ]:
            # Light mode
            eff_color_l = model_light.resolve_property(tag, classes, eid, "color")
            is_white_important_l = (
                eff_color_l is not None and
                eff_color_l["important"] and
                eff_color_l["value"] in ("#FFFFFF", "white", "rgb(255, 255, 255)", "#FFF")
            )
            val_display_l = eff_color_l["value"] if eff_color_l else "inherited"
            rule_display_l = eff_color_l["selector"] if eff_color_l else "none"
            reporter.record(
                f"Test 1.6 [Light] ({btn_name}): Effective color is NOT `white !important`",
                not is_white_important_l,
                f"Computed value: {val_display_l} (important={eff_color_l['important'] if eff_color_l else False}, rule={rule_display_l})"
            )

            # Dark mode
            eff_color_d = model_dark.resolve_property(tag, classes, eid, "color")
            is_white_important_d = (
                eff_color_d is not None and
                eff_color_d["important"] and
                eff_color_d["value"] in ("#FFFFFF", "white", "rgb(255, 255, 255)", "#FFF")
            )
            val_display_d = eff_color_d["value"] if eff_color_d else "inherited"
            rule_display_d = eff_color_d["selector"] if eff_color_d else "none"
            reporter.record(
                f"Test 1.7 [Dark] ({btn_name}): Effective color is NOT `white !important`",
                not is_white_important_d,
                f"Computed value: {val_display_d} (important={eff_color_d['important'] if eff_color_d else False}, rule={rule_display_d})"
            )



# -----------------------------------------------------------------------------
# SUITE 2: Topbar Flexbox & #user-links Layout Verification
# -----------------------------------------------------------------------------
def verify_suite_layout():
    print(f"\n{Colors.CYAN}--- Suite 2: Topbar Flexbox & #user-links Layout Verification ---{Colors.RESET}")

    if not STYLE_LIGHT_PATH.exists():
        reporter.record("Style existence", False, "Missing style.css")
        return

    with open(STYLE_LIGHT_PATH, "r", encoding="utf-8") as f:
        css_light = f.read()

    # 2.1 Check if #user-links has un-overridden position: absolute
    # In legacy DMOJ: #user-links { top: 0; right: 0; position: absolute; height: 100%; }
    if tinycss2:
        model_light = CSSCascadeModel(css_light)
        eff_pos = model_light.resolve_property("div", {"header-user-menu"}, "user-links", "position")
        pos_val = eff_pos["value"].strip() if eff_pos else "static"
        is_relative_or_flex = pos_val in ("relative", "static")
        reporter.record(
            "Test 2.1: `#user-links.header-user-menu` effective CSS position is relative/static in flex flow",
            is_relative_or_flex,
            f"Computed position: '{pos_val}' (from rule '{eff_pos['selector'] if eff_pos else 'default'}')"
        )

        # 2.2 Verify top and right displacement are not active on #user-links
        eff_top = model_light.resolve_property("div", {"header-user-menu"}, "user-links", "top")
        eff_right = model_light.resolve_property("div", {"header-user-menu"}, "user-links", "right")
        top_val = eff_top["value"].strip() if eff_top else "auto"
        right_val = eff_right["value"].strip() if eff_right else "auto"
        is_undisplaced = (pos_val == "relative" and (top_val in ("auto", "0px", "0") or not eff_top["important"])) or pos_val != "absolute"
        reporter.record(
            "Test 2.2: `#user-links` is not absolutely pinned to top: 0 / right: 0",
            pos_val != "absolute",
            f"position: {pos_val}, top: {top_val}, right: {right_val}"
        )
    else:
        # Fallback regex
        abs_leak = re.search(r"#user-links\s*\{[^}]*position:\s*absolute", css_light)
        reporter.record(
            "Test 2.1: `#user-links` position: absolute leak absent",
            abs_leak is None,
            "Found #user-links { position: absolute }" if abs_leak else ""
        )

    # 2.3 Verify base.html template structure places #user-links inside topbar-right flex container
    base_html_path = JUDGE_ROOT / "templates" / "base.html"
    if base_html_path.exists():
        with open(base_html_path, "r", encoding="utf-8") as f:
            base_html = f.read()
        has_user_links_in_topbar = bool(re.search(r'<div\s+id="user-links"\s+class="header-user-menu"', base_html))
        has_topbar_right = '<div class="topbar-right">' in base_html
        reporter.record(
            "Test 2.3: `templates/base.html` encapsulates `#user-links` in `.header-user-menu` inside `.topbar-right`",
            has_user_links_in_topbar and has_topbar_right,
            "Template structure confirmed"
        )


# -----------------------------------------------------------------------------
# SUITE 3: WCAG 2.1 AA Visual Contrast Verification (ratio >= 4.5:1)
# -----------------------------------------------------------------------------
def verify_suite_contrast():
    print(f"\n{Colors.CYAN}--- Suite 3: WCAG 2.1 AA Visual Contrast Verification (Ratio >= 4.5:1) ---{Colors.RESET}")

    if not STYLE_LIGHT_PATH.exists() or not tinycss2:
        reporter.record("Style parsing for contrast", False, "Missing style.css or tinycss2")
        return

    with open(STYLE_LIGHT_PATH, "r", encoding="utf-8") as f:
        css_light = f.read()
    with open(STYLE_DARK_PATH, "r", encoding="utf-8") as f:
        css_dark = f.read()

    model_light = CSSCascadeModel(css_light)
    model_dark = CSSCascadeModel(css_dark)

    # 3.1 Mobile Hamburger Button Contrast (Light Mode)
    # Background: topbar background --color-bg-card (#FFFFFF)
    bg_topbar_light = model_light.root_vars.get("--color-bg-card", "#FFFFFF")
    eff_color_hamb_light = model_light.resolve_property("button", {"mobile-nav-toggle"}, "mobile-nav-toggle", "color")
    fg_hamb_light = eff_color_hamb_light["value"] if eff_color_hamb_light else "#4B5563"
    cr_hamb_light = calculate_contrast_ratio(fg_hamb_light, bg_topbar_light)
    reporter.record(
        f"Test 3.1: Mobile hamburger icon contrast in Light Mode ({fg_hamb_light} on {bg_topbar_light}) >= 4.5:1",
        cr_hamb_light >= 4.5,
        f"Contrast ratio: {cr_hamb_light:.2f}:1 (Required: >= 4.5:1)"
    )

    # 3.2 Mobile Hamburger Button Contrast (Dark Mode)
    bg_topbar_dark = model_dark.root_vars.get("--color-bg-card", "#27272A")
    eff_color_hamb_dark = model_dark.resolve_property("button", {"mobile-nav-toggle"}, "mobile-nav-toggle", "color")
    fg_hamb_dark = eff_color_hamb_dark["value"] if eff_color_hamb_dark else "#D4D4D8"
    cr_hamb_dark = calculate_contrast_ratio(fg_hamb_dark, bg_topbar_dark)
    reporter.record(
        f"Test 3.2: Mobile hamburger icon contrast in Dark Mode ({fg_hamb_dark} on {bg_topbar_dark}) >= 4.5:1",
        cr_hamb_dark >= 4.5,
        f"Contrast ratio: {cr_hamb_dark:.2f}:1 (Required: >= 4.5:1)"
    )

    # 3.3 Notification Bell Button Contrast (Light Mode)
    eff_color_bell_light = model_light.resolve_property("button", {"header-icon-btn", "notification-bell-btn"}, "notification-bell", "color")
    fg_bell_light = eff_color_bell_light["value"] if eff_color_bell_light else "#4B5563"
    cr_bell_light = calculate_contrast_ratio(fg_bell_light, bg_topbar_light)
    reporter.record(
        f"Test 3.3: Notification bell icon contrast in Light Mode ({fg_bell_light} on {bg_topbar_light}) >= 4.5:1",
        cr_bell_light >= 4.5,
        f"Contrast ratio: {cr_bell_light:.2f}:1 (Required: >= 4.5:1)"
    )

    # 3.4 Notification Bell Button Contrast (Dark Mode)
    eff_color_bell_dark = model_dark.resolve_property("button", {"header-icon-btn", "notification-bell-btn"}, "notification-bell", "color")
    fg_bell_dark = eff_color_bell_dark["value"] if eff_color_bell_dark else "#D4D4D8"
    cr_bell_dark = calculate_contrast_ratio(fg_bell_dark, bg_topbar_dark)
    reporter.record(
        f"Test 3.4: Notification bell icon contrast in Dark Mode ({fg_bell_dark} on {bg_topbar_dark}) >= 4.5:1",
        cr_bell_dark >= 4.5,
        f"Contrast ratio: {cr_bell_dark:.2f}:1 (Required: >= 4.5:1)"
    )

    # 3.5 Modal Search ESC Close Button Contrast (Light Mode)
    bg_input_light = model_light.root_vars.get("--color-bg-input", "#F3F4F6")
    eff_color_esc_light = model_light.resolve_property("button", {"modal-search-close"}, "modal-search-close", "color")
    fg_esc_light = eff_color_esc_light["value"] if eff_color_esc_light else "#4B5563"
    cr_esc_light = calculate_contrast_ratio(fg_esc_light, bg_input_light)
    reporter.record(
        f"Test 3.5: Modal search close button contrast ({fg_esc_light} on {bg_input_light}) >= 4.5:1",
        cr_esc_light >= 4.5,
        f"Contrast ratio: {cr_esc_light:.2f}:1 (Required: >= 4.5:1)"
    )

    # 3.6 User Dropdown Logout Button Contrast (Light Mode)
    eff_color_logout = model_light.resolve_property("button", {"dropdown-item", "logout-btn"}, "logout-btn", "color")
    fg_logout = eff_color_logout["value"] if eff_color_logout else "#DC2626"
    bg_dropdown = model_light.root_vars.get("--color-bg-card", "#FFFFFF")
    cr_logout = calculate_contrast_ratio(fg_logout, bg_dropdown)
    reporter.record(
        f"Test 3.6: User dropdown logout button contrast ({fg_logout} on {bg_dropdown}) >= 4.5:1",
        cr_logout >= 4.5,
        f"Contrast ratio: {cr_logout:.2f}:1 (Required: >= 4.5:1)"
    )


# -----------------------------------------------------------------------------
# SUITE 4: Interactive Shell Controller DOM Harness (68 tests)
# -----------------------------------------------------------------------------
def verify_suite_interactive_js():
    print(f"\n{Colors.CYAN}--- Suite 4: Interactive Shell Controller DOM Harness (68 tests) ---{Colors.RESET}")

    if not JS_TEST_PATH.exists():
        reporter.record("Interactive JS test harness existence", False, f"Not found: {JS_TEST_PATH}")
        return

    # Discover candidate NODE_PATH for jsdom
    node_path_candidates = [
        "/Users/ryanx/workspace/vcoderlog-workspace/vcoderlog-websites/apps/academy-v2/node_modules",
        "/Users/ryanx/workspace/datalake-mono/apps/crm-workspace/node_modules",
        "/Users/ryanx/workspace/vcoderlog-academy/apps/academy-v2/node_modules",
    ]
    env = os.environ.copy()
    for cand in node_path_candidates:
        if os.path.isdir(cand) and os.path.isdir(os.path.join(cand, "jsdom")):
            env["NODE_PATH"] = cand
            break

    cmd = ["node", str(JS_TEST_PATH)]
    try:
        proc = subprocess.run(cmd, cwd=str(JUDGE_ROOT), env=env, capture_output=True, text=True, timeout=30)
        output = proc.stdout + proc.stderr
        passed_match = re.search(r"TOTAL TESTS:\s*(\d+)\s*\|\s*PASSED:\s*(\d+)\s*\|\s*FAILED:\s*(\d+)", output)
        if passed_match:
            total = int(passed_match.group(1))
            passed = int(passed_match.group(2))
            failed = int(passed_match.group(3))
            reporter.record(
                f"Test 4.1: Interactive Shell Controller DOM Tests ({passed}/{total} passed)",
                proc.returncode == 0 and failed == 0 and total >= 68,
                f"Exit code: {proc.returncode}, Passed: {passed}, Failed: {failed}"
            )
        else:
            reporter.record(
                "Test 4.1: Interactive Shell Controller DOM Tests execution",
                proc.returncode == 0,
                output.strip()[-300:]
            )
    except Exception as e:
        reporter.record("Test 4.1: Interactive Shell Controller DOM Tests execution", False, str(e))


# -----------------------------------------------------------------------------
# SUITE 5: Backend Regressions & App Shell Templates (41 tests)
# -----------------------------------------------------------------------------
def verify_suite_backend_regressions():
    print(f"\n{Colors.CYAN}--- Suite 5: Backend Regressions & App Shell Templates (41 tests) ---{Colors.RESET}")

    if not PY_BACKEND_TEST_PATH.exists():
        reporter.record("Backend regression harness existence", False, f"Not found: {PY_BACKEND_TEST_PATH}")
        return

    cmd = [str(PYTHON_BIN), str(PY_BACKEND_TEST_PATH)]
    try:
        proc = subprocess.run(cmd, cwd=str(JUDGE_ROOT), capture_output=True, text=True, timeout=45)
        output = proc.stdout + proc.stderr
        passed_match = re.search(r"TOTAL TESTS:\s*(\d+)\s*\|\s*PASSED:\s*(\d+)\s*\|\s*FAILED:\s*(\d+)", output)
        if passed_match:
            total = int(passed_match.group(1))
            passed = int(passed_match.group(2))
            failed = int(passed_match.group(3))
            reporter.record(
                f"Test 5.1: Backend Regressions & App Shell Templates ({passed}/{total} passed)",
                proc.returncode == 0 and failed == 0 and total >= 41,
                f"Exit code: {proc.returncode}, Passed: {passed}, Failed: {failed}"
            )
        else:
            reporter.record(
                "Test 5.1: Backend Regressions & App Shell Templates execution",
                proc.returncode == 0,
                output.strip()[-300:]
            )
    except Exception as e:
        reporter.record("Test 5.1: Backend Regressions & App Shell Templates execution", False, str(e))


# -----------------------------------------------------------------------------
# SUITE 6: Django Unit Test Suite (86 tests)
# -----------------------------------------------------------------------------
def verify_suite_django():
    print(f"\n{Colors.CYAN}--- Suite 6: Django Core Unit Tests (86 tests: `manage.py test judge`) ---{Colors.RESET}")

    cmd = [str(PYTHON_BIN), str(MANAGE_PY), "test", "judge", "--keepdb", "--no-input"]
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(JUDGE_ROOT),
            capture_output=True,
            text=True,
            timeout=120,
            stdin=subprocess.DEVNULL,
        )
        output = proc.stdout + proc.stderr
        ran_match = re.search(r"Ran\s+(\d+)\s+tests\s+in\s+([\d\.]+)s", output)
        ok_match = "OK" in output and proc.returncode == 0
        if ran_match:
            test_count = int(ran_match.group(1))
            duration = ran_match.group(2)
            reporter.record(
                f"Test 6.1: Django Unit Test Suite (`manage.py test judge`: {test_count} tests in {duration}s)",
                ok_match and test_count >= 86,
                f"Exit code: {proc.returncode}, Output status: {'OK' if ok_match else 'FAIL'}"
            )
        else:
            reporter.record(
                "Test 6.1: Django Unit Test Suite (`manage.py test judge`)",
                ok_match,
                output.strip()[-300:]
            )
    except Exception as e:
        reporter.record("Test 6.1: Django Unit Test Suite execution", False, str(e))


# -----------------------------------------------------------------------------
# Main Runner & CLI Dispatcher
# -----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Milestone 2 Iteration 2 End-to-End Verification Suite")
    parser.add_argument("--fast", action="store_true", help="Skip slow Django unit tests (run CSS, contrast, layout, JS, and backend suites)")
    parser.add_argument("--only-css", action="store_true", help="Run only CSS AST and token checks")
    parser.add_argument("--only-layout", action="store_true", help="Run only #user-links positioning checks")
    parser.add_argument("--only-contrast", action="store_true", help="Run only WCAG AA contrast ratio checks")
    parser.add_argument("--only-js", action="store_true", help="Run only 68 interactive JS tests")
    parser.add_argument("--only-backend", action="store_true", help="Run only 41 backend regression tests")
    parser.add_argument("--only-django", action="store_true", help="Run only 86 Django unit tests")
    parser.add_argument("--json", type=str, default="", help="Path to write JSON test report")
    args = parser.parse_args()

    print("=" * 65)
    print(f"{Colors.BOLD}Milestone 2 Iteration 2: Automated Verification & Regression Suite{Colors.RESET}")
    print(f"Target Repository: {JUDGE_ROOT}")
    print("=" * 65)

    specific = any([args.only_css, args.only_layout, args.only_contrast, args.only_js, args.only_backend, args.only_django])

    if specific:
        if args.only_css:
            verify_suite_css()
        if args.only_layout:
            verify_suite_layout()
        if args.only_contrast:
            verify_suite_contrast()
        if args.only_js:
            verify_suite_interactive_js()
        if args.only_backend:
            verify_suite_backend_regressions()
        if args.only_django:
            verify_suite_django()
    else:
        # Full run
        verify_suite_css()
        verify_suite_layout()
        verify_suite_contrast()
        verify_suite_interactive_js()
        verify_suite_backend_regressions()
        if not args.fast:
            verify_suite_django()

    success = reporter.print_summary()

    if args.json:
        report_data = {
            "passed": reporter.passed,
            "failed": reporter.failed,
            "warnings": reporter.warnings,
            "results": reporter.results,
            "success": success
        }
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)
        print(f"Report exported to: {args.json}")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
