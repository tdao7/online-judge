#!/usr/bin/env python3
"""
Adversarial DOM Cleanliness & Layout Stress Verification Harness
Milestone 1 Challenger 1 (DOM Cleanliness & Layout Stress Challenger)

This test suite aggressively probes rendered HTML across all primary and secondary routes,
verifying:
1. Strict absence of legacy macOS floating-window, wallpaper, and traffic light tokens.
2. Positive presence and DOM structural placement of the enterprise app-navbar, app-main,
   top-nav-links, and mobile-nav-toggle.
3. Edge-case scenarios across anonymous, authenticated, and staff sessions, filter query params,
   and auth workspaces.
"""

import os
import sys
import re
import json
from pathlib import Path

# Setup Django environment
JUDGE_ROOT = Path(__file__).resolve().parent.parent
if str(JUDGE_ROOT) not in sys.path:
    sys.path.insert(0, str(JUDGE_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')
import django
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from judge.models import Profile, Language, Problem, Contest

User = get_user_model()

PRIMARY_ENDPOINTS = [
    '/',
    '/problems/',
    '/problem/aplusb',
    '/submissions/',
    '/contests/',
    '/users/',
    '/user/tourist',
    '/accounts/login/',
    '/accounts/register/',
]

SECONDARY_ENDPOINTS = [
    '/accounts/password/reset/',
    '/problem/aplusb/submit',
    '/submissions/?problem=aplusb',
    '/contests/?tag=all',
    '/users/?search=tourist',
    '/problem/array_reconstruction',
]

FORBIDDEN_PATTERNS = [
    r'desktop-wallpaper',
    r'mac-app-window',
    r'mac-window-topbar',
    r'mac-window-body',
    r'mac-window',
    r'traffic-lights',
    r'traffic-light',
    r'traffic-red',
    r'traffic-yellow',
    r'traffic-green',
    r'traffic-close',
    r'traffic-minimize',
    r'traffic-maximize',
    r'mac-modal-backdrop',
    r'mac-modal-dialog',
    r'radial-gradient\(circle at 50% 20%',
]

REQUIRED_SHELL_TOKENS = [
    'app-navbar',
    'app-main',
    'top-nav-links',
    'mobile-nav-toggle',
]

class AdversarialDomTester:
    def __init__(self):
        self.client_anon = Client()
        self.client_auth = Client()
        self.client_staff = Client()
        
        # Ensure test users and profiles
        self.test_user, _ = User.objects.get_or_create(
            username='tourist_stress',
            defaults={'email': 'tourist_stress@example.com'}
        )
        self.test_user.set_password('pw12345')
        self.test_user.save()
        Profile.objects.get_or_create(user=self.test_user)

        self.staff_user, _ = User.objects.get_or_create(
            username='staff_stress',
            defaults={'email': 'staff_stress@example.com', 'is_staff': True}
        )
        self.staff_user.set_password('pw12345')
        self.staff_user.save()
        Profile.objects.get_or_create(user=self.staff_user)

        self.client_auth.force_login(self.test_user)
        self.client_staff.force_login(self.staff_user)

        self.results = []
        self.total_assertions = 0
        self.passed_assertions = 0
        self.failed_assertions = 0

    def assert_condition(self, condition, test_name, detail=""):
        self.total_assertions += 1
        if condition:
            self.passed_assertions += 1
            print(f"  ✔ PASS: {test_name}")
            return True
        else:
            self.failed_assertions += 1
            print(f"  ✖ FAIL: {test_name} - {detail}")
            return False

    def test_endpoint(self, client, client_label, endpoint):
        print(f"\n--- Testing Endpoint: {endpoint} [{client_label}] ---")
        response = client.get(endpoint, follow=True)
        status_code = response.status_code
        content = response.content.decode('utf-8', errors='replace')

        status_ok = self.assert_condition(
            status_code == 200,
            f"{endpoint} [{client_label}] HTTP Status 200",
            f"Returned {status_code}"
        )

        endpoint_result = {
            'endpoint': endpoint,
            'client': client_label,
            'status_code': status_code,
            'forbidden_matches': {},
            'required_tokens': {},
            'structural_checks': {},
        }

        # 1. Forbidden Tokens Check
        for pat in FORBIDDEN_PATTERNS:
            regex = re.compile(pat, re.IGNORECASE)
            matches = regex.findall(content)
            match_count = len(matches)
            endpoint_result['forbidden_matches'][pat] = match_count
            self.assert_condition(
                match_count == 0,
                f"{endpoint} [{client_label}] ZERO '{pat}'",
                f"Found {match_count} occurrences"
            )

        # 2. Required Shell Tokens (for standard pages using base.html)
        # Note: Auth pages or standalone pages may or may not use full top-nav
        is_auth_page = '/accounts/' in endpoint
        for req in REQUIRED_SHELL_TOKENS:
            token_present = req in content
            endpoint_result['required_tokens'][req] = token_present
            if not is_auth_page or req in ['app-main', 'app-navbar']:
                self.assert_condition(
                    token_present,
                    f"{endpoint} [{client_label}] Presence of '{req}'",
                    f"'{req}' missing from rendered HTML"
                )

        # 3. Structural checks
        # Verify app-navbar is NOT inside app-main
        navbar_pos = content.find('id="app-navbar"')
        if navbar_pos == -1:
            navbar_pos = content.find('class="app-navbar"')
        main_pos = content.find('id="app-main"')
        if main_pos == -1:
            main_pos = content.find('class="app-main"')

        if navbar_pos != -1 and main_pos != -1:
            navbar_before_main = navbar_pos < main_pos
            endpoint_result['structural_checks']['navbar_before_main'] = navbar_before_main
            self.assert_condition(
                navbar_before_main,
                f"{endpoint} [{client_label}] app-navbar precedes app-main in DOM hierarchy"
            )

        # Verify no wrapper enclosing app-navbar with fake desktop styling
        # Search for any outer div containing 'desktop' or 'wallpaper' in class before navbar
        if navbar_pos != -1:
            pre_navbar = content[:navbar_pos]
            has_desktop_parent = 'desktop' in pre_navbar.lower() and ('wrapper' in pre_navbar.lower() or 'wallpaper' in pre_navbar.lower())
            # Check specifically for unclosed tags with desktop
            endpoint_result['structural_checks']['no_desktop_wrapper'] = not has_desktop_parent
            self.assert_condition(
                not has_desktop_parent,
                f"{endpoint} [{client_label}] app-navbar is top-level (no desktop outer container)"
            )

        # Check viewport meta tag presence
        viewport_present = bool(re.search(r'<meta[^>]+name=["\']viewport["\']', content, re.IGNORECASE))
        endpoint_result['structural_checks']['viewport_present'] = viewport_present
        self.assert_condition(
            viewport_present,
            f"{endpoint} [{client_label}] Responsive viewport meta tag present"
        )

        self.results.append(endpoint_result)

    def run_all(self):
        print("=====================================================================")
        print("MILSTONE 1 ADVERSARIAL DOM CLEANLINESS & LAYOUT STRESS SUITE")
        print("=====================================================================")

        # Run Primary Endpoints (Anonymous)
        print("\n=== [PHASE 1] PRIMARY ENDPOINTS (ANONYMOUS USER) ===")
        for ep in PRIMARY_ENDPOINTS:
            self.test_endpoint(self.client_anon, "Anonymous", ep)

        # Run Primary Endpoints (Authenticated)
        print("\n=== [PHASE 2] PRIMARY ENDPOINTS (AUTHENTICATED USER) ===")
        for ep in PRIMARY_ENDPOINTS:
            self.test_endpoint(self.client_auth, "Authenticated", ep)

        # Run Staff Session on Key Routes
        print("\n=== [PHASE 3] STAFF SESSION ON KEY ROUTES ===")
        for ep in ['/', '/problems/', '/submissions/', '/users/']:
            self.test_endpoint(self.client_staff, "Staff", ep)

        # Run Secondary / Stress Endpoints
        print("\n=== [PHASE 4] SECONDARY & FILTER STRESS ROUTES ===")
        for ep in SECONDARY_ENDPOINTS:
            self.test_endpoint(self.client_auth, "Authenticated-Filtered", ep)

        # Summary
        print("\n=====================================================================")
        print(f"ADVERSARIAL DOM AUDIT SUMMARY: {self.passed_assertions}/{self.total_assertions} Passed")
        print(f"Failed Assertions: {self.failed_assertions}")
        print("=====================================================================")

        # Save results to scripts/adversarial_dom_results.json
        output_file = JUDGE_ROOT / 'scripts' / 'adversarial_dom_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_assertions': self.total_assertions,
                'passed_assertions': self.passed_assertions,
                'failed_assertions': self.failed_assertions,
                'results': self.results,
            }, f, indent=2)
        print(f"Detailed JSON results written to {output_file}")

        return self.failed_assertions == 0

if __name__ == '__main__':
    tester = AdversarialDomTester()
    success = tester.run_all()
    sys.exit(0 if success else 1)
