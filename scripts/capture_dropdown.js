const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto('http://100.107.199.45:8090/problem/aplusb', { waitUntil: 'networkidle' });

  // Click language trigger button
  const trigger = await page.waitForSelector('#lang-dropdown-trigger', { timeout: 5000 });
  await trigger.click();
  await page.waitForTimeout(500);

  const outDir = path.join(__dirname, '../docs/screenshots/delivery');
  fs.mkdirSync(outDir, { recursive: true });
  const screenshotPath = path.join(outDir, 'verified_dropdown_languages.png');
  await page.screenshot({ path: screenshotPath });
  console.log('Saved screenshot to:', screenshotPath);

  const options = await page.$$eval('#lang-options-list li', items => items.map(el => el.textContent.trim().replace(/\s+/g, ' ')));
  console.log('Dropdown rendered ' + options.length + ' options:');
  console.log(options);

  await browser.close();
})();
