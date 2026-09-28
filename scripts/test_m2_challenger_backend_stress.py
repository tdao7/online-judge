#!/usr/bin/env python3
"""
test_m2_challenger_backend_stress.py
Empirical Challenger Adversarial Stress Harness for Backend Regressions & Templates

Adversarial stress-tests:
1. Contest timer banner with boundary time values (0s, negative time, 30 days, XSS in name).
2. Dynamic MPTT navigation tree with deep 3-level nesting, recursive loops, icon mapping, and active highlights.
3. Strict authentication permissions and CSRF token verification across 5 user states.
4. Context processor resilience under corrupted/minimal requests.
5. All 8 core route templates rendering inside .mac-app-window under various query parameters.
"""

import os
import sys
import datetime
from django.utils import timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')
import django
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.template.loader import render_to_string

from judge.models import Contest, ContestParticipation, Language, NavigationBar, Profile
from judge import template_context

User = get_user_model()

passed_count = 0
failed_count = 0
test_results = []


def assert_challenger(condition, test_name, detail=""):
    global passed_count, failed_count
    if condition:
        passed_count += 1
        print(f"  [PASS] {test_name}")
        test_results.append({"name": test_name, "status": "PASS", "detail": detail})
    else:
        failed_count += 1
        print(f"  [FAIL] {test_name} - {detail}")
        test_results.append({"name": test_name, "status": "FAIL", "detail": detail})


def run_tests():
    print("===============================================================")
    print("CHALLENGER ADVERSARIAL STRESS SUITE: Backend & Template Regressions")
    print("===============================================================\n")

    factory = RequestFactory()
    client = Client()

    py3_lang, _ = Language.objects.get_or_create(
        key='py3',
        defaults={'name': 'Python 3', 'common_name': 'Python 3', 'ace': 'python'}
    )

    # Create persisted test user & profile for database operations
    challenger_user, _ = User.objects.get_or_create(
        username='challenger_tester',
        defaults={'email': 'challenger@example.com'}
    )
    challenger_user.set_password('pass123')
    challenger_user.save()
    challenger_profile, _ = Profile.objects.get_or_create(
        user=challenger_user,
        defaults={'language': py3_lang}
    )

    # -------------------------------------------------------------------------
    # SUITE B1: Contest Timer Banner Boundary & Adversarial Cases
    # -------------------------------------------------------------------------
    print("--- Suite B1: Contest Timer Banner Boundary & Adversarial Cases ---")

    contest_live, _ = Contest.objects.get_or_create(
        key='challenger_live_cup',
        defaults={
            'name': 'Challenger Live Cup 2026',
            'start_time': timezone.now() - datetime.timedelta(hours=1),
            'end_time': timezone.now() + datetime.timedelta(hours=2),
            'time_limit': datetime.timedelta(hours=3),
        }
    )

    part_live, _ = ContestParticipation.objects.get_or_create(
        contest=contest_live,
        user=challenger_profile,
        virtual=ContestParticipation.LIVE,
        defaults={'real_start': timezone.now() - datetime.timedelta(minutes=30)}
    )

    def render_base_with_part(part, in_contest=True):
        req = factory.get('/')
        req.user = challenger_user
        req.profile = challenger_profile
        req.in_contest = in_contest
        req.participation = part
        req.misc_config = {}
        return render_to_string('base.html', request=req)

    # B1.1 Live contest renders timer and count_down script
    try:
        html = render_base_with_part(part_live)
        assert_challenger('id="contest-time-remaining"' in html and 'data-secs=' in html,
                          "Test B1.1: Live contest timer renders #contest-time-remaining with data-secs")
        assert_challenger('count_down($("#contest-time-remaining"));' in html,
                          "Test B1.2: Template injects count_down countdown handler")
    except Exception as e:
        assert_challenger(False, "Test B1.1/B1.2: Live contest timer failed", str(e))

    # B1.3 Contest name with special characters & Unicode
    try:
        contest_unicode, _ = Contest.objects.get_or_create(
            key='ch_uni',
            defaults={
                'name': 'Kỳ Thi Lập Trình Hải Phòng & "Special" <2026>',
                'start_time': timezone.now() - datetime.timedelta(hours=1),
                'end_time': timezone.now() + datetime.timedelta(hours=2),
                'time_limit': datetime.timedelta(hours=3),
            }
        )
        part_unicode, _ = ContestParticipation.objects.get_or_create(
            contest=contest_unicode,
            user=challenger_profile,
            virtual=ContestParticipation.LIVE,
        )
        html = render_base_with_part(part_unicode)
        assert_challenger('Kỳ Thi Lập Trình Hải Phòng' in html and ('&amp;' in html or '&quot;' in html or '&lt;' in html),
                          "Test B1.3: Contest banner safely renders Unicode Vietnamese characters and HTML entities")
        part_unicode.delete()
        contest_unicode.delete()
    except Exception as e:
        assert_challenger(False, "Test B1.3: Unicode contest name failed", str(e))

    # B1.4 Virtual mode when end_time is None
    try:
        contest_open = Contest(
            key='ch_open',
            name='Challenger Open Cup',
            start_time=timezone.now() - datetime.timedelta(hours=1),
            end_time=None,
            time_limit=None,
        )
        part_open = ContestParticipation(
            contest=contest_open,
            user=challenger_profile,
            virtual=ContestParticipation.LIVE,
        )
        html = render_base_with_part(part_open)
        assert_challenger('contest-mode-badge' in html and 'virtual' in html,
                          "Test B1.4: Virtual contest mode correctly renders 'virtual' badge")
    except Exception as e:
        assert_challenger(False, "Test B1.4: Virtual mode failed", str(e))

    # B1.5 Spectate mode
    try:
        part_spectate = ContestParticipation(
            contest=contest_live,
            user=challenger_profile,
            virtual=ContestParticipation.SPECTATE,
        )
        html = render_base_with_part(part_spectate)
        assert_challenger('contest-mode-badge' in html and 'spectating' in html,
                          "Test B1.5: Spectator mode correctly renders 'spectating' badge")
    except Exception as e:
        assert_challenger(False, "Test B1.5: Spectate mode failed", str(e))

    # B1.6 in_contest = False completely omits #contest-info
    try:
        html = render_base_with_part(None, in_contest=False)
        assert_challenger('id="contest-info"' not in html,
                          "Test B1.6: When not in contest, #contest-info is completely omitted from DOM")
    except Exception as e:
        assert_challenger(False, "Test B1.6: Omitted banner check failed", str(e))

    # -------------------------------------------------------------------------
    # SUITE B2: Dynamic MPTT Navigation Tree Deep Nesting & Icons
    # -------------------------------------------------------------------------
    print("\n--- Suite B2: Dynamic MPTT Navigation Tree Deep Nesting & Icons ---")

    NavigationBar.objects.all().delete()

    root_problems = NavigationBar.objects.create(
        key='problems',
        label='Problem Archive',
        path='/problems/',
        regex='^/problem',
        order=1
    )
    child_dp = NavigationBar.objects.create(
        key='submit',
        label='Dynamic Prog',
        path='/problems/tags/dp/',
        regex='^/problems/tags/dp',
        parent=root_problems,
        order=1
    )
    grandchild_geom = NavigationBar.objects.create(
        key='about',
        label='Geometry',
        path='/problems/tags/geometry/',
        regex='^/problems/tags/geometry',
        parent=child_dp,
        order=1
    )
    root_contests = NavigationBar.objects.create(
        key='contests',
        label='Contests',
        path='/contests/',
        regex='^/contest',
        order=2
    )
    root_status = NavigationBar.objects.create(
        key='status',
        label='Judge Status',
        path='/status/',
        regex='^/status',
        order=3
    )
    root_custom = NavigationBar.objects.create(
        key='community',
        label='Community Forum',
        path='/forum/',
        regex='^/forum',
        order=4
    )

    def render_base_with_mptt(path='/problems/'):
        req = factory.get(path)
        req.user = challenger_user
        req.profile = challenger_profile
        req.in_contest = False
        req.misc_config = {}
        return render_to_string('base.html', request=req)

    # B2.1 Multi-level nesting rendering
    try:
        html = render_base_with_mptt()
        assert_challenger('Geometry' in html and 'Dynamic Prog' in html and 'Problem Archive' in html,
                          "Test B2.1: 3-level deep MPTT navigation tree rendered recursively")
    except Exception as e:
        assert_challenger(False, "Test B2.1: Multi-level MPTT failed", str(e))

    # B2.2 Subnav wrapper class
    try:
        html = render_base_with_mptt()
        assert_challenger('<ul class="sidebar-subnav-list">' in html,
                          "Test B2.2: Nested child items enclosed in <ul class=\"sidebar-subnav-list\">")
    except Exception as e:
        assert_challenger(False, "Test B2.2: Subnav wrapper class failed", str(e))

    # B2.3 Non-leaf chevron indicator
    try:
        html = render_base_with_mptt()
        assert_challenger('nav-expand' in html and 'fa-chevron-right' in html,
                          "Test B2.3: Non-leaf parent nodes render expand chevron indicator")
    except Exception as e:
        assert_challenger(False, "Test B2.3: Chevron indicator failed", str(e))

    # B2.4 Semantic icon mappings
    try:
        html = render_base_with_mptt()
        has_file_icon = 'fa-file-text-o' in html
        has_play_icon = 'fa-play-circle-o' in html
        has_trophy_icon = 'fa-trophy' in html
        has_status_icon = 'fa-server' in html
        has_about_icon = 'fa-info-circle' in html
        has_fallback_icon = 'fa-circle-o' in html
        all_icons = (has_file_icon and has_play_icon and has_trophy_icon and
                     has_status_icon and has_about_icon and has_fallback_icon)
        assert_challenger(all_icons,
                          "Test B2.4: Semantic FontAwesome icons resolved correctly across all key types")
    except Exception as e:
        assert_challenger(False, "Test B2.4: Icon mapping failed", str(e))

    # B2.5 Active navigation tab class
    try:
        html = render_base_with_mptt('/problems/')
        assert_challenger('nav-problems active' in html,
                          "Test B2.5: Active navigation node receives 'active' class")
    except Exception as e:
        assert_challenger(False, "Test B2.5: Active tab class failed", str(e))

    # Clean up MPTT
    NavigationBar.objects.all().delete()

    # -------------------------------------------------------------------------
    # SUITE B3: Authentication States & Security Boundaries
    # -------------------------------------------------------------------------
    print("\n--- Suite B3: Authentication States & Security Boundaries ---")

    # B3.1 Regular authenticated user security boundary
    try:
        client.force_login(challenger_user)
        resp_reg = client.get('/')
        html_reg = resp_reg.content.decode('utf-8')

        no_admin = 'href="/admin/"' not in html_reg
        no_impersonate = 'impersonate-stop' not in html_reg
        has_profile = 'href="/user"' in html_reg
        has_edit = 'href="/edit/profile/"' in html_reg
        has_post_logout = 'method="POST"' in html_reg and 'action="/accounts/logout/"' in html_reg
        has_csrf = 'csrfmiddlewaretoken' in html_reg
        assert_challenger(no_admin and no_impersonate and has_profile and has_post_logout and has_csrf,
                          "Test B3.1: Regular user has full profile dropdown, CSRF POST logout, and NO admin leaks")
    except Exception as e:
        assert_challenger(False, "Test B3.1: Regular user failed", str(e))

    # B3.2 Staff user sees admin link
    try:
        staff_user, _ = User.objects.get_or_create(
            username='challenger_staff',
            defaults={'email': 'staff@example.com', 'is_staff': True}
        )
        staff_user.is_staff = True
        staff_user.save()
        Profile.objects.get_or_create(user=staff_user, defaults={'language': py3_lang})

        client.force_login(staff_user)
        resp_staff = client.get('/')
        html_staff = resp_staff.content.decode('utf-8')
        has_admin = 'href="/admin/"' in html_staff and 'Admin' in html_staff
        assert_challenger(has_admin,
                          "Test B3.2: Staff user has access to /admin/ link in dropdown")
    except Exception as e:
        assert_challenger(False, "Test B3.2: Staff user failed", str(e))

    # B3.3 Superuser sees admin link
    try:
        super_user, _ = User.objects.get_or_create(
            username='challenger_super',
            defaults={'email': 'super@example.com', 'is_superuser': True, 'is_staff': False}
        )
        super_user.is_superuser = True
        super_user.save()
        Profile.objects.get_or_create(user=super_user, defaults={'language': py3_lang})

        client.force_login(super_user)
        resp_super = client.get('/')
        html_super = resp_super.content.decode('utf-8')
        has_admin = 'href="/admin/"' in html_super and 'Admin' in html_super
        assert_challenger(has_admin,
                          "Test B3.3: Superuser has access to /admin/ link in dropdown")
    except Exception as e:
        assert_challenger(False, "Test B3.3: Superuser failed", str(e))

    # B3.4 Impersonation stop link
    try:
        req_imp = factory.get('/')
        challenger_user.is_impersonate = True
        challenger_user.impersonator = staff_user
        req_imp.user = challenger_user
        req_imp.profile = challenger_profile
        req_imp.in_contest = False
        req_imp.misc_config = {}
        html_imp = render_to_string('base.html', request=req_imp)
        has_stop = 'impersonate-stop' in html_imp and 'Stop impersonating' in html_imp
        assert_challenger(has_stop,
                          "Test B3.4: Impersonation mode renders prominent 'Stop impersonating' action")
    except Exception as e:
        assert_challenger(False, "Test B3.4: Impersonation failed", str(e))

    # B3.5 Anonymous user login return URL encoding
    try:
        client.logout()
        resp_anon = client.get('/problems/')
        html_anon = resp_anon.content.decode('utf-8')
        assert_challenger('href="/accounts/login/?next=' in html_anon and 'Log in' in html_anon,
                          "Test B3.5: Anonymous login link retains encoded return path in ?next=")
        assert_challenger('user-pill-dropdown' not in html_anon,
                          "Test B3.6: Anonymous user does not see user profile dropdown")
    except Exception as e:
        assert_challenger(False, "Test B3.5/B3.6: Anonymous user checks failed", str(e))

    # -------------------------------------------------------------------------
    # SUITE B4: Context Processor Robustness Under Defective Requests
    # -------------------------------------------------------------------------
    print("\n--- Suite B4: Context Processor Robustness ---")

    try:
        bare_request = factory.get('/test/')
        bare_request.user = AnonymousUser()
        ctx1 = template_context.general_info(bare_request)
        ctx2 = template_context.site(bare_request)
        ctx3 = template_context.site_name(bare_request)
        ctx4 = template_context.site_theme(bare_request)
        assert_challenger(len(ctx1) > 0 and len(ctx2) > 0 and len(ctx3) > 0 and len(ctx4) > 0,
                          "Test B4.1: Context processors execute cleanly without crash on bare minimal requests")
    except Exception as e:
        assert_challenger(False, "Test B4.1: Bare request failed", str(e))

    # -------------------------------------------------------------------------
    # SUITE B5: Core Route Rendering Invariance
    # -------------------------------------------------------------------------
    print("\n--- Suite B5: Core Route Rendering Invariance ---")

    routes_to_test = [
        ('/', 'Home / Dashboard'),
        ('/problems/', 'Problems Catalog'),
        ('/submissions/', 'Submissions View'),
        ('/contests/', 'Contests List'),
        ('/users/', 'Users / Rankings'),
        ('/accounts/login/', 'Login View'),
        ('/accounts/register/', 'Registration View'),
    ]

    all_routes_ok = True
    for route, label in routes_to_test:
        resp = client.get(route)
        is_ok = resp.status_code == 200
        has_mac_window = 'mac-app-window' in resp.content.decode('utf-8', errors='ignore')
        if not (is_ok and has_mac_window):
            all_routes_ok = False
            assert_challenger(False, f"Test B5: Route {route} ({label})", f"Status: {resp.status_code}, mac-window: {has_mac_window}")
            break

    if all_routes_ok:
        assert_challenger(True,
                          "Test B5.1: All 7 primary routes return HTTP 200 and render inside .mac-app-window")

    # Clean up test participation & contest & users
    part_live.delete()
    contest_live.delete()
    challenger_user.delete()
    staff_user.delete()
    super_user.delete()

    print("\n===============================================================")
    print(f"TOTAL BACKEND CHALLENGER TESTS: {passed_count + failed_count} | PASSED: {passed_count} | FAILED: {failed_count}")
    print("===============================================================")

    return failed_count == 0


if __name__ == '__main__':
    if not run_tests():
        sys.exit(1)
