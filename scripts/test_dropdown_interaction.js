const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto('http://100.107.199.45:8090/problem/aplusb', { waitUntil: 'networkidle' });

  await page.click('#lang-dropdown-trigger');
  await page.fill('#lang-search-input', 'py');
  await page.waitForTimeout(300);

  const visibleItems = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('#lang-options-list li'))
      .filter(el => el.style.display !== 'none')
      .map(el => el.textContent.trim().replace(/\s+/g, ' '));
  });
  console.log('Visible items with query "py":', visibleItems);

  await page.fill('#lang-search-input', 'rust');
  await page.waitForTimeout(300);
  const visibleRust = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('#lang-options-list li'))
      .filter(el => el.style.display !== 'none')
      .map(el => el.textContent.trim().replace(/\s+/g, ' '));
  });
  console.log('Visible items with query "rust":', visibleRust);

  // Select Rust
  await page.click('#lang-options-list li[data-name="Rust"]');
  await page.waitForTimeout(300);
  const selectedText = await page.evaluate(() => document.getElementById('current-lang-name').textContent.trim());
  console.log('Selected language in trigger button:', selectedText);

  await browser.close();
})();
