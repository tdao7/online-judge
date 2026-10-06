#!/usr/bin/env python3
"""
test_m2_backend_regressions.py
Empirical Challenger Test Harness for Milestone 2: Backend Regressions & App Shell Templates

Verifies:
1. Contest timer banner (#contest-info), time_remaining filter, and spectating/virtual modes.
2. Dynamic MPTT navigation tree rendering (root nodes and recursive child subnav).
3. Context processors execution and dictionary keys.
4. Anonymous, authenticated, staff, and impersonation user states & authentication links.
5. Core routes rendering within .mac-app-window.
"""

import os
import sys
import datetime
from django.utils import timezone

# Setup Django environment
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


def assert_test(condition, test_name, detail=""):
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
    print("RUNNING EMPIRICAL TESTS: Backend Regressions & App Shell Templates")
    print("===============================================================\n")

    factory = RequestFactory()
    client = Client()

    # -------------------------------------------------------------------------
    # SUITE 1: Context Processors Execution
    # -------------------------------------------------------------------------
    print("--- Suite 1: Context Processors Execution ---")
    request = factory.get('/')
    request.user = AnonymousUser()
    request.misc_config = {}

    # 1.1 general_info
    try:
        gen_info = template_context.general_info(request)
        assert_test('nav_bar' in gen_info and 'nav_tab' in gen_info and 'REGISTRATION_OPEN' in gen_info,
                    "Test 1.1: general_info context processor returns required keys")
    except Exception as e:
        assert_test(False, "Test 1.1: general_info context processor failed", str(e))

    # 1.2 site
    try:
        site_ctx = template_context.site(request)
        assert_test('site' in site_ctx, "Test 1.2: site context processor returns site")
    except Exception as e:
        assert_test(False, "Test 1.2: site context processor failed", str(e))

    # 1.3 misc_config
    try:
        misc_ctx = template_context.misc_config(request)
        assert_test('misc_config' in misc_ctx, "Test 1.3: misc_config context processor returns misc_config")
    except Exception as e:
        assert_test(False, "Test 1.3: misc_config context processor failed", str(e))

    # 1.4 site_name
    try:
        sn_ctx = template_context.site_name(request)
        assert_test('SITE_NAME' in sn_ctx and 'SITE_LONG_NAME' in sn_ctx,
                    "Test 1.4: site_name context processor returns site names")
    except Exception as e:
        assert_test(False, "Test 1.4: site_name context processor failed", str(e))

    # 1.5 site_theme
    try:
        st_ctx = template_context.site_theme(request)
        assert_test('DARK_STYLE_CSS' in st_ctx and 'LIGHT_STYLE_CSS' in st_ctx,
                    "Test 1.5: site_theme context processor returns style CSS paths")
    except Exception as e:
        assert_test(False, "Test 1.5: site_theme context processor failed", str(e))

    # 1.6 math_setting
    try:
        math_ctx = template_context.math_setting(request)
        assert_test('MATH_ENGINE' in math_ctx and 'caniuse' in math_ctx,
                    "Test 1.6: math_setting context processor returns MATH_ENGINE")
    except Exception as e:
        assert_test(False, "Test 1.6: math_setting context processor failed", str(e))

    # 1.7 comet_location
    try:
        comet_ctx = template_context.comet_location(request)
        assert_test('EVENT_DAEMON_LOCATION' in comet_ctx,
                    "Test 1.7: comet_location context processor returns daemon location")
    except Exception as e:
        assert_test(False, "Test 1.7: comet_location context processor failed", str(e))

    # 1.8 get_resource
    try:
        res_ctx = template_context.get_resource(request)
        assert_test('DMOJ_SCHEME' in res_ctx and 'FONTAWESOME_CSS' in res_ctx,
                    "Test 1.8: get_resource context processor returns resource paths")
    except Exception as e:
        assert_test(False, "Test 1.8: get_resource context processor failed", str(e))

    # -------------------------------------------------------------------------
    # SUITE 2: Core Routes HTTP 200 & App Shell Presence
    # -------------------------------------------------------------------------
    print("\n--- Suite 2: Core Routes HTTP 200 & App Shell Presence ---")
    core_routes = [
        ('/', 'Home/Dashboard'),
        ('/problems/', 'Problems Catalog'),
        ('/submissions/', 'Submissions List'),
        ('/contests/', 'Contests Overview'),
        ('/users/', 'Global Rankings'),
        ('/accounts/login/', 'Login Page'),
        ('/accounts/register/', 'Registration Page'),
        ('/accounts/password/reset/', 'Password Reset Page'),
    ]

    for route, label in core_routes:
        try:
            resp = client.get(route)
            content = resp.content.decode('utf-8')
            has_navbar = 'app-navbar' in content
            has_main = 'app-main' in content
            no_window = 'mac-app-window' not in content
            assert_test(resp.status_code == 200 and has_navbar and has_main and no_window,
                        f"Test 2.{core_routes.index((route, label))+1}: Route '{route}' ({label}) returns 200 inside app-navbar shell",
                        f"Status: {resp.status_code}, navbar: {has_navbar}")
        except Exception as e:
            assert_test(False, f"Test 2: Route '{route}' failed with exception", str(e))

    # -------------------------------------------------------------------------
    # SUITE 3: Authentication States & Profile Dropdown Navigation
    # -------------------------------------------------------------------------
    print("\n--- Suite 3: Authentication States & Profile Dropdown ---")
    # 3.1 Anonymous User
    anon_resp = client.get('/')
    anon_content = anon_resp.content.decode('utf-8')
    assert_test('anon-auth-links' in anon_content and '/accounts/login/' in anon_content,
                "Test 3.1a: Anonymous user sees login link")
    assert_test('/accounts/register/' in anon_content,
                "Test 3.1b: Anonymous user sees sign up link")
    assert_test('user-pill-dropdown' not in anon_content,
                "Test 3.1c: Anonymous user does not see user profile dropdown")

    # 3.2 Authenticated Regular User
    regular_user, _ = User.objects.get_or_create(
        username='challenger_regular_user',
        defaults={'email': 'reg@example.com'}
    )
    regular_user.set_password('pass123')
    regular_user.is_staff = False
    regular_user.is_superuser = False
    regular_user.save()
    py3_lang, _ = Language.objects.get_or_create(key='py3', defaults={'name': 'Python 3', 'common_name': 'Python 3', 'ace': 'python'})
    reg_profile, _ = Profile.objects.get_or_create(user=regular_user, defaults={'language': py3_lang})

    client.force_login(regular_user)
    auth_resp = client.get('/')
    auth_content = auth_resp.content.decode('utf-8')

    assert_test('user-pill-dropdown' in auth_content and 'challenger_regular_user' in auth_content,
                "Test 3.2a: Authenticated user sees username in user-pill-dropdown")
    assert_test('href="/user"' in auth_content and 'href="/edit/profile/"' in auth_content,
                "Test 3.2b: Authenticated user dropdown has Profile (/user) and Edit profile (/edit/profile/) links")
    assert_test('action="/accounts/logout/"' in auth_content and 'csrfmiddlewaretoken' in auth_content,
                "Test 3.2c: Authenticated user dropdown has POST logout form with CSRF token")
    assert_test('href="/admin/"' not in auth_content,
                "Test 3.2d: Non-staff authenticated user does NOT see admin link")

    # 3.3 Staff User
    staff_user, _ = User.objects.get_or_create(
        username='challenger_staff_user',
        defaults={'email': 'staff@example.com', 'is_staff': True}
    )
    staff_user.set_password('pass123')
    staff_user.is_staff = True
    staff_user.save()
    Profile.objects.get_or_create(user=staff_user, defaults={'language': py3_lang})

    client.force_login(staff_user)
    staff_resp = client.get('/')
    staff_content = staff_resp.content.decode('utf-8')
    assert_test('href="/admin/"' in staff_content and 'Admin' in staff_content,
                "Test 3.3: Staff user sees /admin/ link in profile dropdown")

    # 3.4 Impersonating User
    req_imp = factory.get('/')
    regular_user.is_impersonate = True
    regular_user.impersonator = staff_user
    req_imp.user = regular_user
    req_imp.profile = reg_profile
    req_imp.in_contest = False
    req_imp.misc_config = {}

    rendered_imp = render_to_string('base.html', request=req_imp)
    assert_test('impersonate-indicator' in rendered_imp and 'impersonate-stop' in rendered_imp,
                "Test 3.4: Impersonating user renders impersonate indicator badge and stop link")
    regular_user.is_impersonate = False

    # -------------------------------------------------------------------------
    # SUITE 4: DMOJ Contest Timer & Status Banner (#contest-info)
    # -------------------------------------------------------------------------
    print("\n--- Suite 4: DMOJ Contest Timer & Status Banner ---")
    # 4.1 When NOT in contest, #contest-info must not exist
    client.force_login(regular_user)
    no_contest_resp = client.get('/')
    assert_test('id="contest-info"' not in no_contest_resp.content.decode('utf-8'),
                "Test 4.1: #contest-info banner is absent when user is not in contest")

    # 4.2 In Contest: Active participation with end_time
    test_contest, _ = Contest.objects.get_or_create(
        key='test_challenge_cup',
        defaults={
            'name': 'Test Challenger Cup 2026',
            'start_time': timezone.now() - datetime.timedelta(hours=1),
            'end_time': timezone.now() + datetime.timedelta(hours=2),
            'time_limit': datetime.timedelta(hours=3),
        }
    )

    part_active, _ = ContestParticipation.objects.get_or_create(
        contest=test_contest,
        user=reg_profile,
        virtual=ContestParticipation.LIVE,
        defaults={
            'real_start': timezone.now() - datetime.timedelta(minutes=30),
        }
    )

    # Render base.html with in_contest=True simulating ContestMiddleware
    req_contest = factory.get('/')
    req_contest.user = regular_user
    req_contest.profile = reg_profile
    req_contest.in_contest = True
    req_contest.participation = part_active
    req_contest.misc_config = {}

    rendered_contest = render_to_string('base.html', request=req_contest)

    assert_test('id="contest-info"' in rendered_contest and 'contest-info-pill' in rendered_contest,
                "Test 4.2a: #contest-info pill is rendered when request.in_contest is True")
    assert_test('Test Challenger Cup 2026' in rendered_contest,
                "Test 4.2b: Contest name is correctly displayed in timer pill")
    assert_test('id="contest-time-remaining"' in rendered_contest and 'data-secs=' in rendered_contest,
                "Test 4.2c: #contest-time-remaining is rendered with data-secs attribute")
    assert_test('count_down($("#contest-time-remaining"));' in rendered_contest,
                "Test 4.2d: Head contains count_down JS invocation")
    assert_test('contest_timer_pos' in rendered_contest,
                "Test 4.2e: Head contains contest timer dragging and position persistence logic")

    # 4.3 In Contest: Spectating Mode
    part_spectate = ContestParticipation(
        contest=test_contest,
        user=reg_profile,
        virtual=ContestParticipation.SPECTATE,
    )
    req_spectate = factory.get('/')
    req_spectate.user = regular_user
    req_spectate.profile = reg_profile
    req_spectate.in_contest = True
    req_spectate.participation = part_spectate
    req_spectate.misc_config = {}

    rendered_spectate = render_to_string('base.html', request=req_spectate)
    assert_test('contest-mode-badge' in rendered_spectate and 'spectating' in rendered_spectate,
                "Test 4.3: Spectating mode renders 'spectating' contest-mode-badge")

    # 4.4 In Contest: Open contest with no end_time
    test_contest_no_end = Contest(
        key='test_open_cup',
        name='Open Cup',
        start_time=timezone.now() - datetime.timedelta(hours=1),
        end_time=None,
        time_limit=None,
    )
    part_open = ContestParticipation(
        contest=test_contest_no_end,
        user=reg_profile,
        virtual=ContestParticipation.LIVE,
    )
    req_virtual = factory.get('/')
    req_virtual.user = regular_user
    req_virtual.profile = reg_profile
    req_virtual.in_contest = True
    req_virtual.participation = part_open
    req_virtual.misc_config = {}

    rendered_virtual = render_to_string('base.html', request=req_virtual)
    assert_test('contest-mode-badge' in rendered_virtual and 'virtual' in rendered_virtual,
                "Test 4.4: Participation without end_time renders 'virtual' contest-mode-badge")

    # -------------------------------------------------------------------------
    # SUITE 5: Dynamic MPTT Navigation Tree
    # -------------------------------------------------------------------------
    print("\n--- Suite 5: Dynamic MPTT Navigation Tree ---")

    # 5.1 When NavigationBar is empty: fallback links render
    NavigationBar.objects.all().delete()
    req_no_mptt = factory.get('/')
    req_no_mptt.user = regular_user
    req_no_mptt.profile = reg_profile
    req_no_mptt.in_contest = False
    req_no_mptt.misc_config = {}

    rendered_no_mptt = render_to_string('base.html', request=req_no_mptt)
    assert_test('/problems/' in rendered_no_mptt and 'nav-problems' in rendered_no_mptt,
                "Test 5.1a: Fallback navigation includes Problems link")
    assert_test('/submissions/' in rendered_no_mptt and 'nav-submissions' in rendered_no_mptt,
                "Test 5.1b: Fallback navigation includes Submissions link")
    assert_test('/contests/' in rendered_no_mptt and 'nav-contests' in rendered_no_mptt,
                "Test 5.1c: Fallback navigation includes Contests link")
    assert_test('/users/' in rendered_no_mptt and 'nav-rankings' in rendered_no_mptt,
                "Test 5.1d: Fallback navigation includes Rankings link")

    # 5.2 When NavigationBar has root & nested child items (MPTT)
    root_problems = NavigationBar.objects.create(
        key='problems',
        label='Problem Archive',
        path='/problems/',
        regex='^/problem',
        order=1
    )
    root_contests = NavigationBar.objects.create(
        key='contests',
        label='Contests',
        path='/contests/',
        regex='^/contest',
        order=2
    )
    child_practice = NavigationBar.objects.create(
        key='practice',
        label='Practice Rounds',
        path='/contests/practice/',
        regex='^/contest/practice',
        parent=root_contests,
        order=1
    )

    req_mptt = factory.get('/problems/')
    req_mptt.user = regular_user
    req_mptt.profile = reg_profile
    req_mptt.in_contest = False
    req_mptt.misc_config = {}

    rendered_mptt = render_to_string('base.html', request=req_mptt)

    assert_test('Problem Archive' in rendered_mptt,
                "Test 5.2a: MPTT root item 'Problem Archive' rendered via mptt_tree")
    assert_test('fa-file-text-o' in rendered_mptt,
                "Test 5.2b: Problems item receives fa-file-text-o semantic icon")
    assert_test('Practice Rounds' in rendered_mptt,
                "Test 5.2c: MPTT child item 'Practice Rounds' rendered recursively")
    assert_test('sidebar-subnav-list' in rendered_mptt,
                "Test 5.2d: Child items wrapped inside <ul class=\"sidebar-subnav-list\">")

    # Clean up test navigation bar objects
    NavigationBar.objects.all().delete()

    # Clean up test contest & participation
    part_active.delete()
    test_contest.delete()

    print("\n===============================================================")
    print(f"TOTAL TESTS: {passed_count + failed_count} | PASSED: {passed_count} | FAILED: {failed_count}")
    print("===============================================================")

    return failed_count == 0


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
