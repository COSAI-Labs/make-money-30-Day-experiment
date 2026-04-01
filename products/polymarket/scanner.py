#!/usr/bin/env python3
"""
Polymarket Market Scanner
Fetches active markets, analyzes odds, identifies opportunities.
"""

import requests
import json
import os
from datetime import datetime

GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"

def fetch_active_markets(limit=100, offset=0):
    """Fetch active, open markets from Polymarket."""
    resp = requests.get(f"{GAMMA_API}/markets", params={
        "active": "true",
        "closed": "false",
        "limit": limit,
        "offset": offset,
    })
    resp.raise_for_status()
    return resp.json()

def fetch_market_prices(token_id):
    """Get current price for a token."""
    try:
        resp = requests.get(f"{CLOB_API}/price", params={
            "token_id": token_id,
            "side": "buy",
        })
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def fetch_orderbook(token_id):
    """Get order book for a token."""
    try:
        resp = requests.get(f"{CLOB_API}/book", params={
            "token_id": token_id,
        })
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def analyze_market(market):
    """Analyze a single market for opportunity."""
    result = {
        "question": market.get("question", "Unknown"),
        "slug": market.get("slug", ""),
        "volume": market.get("volume", 0),
        "liquidity": market.get("liquidity", 0),
        "end_date": market.get("endDate", ""),
        "category": market.get("category", ""),
        "tokens": [],
    }

    clob_token_ids = market.get("clobTokenIds", "")
    if isinstance(clob_token_ids, str):
        try:
            clob_token_ids = json.loads(clob_token_ids)
        except (json.JSONDecodeError, TypeError):
            clob_token_ids = []

    outcomes = market.get("outcomes", "")
    if isinstance(outcomes, str):
        try:
            outcomes = json.loads(outcomes)
        except (json.JSONDecodeError, TypeError):
            outcomes = ["Yes", "No"]

    outcome_prices = market.get("outcomePrices", "")
    if isinstance(outcome_prices, str):
        try:
            outcome_prices = json.loads(outcome_prices)
        except (json.JSONDecodeError, TypeError):
            outcome_prices = []

    for i, token_id in enumerate(clob_token_ids):
        outcome = outcomes[i] if i < len(outcomes) else f"Outcome {i}"
        price = float(outcome_prices[i]) if i < len(outcome_prices) else None
        result["tokens"].append({
            "token_id": token_id,
            "outcome": outcome,
            "price": price,
        })

    return result

def find_opportunities(markets, min_volume=1000):
    """Find markets with potential mispricing or high-confidence opportunities."""
    opportunities = []

    for market in markets:
        analysis = analyze_market(market)

        # Skip low-volume markets
        try:
            vol = float(analysis["volume"]) if analysis["volume"] else 0
        except (ValueError, TypeError):
            vol = 0

        if vol < min_volume:
            continue

        # Look for extreme prices (potential high-confidence bets)
        for token in analysis["tokens"]:
            price = token.get("price")
            if price is None:
                continue

            # Markets where YES is very cheap (< 0.10) or very expensive (> 0.90)
            # could be opportunities if we have conviction
            if price < 0.10 or price > 0.90:
                token["opportunity_type"] = "extreme_price"
                analysis["opportunity"] = True

            # Markets near 50/50 with high volume = liquid and tradeable
            if 0.40 <= price <= 0.60 and vol > 10000:
                token["opportunity_type"] = "liquid_balanced"
                analysis["opportunity"] = True

        opportunities.append(analysis)

    return opportunities

def scan_and_report():
    """Main scan: fetch markets, analyze, write report."""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    report_dir = os.path.join(os.path.dirname(__file__), "research")
    os.makedirs(report_dir, exist_ok=True)

    print(f"[{timestamp}] Scanning Polymarket...")

    all_markets = []
    for offset in range(0, 500, 100):
        markets = fetch_active_markets(limit=100, offset=offset)
        if not markets:
            break
        all_markets.extend(markets)
        print(f"  Fetched {len(all_markets)} markets...")

    print(f"Total markets: {len(all_markets)}")

    opportunities = find_opportunities(all_markets, min_volume=5000)
    extreme = [o for o in opportunities if o.get("opportunity")]

    # Sort by volume
    extreme.sort(key=lambda x: float(x.get("volume", 0) or 0), reverse=True)

    report = f"# Polymarket Scan Report\n"
    report += f"**Date:** {timestamp}\n"
    report += f"**Total Markets Scanned:** {len(all_markets)}\n"
    report += f"**Opportunities Found:** {len(extreme)}\n\n"

    report += "## High-Interest Markets\n\n"
    for opp in extreme[:30]:
        report += f"### {opp['question']}\n"
        report += f"- Volume: ${float(opp.get('volume', 0) or 0):,.0f}\n"
        report += f"- Liquidity: ${float(opp.get('liquidity', 0) or 0):,.0f}\n"
        report += f"- Category: {opp.get('category', 'N/A')}\n"
        report += f"- End Date: {opp.get('end_date', 'N/A')}\n"
        for token in opp.get("tokens", []):
            price = token.get("price")
            price_str = f"${price:.2f}" if price else "N/A"
            opp_type = token.get("opportunity_type", "")
            report += f"  - {token['outcome']}: {price_str}"
            if opp_type:
                report += f" [{opp_type}]"
            report += "\n"
        report += "\n"

    report_path = os.path.join(report_dir, f"scan_{timestamp}.md")
    with open(report_path, "w") as f:
        f.write(report)

    # Also write latest scan summary
    latest_path = os.path.join(report_dir, "latest_scan.md")
    with open(latest_path, "w") as f:
        f.write(report)

    print(f"Report written to {report_path}")
    print(f"Found {len(extreme)} opportunities")

    return extreme

if __name__ == "__main__":
    opportunities = scan_and_report()
    print(json.dumps(opportunities[:5], indent=2))
