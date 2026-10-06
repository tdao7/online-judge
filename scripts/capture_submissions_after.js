const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

async function capture() {
  const artifactDir = '/Users/ryanx/.gemini/antigravity/brain/e9cedfde-1958-4142-a1f7-1219ddddf914/screenshots/judge';
  fs.mkdirSync(artifactDir, { recursive: true });

  const browser = await chromium.launch({ headless: true });

  // 1. Desktop 1440x900 - Empty state on good_subarrays
  const pageEmpty = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await pageEmpty.goto('http://127.0.0.1:8090/problem/good_subarrays/submissions/', { waitUntil: 'networkidle' });
  await pageEmpty.waitForTimeout(1000);
  await pageEmpty.screenshot({
    path: path.join(artifactDir, 'good_subarrays_submissions_after.png'),
    fullPage: false
  });
  console.log('Saved good_subarrays_submissions_after.png');

  // 2. Desktop 1440x900 - Populated submissions on aplusb
  const pagePopulated = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await pagePopulated.goto('http://127.0.0.1:8090/problem/aplusb/submissions/', { waitUntil: 'networkidle' });
  await pagePopulated.waitForTimeout(1000);
  await pagePopulated.screenshot({
    path: path.join(artifactDir, 'aplusb_submissions_after.png'),
    fullPage: false
  });
  console.log('Saved aplusb_submissions_after.png');

  // 3. Desktop 1440x900 - Global submissions catalog
  const pageGlobal = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await pageGlobal.goto('http://127.0.0.1:8090/submissions/', { waitUntil: 'networkidle' });
  await pageGlobal.waitForTimeout(1000);
  await pageGlobal.screenshot({
    path: path.join(artifactDir, 'global_submissions_after.png'),
    fullPage: false
  });
  console.log('Saved global_submissions_after.png');

  // 4. Mobile 375x812 - good_subarrays
  const pageMobile = await browser.newPage({ viewport: { width: 375, height: 812 } });
  await pageMobile.goto('http://127.0.0.1:8090/problem/good_subarrays/submissions/', { waitUntil: 'networkidle' });
  await pageMobile.waitForTimeout(1000);
  await pageMobile.screenshot({
    path: path.join(artifactDir, 'good_subarrays_submissions_mobile.png'),
    fullPage: false
  });
  console.log('Saved good_subarrays_submissions_mobile.png');

  await browser.close();
  console.log('All submissions verification screenshots captured successfully.');
}

capture().catch(err => {
  console.error(err);
  process.exit(1);
});
