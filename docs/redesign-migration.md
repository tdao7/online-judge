# Redesign Migration & Template Mapping Guide

This guide maps each original upstream DMOJ template to its redesigned counterpart, documents backend context enrichments, and outlines regression testing checklists across all platform milestones.

---

## 1. Template & View Mapping Matrix

| Screen / Feature | Original Template | Redesigned Template | SCSS Component | Backend View / Enhancements |
| :--- | :--- | :--- | :--- | :--- |
| **App Shell** | `templates/base.html` | `templates/base.html` | `app-shell.scss` | Traffic lights, ⌘K search, responsive drawer |
| **Dashboard (R4)** | `templates/home.html` | `templates/home.html` | `dashboard.scss` | `judge.views.blog.PostList` (+ recent submissions, metrics, top contenders) |
| **Screen 1: Problems** | `templates/problem/list.html` | `templates/problem/list.html` | `problems-list.scss` | `judge.views.problem.ProblemList` (category filters, quick pills, progress bars) |
| **Screen 2: Problem Workspace** | `templates/problem/problem.html` | `templates/problem/problem.html` | `problem-workspace.scss` | `judge.views.problem.ProblemDetail` (split-pane, Ace editor integration, KaTeX) |
| **Screen 3: Submissions** | `templates/submission/list.html` | `templates/submission/list.html` | `submissions-list.scss`<br>`submission-drawer.scss` | `judge.views.submission.SubmissionList` (verdict badges, 40% slide-out drawer) |
| **Screen 4: Contests Overview** | `templates/contest/list.html` | `templates/contest/list.html` | `contests-list.scss` | `judge.views.contests.ContestList` (featured hero card, countdown, mini calendar) |
| **Screen 5: Live Contest Workspace** | `templates/contest/contest.html` | `templates/contest/contest.html` | `contest-workspace.scss` | `judge.views.contests.ContestDetail` (3-column layout, problem switcher, live timer) |
| **Screen 6: Global Rankings** | `templates/user/list.html` | `templates/user/list.html` | `rankings-list.scss` | `judge.views.user.UserList` (Top 3 podium cards, rating histograms, sparklines) |
| **Screen 7: User Profile** | `templates/user/user-base.html`<br>`templates/user/user-about.html` | `templates/user/user-base.html`<br>`templates/user/user-about.html` | `user-profile.scss` | `judge.views.user.UserAboutPage` (User hero card, 4 stat cards, SVG rating curve) |
| **Auth: Sign In** | `templates/registration/login.html` | `templates/registration/login.html` | `auth-workspace.scss` | Standard Django auth, CSRF, social providers |
| **Auth: Register** | `templates/registration/registration_form.html` | `templates/registration/registration_form.html` | `auth-workspace.scss` | Timezone detection, password validators, captcha |
| **Auth: Reset Password**| `templates/registration/password_reset.html` | `templates/registration/password_reset.html` | `auth-workspace.scss` | Password reset email workflow |
| **Auth: 2FA / WebAuthn**| `templates/registration/two_factor_auth.html` | `templates/registration/two_factor_auth.html` | `auth-workspace.scss` | TOTP token validation, WebAuthn navigator credentials |

---

## 2. Backend View Modifications & Context Enrichments

To ensure zero fake data and complete preservation of DMOJ ORM patterns, the following view classes were extended:

1. **`judge/views/blog.py` (`PostList.get_context_data`)**:
   - Added `recent_submissions`: Latest 8 public submissions with `select_related('user__user', 'problem', 'language')`.
   - Added `top_contenders`: Top 5 rated users with `order_by('-rating')`.
2. **`judge/views/contests.py` (`ContestDetail.get_context_data`)**:
   - Added `workspace_problems`: List of problems in the contest with letter labels (A, B, C...) and scores.
   - Added `active_cp`: Selected problem for the split-pane contest statement & editor.
   - Added `user_score`, `max_score`, `user_rank` computed from contest participations.
   - Added `languages` and `default_language` for the embedded Ace editor.
3. **`judge/views/user.py` (`UserList.get_context_data` & `UserAboutPage.get_context_data`)**:
   - Unpacked `ranker` generator tuples `(rank, profile)` into `podium` (`rank_1`, `rank_2`, `rank_3`) and `table_users`.
   - Added `total_rated_users`, `new_this_month`, `avg_rating_gain`, `rating_distribution` histogram bins.
   - Added `top_organizations` with `Count('member')`.
   - Added `rank_title`, `recent_submissions`, `recent_contests`, and `topic_strengths` to profile view.

---

## 3. Seed & Data Utility Scripts

The following helper scripts automate database population for testing and production verification:
- `scripts/seed_data.py`: Creates problems (e.g. `aplusb`, `primes`, `dijkstra`, `knapsack`), sample submissions with verdicts (AC, WA, TLE), and sample contests (`WCC 2026`, `Biweekly Contest 42`).
- `scripts/seed_rankings_m6.py`: Seeds top competitive programmers (`tourist`, `ecnerwala`, `qwqaqa`, `matthew99`, `BlueBook`, `admin`), organizations, and contest rating histories.

---

## 4. Verification Checklists Across All Milestones

- **Milestone 1**: DMOJ core setup, judge connection, test submissions grading AC/WA/TLE/CE.
- **Milestone 2**: Floating window shell, traffic lights, global search, responsive navigation.
- **Milestone 3**: Screen 1 (Problems catalog & filters) and Screen 2 (Problem split-pane workspace).
- **Milestone 4**: Screen 3 (Submissions table & 40% slide-out inspector drawer).
- **Milestone 5**: Screen 4 (Contests catalog & featured countdown) and Screen 5 (Live contest workspace).
- **Milestone 6**: Screen 6 (Rankings leaderboard & podium cards) and Screen 7 (User profile & rating chart).
- **Milestone 7**: Dashboard (hero banner, metrics, live feed), Auth workspaces (login, register, reset, 2FA), and architecture documentation.
