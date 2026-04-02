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

  try {
    const inputs = await page.$$('input');

    // Field 0: GitHub URL (type=url, placeholder=https://github.com/org/mcp-server)
    if (inputs[0]) {
      await inputs[0].click({ clickCount: 3 });
      await inputs[0].type('https://github.com/COSAI-Labs/make-money-30day-challenge/tree/master/products/mcp-server');
      console.log('Filled: GitHub URL');
    }

    // Field 1: npm package (type=text, placeholder=@org/mcp-server)
    if (inputs[1]) {
      await inputs[1].click({ clickCount: 3 });
      await inputs[1].type('@cosai-labs/toolpipe-mcp-server');
      console.log('Filled: npm package');
    }

    // Field 2: PyPI package (type=text, placeholder=mcp-server-name)
    // Skip - we don't have a PyPI package

    // Field 3: Short description (max 100 chars)
    if (inputs[3]) {
      await inputs[3].click({ clickCount: 3 });
      await inputs[3].type('238+ dev tools via MCP: JSON, QR, PDF, DNS, hash, UUID, JWT, SSL, and more');
      console.log('Filled: Description');
    }

    // Field 4: Email
    if (inputs[4]) {
      await inputs[4].click({ clickCount: 3 });
      await inputs[4].type('toolpipe-project@sharebot.net');
      console.log('Filled: Email');
    }

    await page.screenshot({ path: '/tmp/mcp-directory-filled-v2.png', fullPage: true });
    console.log('Screenshot saved: /tmp/mcp-directory-filled-v2.png');

    // Click "Submit for Review" button
    const buttons = await page.$$('button');
    for (const btn of buttons) {
      const text = await btn.evaluate(el => el.textContent.trim());
      if (text === 'Submit for Review') {
        console.log('Found "Submit for Review" button, clicking...');
        await btn.click();
        await new Promise(r => setTimeout(r, 5000));
        break;
      }
    }

    await page.screenshot({ path: '/tmp/mcp-directory-result-v2.png', fullPage: true });
    console.log('Result URL:', page.url());

    // Check for success/error messages
    const bodyText = await page.evaluate(() => document.body.innerText);
    if (bodyText.includes('success') || bodyText.includes('Success') || bodyText.includes('submitted') || bodyText.includes('review')) {
      console.log('SUCCESS: Submission appears to have gone through');
    }
    // Print any visible status messages
    const statusText = bodyText.split('\n').filter(l => l.includes('success') || l.includes('error') || l.includes('submit') || l.includes('review') || l.includes('thank'));
    if (statusText.length > 0) {
      console.log('Status messages:', statusText.slice(0, 5).join(' | '));
    }

  } catch (e) {
    console.error('Error:', e.message);
    await page.screenshot({ path: '/tmp/mcp-directory-error-v2.png', fullPage: true });
  }

  await browser.close();
  console.log('Done');
})();
