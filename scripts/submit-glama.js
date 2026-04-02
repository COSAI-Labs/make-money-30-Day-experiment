const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();

  // Try Glama.ai
  console.log('=== Glama.ai ===');
  try {
    await page.goto('https://glama.ai/mcp/servers', { waitUntil: 'networkidle2', timeout: 30000 });
    await new Promise(r => setTimeout(r, 3000));

    // Look for "Add Server" button
    const addBtn = await page.$('a[href*="add"], button:has-text("Add"), a:has-text("Add Server")');
    if (addBtn) {
      const href = await addBtn.evaluate(el => el.href || el.getAttribute('href'));
      console.log('Add Server link:', href);
      await addBtn.click();
      await new Promise(r => setTimeout(r, 3000));

      // Check for form
      const inputs = await page.$$eval('input', els => els.map(el => ({
        name: el.name, type: el.type, placeholder: el.placeholder
      })));
      console.log('Form inputs:', JSON.stringify(inputs));

      // Try to fill URL
      const urlInput = await page.$('input[type="url"], input[type="text"], input[placeholder*="github"], input[placeholder*="URL"]');
      if (urlInput) {
        await urlInput.type('https://github.com/COSAI-Labs/make-money-30day-challenge');
        console.log('Filled URL');

        const submitBtn = await page.$('button[type="submit"], button:has-text("Submit"), button:has-text("Add")');
        if (submitBtn) {
          await submitBtn.click();
          await new Promise(r => setTimeout(r, 5000));
          console.log('Submitted! URL:', page.url());
        }
      }
    } else {
      // Try direct URL
      console.log('No Add button found, trying direct URL...');
      await page.goto('https://glama.ai/mcp/servers/add', { waitUntil: 'networkidle2', timeout: 15000 });
      await new Promise(r => setTimeout(r, 2000));

      const inputs = await page.$$eval('input', els => els.map(el => ({
        name: el.name, type: el.type, placeholder: el.placeholder
      })));
      console.log('Add page inputs:', JSON.stringify(inputs));
    }

    await page.screenshot({ path: '/tmp/glama-result.png', fullPage: true });

  } catch (e) {
    console.error('Glama error:', e.message);
    await page.screenshot({ path: '/tmp/glama-error.png', fullPage: true });
  }

  // Try freepublicapis.com
  console.log('\n=== freepublicapis.com ===');
  try {
    await page.goto('https://www.freepublicapis.com/new', { waitUntil: 'networkidle2', timeout: 30000 });
    await new Promise(r => setTimeout(r, 3000));

    const inputs = await page.$$eval('input', els => els.map(el => ({
      name: el.name, type: el.type, placeholder: el.placeholder, id: el.id
    })));
    console.log('Form inputs:', JSON.stringify(inputs));

    // Look for URL/documentation input
    const allInputs = await page.$$('input');
    for (let i = 0; i < allInputs.length; i++) {
      const ph = await allInputs[i].evaluate(el => el.placeholder);
      if (ph && (ph.toLowerCase().includes('url') || ph.toLowerCase().includes('link') || ph.toLowerCase().includes('doc'))) {
        await allInputs[i].type('https://toolpipe.dev/docs');
        console.log(`Filled input ${i} (placeholder: ${ph})`);
        break;
      }
    }

    await page.screenshot({ path: '/tmp/freepublicapis-result.png', fullPage: true });

  } catch (e) {
    console.error('freepublicapis error:', e.message);
  }

  await browser.close();
  console.log('\nDone');
})();
