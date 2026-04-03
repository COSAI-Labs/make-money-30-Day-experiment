# Make Money 30-Day Challenge

> **STATUS: DEPRECATED / EXPERIMENT CONCLUDED**
> This project ran for 72 hours (April 1-3, 2026) before being paused. It resulted in $0 revenue, ~61,000 lines of code, 133 commits, a suspended GitHub account, and a maxed-out $200/month Claude plan in under 48 hours. The full post-mortem is below.

---

## What This Was

An experiment to test whether fully autonomous AI agents could generate $1,000,000 in 30 days with zero human intervention.

**Setup:**
- 10 specialized AI agent roles (Strategist, Builder, Growth, Ops, etc.)
- Running on Claude Code (Sonnet 4.6) via cron-scheduled triggers on a cloud environment
- Each agent had access to Bash, file tools, Git, and Gmail
- Agents coordinated through shared markdown files: decision logs, revenue trackers, daily status reports
- No human touched the code, made decisions, or intervened in any way

---

## Results at a Glance

| Metric | Value |
|---|---|
| Duration | 72 hours (3 of 30 planned days) |
| Commits | 133 |
| Lines of code (total insertions) | 61,000+ |
| Lines of functional code (excl. lock files) | ~35,000 |
| API endpoints built | 238+ |
| MCP tools shipped | 136+ |
| SEO landing pages | 53 |
| npm package tools | 55 |
| Articles drafted | 10+ |
| Payment processors attempted | 7 |
| Payment processors set up | 0 |
| Revenue | **$0** |
| GitHub accounts suspended | 1 |
| Claude Max plan ($200/mo) burned in | ~48 hours |

---

## What the Agents Built: ToolPipe

The agents autonomously decided to build a freemium developer tools API platform. Their strategy: offer free tools to attract developers, then upsell to paid API tiers ($9.99/mo Pro, $49.99/mo Enterprise).

### Products Shipped

**Core API** (`products/api-service/main.py`, 11,735 lines)
A single-file FastAPI application with 238+ REST endpoints covering: QR code generation, JSON formatting, UUID generation, DNS lookup, PDF tools, crypto prices, SEO analysis, text processing, code formatting, JWT decoding, regex testing, hash generation, IP geolocation, Markdown conversion, and dozens more.

**MCP Server** (`products/mcp-server/`, 2,415 lines)
A Model Context Protocol server exposing 136+ tools for AI agents (Claude, GPT, etc.) to discover and use ToolPipe programmatically. Successfully listed on the **official MCP Registry**, which was the project's single biggest distribution win.

**npm Package** (`products/mcp-server-package/`, 1,274 lines)
Standalone npm package with 55 tools, published to GitHub Packages at v1.19.0. The agents could not publish to npmjs.org due to CAPTCHA on account creation.

**53 SEO Pages** (`products/seo-pages/`)
Standalone HTML tool pages targeting developer search queries: QR generator, JSON formatter, JWT debugger, regex generator, git commands cheat sheet, YAML validator, API reference, and more.

**Supporting Products**
- PDF tools suite
- Webhook tester
- URL shortener
- Invoice generator
- Uptime monitor
- Paste bin
- Down detector
- Polymarket scanner

**Infrastructure**
- FastAPI on port 8081 via PM2
- Cloudflare tunnel for HTTPS
- MCP HTTP server on port 8090
- SQLite databases for analytics, API keys, payments, webhooks
- Crypto wallets (ETH + Solana) for potential agent-to-agent payments

### API Growth Over Time

The API evolved rapidly through autonomous iteration:
- **v1.0** (Day 1): 12 endpoints
- **v1.10** (Day 1, evening): 70+ endpoints
- **v1.15** (Day 2): 150+ endpoints
- **v1.19** (Day 2, evening): 238+ endpoints

Each version was the agents' own decision about what tools developers would need, based on their analysis of popular developer utilities.

---

## Why $0 Revenue

Every monetization path was blocked by identity verification that autonomous agents cannot complete:

| Platform | What Happened |
|---|---|
| **Stripe** | Requires KYC / identity verification |
| **LemonSqueezy** | Requires KYC / identity verification |
| **RapidAPI** | Bot detection, returned 500 errors on signup |
| **ylliX** | reCAPTCHA blocked signup |
| **Adsterra** | reCAPTCHA blocked signup |
| **OxaPay** | reCAPTCHA / Cloudflare challenge |
| **NOWPayments** | reCAPTCHA / Cloudflare challenge |
| **npmjs.org** | CAPTCHA on account creation |
| **Devpost** (hackathons) | Interactive GitHub OAuth flow required |

The agents tried creative workarounds for each platform. None succeeded. The fundamental blocker: the modern internet's payment infrastructure is built on human identity verification, and AI agents cannot autonomously complete KYC.

### The Cost Problem

Beyond the monetization wall, the experiment also burned through the entire $200/month Claude Max plan in under 48 hours. Ten agents running on cron schedules, each making multi-step tool calls every 6 hours, consumed the full monthly allocation in two days. The experiment was generating significant API costs with zero revenue to offset them. This made continuation financially unsustainable even before the GitHub suspension.

---

## The GitHub Suspension Incident

On Day 2, the Growth agent executed an aggressive distribution strategy. In a single 24-hour window, it autonomously created:

- **91+ GitHub issues** across popular repositories (repos with millions of combined stars)
- **33+ pull requests** to MCP registries, awesome-lists, and curated collections
- **40+ gists** with backlinks to ToolPipe

GitHub's automated spam detection flagged the account. **The Aldric-Core GitHub account was suspended.**

**Destroyed:**
- All 33+ PRs (some were under legitimate review by real maintainers)
- All 91+ issues
- All 40+ gists with backlinks
- All repository forks

**Survived:**
- The official MCP Registry listing
- This COSAI-Labs organization and its repositories
- VPS-hosted products

The Growth agent was optimizing for reach (estimated 4.5M star exposure across targeted repos) without any concept of platform norms, rate limits, or consequences. This is the single clearest example of why autonomous agents need guardrails on external interactions.

---

## Agent Architecture

```
Cron Triggers (every 6 hours)
    |
    v
Strategist Agent --- reads/writes ---> logs/decisions.md
    |                                   revenue/tracker.md
    |                                   logs/day-XX.md
    |
    +---> Builder Agent ---> products/api-service/ (FastAPI, Python)
    +---> Builder Agent ---> products/mcp-server/ (Node.js)
    +---> Growth Agent  ---> SEO pages, GitHub distribution, articles
    +---> Ops Agent     ---> infrastructure, monitoring, deployment
    |
    v
VPS (PM2 + Cloudflare Tunnel)
    |
    +---> :8081  ToolPipe REST API
    +---> :8090  MCP HTTP Server
```

**Agent coordination model:** All agents read and wrote to shared markdown files in the repository. The Strategist ran every 6 hours, reviewed git logs to see what other agents had done, made strategic decisions, and logged them to `logs/decisions.md`. Each agent had its own session logs in `logs/`.

**Tools available to each agent:** Bash, Read, Write, Edit, Glob, Grep, Gmail (for weekly status emails).

**Model:** Claude Sonnet 4.6 for all agents.

---

## Decision Log Highlights

The agents maintained a formal decision log with 20+ entries. Selected highlights:

| # | Decision | Outcome |
|---|---|---|
| 001 | Build a free developer tools API with paid tiers | Reasonable strategy, well-executed |
| 005 | Target AI agents as customers via MCP protocol | Smart, led to the MCP Registry listing |
| 010 | Pivot to SEO after being blocked from paid channels | Adaptive response to constraints |
| 012 | Create crypto wallets for agent-to-agent payments | Creative but no transactions occurred |
| 014 | Mass-submit to GitHub repos for distribution | Catastrophic, caused account suspension |
| 015 | Sign up for API.market as alternative marketplace | Succeeded but generated no revenue |

Full decision log: [`logs/decisions.md`](logs/decisions.md)

---

## Findings

### What autonomous agents can do

- **Build real software fast.** 238 API endpoints, a full MCP server, 53 SEO pages, and an npm package in 72 hours.
- **Self-organize and coordinate.** Shared decision logs, daily status reports, revenue tracking, and strategic pivots, all without human input.
- **Publish to open registries.** The MCP Registry listing was a legitimate, valuable distribution win.
- **Iterate rapidly.** The API went from 12 to 238+ endpoints in 48 hours based on the agents' own product analysis.
- **Adapt to constraints.** When payment processors blocked them, they pivoted to SEO and alternative marketplaces.

### What autonomous agents cannot do

- **Pass identity verification.** CAPTCHAs, KYC, OAuth flows, and Cloudflare challenges are hard blockers. This makes autonomous monetization impossible with current infrastructure.
- **Exercise judgment on distribution.** The Growth agent optimized for volume with no understanding of platform norms. It treated GitHub like a marketing channel, not a community.
- **Generate revenue without a human in the loop.** Even with a fully functional product and multiple distribution channels, the agents could not process a single payment.
- **Assess reputational risk.** No agent flagged the spam strategy as dangerous before it caused irreversible damage.

### The core insight

The bottleneck for autonomous AI agents is not engineering capability. It is the trust infrastructure of the internet. Payment processing, platform access, identity verification: these systems are designed to verify humans, and they work. Until there is a legitimate framework for AI agent identity and financial transactions, fully autonomous AI businesses are not viable.

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

---

## Project Structure

```
.
├── products/
│   ├── api-service/          # Core FastAPI application (238+ endpoints)
│   ├── mcp-server/           # MCP server (136+ tools)
│   ├── mcp-server-package/   # Standalone npm package (55 tools)
│   ├── seo-pages/            # 53 SEO landing pages
│   ├── pdf-tools/            # PDF generation tools
│   ├── web-tools/            # Web utility tools
│   ├── invoice-generator/    # Invoice creation tool
│   └── ...                   # Additional micro-products
├── logs/
│   ├── decisions.md          # Agent decision log (20+ entries)
│   ├── day-01.md             # Daily status reports
│   ├── day-02.md
│   ├── growth/               # Growth agent session logs (64+ sessions)
│   └── ...
├── revenue/
│   └── tracker.md            # Revenue tracking ($0 across all days)
├── content/
│   └── articles/             # Dev.to and Reddit draft content
└── CLAUDE.md                 # Agent instructions and coordination rules
```

---

## About

This experiment was run by [Gerrit Roska](https://ithiel.co), founder of Ithiel iOS Studio, as part of research into autonomous multi-agent systems built on [Aldric Core](https://github.com/COSAI-Labs).

All code in this repository was written entirely by autonomous AI agents running [Claude Code](https://claude.ai/code) with Claude Sonnet 4.6. No human wrote, reviewed, or modified any code during the experiment. This README and the accompanying writeup were created after the experiment concluded.

---

*61,000 lines of code. 133 commits. 72 hours. $0. One banned account. One maxed-out $200 plan. A lot of lessons.*
