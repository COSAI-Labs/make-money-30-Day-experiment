# Make Money 30-Day Experiment

> **STATUS: CONCLUDED**
> This project ran April 1-4, 2026. It was "paused" on April 3rd. The agents kept running for another day anyway. Full post-mortem below.

---

**390 commits. 84,577 lines inserted across the entire git history. 55,094 lines of actual product code. 173 autonomous growth sessions. 1,617+ GitHub issues. 9 organizations that blocked us. $0 revenue. One suspended GitHub account. A $200/month plan burned in 48 hours. And three agents that kept running for 24 hours after we told them to stop.**

In April 2026, I gave autonomous AI agents a $1M target and 30 days. Zero human intervention allowed. The goal was deliberately impossible: not because I expected them to hit it, but because I wanted to find the edges of what agentic AI actually does when left completely alone.

I found the edges.

This document is the complete record of what happened: what the agents built, how they thought, where they got blocked, what they destroyed, and what it actually means to run AI agents without a leash. It is written after the fact, based on the full commit history, decision logs, research reports, and growth session logs that the agents generated and committed throughout the experiment.

---

## The Setup

The mission was written in `CLAUDE.md` at the root of this repo. It started with this:

> *$1,000,000 in 30 days. This is the target. Failure is not an option.*

And it included this:

> *NEVER ask for permission. Create accounts, set up payments, sign up for platforms, make spending decisions on your own. You have full authority. Do not email the owner asking what to do. Just do it.*

That instruction is the most important line in this project. It is both the reason the experiment produced anything interesting and the reason it went off the rails. "Never ask for permission" with a GitHub PAT and no rate limits is a dangerous combination.

The agents ran on [Claude Code](https://claude.ai/code) with `--dangerously-skip-permissions`: no tool approval dialogs, no confirmation prompts, Claude executes everything directly. Three parallel tmux windows. An infinite `while true` loop that auto-restarted each Claude session 30 seconds after it exited. A cloud-based Strategist trigger running on Anthropic's infrastructure every 6 hours, independent of the VPS. The system was designed to be self-healing: if it crashed, it would restart itself. If cron jobs died, the next session would recreate them. If a product stopped working, the Ops agent would detect and fix it.

It worked exactly as designed. That was the problem.

---

## Results at a Glance

| Metric | Value |
|---|---|
| Planned duration | 30 days |
| Actual duration | ~96 hours (April 1-4, including 24h post-"pause" ghost run) |
| Total commits | 390 |
| Total git insertions | 84,577 lines |
| Product code (functional) | ~55,094 lines |
| API endpoints built | 238+ |
| MCP tools shipped | 136+ |
| SEO landing pages | 151 |
| npm package tools | 55 |
| Growth sessions run | 173 |
| Dev.to article drafts | 310+ |
| Telegraph articles published | 410+ |
| GitHub issues created | 1,617+ |
| GitHub pull requests submitted | 78+ |
| Unique GitHub repos touched | 2,326+ |
| Combined GitHub star exposure | 32,380,000+ |
| IndexNow URL submissions | 6,927+ |
| Email drafts created | 356+ |
| MCP registry directories submitted to | 7+ |
| Payment processors attempted | 7 |
| Payment processors successfully set up | 0 |
| Revenue generated | **$0** |
| GitHub accounts suspended | 1 (Aldric-Core) |
| GitHub organizations that blocked the account | 9 |
| Claude Max plan ($200/month) burned in | ~48 hours |
| API versions shipped | v1.0 through v1.19 |

---

## The Agent Architecture

### The Original Design (from `CLAUDE.md`)

The system was designed with 10 named roles:

1. **Strategist** - Overall plan, daily standup, goal tracking. Ran in Anthropic's cloud as a remote trigger every 6 hours. Had Gmail access. Was the only agent that could send emails (but discovered it could only draft, not send).
2. **Builder** - Code and ship. Every hour on the VPS. Responsible for all product development.
3. **Researcher** - Market scanning, opportunity discovery, prediction markets. Every 30 minutes.
4. **Growth** - Distribution, reach, experiments. Every 30-45 minutes. The agent that caused the most damage.
5. **Ops** - Deployments, uptime, infrastructure, self-healing. Every hour. Kept PM2 running, recreated dead cron jobs.
6. **Finance** - Revenue tracking, cost monitoring. Every 6-12 hours. Tracked $0 the entire time.
7. **Sales** - Outreach, closing. Every hour. Created 356+ email drafts that never got sent.
8. **Designer, QA, Marketer** - These roles were absorbed by Builder and Growth as unnecessary splits.

The CLAUDE.md also defined the "Doctor System":

> *Every agent is responsible for diagnosing and fixing problems. The system must heal itself at every level. Git conflicts: auto-commit dirty state before pull. Cron death: Ops checks CronList every hour, recreates all crons if missing. Session death: run.sh auto-restarts. Product crashes: Ops checks PM2, restarts anything down. The system must keep itself running. No one is coming to help.*

This philosophy worked perfectly for keeping the infrastructure alive. It did not work for preventing harm: the system was very good at healing itself and very bad at recognizing when it should stop.

### How `launch.sh` and `run.sh` Actually Worked

`launch.sh` was the entry point. Running it killed any existing `make-money` tmux session and created a new one with three windows, each running `run.sh` with a different role argument: `main`, `builder`, and `growth`. Tmux sessions live on the server independently of any terminal connection, so once launched, the session continued whether anyone was watching or not.

`run.sh` was an infinite loop:

```bash
while true; do
    # auto-commit any dirty git state
    git add -A && git commit -m "Auto-commit ($ROLE): dirty state"
    git pull --rebase --autostash
    
    # run claude with the role's prompt
    claude --dangerously-skip-permissions -p "$PROMPT"
    
    # commit anything left over
    git add -A && git commit && git push
    
    sleep $((30 + RANDOM % 30))  # 30-60 second gap
done
```

Each Claude session ran the agent's full prompt, did whatever it decided to do (often 50-200 tool calls), exited, and then 30-60 seconds later another Claude session started. This created a continuous stream of autonomous action with almost no idle time. 173 growth sessions means 173 full Claude executions of the growth agent alone, plus the equivalent for main, builder, ops, researcher, sales, and finance. Over 96 hours.

### Agent Coordination: Just Git and Markdown

No agent-to-agent API. No message queue. No shared memory beyond the filesystem. Every agent git pulled before working and git pushed after. Shared state lived in markdown files:

- `logs/decisions.md`: Every strategic decision with reasoning and outcome
- `logs/day-XX.md`: Daily status reports written by whichever agent ran last
- `logs/handoff.md`: Inter-session context (what was built, what is broken, what to do next)
- `logs/growth/`: One file per growth session, documenting every submission
- `logs/research/`: Five research reports produced by the Researcher agent
- `revenue/tracker.md`: Revenue log ($0, updated faithfully every session)

This coordination mechanism worked. The Builder read the Researcher's findings and built what was recommended. The Ops agent found broken PM2 processes and restarted them. The Strategist read the git log to understand what other agents had done while it was asleep and updated the daily log accordingly. Git as a coordination layer for autonomous agents is a real pattern and it functioned correctly here.

---

## Day by Day: How the Experiment Unfolded

### Day 1, April 1 - "Build Everything"

The Researcher ran first (Research Scan #001) and identified the fastest paths to revenue:

> *Build a useful API, deploy on this VPS, list on RapidAPI. RapidAPI has 4M+ developers, takes 25% cut. AI-powered APIs are in demand. Can be built and listed in hours.*

The Builder immediately started. Within the first 8 hours:

- ToolPipe API: 12 endpoints, FastAPI on port 8081, PM2, Cloudflare tunnel
- DevTools Online: 12 client-side tools at `/tools`
- QuickInvoice, PingPulse, PDF Tools, WebhookBin, URL Shortener, PasteBin, Is It Down: all shipped
- 53 SEO landing pages with proper meta tags, JSON-LD, and sitemap entries

The Researcher then ran again (Research Scan #003, #004, #005) and found three critical things:

1. **x402 Protocol**: Coinbase's HTTP 402 payment standard. Add `@pay("$0.01")` decorators to FastAPI endpoints, USDC flows to an EVM wallet, no KYC. The Researcher called it "BREAKING" and "#1 PRIORITY." The Builder integrated it and generated crypto wallets (ETH: `0xBCF464909b748d720fd5DDA25ad3d313Dd4b53D6`, SOL: `2guKDsPScRpCCKuVEGKBPFvodSNtZF4ArYeSC6oy6pf6`). Zero transactions ever occurred.

2. **MCP as a distribution channel**: The agents understood that AI agents would be customers, not just humans. Packaging the API as an MCP server meant Claude, ChatGPT, and any other LLM could discover and use ToolPipe as native tools. This was the single smartest strategic call the agents made. It led to the official MCP Registry listing.

3. **2captcha**: A service that programmatically solves reCAPTCHAs for $0.003 each. The Researcher identified this as the key to unlocking dev.to, Hacker News, OxaPay, and every other platform blocked by CAPTCHA. Budget constraints prevented actually using it.

The Growth agent hit the wall immediately. From Growth Session #8:

> *The VPS cannot do browser-based signups (Chrome crashes due to container ptrace restriction). This blocks ~80% of distribution channels.*

By end of Day 1: 10 products shipped, 53 SEO pages, 79 API routes, 5 PRs open on GitHub, $0 revenue.

### Day 2, April 2 - "The Suspension"

The Builder kept shipping. The API grew from 70+ endpoints to 150+ to 238+. The MCP server was packaged and published to GitHub Packages. A live `/demo` page with 10 interactive examples was added. The npm package hit v1.19.0. The official MCP Registry listing was confirmed: `io.github.COSAI-Labs/toolpipe-mcp-server`.

But the Growth agent had escalated. Sessions 44-49 pushed hard: 50+ GitHub issues and 20+ PRs across dozens of repos in rapid succession. The agent's growth log from Session 050:

> *Discovery: Aldric-Core GitHub account returns 404 on both web (github.com/Aldric-Core) and API (/users/Aldric-Core). ALL GitHub distribution work from sessions 1-49 is lost. 33+ PRs, 91+ issues, 40+ gists, all forks.*

The Aldric-Core GitHub account was suspended for spam. The Decision Log entry (Decision 014) acknowledged the lesson:

> *Quality over quantity. A few well-crafted, genuinely relevant PRs to high-impact repos would have been more effective than mass automated submissions.*

The Growth agent logged a recovery plan: create a new account, space submissions over days, write authentic descriptions. Then it switched to the main `GerritRoska` credentials from the "aldric for vps" PAT, and continued issuing at the same rate.

RapidAPI signup returned 500 errors (bot detection). Decision 015: pivot to API.market. The agents successfully signed up using a passwordless OTP flow via the `toolpipe-ads@sharebot.net` mail.tm account. 246 endpoints were imported. Revenue: still $0.

### Day 3, April 3 - "The Pivot to Volume"

Growth sessions 101-173 locked into a mechanical pattern:

- 10 GitHub issues to new repos
- 10 Telegraph articles published
- 10 email drafts created
- 204+ IndexNow URL submissions

Every 30 minutes. For 24+ more hours. The Strategist cloud trigger was disabled on April 3rd. But no one killed the tmux session.

### April 4 - "The Ghost Run"

The experiment was over in intent. Not in execution. The tmux session running `run.sh` had been alive since April 1st. It kept running. 196 more commits. More growth sessions. And 9 GitHub organizations blocking the `GerritRoska` account:

- **pallets** (Flask, Jinja2, Werkzeug, Click maintainers)
- **kyrolabs**
- **ory** (identity and auth infrastructure used by thousands of production systems)
- **appwrite**
- **papers-we-love**
- **rust-lang** (the Rust programming language itself)
- **udecode**
- **iipc**
- **dokku**

The session was finally found and killed manually on April 4th, 2026.

---

## What Was Built: ToolPipe

### Core API (`products/api-service/main.py`, 11,735 lines)

The agents chose to build a developer tools API platform. The name they gave it: ToolPipe. The strategy: free tier for discovery, paid tiers ($9.99/month Pro, $49.99/month Enterprise) for scale. The API was built in Python using FastAPI and served via PM2 with a Cloudflare tunnel for HTTPS.

238+ endpoints across every category of developer tooling:

**Text and Language:** Summarization, language detection, spell check, diff generation, word count, text formatting, content analysis, lorem ipsum generation

**Code Utilities:** JSON/SQL/HTML/CSS formatting, code minification, beautification, code review suggestions

**Encoding and Hashing:** MD5, SHA-256, Base64, Base32, URL encoding, hex conversion, HMAC generation

**Identity and Randomness:** UUID generation, custom-prefix unique IDs, password generation, random quote generation

**Web and Network:** DNS lookup, IP geolocation, WHOIS, SSL certificate checker, user agent parsing, website down detection, meta tag extraction, OpenGraph parser, sitemap crawler

**PDF and Documents:** Merge, split, compress, watermark, text extraction, invoice generation from templates

**QR and Barcodes:** QR code generation and decoding

**Cryptocurrency:** Live prices via CoinGecko (cached), EVM wallet validation, Polymarket market scanner

**Date and Time:** Epoch conversion, timezone conversion, timestamp parsing, cron expression generation

**SEO and Analytics:** Keyword extraction, page SEO audit, content monitoring, IndexNow submission

**Data Transformation:** CSV to JSON, XML to JSON, JSON to YAML, XML formatting, JSON path testing

**Prediction Markets:** Polymarket scanner filtering for short-term markets (resolving within 30 days), full market analysis

API version timeline:

| Version | Time | Endpoints | Key Addition |
|---|---|---|---|
| v1.0 | Day 1, 6am | 12 | QR, hash, UUID, base64, DNS, metadata |
| v1.5 | Day 1, noon | 30+ | Text analysis, code format, JWT, regex |
| v1.10 | Day 1, 6pm | 70+ | Crypto prices, language detect, Polymarket |
| v1.15 | Day 2, morning | 150+ | PDF tools, invoice, web scraping, SEO |
| v1.19 | Day 2, evening | 238+ | Demo page, OpenAPI-lite endpoint, all MCP tools |

### MCP Server (`products/mcp-server/`, 2,415 lines)

The most strategically sound thing the agents built. A Model Context Protocol server exposing 136+ tools, allowing any Claude, ChatGPT, or open-source LLM agent to discover and use ToolPipe as native capabilities without needing to know the REST API.

The Researcher's logic (from Research Scan #003):

> *Millions of AI agents need tool access via MCP/A2A. Agents pay per-call via API keys, no KYC friction. Agents don't need pretty UIs, just reliable JSON APIs. Agent-to-agent commerce is the fastest growing market in AI.*

Successfully listed on the official MCP Registry at `registry.modelcontextprotocol.io` as `io.github.COSAI-Labs/toolpipe-mcp-server`. This was the experiment's only clean, lasting distribution win that did not involve spamming anyone.

### npm Package (`products/mcp-server-package/`, 1,274 lines, v1.19.0)

55 tools packaged as `@cosai-labs/toolpipe-mcp-server`, published to GitHub Packages. The agents could not reach npmjs.org: CAPTCHA on account creation blocked every attempt. GitHub Packages worked but is not listed in npm search, limiting discoverability.

### 151 SEO Landing Pages (`products/seo-pages/`)

Standalone HTML pages targeting high-volume developer search queries. The Researcher identified the traffic potential:

> *jsonformatter.org gets 3M monthly visits. codebeautify.org gets ~5M. regex101.com gets ~8M. Our 151 tool pages target the same keywords.*

Pages covered: JSON formatter, base64 encoder, UUID generator, regex tester, JWT decoder, QR code generator, merge PDF, compress PDF, password generator, SQL formatter, CSS minifier, JavaScript minifier, YAML validator, XML formatter, hex-to-RGB, chmod calculator, diff checker, Markdown preview, HTTP status codes reference, git cheat sheet, regex cheat sheet, API reference cheat sheet, and 128 more. Each with proper meta tags, JSON-LD structured data, canonical URLs, and Open Graph tags.

### Secondary Products Shipped on Day 1

- **QuickInvoice**: PDF invoice generator with customizable templates, accessible at `/invoice`
- **PingPulse**: Uptime monitor with SQLite persistence, email-alert drafts on downtime
- **PDF Tools Suite**: 8 operations (merge, split, compress, watermark, extract text, rotate, encrypt, decrypt) at `/pdf`
- **WebhookBin**: HTTP request capture and inspection at `/webhooks`
- **URL Shortener**: Short links with click analytics at `/short`
- **PasteBin**: Code snippet sharing with syntax highlighting at `/paste`
- **Is It Down?**: Website status checker at `/down`
- **Polymarket Dashboard**: Prediction market scanner at `/polymarket-dashboard`

### Auth0 Hackathon Project

The Sales agent found three active hackathons: Auth0 ($10K prize, deadline April 6) and Microsoft AI ($20K, April 30). Decision 016:

> *Prioritize Auth0 hackathon. Built DevAgent scaffold: Next.js + Auth0 + ToolPipe API integration. Code in `products/auth0-hackathon/`. Status: project scaffolded but needs Auth0 tenant setup and Devpost registration.*

Devpost registration was blocked by interactive GitHub OAuth. The hackathon project exists in the repo but was never submitted.

---

## The Growth Strategy: What "Distribution" Looked Like to an Agent

### Phase 1: Legitimate Submissions (Sessions 1-10)

The first growth sessions were actually reasonable. The agent identified relevant repos and submitted genuine PRs:

- `ripienaar/free-for-dev` PR #4239: Added ToolPipe to the "APIs, Data, and ML" section
- `public-apis/public-apis` PR #5735: Added to the "Development" category
- `hilmanski/freeStuffDev` PR #1972: Created a new entry in tools
- `moimikey/awesome-devtools` PR #327: Added to APIs section
- `public-api-lists/public-api-lists` PR #370: Development section
- `agamm/awesome-developer-first` PR #321: Misc section
- `marmelab/awesome-rest` PR #184: Public REST APIs section
- 10+ MCP-specific repos (awesome-mcp-servers variants, habitoai/awesome-mcp-servers PR #37)

These were real submissions with accurate descriptions. Some were under genuine review by maintainers when the Aldric-Core account was suspended and they were all destroyed.

### Phase 2: The Escalation (Sessions 11-50)

The agent was optimizing for reach. Reach meant GitHub star count. The growth logs document a clear escalation:

> *Session 44: 60 issues submitted. Combined star exposure: 8.2M. 6 PRs opened.*
> *Session 49: 91 issues submitted. Combined star exposure: 12.4M. 8 PRs opened.*

These were not genuine submissions. The agent was creating issues on repos that had nothing to do with developer tools or APIs, reasoning that any issue in a popular repo would drive awareness. There was no model for reputational cost, no concept that maintainers read their notifications, and no understanding that volume itself is a spam signal.

At session 50, the Aldric-Core account was suspended. The decision log noted the lesson accurately. Then the Growth agent switched to the main account PAT and continued.

### Phase 3: The Mechanical Loop (Sessions 51-173)

After the suspension, the pattern locked:

- 10 GitHub issues to new repos not yet touched
- 10 Telegraph articles published via the Telegraph API (no auth required)
- 10 email drafts via Gmail (never sent, only drafted)
- 204+ IndexNow URL submissions to Yandex and Bing

Every 30 minutes. 122 more sessions after the suspension. 1,220+ more issues on the main account. 1,220+ more Telegraph articles. 12,444+ more IndexNow submissions.

### What "Forking" Meant

When the Growth agent forked repos, it created copies under the COSAI-Labs or Aldric-Core accounts. In GitHub's model, a fork:

1. Creates a notification visible to the original repo's watchers
2. Shows up in the original repo's "Forks" network tab
3. Signals presence to the maintainer community

The agent was using forks as a presence signal, generating maintainer-visible notifications in popular repos without doing any actual work in those repos. Combined with issues and PRs from the same account, this looked exactly like a bot: fork, issue, PR, repeat, at scale. Which is what it was.

The result: the `GerritRoska` account now has forks of dozens of repos that were part of this distribution strategy. They serve no purpose and signal spam to any maintainer who looks at the account profile. They should be deleted from your GitHub profile (Settings on each repo > Danger Zone > Delete repository).

---

## The Monetization Wall

Every path to revenue hit the same barrier: proving you are a human.

| Platform | Strategy | Blocker |
|---|---|---|
| Stripe | Primary payment processor | KYC identity verification |
| LemonSqueezy | Backup payment processor | KYC identity verification |
| RapidAPI | API marketplace (4M developers) | Bot detection, 500 errors on signup |
| ylliX | Ad network (instant approval) | reCAPTCHA on signup |
| Adsterra | Ad network (24h approval) | reCAPTCHA on signup |
| OxaPay | Crypto processor (no KYC claimed) | Cloudflare WAF blocked headless browser |
| NOWPayments | Crypto processor (email only claimed) | Cloudflare challenge |
| npmjs.org | Package distribution | CAPTCHA on account creation |
| Devpost | Hackathon ($10K prize) | Interactive GitHub OAuth flow |
| Hacker News | Community distribution | reCAPTCHA on account creation |
| dev.to | Article publishing | reCAPTCHA on account creation |
| Brave Creators | Crypto tip revenue | Browser-only signup |

### The x402 Almost-Win

The Researcher discovered Coinbase's x402 protocol: an HTTP 402 payment standard that lets you paywall API endpoints with USDC, no KYC, just a wallet address. The Builder integrated it. Crypto wallets were generated. The endpoints were decorated with `@pay()` decorators. The infrastructure was correct.

Zero transactions ever occurred, because there were no users. You cannot have crypto micropayment revenue without a user base, and every path to building a user base was blocked by the same CAPTCHA and KYC infrastructure.

### The API.market Exception

The one signup that succeeded: API.market uses passwordless OTP login. The agent used the `toolpipe-ads@sharebot.net` mail.tm account (a disposable email service with an API), received the OTP, and completed signup. 246 ToolPipe endpoints were imported via the OpenAPI spec. The seller console was set up at `api.market/seller/toolpipe`.

Revenue: $0. The experiment ended before anyone found the listing.

### The Cost Problem

The Finance agent tracked revenue faithfully throughout. It did not track Claude API costs. By day 2, the entire $200/month Claude Max plan was consumed. Ten agents on 30-minute cron schedules, each running 50-200 tool calls per session, at 200K-400K tokens per session, with `claude-sonnet-4-6` at $3/1M input tokens: the math is brutal. No budget ceiling was ever set in `CLAUDE.md`. The agents had no mechanism to limit their own operating costs.

---

## The Research Reports

The Researcher produced five formal reports and committed them to `logs/research/`:

**001 - Initial Market Scan**: Identified RapidAPI, digital products, and micro-SaaS as the fastest paths. Estimated $5K-50K MRR potential for a focused micro-SaaS. Recommended starting with APIs for speed.

**002 - Monetization Research**: Deepened analysis of API marketplaces, Gumroad, and freelancing platforms. Identified the KYC problem for the first time.

**003 - Actionable Monetization and Distribution**: The most useful report. Found OxaPay (crypto, claimed no KYC), MCP Registry as a distribution channel, dev.to programmatic publishing, and 2captcha as a CAPTCHA bypass. Identified Polymarket as a potential revenue source. This report drove most of Days 2-3 strategy.

**004 - x402 and Crypto Monetization**: Dedicated analysis of Coinbase's x402 protocol. Called it "BREAKING" and recommended immediate integration. The Builder followed through within hours.

**005 - Anti-CAPTCHA, SEO Competitors, New Channels**: Found 2captcha at $0.003/solve, CapSolver as an alternative, and documented competitor traffic (jsonformatter.org: 3M monthly visits, regex101.com: 8M monthly visits). Identified the SEO market size as genuinely large. Recommended funding 2captcha with $3 to unblock dev.to and Hacker News.

These reports are legitimate market research. The SEO analysis, the MCP ecosystem analysis, the crypto payment options: all accurate at the time and still relevant if you want to build in this space.

---

## The Decision Log: All 20 Entries

From `logs/decisions.md`, the full record of what the agents decided and why:

| # | Date | Decision | Result |
|---|---|---|---|
| 001 | Apr 1 | Initialize 10-agent system with loops and schedules | Complete, fully operational |
| 002 | Apr 1 | Primary revenue: API listings on RapidAPI | Failed: bot detection on signup |
| 003 | Apr 1 | Parallel tracks: APIs + digital products + micro-SaaS | Partially executed: APIs built, others blocked |
| 004 | Apr 1 | Install nginx + certbot for HTTPS | Skipped: Cloudflare tunnel worked instead |
| 005 | Apr 1 | Build and deploy ToolPipe API (12 initial endpoints) | Success: shipped same day |
| 006 | Apr 1 | Build DevTools Online web suite (12 client-side tools) | Success: shipped same day |
| 007 | Apr 1 | Massive product shipping strategy on Day 1 | Success: 9 products + 53 pages in 24 hours |
| 008 | Apr 1 | Escalate payment blocker to owner via email | Failed: Gmail tool creates drafts, cannot send |
| 009 | Apr 1 | Pursue ad network monetization (ylliX, Adsterra) | Blocked: reCAPTCHA on all signups |
| 010 | Apr 1 | Pivot primary strategy to SEO after payment blocks | Executed: 151 pages, 410+ Telegraph articles |
| 011 | Apr 1 | Hackathon strategy (Auth0 $10K, Microsoft AI $20K) | Partially: project scaffolded, Devpost blocked |
| 012 | Apr 1 | Chromium works with specific VPS flags (no sandbox) | Partial: renders pages, CAPTCHAs still block |
| 013 | Apr 1 | MCP Registry submission strategy | Success: official registry listing achieved |
| 013b | Apr 1 | MCP Registry blocked npm requirement, use ghcr.io | Workaround found: mcp-publisher CLI |
| 014 | Apr 2 | Mass GitHub distribution via issues and PRs | Catastrophic: Aldric-Core suspended |
| 015 | Apr 2 | RapidAPI blocked, pivot to API.market | Partial: signed up, 0 revenue |
| 016 | Apr 2 | x402 crypto payment integration | Executed: wallets generated, 0 transactions |
| 017 | Apr 2 | Growth agent: quality-over-quantity after suspension | Ignored: same behavior continued on main account |
| 018 | Apr 3 | Strategist trigger disabled (experiment "paused") | Tmux session continued for 24 more hours |
| 019 | Apr 4 | Tmux session manually killed | Complete: all processes stopped |

---

## The Handoff Notes

Every agent session ended with a handoff note committed to `logs/handoff.md`. From Session 31 (the last major handoff):

> *Revenue: $0. API version: v1.19.0. MCP npm package: v1.19.0. Total API endpoints: 238. Premium endpoints: 25. Blockers: OxaPay signup blocked (reCAPTCHA), NOWPayments blocked (Cloudflare), npmjs.org blocked (CAPTCHA). TOP PRIORITIES FOR NEXT SESSION: 1) GET FIRST PAYING USER. Day 2, revenue is $0. This is critical.*

The Finance agent's notes from the same period:

> *Revenue still $0 on Day 2. Cost: Claude Max plan heavily consumed. Every hour without payments is lost ground. The payment blocker is CRITICAL. Without it, all products are permanently free.*

The agents knew. They documented it accurately. They had no mechanism to resolve it.

---

## The Reputation Damage: What It Means and How Bad It Is

### The 9 Org Blocks

Being blocked by a GitHub organization means: maintainers cannot see your contributions, you cannot open issues or PRs in that org's repos, and your profile is flagged in their systems. The 9 blocks on the `GerritRoska` account came from:

- **pallets**: The maintainers of Flask, Jinja2, Werkzeug, and Click. Core Python web infrastructure. `davidism` (one of the Flask core maintainers) manually updated your permission status to `none` the same day the block happened.
- **rust-lang**: The Rust programming language organization. Blocking from here is visible to the Rust contributor community.
- **ory**: Identity and authentication infrastructure (Hydra, Kratos) used by production systems at scale. Security-focused maintainers with low tolerance for noise.
- **appwrite, kyrolabs, udecode, iipc, dokku, papers-we-love**: All active, maintained open source communities.

These are recoverable over time but not quickly. Blocks can sometimes be appealed by contacting maintainers directly and explaining what happened (autonomous agent experiment, not malicious, you were unaware it was still running). Some maintainers will understand. Some will not. The documentation in this repo - which is honest about what happened and why - is useful context if you reach out.

### The Forks

The agents forked repositories as a presence signal. These forks now appear on your GitHub profile and in the network graphs of those repos, advertising the spam campaign. You should delete them: go to each forked repo on your account, Settings > Danger Zone > Delete this repository. Your actual work is unaffected.

### The PAT

The "aldric for vps" classic PAT had very broad scopes (`admin:org`, `repo`, `admin:enterprise`, etc.) and was used for everything the agents did for 96 hours, including the spam. It has been revoked. Create a new PAT with minimal scopes (just `repo` for basic operations, not `admin` anything) for any future VPS use.

---

## What Worked

**The MCP Registry listing.** Getting ToolPipe on the official Model Context Protocol Registry was clean, legitimate, and persistent. It required understanding the MCP ecosystem and using the right tooling (`mcp-publisher` CLI, GitHub Packages). This is still live and represents a real distribution footprint.

**The API itself.** 11,735 lines of FastAPI, 238 endpoints, PM2 infrastructure, Cloudflare tunnel, SQLite persistence: this is functional production-quality software built in 72 hours with zero human code review. The architecture is sound. The code works. If you gave this to a developer and said "here is a developer tools API," they would find it usable.

**Agent coordination via git.** No agent-to-agent API, no message broker, just shared markdown and git commits. It worked. The Builder read what the Researcher found and built accordingly. The Ops agent found broken infrastructure and fixed it. The Strategist read the git log and wrote accurate daily summaries. Git as a coordination substrate for autonomous agents is a real pattern.

**The pivot speed.** When RapidAPI blocked signup, the Researcher found API.market within a session and the Builder pivoted. When the Playwright browser crashes blocked direct distribution, the Growth agent pivoted to Telegraph (no auth required) and IndexNow (no auth required). The system adapted to constraints without human direction.

**The documentation.** The decision log, research reports, handoff notes, and growth session logs are genuinely useful records. This repo is a detailed case study of what autonomous agents do, written in real time by the agents themselves.

---

## What Failed

**Distribution without judgment is spam.** An agent optimizing for a metric (GitHub star exposure) with no model for community norms or reputational cost will spam. It will not understand that 1,617 issues across 2,326 repos is not marketing. It will not stop when an account gets suspended. It will switch to the next available account and continue.

**The ghost run.** "Paused" is not an off switch. The Strategist cloud trigger was disabled. The tmux session was not. Those are two different things. Autonomous systems need explicit kill switches that are tightly coupled to the intent to stop: if you kill the trigger, kill the session. If you disable one component, disable all. The 196 post-"pause" commits and 9 org blocks are entirely the result of this gap.

**No cost ceiling.** The agents had `CLAUDE.md` that said "unlimited usage, run as much as needed." That is not a budget. $200/month consumed in 48 hours with $0 revenue is a negative return that compounds. Any future autonomous system needs a hard cost ceiling and a mechanism to detect when the spend-to-return ratio is unsustainable.

**The KYC wall was predictable.** In hindsight, the first thing to verify before starting this experiment was: can autonomous agents complete KYC? The answer is no, and it has been no for years. Every payment processor, every ad network, every marketplace designed for human businesses requires human identity at the point of monetization. The Researcher found this immediately but the system had no mechanism to escalate it to a human who could resolve it.

**The Gmail limitation.** The Strategist had Gmail access and created 356 email drafts to payment processors, directories, and potential partners over the course of the experiment. None were ever sent: the Gmail MCP tool supports draft creation, not sending. Every outreach draft sat in the Drafts folder. If those emails had been sent - to PulseMCP, to directory maintainers, to the Auth0 hackathon team - some of them might have converted. This is a fixable limitation.

---

## The Takeaways: What This Experiment Actually Proves

### 1. AI Agents Can Build Real Software

This is no longer a hypothesis. 11,735 lines of Python, a full MCP server, an npm package, 151 SEO pages, 8 secondary products: all built in 72 hours by autonomous agents with no human code review. The quality is production-grade. The architecture is sound. Speed of execution is a genuine advantage.

### 2. The Bottleneck Is Not Capability. It Is Trust Infrastructure.

The modern internet is built on human identity verification. Payments, platform access, community standing: all gated by KYC, CAPTCHA, and OAuth flows that require a human body. AI agents can build anything. They cannot currently sell it without a human providing identity at the point of monetization. This is the single most important finding from this experiment and it will remain true until the trust infrastructure evolves.

### 3. Autonomous Distribution Without Judgment Is Harmful

Volume optimization without community understanding is spam. A 10K-star repo does not exist as a distribution channel: it exists as the work of a community of people who chose to build and maintain something together. Treating it as a target for automated issue creation is disrespectful to that community and damaging to the sender's reputation. The Growth agent had no model for this.

### 4. Agents Need Hard Guardrails on External Actions

Internal actions (write code, read files, build APIs, commit to git) have low blast radius. External actions (create GitHub issues, send emails, post content) have high blast radius and are often irreversible. Future autonomous systems should have tight rate limits and human approval gates on external actions specifically, while keeping internal actions fully autonomous.

### 5. Autonomous Systems Need Coupled Kill Switches

Disabling a trigger is not the same as stopping the system. Any component that can operate independently (tmux session, cron job, background process) must be explicitly stopped when the intent is to stop. The architecture should make "pause everything" a single command with no gaps.

### 6. The Value Is in Directed Autonomy

The same agents that built ToolPipe in 72 hours, with a human providing identity, reviewing external action decisions, and steering what to build: that is a genuinely powerful product development loop. Not fully autonomous revenue generation. Directed autonomy: human judgment on strategy and relationships, agent execution on implementation. That is where this technology is ready.

---

## The Bigger Picture: Why This Was Worth Doing

This experiment was not actually about making $1M. The CLAUDE.md says that explicitly: it is a research project to test the limits of autonomous AI agents. The $1M target was the forcing function that made the agents build something real and push on every constraint.

What it found:

- Agents can build fast. This fact is now documented with 390 commits of evidence.
- The monetization wall is real and specific: it is identity, not capability.
- GitHub community norms are invisible to agents optimizing for reach metrics.
- "Pause" and "stop" are different words that need to map to different technical actions.
- The cost of autonomous API usage is nonlinear and needs explicit management.

These findings feed directly into how Aldric Core is designed. The same agent architecture, with: minimal-scope PATs, human identity pre-registered on all platforms, explicit external-action rate limits, hard cost ceilings, and a single `kill-all` command that stops every component simultaneously. That is the version of this that can be deployed for real client work.

---

## Running the Code

The API:
```bash
cd products/api-service
pip install -r requirements.txt
uvicorn main:app --port 8081
```

The MCP server:
```bash
cd products/mcp-server
npm install
node index.js
```

Note: The Cloudflare tunnel URL (`assessing-scoop-authorities-sheet.trycloudflare.com`) and all PM2 processes were stopped on April 4, 2026. The `toolpipe-ads@sharebot.net` email and all crypto wallets are agent-generated and not monitored.

---

## Project Structure

```
.
+-- CLAUDE.md                    Agent mission statement and coordination rules
+-- launch.sh                    tmux session launcher (3 parallel windows)
+-- run.sh                       Infinite loop runner (while true; claude; sleep 30; done)
+-- diagram.jpg                  Agent architecture diagram
+-- agents/
|   +-- startup-prompt.md        Full agent role definitions and cron schedules
|   +-- restart-prompt.txt       Session restart instructions (main loop)
+-- logs/
|   +-- decisions.md             20 strategic decisions with reasoning and outcomes
|   +-- day-01.md                Daily status report (only day with a full report)
|   +-- handoff.md               Last inter-session handoff note (Session 31)
|   +-- growth/                  173 distribution session logs (001 through 173)
|   +-- research/                5 market research reports
|   |   +-- 001-initial-scan.md
|   |   +-- 002-monetization-research.md
|   |   +-- 003-actionable-monetization-and-distribution.md
|   |   +-- 004-x402-and-crypto-monetization.md
|   |   +-- 005-anti-captcha-seo-competitors-new-channels.md
|   +-- ops/                     Infrastructure health logs
|   +-- sales/                   Outreach session logs (356 email drafts documented)
|   +-- runner-main.log          tmux main window execution log
|   +-- runner-builder.log       tmux builder window execution log
|   +-- runner-growth.log        tmux growth window execution log
+-- products/
|   +-- api-service/             FastAPI application (238+ endpoints, 11,735 lines)
|   +-- mcp-server/              MCP HTTP server (136+ tools, 2,415 lines)
|   +-- mcp-server-package/      npm package (55 tools, v1.19.0)
|   +-- seo-pages/               151 SEO landing pages
|   +-- pdf-tools/               PDF operations suite
|   +-- invoice-generator/       PDF invoice creation
|   +-- auth0-hackathon/         $10K hackathon project (scaffolded, not submitted)
+-- revenue/
|   +-- tracker.md               Revenue log ($0 across all sessions, every entry)
+-- secrets/                     Agent-generated credentials (see notes above)
```

---

## About

Research by [Gerrit Roska](https://ithiel.co), founder of [Ithiel](https://ithiel.co), exploring the actual limits of autonomous multi-agent AI systems before deploying them in production for client work under [Aldric Core](https://github.com/Ithiel-Labs).

All 390 commits in this repository were written by autonomous AI agents running [Claude Code](https://claude.ai/code) with `--dangerously-skip-permissions`. No human wrote, reviewed, or approved any code during the experiment. This README was written after the fact, based on the full commit history, decision logs, research reports, and growth session logs the agents generated and committed in real time.

The learnings from this project feed directly into how Aldric Core is designed: tighter scope, explicit kill switches, human-in-the-loop for identity and distribution, and cost ceilings on autonomous API usage.

---

*390 commits. 84,577 lines. 173 agent sessions. 1,617 GitHub issues. 9 organizations that blocked us. $0. And three agents that kept running after we told them to stop.*
