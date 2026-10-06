# Project: VCoderLog Online Judge Frontend Redesign & Full-Bleed Enterprise Platform

## Architecture & Design System
- **Shell Model**: Native edge-to-edge web application shell replacing simulated macOS desktop wallpaper and floating window.
- **Top Navigation Bar**: Sticky 56px navbar (`#app-navbar`) containing VCoderLog brand logo, primary navigation links (Dashboard, Problems, Contests, Submissions, Rankings), global `⌘K` search shortcut pill, contest countdown timer badge, notification bell, and user profile menu.
- **Mobile Navigation Drawer**: Sliding off-canvas navigation drawer (`#navigation.mobile-drawer`) on `< 1024px` with smooth transition and backdrop overlay.
- **Main Canvas**: Full-bleed responsive `<main id="app-main">` with `.app-container` (default `max-width: 1440px` centered) and `.is-full-bleed` for the Split-Pane Coding Workspace (`calc(100vh - 56px)` height with suppressed footer).
- **Color System**: Light theme (`#F8FAFC` canvas, `#FFFFFF` cards, `#0F172A` text, `#F97316` brand orange); Dark theme (`#0B0F19` canvas, `#1E293B` cards, `#F1F5F9` text).
- **Build Pipeline**: Dart Sass 1.99.0 + PostCSS Autoprefixer via `./make_style.sh all`, synchronized with `static/` via `collectstatic`.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Strip Desktop Wallpaper | Remove `.desktop-wallpaper`, wallpaper gradients, and outer padding | M1 | Survey Explorer 1 |
| 2 | Strip Mac Window Chrome | Remove `.mac-app-window`, `.mac-window`, `.mac-window-topbar`, and `.mac-window-body` | M1 | Survey Explorer 1 |
| 3 | Strip macOS Traffic Lights | Remove simulated OS window controls (`.traffic-lights`, red/yellow/green buttons) and JS handlers | M1 | Survey Explorer 1 |
| 4 | Enterprise Sticky Top Navbar | 56px sticky top bar with logo, nav links, search trigger, timer, notifications, user menu | M1 | Survey Explorer 1 |
| 5 | Mobile Navigation Drawer | Sliding drawer navigation on `< 1024px` with hamburger button and backdrop | M1 | Survey Explorer 1 |
| 6 | Full-Bleed Main Viewport | `<main id="app-main">` spanning 100% viewport width with responsive layout container | M1 | Survey Explorer 1 |
| 7 | Global ⌘K Quick Search Modal | Decoupled search modal dialog with keyboard shortcuts and search index | M1 | Survey Explorer 1 |
| 8 | User Profile Menu & Auth Links | Dropdown menu for authenticated users, clean login/signup buttons for guests | M1 | Survey Explorer 1 |
| 9 | Impersonation Topbar Banner | Top border indicator and alert badge when admin is impersonating a user | M1 | Survey Explorer 1 |
| 10 | Docked Contest Timer Badge | Topbar-docked timer badge replacing floating draggable pill | M1 | Survey Explorer 1 |
| 11 | Shell Unit Tests Inversion | Update `judge/tests.py` to assert enterprise navbar and verify absence of desktop wallpaper | M1 | Survey Explorer 1 & 3 |
| 12 | Dashboard Polish | Clean hero banner, suppress legacy title row, 4-metric strip, activity feed, upcoming contests | M2 | Survey Explorer 2 |
| 13 | Problems Catalog Polish | Full 1440px container, unified multi-filters, quick pills, 8-column data table, pagination | M2 | Survey Explorer 2 |
| 14 | Split-Pane Problem Workspace Polish | Full viewport height (`calc(100vh - 56px)`), suppress footer, draggable split divider, Ace editor, KaTeX | M2 | Survey Explorer 2 |
| 15 | Submissions Catalog & Drawer Polish | Verdict pills, execution metrics, 58/42 split-view on desktop, 420px fixed drawer on mobile | M2 | Survey Explorer 2 |
| 16 | Contests Overview & Workspace Polish | Featured contest hero countdown, tables, 3-column live contest workspace (`240px 1fr 1.15fr`) | M2 | Survey Explorer 2 |
| 17 | Rankings & Leaderboard Polish | Top 3 podium showcase cards (gold/silver/bronze), color rating tiers, distribution sidebar | M2 | Survey Explorer 2 |
| 18 | User Profile Polish | Hero card with avatar & 4 stat cards, SVG rating history curve, topic proficiency, recent submissions | M2 | Survey Explorer 2 |
| 19 | Auth Workspaces Polish | Centered login, register, password reset, and 2FA cards on clean canvas without sidebars | M2 | Survey Explorer 2 |
| 20 | SCSS Deprecation Elimination | Replace `@import "vars-vcoder"` with `@use "vars-vcoder" as *;` in `dashboard.scss` & `auth-workspace.scss` | M3 | Survey Explorer 1 & 3 |
| 21 | Obsolete SCSS Variables Removal | Remove `--traffic-*`, `--shell-wallpaper-padding-*`, `--color-bg-desktop*` from `vars-vcoder.scss` | M3 | Survey Explorer 1 & 3 |
| 22 | Clean SCSS Compilation | Recompile stylesheets via `./make_style.sh all` with zero warnings and sync with `static/` | M3 | Survey Explorer 3 |
| 23 | Full Functional Regression Verification | Pass 100% of `scripts/verify_m7_full_regression.py` (61/61 tests) and per-screen test suites | M4 | Survey Explorer 3 |
| 24 | Automated Visual Delivery Review | Execute Playwright automated screenshots into `docs/screenshots/delivery/` (13 full-page captures) | M4 | Survey Explorer 3 |
| 25 | Final Delivery Verification | End-to-end audit, DOM inspection for zero legacy tokens, and report back to Sentinel | M4 | Project Orchestrator |

## Milestones
| # | Name | Scope | Dependencies | Status | Output Summary |
|---|------|-------|-------------|--------|----------------|
| M1 | App Shell Decoupling & Sticky Top Navbar | Decouple wallpaper/window, build sticky navbar, mobile drawer, update tests.py | None | **DONE** | Gate PASSED (2x APPROVE, 2x APPROVE, 1x CLEAN). Zero legacy tokens. 540 tests passed. |
| M2 | 7 Core Workspaces UI Refactoring & Polish | Refactor Dashboard, Problems, Split Editor, Submissions, Contests, Rankings, Profile, Auth | M1 | **DONE** | Gate PASSED after remediation (2x APPROVE, 2x APPROVE, 1x CLEAN). 51/51 empirics pass, 61/61 regression pass. |
| M3 | SCSS Architecture Refactoring & Compilation | Migrate to `@use`, clean tokens, compile via `./make_style.sh all`, sync `static/` | M1, M2 | **DONE** | Stylesheets compile cleanly with 0 errors/warnings. Zero legacy tokens in CSS. Static assets collected. |
| M4 | Full Regression & Automated Visual Delivery | Run 61/61 regression tests, generate 13 delivery screenshots, final quality audit | M3 | **DONE** | 13/13 retina screenshots generated (>120KB each), 61/61 regression tests pass, 662/662 DOM tests pass, Final Forensic Audit CLEAN. |

## Interface Contracts & Code Layout

### Code Layout
- `templates/base.html`: Root application shell (navbar, mobile drawer, main canvas, search modal)
- `templates/home.html`: Dashboard template
- `templates/problem/`: Problem catalog (`list.html`) and split-pane workspace (`problem.html`, `statement-pane.html`, `editor-pane.html`)
- `templates/submission/`: Submissions catalog & inspector drawer (`list.html`)
- `templates/contest/`: Contests catalog (`list.html`) and live contest workspace (`contest.html`)
- `templates/user/`: Leaderboard rankings (`list.html`) and user profile (`user-base.html`, `user-about.html`)
- `templates/registration/`: Authentication templates (`login.html`, `registration_form.html`, `password_reset.html`, `two_factor_auth.html`)
- `resources/vars-vcoder.scss`: Design system CSS custom properties
- `resources/app-shell.scss`: Enterprise shell, navbar, drawer, and global components
- `resources/app-shell-controller.js`: DOM event controller (mobile drawer, ⌘K search modal, user dropdown)
- `make_style.sh`: Stylesheet build script
- `scripts/verify_m7_full_regression.py`: 61-point functional regression suite
- `docs/screenshots/delivery/`: Target directory for full-page delivery screenshots
