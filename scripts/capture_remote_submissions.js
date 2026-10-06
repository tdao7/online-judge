const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

async function capture() {
  const artifactDir = '/Users/ryanx/.gemini/antigravity/brain/e9cedfde-1958-4142-a1f7-1219ddddf914/screenshots/judge';
  fs.mkdirSync(artifactDir, { recursive: true });

  const browser = await chromium.launch({ headless: true });

  // 1. Remote Desktop 1440x900 - Empty state on good_subarrays
  const pageEmpty = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await pageEmpty.goto('http://100.107.199.45:8090/problem/good_subarrays/submissions/', { waitUntil: 'networkidle' });
  await pageEmpty.waitForTimeout(1000);
  await pageEmpty.screenshot({
    path: path.join(artifactDir, 'remote_node2_good_subarrays_submissions.png'),
    fullPage: false
  });
  console.log('Saved remote_node2_good_subarrays_submissions.png');

  // 2. Remote Desktop 1440x900 - Populated submissions on aplusb
  const pagePopulated = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await pagePopulated.goto('http://100.107.199.45:8090/problem/aplusb/submissions/', { waitUntil: 'networkidle' });
  await pagePopulated.waitForTimeout(1000);
  await pagePopulated.screenshot({
    path: path.join(artifactDir, 'remote_node2_aplusb_submissions.png'),
    fullPage: false
  });
  console.log('Saved remote_node2_aplusb_submissions.png');

  await browser.close();
  console.log('All remote Node 2 screenshots captured.');
}

capture().catch(err => {
  console.error(err);
  process.exit(1);
});
