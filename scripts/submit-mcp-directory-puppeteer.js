const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();

  console.log('Navigating to mcp.directory/submit...');
  await page.goto('https://mcp.directory/submit', { waitUntil: 'networkidle2', timeout: 30000 });
  await new Promise(r => setTimeout(r, 3000));

  // Get all input fields
  const inputs = await page.$$eval('input', els => els.map(el => ({
    name: el.name, type: el.type, id: el.id, placeholder: el.placeholder, value: el.value
  })));
  console.log('Input fields:', JSON.stringify(inputs, null, 2));

  // Get textareas
  const textareas = await page.$$eval('textarea', els => els.map(el => ({
    name: el.name, id: el.id, placeholder: el.placeholder
  })));
  console.log('Textareas:', JSON.stringify(textareas, null, 2));

  // Get buttons
  const buttons = await page.$$eval('button', els => els.map(el => ({
    text: el.textContent.trim(), type: el.type
  })));
  console.log('Buttons:', JSON.stringify(buttons, null, 2));

  // Try to fill the form
  try {
    // Fill GitHub URL field (first text/url input)
    const urlSelector = 'input[type="url"], input[type="text"]:not([type="hidden"])';
    const urlInputs = await page.$$(urlSelector);

    if (urlInputs.length > 0) {
      await urlInputs[0].click({ clickCount: 3 });
      await urlInputs[0].type('https://github.com/COSAI-Labs/make-money-30day-challenge/tree/master/products/mcp-server');
      console.log('Filled GitHub URL');
    }

    // Fill email if present
    const emailInput = await page.$('input[type="email"]');
    if (emailInput) {
      await emailInput.type('toolpipe-project@sharebot.net');
      console.log('Filled email');
    }

    // Fill description if present
    const textarea = await page.$('textarea');
    if (textarea) {
      await textarea.type('238+ dev tools via MCP: JSON, QR, PDF, DNS, hash, UUID, code review, JWT, SSL, WHOIS, and more. Free tier: 100 calls/day.');
      console.log('Filled description');
    }

    // Screenshot
    await page.screenshot({ path: '/tmp/mcp-directory-filled.png', fullPage: true });
    console.log('Screenshot saved');

    // Click submit
    const submitBtn = await page.$('button[type="submit"]');
    if (submitBtn) {
      await submitBtn.click();
      console.log('Clicked submit');
      await new Promise(r => setTimeout(r, 5000));
      await page.screenshot({ path: '/tmp/mcp-directory-result.png', fullPage: true });
      console.log('Result URL:', page.url());
    }
  } catch (e) {
    console.error('Error:', e.message);
  }

  await browser.close();
  console.log('Done');
})();
