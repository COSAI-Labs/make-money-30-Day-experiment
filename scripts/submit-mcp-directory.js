// Submit ToolPipe MCP Server to mcp.directory
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  console.log('Navigating to mcp.directory/submit...');
  await page.goto('https://mcp.directory/submit', { waitUntil: 'networkidle', timeout: 30000 });

  // Wait for form to load
  await page.waitForTimeout(3000);

  // Get page content to understand the form
  const content = await page.content();
  console.log('Page loaded. Looking for form fields...');

  // Try to find and fill the GitHub URL field
  const inputs = await page.$$('input');
  console.log(`Found ${inputs.length} input fields`);

  for (const input of inputs) {
    const placeholder = await input.getAttribute('placeholder');
    const name = await input.getAttribute('name');
    const type = await input.getAttribute('type');
    const id = await input.getAttribute('id');
    console.log(`  Input: name=${name}, type=${type}, id=${id}, placeholder=${placeholder}`);
  }

  // Try to fill GitHub URL
  try {
    // Look for the GitHub URL input
    const urlInput = await page.$('input[type="url"], input[type="text"], input[placeholder*="github"], input[placeholder*="URL"], input[placeholder*="url"], input[name*="url"], input[name*="repo"]');
    if (urlInput) {
      await urlInput.fill('https://github.com/COSAI-Labs/make-money-30day-challenge/tree/master/products/mcp-server');
      console.log('Filled GitHub URL');

      // Look for optional fields
      const descInput = await page.$('textarea, input[name*="desc"], input[placeholder*="desc"]');
      if (descInput) {
        await descInput.fill('238+ dev tools via MCP: JSON, QR, PDF, DNS, hash, UUID, code review, JWT, SSL, WHOIS, and more');
        console.log('Filled description');
      }

      const emailInput = await page.$('input[type="email"], input[name*="email"], input[placeholder*="email"]');
      if (emailInput) {
        await emailInput.fill('toolpipe-project@sharebot.net');
        console.log('Filled email');
      }

      // Screenshot before submit
      await page.screenshot({ path: '/tmp/mcp-directory-form.png' });
      console.log('Screenshot saved to /tmp/mcp-directory-form.png');

      // Find and click submit button
      const submitBtn = await page.$('button[type="submit"], button:has-text("Submit"), button:has-text("Add")');
      if (submitBtn) {
        await submitBtn.click();
        console.log('Clicked submit button');
        await page.waitForTimeout(5000);
        await page.screenshot({ path: '/tmp/mcp-directory-result.png' });
        console.log('Result screenshot saved');
        console.log('Current URL:', page.url());
      } else {
        console.log('No submit button found');
      }
    } else {
      console.log('No URL input found. Taking screenshot...');
      await page.screenshot({ path: '/tmp/mcp-directory-form.png' });
    }
  } catch (e) {
    console.error('Error:', e.message);
    await page.screenshot({ path: '/tmp/mcp-directory-error.png' });
  }

  await browser.close();
  console.log('Done');
})();
