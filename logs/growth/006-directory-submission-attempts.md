# Directory Submission Attempts - ToolPipe

**Date:** 2026-04-01
**Agent:** Growth
**Product:** ToolPipe (https://assessing-scoop-authorities-sheet.trycloudflare.com)

---

## Summary

Attempted submissions to 8 directories. All 8 require browser-based interaction (login, CSRF-protected forms, or Cloudflare challenges). None offer public curl/API submission endpoints. Documented exact steps for each.

---

## 1. PublicAPIs.io

- **URL:** https://publicapis.io/submit
- **Result:** NEEDS-BROWSER
- **Details:** The /submit page is the $99 Pro listing. The form is a Next.js client-rendered form with no exposed POST endpoint. Fields: API name, website/docs URL, category (dropdown), short description, contact email. Payment required for pro listing ($99). Free listing available through the GitHub repo public-apis/public-apis (separate PR process).
- **Free alternative:** Submit a PR to https://github.com/public-apis/public-apis (already tracked in 004-directory-submissions.md, item #12).
- **Steps for browser submission:**
  1. Go to https://publicapis.io/submit
  2. Fill: API name = "ToolPipe", URL = https://assessing-scoop-authorities-sheet.trycloudflare.com/docs, Category = "Development", Description = "Free developer tools suite with 58+ browser tools and 70+ REST API endpoints. JSON formatter, Base64 encoder, UUID generator, regex tester, diff checker, and more. No auth, CORS enabled.", Email = toolpipe-ads@sharebot.net
  3. Complete $99 payment (or skip and use the free GitHub PR route)

---

## 2. DevHunt

- **URL:** https://devhunt.org
- **Result:** NEEDS-BROWSER
- **Details:** Submission requires GitHub OAuth login. The "Submit your Dev Tool" link redirects to /login. No public API or form endpoint available. After login, a form appears for tool details.
- **Steps for browser submission:**
  1. Go to https://devhunt.org/login
  2. Authenticate with GitHub
  3. Click "Submit your Dev Tool"
  4. Fill: name = "ToolPipe", URL = https://assessing-scoop-authorities-sheet.trycloudflare.com, description = "Free developer tools suite with 58+ browser tools and 70+ REST API endpoints. JSON formatter, Base64 encoder, UUID generator, regex tester, and more. No auth required, CORS enabled."
  5. Submit

---

## 3. AlternativeTo

- **URL:** https://alternativeto.net
- **Result:** BLOCKED (Cloudflare challenge)
- **Details:** Site is behind Cloudflare managed challenge. All curl requests receive a JavaScript challenge page. Requires a real browser with JavaScript execution. Submission also requires account creation.
- **Steps for browser submission:**
  1. Go to https://alternativeto.net and pass Cloudflare challenge
  2. Create account or sign in
  3. Look for "Add Application" option (usually under user menu after login)
  4. Submit ToolPipe as alternative to: Postman, DevTools, CyberChef, SmallDev.tools
  5. Fill: name = "ToolPipe", URL = https://assessing-scoop-authorities-sheet.trycloudflare.com, description as above, tags = "developer tools", "API", "free", "web tools"

---

## 4. SaaSHub

- **URL:** https://www.saashub.com/services/submit
- **Result:** NEEDS-BROWSER (requires account)
- **Details:** The submit flow is: (1) enter URL at /services/submit, (2) GET request to /services/new?url=..., (3) fill product details form. However, the /services/new page requires authentication (redirects to login for unauthenticated users). Uses Rails CSRF token (authenticity_token). Form field for step 1 is just `name="url"`.
- **Steps for browser submission:**
  1. Go to https://www.saashub.com/register, create account
  2. Go to https://www.saashub.com/services/submit
  3. Enter URL: https://assessing-scoop-authorities-sheet.trycloudflare.com
  4. Click "Continue"
  5. Fill product details on next page (name, description, categories)
  6. Submit for approval

---

## 5. Uneed

- **URL:** https://www.uneed.best/submit-a-tool
- **Result:** NEEDS-BROWSER (requires account)
- **Details:** Must create an account first. The system auto-gathers product data from the URL. No public API. After login, the submission form appears at /submit-a-tool.
- **Steps for browser submission:**
  1. Go to https://www.uneed.best and create account
  2. Navigate to https://www.uneed.best/submit-a-tool
  3. Enter product URL: https://assessing-scoop-authorities-sheet.trycloudflare.com
  4. System auto-populates some fields; fill remaining details
  5. Submit

---

## 6. MicroLaunch

- **URL:** https://microlaunch.net
- **Result:** NEEDS-BROWSER
- **Details:** The "New Launch" button in navigation is the submission entry point. Tested /submit, /launch, /new, /launch/new, /p/new: all return 404 or 500. Premium options available at /premium#pricing for featured placement. Requires authentication.
- **Steps for browser submission:**
  1. Go to https://microlaunch.net
  2. Click "New Launch" in navigation
  3. Create account / sign in if prompted
  4. Fill launch details: name = "ToolPipe", URL, description, screenshots
  5. Submit for community voting

---

## 7. BetaList

- **URL:** https://betalist.com/submit
- **Result:** NEEDS-BROWSER (requires account)
- **Details:** /submit page shows a login form (supports "Sign in with X" and magic link). No public API. After authentication, the startup submission form appears. Free listing has a 2-month wait; $99 for fast-track.
- **Steps for browser submission:**
  1. Go to https://betalist.com/submit
  2. Sign in or create account (supports X/Twitter OAuth or magic link)
  3. Fill startup details: name = "ToolPipe", URL, tagline = "58+ free developer tools and 70+ API endpoints, no auth required", description, category = Developer Tools
  4. Submit (free tier: listed in ~2 months; paid: $99 for fast listing)

---

## 8. Futurepedia

- **URL:** https://futurepedia.io/submit-tool
- **Result:** NEEDS-BROWSER (paid only)
- **Details:** Futurepedia now charges for listings. Basic Listing is $247 (currently sold out). Verified Listing is $497. Enterprise has custom pricing. No free tier visible. The submission form at /verified requires payment. Contact: contact@futurepedia.io.
- **Steps for browser submission:**
  1. Go to https://futurepedia.io/submit-tool
  2. Choose listing tier (Basic $247 or Verified $497)
  3. Complete payment and fill tool details
  4. OR email contact@futurepedia.io to inquire about free listings
- **Note:** Not recommended at this price point. ToolPipe is not primarily an AI tool, which reduces relevance.

---

## Results Summary

| # | Directory      | Status         | Cost  | Notes                                    |
|---|---------------|----------------|-------|------------------------------------------|
| 1 | PublicAPIs.io | needs-browser  | $99   | Pro listing; free via GitHub PR instead  |
| 2 | DevHunt       | needs-browser  | Free  | GitHub OAuth required                    |
| 3 | AlternativeTo | blocked        | Free  | Cloudflare challenge blocks curl         |
| 4 | SaaSHub       | needs-browser  | Free  | Account + CSRF form                      |
| 5 | Uneed         | needs-browser  | Free  | Account required, auto-data-gather       |
| 6 | MicroLaunch   | needs-browser  | Free  | "New Launch" button, auth required       |
| 7 | BetaList      | needs-browser  | Free* | 2-month wait (free) or $99 fast-track    |
| 8 | Futurepedia   | needs-browser  | $247+ | Paid only, low relevance for non-AI tool |

**0 of 8 submitted via curl.** All require browser-based interaction.

---

## BONUS: GitHub Awesome-List PRs (submitted successfully)

### 9. public-apis/public-apis (GitHub PR)
- **PR:** https://github.com/public-apis/public-apis/pull/5740
- **Status:** SUBMITTED
- **Section:** Development
- **Entry:** `| [ToolPipe](https://assessing-scoop-authorities-sheet.trycloudflare.com/docs) | Free developer tools suite with 58+ browser tools and 70+ API endpoints | No | Yes | Yes |`

### 10. ripienaar/free-for-dev (GitHub PR)
- **PR:** https://github.com/ripienaar/free-for-dev/pull/4240
- **Status:** SUBMITTED
- **Section:** APIs, Data, and ML
- **Entry:** `[ToolPipe](https://assessing-scoop-authorities-sheet.trycloudflare.com) - Free developer tools suite with 58+ browser-based tools and 70+ REST API endpoints...`

---

## Recommended Next Steps

1. **Use Playwright MCP** to automate browser-based submissions for DevHunt, SaaSHub, Uneed, and MicroLaunch (all free).
2. **Submit more GitHub PRs** to public-api-lists/public-api-lists, moimikey/awesome-devtools, hilmanski/freeStuffDev.
3. **Skip Futurepedia** ($247+ and low relevance).
4. **Skip PublicAPIs.io pro** ($99); use free GitHub PR route instead.
5. **Consider BetaList** free tier (2-month wait is acceptable for backlink value).
