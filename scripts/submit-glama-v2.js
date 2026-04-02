const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();

  // Try Glama.ai direct add URL
  console.log('=== Glama.ai ===');
  try {
    await page.goto('https://glama.ai/mcp/servers/new', { waitUntil: 'networkidle2', timeout: 30000 });
    await new Promise(r => setTimeout(r, 3000));

    let inputs = await page.$$eval('input', els => els.map(el => ({
      name: el.name, type: el.type, placeholder: el.placeholder
    })));
    console.log('Inputs on /new:', JSON.stringify(inputs));

    if (inputs.length === 0) {
      // Try /add
      await page.goto('https://glama.ai/mcp/servers/add', { waitUntil: 'networkidle2', timeout: 15000 });
      await new Promise(r => setTimeout(r, 2000));
      inputs = await page.$$eval('input', els => els.map(el => ({
        name: el.name, type: el.type, placeholder: el.placeholder
      })));
      console.log('Inputs on /add:', JSON.stringify(inputs));
    }

    // Get page text for context
    const text = await page.evaluate(() => document.body.innerText.substring(0, 1000));
    console.log('Page text:', text.substring(0, 500));

    // Look for any links containing 'add' or 'submit'
    const links = await page.$$eval('a', els => els.filter(el =>
      el.href && (el.href.includes('add') || el.href.includes('submit') || el.href.includes('new'))
    ).map(el => ({ text: el.textContent.trim().substring(0, 50), href: el.href })));
    console.log('Relevant links:', JSON.stringify(links.slice(0, 10)));

    await page.screenshot({ path: '/tmp/glama-v2.png', fullPage: true });

  } catch (e) {
    console.error('Error:', e.message);
    await page.screenshot({ path: '/tmp/glama-error-v2.png', fullPage: true });
  }

  // Try Smithery without auth (just browse to see if there's a submit form)
  console.log('\n=== Smithery.ai ===');
  try {
    await page.goto('https://smithery.ai/new', { waitUntil: 'networkidle2', timeout: 30000 });
    await new Promise(r => setTimeout(r, 3000));

    const text = await page.evaluate(() => document.body.innerText.substring(0, 500));
    console.log('Smithery page:', text.substring(0, 300));

    const inputs = await page.$$eval('input', els => els.map(el => ({
      name: el.name, type: el.type, placeholder: el.placeholder
    })));
    console.log('Inputs:', JSON.stringify(inputs));

    await page.screenshot({ path: '/tmp/smithery-new.png', fullPage: true });

  } catch (e) {
    console.error('Smithery error:', e.message);
  }

  await browser.close();
  console.log('\nDone');
})();
