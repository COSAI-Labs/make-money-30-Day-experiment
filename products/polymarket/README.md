# Polymarket Trading System

Dedicated autonomous prediction market research and trading system.

## Architecture
- **scanner.py** - Fetches and analyzes all active markets, finds opportunities
- **trader.py** - Executes trades via CLOB API (requires USDC.e funding)
- **research/** - Scan reports and analysis
- **positions/** - Current positions and P&L tracking
- **logs/** - All trading activity

## API Credentials
Stored in project root `.env` (gitignored):
- POLYMARKET_API_KEY
- POLYMARKET_SECRET
- POLYMARKET_PASSPHRASE

## Strategy
1. Scan for markets resolving within 30 days
2. Identify high-confidence outcomes (extreme mispricing)
3. Research the underlying events for conviction
4. Place positions on high-confidence bets
5. Monitor and exit early if odds shift favorably

## Current Findings (Day 1)
- 65 near-term markets (resolving within 45 days)
- Hungary PM election (10 days): Magyar 62%, Orbán 38%
- 2026 Masters (11 days): Scheffler 14% favorite
- Multiple high-volume political and sports markets

## Requirements
- USDC.e on Polygon for trading
- POL for gas (if using EOA)
- py-clob-client SDK installed
