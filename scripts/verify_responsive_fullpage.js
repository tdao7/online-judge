/**
 * verify_responsive_fullpage.js
 * Verifies full-page width and responsive behavior across viewports:
 * 1920x1080 (ultrawide desktop)
 * 1440x900 (standard laptop)
 * 768x1024 (tablet)
 * 375x812 (mobile)
 */
const { chromium } = require('playwright');

async function run() {
  const browser = await chromium.launch({ headless: true });
  const viewports = [
    { name: '1920px Desktop', width: 1920, height: 1080 },
    { name: '1440px Laptop', width: 1440, height: 900 },
    { name: '768px Tablet', width: 768, height: 1024 },
    { name: '375px Mobile', width: 375, height: 812 }
  ];

  const urls = [
    { name: 'Dashboard', url: 'http://127.0.0.1:8090/' },
    { name: 'Problems', url: 'http://127.0.0.1:8090/problems/' },
    { name: 'Problem Workspace', url: 'http://127.0.0.1:8090/problem/aplusb' },
    { name: 'Submissions', url: 'http://127.0.0.1:8090/submissions/' },
    { name: 'Rankings', url: 'http://127.0.0.1:8090/users/' }
  ];

  let allPassed = true;

  for (const vp of viewports) {
    console.log(`\n=== Testing Viewport: ${vp.name} (${vp.width}x${vp.height}) ===`);
    const page = await browser.newPage({ viewport: { width: vp.width, height: vp.height } });

    for (const target of urls) {
      await page.goto(target.url, { waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(300);

      const metrics = await page.evaluate(() => {
        const body = document.body;
        const appLayout = document.querySelector('.app-layout');
        const navbar = document.querySelector('.app-navbar');
        const mainViewport = document.querySelector('.app-main-viewport');
        const content = document.querySelector('#content');
        const desktopWallpaper = document.querySelector('.desktop-wallpaper');
        const trafficLights = document.querySelector('.traffic-lights');

        const windowWidth = window.innerWidth;
        const bodyWidth = body ? body.getBoundingClientRect().width : 0;
        const navbarWidth = navbar ? navbar.getBoundingClientRect().width : 0;
        const mainViewportWidth = mainViewport ? mainViewport.getBoundingClientRect().width : 0;
        const contentWidth = content ? content.getBoundingClientRect().width : 0;

        return {
          windowWidth,
          bodyWidth,
          navbarWidth,
          mainViewportWidth,
          contentWidth,
          hasWallpaper: !!desktopWallpaper,
          hasTrafficLights: !!trafficLights,
          scrollWidth: document.documentElement.scrollWidth
        };
      });

      const fullWidthMatch = Math.abs(metrics.bodyWidth - vp.width) < 2 && Math.abs(metrics.navbarWidth - vp.width) < 2;
      const noHorizontalOverflow = metrics.scrollWidth <= vp.width;
      const cleanShell = !metrics.hasWallpaper && !metrics.hasTrafficLights;

      const passed = fullWidthMatch && noHorizontalOverflow && cleanShell;
      if (!passed) allPassed = false;

      console.log(`  [${passed ? 'PASS' : 'FAIL'}] ${target.name}: bodyWidth=${metrics.bodyWidth}px, navbarWidth=${metrics.navbarWidth}px, scrollWidth=${metrics.scrollWidth}px, noOverflow=${noHorizontalOverflow}, cleanShell=${cleanShell}`);
    }

    await page.close();
  }

  await browser.close();
  console.log(`\nOverall Responsive & Full-Page Verification: ${allPassed ? 'ALL PASSED 100%' : 'SOME CHECKS FAILED'}`);
  process.exit(allPassed ? 0 : 1);
}

run().catch(err => {
  console.error(err);
  process.exit(1);
});
