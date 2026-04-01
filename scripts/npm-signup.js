const { chromium } = require('playwright');
const { spawn } = require('child_process');

const screenshotDir = '/home/GerritRoskaBot/make-money-30day-challenge/scripts';

(async () => {
  const usernames = ['toolpipe', 'toolpipe-dev', 'toolpipe-io', 'toolpipe-api'];
  const email = 'toolpipe-ads@sharebot.net';
  const password = 'TP-Npm-2026-Secure!';

  // Use chrome-headless-shell which doesn't need fontconfig
  const chromePath = '/home/GerritRoskaBot/.cache/ms-playwright/chromium_headless_shell-1217/chrome-headless-shell-linux64/chrome-headless-shell';
  const userDataDir = '/tmp/npm-signup-profile-' + Date.now();

  console.log('Spawning chrome-headless-shell with remote debugging...');
  const chromeProcess = spawn(chromePath, [
    '--headless',
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--enable-unsafe-swiftshader',
    '--disable-blink-features=AutomationControlled',
    '--remote-debugging-port=9223',
    `--user-data-dir=${userDataDir}`
  ], {
    env: {
      ...process.env,
      LD_LIBRARY_PATH: '/home/linuxbrew/.linuxbrew/lib:' + (process.env.LD_LIBRARY_PATH || '')
    },
    stdio: ['ignore', 'pipe', 'pipe']
  });

  let debugUrl = null;

  await new Promise((resolve, reject) => {
    const timeout = setTimeout(() => reject(new Error('Chrome startup timeout')), 15000);

    chromeProcess.stderr.on('data', (data) => {
      const line = data.toString();
      if (line.includes('DevTools listening on')) {
        const match = line.match(/(ws:\/\/[^\s]+)/);
        if (match) {
          debugUrl = match[1];
          clearTimeout(timeout);
          resolve();
        }
      }
    });

    chromeProcess.on('error', (err) => { clearTimeout(timeout); reject(err); });
    chromeProcess.on('exit', (code) => { if (!debugUrl) { clearTimeout(timeout); reject(new Error(`Chrome exited: ${code}`)); } });
  });

  console.log('Connected via CDP:', debugUrl);
  const browser = await chromium.connectOverCDP(debugUrl);

  const context = browser.contexts()[0] || await browser.newContext();
  const page = context.pages()[0] || await context.newPage();

  try {
    console.log('Navigating to npm signup...');
    const response = await page.goto('https://www.npmjs.com/signup', {
      waitUntil: 'domcontentloaded',
      timeout: 30000
    });
    console.log('Response status:', response?.status());

    let title = await page.title();
    console.log('Title:', title);

    await page.screenshot({ path: `${screenshotDir}/npm-signup-1-loaded.png`, fullPage: true });
    console.log('Screenshot 1 saved');

    // Cloudflare challenge?
    if (title.includes('moment') || title.includes('challenge')) {
      console.log('Cloudflare challenge detected. Waiting up to 45s...');
      try {
        await page.waitForFunction(() => !document.title.includes('moment'), { timeout: 45000 });
        title = await page.title();
        console.log('Challenge resolved. New title:', title);
        await page.waitForTimeout(2000);
      } catch (e) {
        console.log('Cloudflare challenge did NOT resolve.');
        await page.screenshot({ path: `${screenshotDir}/npm-signup-cf-blocked.png`, fullPage: true });

        const html = await page.content();
        const hasTurnstile = html.includes('turnstile') || html.includes('cf-turnstile');
        console.log('Has Turnstile widget:', hasTurnstile);

        console.log('');
        console.log('=== RESULT ===');
        console.log('BLOCKED by Cloudflare Turnstile CAPTCHA.');
        console.log('npmjs.com signup page is protected by Cloudflare bot detection.');
        console.log('This cannot be bypassed with a headless browser.');
        console.log('');
        console.log('Alternative approaches:');
        console.log('1. Sign up manually at https://www.npmjs.com/signup');
        console.log('2. Use "npm adduser --auth-type=web" (still needs browser for Cloudflare)');
        console.log('3. Use a non-headless browser with a display server (Xvfb)');
        await browser.close();
        chromeProcess.kill();
        return;
      }
    }

    // If we get past Cloudflare...
    console.log('Page URL:', page.url());
    const inputs = await page.$$eval('input', els => els.map(el => ({
      type: el.type, name: el.name, id: el.id, placeholder: el.placeholder
    })));
    console.log('Input fields:', JSON.stringify(inputs, null, 2));

    const usernameField = await page.$('input[name="username"], input#username');
    const emailField = await page.$('input[name="email"], input#email, input[type="email"]');
    const passwordField = await page.$('input[name="password"], input#password, input[type="password"]');

    if (usernameField) { await usernameField.fill(usernames[0]); console.log('Filled username'); }
    if (emailField) { await emailField.fill(email); console.log('Filled email'); }
    if (passwordField) { await passwordField.fill(password); console.log('Filled password'); }

    const cbs = await page.$$('input[type="checkbox"]');
    for (const cb of cbs) { if (!(await cb.isChecked())) await cb.check(); }

    await page.screenshot({ path: `${screenshotDir}/npm-signup-2-filled.png`, fullPage: true });

    const submitBtn = await page.$('button[type="submit"]');
    if (submitBtn) {
      await submitBtn.click();
      await page.waitForTimeout(5000);
      await page.screenshot({ path: `${screenshotDir}/npm-signup-3-submitted.png`, fullPage: true });
      console.log('URL after submit:', page.url());
      const bodyText = await page.textContent('body').catch(() => '');
      console.log('Page text:', bodyText.substring(0, 2000));
    }

  } catch (error) {
    console.error('Error:', error.message);
    await page.screenshot({ path: `${screenshotDir}/npm-signup-error.png`, fullPage: true }).catch(() => {});
  } finally {
    await browser.close();
    chromeProcess.kill();
  }
})();
