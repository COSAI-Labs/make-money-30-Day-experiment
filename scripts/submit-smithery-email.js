const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();

  console.log('=== Smithery.ai Email Login ===');
  try {
    await page.goto('https://smithery.ai/new', { waitUntil: 'networkidle2', timeout: 30000 });
    await new Promise(r => setTimeout(r, 2000));

    // Fill email
    const emailInput = await page.$('input[name="email"]');
    if (emailInput) {
      await emailInput.type('toolpipe-project@sharebot.net');
      console.log('Filled email: toolpipe-project@sharebot.net');

      // Find and click submit/continue button
      const buttons = await page.$$('button');
      for (const btn of buttons) {
        const text = await btn.evaluate(el => el.textContent.trim());
        const type = await btn.evaluate(el => el.type);
        console.log(`  Button: "${text}" (type=${type})`);
      }

      // Click the submit button
      const submitBtn = await page.$('button[type="submit"]');
      if (submitBtn) {
        await submitBtn.click();
        console.log('Clicked submit');
        await new Promise(r => setTimeout(r, 5000));

        const text = await page.evaluate(() => document.body.innerText.substring(0, 500));
        console.log('After submit:', text.substring(0, 300));
        console.log('URL:', page.url());
      }
    }

    await page.screenshot({ path: '/tmp/smithery-email.png', fullPage: true });

  } catch (e) {
    console.error('Error:', e.message);
  }

  // Try Glama add server
  console.log('\n=== Glama.ai Add Server ===');
  try {
    await page.goto('https://glama.ai/mcp/servers', { waitUntil: 'networkidle2', timeout: 30000 });
    await new Promise(r => setTimeout(r, 2000));

    // Find the Add Server link by evaluating all links
    const addLink = await page.evaluate(() => {
      const links = Array.from(document.querySelectorAll('a'));
      for (const l of links) {
        if (l.textContent.includes('Add') && l.textContent.includes('Server')) {
          return l.href;
        }
      }
      // Also check buttons
      const btns = Array.from(document.querySelectorAll('button'));
      for (const b of btns) {
        if (b.textContent.includes('Add') && b.textContent.includes('Server')) {
          return 'button:' + b.textContent.trim();
        }
      }
      return null;
    });

    if (addLink) {
      console.log('Found Add Server:', addLink);
      if (addLink.startsWith('http')) {
        await page.goto(addLink, { waitUntil: 'networkidle2', timeout: 15000 });
      }
      await new Promise(r => setTimeout(r, 2000));

      const inputs = await page.$$eval('input', els => els.map(el => ({
        name: el.name, type: el.type, placeholder: el.placeholder
      })));
      console.log('Inputs:', JSON.stringify(inputs));
    } else {
      console.log('No Add Server link found');
      // Print all link texts containing relevant keywords
      const relevantLinks = await page.evaluate(() => {
        return Array.from(document.querySelectorAll('a')).filter(a =>
          a.textContent.toLowerCase().includes('add') ||
          a.textContent.toLowerCase().includes('submit') ||
          a.textContent.toLowerCase().includes('register')
        ).map(a => ({ text: a.textContent.trim().substring(0, 50), href: a.href }));
      });
      console.log('Relevant links:', JSON.stringify(relevantLinks));
    }

    await page.screenshot({ path: '/tmp/glama-servers.png', fullPage: true });

  } catch (e) {
    console.error('Glama error:', e.message);
  }

  await browser.close();
  console.log('\nDone');
})();
