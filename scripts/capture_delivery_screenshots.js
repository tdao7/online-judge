/**
 * capture_delivery_screenshots.js
 * Automated Visual Delivery Screenshot Capture Suite
 * 
 * Captures pixel-perfect full-page screenshots of all redesigned screens into
 * `docs/screenshots/delivery/` using Playwright and Chromium.
 * 
 * Execution:
 *   NODE_PATH="/Users/ryanx/workspace/vcoderlog-workspace/vcoderlog-websites/apps/academy-v2/node_modules" \
 *   node scripts/capture_delivery_screenshots.js
 */

const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const PROJECT_ROOT = path.resolve(__dirname, '..');
const OUTPUT_DIR = path.join(PROJECT_ROOT, 'docs', 'screenshots', 'delivery');
const BASE_URL = process.env.BASE_URL || 'http://127.0.0.1:8090';

const SCREENS = [
  {
    filename: '00_dashboard.png',
    name: 'Dashboard Workspace',
    path: '/',
    waitFor: '#dashboard-wrapper',
    viewport: { width: 1440, height: 900 }
  },
  {
    filename: '01_problems_catalog.png',
    name: 'Problems Catalog (Screen 1)',
    path: '/problems/',
    waitFor: '.problems-catalog-wrapper',
    viewport: { width: 1440, height: 900 }
  },
  {
    filename: '02_problem_workspace.png',
    name: 'Problem Workspace (Screen 2)',
    path: '/problem/aplusb',
    waitFor: '#workspace-split-container',
    viewport: { width: 1440, height: 900 }
  },
  {
    filename: '03_submissions_catalog.png',
    name: 'Submissions Catalog (Screen 3)',
    path: '/submissions/',
    waitFor: '.submissions-catalog-wrapper',
    viewport: { width: 1440, height: 900 }
  },
  {
    filename: '03b_submission_drawer.png',
    name: 'Submissions Detail Drawer (Screen 3 Drawer)',
    path: '/submissions/',
    waitFor: '.submissions-catalog-wrapper',
    viewport: { width: 1440, height: 900 },
    interact: async (page) => {
      // Click first submission row to open slide-out detail drawer
      const row = await page.$('.submission-row, tr[data-submission-id]');
      if (row) {
        await row.click();
        await page.waitForTimeout(600); // Wait for drawer slide-in animation
      }
    }
  },
  {
    filename: '04_contests_catalog.png',
    name: 'Contests Arena Overview (Screen 4)',
    path: '/contests/',
    waitFor: '.contests-list-wrapper',
    viewport: { width: 1440, height: 900 }
  },
  {
    filename: '05_contest_workspace.png',
    name: 'Live Contest Workspace (Screen 5)',
    path: '/contest/monthly2026',
    waitFor: '.contest-workspace-wrapper',
    viewport: { width: 1440, height: 900 }
  },
  {
    filename: '06_rankings_leaderboard.png',
    name: 'Leaderboard & Rankings (Screen 6)',
    path: '/users/',
    waitFor: '.rankings-catalog-wrapper',
    viewport: { width: 1440, height: 900 }
  },
  {
    filename: '07_user_profile.png',
    name: 'User Profile (Screen 7)',
    path: '/user/tourist',
    waitFor: '.user-hero-card',
    viewport: { width: 1440, height: 900 }
  },
  {
    filename: '08_auth_login.png',
    name: 'Authentication Login Workspace',
    path: '/accounts/login/',
    waitFor: '#auth-login-card',
    viewport: { width: 1440, height: 900 }
  },
  {
    filename: '09_auth_register.png',
    name: 'Authentication Register Workspace',
    path: '/accounts/register/',
    waitFor: '#auth-register-card',
    viewport: { width: 1440, height: 900 }
  },
  // Mobile Viewport Verification
  {
    filename: 'mobile_00_dashboard.png',
    name: 'Mobile Dashboard (375px)',
    path: '/',
    waitFor: '#dashboard-wrapper',
    viewport: { width: 375, height: 812 }
  },
  {
    filename: 'mobile_01_problems.png',
    name: 'Mobile Problems Catalog (375px)',
    path: '/problems/',
    waitFor: '.problems-catalog-wrapper',
    viewport: { width: 375, height: 812 }
  }
];

async function captureAll() {
  console.log('====================================================');
  console.log('VCoderLog Automated Visual Delivery Screenshot Audit');
  console.log('Target Server:', BASE_URL);
  console.log('Output Directory:', OUTPUT_DIR);
  console.log('====================================================\n');

  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  let captured = 0;
  let failed = 0;

  for (const screen of SCREENS) {
    const targetUrl = `${BASE_URL}${screen.path}`;
    const outputPath = path.join(OUTPUT_DIR, screen.filename);
    console.log(`[Capturing] ${screen.name} -> ${screen.filename}...`);

    try {
      const context = await browser.newContext({
        viewport: screen.viewport,
        deviceScaleFactor: 2 // High-DPI retina screenshots
      });
      const page = await context.newPage();

      await page.goto(targetUrl, { waitUntil: 'networkidle', timeout: 15000 });

      if (screen.waitFor) {
        await page.waitForSelector(screen.waitFor, { timeout: 5000 }).catch(() => {
          console.warn(`  Warning: Selector '${screen.waitFor}' not immediately visible.`);
        });
      }

      // Wait for font rendering
      await page.evaluate(() => document.fonts.ready);

      // Execute custom interactions if required (e.g. drawer open)
      if (screen.interact) {
        await screen.interact(page);
      }

      // Capture full-page screenshot
      await page.screenshot({
        path: outputPath,
        fullPage: true
      });

      const stat = fs.statSync(outputPath);
      console.log(`  ✔ SUCCESS: Saved ${screen.filename} (${(stat.size / 1024).toFixed(1)} KB)`);
      captured++;

      await context.close();
    } catch (err) {
      console.error(`  ✖ ERROR: Failed to capture ${screen.name}: ${err.message}`);
      failed++;
    }
  }

  await browser.close();

  console.log('\n====================================================');
  console.log(`SUMMARY: ${captured} captured, ${failed} failed`);
  console.log('====================================================');

  if (failed > 0) {
    process.exit(1);
  }
}

if (require.main === module) {
  captureAll().catch((err) => {
    console.error('Fatal execution error:', err);
    process.exit(1);
  });
}

module.exports = { captureAll, SCREENS };
