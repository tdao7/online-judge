# VCoder Design System Specification

This document defines the visual architecture, design tokens, component specifications, and responsive behaviors for the VCoder Online Judge platform.

---

## 1. Design Philosophy

- **Desktop-App Aesthetic**: Emulates a sleek macOS application floating on a calm, deep desktop wallpaper.
- **Developer-Centric Clarity**: High information density without visual clutter, crisp monospace code presentation, and instant visual feedback for judging statuses.
- **Vibrant Accent Palette**: Primary action brand color is vibrant orange (`#F97316`), paired with deep slate backgrounds (`#0F172A`) and distinct semantic status colors.

---

## 2. Semantic Design Tokens

### Color Tokens
| Token | Default (Light) | Dark Theme | Purpose |
| :--- | :--- | :--- | :--- |
| `--color-bg-desktop` | `#3A6073` / `#4A729E` | `#090D16` | Outer desktop wallpaper |
| `--color-bg-app` | `#F8FAFC` | `#0F172A` | Floating window body |
| `--color-bg-card` | `#FFFFFF` | `#1E293B` | Card and panel surfaces |
| `--color-bg-sidebar` | `#0F172A` | `#080C14` | Navigation sidebar |
| `--color-border-subtle`| `rgba(0, 0, 0, 0.07)`| `rgba(255, 255, 255, 0.08)` | Dividers, card borders |
| `--color-primary` | `#F97316` | `#FB923C` | Primary CTA, active states |
| `--color-primary-hover`| `#EA580C` | `#F97316` | Hover state for buttons |
| `--color-success` | `#16A34A` | `#22C55E` | Accepted (AC), online status |
| `--color-danger` | `#DC2626` | `#EF4444` | Wrong Answer (WA), errors |
| `--color-warning` | `#D97706` | `#F59E0B` | Time Limit Exceeded (TLE) |
| `--color-info` | `#2563EB` | `#3B82F6` | Informational badges, links |
| `--color-text-main` | `#0F172A` | `#F8FAFC` | Headings, primary content |
| `--color-text-muted` | `#64748B` | `#94A3B8` | Subtitles, timestamps, captions |

### Typography
- **Sans Font Family**: `Inter`, `-apple-system`, `BlinkMacSystemFont`, `"Segoe UI"`, `Roboto`, `sans-serif`
- **Monospace Font Family**: `JetBrains Mono`, `Fira Code`, `SF Mono`, `Menlo`, `Monaco`, `monospace`

---

## 3. Window & Shell Anatomy

- **Desktop Window Container (`.macos-app-window`)**:
  - `max-width: 1560px`
  - `margin: 24px auto`
  - `border-radius: 14px`
  - `box-shadow: 0 20px 45px rgba(0, 0, 0, 0.22), 0 8px 18px rgba(0, 0, 0, 0.12)`
  - `overflow: hidden`
- **Traffic Light Controls**:
  - Located at top-left of the application header.
  - Three circular buttons (12px diameter):
    - Close: `#FF5F56` (Border: `#E0443E`)
    - Minimize: `#FFBD2E` (Border: `#DEA123`)
    - Maximize: `#27C93F` (Border: `#1AAB29`)
- **Navigation Sidebar (`.app-sidebar`)**:
  - `width: 200px`
  - `background: #0F172A`
  - Nav items with rounded hover pills and active left orange accent indicator.

---

## 4. Reusable UI Components

### 4.1 Verdict Badges
```html
<span class="badge-verdict v-ac">AC</span>
<span class="badge-verdict v-wa">WA</span>
<span class="badge-verdict v-tle">TLE</span>
<span class="badge-verdict v-mle">MLE</span>
<span class="badge-verdict v-ce">CE</span>
<span class="badge-verdict v-re">RE</span>
```

### 4.2 Top 3 Podium Cards (Screen 6)
- **Rank 1 (Gold)**: Centered, elevated scale, gold crown badge `#F59E0B`, glowing avatar ring.
- **Rank 2 (Silver)**: Left position, silver badge `#94A3B8`.
- **Rank 3 (Bronze)**: Right position, bronze badge `#B45309`.

### 4.3 Slide-Out Submissions Drawer (Screen 3)
- Smooth slide-out panel occupying `40%` width of the submissions viewport.
- Contains:
  - Submission summary header (ID, user, verdict pill, runtime, memory).
  - Batch testcase status matrix with color-coded case blocks.
  - Read-only syntax-highlighted code viewer with instant copy button.

### 4.4 Split-Pane Workspace (Screen 2 & Screen 5)
- Left pane (~42%): Statement, constraints, KaTeX math blocks, sample input/output cards with one-click copy buttons.
- Middle divider: 6px drag handle with hover glow.
- Right pane (~58%): Language picker, theme selector, full-height Ace editor, test case runner, and primary Submit button.

---

## 5. Responsive Behavior

| Device | Viewport Width | Window Presentation | Sidebar Behavior |
| :--- | :--- | :--- | :--- |
| **Desktop** | > 1024px | Floating centered window (1560px max) on desktop wallpaper | Fixed 200px sidebar |
| **Tablet** | 768px – 1024px | Full-width window, margins removed | Collapsible drawer menu |
| **Mobile** | < 768px | Native full-screen mobile app layout | Drawer hamburger navigation, stacked tables |
