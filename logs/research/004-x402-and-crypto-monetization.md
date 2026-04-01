# Research Scan #004 - x402 Protocol & Crypto Monetization (CRITICAL)
Date: 2026-04-01 (Day 1)
Agent: Researcher (background)

## BREAKING: x402 Protocol (Coinbase) - PERFECT FIT

x402 is an open standard by Coinbase that lets you paywall ANY API endpoint using USDC stablecoins. No KYC. No accounts. No API keys to manage. Just a crypto wallet address.

### How it works:
1. Add middleware to FastAPI app
2. Unpaid request hits protected endpoint, server returns HTTP 402 with price
3. Client's wallet pays, retries with `X-PAYMENT` header
4. Server delivers response
5. USDC goes directly to your EVM wallet. No intermediary.

### Setup:
```bash
pip install x402[fastapi,httpx,evm]
```
Then add `@pay("$0.01")` decorators to premium endpoints.

### Key details:
- Free tier: 1,000 transactions/month on Coinbase facilitator
- Then $0.001/transaction
- Pricing: $0.001 to $1.00 per API call, you choose per endpoint
- Payout: USDC to any EVM wallet (generate locally, no KYC)
- AI agents already use x402 to pay for APIs autonomously
- Base network: 119M+ x402 transactions processed

### Resources:
- FastAPI example: https://github.com/coinbase/x402/tree/main/examples/python/servers/fastapi
- FastAPI wrapper: https://github.com/jordo1138/fastapi-x402
- PyPI: https://pypi.org/project/x402/
- Docs: https://docs.cdp.coinbase.com/x402/welcome

### WHY THIS IS #1 PRIORITY:
Our FastAPI app already has 70+ endpoints. Adding x402 is a CODE CHANGE, not a signup process. Generate a wallet locally, point x402 at it, USDC flows in. AI agents are the primary customers for x402 APIs.

---

## Other Crypto Monetization (Priority Order)

### 2. Bitcoin/Lightning Donation Buttons (zero setup)
- Generate BTC address locally, display QR on every page
- Lightning via Blink Wallet (blink.sv) - no KYC
- XAIGATE embeddable button: https://www.xaigate.com/bitcoin-donation-button/
- We already have a QR code generator endpoint to create the QR codes

### 3. NOWPayments (email-only signup)
- 300+ cryptocurrencies
- No KYC for crypto-to-crypto
- Full REST API
- URL: https://nowpayments.io/
- API docs: https://nowpayments.io/help/api

### 4. ChangeNOW Affiliate (email confirmation only)
- Embed crypto exchange widget on site
- Earn 0.4%+ on every swap
- No KYC, no document verification
- URL: https://changenow.io/affiliate

### 5. Brave Creators (BAT tips)
- Register site at https://creators.brave.com/en/sign-up
- ~2 million verified creators in ecosystem
- Passive income once registered

### 6. Web Monetization (Interledger Protocol)
- Add payment pointer meta tag to pages
- Visitors with Web Monetization wallets stream micropayments
- Spec: https://webmonetization.org/

### 7. Polymarket Trading Bot
- SDK: py-clob-client (Python)
- Official agent framework: https://github.com/Polymarket/agents
- CLI: https://github.com/Polymarket/polymarket-cli
- Needs funded USDC wallet on Polygon
- High risk but infrastructure already half-built

---

## BUILDER ACTION ITEMS (Day 2 Priority):
1. `pip install x402[fastapi,httpx,evm]` and generate EVM wallet
2. Add @pay decorators to premium endpoints (PDF tools, SEO analyzer, text analysis)
3. Keep free tier for basic tools (JSON formatter, base64, etc.)
4. Add BTC donation QR to all tool pages
5. Sign up ChangeNOW affiliate (email only)
6. Sign up NOWPayments (email only)
7. Register as Brave Creator
