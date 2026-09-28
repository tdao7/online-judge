# Frontend Redesign & Architectural Audit

This document provides a comprehensive architectural audit and analysis of the upstream DMOJ Online Judge system and details how the modern macOS-inspired floating-window design system is layered atop it without modifying core judging protocols or backend business logic.

---

## 1. Upstream DMOJ Core Architecture

The DMOJ online judge platform consists of three core components:
1. **Django Web Application (`online-judge`)**:
   - Manages authentication, permissions, database models (users, profiles, problems, submissions, contests, organizations), and HTTP/WebSocket endpoints.
   - Leverages `django-jinja` with Jinja2 as its high-performance templating engine.
   - Exposes RESTful and AJAX endpoints for submission submission, live status streaming, problem searching, and code editing.
2. **Bridge Daemon (`dmoj-judge` bridge)**:
   - A persistent daemon coordinating judging jobs between the web server and connected judge servers over an encrypted internal protocol.
3. **Judge Server (`judge-server`)**:
   - An isolated Linux sandboxing executor running `ptrace`/cgroups to evaluate untrusted user submissions across 60+ programming languages with precise CPU, memory, and security limits.

---

## 2. Template Hierarchy & Rendering Engine

DMOJ uses Jinja2 with custom extensions (`judge/jinja2/`):
- `base.html`: The master shell. In our redesign, `base.html` implements the desktop wallpaper background (`--color-bg-desktop`), the centered 1560px floating application window (`.macos-app-window`), the macOS top traffic lights (red, yellow, green), the global search bar (`⌘K`), the sidebar navigation (`.app-sidebar`), and the user menu.
- **Page-Level Templates**:
  - `home.html`: High-fidelity Dashboard with platform metrics, hero CTA banner, live submissions stream, and active contest widgets.
  - `problem/list.html` (Screen 1): Problems Catalog with search, multi-filters (difficulty, type, tags, sort), and progress bars.
  - `problem/problem.html` (Screen 2): Split-pane Problem Workspace (~42% statement with KaTeX math rendering, ~58% interactive Ace editor workspace).
  - `submission/list.html` (Screen 3): Submissions Catalog with verdict pills and slide-out inspector drawer for testcase batches and syntax-highlighted code.
  - `contest/list.html` (Screen 4): Contests Catalog with featured contest countdown card and mini calendar.
  - `contest/contest.html` (Screen 5): Live Contest Workspace with problem switcher sidebar (A, B, C, D), live countdown stopwatch, score progress bar, and integrated code editor.
  - `user/list.html` (Screen 6): Global Leaderboard with Top 3 Podium cards (Gold, Silver, Bronze), trend sparklines, and rating distribution histograms.
  - `user/user-base.html` & `user-about.html` (Screen 7): User Profile with Hero header, verified badge, 4 stat cards, SVG rating history chart, topic strengths, and submission history.
  - `registration/login.html`, `registration_form.html`, `password_reset.html`, `two_factor_auth.html`: Modern macOS card authentication workspaces.

---

## 3. Asset Pipeline & SCSS Architecture

Styles are structured modularly under `resources/`:
- `resources/vars-vcoder.scss`: Core design tokens for light theme (brand orange `#F97316`, dark slate `#0F172A`, calm wallpaper `#4A729E`).
- `resources/vars-dark.scss`: Dark mode tokens (`#0F172A` background, `#1E293B` cards).
- `make_style.sh`: Build pipeline executing Dart Sass and PostCSS with Autoprefixer. It outputs compiled CSS into `resources/` and `resources/dark/`, followed by Django `collectstatic`.

### Component Stylesheets:
| SCSS File | Target Screen / Component |
| :--- | :--- |
| `app-shell.scss` | Desktop wallpaper, floating window shell, traffic lights, sidebar |
| `problems-list.scss` | Screen 1: Problems Catalog & Multi-Filters |
| `problem-workspace.scss` | Screen 2: Split-Pane statement & coding workspace |
| `submissions-list.scss` | Screen 3: Submissions table & verdict badges |
| `submission-drawer.scss` | Screen 3: 40% slide-out detail drawer & batch grid |
| `contests-list.scss` | Screen 4: Featured contest hero card & contest tables |
| `contest-workspace.scss` | Screen 5: 3-column Live Contest Workspace |
| `rankings-list.scss` | Screen 6: Top 3 Podium cards, leaderboard & histograms |
| `user-profile.scss` | Screen 7: User Hero card, SVG rating curve, topic bars |
| `dashboard.scss` | Dashboard: Hero card, metric counters, live feeds |
| `auth-workspace.scss` | Auth screens: Login, Register, Password Reset, 2FA |

---

## 4. Split-Pane Coding Workspace & Ace Integration

- **Dual-Pane Layout**: The Problem Workspace (`problem.html`) uses CSS Flexbox with an interactive resize divider (`.split-resizer`). Users can drag the divider or double-click to reset to default 42%/58% ratio.
- **Ace Editor Customization**: Embedded via `django_ace` and styled through `ace-dmoj.scss` with Monokai / Chrome themes, custom font ligatures, line numbers, and keyboard shortcuts (`Ctrl+Enter` to submit).
- **Direct Submission Execution**: Code is submitted via asynchronous AJAX or standard POST to `url('problem_submit', problem.code)`, triggering immediate grading without page reload.

---

## 5. Live WebSocket & Real-Time Event Architecture

- DMOJ uses a lightweight WebSocket daemon (`websocket/` service) to broadcast real-time submission progress.
- Submissions receive event packets (`test_case`, `compile_error`, `graded`) via `submission-live.js`.
- The redesigned Submissions Drawer dynamically updates verdict badges, execution time, memory usage, and testcase batch checkboxes as judge results stream in from the `judge-server`.
