import os
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.conf import settings

from judge.models import Profile, Language, Problem, ProblemGroup, ProblemType, Judge

User = get_user_model()


class Milestone2AppShellTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='tourist_test',
            email='tourist@example.com',
            password='securepassword123',
        )
        self.language, _ = Language.objects.get_or_create(
            key='py3',
            defaults={'name': 'Python 3', 'common_name': 'Python 3', 'ace': 'python'}
        )
        self.profile = Profile.objects.create(user=self.user, language=self.language)

    def test_desktop_wallpaper_and_mac_window_shell(self):
        """Verify wide desktop wallpaper container, floating window, and traffic light controls."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Wallpaper and floating window
        self.assertIn('desktop-wallpaper', content)
        self.assertIn('mac-app-window', content)
        self.assertIn('mac-window-topbar', content)

        # Traffic light controls
        self.assertIn('traffic-lights', content)
        self.assertIn('traffic-light traffic-red', content)
        self.assertIn('traffic-light traffic-yellow', content)
        self.assertIn('traffic-light traffic-green', content)

    def test_global_search_and_quick_search_modal(self):
        """Verify global ⌘K search bar pill and quick search modal overlay."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Search pill and ⌘K badge
        self.assertIn('header-search-wrap', content)
        self.assertIn('header-search-pill', content)
        self.assertIn('global-search-input', content)
        self.assertIn('search-kbd-badge', content)

        # Quick search modal dialog
        self.assertIn('global-search-modal', content)
        self.assertIn('modal-search-input', content)
        self.assertIn('modal-search-close', content)

    def test_sidebar_navigation_and_brand_logo(self):
        """Verify 200px sidebar with DMOJ brand logo and navigation menu."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Sidebar and navigation
        self.assertIn('app-sidebar', content)
        self.assertIn('sidebar-brand', content)
        self.assertIn('brand-accent-o', content)
        self.assertIn('nav-list', content)
        self.assertIn('sidebar-backdrop', content)

    def test_anonymous_and_authenticated_user_profile_menu(self):
        """Verify anonymous login links vs authenticated user profile dropdown menu."""
        # 1. Anonymous state
        anon_resp = self.client.get('/')
        self.assertEqual(anon_resp.status_code, 200)
        anon_content = anon_resp.content.decode('utf-8')
        self.assertIn('anon-auth-links', anon_content)
        self.assertIn('auth-link-login', anon_content)

        # 2. Authenticated state
        self.client.force_login(self.user)
        auth_resp = self.client.get('/')
        self.assertEqual(auth_resp.status_code, 200)
        auth_content = auth_resp.content.decode('utf-8')
        self.assertIn('user-pill-dropdown', auth_content)
        self.assertIn('user-pill-trigger', auth_content)
        self.assertIn('user-dropdown-menu', auth_content)
        self.assertIn('tourist_test', auth_content)
        self.assertIn('/accounts/logout/', auth_content)
        self.assertIn('Log out', auth_content)

    def test_core_subpages_rendered_within_shell(self):
        """Verify that core subpages (problems, submissions, contests, rankings) render inside the app shell."""
        subpages = ['/problems/', '/submissions/', '/contests/', '/users/']
        for url in subpages:
            with self.subTest(url=url):
                resp = self.client.get(url)
                self.assertEqual(resp.status_code, 200)
                content = resp.content.decode('utf-8')
                self.assertIn('mac-app-window', content)
                self.assertIn('content-body', content)

    def test_app_shell_controller_script_included(self):
        """Verify that app-shell-controller.js asset is included in the base template."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('app-shell-controller.js', content)

    def test_compiled_css_tokens(self):
        """Verify that compiled resources/style.css contains all required design tokens."""
        css_path = os.path.join(settings.BASE_DIR, 'resources', 'style.css')
        self.assertTrue(os.path.exists(css_path), f"File {css_path} does not exist")
        with open(css_path, 'r', encoding='utf-8') as f:
            css = f.read()

        tokens = [
            '--color-bg-desktop:',
            '--color-primary: #F97316',
            '--radius-window: 18px',
            '.mac-app-window',
            '.traffic-lights',
            '.app-sidebar',
        ]
        for token in tokens:
            with self.subTest(token=token):
                self.assertIn(token, css)


class Milestone3ScreensTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='m3_worker_user',
            email='m3_worker@example.com',
            password='securepassword123',
        )
        self.language, _ = Language.objects.get_or_create(
            key='py3',
            defaults={'name': 'Python 3', 'common_name': 'Python 3', 'ace': 'python'}
        )
        self.profile = Profile.objects.create(user=self.user, language=self.language)
        self.group = ProblemGroup.objects.create(name='Test Group', full_name='Test Group')
        self.ptype = ProblemType.objects.create(name='Math', full_name='Mathematics')
        self.judge, _ = Judge.objects.get_or_create(name='default', defaults={'auth_key': 'defaultkey', 'online': True})
        self.problem = Problem.objects.create(
            code='aplusb',
            name='A Plus B',
            points=100.0,
            is_public=True,
            group=self.group,
            time_limit=1.0,
            memory_limit=65536,
            description='Compute A + B.',
        )
        self.problem.allowed_languages.add(self.language)
        self.problem.types.add(self.ptype)
        self.problem.judges.add(self.judge)
        self.judge.runtimes.add(self.language)

    def test_screen1_problems_catalog_layout_and_elements(self):
        """Screen 1: Verify problems catalog wrapper, filters, pills, and table columns."""
        response = self.client.get('/problems/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Wrapper & Header
        self.assertIn('problems-catalog-wrapper', content)
        self.assertIn('problems-title', content)
        self.assertIn('problems-count-badge', content)
        self.assertIn('problems-search-input', content)

        # Multi-dropdown filters
        self.assertIn('name="difficulty"', content)
        self.assertIn('name="type"', content)
        self.assertIn('dropdown-group', content)
        self.assertIn('dropdown-tags', content)
        self.assertIn('name="points_preset"', content)
        self.assertIn('name="order"', content)
        self.assertIn('btn-sort-toggle', content)

        # Quick filter pills
        self.assertIn('data-filter="all"', content)
        self.assertIn('data-filter="bookmarked"', content)
        self.assertIn('data-filter="solved"', content)
        self.assertIn('data-filter="unsolved"', content)
        self.assertIn('bookmark-count-badge', content)

        # Table Card & Columns
        self.assertIn('problems-table', content)
        self.assertIn('col-star', content)
        self.assertIn('col-index', content)
        self.assertIn('col-problem', content)
        self.assertIn('col-group', content)
        self.assertIn('col-points', content)
        self.assertIn('col-ac-rate', content)
        self.assertIn('col-status', content)
        self.assertIn('col-actions', content)

    def test_screen1_backend_filter_query_params(self):
        """Screen 1: Verify difficulty, points_preset, search, and order query params."""
        urls = [
            '/problems/?difficulty=easy',
            '/problems/?difficulty=medium',
            '/problems/?difficulty=hard',
            '/problems/?points_preset=1-10',
            '/problems/?points_preset=50+',
            '/problems/?order=-points',
            '/problems/?search=plus',
            '/problems/?q=plus',
            '/problems/?status=all',
            '/problems/?status=unsolved',
        ]
        for url in urls:
            with self.subTest(url=url):
                resp = self.client.get(url)
                self.assertEqual(resp.status_code, 200)

    def test_screen2_problem_workspace_layout_and_elements(self):
        """Screen 2: Verify split workspace, header metrics, statement pane, and editor pane."""
        response = self.client.get('/problem/aplusb')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Workspace container & split layout
        self.assertIn('problem-workspace-wrap', content)
        self.assertIn('workspace-split-container', content)
        self.assertIn('statement-pane', content)
        self.assertIn('workspace-split-divider', content)
        self.assertIn('editor-pane', content)

        # Header & 5 Metric cards
        self.assertIn('workspace-breadcrumb', content)
        self.assertIn('workspace-problem-title', content)
        self.assertIn('problem-bookmark-star', content)
        self.assertIn('metric-points', content)
        self.assertIn('metric-ac-rate', content)
        self.assertIn('metric-group', content)
        self.assertIn('metric-time-limit', content)
        self.assertIn('metric-memory-limit', content)

        # Left pane: statement tabs & KaTeX
        self.assertIn('tab-statement', content)
        self.assertIn('tab-submissions', content)
        self.assertIn('statement-content', content)
        self.assertIn('katex.min.css', content)
        self.assertIn('auto-render.min.js', content)

        # Right pane: editor toolbar & Ace
        self.assertIn('btn-reset-code', content)
        self.assertIn('btn-run-code', content)
        self.assertIn('btn-submit-code', content)
        self.assertIn('ace_source', content)
        self.assertIn('btn-copy-code', content)
        self.assertIn('btn-fullscreen-code', content)
        self.assertIn('editor-draft-indicator', content)

        # Console
        self.assertIn('workspace-console', content)
        self.assertIn('tab-console-testcases', content)
        self.assertIn('tab-console-submissions', content)
        self.assertIn('testcases-list', content)
        self.assertIn('btn-add-custom-test', content)

    def test_screen2_authenticated_submit_route_and_post(self):
        """Screen 2: Verify authenticated submit view renders split workspace and validates POST."""
        self.client.force_login(self.user)

        # GET /problem/aplusb/submit renders workspace
        resp = self.client.get('/problem/aplusb/submit')
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode('utf-8')
        self.assertIn('workspace-split-container', content)
        self.assertIn('editor-pane', content)
        self.assertIn('btn-submit-code', content)

        # POST with empty source re-renders with validation error
        resp_empty = self.client.post('/problem/aplusb/submit', {'source': '', 'language': self.language.id})
        self.assertEqual(resp_empty.status_code, 200)
        self.assertIn('error', resp_empty.content.decode('utf-8').lower())

        # POST with valid code redirects to submission
        resp_valid = self.client.post('/problem/aplusb/submit', {
            'source': 'print(1)',
            'language': self.language.id,
        })
        self.assertEqual(resp_valid.status_code, 302)
        self.assertIn('/submission/', resp_valid['Location'])
