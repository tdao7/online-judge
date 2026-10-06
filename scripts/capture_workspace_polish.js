const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

async function capture() {
  const artifactDir = '/Users/ryanx/.gemini/antigravity/brain/e9cedfde-1958-4142-a1f7-1219ddddf914/screenshots/judge';
  fs.mkdirSync(artifactDir, { recursive: true });

  const browser = await chromium.launch({ headless: true });

  // 1. Desktop 1440x900 - Collapsed console (Default)
  const pageDesktop = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await pageDesktop.goto('http://127.0.0.1:8090/problem/aplusb', { waitUntil: 'networkidle' });
  await pageDesktop.waitForTimeout(1000);

  await pageDesktop.screenshot({
    path: path.join(artifactDir, 'screen2_workspace_collapsed_desktop.png'),
    fullPage: false
  });
  console.log('Saved screen2_workspace_collapsed_desktop.png');

  // 2. Desktop 1440x900 - Expanded console
  const toggleBtn = await pageDesktop.$('#console-collapse-toggle');
  if (toggleBtn) {
    await toggleBtn.click();
    await pageDesktop.waitForTimeout(500);
  }
  await pageDesktop.screenshot({
    path: path.join(artifactDir, 'screen2_workspace_expanded_desktop.png'),
    fullPage: false
  });
  console.log('Saved screen2_workspace_expanded_desktop.png');

  // 3. Tablet 768x1024
  const pageTablet = await browser.newPage({ viewport: { width: 768, height: 1024 } });
  await pageTablet.goto('http://127.0.0.1:8090/problem/aplusb', { waitUntil: 'networkidle' });
  await pageTablet.waitForTimeout(1000);
  await pageTablet.screenshot({
    path: path.join(artifactDir, 'screen2_workspace_tablet.png'),
    fullPage: false
  });
  console.log('Saved screen2_workspace_tablet.png');

  // 4. Mobile 375x812
  const pageMobile = await browser.newPage({ viewport: { width: 375, height: 812 } });
  await pageMobile.goto('http://127.0.0.1:8090/problem/aplusb', { waitUntil: 'networkidle' });
  await pageMobile.waitForTimeout(1000);
  await pageMobile.screenshot({
    path: path.join(artifactDir, 'screen2_workspace_mobile.png'),
    fullPage: false
  });
  console.log('Saved screen2_workspace_mobile.png');

  await browser.close();
  console.log('All screenshots captured successfully.');
}

capture().catch(err => {
  console.error(err);
  process.exit(1);
});
