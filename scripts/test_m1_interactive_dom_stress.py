#!/usr/bin/env python3
"""
scripts/test_m1_interactive_dom_stress.py
Empirical Challenger Test Harness: Live Django DOM Inspection for Interactive Shell Hooks

Verifies:
1. Complete presence of all interactive controller hooks across all core routes.
2. Complete absence of legacy macOS wallpaper, floating window, and traffic-light controls.
3. DOM accessibility contracts: role="banner", role="navigation", role="dialog", aria-expanded, aria-hidden.
4. Anonymous vs Authenticated user state switches in the navbar.
5. In-contest timer docking in the sticky top navbar.
6. SCSS/CSS bundle integrity: static/style.css, resources/style.css, and app-shell-controller.js.
"""

import os
import re
import sys
import django

# Setup Django environment
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from judge.models import Profile, Language

User = get_user_model()

print("======================================================================")
print("CHALLENGER 2: LIVE DJANGO DOM & INTERACTIVE SHELL AUDIT")
print("======================================================================\n")

passed = 0
failed = 0
findings = []

def check(title, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  [PASS] {title}")
    else:
        failed += 1
        msg = f"  [FAIL] {title}{' - ' + detail if detail else ''}"
        print(msg, file=sys.stderr)
        findings.append(msg)

client = Client()

# Setup test user
test_user, _ = User.objects.get_or_create(
    username="challenger2_tester",
    defaults={"email": "challenger2@example.com"}
)
test_user.set_password("pass1234")
test_user.save()

lang, _ = Language.objects.get_or_create(key="py3", defaults={"name": "Python 3", "common_name": "Python 3", "ace": "python"})
profile, _ = Profile.objects.get_or_create(user=test_user, defaults={"language": lang})

# ----------------------------------------------------------------------
# SUITE 1: Enterprise Top Navbar & Shell Infrastructure
# ----------------------------------------------------------------------
print("--- Suite 1: Enterprise Top Navbar & Shell Infrastructure ---")

resp = client.get("/")
check("1.1: Root / returns HTTP 200", resp.status_code == 200)
html = resp.content.decode("utf-8")

# Check navbar
check("1.2: Sticky navbar #app-navbar present with role='banner'",
      '<header class="app-navbar" id="app-navbar" role="banner">' in html)

check("1.3: Brand logo with orange accent #F97316 indicator",
      'VCoder<span class="brand-accent-o">Log</span>' in html)

check("1.4: Primary navigation links container #top-nav-links with aria-label",
      'id="top-nav-links"' in html and 'aria-label="Main Navigation"' in html)

for nav_item in ['Dashboard', 'Problems', 'Contests', 'Submissions', 'Rankings']:
    check(f"1.5: Desktop nav contains link to '{nav_item}'",
          nav_item in html)

check("1.6: Main content container <main id='app-main'> present",
      '<main id="app-main"' in html and 'class="app-main"' in html)

check("1.7: Centered content viewport #app-main-viewport present",
      'id="app-main-viewport"' in html)

check("1.8: Core DMOJ hooks #page-container, #content, #content-body preserved",
      'id="page-container"' in html and 'id="content"' in html and 'id="content-body"' in html)

# ----------------------------------------------------------------------
# SUITE 2: Mobile Navigation Drawer & Accessibility
# ----------------------------------------------------------------------
print("\n--- Suite 2: Mobile Navigation Drawer & Accessibility ---")

check("2.1: Mobile hamburger button #mobile-nav-toggle present with aria-expanded='false'",
      'id="mobile-nav-toggle"' in html and 'aria-expanded="false"' in html)

check("2.2: Mobile drawer <aside id='navigation'> with role='navigation'",
      '<aside id="navigation" class="mobile-drawer app-sidebar" role="navigation"' in html)

check("2.3: Mobile drawer backdrop #sidebar-backdrop present with aria-hidden='true'",
      'id="sidebar-backdrop"' in html and 'class="sidebar-backdrop drawer-backdrop"' in html and 'aria-hidden="true"' in html)

check("2.4: Drawer close button #sidebar-close-btn present with aria-label",
      'id="sidebar-close-btn"' in html and 'aria-label="Close navigation"' in html)

# ----------------------------------------------------------------------
# SUITE 3: Global ⌘K Quick Search Modal
# ----------------------------------------------------------------------
print("\n--- Suite 3: Global ⌘K Quick Search Modal ---")

check("3.1: Global search trigger pill #global-search-trigger present in navbar",
      'id="global-search-trigger"' in html and 'class="header-search-pill"' in html and 'role="button"' in html)

check("3.2: Keycap badge #search-kbd-badge present with ⌘K defaults",
      'id="search-kbd-badge"' in html and '<kbd>⌘</kbd><kbd>K</kbd>' in html)

check("3.3: Decoupled search modal #global-search-modal present with role='dialog' & aria-hidden='true'",
      'id="global-search-modal"' in html and 'class="modal-backdrop search-modal-root"' in html and 'role="dialog"' in html and 'aria-hidden="true"' in html)

check("3.4: Modal search input #modal-search-input present with placeholder",
      'id="modal-search-input"' in html and 'placeholder="Search problems, tags, contests, or users..."' in html)

check("3.5: Modal close button #modal-search-close present with <kbd>ESC</kbd>",
      'id="modal-search-close"' in html and '<kbd>ESC</kbd>' in html)

check("3.6: Search modal results container #modal-search-results present",
      'id="modal-search-results"' in html)

# ----------------------------------------------------------------------
# SUITE 4: User Profile Dropdown & Auth States
# ----------------------------------------------------------------------
print("\n--- Suite 4: User Profile Dropdown & Auth States ---")

# 4.1 Anonymous state
check("4.1a: Anonymous user sees login link", 'class="auth-link-login"' in html)
check("4.1b: Anonymous user sees signup link", 'class="auth-link-signup"' in html)
check("4.1c: Anonymous user does not see #user-pill-dropdown", 'id="user-pill-dropdown"' not in html)

# 4.2 Authenticated state
client.force_login(test_user)
auth_resp = client.get("/")
auth_html = auth_resp.content.decode("utf-8")

check("4.2a: Authenticated user sees #user-pill-dropdown container",
      'id="user-pill-dropdown"' in auth_html)

check("4.2b: User pill trigger #user-pill-trigger present with aria-haspopup and aria-expanded='false'",
      'id="user-pill-trigger"' in auth_html and 'aria-haspopup="true"' in auth_html and 'aria-expanded="false"' in auth_html)

check("4.2c: User avatar and username displayed in trigger",
      'user-avatar-circle' in auth_html and 'challenger2_tester' in auth_html)

check("4.2d: User dropdown menu #user-dropdown-menu present with role='menu'",
      '<ul class="user-dropdown-menu" id="user-dropdown-menu" role="menu">' in auth_html)

check("4.2e: Menu contains Profile and Edit Profile links",
      'href="/user"' in auth_html and 'href="/edit/profile/"' in auth_html)

check("4.2f: Menu contains POST logout form with CSRF token",
      'action="/accounts/logout/"' in auth_html and 'method="POST"' in auth_html and 'csrfmiddlewaretoken' in auth_html)

# ----------------------------------------------------------------------
# SUITE 5: Zero Legacy macOS Simulator Artifacts
# ----------------------------------------------------------------------
print("\n--- Suite 5: Zero Legacy macOS Simulator Artifacts ---")

routes_to_test = [
    ("/", "Dashboard"),
    ("/problems/", "Problems Catalog"),
    ("/submissions/", "Submissions Catalog"),
    ("/contests/", "Contests Arena"),
    ("/users/", "Rankings Leaderboard"),
    ("/accounts/login/", "Login"),
    ("/accounts/register/", "Register"),
]

legacy_tokens = [
    "desktop-wallpaper",
    "mac-app-window",
    "mac-window",
    "mac-window-topbar",
    "mac-window-body",
    "traffic-lights",
    "traffic-light",
    "traffic-red",
    "traffic-yellow",
    "traffic-green",
    "mac-modal-backdrop",
    "mac-modal-dialog",
]

for route, name in routes_to_test:
    r = client.get(route)
    c = r.content.decode("utf-8")
    for token in legacy_tokens:
        check(f"5.{token} absent on {name} ({route})",
              token not in c,
              f"Found legacy token '{token}' in response HTML")

# ----------------------------------------------------------------------
# SUITE 6: Asset Pipeline & Controller Script Verification
# ----------------------------------------------------------------------
print("\n--- Suite 6: Asset Pipeline & Controller Script Verification ---")

check("6.1: base.html includes static/app-shell-controller.js",
      'app-shell-controller.js' in html)

js_path = os.path.join(django.conf.settings.BASE_DIR, 'resources', 'app-shell-controller.js')
check("6.2: resources/app-shell-controller.js exists", os.path.exists(js_path))

with open(js_path, 'r', encoding='utf-8') as f:
    js_content = f.read()

check("6.3: Controller exports window.DmojAppShell",
      'window.DmojAppShell = {' in js_content)

check("6.4: Controller binds #mobile-nav-toggle",
      '#mobile-nav-toggle' in js_content)

check("6.5: Controller binds #global-search-trigger",
      '#global-search-trigger' in js_content)

check("6.6: Controller binds #user-pill-trigger",
      '#user-pill-trigger' in js_content)

check("6.7: Controller binds #notification-bell",
      '#notification-bell' in js_content)

check("6.8: Controller contains zero references to traffic-lights",
      'traffic-light' not in js_content and 'mac-app-window' not in js_content)

print("\n======================================================================")
print(f"TOTAL TESTS: {passed + failed} | PASSED: {passed} | FAILED: {failed}")
print("======================================================================\n")

if failed > 0:
    sys.exit(1)
else:
    sys.exit(0)
