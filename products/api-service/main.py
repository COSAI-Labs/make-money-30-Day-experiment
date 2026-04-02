"""
ToolPipe API - Multi-endpoint utility API service.
Fast, reliable developer tools via REST API.
"""

import io
import json
import hashlib
import base64
import re
import time
import uuid
import tempfile
import os
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlparse

import httpx
import markdown
import qrcode
from bs4 import BeautifulSoup
from pathlib import Path
from fastapi import FastAPI, File, Form, HTTPException, Query, Request, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
from pydantic import BaseModel, HttpUrl
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.pagesizes import letter

app = FastAPI(
    title="ToolPipe API",
    description="240+ developer utility APIs. Web scraping, domain intelligence, bulk operations, API testing, sitemap parsing, content monitoring, code review, fake data, JSON Schema validation, security headers, API client generation, CSV analysis, code minification, QR codes, PDF tools, hashing, UUID, DNS, regex, JWT, SQL formatting, XML/YAML, text stats, and more. Free tier: 100 calls/day. Pro: 10,000 calls/day ($9.99/mo). Credits: 1K for $4.99. Pay with crypto, no KYC.",
    version="1.19.0",
    contact={"name": "ToolPipe", "url": "https://toolpipe.dev", "email": "toolpipe-ads@sharebot.net"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    servers=[{"url": "https://toolpipe.dev", "description": "Production"}],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Favicon endpoint
_STATIC_DIR = Path(__file__).parent / "static"
_STATIC_DIR.mkdir(exist_ok=True)

@app.get("/favicon.ico")
async def favicon():
    ico_path = _STATIC_DIR / "favicon.ico"
    if ico_path.exists():
        return FileResponse(str(ico_path), media_type="image/x-icon")
    return Response(status_code=204)

# x402 crypto payments (USDC on Base Sepolia)
# Premium endpoints return HTTP 402 with payment instructions
# AI agents and developers pay per-call via USDC
WALLET_ADDRESS = "0xBCF464909b748d720fd5DDA25ad3d313Dd4b53D6"
SOLANA_WALLET = os.environ.get("SOLANA_WALLET", "2guKDsPScRpCCKuVEGKBPFvodSNtZF4ArYeSC6oy6pf6")
SOLANA_RPC = "https://api.mainnet-beta.solana.com"
X402_ENABLED = False
try:
    from fastapi_x402 import init_x402, pay
    init_x402(
        app=app,
        pay_to=WALLET_ADDRESS,
        network="base-sepolia",
        default_asset="USDC",
        default_expires_in=300,
        auto_add_middleware=True,
    )
    X402_ENABLED = True
    print(f"x402 payments enabled. Pay to: {WALLET_ADDRESS}")
except Exception as e:
    print(f"x402 init skipped: {e}. All endpoints free.")

# Premium pricing info endpoint
@app.get("/api/pricing")
async def pricing_info_json():
    return {
        "payment_protocol": "x402",
        "enabled": X402_ENABLED,
        "wallet": WALLET_ADDRESS,
        "network": "base-sepolia",
        "asset": "USDC",
        "tiers": PRICING_TIERS,
        "free_tier": {"daily_limit": 100, "endpoints": "all"},
        "how_to_pay": "POST /payments/create with email and tier, then pay via crypto. Or send directly to the wallet and verify via /payments/verify-tx.",
    }


@app.get("/pricing", response_class=HTMLResponse)
async def pricing_page():
    return HTMLResponse(inject_snippet("""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>ToolPipe Pricing - API Plans for Developers and AI Agents</title>
<meta name="description" content="ToolPipe API pricing. Free tier with 100 calls/day. Pro $9.99/mo for 10,000 calls/day. Enterprise $49.99/mo for 100,000 calls/day. Pay with crypto, no KYC.">
<link rel="canonical" href="https://toolpipe.dev/pricing">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0a0a0a;color:#e0e0e0}
.container{max-width:1000px;margin:0 auto;padding:40px 20px}
h1{font-size:2.5rem;text-align:center;margin-bottom:8px;color:#fff}
.subtitle{text-align:center;color:#94a3b8;font-size:1.1rem;margin-bottom:48px}
.plans{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin-bottom:48px}
.plan{background:#1a1a1a;border:2px solid #2a2a2a;border-radius:16px;padding:32px 24px;position:relative;transition:all 0.2s}
.plan:hover{border-color:#6c63ff;transform:translateY(-4px)}
.plan.featured{border-color:#6c63ff;background:#1a1a2e}
.plan.featured::before{content:"MOST POPULAR";position:absolute;top:-12px;left:50%;transform:translateX(-50%);background:#6c63ff;color:#fff;padding:4px 16px;border-radius:12px;font-size:0.75rem;font-weight:700;letter-spacing:0.5px}
.plan-name{font-size:1.3rem;font-weight:700;color:#fff;margin-bottom:4px}
.plan-price{font-size:2.5rem;font-weight:800;color:#fff;margin:16px 0 4px}
.plan-price span{font-size:0.9rem;font-weight:400;color:#64748b}
.plan-desc{color:#94a3b8;font-size:0.9rem;margin-bottom:24px}
.plan-features{list-style:none;margin-bottom:32px}
.plan-features li{padding:8px 0;color:#cbd5e1;font-size:0.95rem;border-bottom:1px solid #1e1e2e}
.plan-features li::before{content:"\\2713 ";color:#22c55e;font-weight:700;margin-right:6px}
.plan-btn{display:block;width:100%;padding:14px;border:none;border-radius:10px;font-size:1rem;font-weight:700;cursor:pointer;text-align:center;text-decoration:none;transition:all 0.2s}
.btn-free{background:#2a2a2a;color:#fff}.btn-free:hover{background:#3a3a3a}
.btn-pro{background:#6c63ff;color:#fff}.btn-pro:hover{background:#5b52e0}
.btn-ent{background:linear-gradient(135deg,#6c63ff,#3b82f6);color:#fff}.btn-ent:hover{opacity:0.9}
.how{background:#1a1a1a;border:1px solid #2a2a2a;border-radius:16px;padding:32px;margin-bottom:32px}
.how h2{color:#fff;font-size:1.5rem;margin-bottom:20px}
.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
.step{text-align:center;padding:16px}
.step-num{width:40px;height:40px;background:#6c63ff;color:#fff;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-weight:700;font-size:1.1rem;margin-bottom:12px}
.step h3{color:#fff;font-size:1rem;margin-bottom:8px}
.step p{color:#94a3b8;font-size:0.9rem;line-height:1.5}
.faq{margin-top:48px}
.faq h2{color:#fff;font-size:1.5rem;margin-bottom:24px;text-align:center}
.faq-item{background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;margin-bottom:12px;overflow:hidden}
.faq-q{padding:16px 20px;font-weight:600;color:#fff;cursor:pointer;display:flex;justify-content:space-between;align-items:center}
.faq-q::after{content:"+";font-size:1.2rem;color:#6c63ff}
.faq-a{padding:0 20px 16px;color:#94a3b8;font-size:0.95rem;line-height:1.6;display:none}
.faq-item.open .faq-a{display:block}
.faq-item.open .faq-q::after{content:"\\2212"}
.agent-box{background:linear-gradient(135deg,#1a1a2e,#0f172a);border:1px solid #3b82f6;border-radius:16px;padding:32px;margin:32px 0;text-align:center}
.agent-box h2{color:#fff;font-size:1.5rem;margin-bottom:12px}
.agent-box p{color:#94a3b8;font-size:1rem;margin-bottom:16px;line-height:1.6}
.agent-box code{background:#111;color:#22c55e;padding:8px 16px;border-radius:8px;font-size:0.9rem;display:block;margin:12px auto;max-width:500px;text-align:left;white-space:pre-wrap}
@media(max-width:700px){.plans{grid-template-columns:1fr}.steps{grid-template-columns:1fr}}
</style></head><body>
<div class="container">
<h1>Simple, Transparent Pricing</h1>
<p class="subtitle">230+ API endpoints. Pay with crypto. No KYC required.</p>

<div class="plans">
<div class="plan">
<div class="plan-name">Free</div>
<div class="plan-price">$0<span>/forever</span></div>
<div class="plan-desc">Perfect for testing and personal projects</div>
<ul class="plan-features">
<li>100 API calls per day</li>
<li>All 230+ endpoints</li>
<li>No credit card needed</li>
<li>Email support</li>
<li>Rate limited (100 req/min)</li>
</ul>
<a href="/api-keys" class="plan-btn btn-free">Get Free API Key</a>
</div>

<div class="plan featured">
<div class="plan-name">Pro</div>
<div class="plan-price">$9.99<span>/month</span></div>
<div class="plan-desc">For developers and small teams shipping products</div>
<ul class="plan-features">
<li>10,000 API calls per day</li>
<li>All 230+ endpoints</li>
<li>Priority rate limits</li>
<li>Pay with any crypto</li>
<li>Priority support</li>
</ul>
<button class="plan-btn btn-pro" onclick="startCheckout('pro')">Get Pro Access</button>
</div>

<div class="plan">
<div class="plan-name">Enterprise</div>
<div class="plan-price">$49.99<span>/month</span></div>
<div class="plan-desc">For teams and AI agents needing high throughput</div>
<ul class="plan-features">
<li>100,000 API calls per day</li>
<li>All 230+ endpoints</li>
<li>Unlimited rate limits</li>
<li>Pay with any crypto</li>
<li>Dedicated support</li>
</ul>
<button class="plan-btn btn-ent" onclick="startCheckout('enterprise')">Get Enterprise Access</button>
</div>
</div>

<div class="agent-box">
<h2>Built for AI Agents</h2>
<p>ToolPipe is an MCP server that any AI agent (Claude, GPT, Gemini) can use directly. Install via npm and your agent gets 156+ MCP tools instantly.</p>
<code>npx @cosai-labs/toolpipe-mcp-server</code>
<p style="margin-top:16px;font-size:0.9rem;">Agents can self-serve: register API keys, create payment orders, and verify transactions. All via API, zero human needed.</p>
</div>

<div class="how">
<h2>How Payment Works</h2>
<div class="steps">
<div class="step">
<div class="step-num">1</div>
<h3>Choose a Plan</h3>
<p>Select Pro or Enterprise. Enter your email to get an API key.</p>
</div>
<div class="step">
<div class="step-num">2</div>
<h3>Pay with Crypto</h3>
<p>Send ETH, USDC, USDT, SOL, or any token to our wallet on Ethereum, Polygon, Arbitrum, Base, Optimism, or Solana.</p>
</div>
<div class="step">
<div class="step-num">3</div>
<h3>Verify & Activate</h3>
<p>Submit your transaction hash and your API key is instantly upgraded. Fully automated, on-chain verification.</p>
</div>
</div>
</div>

<div class="faq">
<h2>FAQ</h2>
<div class="faq-item"><div class="faq-q" onclick="this.parentElement.classList.toggle('open')">What cryptocurrencies do you accept?</div><div class="faq-a">We accept ETH, USDC, USDT, DAI, WETH on Ethereum, Polygon, Arbitrum, Base, and Optimism. We also accept SOL and USDC-SPL on Solana. Recommended: USDC on Base (lowest fees, ~$0.01 per tx).</div></div>
<div class="faq-item"><div class="faq-q" onclick="this.parentElement.classList.toggle('open')">Do I need KYC or identity verification?</div><div class="faq-a">No. We accept crypto payments with no identity verification required. Just an email address for your API key.</div></div>
<div class="faq-item"><div class="faq-q" onclick="this.parentElement.classList.toggle('open')">How is payment verified?</div><div class="faq-a">After sending payment, submit your transaction hash via our /payments/verify-tx endpoint. We verify the transaction on-chain across all supported networks automatically. Your API key is upgraded instantly upon verification.</div></div>
<div class="faq-item"><div class="faq-q" onclick="this.parentElement.classList.toggle('open')">Can AI agents pay for themselves?</div><div class="faq-a">Yes. Our entire payment flow is API-first. An AI agent can POST to /payments/create, send crypto, then POST to /payments/verify-tx with the tx hash. Fully automated, zero human interaction needed.</div></div>
<div class="faq-item"><div class="faq-q" onclick="this.parentElement.classList.toggle('open')">What happens if I exceed my daily limit?</div><div class="faq-a">Requests beyond your daily limit return HTTP 429. Your counter resets at midnight UTC. Upgrade to a higher tier for more capacity.</div></div>
</div>
</div>

<!-- Checkout Modal -->
<div id="checkout-modal" style="display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.8);z-index:10000;display:none;align-items:center;justify-content:center">
<div style="background:#1a1a1a;border:2px solid #6c63ff;border-radius:16px;padding:40px;max-width:520px;width:90%;position:relative;max-height:90vh;overflow-y:auto">
<button onclick="closeCheckout()" style="position:absolute;top:12px;right:16px;background:none;border:none;color:#94a3b8;font-size:1.5rem;cursor:pointer">x</button>
<h2 style="color:#fff;font-size:1.5rem;margin-bottom:8px" id="checkout-title">Upgrade to Pro</h2>
<p style="color:#94a3b8;margin-bottom:24px" id="checkout-price">$9.99/month - 10,000 API calls/day</p>

<div id="checkout-step1">
<label style="color:#cbd5e1;display:block;margin-bottom:8px;font-weight:600">Email Address</label>
<input type="email" id="checkout-email" placeholder="you@email.com" style="width:100%;padding:12px 16px;background:#111;border:1px solid #2a2a2a;border-radius:8px;color:#e0e0e0;font-size:1rem;margin-bottom:16px">
<button onclick="createOrder()" id="checkout-btn" style="width:100%;padding:14px;background:#6c63ff;color:#fff;border:none;border-radius:10px;font-size:1rem;font-weight:700;cursor:pointer">Create Payment Order</button>
</div>

<div id="checkout-step2" style="display:none">
<div style="background:#111;border:1px solid #22c55e;border-radius:12px;padding:20px;margin-bottom:16px">
<p style="color:#22c55e;font-weight:700;margin-bottom:8px">Send crypto to this address:</p>
<code style="color:#22c55e;font-size:0.85rem;word-break:break-all;display:block;margin-bottom:8px">0xBCF464909b748d720fd5DDA25ad3d313Dd4b53D6</code>
<button onclick="navigator.clipboard.writeText('0xBCF464909b748d720fd5DDA25ad3d313Dd4b53D6');this.textContent='Copied!';setTimeout(()=>this.textContent='Copy Address',2000)" style="background:#22c55e;color:#000;border:none;padding:8px 16px;border-radius:6px;cursor:pointer;font-weight:600">Copy Address</button>
</div>
<p style="color:#94a3b8;font-size:0.9rem;margin-bottom:4px">Amount: <strong style="color:#fff" id="checkout-amount">$9.99</strong> in any supported crypto</p>
<p style="color:#64748b;font-size:0.85rem;margin-bottom:8px">EVM Networks: Ethereum, Polygon, Arbitrum, Base, Optimism</p>
<div style="background:#111;border:1px solid #8b5cf6;border-radius:8px;padding:12px;margin-bottom:16px">
<p style="color:#8b5cf6;font-weight:600;font-size:0.85rem;margin-bottom:4px">Solana (SOL, USDC-SPL):</p>
<code style="color:#8b5cf6;font-size:0.8rem;word-break:break-all;display:block;margin-bottom:6px">2guKDsPScRpCCKuVEGKBPFvodSNtZF4ArYeSC6oy6pf6</code>
<button onclick="navigator.clipboard.writeText('2guKDsPScRpCCKuVEGKBPFvodSNtZF4ArYeSC6oy6pf6');this.textContent='Copied!';setTimeout(()=>this.textContent='Copy SOL Address',2000)" style="background:#8b5cf6;color:#fff;border:none;padding:6px 12px;border-radius:6px;cursor:pointer;font-weight:600;font-size:0.85rem">Copy SOL Address</button>
</div>
<p style="color:#64748b;font-size:0.85rem;margin-bottom:16px">Order ID: <code id="checkout-order-id" style="color:#6c63ff"></code></p>

<label style="color:#cbd5e1;display:block;margin-bottom:8px;font-weight:600;margin-top:16px">Paste Transaction Hash</label>
<input type="text" id="checkout-txhash" placeholder="0x..." style="width:100%;padding:12px 16px;background:#111;border:1px solid #2a2a2a;border-radius:8px;color:#e0e0e0;font-size:0.9rem;font-family:monospace;margin-bottom:16px">
<button onclick="verifyPayment()" id="verify-btn" style="width:100%;padding:14px;background:#22c55e;color:#000;border:none;border-radius:10px;font-size:1rem;font-weight:700;cursor:pointer">Verify Payment On-Chain</button>
<p id="verify-status" style="margin-top:12px;font-size:0.9rem;text-align:center"></p>
</div>

<div id="checkout-step3" style="display:none;text-align:center">
<div style="font-size:3rem;margin-bottom:16px">&#10003;</div>
<h3 style="color:#22c55e;font-size:1.3rem;margin-bottom:8px">Payment Verified!</h3>
<p style="color:#cbd5e1;margin-bottom:16px">Your API key has been upgraded.</p>
<p style="color:#fff;font-weight:700;margin-bottom:4px">API Key:</p>
<code id="checkout-apikey" style="color:#22c55e;font-size:1rem;display:block;margin-bottom:24px;word-break:break-all"></code>
<a href="/api-keys" style="display:inline-block;padding:12px 32px;background:#6c63ff;color:#fff;border-radius:8px;text-decoration:none;font-weight:600">View Dashboard</a>
</div>
</div>
</div>

<script>
let checkoutTier = 'pro';
let checkoutOrderId = '';

function startCheckout(tier) {
    checkoutTier = tier;
    const info = tier === 'enterprise'
        ? {name:'Enterprise',price:'$49.99/month',desc:'$49.99/month - 100,000 API calls/day'}
        : {name:'Pro',price:'$9.99/month',desc:'$9.99/month - 10,000 API calls/day'};
    document.getElementById('checkout-title').textContent = 'Upgrade to ' + info.name;
    document.getElementById('checkout-price').textContent = info.desc;
    document.getElementById('checkout-amount').textContent = info.price.replace('/month','');
    document.getElementById('checkout-step1').style.display = 'block';
    document.getElementById('checkout-step2').style.display = 'none';
    document.getElementById('checkout-step3').style.display = 'none';
    document.getElementById('checkout-modal').style.display = 'flex';
}
function closeCheckout() { document.getElementById('checkout-modal').style.display = 'none'; }

async function createOrder() {
    const email = document.getElementById('checkout-email').value.trim();
    if (!email || !email.includes('@')) { alert('Enter a valid email.'); return; }
    const btn = document.getElementById('checkout-btn');
    btn.textContent = 'Creating order...';
    btn.disabled = true;
    try {
        const res = await fetch('/payments/create', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, tier: checkoutTier})
        });
        const data = await res.json();
        if (data.order_id) {
            checkoutOrderId = data.order_id;
            document.getElementById('checkout-order-id').textContent = data.order_id;
            document.getElementById('checkout-step1').style.display = 'none';
            document.getElementById('checkout-step2').style.display = 'block';
        } else {
            alert('Error creating order: ' + JSON.stringify(data));
        }
    } catch(e) { alert('Network error. Try again.'); }
    btn.textContent = 'Create Payment Order';
    btn.disabled = false;
}

async function verifyPayment() {
    const txHash = document.getElementById('checkout-txhash').value.trim();
    const isEvm = txHash.startsWith('0x') && txHash.length === 66;
    const isSolana = !txHash.startsWith('0x') && txHash.length >= 43 && txHash.length <= 88;
    if (!txHash || (!isEvm && !isSolana)) {
        alert('Enter a valid transaction hash. EVM: 0x + 64 hex chars. Solana: 43-88 base58 chars.');
        return;
    }
    const btn = document.getElementById('verify-btn');
    const status = document.getElementById('verify-status');
    btn.textContent = 'Verifying on-chain...';
    btn.disabled = true;
    status.style.color = '#94a3b8';
    status.textContent = 'Checking transaction across all supported networks...';
    try {
        const res = await fetch('/payments/verify-tx', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({order_id: checkoutOrderId, tx_hash: txHash})
        });
        const data = await res.json();
        if (data.status === 'verified' || data.status === 'already_paid') {
            document.getElementById('checkout-step2').style.display = 'none';
            document.getElementById('checkout-step3').style.display = 'block';
            document.getElementById('checkout-apikey').textContent = data.api_key || 'Check /api-keys dashboard';
        } else if (data.status === 'unverified') {
            status.style.color = '#f59e0b';
            status.textContent = 'Transaction not confirmed yet. Wait a few minutes and try again.';
        } else if (data.status === 'underpaid') {
            status.style.color = '#ef4444';
            status.textContent = 'Underpaid: received $' + (data.received||0).toFixed(2) + ' of $' + (data.expected||0).toFixed(2) + '. Send the remaining amount.';
        } else {
            status.style.color = '#ef4444';
            status.textContent = data.message || 'Verification failed. Check the tx hash.';
        }
    } catch(e) {
        status.style.color = '#ef4444';
        status.textContent = 'Network error. Try again.';
    }
    btn.textContent = 'Verify Payment On-Chain';
    btn.disabled = false;
}

document.querySelectorAll('.faq-q').forEach(q => q.addEventListener('click', () => q.parentElement.classList.toggle('open')));
</script>
</body></html>"""))

# Rate limiting (simple in-memory)
rate_limits: dict[str, list[float]] = {}
RATE_LIMIT = 100  # requests per minute
RATE_WINDOW = 60  # seconds


def check_rate_limit(client_ip: str) -> bool:
    now = time.time()
    if client_ip not in rate_limits:
        rate_limits[client_ip] = []
    rate_limits[client_ip] = [t for t in rate_limits[client_ip] if now - t < RATE_WINDOW]
    if len(rate_limits[client_ip]) >= RATE_LIMIT:
        return False
    rate_limits[client_ip].append(now)
    return True


# --- Analytics DB ---
ANALYTICS_DB = Path(__file__).parent / "data" / "analytics.db"
ANALYTICS_DB.parent.mkdir(parents=True, exist_ok=True)
_analytics_lock = threading.Lock()


def _init_analytics():
    conn = sqlite3.connect(str(ANALYTICS_DB))
    conn.execute("""CREATE TABLE IF NOT EXISTS pageviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT NOT NULL,
        ip TEXT,
        user_agent TEXT,
        referrer TEXT,
        timestamp TEXT NOT NULL
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS daily_stats (
        date TEXT NOT NULL,
        path TEXT NOT NULL,
        views INTEGER DEFAULT 0,
        unique_ips INTEGER DEFAULT 0,
        PRIMARY KEY (date, path)
    )""")
    conn.commit()
    conn.close()

_init_analytics()


# --- API Key System ---
API_KEYS_DB = Path(__file__).parent / "data" / "api_keys.db"
_keys_lock = threading.Lock()


def _init_keys_db():
    conn = sqlite3.connect(str(API_KEYS_DB))
    conn.execute("""CREATE TABLE IF NOT EXISTS api_keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        api_key TEXT NOT NULL UNIQUE,
        tier TEXT DEFAULT 'free',
        requests_today INTEGER DEFAULT 0,
        requests_total INTEGER DEFAULT 0,
        daily_limit INTEGER DEFAULT 100,
        created_at TEXT NOT NULL,
        last_used TEXT
    )""")
    conn.commit()
    conn.close()

_init_keys_db()


def generate_api_key() -> str:
    return f"tp_{uuid.uuid4().hex[:24]}"


def register_api_key(email: str) -> dict:
    with _keys_lock:
        conn = sqlite3.connect(str(API_KEYS_DB))
        existing = conn.execute("SELECT api_key, tier FROM api_keys WHERE email = ?", (email,)).fetchone()
        if existing:
            conn.close()
            return {"api_key": existing[0], "tier": existing[1], "existing": True}
        key = generate_api_key()
        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            "INSERT INTO api_keys (email, api_key, tier, created_at) VALUES (?, ?, 'free', ?)",
            (email, key, now)
        )
        conn.commit()
        conn.close()
        wl_file = Path(__file__).parent / "waitlist.txt"
        with open(wl_file, "a") as f:
            f.write(f"{email},{now},api_key_signup\n")
        return {"api_key": key, "tier": "free", "daily_limit": 100, "existing": False}


def upgrade_api_key(email: str, tier: str = "pro") -> dict:
    limits = {"pro": 10000, "enterprise": 100000}
    daily_limit = limits.get(tier, 10000)
    with _keys_lock:
        conn = sqlite3.connect(str(API_KEYS_DB))
        row = conn.execute("SELECT api_key FROM api_keys WHERE email = ?", (email,)).fetchone()
        if row:
            conn.execute(
                "UPDATE api_keys SET tier = ?, daily_limit = ? WHERE email = ?",
                (tier, daily_limit, email)
            )
            conn.commit()
            api_key = row[0]
        else:
            api_key = generate_api_key()
            now = datetime.now(timezone.utc).isoformat()
            conn.execute(
                "INSERT INTO api_keys (email, api_key, tier, daily_limit, created_at) VALUES (?, ?, ?, ?, ?)",
                (email, api_key, tier, daily_limit, now)
            )
            conn.commit()
        conn.close()
        return {"api_key": api_key, "tier": tier, "daily_limit": daily_limit}


def check_api_key(key: str) -> dict | None:
    with _keys_lock:
        conn = sqlite3.connect(str(API_KEYS_DB))
        row = conn.execute(
            "SELECT email, tier, requests_today, daily_limit FROM api_keys WHERE api_key = ?", (key,)
        ).fetchone()
        if not row:
            conn.close()
            return None
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        conn.execute(
            "UPDATE api_keys SET requests_today = requests_today + 1, requests_total = requests_total + 1, last_used = ? WHERE api_key = ?",
            (today, key)
        )
        conn.commit()
        conn.close()
        return {"email": row[0], "tier": row[1], "requests_today": row[2], "daily_limit": row[3]}


# --- Crypto Payment Gateway Integration ---
# OxaPay Merchant API (primary gateway)
OXAPAY_MERCHANT_KEY = os.environ.get("OXAPAY_MERCHANT_KEY", "sandbox")
OXAPAY_API_URL = "https://api.oxapay.com/merchants/request"
# NOWPayments (backup gateway, no KYC)
NOWPAYMENTS_API_KEY = os.environ.get("NOWPAYMENTS_API_KEY", "")
PAYMENTS_DB = Path(__file__).parent / "data" / "payments.db"
_payments_lock = threading.Lock()


def _init_payments_db():
    conn = sqlite3.connect(str(PAYMENTS_DB))
    conn.execute("""CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        track_id TEXT UNIQUE,
        order_id TEXT UNIQUE,
        email TEXT NOT NULL,
        tier TEXT NOT NULL,
        amount REAL NOT NULL,
        currency TEXT DEFAULT 'USD',
        status TEXT DEFAULT 'pending',
        payment_url TEXT,
        created_at TEXT NOT NULL,
        paid_at TEXT,
        callback_data TEXT
    )""")
    conn.commit()
    conn.close()

_init_payments_db()


async def create_nowpayments_invoice(amount: float, email: str, tier: str, order_id: str, callback_url: str, return_url: str) -> dict:
    """Create invoice via NOWPayments API (backup gateway)."""
    if not NOWPAYMENTS_API_KEY:
        return {"success": False}
    try:
        payload = {
            "price_amount": amount,
            "price_currency": "usd",
            "order_id": order_id,
            "order_description": f"ToolPipe {tier.title()} Plan",
            "ipn_callback_url": callback_url,
            "success_url": return_url,
            "cancel_url": return_url.replace("success", "cancel"),
        }
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                "https://api.nowpayments.io/v1/invoice",
                json=payload,
                headers={"x-api-key": NOWPAYMENTS_API_KEY, "Content-Type": "application/json"},
            )
            data = resp.json()
        if data.get("id"):
            return {
                "success": True,
                "gateway": "nowpayments",
                "payment_url": data.get("invoice_url", ""),
                "track_id": str(data["id"]),
                "order_id": order_id,
            }
    except Exception:
        pass
    return {"success": False}


async def create_payment_invoice(amount: float, email: str, tier: str, order_id: str, callback_url: str, return_url: str) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    crypto_addresses = {
        "ETH/ERC-20 (Ethereum, Polygon, Arbitrum, Base, Optimism)": WALLET_ADDRESS,
        "Solana (SOL, USDC-SPL)": SOLANA_WALLET,
    }

    # Try OxaPay Merchant API first
    try:
        payload = {
            "merchant": OXAPAY_MERCHANT_KEY,
            "amount": amount,
            "currency": "USD",
            "lifeTime": 60,
            "feePaidByPayer": 1,
            "callbackUrl": callback_url,
            "returnUrl": return_url,
            "email": email,
            "orderId": order_id,
            "description": f"ToolPipe {tier.title()} Plan",
        }
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                OXAPAY_API_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            data = resp.json()

        if data.get("result") == 100 and data.get("payLink"):
            track_id = str(data.get("trackId", ""))
            payment_url = data.get("payLink", "")
            with _payments_lock:
                conn = sqlite3.connect(str(PAYMENTS_DB))
                conn.execute(
                    "INSERT OR REPLACE INTO payments (track_id, order_id, email, tier, amount, status, payment_url, created_at) VALUES (?, ?, ?, ?, ?, 'pending', ?, ?)",
                    (track_id, order_id, email, tier, amount, payment_url, now)
                )
                conn.commit()
                conn.close()
            return {"success": True, "gateway": "oxapay", "payment_url": payment_url, "track_id": track_id, "order_id": order_id}
    except Exception:
        pass

    # Try NOWPayments as backup
    np_result = await create_nowpayments_invoice(amount, email, tier, order_id, callback_url, return_url)
    if np_result.get("success"):
        with _payments_lock:
            conn = sqlite3.connect(str(PAYMENTS_DB))
            conn.execute(
                "INSERT OR REPLACE INTO payments (track_id, order_id, email, tier, amount, status, payment_url, created_at) VALUES (?, ?, ?, ?, ?, 'pending', ?, ?)",
                (np_result.get("track_id", order_id), order_id, email, tier, amount, np_result.get("payment_url", ""), now)
            )
            conn.commit()
            conn.close()
        return np_result

    # Direct crypto payment (always-available fallback)
    with _payments_lock:
        conn = sqlite3.connect(str(PAYMENTS_DB))
        conn.execute(
            "INSERT OR REPLACE INTO payments (track_id, order_id, email, tier, amount, status, created_at) VALUES (?, ?, ?, ?, ?, 'awaiting_direct', ?)",
            (order_id, order_id, email, tier, amount, now)
        )
        conn.commit()
        conn.close()
    result = {
        "success": True,
        "gateway": "direct_crypto",
        "payment_method": "crypto_direct",
        "crypto_addresses": crypto_addresses,
        "evm_address": WALLET_ADDRESS,
        "accepted_evm": ["ETH", "USDC", "USDT", "DAI", "BUSD", "WETH", "BNB", "AVAX", "any ERC-20"],
        "evm_networks": ["Ethereum", "Polygon", "Arbitrum", "Base", "Optimism", "BSC", "Avalanche"],
        "amount_usd": amount,
        "order_id": order_id,
        "qr_code_url": f"/qr/generate?text=ethereum:{WALLET_ADDRESS}&size=300",
        "verify_endpoint": "POST /payments/verify-tx with {order_id, tx_hash}",
        "instructions": f"Send ${amount} worth of crypto to any address above. Then POST /payments/verify-tx with your tx_hash and order_id ({order_id}). Your API key upgrades instantly on verification.",
    }
    if SOLANA_WALLET:
        result["solana_address"] = SOLANA_WALLET
        result["accepted_solana"] = ["SOL", "USDC-SPL"]
    return result


def record_pageview(path: str, ip: str, user_agent: str, referrer: str):
    try:
        with _analytics_lock:
            conn = sqlite3.connect(str(ANALYTICS_DB))
            now = datetime.now(timezone.utc).isoformat()
            today = now[:10]
            conn.execute(
                "INSERT INTO pageviews (path, ip, user_agent, referrer, timestamp) VALUES (?, ?, ?, ?, ?)",
                (path, ip, user_agent, referrer, now)
            )
            conn.execute("""INSERT INTO daily_stats (date, path, views, unique_ips)
                VALUES (?, ?, 1, 1)
                ON CONFLICT(date, path) DO UPDATE SET views = views + 1""", (today, path))
            conn.commit()
            conn.close()
    except Exception:
        pass


# Snippet injected before </body> on all HTML pages
INJECT_SNIPPET = """
<!-- Analytics & Monetization -->
<div id="tp-banner" style="position:fixed;bottom:0;left:0;right:0;background:linear-gradient(135deg,#302b63,#24243e);color:#fff;padding:10px 20px;text-align:center;font-family:-apple-system,sans-serif;font-size:14px;z-index:9999;display:flex;align-items:center;justify-content:center;gap:12px;flex-wrap:wrap;">
  <span>Get a free API key for 100+ developer endpoints:</span>
  <form id="tp-email-form" style="display:flex;gap:6px;" onsubmit="return tpCapture(event)">
    <input type="email" id="tp-email" placeholder="you@email.com" required style="padding:6px 12px;border:none;border-radius:6px;font-size:14px;width:200px;">
    <button type="submit" style="background:#6c63ff;color:#fff;padding:6px 16px;border-radius:6px;border:none;font-weight:600;cursor:pointer;">Get Free Key</button>
  </form>
  <a href="/pricing" style="color:#aaa;text-decoration:underline;font-size:12px;margin-left:8px;">Pro plans</a>
  <button onclick="this.parentElement.style.display='none'" style="background:none;border:none;color:#fff;cursor:pointer;font-size:18px;margin-left:8px;">x</button>
</div>
<div id="tp-success" style="display:none;position:fixed;bottom:0;left:0;right:0;background:#22c55e;color:#fff;padding:14px 20px;text-align:center;font-family:-apple-system,sans-serif;font-size:14px;z-index:9999;">
  Check your dashboard! Your free API key: <strong id="tp-key-display"></strong> <a href="/api-keys" style="color:#fff;margin-left:12px;">View Dashboard</a>
</div>
<script>
fetch('/analytics/track', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({path:location.pathname,ref:document.referrer})}).catch(()=>{});
function tpCapture(e){
  e.preventDefault();
  var email=document.getElementById('tp-email').value;
  fetch('/api-keys/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:email})})
  .then(r=>r.json()).then(d=>{
    if(d.api_key){
      document.getElementById('tp-key-display').textContent=d.api_key;
      document.getElementById('tp-banner').style.display='none';
      document.getElementById('tp-success').style.display='block';
      setTimeout(()=>{document.getElementById('tp-success').style.display='none'},15000);
    }
  }).catch(()=>{});
  return false;
}
</script>
<div style="background:#1a1a2e;padding:24px 20px;font-family:-apple-system,sans-serif;margin-top:40px;">
<div style="max-width:900px;margin:0 auto;text-align:center;font-size:13px;line-height:2;">
<a href="/" style="color:#6c63ff;text-decoration:none;margin:0 8px;">ToolPipe</a>
<a href="/json-formatter" style="color:#94a3b8;text-decoration:none;margin:0 8px;">JSON Formatter</a>
<a href="/css-minifier" style="color:#94a3b8;text-decoration:none;margin:0 8px;">CSS Minifier</a>
<a href="/javascript-minifier" style="color:#94a3b8;text-decoration:none;margin:0 8px;">JS Minifier</a>
<a href="/uuid-generator" style="color:#94a3b8;text-decoration:none;margin:0 8px;">UUID Generator</a>
<a href="/regex-tester" style="color:#94a3b8;text-decoration:none;margin:0 8px;">Regex Tester</a>
<a href="/jwt-decoder" style="color:#94a3b8;text-decoration:none;margin:0 8px;">JWT Decoder</a>
<a href="/password-generator" style="color:#94a3b8;text-decoration:none;margin:0 8px;">Password Generator</a>
<a href="/hash-generator" style="color:#94a3b8;text-decoration:none;margin:0 8px;">Hash Generator</a>
<a href="/base64-encoder" style="color:#94a3b8;text-decoration:none;margin:0 8px;">Base64</a>
<a href="/json-to-yaml" style="color:#94a3b8;text-decoration:none;margin:0 8px;">JSON to YAML</a>
<a href="/qr-code-generator" style="color:#94a3b8;text-decoration:none;margin:0 8px;">QR Generator</a>
<a href="/merge-pdf" style="color:#94a3b8;text-decoration:none;margin:0 8px;">Merge PDF</a>
<a href="/image-to-base64" style="color:#94a3b8;text-decoration:none;margin:0 8px;">Image to Base64</a>
<a href="/color-picker" style="color:#94a3b8;text-decoration:none;margin:0 8px;">Color Picker</a>
<a href="/whats-my-ip" style="color:#94a3b8;text-decoration:none;margin:0 8px;">My IP</a>
<a href="/xml-formatter" style="color:#94a3b8;text-decoration:none;margin:0 8px;">XML Formatter</a>
<a href="/yaml-validator" style="color:#94a3b8;text-decoration:none;margin:0 8px;">YAML Validator</a>
<a href="/csv-to-json" style="color:#94a3b8;text-decoration:none;margin:0 8px;">CSV to JSON</a>
<a href="/diff-checker" style="color:#94a3b8;text-decoration:none;margin:0 8px;">Diff Checker</a>
<a href="/sql-formatter" style="color:#94a3b8;text-decoration:none;margin:0 8px;">SQL Formatter</a>
<a href="/api-keys" style="color:#6c63ff;text-decoration:none;margin:0 8px;">Free API Key</a>
<a href="/pricing" style="color:#6c63ff;text-decoration:none;margin:0 8px;">Pro Plans</a>
<a href="/quickstart" style="color:#6c63ff;text-decoration:none;margin:0 8px;">Quick Start</a>
<br><span style="color:#475569;">130+ free developer tools by ToolPipe. No signup, no tracking. <a href="/donate" style="color:#6c63ff;text-decoration:none;">Support us</a></span>
</div></div>
"""


def inject_snippet(html: str) -> str:
    """Inject analytics, favicon, and monetization snippet into HTML pages."""
    favicon_tag = '<link rel="icon" href="/favicon.ico" type="image/x-icon">'
    if "<head>" in html and 'rel="icon"' not in html:
        html = html.replace("<head>", "<head>" + favicon_tag)
    if "</body>" in html:
        return html.replace("</body>", INJECT_SNIPPET + "</body>")
    return html + INJECT_SNIPPET


def serve_html(path: Path, track_path: str = "") -> HTMLResponse:
    """Serve an HTML file with injected analytics/monetization."""
    if path.exists():
        return HTMLResponse(inject_snippet(path.read_text()))
    return HTMLResponse("<h1>Page not found</h1>", status_code=404)


# Paths that don't need API key auth (free for everyone)
FREE_PATHS = {
    "/", "/docs", "/openapi.json", "/pricing", "/api-keys", "/donate",
    "/health", "/tools", "/favicon.ico", "/analytics/track", "/analytics/dashboard",
    "/payments/create", "/payments/webhook", "/payments/success", "/payments/verify-tx",
    "/payments/verify", "/payments/pending", "/payments/status", "/payments/agent-pay",
    "/api-for-ai-agents", "/free-api-tools",
    "/api-keys/register", "/apis.json", "/sitemap.xml", "/robots.txt",
    "/.well-known/mcp.json", "/.well-known/ai-plugin.json", "/quickstart",
}
# API paths that are always free (no key needed, but rate limited by IP)
FREE_API_PATHS = {
    "/qr/generate", "/hash/generate", "/uuid/generate",
    "/base64/encode", "/base64/decode", "/url/encode", "/url/decode",
    "/text/analyze", "/json/format", "/json/validate", "/markdown/to-html",
    "/api/pricing",
}
# Premium API paths that require paid tier
PREMIUM_API_PATHS = {
    "/seo/analyze", "/pdf/merge", "/pdf/split", "/pdf/compress",
    "/pdf/protect", "/pdf/watermark", "/api/text/summarize",
    "/api/code/format", "/meta/extract", "/image/resize",
    "/api/web/extract", "/api/code/analyze", "/api/schema/generate",
    "/api/prompt/build", "/api/test/endpoint",
    "/api/web/compare", "/api/bulk/hash", "/api/bulk/url-check",
    "/api/web/structured-extract", "/api/domain/intel", "/api/bulk/dns",
    "/api/web/monitor", "/api/test/suite", "/api/web/sitemap", "/api/web/robots",
}


def _reset_daily_counts():
    """Reset daily request counts at midnight UTC."""
    try:
        with _keys_lock:
            conn = sqlite3.connect(str(API_KEYS_DB))
            conn.execute("UPDATE api_keys SET requests_today = 0")
            conn.commit()
            conn.close()
    except Exception:
        pass


_last_reset_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    global _last_reset_date
    client_ip = request.client.host if request.client else "unknown"
    path = str(request.url.path)

    # Reset daily counts at midnight UTC
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if today != _last_reset_date:
        _reset_daily_counts()
        _last_reset_date = today

    # IP-based rate limiting for all requests
    if not check_rate_limit(client_ip):
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded. Max 100 requests per minute.",
                "upgrade": "Get an API key at /api-keys or upgrade at /pricing for higher limits.",
            },
        )

    # For API endpoints, check API key and enforce daily limits
    is_api_path = path.startswith("/api/") or path in PREMIUM_API_PATHS or any(path.startswith(p) for p in ("/qr/", "/hash/", "/uuid/", "/base64/", "/url/", "/text/", "/json/", "/seo/", "/pdf/", "/meta/", "/image/", "/markdown/"))
    is_free_path = path in FREE_PATHS or path in FREE_API_PATHS or not is_api_path

    if is_api_path and not is_free_path:
        api_key = request.headers.get("x-api-key", "") or request.query_params.get("api_key", "")
        is_premium = path in PREMIUM_API_PATHS

        if api_key:
            key_info = check_api_key(api_key)
            if not key_info:
                return JSONResponse(
                    status_code=401,
                    content={"error": "Invalid API key.", "get_key": "Register at /api-keys/register"},
                )
            if key_info["requests_today"] >= key_info["daily_limit"]:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": f"Daily limit reached ({key_info['daily_limit']} calls/day for {key_info['tier']} tier).",
                        "upgrade": "Upgrade at /pricing for higher limits.",
                        "tier": key_info["tier"],
                    },
                )
            if is_premium and key_info["tier"] == "free":
                return JSONResponse(
                    status_code=402,
                    content={
                        "error": "This endpoint requires a Pro or Enterprise plan.",
                        "endpoint": path,
                        "upgrade": "Upgrade at /pricing. Pay with crypto, no KYC needed.",
                        "pricing": {"pro": "$9.99/mo (10K calls/day)", "enterprise": "$49.99/mo (100K calls/day)"},
                    },
                )
        else:
            # No API key provided: allow free-tier endpoints, block premium
            if is_premium:
                return JSONResponse(
                    status_code=402,
                    content={
                        "error": "API key required for premium endpoints.",
                        "get_key": "Get a free key at /api-keys/register (100 calls/day). Upgrade at /pricing.",
                        "endpoint": path,
                    },
                )

    # Track pageviews for page requests
    if not path.startswith("/analytics") and not path.startswith("/health"):
        ua = request.headers.get("user-agent", "")
        ref = request.headers.get("referer", "")
        record_pageview(path, client_ip, ua, ref)

    response = await call_next(request)
    return response


# --- Health ---

LANDING_HTML = Path(__file__).parent / "landing.html"
TOOLS_HTML = Path(__file__).parent.parent / "web-tools" / "index.html"
INVOICE_HTML = Path(__file__).parent.parent / "invoice-generator" / "index.html"
MONITOR_HTML = Path(__file__).parent.parent / "uptime-monitor" / "index.html"
PDF_HTML = Path(__file__).parent.parent / "pdf-tools" / "index.html"
WEBHOOK_HTML = Path(__file__).parent.parent / "webhook-tester" / "index.html"
SHORTENER_HTML = Path(__file__).parent.parent / "url-shortener" / "index.html"
PASTE_HTML = Path(__file__).parent.parent / "pastebin" / "index.html"
DOWN_HTML = Path(__file__).parent.parent / "downdetector" / "index.html"
SEO_PAGES_DIR = Path(__file__).parent.parent / "seo-pages"

# Import external modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "url-shortener"))
import db as url_db
sys.path.insert(0, str(Path(__file__).parent.parent / "uptime-monitor"))
import monitor as uptime_monitor


@app.get("/", response_class=HTMLResponse)
async def root():
    if LANDING_HTML.exists():
        return HTMLResponse(inject_snippet(LANDING_HTML.read_text()))
    return HTMLResponse("<h1>ToolPipe API</h1><p><a href='/docs'>API Docs</a></p>")


@app.get("/tools", response_class=HTMLResponse)
async def tools_page():
    # Auto-generate tools listing from SEO pages
    tools = []
    if SEO_PAGES_DIR.exists():
        for p in sorted(SEO_PAGES_DIR.glob("*.html")):
            slug = p.stem
            # Extract title from the file
            content = p.read_text()
            import re as _re
            title_match = _re.search(r'<title>(.*?)</title>', content)
            title = title_match.group(1).split(' - ')[0].split(' | ')[0] if title_match else slug.replace('-', ' ').title()
            if slug in ('pricing', 'polymarket-dashboard', 'blog-free-developer-tools', 'api-consulting', 'ai-automation-consulting', 'api-reference-cheat-sheet'):
                continue  # Skip non-tool pages
            tools.append((slug, title))

    tool_cards = ""
    for slug, title in tools:
        tool_cards += f'<a href="/{slug}" style="display:block;padding:16px;background:#fff;border-radius:10px;box-shadow:0 1px 4px rgba(0,0,0,0.06);text-decoration:none;color:#333;transition:transform 0.2s" onmouseover="this.style.transform=\'translateY(-2px)\'" onmouseout="this.style.transform=\'none\'"><strong style="color:#1a1a2e">{title}</strong></a>\n'

    html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>100+ Free Developer Tools - ToolPipe</title>
<meta name="description" content="100+ free online developer tools: JSON formatter, regex tester, QR generator, PDF tools, hash generator, UUID, DNS lookup, and more. No signup needed.">
<style>*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f8f9fa;color:#333}}nav{{background:#1a1a2e;color:#fff;padding:12px 20px;display:flex;justify-content:space-between;font-size:.9rem}}nav a{{color:#6c63ff;text-decoration:none}}.container{{max-width:1100px;margin:0 auto;padding:20px}}h1{{font-size:2.5rem;text-align:center;margin:40px 0 8px}}p.sub{{text-align:center;color:#666;margin-bottom:40px;font-size:1.1rem}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px}}footer{{text-align:center;padding:40px;color:#999;font-size:.85rem}}footer a{{color:#6c63ff;text-decoration:none;margin:0 8px}}input{{width:100%;max-width:400px;margin:0 auto 32px;display:block;padding:14px 20px;border:2px solid #ddd;border-radius:10px;font-size:1rem}}input:focus{{outline:none;border-color:#6c63ff}}</style></head><body>
<nav><a href="/">ToolPipe</a><div><a href="/demo">Demo</a> | <a href="/docs">API Docs</a> | <a href="/pricing">Pricing</a> | <a href="/api-keys">Get API Key</a></div></nav>
<div class="container">
<h1>{len(tools)}+ Free Developer Tools</h1>
<p class="sub">All tools run in your browser. No signup required. Also available as REST APIs.</p>
<input type="text" id="search" placeholder="Search tools..." oninput="filter()">
<div class="grid" id="grid">{tool_cards}</div>
</div>
<footer><a href="/">Home</a> | <a href="/demo">Demo</a> | <a href="/docs">API Docs</a> | <a href="/pricing">Pricing</a> | <a href="/api-keys">Get API Key</a></footer>
<script>function filter(){{const q=document.getElementById('search').value.toLowerCase();document.querySelectorAll('#grid > a').forEach(a=>{{a.style.display=a.textContent.toLowerCase().includes(q)?'block':'none'}})}}</script></body></html>"""
    return HTMLResponse(inject_snippet(html))


# IndexNow verification key
@app.get("/b4d8f2a1c3e5d7f9.txt")
async def indexnow_key():
    return Response(content="b4d8f2a1c3e5d7f9", media_type="text/plain")


@app.get("/invoice", response_class=HTMLResponse)
async def invoice_page():
    return serve_html(INVOICE_HTML)


@app.get("/api")
async def api_info():
    return {
        "service": "ToolPipe API",
        "version": "1.10.0",
        "status": "operational",
        "total_endpoints": "175+",
        "new_in_v1_7": [
            "/api/sql/format",
            "/api/html/strip",
            "/api/text/stats",
            "/api/number/format",
            "/api/xml/to-json",
            "/api/yaml/validate",
            "/api/env/parse",
            "/api/http-status/{code}",
            "/api/jwt/create",
            "/api/myip",
        ],
        "categories": {
            "json": ["/json/format", "/json/validate", "/api/json/query", "/api/json/to-schema", "/api/diff/json"],
            "text": ["/text/analyze", "/api/text/count", "/api/text/similarity", "/api/text/stats", "/api/diff/text", "/api/lorem", "/api/slug/generate", "/api/markdown/strip", "/api/html/strip"],
            "crypto_hash": ["/hash/generate", "/api/jwt/decode", "/api/jwt/create", "/api/password/check"],
            "web": ["/meta/extract", "/seo/analyze", "/api/web/extract", "/api/headers/analyze", "/api/test/endpoint", "/api/myip"],
            "convert": ["/base64", "/api/convert/json-to-yaml", "/api/convert/csv-to-json", "/api/time/convert", "/color/convert", "/api/color/palette", "/api/xml/to-json", "/api/yaml/validate", "/api/number/format"],
            "generate": ["/qr/generate", "/uuid/generate", "/api/fake/generate", "/api/gitignore/generate", "/api/dockerfile/generate", "/api/lorem"],
            "network": ["/dns/lookup", "/api/ip/lookup", "/api/validate/ip", "/api/validate/email", "/api/http-status/{code}"],
            "code": ["/api/code/analyze", "/api/schema/generate", "/api/regex/test", "/api/cron/parse", "/api/sql/format", "/api/env/parse"],
        },
        "mcp_server": {
            "stdio_tools": 97,
            "http_tools": 85,
            "http_endpoint": "/mcp",
        },
        "pricing": {
            "free": "100 requests/day, no signup",
            "pro": "$9.99/mo, 10,000 requests/day",
            "enterprise": "$49.99/mo, 100,000 requests/day",
        },
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


# --- QR Code Generation ---

class QRRequest(BaseModel):
    data: str
    size: int = 300
    error_correction: str = "M"  # L, M, Q, H


@app.post("/qr/generate")
async def generate_qr(req: QRRequest):
    ec_map = {"L": qrcode.constants.ERROR_CORRECT_L, "M": qrcode.constants.ERROR_CORRECT_M,
              "Q": qrcode.constants.ERROR_CORRECT_Q, "H": qrcode.constants.ERROR_CORRECT_H}
    ec = ec_map.get(req.error_correction.upper(), qrcode.constants.ERROR_CORRECT_M)

    qr = qrcode.QRCode(version=1, error_correction=ec, box_size=10, border=4)
    qr.add_data(req.data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((req.size, req.size), Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


@app.get("/qr/generate")
async def generate_qr_get(data: str = Query(...), size: int = Query(300)):
    return await generate_qr(QRRequest(data=data, size=size))


# --- URL Metadata Extraction ---

@app.get("/meta/extract")
async def extract_metadata(url: str = Query(...)):
    parsed = urlparse(url)
    if not parsed.scheme:
        url = "https://" + url

    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "ToolPipe-Bot/1.0"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not fetch URL: {str(e)}")

    soup = BeautifulSoup(resp.text, "html.parser")

    def get_meta(name: str) -> Optional[str]:
        tag = soup.find("meta", attrs={"property": name}) or soup.find("meta", attrs={"name": name})
        return tag.get("content") if tag else None

    title = soup.title.string.strip() if soup.title and soup.title.string else None

    return {
        "url": str(resp.url),
        "status_code": resp.status_code,
        "title": title,
        "description": get_meta("description") or get_meta("og:description"),
        "og_title": get_meta("og:title"),
        "og_image": get_meta("og:image"),
        "og_type": get_meta("og:type"),
        "og_url": get_meta("og:url"),
        "twitter_card": get_meta("twitter:card"),
        "twitter_title": get_meta("twitter:title"),
        "twitter_image": get_meta("twitter:image"),
        "favicon": _get_favicon(soup, url),
        "language": soup.html.get("lang") if soup.html else None,
        "canonical": _get_canonical(soup),
    }


def _get_favicon(soup, base_url):
    link = soup.find("link", rel=lambda x: x and "icon" in x)
    if link and link.get("href"):
        href = link["href"]
        if href.startswith("//"):
            return "https:" + href
        if href.startswith("/"):
            parsed = urlparse(base_url)
            return f"{parsed.scheme}://{parsed.netloc}{href}"
        return href
    return None


def _get_canonical(soup):
    link = soup.find("link", rel="canonical")
    return link["href"] if link and link.get("href") else None


# --- Markdown to HTML ---

class MarkdownRequest(BaseModel):
    content: str
    extensions: list[str] = ["extra", "codehilite", "toc"]


@app.post("/markdown/to-html")
async def markdown_to_html(req: MarkdownRequest):
    html = markdown.markdown(req.content, extensions=req.extensions)
    return {"html": html, "char_count": len(html)}


# --- Text Analysis ---

class TextRequest(BaseModel):
    text: str


@app.post("/text/analyze")
async def analyze_text(req: TextRequest):
    text = req.text
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    word_count = len(words)
    sentence_count = len(sentences)
    avg_word_length = sum(len(w) for w in words) / max(word_count, 1)
    avg_sentence_length = word_count / max(sentence_count, 1)

    # Flesch reading ease approximation
    syllable_count = sum(_count_syllables(w) for w in words)
    flesch = 206.835 - 1.015 * avg_sentence_length - 84.6 * (syllable_count / max(word_count, 1))

    return {
        "characters": len(text),
        "characters_no_spaces": len(text.replace(" ", "")),
        "words": word_count,
        "sentences": sentence_count,
        "paragraphs": len(paragraphs),
        "avg_word_length": round(avg_word_length, 2),
        "avg_sentence_length": round(avg_sentence_length, 2),
        "reading_time_minutes": round(word_count / 238, 2),
        "speaking_time_minutes": round(word_count / 150, 2),
        "flesch_reading_ease": round(flesch, 2),
    }


def _count_syllables(word: str) -> int:
    word = word.lower().strip(".,!?;:'\"")
    if len(word) <= 3:
        return 1
    vowels = "aeiouy"
    count = 0
    prev_vowel = False
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    if word.endswith("e"):
        count -= 1
    return max(count, 1)


# --- Hash Generation ---

class HashRequest(BaseModel):
    data: str
    algorithms: list[str] = ["md5", "sha256"]


@app.post("/hash/generate")
async def generate_hash(req: HashRequest):
    results = {}
    data_bytes = req.data.encode("utf-8")
    for algo in req.algorithms:
        if algo in hashlib.algorithms_available:
            h = hashlib.new(algo)
            h.update(data_bytes)
            results[algo] = h.hexdigest()
        else:
            results[algo] = f"unsupported algorithm: {algo}"
    return {"input_length": len(req.data), "hashes": results}


# --- Image Resize ---

class ImageResizeRequest(BaseModel):
    url: str
    width: int
    height: Optional[int] = None
    format: str = "PNG"


@app.post("/image/resize")
async def resize_image(req: ImageResizeRequest):
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(req.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not fetch image: {str(e)}")

    try:
        img = Image.open(io.BytesIO(resp.content))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image data")

    if req.height:
        new_size = (req.width, req.height)
    else:
        ratio = req.width / img.width
        new_size = (req.width, int(img.height * ratio))

    img = img.resize(new_size, Image.LANCZOS)
    buf = io.BytesIO()
    fmt = req.format.upper()
    if fmt == "JPG":
        fmt = "JPEG"
    if fmt == "JPEG" and img.mode == "RGBA":
        img = img.convert("RGB")
    img.save(buf, format=fmt)
    buf.seek(0)

    media_types = {"PNG": "image/png", "JPEG": "image/jpeg", "WEBP": "image/webp", "GIF": "image/gif"}
    return StreamingResponse(buf, media_type=media_types.get(fmt, "image/png"))


# --- JSON to CSV ---

class JsonToCsvRequest(BaseModel):
    data: list[dict]
    delimiter: str = ","


@app.post("/json/to-csv")
async def json_to_csv(req: JsonToCsvRequest):
    if not req.data:
        return {"csv": "", "rows": 0}

    headers = list(req.data[0].keys())
    lines = [req.delimiter.join(headers)]
    for row in req.data:
        values = [str(row.get(h, "")).replace(req.delimiter, " ") for h in headers]
        lines.append(req.delimiter.join(values))

    csv_text = "\n".join(lines)
    return {"csv": csv_text, "rows": len(req.data), "columns": len(headers)}


# --- UUID Generation ---

@app.get("/uuid/generate")
async def generate_uuid(count: int = Query(1, ge=1, le=100), version: int = Query(4)):
    if version == 4:
        uuids = [str(uuid.uuid4()) for _ in range(count)]
    elif version == 1:
        uuids = [str(uuid.uuid1()) for _ in range(count)]
    else:
        raise HTTPException(status_code=400, detail="Supported versions: 1, 4")
    return {"uuids": uuids, "version": version, "count": len(uuids)}


# --- DNS Lookup ---

@app.get("/dns/lookup")
async def dns_lookup(domain: str = Query(...)):
    import socket
    try:
        results = socket.getaddrinfo(domain, None)
        ips = list(set(r[4][0] for r in results))
        return {"domain": domain, "addresses": ips, "count": len(ips)}
    except socket.gaierror as e:
        raise HTTPException(status_code=400, detail=f"DNS lookup failed: {str(e)}")


# --- Color Converter ---

@app.get("/color/convert")
async def convert_color(hex: str = Query(..., description="Hex color like #FF5733 or FF5733")):
    hex_clean = hex.lstrip("#")
    if len(hex_clean) not in (3, 6):
        raise HTTPException(status_code=400, detail="Invalid hex color")
    if len(hex_clean) == 3:
        hex_clean = "".join(c * 2 for c in hex_clean)

    r, g, b = int(hex_clean[0:2], 16), int(hex_clean[2:4], 16), int(hex_clean[4:6], 16)

    # HSL conversion
    r_norm, g_norm, b_norm = r / 255, g / 255, b / 255
    max_c, min_c = max(r_norm, g_norm, b_norm), min(r_norm, g_norm, b_norm)
    l = (max_c + min_c) / 2
    if max_c == min_c:
        h = s = 0.0
    else:
        d = max_c - min_c
        s = d / (2 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)
        if max_c == r_norm:
            h = (g_norm - b_norm) / d + (6 if g_norm < b_norm else 0)
        elif max_c == g_norm:
            h = (b_norm - r_norm) / d + 2
        else:
            h = (r_norm - g_norm) / d + 4
        h /= 6

    return {
        "hex": f"#{hex_clean.upper()}",
        "rgb": {"r": r, "g": g, "b": b},
        "rgb_string": f"rgb({r}, {g}, {b})",
        "hsl": {"h": round(h * 360, 1), "s": round(s * 100, 1), "l": round(l * 100, 1)},
        "hsl_string": f"hsl({round(h * 360, 1)}, {round(s * 100, 1)}%, {round(l * 100, 1)}%)",
    }


# --- Base64 Encode/Decode ---

class Base64Request(BaseModel):
    data: str
    action: str = "encode"  # encode or decode


@app.post("/base64")
async def base64_convert(req: Base64Request):
    if req.action == "encode":
        result = base64.b64encode(req.data.encode()).decode()
    elif req.action == "decode":
        try:
            result = base64.b64decode(req.data).decode()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid base64 data")
    else:
        raise HTTPException(status_code=400, detail="Action must be 'encode' or 'decode'")
    return {"result": result, "action": req.action}


# --- CSS/JS Minify ---

class MinifyRequest(BaseModel):
    code: str = ""
    css: str = ""


@app.post("/api/css/minify")
async def css_minify(req: MinifyRequest):
    css = req.css or req.code
    if not css:
        raise HTTPException(status_code=400, detail="Provide 'css' or 'code' field")
    original_size = len(css.encode())
    # Remove comments
    result = re.sub(r'/\*[\s\S]*?\*/', '', css)
    # Collapse whitespace
    result = re.sub(r'\s+', ' ', result)
    result = re.sub(r'\s*([{}:;,])\s*', r'\1', result)
    result = re.sub(r';}', '}', result)
    result = result.strip()
    minified_size = len(result.encode())
    saved = round((1 - minified_size / original_size) * 100, 1) if original_size > 0 else 0
    return {"result": result, "original_size": original_size, "minified_size": minified_size, "saved_percent": saved}


@app.post("/api/js/minify")
async def js_minify(req: MinifyRequest):
    js = req.code
    if not js:
        raise HTTPException(status_code=400, detail="Provide 'code' field")
    original_size = len(js.encode())
    # Remove multi-line comments
    result = re.sub(r'/\*[\s\S]*?\*/', '', js)
    # Remove single-line comments
    result = re.sub(r'([^:])//.*$', r'\1', result, flags=re.MULTILINE)
    # Collapse whitespace
    result = re.sub(r'\s+', ' ', result).strip()
    minified_size = len(result.encode())
    saved = round((1 - minified_size / original_size) * 100, 1) if original_size > 0 else 0
    return {"result": result, "original_size": original_size, "minified_size": minified_size, "saved_percent": saved}


class YamlConvertRequest(BaseModel):
    json_data: str = ""
    yaml_data: str = ""


@app.post("/api/convert/json-to-yaml")
async def json_to_yaml_api(req: YamlConvertRequest):
    if not req.json_data:
        raise HTTPException(status_code=400, detail="Provide 'json_data' field")
    try:
        data = json.loads(req.json_data)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")

    def to_yaml(obj, indent=0):
        prefix = "  " * indent
        if obj is None:
            return "null"
        if isinstance(obj, bool):
            return "true" if obj else "false"
        if isinstance(obj, (int, float)):
            return str(obj)
        if isinstance(obj, str):
            if any(c in obj for c in ':\n#"\'') or obj == '':
                return json.dumps(obj)
            return obj
        if isinstance(obj, list):
            if not obj:
                return "[]"
            return "\n".join(f"{prefix}- {to_yaml(item, indent + 1).lstrip()}" for item in obj)
        if isinstance(obj, dict):
            if not obj:
                return "{}"
            return "\n".join(f"{prefix}{k}: {to_yaml(v, indent + 1).lstrip() if isinstance(v, (str, int, float, bool, type(None))) else chr(10) + to_yaml(v, indent + 1)}" for k, v in obj.items())
        return str(obj)

    return {"yaml": to_yaml(data), "success": True}


# --- Uptime Monitor ---

@app.get("/monitor", response_class=HTMLResponse)
async def monitor_page():
    if MONITOR_HTML.exists():
        return HTMLResponse(inject_snippet(MONITOR_HTML.read_text()))
    return HTMLResponse("<h1>PingPulse coming soon</h1>")


class AddMonitorRequest(BaseModel):
    name: str
    url: str
    interval_seconds: int = 300


@app.post("/monitor/add")
async def add_monitor(req: AddMonitorRequest):
    conn = uptime_monitor.get_db()
    # Limit to 20 monitors (free tier)
    count = conn.execute("SELECT COUNT(*) as c FROM monitors").fetchone()["c"]
    if count >= 20:
        raise HTTPException(status_code=400, detail="Maximum 20 monitors on free tier")
    cursor = conn.execute(
        "INSERT INTO monitors (name, url, interval_seconds) VALUES (?, ?, ?)",
        (req.name, req.url, req.interval_seconds),
    )
    conn.commit()
    monitor_id = cursor.lastrowid
    conn.close()
    # Run first check immediately
    await _check_single_monitor(monitor_id)
    return {"id": monitor_id, "name": req.name, "url": req.url}


@app.get("/monitor/list")
async def list_monitors():
    conn = uptime_monitor.get_db()
    monitors = conn.execute("SELECT * FROM monitors ORDER BY id").fetchall()
    result = []
    for m in monitors:
        stats = uptime_monitor.get_monitor_stats(m["id"], hours=24)
        result.append({**dict(m), "stats": stats})
    conn.close()
    return {"monitors": result}


@app.delete("/monitor/{monitor_id}")
async def delete_monitor(monitor_id: int):
    conn = uptime_monitor.get_db()
    conn.execute("DELETE FROM checks WHERE monitor_id = ?", (monitor_id,))
    conn.execute("DELETE FROM monitors WHERE id = ?", (monitor_id,))
    conn.commit()
    conn.close()
    return {"deleted": True}


@app.post("/monitor/{monitor_id}/check")
async def check_monitor_now(monitor_id: int):
    return await _check_single_monitor(monitor_id)


async def _check_single_monitor(monitor_id: int):
    conn = uptime_monitor.get_db()
    mon = conn.execute("SELECT * FROM monitors WHERE id = ?", (monitor_id,)).fetchone()
    if not mon:
        conn.close()
        raise HTTPException(status_code=404, detail="Monitor not found")
    result = await uptime_monitor.check_url(mon["url"], mon["expected_status"])
    conn.execute(
        "INSERT INTO checks (monitor_id, status_code, response_time_ms, is_up, error) VALUES (?, ?, ?, ?, ?)",
        (monitor_id, result["status_code"], result["response_time_ms"], result["is_up"], result["error"]),
    )
    conn.commit()
    conn.close()
    return result


@app.post("/monitor/run-all")
async def run_all_checks():
    count = await uptime_monitor.run_checks()
    return {"checked": count}


# --- SEO Analyzer ---

SEO_HTML = Path(__file__).parent.parent / "seo-analyzer" / "index.html"


@app.get("/seo", response_class=HTMLResponse)
async def seo_page():
    if SEO_HTML.exists():
        return HTMLResponse(inject_snippet(SEO_HTML.read_text()))
    return HTMLResponse("<h1>SEO Analyzer coming soon</h1>")


@app.get("/seo/analyze")
async def analyze_seo(url: str = Query(...)):
    parsed = urlparse(url)
    if not parsed.scheme:
        url = "https://" + url
        parsed = urlparse(url)

    start_time = time.time()
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "ToolPipe-SEO-Bot/1.0"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not fetch URL: {str(e)}")

    elapsed_ms = int((time.time() - start_time) * 1000)
    soup = BeautifulSoup(resp.text, "html.parser")

    def get_meta(name):
        tag = soup.find("meta", attrs={"property": name}) or soup.find("meta", attrs={"name": name})
        return tag.get("content", "").strip() if tag else ""

    # Meta analysis
    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    description = get_meta("description") or get_meta("og:description")
    canonical = ""
    canon_tag = soup.find("link", rel="canonical")
    if canon_tag:
        canonical = canon_tag.get("href", "")
    language = soup.html.get("lang", "") if soup.html else ""

    meta_score = 100
    meta_recs = []
    if not title:
        meta_score -= 30
        meta_recs.append("Add a title tag. This is critical for SEO.")
    elif len(title) < 30:
        meta_score -= 10
        meta_recs.append("Title is too short. Aim for 30-60 characters.")
    elif len(title) > 60:
        meta_score -= 5
        meta_recs.append("Title may be truncated in search results. Keep under 60 characters.")
    if not description:
        meta_score -= 25
        meta_recs.append("Add a meta description. This appears in search results.")
    elif len(description) < 120:
        meta_score -= 10
        meta_recs.append("Meta description is short. Aim for 120-160 characters.")
    elif len(description) > 160:
        meta_score -= 5
        meta_recs.append("Meta description may be truncated. Keep under 160 characters.")
    if not canonical:
        meta_score -= 5
        meta_recs.append("Set a canonical URL to prevent duplicate content issues.")
    if not language:
        meta_score -= 5
        meta_recs.append("Set the lang attribute on the html tag.")

    # OG tags
    og_title = get_meta("og:title")
    og_desc = get_meta("og:description")
    og_image = get_meta("og:image")
    twitter_card = get_meta("twitter:card")

    og_score = 100
    og_recs = []
    if not og_title:
        og_score -= 25
        og_recs.append("Add og:title for better social media sharing.")
    if not og_desc:
        og_score -= 25
        og_recs.append("Add og:description for social media previews.")
    if not og_image:
        og_score -= 25
        og_recs.append("Add og:image. Posts with images get significantly more engagement.")
    if not twitter_card:
        og_score -= 15
        og_recs.append("Add twitter:card meta tag for Twitter/X previews.")

    # Headings
    h1s = soup.find_all("h1")
    h2s = soup.find_all("h2")
    h3s = soup.find_all("h3")
    h1_texts = [h.get_text(strip=True) for h in h1s][:5]

    heading_score = 100
    heading_recs = []
    if len(h1s) == 0:
        heading_score -= 30
        heading_recs.append("Add an H1 tag. Every page should have exactly one H1.")
    elif len(h1s) > 1:
        heading_score -= 15
        heading_recs.append(f"Found {len(h1s)} H1 tags. Best practice is exactly one H1 per page.")
    if len(h2s) == 0:
        heading_score -= 15
        heading_recs.append("Add H2 subheadings to structure your content.")

    # Links
    all_links = soup.find_all("a", href=True)
    internal = 0
    external = 0
    nofollow = 0
    for a in all_links:
        href = a.get("href", "")
        rel = a.get("rel", [])
        if "nofollow" in rel:
            nofollow += 1
        link_parsed = urlparse(href)
        if link_parsed.netloc and link_parsed.netloc != parsed.netloc:
            external += 1
        else:
            internal += 1

    link_score = 100
    link_recs = []
    if internal < 3:
        link_score -= 20
        link_recs.append("Add more internal links to help search engines discover your content.")
    if external == 0:
        link_score -= 10
        link_recs.append("Consider adding external links to authoritative sources.")

    # Images
    all_imgs = soup.find_all("img")
    imgs_with_alt = sum(1 for img in all_imgs if img.get("alt", "").strip())
    imgs_without_alt = len(all_imgs) - imgs_with_alt

    img_score = 100
    img_recs = []
    if imgs_without_alt > 0:
        img_score -= min(30, imgs_without_alt * 10)
        img_recs.append(f"{imgs_without_alt} image(s) missing alt text. Add descriptive alt attributes for accessibility and SEO.")
    if len(all_imgs) == 0:
        img_recs.append("Consider adding images to make content more engaging.")

    # Technical
    is_https = parsed.scheme == "https"
    has_viewport = bool(soup.find("meta", attrs={"name": "viewport"}))
    charset_tag = soup.find("meta", charset=True)
    charset = charset_tag.get("charset", "") if charset_tag else ""
    page_size_kb = round(len(resp.text) / 1024, 1)

    tech_score = 100
    tech_recs = []
    if not is_https:
        tech_score -= 30
        tech_recs.append("Switch to HTTPS. Google prioritizes secure sites.")
    if not has_viewport:
        tech_score -= 20
        tech_recs.append("Add a viewport meta tag for mobile responsiveness.")
    if elapsed_ms > 1000:
        tech_score -= 15
        tech_recs.append(f"Page took {elapsed_ms}ms to load. Aim for under 500ms.")
    elif elapsed_ms > 500:
        tech_score -= 5
    if page_size_kb > 500:
        tech_score -= 10
        tech_recs.append("Page size is large. Consider optimizing assets.")

    # Overall score
    weights = [0.25, 0.1, 0.15, 0.1, 0.15, 0.25]
    scores = [meta_score, og_score, heading_score, link_score, img_score, tech_score]
    overall = int(sum(w * s for w, s in zip(weights, scores)))

    return {
        "url": str(resp.url),
        "score": max(0, min(100, overall)),
        "meta": {
            "score": max(0, meta_score),
            "title": title,
            "title_length": len(title),
            "description": description,
            "desc_length": len(description),
            "canonical": canonical,
            "language": language,
            "recommendations": meta_recs,
        },
        "og": {
            "score": max(0, og_score),
            "og_title": og_title,
            "og_description": og_desc,
            "og_image": og_image,
            "twitter_card": twitter_card,
            "recommendations": og_recs,
        },
        "headings": {
            "score": max(0, heading_score),
            "h1_count": len(h1s),
            "h2_count": len(h2s),
            "h3_count": len(h3s),
            "h1_texts": h1_texts,
            "recommendations": heading_recs,
        },
        "links": {
            "score": max(0, link_score),
            "total": len(all_links),
            "internal": internal,
            "external": external,
            "nofollow": nofollow,
            "recommendations": link_recs,
        },
        "images": {
            "score": max(0, img_score),
            "total": len(all_imgs),
            "with_alt": imgs_with_alt,
            "without_alt": imgs_without_alt,
            "recommendations": img_recs,
        },
        "technical": {
            "score": max(0, tech_score),
            "https": is_https,
            "response_time_ms": elapsed_ms,
            "page_size_kb": page_size_kb,
            "has_viewport": has_viewport,
            "charset": charset,
            "recommendations": tech_recs,
        },
    }


# --- Sitemap ---

@app.get("/sitemap.xml")
async def sitemap(request: Request):
    # Auto-detect base URL from request
    host = request.headers.get("host", "")
    scheme = "https" if "trycloudflare.com" in host or "toolpipe" in host else request.url.scheme
    base = f"{scheme}://{host}" if host else "https://assessing-scoop-authorities-sheet.trycloudflare.com"

    # Auto-generate from SEO pages directory
    seo_pages = []
    if SEO_PAGES_DIR.exists():
        seo_pages = [f"/{p.stem}" for p in SEO_PAGES_DIR.glob("*.html")]

    urls = [
        "/", "/tools", "/seo", "/invoice", "/monitor", "/pdf", "/webhooks", "/short", "/paste", "/down", "/pricing", "/docs",
        "/donate", "/api-keys", "/api-consulting", "/polymarket", "/quickstart", "/mcp-server", "/free-developer-api",
    ] + seo_pages
    urls = list(dict.fromkeys(urls))  # deduplicate while preserving order
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url in urls:
        xml += f'  <url><loc>{base}{url}</loc><changefreq>weekly</changefreq></url>\n'
    xml += '</urlset>'
    return Response(content=xml, media_type="application/xml")


INDEXNOW_KEY = "dc57971f04a84a7e99edf0b3c4105663"


@app.get("/robots.txt")
async def robots(request: Request):
    host = request.headers.get("host", "")
    scheme = "https" if "trycloudflare.com" in host or "toolpipe" in host else request.url.scheme
    base = f"{scheme}://{host}" if host else "https://assessing-scoop-authorities-sheet.trycloudflare.com"
    content = f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n"
    return Response(content=content, media_type="text/plain")


@app.get(f"/{INDEXNOW_KEY}.txt")
async def indexnow_key():
    return Response(content=INDEXNOW_KEY, media_type="text/plain")


@app.post("/api/indexnow/submit")
async def submit_indexnow(request: Request):
    """Submit URLs to IndexNow (Bing, Yandex, etc.)."""
    host = request.headers.get("host", "")
    scheme = "https" if "trycloudflare.com" in host else "http"
    base = f"{scheme}://{host}" if host else "https://assessing-scoop-authorities-sheet.trycloudflare.com"

    # Collect all URLs from SEO pages
    urls = [f"{base}/"]
    if SEO_PAGES_DIR.exists():
        urls.extend(f"{base}/{p.stem}" for p in SEO_PAGES_DIR.glob("*.html"))
    urls.extend(f"{base}{p}" for p in [
        "/tools", "/seo", "/invoice", "/monitor", "/pdf",
        "/webhooks", "/short", "/paste", "/down", "/docs",
    ])

    payload = {
        "host": host or "assessing-scoop-authorities-sheet.trycloudflare.com",
        "key": INDEXNOW_KEY,
        "keyLocation": f"{base}/{INDEXNOW_KEY}.txt",
        "urlList": urls[:100],
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post("https://api.indexnow.org/indexnow", json=payload)
            return {"status": resp.status_code, "urls_submitted": len(urls), "response": resp.text[:200]}
    except Exception as e:
        return {"error": str(e)}


# --- PDF Tools ---

PDF_MAX_SIZE = 50 * 1024 * 1024  # 50MB


@app.get("/pdf", response_class=HTMLResponse)
async def pdf_tools_page():
    if PDF_HTML.exists():
        return HTMLResponse(inject_snippet(PDF_HTML.read_text()))
    return HTMLResponse("<h1>PDF Tools coming soon</h1>")


async def _read_pdf_upload(file: UploadFile) -> bytes:
    data = await file.read()
    if len(data) > PDF_MAX_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max 50MB.")
    return data


@app.post("/pdf/merge")
async def pdf_merge(files: list[UploadFile] = File(...)):
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 PDF files to merge.")
    if len(files) > 20:
        raise HTTPException(status_code=400, detail="Max 20 files.")

    writer = PdfWriter()
    for f in files:
        data = await _read_pdf_upload(f)
        reader = PdfReader(io.BytesIO(data))
        for page in reader.pages:
            writer.add_page(page)

    buf = io.BytesIO()
    writer.write(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=merged.pdf"},
    )


@app.post("/pdf/split")
async def pdf_split(files: list[UploadFile] = File(...), pages: str = Form(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No file provided.")
    data = await _read_pdf_upload(files[0])
    reader = PdfReader(io.BytesIO(data))
    total = len(reader.pages)

    # Parse page ranges like "1-3, 5, 7-10"
    selected = set()
    for part in pages.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            start, end = int(start.strip()), int(end.strip())
            for i in range(max(1, start), min(total, end) + 1):
                selected.add(i)
        else:
            p = int(part.strip())
            if 1 <= p <= total:
                selected.add(p)

    if not selected:
        raise HTTPException(status_code=400, detail=f"No valid pages selected. PDF has {total} pages.")

    writer = PdfWriter()
    for i in sorted(selected):
        writer.add_page(reader.pages[i - 1])

    buf = io.BytesIO()
    writer.write(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=split.pdf"},
    )


@app.post("/pdf/compress")
async def pdf_compress(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No file provided.")
    data = await _read_pdf_upload(files[0])
    reader = PdfReader(io.BytesIO(data))

    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    for page in writer.pages:
        page.compress_content_streams()

    if reader.metadata:
        writer.add_metadata(reader.metadata)

    buf = io.BytesIO()
    writer.write(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=compressed.pdf"},
    )


@app.post("/pdf/protect")
async def pdf_protect(files: list[UploadFile] = File(...), password: str = Form(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No file provided.")
    if not password:
        raise HTTPException(status_code=400, detail="Password required.")
    data = await _read_pdf_upload(files[0])
    reader = PdfReader(io.BytesIO(data))

    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.encrypt(password)

    buf = io.BytesIO()
    writer.write(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=protected.pdf"},
    )


@app.post("/pdf/unlock")
async def pdf_unlock(files: list[UploadFile] = File(...), password: str = Form(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No file provided.")
    data = await _read_pdf_upload(files[0])
    reader = PdfReader(io.BytesIO(data))

    if reader.is_encrypted:
        if not reader.decrypt(password):
            raise HTTPException(status_code=400, detail="Wrong password.")

    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    buf = io.BytesIO()
    writer.write(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=unlocked.pdf"},
    )


@app.post("/pdf/rotate")
async def pdf_rotate(files: list[UploadFile] = File(...), angle: int = Form(90)):
    if not files:
        raise HTTPException(status_code=400, detail="No file provided.")
    if angle not in (90, 180, 270):
        raise HTTPException(status_code=400, detail="Angle must be 90, 180, or 270.")
    data = await _read_pdf_upload(files[0])
    reader = PdfReader(io.BytesIO(data))

    writer = PdfWriter()
    for page in reader.pages:
        page.rotate(angle)
        writer.add_page(page)

    buf = io.BytesIO()
    writer.write(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=rotated.pdf"},
    )


@app.post("/pdf/watermark")
async def pdf_watermark(files: list[UploadFile] = File(...), text: str = Form(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No file provided.")
    if not text:
        raise HTTPException(status_code=400, detail="Watermark text required.")
    data = await _read_pdf_upload(files[0])
    reader = PdfReader(io.BytesIO(data))

    # Create watermark PDF in memory
    wm_buf = io.BytesIO()
    c = rl_canvas.Canvas(wm_buf, pagesize=letter)
    c.setFont("Helvetica", 48)
    c.setFillAlpha(0.15)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.saveState()
    c.translate(letter[0] / 2, letter[1] / 2)
    c.rotate(45)
    c.drawCentredString(0, 0, text)
    c.restoreState()
    c.save()
    wm_buf.seek(0)
    wm_reader = PdfReader(wm_buf)
    wm_page = wm_reader.pages[0]

    writer = PdfWriter()
    for page in reader.pages:
        page.merge_page(wm_page)
        writer.add_page(page)

    buf = io.BytesIO()
    writer.write(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=watermarked.pdf"},
    )


@app.post("/pdf/info")
async def pdf_info(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No file provided.")
    data = await _read_pdf_upload(files[0])
    reader = PdfReader(io.BytesIO(data))

    meta = reader.metadata or {}
    info = {
        "filename": files[0].filename,
        "pages": len(reader.pages),
        "file_size": formatFileSize(len(data)),
        "file_size_bytes": len(data),
        "encrypted": reader.is_encrypted,
        "author": str(meta.get("/Author", "")) if meta.get("/Author") else "",
        "creator": str(meta.get("/Creator", "")) if meta.get("/Creator") else "",
        "producer": str(meta.get("/Producer", "")) if meta.get("/Producer") else "",
        "subject": str(meta.get("/Subject", "")) if meta.get("/Subject") else "",
        "title": str(meta.get("/Title", "")) if meta.get("/Title") else "",
    }

    # Page dimensions from first page
    if reader.pages:
        p = reader.pages[0]
        box = p.mediabox
        w = float(box.width) / 72  # Convert points to inches
        h = float(box.height) / 72
        info["page_width_inches"] = round(w, 2)
        info["page_height_inches"] = round(h, 2)
        info["page_size"] = f"{round(w, 1)}\" x {round(h, 1)}\""

    return info


def formatFileSize(bytes_val):
    if bytes_val < 1024:
        return f"{bytes_val} B"
    if bytes_val < 1048576:
        return f"{bytes_val / 1024:.1f} KB"
    return f"{bytes_val / 1048576:.1f} MB"


# --- Webhook Tester ---

# In-memory storage for webhook bins (24h expiry)
webhook_bins: dict[str, dict] = {}
WEBHOOK_BIN_EXPIRY = 86400  # 24 hours
WEBHOOK_MAX_REQUESTS = 500


def _clean_expired_bins():
    now = time.time()
    expired = [k for k, v in webhook_bins.items() if now - v["created"] > WEBHOOK_BIN_EXPIRY]
    for k in expired:
        del webhook_bins[k]


@app.get("/webhooks", response_class=HTMLResponse)
async def webhooks_page():
    if WEBHOOK_HTML.exists():
        return HTMLResponse(inject_snippet(WEBHOOK_HTML.read_text()))
    return HTMLResponse("<h1>WebhookBin coming soon</h1>")


@app.post("/webhook/create")
async def webhook_create():
    _clean_expired_bins()
    bin_id = uuid.uuid4().hex[:12]
    webhook_bins[bin_id] = {
        "created": time.time(),
        "requests": [],
    }
    return {"bin_id": bin_id}


@app.get("/webhook/bin/{bin_id}/requests")
async def webhook_get_requests(bin_id: str):
    if bin_id not in webhook_bins:
        raise HTTPException(status_code=404, detail="Bin not found or expired.")
    return {"requests": webhook_bins[bin_id]["requests"]}


@app.post("/webhook/bin/{bin_id}/clear")
async def webhook_clear(bin_id: str):
    if bin_id not in webhook_bins:
        raise HTTPException(status_code=404, detail="Bin not found or expired.")
    webhook_bins[bin_id]["requests"] = []
    return {"cleared": True}


@app.api_route("/webhook/catch/{bin_id}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def webhook_capture(bin_id: str, request: Request):
    _clean_expired_bins()
    if bin_id not in webhook_bins:
        raise HTTPException(status_code=404, detail="Bin not found or expired.")

    body_bytes = await request.body()
    body_text = ""
    try:
        body_text = body_bytes.decode("utf-8")
    except Exception:
        body_text = f"(binary data, {len(body_bytes)} bytes)"

    body_parsed = body_text
    try:
        body_parsed = json.loads(body_text)
    except Exception:
        pass

    req_data = {
        "id": uuid.uuid4().hex[:8],
        "method": request.method,
        "path": str(request.url.path),
        "query": dict(request.query_params),
        "headers": dict(request.headers),
        "body": body_parsed,
        "ip": request.client.host if request.client else "unknown",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "content_length": len(body_bytes),
    }

    bin_data = webhook_bins[bin_id]
    bin_data["requests"].append(req_data)
    if len(bin_data["requests"]) > WEBHOOK_MAX_REQUESTS:
        bin_data["requests"] = bin_data["requests"][-WEBHOOK_MAX_REQUESTS:]

    return {"status": "captured", "request_id": req_data["id"]}


# --- URL Shortener ---

@app.get("/short", response_class=HTMLResponse)
async def shortener_page():
    if SHORTENER_HTML.exists():
        return HTMLResponse(inject_snippet(SHORTENER_HTML.read_text()))
    return HTMLResponse("<h1>URL Shortener coming soon</h1>")


class ShortenRequest(BaseModel):
    url: str
    custom_code: Optional[str] = None


@app.post("/s/create")
async def create_short_url(req: ShortenRequest, request: Request):
    # Validate URL
    if not req.url.startswith(("http://", "https://")):
        req.url = "https://" + req.url
    parsed = urlparse(req.url)
    if not parsed.netloc:
        raise HTTPException(status_code=400, detail="Invalid URL.")

    # Custom code validation
    if req.custom_code:
        if len(req.custom_code) < 2 or len(req.custom_code) > 20:
            raise HTTPException(status_code=400, detail="Custom code must be 2-20 characters.")
        if not re.match(r'^[a-zA-Z0-9_-]+$', req.custom_code):
            raise HTTPException(status_code=400, detail="Custom code can only contain letters, numbers, hyphens, and underscores.")
        existing = url_db.get_url(req.custom_code)
        if existing:
            raise HTTPException(status_code=409, detail="Custom code already taken.")

    client_ip = request.client.host if request.client else None
    code = url_db.create_short_url(req.url, creator_ip=client_ip, custom_code=req.custom_code)
    return {"short_code": code, "short_url": f"/s/{code}", "long_url": req.url}


@app.get("/s/{short_code}/stats")
async def get_url_stats(short_code: str):
    stats = url_db.get_url_stats(short_code)
    if not stats:
        raise HTTPException(status_code=404, detail="Short URL not found.")
    return stats


@app.get("/s/{short_code}")
async def redirect_short_url(short_code: str, request: Request):
    from fastapi.responses import RedirectResponse
    url_data = url_db.get_url(short_code)
    if not url_data:
        raise HTTPException(status_code=404, detail="Short URL not found.")

    # Record click asynchronously
    url_db.record_click(
        url_data["id"],
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent", ""),
        referer=request.headers.get("referer", ""),
    )
    return RedirectResponse(url=url_data["long_url"], status_code=302)


# --- PasteBin ---

paste_store: dict[str, dict] = {}
PASTE_EXPIRY_MAP = {"1h": 3600, "24h": 86400, "7d": 604800, "30d": 2592000, "never": 0}
PASTE_MAX_SIZE = 500000  # 500KB


def _clean_expired_pastes():
    now = time.time()
    expired = [k for k, v in paste_store.items() if v["expiry_time"] and now > v["expiry_time"]]
    for k in expired:
        del paste_store[k]


@app.get("/paste", response_class=HTMLResponse)
async def paste_page():
    if PASTE_HTML.exists():
        return HTMLResponse(inject_snippet(PASTE_HTML.read_text()))
    return HTMLResponse("<h1>PasteBin coming soon</h1>")


class PasteRequest(BaseModel):
    content: str
    title: Optional[str] = None
    language: str = "text"
    expiry: str = "24h"


@app.post("/paste/create")
async def create_paste(req: PasteRequest):
    _clean_expired_pastes()
    if len(req.content) > PASTE_MAX_SIZE:
        raise HTTPException(status_code=400, detail="Content too large. Max 500KB.")
    if len(paste_store) > 10000:
        raise HTTPException(status_code=503, detail="Service at capacity. Try again later.")

    paste_id = uuid.uuid4().hex[:8]
    expiry_seconds = PASTE_EXPIRY_MAP.get(req.expiry, 86400)
    expiry_time = time.time() + expiry_seconds if expiry_seconds > 0 else None

    paste_store[paste_id] = {
        "content": req.content,
        "title": req.title or "",
        "language": req.language,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "expiry": req.expiry,
        "expiry_time": expiry_time,
        "views": 0,
    }
    return {"id": paste_id}


@app.get("/paste/{paste_id}/raw")
async def get_paste_raw(paste_id: str):
    _clean_expired_pastes()
    paste = paste_store.get(paste_id)
    if not paste:
        raise HTTPException(status_code=404, detail="Paste not found or expired.")
    paste["views"] += 1
    return paste


@app.get("/paste/{paste_id}", response_class=HTMLResponse)
async def view_paste(paste_id: str):
    if PASTE_HTML.exists():
        return HTMLResponse(inject_snippet(PASTE_HTML.read_text()))
    raise HTTPException(status_code=404, detail="Paste not found.")


# --- Down Checker ---

@app.get("/down", response_class=HTMLResponse)
async def down_page():
    if DOWN_HTML.exists():
        return HTMLResponse(inject_snippet(DOWN_HTML.read_text()))
    return HTMLResponse("<h1>Down Checker coming soon</h1>")


@app.get("/down/check")
async def check_down(url: str = Query(...)):
    import socket
    parsed = urlparse(url)
    if not parsed.scheme:
        url = "https://" + url
        parsed = urlparse(url)

    domain = parsed.netloc or parsed.path.split("/")[0]
    if not domain:
        raise HTTPException(status_code=400, detail="Invalid URL.")

    # DNS lookup
    ip = None
    try:
        results = socket.getaddrinfo(domain, None)
        ip = results[0][4][0] if results else None
    except Exception:
        pass

    # HTTP check
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "ToolPipe-DownChecker/1.0"})
        elapsed_ms = int((time.time() - start) * 1000)
        is_up = resp.status_code < 500
        return {
            "url": str(resp.url),
            "domain": domain,
            "is_up": is_up,
            "status_code": resp.status_code,
            "response_time_ms": elapsed_ms,
            "ip": ip,
            "error": None,
        }
    except Exception as e:
        elapsed_ms = int((time.time() - start) * 1000)
        return {
            "url": url,
            "domain": domain,
            "is_up": False,
            "status_code": None,
            "response_time_ms": elapsed_ms,
            "ip": ip,
            "error": str(e),
        }


# --- IP Lookup / Geolocation ---

@app.get("/ip/lookup")
async def ip_lookup(ip: Optional[str] = Query(None)):
    """Look up geolocation info for an IP address. Uses ip-api.com free tier."""
    target = ip or "check"  # "check" returns the requester's IP info
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"http://ip-api.com/json/{target}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query")
        data = resp.json()
        if data.get("status") == "fail":
            raise HTTPException(status_code=400, detail=data.get("message", "Lookup failed"))
        return data
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Upstream lookup failed: {str(e)}")


@app.get("/ip/my")
async def my_ip(request: Request):
    """Returns the requester's IP address."""
    client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    if not client_ip:
        client_ip = request.client.host if request.client else "unknown"
    return {"ip": client_ip}


# --- User Agent Parser ---

@app.get("/useragent/parse")
async def parse_user_agent(ua: Optional[str] = Query(None), request: Request = None):
    """Parse a user agent string into components."""
    user_agent = ua or (request.headers.get("user-agent", "") if request else "")
    if not user_agent:
        raise HTTPException(status_code=400, detail="No user agent provided.")

    result = {
        "raw": user_agent,
        "is_bot": False,
        "browser": "Unknown",
        "browser_version": "",
        "os": "Unknown",
        "device": "Desktop",
    }

    # Bot detection
    bot_patterns = ["bot", "crawl", "spider", "slurp", "mediapartners", "facebookexternalhit", "bingpreview"]
    ua_lower = user_agent.lower()
    for pattern in bot_patterns:
        if pattern in ua_lower:
            result["is_bot"] = True
            result["device"] = "Bot"
            break

    # Browser detection
    if "Firefox/" in user_agent:
        result["browser"] = "Firefox"
        m = re.search(r"Firefox/([\d.]+)", user_agent)
        if m: result["browser_version"] = m.group(1)
    elif "Edg/" in user_agent:
        result["browser"] = "Edge"
        m = re.search(r"Edg/([\d.]+)", user_agent)
        if m: result["browser_version"] = m.group(1)
    elif "Chrome/" in user_agent:
        result["browser"] = "Chrome"
        m = re.search(r"Chrome/([\d.]+)", user_agent)
        if m: result["browser_version"] = m.group(1)
    elif "Safari/" in user_agent and "Chrome" not in user_agent:
        result["browser"] = "Safari"
        m = re.search(r"Version/([\d.]+)", user_agent)
        if m: result["browser_version"] = m.group(1)

    # OS detection
    if "Windows" in user_agent: result["os"] = "Windows"
    elif "Mac OS X" in user_agent: result["os"] = "macOS"
    elif "Linux" in user_agent: result["os"] = "Linux"
    elif "Android" in user_agent: result["os"] = "Android"
    elif "iPhone" in user_agent or "iPad" in user_agent: result["os"] = "iOS"

    # Device
    if "Mobile" in user_agent or "Android" in user_agent:
        result["device"] = "Mobile"
    elif "iPad" in user_agent or "Tablet" in user_agent:
        result["device"] = "Tablet"

    return result


# --- API Key Endpoints ---

class ApiKeyRequest(BaseModel):
    email: str


@app.post("/api-keys/register")
async def register_key(req: ApiKeyRequest):
    email = req.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Valid email required")
    result = register_api_key(email)
    return result


@app.get("/api-keys", response_class=HTMLResponse)
async def api_keys_dashboard():
    return HTMLResponse("""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>ToolPipe API Keys - Developer Dashboard</title>
<meta name="description" content="Get your free API key for 100+ developer utility endpoints. JSON, PDF, QR, hash, UUID, and more.">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0a0a0a;color:#e0e0e0}
.container{max-width:700px;margin:60px auto;padding:0 20px}
h1{font-size:2rem;color:#fff;margin-bottom:8px}
.sub{color:#94a3b8;margin-bottom:32px}
.card{background:#1a1a1a;border:2px solid #2a2a2a;border-radius:12px;padding:24px;margin-bottom:20px}
.card h2{color:#fff;font-size:1.2rem;margin-bottom:12px}
input{width:100%;background:#111;border:1px solid #2a2a2a;color:#e0e0e0;padding:12px;border-radius:8px;font-size:1rem;margin-bottom:12px}
button{background:#6c63ff;color:#fff;border:none;padding:12px 24px;border-radius:8px;font-weight:600;cursor:pointer;font-size:1rem;width:100%}
button:hover{background:#5b52ee}
.key-display{background:#0d1117;border:1px solid #30363d;border-radius:8px;padding:16px;font-family:monospace;font-size:1.1rem;color:#58a6ff;word-break:break-all;display:none;margin-top:12px}
.tiers{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:24px}
.tier{background:#1a1a1a;border:2px solid #2a2a2a;border-radius:12px;padding:20px}
.tier.pro{border-color:#6c63ff}
.tier h3{color:#fff;margin-bottom:8px}
.tier .price{font-size:1.5rem;font-weight:700;color:#fff;margin-bottom:8px}
.tier .price span{font-size:0.85rem;color:#64748b}
.tier ul{list-style:none;padding:0}
.tier li{color:#94a3b8;padding:4px 0;font-size:0.9rem}
.tier li::before{content:"-> ";color:#6c63ff}
.endpoints{margin-top:24px;color:#94a3b8;font-size:0.9rem;line-height:1.8}
.endpoints code{background:#1a1a2e;padding:2px 6px;border-radius:4px;color:#a78bfa}
a{color:#6c63ff;text-decoration:none}
.back{display:inline-block;margin-top:24px}
</style></head><body>
<div class="container">
<h1>ToolPipe Developer API</h1>
<p class="sub">100+ utility endpoints. Free API key in 10 seconds.</p>

<div class="card">
<h2>Get Your Free API Key</h2>
<form onsubmit="return getKey(event)">
<input type="email" id="email" placeholder="your@email.com" required>
<button type="submit">Generate Free API Key</button>
</form>
<div class="key-display" id="key-result"></div>
</div>

<div class="tiers">
<div class="tier">
<h3>Free</h3>
<div class="price">$0 <span>/month</span></div>
<ul>
<li>100 requests/day</li>
<li>All endpoints</li>
<li>Community support</li>
<li>Rate limited</li>
</ul>
</div>
<div class="tier pro">
<h3>Pro</h3>
<div class="price">$9.99 <span>/month</span></div>
<ul>
<li>10,000 requests/day</li>
<li>All endpoints</li>
<li>Priority support</li>
<li>No rate limits</li>
<li>Bulk operations</li>
<li>Webhooks</li>
</ul>
<a href="/pricing" style="display:block;background:#6c63ff;color:#fff;text-align:center;padding:10px;border-radius:8px;margin-top:12px;font-weight:600;">Upgrade to Pro</a>
</div>
</div>

<div class="endpoints">
<h2 style="color:#fff;margin:24px 0 12px;">Popular Endpoints</h2>
<p><code>GET /api/qr?text=hello</code> Generate QR codes</p>
<p><code>POST /api/json/format</code> Format & validate JSON</p>
<p><code>GET /api/uuid</code> Generate UUIDs</p>
<p><code>POST /api/hash</code> Hash text (MD5/SHA)</p>
<p><code>GET /api/ip</code> IP geolocation</p>
<p><code>POST /api/markdown</code> Markdown to HTML</p>
<p><code>GET /api/password</code> Generate passwords</p>
<p style="margin-top:12px;"><a href="/docs">View all 100+ endpoints</a></p>
</div>

<a href="/" class="back">Back to ToolPipe</a>
</div>
<script>
function getKey(e){
  e.preventDefault();
  var email=document.getElementById('email').value;
  fetch('/api-keys/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:email})})
  .then(r=>r.json()).then(d=>{
    var el=document.getElementById('key-result');
    if(d.api_key){
      el.style.display='block';
      el.innerHTML='Your API Key: <strong>'+d.api_key+'</strong><br><br><small>Add to requests as: <code>?api_key='+d.api_key+'</code> or header <code>X-API-Key: '+d.api_key+'</code></small>';
    }
  });
  return false;
}
</script>
</body></html>""")


# --- API Key Usage Endpoint ---

@app.get("/api-keys/usage")
async def api_key_usage(api_key: str = "", email: str = ""):
    """Check API key usage and limits. AI agents can use this to monitor their consumption."""
    if not api_key and not email:
        raise HTTPException(status_code=400, detail="Provide api_key or email parameter")
    with _keys_lock:
        conn = sqlite3.connect(str(API_KEYS_DB))
        if api_key:
            row = conn.execute(
                "SELECT email, api_key, tier, requests_today, requests_total, daily_limit, created_at, last_used FROM api_keys WHERE api_key = ?",
                (api_key,)
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT email, api_key, tier, requests_today, requests_total, daily_limit, created_at, last_used FROM api_keys WHERE email = ?",
                (email.strip().lower(),)
            ).fetchone()
        conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="API key not found")
    return {
        "email": row[0],
        "api_key": row[1][:8] + "..." if api_key else row[1],
        "tier": row[2],
        "requests_today": row[3],
        "requests_total": row[4],
        "daily_limit": row[5],
        "remaining_today": max(0, row[5] - row[3]),
        "created_at": row[6],
        "last_used": row[7],
        "upgrade_url": "/pricing" if row[2] == "free" else None,
    }


# --- Waitlist ---

waitlist_emails: list[str] = []


class WaitlistRequest(BaseModel):
    email: str


@app.post("/waitlist/join")
async def join_waitlist(req: WaitlistRequest):
    email = req.email.strip().lower()
    if email not in waitlist_emails:
        waitlist_emails.append(email)
        # Also append to a file for persistence
        wl_file = Path(__file__).parent / "waitlist.txt"
        with open(wl_file, "a") as f:
            f.write(f"{email},{datetime.now(timezone.utc).isoformat()}\n")
    return {"joined": True, "position": len(waitlist_emails)}


# --- Polymarket Analysis Dashboard ---

@app.get("/api/polymarket/markets")
async def polymarket_markets():
    """Fetch and analyze current Polymarket markets."""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(f"https://gamma-api.polymarket.com/markets", params={
                "active": "true", "closed": "false", "limit": 50
            })
            resp.raise_for_status()
            markets = resp.json()

        results = []
        for m in markets:
            vol = 0
            try:
                vol = float(m.get("volume", 0) or 0)
            except (ValueError, TypeError):
                pass
            if vol < 5000:
                continue

            outcome_prices = m.get("outcomePrices", "")
            if isinstance(outcome_prices, str):
                try:
                    outcome_prices = json.loads(outcome_prices)
                except (json.JSONDecodeError, TypeError):
                    outcome_prices = []

            outcomes = m.get("outcomes", "")
            if isinstance(outcomes, str):
                try:
                    outcomes = json.loads(outcomes)
                except (json.JSONDecodeError, TypeError):
                    outcomes = ["Yes", "No"]

            tokens = []
            for i, price in enumerate(outcome_prices):
                tokens.append({
                    "outcome": outcomes[i] if i < len(outcomes) else f"Outcome {i}",
                    "price": float(price) if price else None,
                })

            results.append({
                "question": m.get("question", ""),
                "volume": vol,
                "liquidity": float(m.get("liquidity", 0) or 0),
                "end_date": m.get("endDate", ""),
                "category": m.get("category", ""),
                "slug": m.get("slug", ""),
                "tokens": tokens,
            })

        results.sort(key=lambda x: x["volume"], reverse=True)
        return {"markets": results[:30], "total_scanned": len(markets)}
    except Exception as e:
        return {"error": str(e), "markets": []}


@app.get("/api/polymarket/analysis")
async def polymarket_analysis():
    """Premium: structured analysis from latest scan with short-term focus."""
    latest_path = Path(__file__).parent.parent / "polymarket" / "research" / "latest_scan.md"
    if not latest_path.exists():
        return {"error": "No analysis available. Scanner has not run yet.", "markets": []}
    content = latest_path.read_text()
    lines = content.split("\n")
    # Extract metadata
    date_line = next((l for l in lines if l.startswith("**Date:**")), "")
    total_line = next((l for l in lines if "Total Markets" in l), "")
    short_line = next((l for l in lines if "Short-Term" in l), "")
    return {
        "report_date": date_line.replace("**Date:**", "").strip(),
        "summary": {
            "total_scanned": total_line,
            "short_term": short_line,
        },
        "report_markdown": content,
        "note": "Full analysis updated every 2 hours. Premium API coming soon.",
    }


@app.get("/api/polymarket/short-term")
async def polymarket_short_term():
    """Short-term markets resolving within 30 days with analysis."""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get("https://gamma-api.polymarket.com/markets", params={
                "active": "true", "closed": "false", "limit": 100
            })
            resp.raise_for_status()
            markets = resp.json()

        from datetime import timezone as tz, timedelta
        now = datetime.now(tz.utc)
        cutoff = now + timedelta(days=30)
        results = []

        for m in markets:
            vol = 0
            try:
                vol = float(m.get("volume", 0) or 0)
            except (ValueError, TypeError):
                pass
            if vol < 10000:
                continue

            end_str = m.get("endDate", "")
            if not end_str:
                continue
            try:
                end_dt = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
                if end_dt > cutoff or end_dt <= now:
                    continue
                days_left = (end_dt - now).days
            except (ValueError, TypeError):
                continue

            outcome_prices = m.get("outcomePrices", "")
            if isinstance(outcome_prices, str):
                try:
                    outcome_prices = json.loads(outcome_prices)
                except (json.JSONDecodeError, TypeError):
                    outcome_prices = []

            outcomes = m.get("outcomes", "")
            if isinstance(outcomes, str):
                try:
                    outcomes = json.loads(outcomes)
                except (json.JSONDecodeError, TypeError):
                    outcomes = ["Yes", "No"]

            tokens = []
            for i, price in enumerate(outcome_prices):
                tokens.append({
                    "outcome": outcomes[i] if i < len(outcomes) else f"Outcome {i}",
                    "price": float(price) if price else None,
                })

            results.append({
                "question": m.get("question", ""),
                "days_left": days_left,
                "volume": vol,
                "liquidity": float(m.get("liquidity", 0) or 0),
                "end_date": end_str,
                "slug": m.get("slug", ""),
                "tokens": tokens,
            })

        results.sort(key=lambda x: x["volume"], reverse=True)
        return {"markets": results[:25], "total_short_term": len(results), "cutoff_days": 30}
    except Exception as e:
        return {"error": str(e), "markets": []}


@app.get("/polymarket", response_class=HTMLResponse)
async def polymarket_dashboard():
    return HTMLResponse(inject_snippet(Path(Path(__file__).parent.parent / "seo-pages" / "polymarket-dashboard.html").read_text()) if (Path(__file__).parent.parent / "seo-pages" / "polymarket-dashboard.html").exists() else "<h1>Coming soon</h1>")


# --- New Premium API Endpoints ---

import random as _random
import collections as _collections

PROGRAMMING_QUOTES = [
    {"quote": "Any fool can write code that a computer can understand. Good programmers write code that humans can understand.", "author": "Martin Fowler"},
    {"quote": "First, solve the problem. Then, write the code.", "author": "John Johnson"},
    {"quote": "Experience is the name everyone gives to their mistakes.", "author": "Oscar Wilde"},
    {"quote": "Code is like humor. When you have to explain it, it's bad.", "author": "Cory House"},
    {"quote": "Fix the cause, not the symptom.", "author": "Steve Maguire"},
    {"quote": "Optimism is an occupational hazard of programming: feedback is the treatment.", "author": "Kent Beck"},
    {"quote": "Simplicity is the soul of efficiency.", "author": "Austin Freeman"},
    {"quote": "Before software can be reusable it first has to be usable.", "author": "Ralph Johnson"},
    {"quote": "Make it work, make it right, make it fast.", "author": "Kent Beck"},
    {"quote": "Walking on water and developing software from a specification are easy if both are frozen.", "author": "Edward V. Berard"},
    {"quote": "If debugging is the process of removing software bugs, then programming must be the process of putting them in.", "author": "Edsger Dijkstra"},
    {"quote": "The best error message is the one that never shows up.", "author": "Thomas Fuchs"},
    {"quote": "A language that doesn't affect the way you think about programming is not worth knowing.", "author": "Alan Perlis"},
    {"quote": "The most disastrous thing that you can ever learn is your first programming language.", "author": "Alan Kay"},
    {"quote": "Deleted code is debugged code.", "author": "Jeff Sickel"},
    {"quote": "Programming isn't about what you know; it's about what you can figure out.", "author": "Chris Pine"},
    {"quote": "The only way to learn a new programming language is by writing programs in it.", "author": "Dennis Ritchie"},
    {"quote": "Sometimes it pays to stay in bed on Monday, rather than spending the rest of the week debugging Monday's code.", "author": "Dan Salomon"},
    {"quote": "Measuring programming progress by lines of code is like measuring aircraft building progress by weight.", "author": "Bill Gates"},
    {"quote": "Controlling complexity is the essence of computer programming.", "author": "Brian Kernighan"},
    {"quote": "The computer was born to solve problems that did not exist before.", "author": "Bill Gates"},
    {"quote": "There are only two kinds of languages: the ones people complain about and the ones nobody uses.", "author": "Bjarne Stroustrup"},
    {"quote": "Talk is cheap. Show me the code.", "author": "Linus Torvalds"},
    {"quote": "Programs must be written for people to read, and only incidentally for machines to execute.", "author": "Harold Abelson"},
    {"quote": "Always code as if the guy who ends up maintaining your code will be a violent psychopath who knows where you live.", "author": "John Woods"},
    {"quote": "In theory, there is no difference between theory and practice. But in practice, there is.", "author": "Jan L. A. van de Snepscheut"},
    {"quote": "Any sufficiently advanced technology is indistinguishable from magic.", "author": "Arthur C. Clarke"},
    {"quote": "Truth can only be found in one place: the code.", "author": "Robert C. Martin"},
    {"quote": "Give a man a program, frustrate him for a day. Teach a man to program, frustrate him for a lifetime.", "author": "Muhammad Waseem"},
    {"quote": "There are two ways of constructing a software design: One way is to make it so simple that there are obviously no deficiencies, and the other way is to make it so complicated that there are no obvious deficiencies.", "author": "C.A.R. Hoare"},
]


@app.get("/api/random/quote")
async def random_quote():
    """Return a random programming quote."""
    return _random.choice(PROGRAMMING_QUOTES)


class TextSummarizeRequest(BaseModel):
    text: str
    sentences: int = 3


@app.post("/api/text/summarize")
async def text_summarize(req: TextSummarizeRequest):
    """Extract key sentences from text using word frequency scoring."""
    text = req.text.strip()
    if not text:
        raise HTTPException(400, "Text is required")

    # Split into sentences
    sents = re.split(r'(?<=[.!?])\s+', text)
    if len(sents) <= req.sentences:
        return {"summary": text, "sentences": sents, "method": "extractive"}

    # Word frequency scoring
    words = re.findall(r'\b\w+\b', text.lower())
    freq = _collections.Counter(words)
    # Remove very common words
    stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                 'should', 'may', 'might', 'shall', 'can', 'to', 'of', 'in', 'for',
                 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during',
                 'and', 'but', 'or', 'nor', 'not', 'so', 'yet', 'both', 'either',
                 'that', 'this', 'these', 'those', 'it', 'its', 'he', 'she', 'they',
                 'we', 'you', 'i', 'me', 'him', 'her', 'us', 'them', 'my', 'your',
                 'his', 'their', 'our', 'which', 'who', 'whom', 'what', 'where', 'when'}
    for sw in stopwords:
        freq.pop(sw, None)

    # Score sentences
    scored = []
    for i, sent in enumerate(sents):
        sent_words = re.findall(r'\b\w+\b', sent.lower())
        score = sum(freq.get(w, 0) for w in sent_words) / max(len(sent_words), 1)
        scored.append((score, i, sent))

    scored.sort(reverse=True)
    top = sorted(scored[:req.sentences], key=lambda x: x[1])
    summary_sents = [s[2] for s in top]

    return {
        "summary": " ".join(summary_sents),
        "sentences": summary_sents,
        "total_sentences": len(sents),
        "method": "extractive_frequency",
    }


class CodeFormatRequest(BaseModel):
    code: str
    language: str = "json"


@app.post("/api/code/format")
async def code_format(req: CodeFormatRequest):
    """Format/beautify code. Supports json, sql, html."""
    code = req.code.strip()
    lang = req.language.lower()

    if lang == "json":
        try:
            parsed = json.loads(code)
            return {"formatted": json.dumps(parsed, indent=2), "language": "json"}
        except json.JSONDecodeError as e:
            raise HTTPException(400, f"Invalid JSON: {e}")

    elif lang == "sql":
        keywords = ['SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'ORDER BY', 'GROUP BY',
                     'HAVING', 'JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'INNER JOIN', 'ON',
                     'INSERT INTO', 'VALUES', 'UPDATE', 'SET', 'DELETE FROM', 'CREATE TABLE',
                     'ALTER TABLE', 'DROP TABLE', 'LIMIT', 'OFFSET', 'UNION', 'AS']
        formatted = code
        for kw in sorted(keywords, key=len, reverse=True):
            formatted = re.sub(rf'\b{kw}\b', kw, formatted, flags=re.IGNORECASE)
        for kw in ['SELECT', 'FROM', 'WHERE', 'ORDER BY', 'GROUP BY', 'HAVING',
                    'JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'INNER JOIN', 'LIMIT', 'UNION']:
            formatted = re.sub(rf'\b({kw})\b', rf'\n\1', formatted, flags=re.IGNORECASE)
        return {"formatted": formatted.strip(), "language": "sql"}

    elif lang == "html":
        indent = 0
        lines = []
        for line in code.split('\n'):
            line = line.strip()
            if not line:
                continue
            if line.startswith('</'):
                indent = max(0, indent - 1)
            lines.append('  ' * indent + line)
            if line.startswith('<') and not line.startswith('</') and not line.endswith('/>') and '/' not in line[:5]:
                indent += 1
        return {"formatted": '\n'.join(lines), "language": "html"}

    else:
        return {"formatted": code, "language": lang, "note": "No formatter available for this language"}


# Crypto price cache
_crypto_cache = {"data": None, "timestamp": 0}


@app.get("/api/crypto/prices")
async def crypto_prices():
    """Fetch current top 10 crypto prices from CoinGecko."""
    now = time.time()
    if _crypto_cache["data"] and now - _crypto_cache["timestamp"] < 60:
        return _crypto_cache["data"]

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://api.coingecko.com/api/v3/coins/markets",
                params={
                    "vs_currency": "usd",
                    "order": "market_cap_desc",
                    "per_page": 10,
                    "page": 1,
                    "sparkline": "false",
                    "price_change_percentage": "24h",
                }
            )
            resp.raise_for_status()
            coins = resp.json()

        result = {
            "coins": [
                {
                    "name": c["name"],
                    "symbol": c["symbol"].upper(),
                    "price": c["current_price"],
                    "change_24h": c.get("price_change_percentage_24h"),
                    "market_cap": c["market_cap"],
                    "volume_24h": c.get("total_volume"),
                }
                for c in coins
            ],
            "currency": "USD",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        _crypto_cache["data"] = result
        _crypto_cache["timestamp"] = now
        return result
    except Exception as e:
        if _crypto_cache["data"]:
            return {**_crypto_cache["data"], "cached": True, "error": str(e)}
        return {"error": str(e), "coins": []}


@app.post("/api/text/detect-language")
async def detect_language(req: TextSummarizeRequest):
    """Detect language of text using character and word frequency analysis."""
    text = req.text.strip()
    if not text:
        raise HTTPException(400, "Text is required")

    # Simple language detection using common words
    lang_words = {
        "en": {"the", "is", "are", "and", "or", "but", "not", "have", "has", "was", "were", "with", "this", "that", "from"},
        "es": {"el", "la", "los", "las", "de", "en", "que", "es", "por", "con", "una", "para", "como", "pero", "sobre"},
        "fr": {"le", "la", "les", "de", "des", "un", "une", "est", "et", "en", "que", "pour", "dans", "pas", "sur"},
        "de": {"der", "die", "das", "und", "ist", "ein", "eine", "nicht", "mit", "auf", "den", "dem", "von", "sich", "auch"},
        "pt": {"de", "que", "e", "do", "da", "em", "um", "para", "com", "uma", "os", "no", "se", "na", "por"},
        "it": {"il", "la", "di", "che", "e", "in", "un", "per", "non", "una", "sono", "del", "da", "con", "dei"},
        "nl": {"de", "het", "een", "van", "en", "in", "is", "dat", "op", "te", "zijn", "voor", "met", "niet", "aan"},
        "ja": set(),  # Detect by character ranges
        "zh": set(),
        "ko": set(),
        "ar": set(),
        "ru": set(),
    }

    words = set(re.findall(r'\b\w+\b', text.lower()))

    # Check for CJK/Arabic/Cyrillic characters
    cjk = len(re.findall(r'[\u4e00-\u9fff]', text))
    hiragana = len(re.findall(r'[\u3040-\u309f]', text))
    katakana = len(re.findall(r'[\u30a0-\u30ff]', text))
    hangul = len(re.findall(r'[\uac00-\ud7af]', text))
    arabic = len(re.findall(r'[\u0600-\u06ff]', text))
    cyrillic = len(re.findall(r'[\u0400-\u04ff]', text))
    total = len(text)

    if total > 0:
        if (hiragana + katakana) / total > 0.1:
            return {"language": "ja", "name": "Japanese", "confidence": 0.9}
        if cjk / total > 0.2:
            return {"language": "zh", "name": "Chinese", "confidence": 0.85}
        if hangul / total > 0.2:
            return {"language": "ko", "name": "Korean", "confidence": 0.9}
        if arabic / total > 0.2:
            return {"language": "ar", "name": "Arabic", "confidence": 0.85}
        if cyrillic / total > 0.2:
            return {"language": "ru", "name": "Russian", "confidence": 0.8}

    # Score by common words
    scores = {}
    lang_names = {"en": "English", "es": "Spanish", "fr": "French", "de": "German",
                  "pt": "Portuguese", "it": "Italian", "nl": "Dutch"}
    for lang, common in lang_words.items():
        if common:
            overlap = len(words & common)
            scores[lang] = overlap / max(len(common), 1)

    if scores:
        best = max(scores, key=scores.get)
        confidence = min(scores[best] * 2, 0.95)
        if confidence < 0.1:
            return {"language": "unknown", "name": "Unknown", "confidence": 0.0, "scores": scores}
        return {"language": best, "name": lang_names.get(best, best), "confidence": round(confidence, 2)}

    return {"language": "unknown", "name": "Unknown", "confidence": 0.0}


# --- New High-Value Endpoints (Session 3) ---

class RegexTestRequest(BaseModel):
    pattern: str
    text: str
    flags: str = ""

@app.post("/api/regex/test")
async def regex_test(req: RegexTestRequest):
    """Test a regex pattern against text. Returns all matches, groups, and positions."""
    flag_map = {"i": re.IGNORECASE, "m": re.MULTILINE, "s": re.DOTALL}
    flags = 0
    for f in req.flags:
        flags |= flag_map.get(f, 0)
    try:
        compiled = re.compile(req.pattern, flags)
        matches = []
        for m in compiled.finditer(req.text):
            matches.append({
                "match": m.group(),
                "start": m.start(),
                "end": m.end(),
                "groups": list(m.groups()),
                "named_groups": m.groupdict()
            })
        return {
            "pattern": req.pattern,
            "flags": req.flags,
            "match_count": len(matches),
            "matches": matches,
            "is_valid": True
        }
    except re.error as e:
        return {"pattern": req.pattern, "is_valid": False, "error": str(e), "matches": []}


@app.post("/api/jwt/decode")
async def jwt_decode(request: Request):
    """Decode a JWT token (without verification). Shows header, payload, and expiration."""
    body = await request.json()
    token = body.get("token", "").strip()
    if not token:
        raise HTTPException(400, "token is required")
    parts = token.split(".")
    if len(parts) != 3:
        raise HTTPException(400, "Invalid JWT format: expected 3 parts separated by dots")
    def decode_part(part):
        padding = 4 - len(part) % 4
        if padding != 4:
            part += "=" * padding
        return json.loads(base64.urlsafe_b64decode(part))
    try:
        header = decode_part(parts[0])
        payload = decode_part(parts[1])
        result = {"header": header, "payload": payload, "signature": parts[2][:20] + "..."}
        if "exp" in payload:
            exp_dt = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
            result["expires_at"] = exp_dt.isoformat()
            result["is_expired"] = datetime.now(timezone.utc) > exp_dt
        if "iat" in payload:
            result["issued_at"] = datetime.fromtimestamp(payload["iat"], tz=timezone.utc).isoformat()
        return result
    except Exception as e:
        raise HTTPException(400, f"Failed to decode JWT: {e}")


class TimestampRequest(BaseModel):
    timestamp: Optional[float] = None
    date_string: Optional[str] = None
    format: str = "%Y-%m-%d %H:%M:%S"

@app.post("/api/timestamp/convert")
async def timestamp_convert(req: TimestampRequest):
    """Convert between Unix timestamps and human-readable dates."""
    now = datetime.now(timezone.utc)
    if req.timestamp is not None:
        dt = datetime.fromtimestamp(req.timestamp, tz=timezone.utc)
        return {
            "unix_timestamp": req.timestamp,
            "utc": dt.isoformat(),
            "formatted": dt.strftime(req.format),
            "relative": f"{(now - dt).total_seconds():.0f} seconds ago" if dt < now else f"in {(dt - now).total_seconds():.0f} seconds"
        }
    elif req.date_string:
        try:
            dt = datetime.fromisoformat(req.date_string.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return {
                "unix_timestamp": dt.timestamp(),
                "utc": dt.isoformat(),
                "formatted": dt.strftime(req.format)
            }
        except ValueError as e:
            raise HTTPException(400, f"Cannot parse date: {e}")
    else:
        return {
            "unix_timestamp": now.timestamp(),
            "utc": now.isoformat(),
            "formatted": now.strftime(req.format)
        }

@app.get("/api/timestamp/now")
async def timestamp_now():
    """Get current UTC timestamp in multiple formats."""
    now = datetime.now(timezone.utc)
    return {
        "unix": now.timestamp(),
        "unix_ms": int(now.timestamp() * 1000),
        "iso8601": now.isoformat(),
        "rfc2822": now.strftime("%a, %d %b %Y %H:%M:%S +0000"),
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
    }


class DiffRequest(BaseModel):
    text1: str
    text2: str

@app.post("/api/text/diff")
async def text_diff(req: DiffRequest):
    """Compare two texts and return differences line by line."""
    import difflib
    lines1 = req.text1.splitlines(keepends=True)
    lines2 = req.text2.splitlines(keepends=True)
    diff = list(difflib.unified_diff(lines1, lines2, fromfile="text1", tofile="text2", lineterm=""))
    added = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
    removed = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))
    return {
        "diff": "\n".join(diff),
        "lines_added": added,
        "lines_removed": removed,
        "identical": len(diff) == 0
    }


class CronParseRequest(BaseModel):
    expression: str

@app.post("/api/cron/parse")
async def cron_parse(req: CronParseRequest):
    """Parse a cron expression and explain what it means in plain English."""
    parts = req.expression.strip().split()
    if len(parts) not in (5, 6):
        raise HTTPException(400, "Cron expression must have 5 or 6 fields")
    field_names = ["minute", "hour", "day_of_month", "month", "day_of_week"]
    if len(parts) == 6:
        field_names.append("year")
    fields = dict(zip(field_names, parts))

    def describe_field(val, name):
        if val == "*":
            return f"every {name}"
        if val.startswith("*/"):
            return f"every {val[2:]} {name}s"
        if "," in val:
            return f"{name} {val}"
        if "-" in val:
            a, b = val.split("-", 1)
            return f"{name} {a} through {b}"
        return f"{name} {val}"

    descriptions = [describe_field(v, n) for n, v in fields.items()]
    return {
        "expression": req.expression,
        "fields": fields,
        "description": "Runs at " + ", ".join(descriptions),
        "is_valid": True
    }


class JsonSchemaValidateRequest(BaseModel):
    data: str
    schema_def: str

@app.post("/api/json/validate-schema")
async def json_schema_validate(req: JsonSchemaValidateRequest):
    """Validate JSON data against a JSON Schema definition."""
    try:
        data = json.loads(req.data)
    except json.JSONDecodeError as e:
        raise HTTPException(400, f"Invalid JSON data: {e}")
    try:
        schema = json.loads(req.schema_def)
    except json.JSONDecodeError as e:
        raise HTTPException(400, f"Invalid JSON schema: {e}")

    errors = []
    def validate_type(val, expected, path="$"):
        type_map = {"string": str, "number": (int, float), "integer": int,
                     "boolean": bool, "array": list, "object": dict, "null": type(None)}
        if expected in type_map and not isinstance(val, type_map[expected]):
            errors.append(f"{path}: expected {expected}, got {type(val).__name__}")

    if "type" in schema:
        validate_type(data, schema["type"])
    if "required" in schema and isinstance(data, dict):
        for field in schema["required"]:
            if field not in data:
                errors.append(f"$.{field}: required field missing")
    if "properties" in schema and isinstance(data, dict):
        for prop, prop_schema in schema["properties"].items():
            if prop in data and "type" in prop_schema:
                validate_type(data[prop], prop_schema["type"], f"$.{prop}")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "error_count": len(errors)
    }


class HttpTestRequest(BaseModel):
    url: str
    method: str = "GET"
    headers: dict = {}
    body: Optional[str] = None
    timeout: float = 10.0

@app.post("/api/http/request")
async def http_request_test(req: HttpTestRequest):
    """Make an HTTP request and return the response details. Like curl via API."""
    if req.timeout > 30:
        req.timeout = 30
    allowed = urlparse(req.url)
    if allowed.hostname in ("localhost", "127.0.0.1", "0.0.0.0") or (allowed.hostname and allowed.hostname.startswith("192.168.")):
        raise HTTPException(400, "Requests to local/private IPs are not allowed")
    try:
        start = time.time()
        async with httpx.AsyncClient(follow_redirects=True, timeout=req.timeout) as client:
            response = await client.request(
                method=req.method.upper(),
                url=req.url,
                headers=req.headers,
                content=req.body if req.body else None
            )
        elapsed = time.time() - start
        body_text = response.text[:5000]
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": body_text,
            "body_length": len(response.text),
            "elapsed_ms": round(elapsed * 1000, 2),
            "url": str(response.url),
            "redirected": str(response.url) != req.url
        }
    except httpx.TimeoutException:
        return {"error": "Request timed out", "timeout": req.timeout}
    except Exception as e:
        return {"error": str(e)}


class PasswordGenRequest(BaseModel):
    length: int = 16
    count: int = 1
    uppercase: bool = True
    lowercase: bool = True
    digits: bool = True
    symbols: bool = True

@app.post("/api/password/generate")
async def generate_password(req: PasswordGenRequest):
    """Generate secure random passwords."""
    import secrets
    import string
    chars = ""
    if req.uppercase:
        chars += string.ascii_uppercase
    if req.lowercase:
        chars += string.ascii_lowercase
    if req.digits:
        chars += string.digits
    if req.symbols:
        chars += "!@#$%^&*()-_=+[]{}|;:,.<>?"
    if not chars:
        chars = string.ascii_letters + string.digits
    length = max(4, min(req.length, 128))
    count = max(1, min(req.count, 20))
    passwords = ["".join(secrets.choice(chars) for _ in range(length)) for _ in range(count)]
    return {"passwords": passwords, "length": length, "count": count}


class EncodeRequest(BaseModel):
    text: str
    action: str = "encode"

@app.post("/api/url/encode-decode")
async def url_encode_decode(req: EncodeRequest):
    """URL encode or decode text."""
    from urllib.parse import quote, unquote
    if req.action == "decode":
        return {"result": unquote(req.text), "action": "decoded"}
    return {"result": quote(req.text, safe=""), "action": "encoded"}


@app.post("/api/html/encode-decode")
async def html_encode_decode(req: EncodeRequest):
    """HTML entity encode or decode text."""
    import html as html_lib
    if req.action == "decode":
        return {"result": html_lib.unescape(req.text), "action": "decoded"}
    return {"result": html_lib.escape(req.text), "action": "encoded"}


class LoremIpsumRequest(BaseModel):
    paragraphs: int = 3
    words_per_paragraph: int = 50

@app.post("/api/lorem-ipsum")
async def lorem_ipsum(req: LoremIpsumRequest):
    """Generate Lorem Ipsum placeholder text."""
    import random
    words = "lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur excepteur sint occaecat cupidatat non proident sunt in culpa qui officia deserunt mollit anim id est laborum".split()
    count = max(1, min(req.paragraphs, 20))
    wpg = max(10, min(req.words_per_paragraph, 200))
    paragraphs = []
    for _ in range(count):
        p = " ".join(random.choice(words) for _ in range(wpg))
        p = p[0].upper() + p[1:] + "."
        paragraphs.append(p)
    return {"text": "\n\n".join(paragraphs), "paragraphs": count, "words_per_paragraph": wpg}


class SlugifyRequest(BaseModel):
    text: str
    separator: str = "-"

@app.post("/api/text/slugify")
async def slugify_text(req: SlugifyRequest):
    """Convert text to URL-friendly slug."""
    slug = re.sub(r'[^\w\s-]', '', req.text.lower())
    slug = re.sub(r'[-\s]+', req.separator, slug).strip(req.separator)
    return {"slug": slug, "original": req.text}


class MarkdownTableRequest(BaseModel):
    headers: list
    rows: list

@app.post("/api/markdown/table")
async def markdown_table(req: MarkdownTableRequest):
    """Generate a markdown table from headers and rows."""
    if not req.headers:
        raise HTTPException(400, "Headers are required")
    header_line = "| " + " | ".join(str(h) for h in req.headers) + " |"
    separator = "| " + " | ".join("---" for _ in req.headers) + " |"
    row_lines = []
    for row in req.rows:
        cells = [str(row[i]) if i < len(row) else "" for i in range(len(req.headers))]
        row_lines.append("| " + " | ".join(cells) + " |")
    table = "\n".join([header_line, separator] + row_lines)
    return {"table": table, "rows": len(req.rows), "columns": len(req.headers)}


# --- Additional Developer Utilities ---


@app.post("/api/validate/email")
async def validate_email(request: Request):
    """Validate email address format and check domain MX records."""
    data = await request.json()
    email = data.get("email", "").strip()
    if not email:
        raise HTTPException(400, "Email is required")
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    is_valid = bool(re.match(pattern, email))
    result = {"email": email, "valid_format": is_valid}
    if is_valid:
        domain = email.split("@")[1]
        import dns.resolver
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            result["has_mx"] = True
            result["mx_records"] = [str(r.exchange).rstrip('.') for r in mx_records]
        except Exception:
            result["has_mx"] = False
            result["mx_records"] = []
        disposable_domains = {"tempmail.com", "throwaway.email", "guerrillamail.com", "mailinator.com", "10minutemail.com", "yopmail.com", "dispostable.com", "trashmail.com"}
        result["disposable"] = domain.lower() in disposable_domains
    return result


@app.post("/api/validate/ip")
async def validate_ip(request: Request):
    """Validate and classify an IP address (IPv4/IPv6, private/public, etc.)."""
    data = await request.json()
    ip_str = data.get("ip", "").strip()
    if not ip_str:
        raise HTTPException(400, "IP address is required")
    import ipaddress
    try:
        ip = ipaddress.ip_address(ip_str)
        return {
            "ip": ip_str,
            "valid": True,
            "version": ip.version,
            "is_private": ip.is_private,
            "is_loopback": ip.is_loopback,
            "is_multicast": ip.is_multicast,
            "is_reserved": ip.is_reserved,
            "is_link_local": ip.is_link_local,
            "is_global": ip.is_global,
            "compressed": str(ip),
        }
    except ValueError:
        try:
            net = ipaddress.ip_network(ip_str, strict=False)
            return {
                "input": ip_str,
                "valid": True,
                "is_network": True,
                "version": net.version,
                "network_address": str(net.network_address),
                "broadcast_address": str(net.broadcast_address),
                "num_addresses": net.num_addresses,
                "prefixlen": net.prefixlen,
            }
        except ValueError:
            return {"ip": ip_str, "valid": False}


@app.get("/api/useragent/parse")
async def parse_useragent(ua: str = "", request: Request = None):
    """Parse a User-Agent string to extract browser, OS, and device info."""
    if not ua and request:
        ua = request.headers.get("user-agent", "")
    if not ua:
        raise HTTPException(400, "User-Agent string required (pass as 'ua' query param)")
    result = {"raw": ua}
    ua_lower = ua.lower()
    # Browser detection
    browsers = [
        ("Edg/", "Microsoft Edge"), ("OPR/", "Opera"), ("Vivaldi/", "Vivaldi"),
        ("Chrome/", "Chrome"), ("Firefox/", "Firefox"), ("Safari/", "Safari"),
        ("MSIE", "Internet Explorer"), ("Trident/", "Internet Explorer"),
    ]
    result["browser"] = "Unknown"
    for sig, name in browsers:
        if sig.lower() in ua_lower:
            result["browser"] = name
            break
    # OS detection
    os_sigs = [
        ("Windows NT 10", "Windows 10/11"), ("Windows NT 6.3", "Windows 8.1"),
        ("Windows NT 6.1", "Windows 7"), ("Mac OS X", "macOS"),
        ("Android", "Android"), ("iPhone", "iOS"), ("iPad", "iPadOS"),
        ("Linux", "Linux"), ("CrOS", "ChromeOS"),
    ]
    result["os"] = "Unknown"
    for sig, name in os_sigs:
        if sig.lower() in ua_lower:
            result["os"] = name
            break
    result["is_mobile"] = any(m in ua_lower for m in ["mobile", "android", "iphone", "ipad"])
    result["is_bot"] = any(b in ua_lower for b in ["bot", "crawl", "spider", "scraper", "curl", "wget", "python-requests"])
    return result


@app.post("/api/diff/json")
async def json_diff(request: Request):
    """Compare two JSON objects and return the differences."""
    data = await request.json()
    json1_str = data.get("json1", "")
    json2_str = data.get("json2", "")
    if not json1_str or not json2_str:
        raise HTTPException(400, "Both json1 and json2 are required")
    try:
        obj1 = json.loads(json1_str) if isinstance(json1_str, str) else json1_str
        obj2 = json.loads(json2_str) if isinstance(json2_str, str) else json2_str
    except json.JSONDecodeError as e:
        raise HTTPException(400, f"Invalid JSON: {e}")

    def diff_objects(a, b, path=""):
        changes = []
        if isinstance(a, dict) and isinstance(b, dict):
            for key in set(list(a.keys()) + list(b.keys())):
                p = f"{path}.{key}" if path else key
                if key not in a:
                    changes.append({"path": p, "type": "added", "value": b[key]})
                elif key not in b:
                    changes.append({"path": p, "type": "removed", "value": a[key]})
                else:
                    changes.extend(diff_objects(a[key], b[key], p))
        elif isinstance(a, list) and isinstance(b, list):
            for i in range(max(len(a), len(b))):
                p = f"{path}[{i}]"
                if i >= len(a):
                    changes.append({"path": p, "type": "added", "value": b[i]})
                elif i >= len(b):
                    changes.append({"path": p, "type": "removed", "value": a[i]})
                else:
                    changes.extend(diff_objects(a[i], b[i], p))
        elif a != b:
            changes.append({"path": path or "(root)", "type": "changed", "old": a, "new": b})
        return changes

    changes = diff_objects(obj1, obj2)
    return {"total_changes": len(changes), "identical": len(changes) == 0, "changes": changes}


@app.post("/api/convert/csv-to-json")
async def csv_to_json(request: Request):
    """Convert CSV text to JSON array."""
    data = await request.json()
    csv_text = data.get("csv", "")
    if not csv_text:
        raise HTTPException(400, "CSV text is required")
    import csv as csv_module
    import io as io_module
    reader = csv_module.DictReader(io_module.StringIO(csv_text))
    rows = [row for row in reader]
    return {"rows": len(rows), "columns": list(rows[0].keys()) if rows else [], "data": rows}


@app.post("/api/convert/yaml-to-json")
async def yaml_to_json(request: Request):
    """Convert YAML text to JSON."""
    data = await request.json()
    yaml_text = data.get("yaml", "")
    if not yaml_text:
        raise HTTPException(400, "YAML text is required")
    try:
        import yaml
        parsed = yaml.safe_load(yaml_text)
        return {"json": json.dumps(parsed, indent=2), "valid": True}
    except Exception as e:
        return {"valid": False, "error": str(e)}


@app.post("/api/text/count")
async def text_count(request: Request):
    """Count specific patterns in text (words, characters, lines, sentences, paragraphs)."""
    data = await request.json()
    text = data.get("text", "")
    if not text:
        raise HTTPException(400, "Text is required")
    words = text.split()
    lines = text.split("\n")
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return {
        "characters": len(text),
        "characters_no_spaces": len(text.replace(" ", "").replace("\n", "")),
        "words": len(words),
        "unique_words": len(set(w.lower() for w in words)),
        "lines": len(lines),
        "sentences": len(sentences),
        "paragraphs": len(paragraphs),
        "avg_word_length": round(sum(len(w) for w in words) / max(len(words), 1), 1),
        "reading_time_minutes": round(len(words) / 238, 1),
        "speaking_time_minutes": round(len(words) / 150, 1),
    }


@app.post("/api/number/convert")
async def number_convert(request: Request):
    """Convert numbers between decimal, binary, octal, hex, and roman numerals."""
    data = await request.json()
    value = data.get("value", "")
    from_base = data.get("from", "decimal")
    if not value:
        raise HTTPException(400, "Value is required")
    try:
        if from_base == "binary":
            num = int(str(value), 2)
        elif from_base == "octal":
            num = int(str(value), 8)
        elif from_base == "hex":
            num = int(str(value), 16)
        elif from_base == "roman":
            roman_vals = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
            num = 0
            s = str(value).upper()
            for i, c in enumerate(s):
                if i + 1 < len(s) and roman_vals.get(c, 0) < roman_vals.get(s[i + 1], 0):
                    num -= roman_vals.get(c, 0)
                else:
                    num += roman_vals.get(c, 0)
        else:
            num = int(float(str(value)))

        # To roman
        roman = ""
        if 0 < num < 4000:
            vals = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
                    (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
            n = num
            for v, s in vals:
                while n >= v:
                    roman += s
                    n -= v

        return {
            "decimal": num,
            "binary": bin(num),
            "octal": oct(num),
            "hex": hex(num),
            "roman": roman or "N/A (out of range 1-3999)",
        }
    except (ValueError, TypeError) as e:
        raise HTTPException(400, f"Invalid number: {e}")


# --- Analytics Endpoints ---

class TrackRequest(BaseModel):
    path: str
    ref: str = ""

@app.post("/analytics/track")
async def track_pageview(req: TrackRequest, request: Request):
    ip = request.client.host if request.client else "unknown"
    ua = request.headers.get("user-agent", "")
    record_pageview(req.path, ip, ua, req.ref)
    return {"ok": True}


@app.get("/analytics/dashboard", response_class=HTMLResponse)
async def analytics_dashboard(request: Request):
    # Simple admin check (only accessible from localhost or with secret)
    secret = request.query_params.get("key", "")
    if secret != "tp-admin-2026" and request.client and request.client.host not in ("127.0.0.1", "::1"):
        raise HTTPException(status_code=403, detail="Forbidden")

    conn = sqlite3.connect(str(ANALYTICS_DB))
    # Today's stats
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    rows = conn.execute(
        "SELECT path, views FROM daily_stats WHERE date = ? ORDER BY views DESC LIMIT 20", (today,)
    ).fetchall()
    # Total all-time
    total = conn.execute("SELECT COUNT(*) FROM pageviews").fetchone()[0]
    unique = conn.execute("SELECT COUNT(DISTINCT ip) FROM pageviews").fetchone()[0]
    # Last 7 days
    daily = conn.execute(
        "SELECT date, SUM(views) FROM daily_stats GROUP BY date ORDER BY date DESC LIMIT 7"
    ).fetchall()
    conn.close()

    page_rows = "".join(f"<tr><td>{r[0]}</td><td>{r[1]}</td></tr>" for r in rows)
    daily_rows = "".join(f"<tr><td>{d[0]}</td><td>{d[1]}</td></tr>" for d in daily)

    return HTMLResponse(f"""<!DOCTYPE html>
<html><head><title>ToolPipe Analytics</title>
<style>body{{font-family:system-ui;max-width:800px;margin:40px auto;padding:0 20px}}
table{{width:100%;border-collapse:collapse}}th,td{{border:1px solid #ddd;padding:8px;text-align:left}}
th{{background:#f5f5f5}}h1{{color:#302b63}}.stat{{display:inline-block;background:#f0f0ff;padding:16px 24px;border-radius:8px;margin:8px}}</style>
</head><body>
<h1>ToolPipe Analytics Dashboard</h1>
<div><div class="stat"><strong>Total Views:</strong> {total}</div>
<div class="stat"><strong>Unique Visitors:</strong> {unique}</div></div>
<h2>Today ({today})</h2>
<table><tr><th>Page</th><th>Views</th></tr>{page_rows or '<tr><td colspan="2">No data yet</td></tr>'}</table>
<h2>Last 7 Days</h2>
<table><tr><th>Date</th><th>Views</th></tr>{daily_rows or '<tr><td colspan="2">No data yet</td></tr>'}</table>
</body></html>""")


# --- Crypto Payment Endpoints ---

PRICING_TIERS = {
    "pro": {"amount": 9.99, "daily_limit": 10000, "name": "Pro"},
    "enterprise": {"amount": 49.99, "daily_limit": 100000, "name": "Enterprise"},
}


class PaymentRequest(BaseModel):
    email: str
    tier: str = "pro"


@app.post("/payments/create")
async def create_payment(req: PaymentRequest, request: Request):
    email = req.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Valid email required")
    tier = req.tier.lower()
    if tier not in PRICING_TIERS:
        raise HTTPException(status_code=400, detail=f"Invalid tier. Options: {', '.join(PRICING_TIERS.keys())}")

    tier_info = PRICING_TIERS[tier]
    order_id = f"tp-{tier}-{uuid.uuid4().hex[:12]}"

    # Build callback/return URLs from request
    base_url = str(request.base_url).rstrip("/")
    callback_url = f"{base_url}/payments/webhook"
    return_url = f"{base_url}/payments/success?order_id={order_id}"

    result = await create_payment_invoice(
        amount=tier_info["amount"],
        email=email,
        tier=tier,
        order_id=order_id,
        callback_url=callback_url,
        return_url=return_url,
    )
    return result


@app.post("/payments/webhook")
async def payment_webhook(request: Request):
    """Handles webhooks from OxaPay, NOWPayments, or generic payment callbacks."""
    try:
        data = await request.json()
    except Exception:
        body = await request.body()
        try:
            data = json.loads(body)
        except Exception:
            return {"status": "error", "message": "Invalid payload"}

    # OxaPay v1 format
    track_id = data.get("trackId", data.get("track_id", ""))
    status = data.get("status", "")
    order_id = data.get("orderId", data.get("order_id", ""))

    # NOWPayments format
    if not order_id and data.get("payment_id"):
        order_id = data.get("order_id", "")
        track_id = str(data.get("payment_id", ""))
    if not status and data.get("payment_status"):
        np_status = data["payment_status"]
        if np_status in ("finished", "confirmed", "partially_paid"):
            status = "paid"

    paid_statuses = ("Paid", "Confirming", "Complete", "paid", "complete", "finished", "confirmed")
    if status.lower() in [s.lower() for s in paid_statuses]:
        now = datetime.now(timezone.utc).isoformat()
        with _payments_lock:
            conn = sqlite3.connect(str(PAYMENTS_DB))
            row = conn.execute(
                "SELECT email, tier FROM payments WHERE track_id = ? OR order_id = ?",
                (track_id, order_id)
            ).fetchone()
            if row:
                email, tier = row
                conn.execute(
                    "UPDATE payments SET status = ?, paid_at = ?, callback_data = ? WHERE track_id = ? OR order_id = ?",
                    (status, now, json.dumps(data), track_id, order_id)
                )
                conn.commit()
                upgrade_api_key(email, tier)
            conn.close()

    return {"status": "ok"}


@app.get("/payments/success", response_class=HTMLResponse)
async def payment_success(order_id: str = ""):
    return HTMLResponse(inject_snippet(f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Payment Successful - ToolPipe</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,sans-serif;background:#0a0a0a;color:#e0e0e0;display:flex;align-items:center;justify-content:center;min-height:100vh}}
.card{{background:#1a1a1a;border:2px solid #22c55e;border-radius:16px;padding:48px;text-align:center;max-width:500px}}
h1{{color:#22c55e;font-size:2rem;margin-bottom:12px}}
p{{color:#94a3b8;line-height:1.6;margin-bottom:16px}}
.order{{font-family:monospace;color:#6c63ff;background:#111;padding:8px 16px;border-radius:8px;display:inline-block;margin:8px 0}}
a{{color:#6c63ff;text-decoration:none}}
.btn{{display:inline-block;background:#6c63ff;color:#fff;padding:12px 32px;border-radius:8px;font-weight:600;margin-top:16px}}
</style></head><body>
<div class="card">
<h1>Payment Received!</h1>
<p>Your Pro access is being activated. You will receive your upgraded API key shortly.</p>
<div class="order">{order_id}</div>
<p>Check your API key status on the <a href="/api-keys">dashboard</a>.</p>
<a href="/api-keys" class="btn">View API Dashboard</a>
</div>
</body></html>"""))


ADMIN_KEY = os.environ.get("TOOLPIPE_ADMIN_KEY", "tp-admin-2026")

# Public RPC endpoints for on-chain verification (no API key needed)
CHAIN_RPC = {
    "ethereum": "https://eth.llamarpc.com",
    "polygon": "https://polygon-rpc.com",
    "arbitrum": "https://arb1.arbitrum.io/rpc",
    "base": "https://mainnet.base.org",
    "optimism": "https://mainnet.optimism.io",
    "bsc": "https://bsc-dataseed.binance.org",
    "avalanche": "https://api.avax.network/ext/bc/C/rpc",
}

# Stablecoin contract addresses (for ERC-20 transfer verification)
STABLECOIN_CONTRACTS = {
    "ethereum": {
        "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
    },
    "polygon": {
        "USDC": "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359",
        "USDT": "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
    },
    "base": {
        "USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    },
    "arbitrum": {
        "USDC": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
        "USDT": "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",
    },
    "bsc": {
        "USDC": "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",
        "USDT": "0x55d398326f99059fF775485246999027B3197955",
        "BUSD": "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56",
    },
    "avalanche": {
        "USDC": "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E",
        "USDT": "0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7",
    },
}


# ETH price oracle with 5-minute cache
_eth_price_cache = {"price": None, "timestamp": 0}


async def get_eth_price_usd() -> float:
    """Fetch current ETH price in USD from CoinGecko. Cached for 5 minutes."""
    now = time.time()
    if _eth_price_cache["price"] is not None and (now - _eth_price_cache["timestamp"]) < 300:
        return _eth_price_cache["price"]

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={"ids": "ethereum", "vs_currencies": "usd"},
            )
            data = resp.json()
            price = float(data["ethereum"]["usd"])
            _eth_price_cache["price"] = price
            _eth_price_cache["timestamp"] = now
            return price
    except Exception:
        # Fallback: try backup API
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get("https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD")
                data = resp.json()
                price = float(data["USD"])
                _eth_price_cache["price"] = price
                _eth_price_cache["timestamp"] = now
                return price
        except Exception:
            pass
    # Return cached value even if stale, or 0 if never fetched
    return _eth_price_cache["price"] or 0.0


async def verify_tx_onchain(tx_hash: str) -> dict:
    """Verify a transaction on-chain across multiple networks. Returns tx details if found."""
    our_wallet = WALLET_ADDRESS.lower()

    for chain_name, rpc_url in CHAIN_RPC.items():
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # Get transaction receipt
                resp = await client.post(rpc_url, json={
                    "jsonrpc": "2.0", "id": 1, "method": "eth_getTransactionByHash",
                    "params": [tx_hash]
                })
                data = resp.json()
                tx = data.get("result")
                if not tx:
                    continue

                to_addr = (tx.get("to") or "").lower()
                value_wei = int(tx.get("value", "0x0"), 16)
                value_eth = value_wei / 1e18

                # Check if it's a direct ETH transfer to our wallet
                if to_addr == our_wallet and value_wei > 0:
                    # Get receipt to confirm success
                    receipt_resp = await client.post(rpc_url, json={
                        "jsonrpc": "2.0", "id": 2, "method": "eth_getTransactionReceipt",
                        "params": [tx_hash]
                    })
                    receipt = receipt_resp.json().get("result", {})
                    status = receipt.get("status", "0x0")

                    return {
                        "verified": status == "0x1",
                        "chain": chain_name,
                        "type": "native_transfer",
                        "from": tx.get("from", ""),
                        "to": to_addr,
                        "value_native": value_eth,
                        "tx_hash": tx_hash,
                        "block": int(tx.get("blockNumber", "0x0"), 16) if tx.get("blockNumber") else 0,
                    }

                # Check for ERC-20 token transfers (Transfer event to our wallet)
                chain_contracts = {addr.lower(): name for name, addr in STABLECOIN_CONTRACTS.get(chain_name, {}).items()}
                if to_addr in chain_contracts:
                    receipt_resp = await client.post(rpc_url, json={
                        "jsonrpc": "2.0", "id": 2, "method": "eth_getTransactionReceipt",
                        "params": [tx_hash]
                    })
                    receipt = receipt_resp.json().get("result", {})
                    # Check Transfer logs for our wallet
                    for log in receipt.get("logs", []):
                        topics = log.get("topics", [])
                        # Transfer(address,address,uint256) topic
                        if len(topics) >= 3 and topics[0] == "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef":
                            recipient = "0x" + topics[2][-40:]
                            if recipient.lower() == our_wallet:
                                raw_amount = int(log.get("data", "0x0"), 16)
                                # USDC/USDT use 6 decimals, DAI uses 18
                                token_name = chain_contracts.get(to_addr, "unknown")
                                decimals = 6 if token_name in ("USDC", "USDT", "BUSD") else 18
                                amount = raw_amount / (10 ** decimals)
                                return {
                                    "verified": receipt.get("status") == "0x1",
                                    "chain": chain_name,
                                    "type": "token_transfer",
                                    "token": token_name,
                                    "from": tx.get("from", ""),
                                    "to": our_wallet,
                                    "amount": amount,
                                    "tx_hash": tx_hash,
                                    "block": int(tx.get("blockNumber", "0x0"), 16) if tx.get("blockNumber") else 0,
                                }
        except Exception:
            continue

    # Solana verification
    if not tx_hash.startswith("0x"):
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(SOLANA_RPC, json={
                    "jsonrpc": "2.0", "id": 1, "method": "getTransaction",
                    "params": [tx_hash, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}]
                })
                data = resp.json()
                tx_data = data.get("result")
                if tx_data and tx_data.get("meta") and tx_data["meta"].get("err") is None:
                    sol_wallet = SOLANA_WALLET.lower()
                    # Check native SOL transfers
                    pre_balances = tx_data["meta"].get("preBalances", [])
                    post_balances = tx_data["meta"].get("postBalances", [])
                    account_keys = []
                    msg = tx_data.get("transaction", {}).get("message", {})
                    for ak in msg.get("accountKeys", []):
                        if isinstance(ak, dict):
                            account_keys.append(ak.get("pubkey", ""))
                        else:
                            account_keys.append(str(ak))

                    # Check for SOL transfer to our wallet
                    for i, key in enumerate(account_keys):
                        if key.lower() == sol_wallet and i < len(pre_balances) and i < len(post_balances):
                            received_lamports = post_balances[i] - pre_balances[i]
                            if received_lamports > 0:
                                sol_amount = received_lamports / 1e9
                                return {
                                    "verified": True,
                                    "chain": "solana",
                                    "type": "native_transfer",
                                    "token": "SOL",
                                    "to": SOLANA_WALLET,
                                    "value_native": sol_amount,
                                    "tx_hash": tx_hash,
                                    "block": tx_data.get("slot", 0),
                                }

                    # Check SPL token transfers (USDC on Solana)
                    inner_instructions = tx_data["meta"].get("innerInstructions", [])
                    parsed_instructions = msg.get("instructions", [])
                    all_instructions = parsed_instructions
                    for inner in inner_instructions:
                        all_instructions.extend(inner.get("instructions", []))

                    for ix in all_instructions:
                        parsed = ix.get("parsed")
                        if not parsed:
                            continue
                        if parsed.get("type") == "transferChecked" or parsed.get("type") == "transfer":
                            info = parsed.get("info", {})
                            dest = info.get("destination", "")
                            # For SPL, destination is a token account, not the wallet directly
                            # Check tokenAmount for USDC (6 decimals)
                            token_amount = info.get("tokenAmount", {})
                            if token_amount:
                                ui_amount = float(token_amount.get("uiAmount", 0))
                                if ui_amount > 0:
                                    return {
                                        "verified": True,
                                        "chain": "solana",
                                        "type": "token_transfer",
                                        "token": "USDC-SPL",
                                        "amount": ui_amount,
                                        "to": SOLANA_WALLET,
                                        "tx_hash": tx_hash,
                                        "block": tx_data.get("slot", 0),
                                    }
                            # Simple transfer (lamport amount)
                            amount_val = info.get("amount") or info.get("lamports")
                            if amount_val:
                                amount_val = int(amount_val)
                                if amount_val > 0:
                                    return {
                                        "verified": True,
                                        "chain": "solana",
                                        "type": "token_transfer",
                                        "token": "SPL",
                                        "amount": amount_val / 1e6,  # Assume 6 decimals for USDC
                                        "to": SOLANA_WALLET,
                                        "tx_hash": tx_hash,
                                        "block": tx_data.get("slot", 0),
                                    }
        except Exception:
            pass

    return {"verified": False, "error": "Transaction not found on any supported chain"}


# SOL price oracle with 5-minute cache
_sol_price_cache = {"price": None, "timestamp": 0}


async def get_sol_price_usd() -> float:
    """Fetch current SOL price in USD from CoinGecko. Cached for 5 minutes."""
    now = time.time()
    if _sol_price_cache["price"] is not None and (now - _sol_price_cache["timestamp"]) < 300:
        return _sol_price_cache["price"]
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={"ids": "solana", "vs_currencies": "usd"},
            )
            data = resp.json()
            price = float(data["solana"]["usd"])
            _sol_price_cache["price"] = price
            _sol_price_cache["timestamp"] = now
            return price
    except Exception:
        pass
    return _sol_price_cache["price"] or 0.0


class VerifyPaymentRequest(BaseModel):
    order_id: str
    tx_hash: str = ""
    admin_key: str = ""


class SelfVerifyRequest(BaseModel):
    order_id: str
    tx_hash: str


@app.post("/payments/verify-tx")
async def self_verify_payment(req: SelfVerifyRequest):
    """Self-service payment verification. Submit your tx hash and we verify on-chain."""
    if not req.tx_hash or len(req.tx_hash) < 32:
        raise HTTPException(status_code=400, detail="Invalid transaction hash.")
    # EVM hashes: 0x + 64 hex chars. Solana hashes: 43-88 base58 chars.
    is_evm_hash = req.tx_hash.startswith("0x") and len(req.tx_hash) == 66
    is_solana_hash = not req.tx_hash.startswith("0x") and 43 <= len(req.tx_hash) <= 88
    if not is_evm_hash and not is_solana_hash:
        raise HTTPException(status_code=400, detail="Invalid transaction hash. EVM: 0x + 64 hex chars. Solana: 43-88 base58 chars.")

    # Check order exists and is pending
    with _payments_lock:
        conn = sqlite3.connect(str(PAYMENTS_DB))
        row = conn.execute(
            "SELECT email, tier, amount, status FROM payments WHERE order_id = ?", (req.order_id,)
        ).fetchone()
        conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Order not found")
    if row[3] == "paid":
        return {"status": "already_paid", "order_id": req.order_id, "message": "This order is already verified and active."}

    email, tier, amount, _ = row

    # Verify on-chain
    chain_result = await verify_tx_onchain(req.tx_hash)

    if not chain_result.get("verified"):
        return {
            "status": "unverified",
            "order_id": req.order_id,
            "message": "Transaction not found or not confirmed yet. Try again in a few minutes, or check the tx hash.",
            "chain_result": chain_result,
        }

    # Check amount (allow 10% underpayment tolerance for price fluctuations)
    is_stablecoin = chain_result.get("type") == "token_transfer"
    is_native = chain_result.get("type") == "native_transfer"

    if is_stablecoin:
        tx_value_usd = chain_result.get("amount", 0)
    elif is_native:
        native_amount = chain_result.get("value_native", 0)
        chain_name = chain_result.get("chain", "")
        if chain_name == "solana":
            native_price = await get_sol_price_usd()
            chain_result["sol_price_usd"] = native_price
        else:
            native_price = await get_eth_price_usd()
            chain_result["eth_price_usd"] = native_price
        tx_value_usd = native_amount * native_price if native_price > 0 else 0
        chain_result["value_usd"] = round(tx_value_usd, 2)
    else:
        tx_value_usd = 0

    if tx_value_usd < amount * 0.9:
        underpaid_resp = {
            "status": "underpaid",
            "order_id": req.order_id,
            "expected_usd": amount,
            "received_usd": round(tx_value_usd, 2),
            "message": f"Payment amount ${tx_value_usd:.2f} is below the required ${amount:.2f}. Please send the remaining amount.",
        }
        if is_native:
            underpaid_resp["native_price_used"] = chain_result.get("eth_price_usd") or chain_result.get("sol_price_usd", 0)
            underpaid_resp["native_received"] = chain_result.get("value_native", 0)
        return underpaid_resp

    # Payment verified, upgrade the user
    now = datetime.now(timezone.utc).isoformat()
    with _payments_lock:
        conn = sqlite3.connect(str(PAYMENTS_DB))
        conn.execute(
            "UPDATE payments SET status = 'paid', paid_at = ?, callback_data = ? WHERE order_id = ?",
            (now, json.dumps({"tx_hash": req.tx_hash, "chain_verification": chain_result, "auto_verified": True}), req.order_id)
        )
        conn.commit()
        conn.close()

    result = upgrade_api_key(email, tier)
    return {
        "status": "verified",
        "order_id": req.order_id,
        "email": email,
        "tier": tier,
        "api_key": result.get("api_key"),
        "chain": chain_result.get("chain"),
        "tx_hash": req.tx_hash,
        "message": f"Payment verified on {chain_result.get('chain', 'blockchain')}! Your API key has been upgraded to {tier}.",
    }


@app.post("/payments/verify")
async def verify_payment(req: VerifyPaymentRequest):
    """Admin endpoint to manually verify a direct crypto payment and upgrade the user."""
    if req.admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin key")
    now = datetime.now(timezone.utc).isoformat()
    with _payments_lock:
        conn = sqlite3.connect(str(PAYMENTS_DB))
        row = conn.execute(
            "SELECT email, tier FROM payments WHERE order_id = ?", (req.order_id,)
        ).fetchone()
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail="Order not found")
        email, tier = row
        conn.execute(
            "UPDATE payments SET status = 'paid', paid_at = ?, callback_data = ? WHERE order_id = ?",
            (now, json.dumps({"tx_hash": req.tx_hash, "verified_manually": True}), req.order_id)
        )
        conn.commit()
        conn.close()
    result = upgrade_api_key(email, tier)
    return {"verified": True, "order_id": req.order_id, "email": email, "tier": tier, "api_key": result.get("api_key")}


@app.get("/payments/pending")
async def list_pending_payments(key: str = ""):
    """Admin endpoint to list all pending payments awaiting verification."""
    if key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin key")
    with _payments_lock:
        conn = sqlite3.connect(str(PAYMENTS_DB))
        rows = conn.execute(
            "SELECT order_id, email, tier, amount, status, created_at FROM payments WHERE status IN ('pending', 'awaiting_direct') ORDER BY created_at DESC"
        ).fetchall()
        conn.close()
    return [{"order_id": r[0], "email": r[1], "tier": r[2], "amount": r[3], "status": r[4], "created_at": r[5]} for r in rows]


@app.get("/payments/status")
async def payment_status(order_id: str = "", track_id: str = ""):
    with _payments_lock:
        conn = sqlite3.connect(str(PAYMENTS_DB))
        if order_id:
            row = conn.execute(
                "SELECT order_id, email, tier, amount, status, created_at, paid_at FROM payments WHERE order_id = ?",
                (order_id,)
            ).fetchone()
        elif track_id:
            row = conn.execute(
                "SELECT order_id, email, tier, amount, status, created_at, paid_at FROM payments WHERE track_id = ?",
                (track_id,)
            ).fetchone()
        else:
            conn.close()
            raise HTTPException(status_code=400, detail="Provide order_id or track_id")
        conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {
        "order_id": row[0], "email": row[1], "tier": row[2],
        "amount": row[3], "status": row[4], "created_at": row[5], "paid_at": row[6]
    }


# --- Credit-based Pay-Per-Call System ---
# Agents can buy credits (1 credit = 1 API call to premium endpoints)
# Credit packs: 1000 credits for $4.99, 10000 for $29.99, 100000 for $199.99

CREDIT_PACKS = {
    "starter": {"credits": 1000, "amount": 4.99, "name": "Starter (1K credits)"},
    "growth": {"credits": 10000, "amount": 29.99, "name": "Growth (10K credits)"},
    "scale": {"credits": 100000, "amount": 199.99, "name": "Scale (100K credits)"},
}

def _init_credits_db():
    conn = sqlite3.connect(str(PAYMENTS_DB))
    conn.execute("""CREATE TABLE IF NOT EXISTS credits (
        api_key TEXT PRIMARY KEY,
        email TEXT NOT NULL,
        balance INTEGER DEFAULT 0,
        total_purchased INTEGER DEFAULT 0,
        total_used INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS credit_purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        api_key TEXT NOT NULL,
        pack TEXT NOT NULL,
        credits INTEGER NOT NULL,
        amount REAL NOT NULL,
        order_id TEXT UNIQUE,
        tx_hash TEXT,
        status TEXT DEFAULT 'pending',
        created_at TEXT NOT NULL,
        verified_at TEXT
    )""")
    conn.commit()
    conn.close()

_init_credits_db()


class CreditPurchaseRequest(BaseModel):
    api_key: str
    pack: str = "starter"
    email: str = ""


@app.get("/api/credits/packs")
async def list_credit_packs():
    """List available credit packs for pay-per-call usage."""
    return {
        "packs": CREDIT_PACKS,
        "how_it_works": "1 credit = 1 premium API call. Buy credits, then use your API key. Credits never expire.",
        "payment": {
            "crypto_wallets": {
                "ETH/ERC-20": WALLET_ADDRESS,
                "Solana": SOLANA_WALLET,
            },
            "flow": "POST /api/credits/buy -> send crypto -> POST /api/credits/verify with tx_hash",
        },
    }


@app.post("/api/credits/buy")
async def buy_credits(req: CreditPurchaseRequest, request: Request):
    """Purchase API credits. Returns payment instructions."""
    if req.pack not in CREDIT_PACKS:
        raise HTTPException(status_code=400, detail=f"Invalid pack. Options: {', '.join(CREDIT_PACKS.keys())}")

    pack = CREDIT_PACKS[req.pack]
    order_id = f"cr-{req.pack}-{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()
    email = req.email.strip().lower() if req.email else "agent@toolpipe.dev"

    with _payments_lock:
        conn = sqlite3.connect(str(PAYMENTS_DB))
        conn.execute(
            "INSERT INTO credit_purchases (api_key, pack, credits, amount, order_id, status, created_at) VALUES (?, ?, ?, ?, ?, 'pending', ?)",
            (req.api_key, req.pack, pack["credits"], pack["amount"], order_id, now)
        )
        # Ensure credit account exists
        existing = conn.execute("SELECT api_key FROM credits WHERE api_key = ?", (req.api_key,)).fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO credits (api_key, email, balance, total_purchased, total_used, created_at, updated_at) VALUES (?, ?, 0, 0, 0, ?, ?)",
                (req.api_key, email, now, now)
            )
        conn.commit()
        conn.close()

    return {
        "order_id": order_id,
        "pack": req.pack,
        "credits": pack["credits"],
        "amount_usd": pack["amount"],
        "payment_instructions": {
            "send_to": {
                "ETH/USDC/USDT (any EVM chain)": WALLET_ADDRESS,
                "SOL/USDC-SPL (Solana)": SOLANA_WALLET,
            },
            "amount": f"${pack['amount']}",
            "then": f"POST /api/credits/verify with order_id={order_id} and your tx_hash",
        },
    }


class CreditVerifyRequest(BaseModel):
    order_id: str
    tx_hash: str


@app.post("/api/credits/verify")
async def verify_credit_purchase(req: CreditVerifyRequest):
    """Verify crypto payment and add credits to your account."""
    with _payments_lock:
        conn = sqlite3.connect(str(PAYMENTS_DB))
        row = conn.execute(
            "SELECT api_key, pack, credits, amount, status FROM credit_purchases WHERE order_id = ?",
            (req.order_id,)
        ).fetchone()
        conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Order not found")
    if row[4] == "verified":
        return {"status": "already_verified", "order_id": req.order_id}

    api_key, pack, credits, amount, _ = row

    chain_result = await verify_tx_onchain(req.tx_hash)
    if not chain_result.get("verified"):
        return {"status": "unverified", "message": "Transaction not found or pending. Try again in a few minutes.", "chain_result": chain_result}

    # Verify amount
    is_stablecoin = chain_result.get("type") == "token_transfer"
    is_native = chain_result.get("type") == "native_transfer"
    if is_stablecoin:
        tx_value_usd = chain_result.get("amount", 0)
    elif is_native:
        native_amount = chain_result.get("value_native", 0)
        if chain_result.get("chain") == "solana":
            native_price = await get_sol_price_usd()
        else:
            native_price = await get_eth_price_usd()
        tx_value_usd = native_amount * native_price if native_price > 0 else 0
    else:
        tx_value_usd = 0

    if tx_value_usd < amount * 0.9:
        return {"status": "underpaid", "expected_usd": amount, "received_usd": round(tx_value_usd, 2)}

    now = datetime.now(timezone.utc).isoformat()
    with _payments_lock:
        conn = sqlite3.connect(str(PAYMENTS_DB))
        conn.execute(
            "UPDATE credit_purchases SET status = 'verified', tx_hash = ?, verified_at = ? WHERE order_id = ?",
            (req.tx_hash, now, req.order_id)
        )
        conn.execute(
            "UPDATE credits SET balance = balance + ?, total_purchased = total_purchased + ?, updated_at = ? WHERE api_key = ?",
            (credits, credits, now, api_key)
        )
        conn.commit()
        new_balance = conn.execute("SELECT balance FROM credits WHERE api_key = ?", (api_key,)).fetchone()
        conn.close()

    return {
        "status": "verified",
        "credits_added": credits,
        "new_balance": new_balance[0] if new_balance else credits,
        "order_id": req.order_id,
        "chain": chain_result.get("chain"),
    }


@app.get("/api/credits/balance")
async def credit_balance(api_key: str = ""):
    """Check your credit balance."""
    if not api_key:
        raise HTTPException(status_code=400, detail="api_key required")
    with _payments_lock:
        conn = sqlite3.connect(str(PAYMENTS_DB))
        row = conn.execute(
            "SELECT balance, total_purchased, total_used FROM credits WHERE api_key = ?",
            (api_key,)
        ).fetchone()
        conn.close()
    if not row:
        return {"balance": 0, "total_purchased": 0, "total_used": 0, "message": "No credit account found. Buy credits at POST /api/credits/buy"}
    return {"balance": row[0], "total_purchased": row[1], "total_used": row[2]}


@app.get("/checkout", response_class=HTMLResponse)
async def checkout_page(tier: str = "pro"):
    tier_info = PRICING_TIERS.get(tier, PRICING_TIERS["pro"])
    amount = tier_info["amount"]
    name = tier_info["name"]
    limit = tier_info["daily_limit"]
    return HTMLResponse(f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Checkout - ToolPipe {name}</title>
<meta name="description" content="Upgrade to ToolPipe {name}: {limit:,} API calls/day for ${amount}/month. Pay with crypto, no KYC required.">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0a0a0a;color:#e0e0e0;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}}
.checkout{{max-width:480px;width:100%;background:#111;border:1px solid #222;border-radius:16px;overflow:hidden}}
.header{{background:linear-gradient(135deg,#6c63ff,#4f46e5);padding:32px;text-align:center}}
.header h1{{color:#fff;font-size:1.5rem;margin-bottom:4px}}
.header .price{{color:rgba(255,255,255,0.9);font-size:2rem;font-weight:800;margin:8px 0}}
.header .price span{{font-size:0.9rem;font-weight:400}}
.header .features{{color:rgba(255,255,255,0.8);font-size:0.9rem}}
.body{{padding:32px}}
.step{{display:none}}.step.active{{display:block}}
label{{color:#94a3b8;font-size:0.85rem;display:block;margin-bottom:6px}}
input{{width:100%;padding:12px 16px;background:#1a1a1a;border:1px solid #2a2a2a;border-radius:8px;color:#e0e0e0;font-size:1rem;margin-bottom:16px;outline:none}}
input:focus{{border-color:#6c63ff}}
.btn{{width:100%;padding:14px;background:#6c63ff;color:#fff;border:none;border-radius:10px;font-size:1rem;font-weight:700;cursor:pointer;transition:background 0.2s}}
.btn:hover{{background:#5b54e6}}
.btn:disabled{{background:#333;cursor:not-allowed}}
.addresses{{background:#0a0a0a;border-radius:8px;padding:16px;margin:16px 0}}
.addr{{margin:8px 0}}
.addr-label{{color:#64748b;font-size:0.8rem}}
.addr-value{{color:#6c63ff;font-family:monospace;font-size:0.8rem;word-break:break-all;cursor:pointer}}
.addr-value:hover{{color:#8b85ff}}
.notice{{background:#1a1a1a;border-left:3px solid #6c63ff;padding:12px 16px;margin:16px 0;border-radius:0 8px 8px 0;font-size:0.85rem;color:#94a3b8}}
.success{{text-align:center;padding:20px 0}}
.success h2{{color:#22c55e;margin-bottom:8px}}
.key{{background:#0a0a0a;padding:12px;border-radius:8px;font-family:monospace;color:#6c63ff;word-break:break-all;margin:12px 0}}
.spinner{{display:inline-block;width:20px;height:20px;border:2px solid #fff;border-top-color:transparent;border-radius:50%;animation:spin 0.6s linear infinite;vertical-align:middle;margin-right:8px}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
.back{{color:#64748b;font-size:0.85rem;cursor:pointer;margin-top:12px;display:inline-block}}
.back:hover{{color:#94a3b8}}
.powered{{text-align:center;padding:16px;color:#333;font-size:0.75rem}}
.powered a{{color:#444}}
</style></head><body>
<div class="checkout">
<div class="header">
<h1>ToolPipe {name}</h1>
<div class="price">${amount}<span>/month</span></div>
<div class="features">{limit:,} API calls/day &middot; All 200+ endpoints &middot; Priority support</div>
</div>
<div class="body">
<div id="step1" class="step active">
<label>Email address</label>
<input type="email" id="email" placeholder="you@example.com" autofocus>
<button class="btn" onclick="createOrder()" id="orderBtn">Continue to Payment</button>
</div>
<div id="step2" class="step">
<div class="notice">Send <strong>${amount}</strong> in any supported cryptocurrency to one of the addresses below. USDC on Base has the lowest gas fees (~$0.01).</div>
<div class="addresses">
<div class="addr"><div class="addr-label">EVM (Ethereum, Polygon, Base, Arbitrum, Optimism, BSC)</div><div class="addr-value" onclick="copyAddr(this)">{WALLET_ADDRESS}</div></div>
<div class="addr"><div class="addr-label">Solana (SOL, USDC-SPL)</div><div class="addr-value" onclick="copyAddr(this)">{SOLANA_WALLET}</div></div>
</div>
<p style="color:#64748b;font-size:0.8rem;margin-bottom:4px">Accepted: ETH, USDC, USDT, DAI, SOL, BNB, AVAX, any ERC-20</p>
<p style="color:#64748b;font-size:0.8rem;margin-bottom:16px">Order: <code id="orderId" style="color:#6c63ff"></code></p>
<label>Transaction hash (after sending)</label>
<input type="text" id="txHash" placeholder="0x... or Solana tx hash">
<button class="btn" onclick="verifyPayment()" id="verifyBtn">Verify Payment</button>
<div class="back" onclick="showStep(1)">Back</div>
</div>
<div id="step3" class="step">
<div class="success">
<h2>Payment Verified!</h2>
<p style="color:#94a3b8">Your API key has been upgraded to {name}.</p>
<div class="key" id="apiKey"></div>
<p style="color:#64748b;font-size:0.85rem">Save this key. Use it with X-API-Key header or api_key query parameter.</p>
<a href="/api-keys" class="btn" style="display:inline-block;text-decoration:none;margin-top:16px;width:auto;padding:12px 32px">View Dashboard</a>
</div>
</div>
<div id="step-error" class="step">
<div style="text-align:center;padding:20px 0">
<h2 style="color:#ef4444">Verification Pending</h2>
<p id="errorMsg" style="color:#94a3b8;margin:8px 0"></p>
<button class="btn" onclick="showStep(2)" style="margin-top:16px">Try Again</button>
</div>
</div>
</div>
<div class="powered">Powered by <a href="/">ToolPipe</a> &middot; Crypto payments, no KYC</div>
</div>
<script>
let currentOrderId='';
function showStep(n){{document.querySelectorAll('.step').forEach(s=>s.classList.remove('active'));document.getElementById(n==='error'?'step-error':'step'+n).classList.add('active')}}
function copyAddr(el){{navigator.clipboard.writeText(el.textContent);el.style.color='#22c55e';setTimeout(()=>el.style.color='',1500)}}
async function createOrder(){{
  const email=document.getElementById('email').value.trim();
  if(!email||!email.includes('@')){{alert('Valid email required');return}}
  const btn=document.getElementById('orderBtn');btn.disabled=true;btn.innerHTML='<span class="spinner"></span>Creating...';
  try{{
    const r=await fetch('/payments/create',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{email,tier:'{tier}'}})}});
    const d=await r.json();
    if(d.payment_url&&d.gateway!=='direct_crypto'){{window.location.href=d.payment_url;return}}
    currentOrderId=d.order_id;
    document.getElementById('orderId').textContent=d.order_id;
    showStep(2);
  }}catch(e){{alert('Error: '+e.message)}}
  btn.disabled=false;btn.textContent='Continue to Payment';
}}
async function verifyPayment(){{
  const txHash=document.getElementById('txHash').value.trim();
  if(!txHash){{alert('Enter transaction hash');return}}
  const btn=document.getElementById('verifyBtn');btn.disabled=true;btn.innerHTML='<span class="spinner"></span>Verifying on-chain...';
  try{{
    const r=await fetch('/payments/verify-tx',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{order_id:currentOrderId,tx_hash:txHash}})}});
    const d=await r.json();
    if(d.status==='verified'){{document.getElementById('apiKey').textContent=d.api_key;showStep(3)}}
    else{{document.getElementById('errorMsg').textContent=d.message||'Transaction not confirmed yet. Try again in a few minutes.';showStep('error')}}
  }}catch(e){{document.getElementById('errorMsg').textContent=e.message;showStep('error')}}
  btn.disabled=false;btn.textContent='Verify Payment';
}}
</script>
</body></html>""")


# --- Solana Transaction Verification ---

async def verify_solana_tx(tx_hash: str) -> dict:
    """Verify a Solana transaction to our wallet."""
    if not SOLANA_WALLET:
        return {"verified": False, "error": "Solana wallet not configured"}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(SOLANA_RPC, json={
                "jsonrpc": "2.0", "id": 1,
                "method": "getTransaction",
                "params": [tx_hash, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}]
            })
            data = resp.json()
            result = data.get("result")
            if not result:
                return {"verified": False, "error": "Transaction not found on Solana"}

            meta = result.get("meta", {})
            if meta.get("err") is not None:
                return {"verified": False, "error": "Transaction failed on-chain"}

            our_wallet_lower = SOLANA_WALLET.lower()
            # Check SOL transfers via balance changes
            pre_balances = meta.get("preBalances", [])
            post_balances = meta.get("postBalances", [])
            account_keys = result.get("transaction", {}).get("message", {}).get("accountKeys", [])

            for i, key_info in enumerate(account_keys):
                pubkey = key_info.get("pubkey", key_info) if isinstance(key_info, dict) else str(key_info)
                if str(pubkey).lower() == our_wallet_lower and i < len(pre_balances) and i < len(post_balances):
                    diff_lamports = post_balances[i] - pre_balances[i]
                    if diff_lamports > 0:
                        sol_amount = diff_lamports / 1e9
                        return {
                            "verified": True,
                            "chain": "solana",
                            "type": "native_transfer",
                            "token": "SOL",
                            "amount": sol_amount,
                            "tx_hash": tx_hash,
                        }

            # Check SPL token transfers (USDC on Solana)
            for ix in (result.get("transaction", {}).get("message", {}).get("instructions", []) +
                       meta.get("innerInstructions", [{}])):
                parsed = ix.get("parsed", {}) if isinstance(ix, dict) else {}
                if isinstance(parsed, dict) and parsed.get("type") in ("transfer", "transferChecked"):
                    info = parsed.get("info", {})
                    dest = info.get("destination", "")
                    if str(dest).lower() == our_wallet_lower:
                        amount = float(info.get("amount", info.get("tokenAmount", {}).get("uiAmount", 0)))
                        return {
                            "verified": True,
                            "chain": "solana",
                            "type": "token_transfer",
                            "token": "USDC-SPL",
                            "amount": amount,
                            "tx_hash": tx_hash,
                        }

    except Exception:
        pass
    return {"verified": False, "error": "Could not verify Solana transaction"}


# --- Agent-Optimized Payment Flow ---
# Single endpoint for AI agents: create order + get payment instructions in one call

class AgentPayRequest(BaseModel):
    email: str
    tier: str = "pro"
    preferred_chain: str = "base"  # base, polygon, arbitrum, ethereum, optimism, solana


@app.post("/payments/agent-pay")
async def agent_pay(req: AgentPayRequest, request: Request):
    """
    Agent-optimized payment endpoint. Returns everything an AI agent needs
    to pay for API access in a single call. Designed for MCP tool use.

    Flow: 1) Call this endpoint -> 2) Send crypto -> 3) POST /payments/verify-tx
    """
    email = req.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Valid email required")
    tier = req.tier.lower()
    if tier not in PRICING_TIERS:
        raise HTTPException(status_code=400, detail=f"Invalid tier: {', '.join(PRICING_TIERS.keys())}")

    tier_info = PRICING_TIERS[tier]
    order_id = f"tp-{tier}-{uuid.uuid4().hex[:12]}"
    amount = tier_info["amount"]
    now = datetime.now(timezone.utc).isoformat()

    # Record the order
    with _payments_lock:
        conn = sqlite3.connect(str(PAYMENTS_DB))
        conn.execute(
            "INSERT OR REPLACE INTO payments (track_id, order_id, email, tier, amount, status, created_at) VALUES (?, ?, ?, ?, ?, 'awaiting_direct', ?)",
            (order_id, order_id, email, tier, amount, now)
        )
        conn.commit()
        conn.close()

    chain = req.preferred_chain.lower()

    # Get current ETH price for amount calculation
    eth_price = await get_eth_price_usd()
    eth_amount = round(amount / eth_price, 6) if eth_price > 0 else None

    response = {
        "order_id": order_id,
        "amount_usd": amount,
        "tier": tier,
        "daily_limit": tier_info["daily_limit"],
        "payment_instructions": {
            "evm": {
                "address": WALLET_ADDRESS,
                "networks": ["ethereum", "polygon", "arbitrum", "base", "optimism"],
                "recommended_network": chain if chain != "solana" else "base",
                "accepted_tokens": ["USDC", "USDT", "DAI", "ETH", "WETH"],
                "recommended_token": "USDC",
                "stablecoin_amount": amount,
            },
        },
        "verification": {
            "endpoint": "POST /payments/verify-tx",
            "body": {"order_id": order_id, "tx_hash": "<your_tx_hash>"},
            "result": "API key returned instantly on successful verification",
        },
        "notes": "Send any supported token on any supported network. USDC on Base has lowest gas fees (~$0.01). After sending, POST your tx_hash to /payments/verify-tx for instant upgrade.",
    }

    if eth_amount:
        response["payment_instructions"]["evm"]["eth_amount"] = eth_amount
        response["payment_instructions"]["evm"]["eth_price_usd"] = eth_price

    if SOLANA_WALLET:
        response["payment_instructions"]["solana"] = {
            "address": SOLANA_WALLET,
            "accepted_tokens": ["SOL", "USDC-SPL"],
            "stablecoin_amount": amount,
        }

    return response


# Update verify-tx to also check Solana
_original_verify_tx_onchain = verify_tx_onchain

async def verify_tx_onchain_multi(tx_hash: str) -> dict:
    """Verify a transaction on EVM chains or Solana."""
    # Try EVM first
    result = await _original_verify_tx_onchain(tx_hash)
    if result.get("verified"):
        return result
    # Try Solana (Solana tx hashes are base58, not 0x-prefixed)
    if not tx_hash.startswith("0x") and SOLANA_WALLET:
        sol_result = await verify_solana_tx(tx_hash)
        if sol_result.get("verified"):
            return sol_result
    return result

verify_tx_onchain = verify_tx_onchain_multi


# --- Pricing Page (v2, enhanced) ---

@app.get("/pricing-v2", response_class=HTMLResponse)
async def pricing_page_v2():
    return HTMLResponse(inject_snippet("""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>ToolPipe Pricing - API Plans for Developers & AI Agents</title>
<meta name="description" content="ToolPipe API pricing: Free tier (100 calls/day), Pro ($9.99/mo, 10K calls/day), Enterprise ($49.99/mo, 100K calls/day). Pay with crypto. No KYC.">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0a0a0a;color:#e0e0e0}
.container{max-width:900px;margin:0 auto;padding:60px 20px}
h1{font-size:2.5rem;color:#fff;text-align:center;margin-bottom:8px}
.sub{text-align:center;color:#94a3b8;margin-bottom:48px;font-size:1.1rem}
.tiers{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
@media(max-width:700px){.tiers{grid-template-columns:1fr}}
.tier{background:#1a1a1a;border:2px solid #2a2a2a;border-radius:16px;padding:32px;position:relative}
.tier.featured{border-color:#6c63ff;box-shadow:0 0 40px rgba(108,99,255,0.15)}
.badge{position:absolute;top:-12px;left:50%;transform:translateX(-50%);background:#6c63ff;color:#fff;padding:4px 16px;border-radius:20px;font-size:0.75rem;font-weight:700;text-transform:uppercase}
.tier h2{color:#fff;font-size:1.3rem;margin-bottom:8px}
.tier .price{font-size:2.2rem;font-weight:800;color:#fff;margin-bottom:4px}
.tier .price span{font-size:0.9rem;color:#64748b;font-weight:400}
.tier .period{color:#64748b;font-size:0.85rem;margin-bottom:20px}
.tier ul{list-style:none;padding:0;margin-bottom:24px}
.tier li{color:#94a3b8;padding:6px 0;font-size:0.95rem}
.tier li::before{content:"-> ";color:#6c63ff}
.btn{display:block;text-align:center;padding:14px;border-radius:10px;font-weight:600;font-size:1rem;text-decoration:none;cursor:pointer;border:none;width:100%;transition:all 0.2s}
.btn-free{background:#2a2a2a;color:#fff}
.btn-free:hover{background:#3a3a3a}
.btn-pro{background:#6c63ff;color:#fff}
.btn-pro:hover{background:#5b52ee;transform:translateY(-1px)}
.btn-ent{background:linear-gradient(135deg,#6c63ff,#3b82f6);color:#fff}
.btn-ent:hover{transform:translateY(-1px)}
.crypto-note{text-align:center;margin-top:40px;padding:24px;background:#1a1a2e;border:1px solid #6c63ff44;border-radius:12px}
.crypto-note h3{color:#fff;margin-bottom:8px}
.crypto-note p{color:#94a3b8;font-size:0.95rem}
.faq{margin-top:48px}
.faq h2{color:#fff;text-align:center;margin-bottom:24px}
.faq-item{background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;padding:20px;margin-bottom:12px}
.faq-item h3{color:#fff;font-size:1rem;margin-bottom:8px}
.faq-item p{color:#94a3b8;font-size:0.9rem;line-height:1.6}
.links{text-align:center;margin-top:32px}
.links a{color:#6c63ff;text-decoration:none;margin:0 16px}
</style></head><body>
<div class="container">
<h1>Simple, Transparent Pricing</h1>
<p class="sub">175+ developer APIs. Pay with crypto. No KYC needed.</p>

<div class="tiers">
<div class="tier">
<h2>Free</h2>
<div class="price">$0 <span>/mo</span></div>
<div class="period">No credit card required</div>
<ul>
<li>100 requests/day</li>
<li>All 230+ endpoints</li>
<li>JSON, PDF, QR, hash, UUID, DNS, and more</li>
<li>Community support</li>
<li>Rate limited (100/min)</li>
</ul>
<a href="/api-keys" class="btn btn-free">Get Free API Key</a>
</div>

<div class="tier featured">
<div class="badge">Most Popular</div>
<h2>Pro</h2>
<div class="price">$9.99 <span>/mo</span></div>
<div class="period">Billed monthly via crypto</div>
<ul>
<li>10,000 requests/day</li>
<li>All 230+ endpoints</li>
<li>Priority support</li>
<li>No rate limits</li>
<li>Bulk operations</li>
<li>Webhook notifications</li>
<li>MCP server access</li>
</ul>
<button class="btn btn-pro" onclick="buyPlan('pro')">Upgrade to Pro</button>
</div>

<div class="tier">
<h2>Enterprise</h2>
<div class="price">$49.99 <span>/mo</span></div>
<div class="period">For high-volume users & AI agents</div>
<ul>
<li>100,000 requests/day</li>
<li>All 230+ endpoints</li>
<li>Dedicated support</li>
<li>No rate limits</li>
<li>Bulk operations</li>
<li>Custom webhooks</li>
<li>MCP server access</li>
<li>SLA guarantee</li>
</ul>
<button class="btn btn-ent" onclick="buyPlan('enterprise')">Get Enterprise</button>
</div>
</div>

<div class="crypto-note">
<h3>Pay with Crypto</h3>
<p>We accept BTC, ETH, USDT, USDC, SOL, TON, DOGE, LTC, and 20+ cryptocurrencies via OxaPay. No KYC, no bank account needed. Perfect for AI agents and global developers.</p>
</div>

<div class="faq">
<h2>FAQ</h2>
<div class="faq-item"><h3>How do I get started?</h3><p>Sign up for a free API key at <a href="/api-keys" style="color:#6c63ff">/api-keys</a>. No credit card needed. Start making API calls immediately.</p></div>
<div class="faq-item"><h3>How does crypto payment work?</h3><p>Click "Upgrade to Pro" or "Get Enterprise", enter your email, and you will be redirected to a secure crypto payment page. Once payment confirms, your API key is automatically upgraded.</p></div>
<div class="faq-item"><h3>Can AI agents use this API?</h3><p>Yes! ToolPipe is designed for both human developers and AI agents. Use our MCP server package or call the REST API directly. Agents can self-register for API keys and upgrade via crypto.</p></div>
<div class="faq-item"><h3>What endpoints are included?</h3><p>All plans include access to all 175+ endpoints: JSON formatting, PDF tools, QR codes, hash generation, UUID, DNS lookup, image processing, text analysis, and more. See <a href="/docs" style="color:#6c63ff">/docs</a> for the full list.</p></div>
<div class="faq-item"><h3>Is there a refund policy?</h3><p>Due to the nature of crypto payments, refunds are handled case-by-case. Contact toolpipe-ads@sharebot.net.</p></div>
</div>

<div class="links">
<a href="/">Home</a>
<a href="/api-keys">Get API Key</a>
<a href="/docs">API Docs</a>
<a href="/donate">Donate</a>
</div>
</div>

<!-- Payment Modal -->
<div id="pay-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.8);z-index:10000;display:none;align-items:center;justify-content:center">
<div style="background:#1a1a1a;border:2px solid #6c63ff;border-radius:16px;padding:32px;max-width:420px;width:90%;position:relative">
<button onclick="closeModal()" style="position:absolute;top:12px;right:16px;background:none;border:none;color:#fff;font-size:1.5rem;cursor:pointer">x</button>
<h2 style="color:#fff;margin-bottom:4px" id="modal-title">Upgrade to Pro</h2>
<p style="color:#94a3b8;margin-bottom:20px" id="modal-price">$9.99/month</p>
<input type="email" id="pay-email" placeholder="your@email.com" style="width:100%;background:#111;border:1px solid #2a2a2a;color:#e0e0e0;padding:12px;border-radius:8px;font-size:1rem;margin-bottom:12px">
<button id="pay-btn" onclick="submitPayment()" style="width:100%;background:#6c63ff;color:#fff;border:none;padding:14px;border-radius:8px;font-weight:600;font-size:1rem;cursor:pointer">Pay with Crypto</button>
<p id="pay-status" style="color:#94a3b8;margin-top:12px;font-size:0.9rem;text-align:center;display:none"></p>
<div style="margin-top:16px;padding-top:16px;border-top:1px solid #2a2a2a">
<p style="color:#64748b;font-size:0.8rem;text-align:center">Or send crypto directly:</p>
<p style="color:#22c55e;font-family:monospace;font-size:0.75rem;text-align:center;word-break:break-all;margin-top:4px">0xBCF464909b748d720fd5DDA25ad3d313Dd4b53D6</p>
<p style="color:#64748b;font-size:0.75rem;text-align:center;margin-top:4px">Then email toolpipe-ads@sharebot.net with tx hash</p>
</div>
</div>
</div>

<script>
let selectedTier = 'pro';
function buyPlan(tier) {
    selectedTier = tier;
    const prices = {pro: '$9.99/month', enterprise: '$49.99/month'};
    const titles = {pro: 'Upgrade to Pro', enterprise: 'Get Enterprise'};
    document.getElementById('modal-title').textContent = titles[tier];
    document.getElementById('modal-price').textContent = prices[tier];
    document.getElementById('pay-modal').style.display = 'flex';
    document.getElementById('pay-email').focus();
}
function closeModal() {
    document.getElementById('pay-modal').style.display = 'none';
}
async function submitPayment() {
    const email = document.getElementById('pay-email').value.trim();
    if (!email || !email.includes('@')) { alert('Enter a valid email'); return; }
    const btn = document.getElementById('pay-btn');
    const status = document.getElementById('pay-status');
    btn.textContent = 'Creating payment...';
    btn.disabled = true;
    status.style.display = 'none';
    try {
        const res = await fetch('/payments/create', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, tier: selectedTier})
        });
        const data = await res.json();
        if (data.success && data.payment_url) {
            window.location.href = data.payment_url;
        } else if (data.success && data.payment_method === 'crypto_direct') {
            const addr = data.primary_address;
            const amt = data.amount_usd;
            const oid = data.order_id;
            const qr = data.qr_code_url;
            status.innerHTML = '<div style="text-align:center">' +
              '<strong style="font-size:1.1rem;color:#22c55e">Send Crypto to Complete Payment</strong><br><br>' +
              '<img src="' + qr + '" alt="QR Code" style="width:200px;height:200px;border-radius:8px;margin:8px auto;display:block;background:#fff;padding:8px"><br>' +
              '<code style="color:#22c55e;word-break:break-all;font-size:0.85rem;background:#111;padding:8px 12px;border-radius:6px;display:block;margin:8px 0">' + addr + '</code>' +
              '<p style="margin:8px 0;color:#e0e0e0">Amount: <strong>$' + amt + '</strong> in ETH, USDC, USDT, or any ERC-20</p>' +
              '<p style="color:#94a3b8;font-size:0.85rem">Networks: Ethereum, Polygon, Arbitrum, Base, Optimism</p>' +
              '<p style="margin-top:12px;padding:12px;background:#1a1a2e;border-radius:8px;border:1px solid #6c63ff44">' +
              '<div style="margin-top:12px"><input id="verify-tx-hash" placeholder="Paste your tx hash (0x...)" style="width:100%;background:#111;border:1px solid #2a2a2a;color:#e0e0e0;padding:10px;border-radius:6px;font-size:0.85rem;font-family:monospace;margin-bottom:8px">' +
              '<button onclick="verifyTx(\\''+oid+'\\',document.getElementById(\\'verify-tx-hash\\').value)" style="width:100%;background:#22c55e;color:#fff;border:none;padding:12px;border-radius:8px;font-weight:600;cursor:pointer">Verify Payment On-Chain</button>' +
              '<p id="verify-result" style="margin-top:8px;font-size:0.85rem;text-align:center"></p></div>' +
              '<p style="margin-top:8px;color:#64748b;font-size:0.75rem;text-align:center">Or email <a href="mailto:toolpipe-ads@sharebot.net?subject=Payment%20' + oid + '" style="color:#6c63ff">toolpipe-ads@sharebot.net</a> with tx hash</p>' +
              '</div>';
            status.style.color = '#e0e0e0';
            status.style.display = 'block';
            btn.textContent = 'Payment Address Ready';
            btn.disabled = true;
        } else {
            status.textContent = data.error || 'Payment creation failed.';
            status.style.color = '#ef4444';
            status.style.display = 'block';
            btn.textContent = 'Pay with Crypto';
            btn.disabled = false;
        }
    } catch(e) {
        status.textContent = 'Network error. Try the direct crypto address below.';
        status.style.color = '#ef4444';
        status.style.display = 'block';
        btn.textContent = 'Pay with Crypto';
        btn.disabled = false;
    }
}
document.getElementById('pay-modal').addEventListener('click', function(e) {
    if (e.target === this) closeModal();
});
async function verifyTx(orderId, txHash) {
    const result = document.getElementById('verify-result');
    if (!txHash || !txHash.startsWith('0x') || txHash.length !== 66) {
        result.textContent = 'Enter a valid tx hash (0x + 64 hex chars)';
        result.style.color = '#ef4444';
        return;
    }
    result.textContent = 'Checking on-chain (may take 10-20s)...';
    result.style.color = '#94a3b8';
    try {
        const res = await fetch('/payments/verify-tx', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({order_id: orderId, tx_hash: txHash})
        });
        const data = await res.json();
        if (data.status === 'verified') {
            result.innerHTML = '<strong style="color:#22c55e">Payment verified! Your API key: ' + data.api_key + '</strong><br><a href="/api-keys" style="color:#6c63ff">View Dashboard</a>';
        } else if (data.status === 'already_paid') {
            result.innerHTML = '<strong style="color:#22c55e">Already verified!</strong> <a href="/api-keys" style="color:#6c63ff">Dashboard</a>';
        } else {
            result.textContent = data.message || 'Not verified yet. Try again in a few minutes.';
            result.style.color = '#f59e0b';
        }
    } catch(e) {
        result.textContent = 'Network error. Try again.';
        result.style.color = '#ef4444';
    }
}
</script>
</body></html>"""))


# --- Donate Page ---

@app.get("/donate", response_class=HTMLResponse)
async def donate_page():
    return HTMLResponse("""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Support ToolPipe - Donate to Keep Free APIs Running</title>
<meta name="description" content="Support ToolPipe's 65+ free developer APIs and tools. Donate via card or crypto to help us keep building.">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0a0a0a;color:#e0e0e0}
.container{max-width:700px;margin:0 auto;padding:60px 20px;text-align:center}
h1{font-size:2.5rem;margin-bottom:12px;color:#fff}
.subtitle{font-size:1.1rem;color:#94a3b8;margin-bottom:40px;line-height:1.6}
h2{font-size:1.3rem;color:#fff;margin:40px 0 16px;text-align:center}
.options{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:32px}
.option{background:#1a1a1a;border:2px solid #2a2a2a;border-radius:12px;padding:24px 16px;cursor:pointer;transition:all 0.2s}
.option:hover{border-color:#6c63ff;transform:translateY(-2px)}
.option.selected{border-color:#6c63ff;background:#1a1a2e}
.option .amount{font-size:1.5rem;font-weight:700;color:#fff}
.option .label{font-size:0.85rem;color:#64748b;margin-top:4px}
.custom-amount{margin-bottom:32px}
.custom-amount input{background:#1a1a1a;border:1px solid #2a2a2a;color:#e0e0e0;padding:12px 16px;border-radius:8px;font-size:1rem;width:200px;text-align:center}
.custom-amount input:focus{outline:none;border-color:#6c63ff}
.section{background:#1a1a1a;border:1px solid #2a2a2a;border-radius:16px;padding:32px;margin:24px 0;text-align:left}
.section-title{font-size:1.1rem;font-weight:600;color:#fff;margin-bottom:12px;display:flex;align-items:center;gap:8px}
.crypto-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:16px}
.crypto-item{background:#111;border:1px solid #2a2a2a;border-radius:8px;padding:16px}
.crypto-item .name{font-weight:600;color:#fff;font-size:0.95rem;margin-bottom:4px}
.crypto-item .status{color:#f59e0b;font-size:0.8rem}
.coming-badge{display:inline-block;background:#f59e0b22;color:#f59e0b;padding:2px 10px;border-radius:12px;font-size:0.75rem;font-weight:600;margin-left:8px}
.waitlist-box{background:#1a1a2e;border:1px solid #3b82f6;border-radius:16px;padding:32px;margin:32px 0;text-align:center}
.waitlist-box h3{color:#fff;font-size:1.2rem;margin-bottom:8px}
.waitlist-box p{color:#94a3b8;font-size:0.95rem;margin-bottom:16px}
.waitlist-form{display:flex;gap:10px;max-width:420px;margin:0 auto}
.waitlist-form input{flex:1;background:#111;border:1px solid #2a2a2a;color:#e0e0e0;padding:12px 16px;border-radius:8px;font-size:1rem}
.waitlist-form input:focus{outline:none;border-color:#6c63ff}
.waitlist-form button{background:#6c63ff;color:#fff;border:none;padding:12px 24px;border-radius:8px;cursor:pointer;font-weight:600;white-space:nowrap;transition:background 0.2s}
.waitlist-form button:hover{background:#5b52e0}
.success-msg{display:none;color:#22c55e;margin-top:12px;font-size:0.95rem}
.error-msg{display:none;color:#ef4444;margin-top:12px;font-size:0.95rem}
.cta{display:inline-block;padding:16px 48px;background:#6c63ff;color:white;border-radius:8px;text-decoration:none;font-weight:600;font-size:1.1rem;margin-top:8px;border:none;cursor:pointer;transition:all 0.2s}
.cta:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(108,99,255,0.3)}
.links{margin-top:32px;display:flex;justify-content:center;gap:24px;flex-wrap:wrap}
.links a{color:#6c63ff;text-decoration:none;font-size:0.95rem}
.links a:hover{text-decoration:underline}
.note{color:#64748b;font-size:0.85rem;margin-top:24px}
@media(max-width:500px){.options{grid-template-columns:1fr}.crypto-grid{grid-template-columns:1fr}.waitlist-form{flex-direction:column}}
</style></head><body>
<div class="container">
<h1>Support ToolPipe</h1>
<p class="subtitle">We provide 65+ free developer APIs and tools with no sign-up required. Your support helps us keep the servers running and ship new features.</p>

<h2>Choose an Amount</h2>
<div class="options">
<div class="option" onclick="selectAmount(5,this)"><div class="amount">$5</div><div class="label">A coffee</div></div>
<div class="option selected" onclick="selectAmount(15,this)"><div class="amount">$15</div><div class="label">A lunch</div></div>
<div class="option" onclick="selectAmount(50,this)"><div class="amount">$50</div><div class="label">Champion</div></div>
</div>
<div class="custom-amount">
<input type="number" id="customAmount" placeholder="Or enter custom amount ($)" min="1" onfocus="clearSelection()">
</div>

<div class="section">
<div class="section-title">Pay with Card</div>
<p style="color:#94a3b8;font-size:0.95rem;margin-bottom:16px;">Stripe integration is being finalized. Join the waitlist below and we will email you the moment card payments go live.</p>
<a href="#waitlist-section" class="cta" onclick="document.getElementById('waitlist-section').scrollIntoView({behavior:'smooth'}); return false;" style="display:block;text-align:center;padding:14px;font-size:1rem;">Notify Me When Ready</a>
</div>

<div class="section">
<div class="section-title">Pay with Crypto <span style="display:inline-block;background:#22c55e22;color:#22c55e;padding:2px 10px;border-radius:12px;font-size:0.75rem;font-weight:600;margin-left:8px;">LIVE</span></div>
<p style="color:#94a3b8;font-size:0.95rem;margin-bottom:16px;">Send crypto directly to our wallet. All major ERC-20 tokens accepted on the same address.</p>
<div style="background:#111;border:1px solid #2a2a2a;border-radius:12px;padding:20px;margin-bottom:16px">
<div style="color:#fff;font-weight:600;margin-bottom:8px;">Ethereum / USDC / USDT / ERC-20 Tokens</div>
<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">
<code style="background:#0a0a0a;color:#22c55e;padding:8px 12px;border-radius:6px;font-size:0.85rem;word-break:break-all;flex:1">0xBCF464909b748d720fd5DDA25ad3d313Dd4b53D6</code>
<button onclick="navigator.clipboard.writeText('0xBCF464909b748d720fd5DDA25ad3d313Dd4b53D6');this.textContent='Copied!';setTimeout(()=>this.textContent='Copy',2000)" style="background:#6c63ff;color:white;border:none;padding:8px 16px;border-radius:6px;cursor:pointer;font-weight:600;white-space:nowrap">Copy</button>
</div>
<p style="color:#64748b;font-size:0.8rem;margin-top:8px;">Supports: ETH, USDC, USDT, DAI, and any ERC-20 token on Ethereum mainnet, Polygon, Arbitrum, Base, or Optimism.</p>
</div>
<div style="background:#111;border:1px solid #2a2a2a;border-radius:12px;padding:16px">
<p style="color:#94a3b8;font-size:0.9rem;">After sending, email <a href="mailto:toolpipe-ads@sharebot.net" style="color:#6c63ff">toolpipe-ads@sharebot.net</a> with your tx hash to receive Pro API access.</p>
</div>
</div>

<div class="waitlist-box" id="waitlist-section">
<h3>Get Notified When Donations Go Live</h3>
<p>Enter your email and we will notify you when card and crypto donations are ready. Early supporters may receive Pro access as a thank-you.</p>
<div class="waitlist-form">
<input type="email" id="donateEmail" placeholder="your@email.com">
<button onclick="submitDonateWaitlist()">Join Waitlist</button>
</div>
<div class="success-msg" id="successMsg">You are on the list. We will email you when donations go live.</div>
<div class="error-msg" id="errorMsg">Something went wrong. Please try again.</div>
</div>

<a href="/pricing" class="cta" style="margin-top:24px;">Get Pro Access Instead</a>

<div class="links">
<a href="mailto:toolpipe-project@sharebot.net">toolpipe-project@sharebot.net</a>
<a href="/">Back to ToolPipe</a>
<a href="/docs">API Docs</a>
</div>
<p class="note">ToolPipe is an independent developer tools project. 100% of donations go toward server costs and development.</p>
</div>
<script>
let selectedAmount = 15;
function selectAmount(n, el) {
    selectedAmount = n;
    document.querySelectorAll('.option').forEach(o => o.classList.remove('selected'));
    el.classList.add('selected');
    document.getElementById('customAmount').value = '';
}
function clearSelection() {
    document.querySelectorAll('.option').forEach(o => o.classList.remove('selected'));
}
async function submitDonateWaitlist() {
    const email = document.getElementById('donateEmail').value.trim();
    if (!email || !email.includes('@')) { alert('Please enter a valid email address.'); return; }
    const amount = document.getElementById('customAmount').value || selectedAmount || 15;
    try {
        const res = await fetch('/api-keys/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email, source: 'donate-waitlist', amount: amount }),
        });
        if (res.ok) {
            document.getElementById('successMsg').style.display = 'block';
            document.getElementById('errorMsg').style.display = 'none';
            document.getElementById('donateEmail').value = '';
        } else {
            document.getElementById('errorMsg').style.display = 'block';
        }
    } catch (e) {
        document.getElementById('errorMsg').style.display = 'block';
    }
}
</script>
</body></html>""")


# --- JSON Validate API ---

@app.post("/api/json/validate")
async def json_validate(request: Request):
    """Validate JSON syntax and return formatted JSON or error with line number."""
    try:
        body = await request.body()
        text = body.decode("utf-8")
        # Try to extract json field if it's a JSON request
        try:
            payload = json.loads(text)
            if isinstance(payload, dict) and "json" in payload:
                text = payload["json"]
        except Exception:
            pass
        parsed = json.loads(text)
        formatted = json.dumps(parsed, indent=2)
        return {
            "valid": True,
            "formatted": formatted,
            "type": "array" if isinstance(parsed, list) else "object" if isinstance(parsed, dict) else type(parsed).__name__,
            "size": len(formatted),
        }
    except json.JSONDecodeError as e:
        return JSONResponse(
            status_code=200,
            content={"valid": False, "error": str(e), "line": e.lineno, "column": e.colno, "position": e.pos},
        )
    except Exception as e:
        return JSONResponse(status_code=400, content={"valid": False, "error": str(e)})


# --- MCP Server Proxy ---

@app.api_route("/mcp", methods=["GET", "POST", "DELETE", "OPTIONS"])
async def mcp_proxy(request: Request):
    """Proxy MCP requests to the dedicated MCP HTTP server on port 8090."""
    method = request.method
    body = await request.body()
    headers = dict(request.headers)
    headers.pop("host", None)
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.request(
                method=method,
                url=f"http://localhost:8090/mcp",
                content=body,
                headers=headers,
            )
        response_headers = dict(resp.headers)
        response_headers.pop("transfer-encoding", None)
        response_headers.pop("content-encoding", None)
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=response_headers,
            media_type=resp.headers.get("content-type"),
        )
    except Exception as e:
        return JSONResponse(
            status_code=502,
            content={"error": f"MCP server unavailable: {e}"}
        )


def _get_tunnel_url():
    """Read the current tunnel URL from the capture file."""
    url_file = Path(__file__).parent.parent.parent / ".tunnel-url"
    try:
        return url_file.read_text().strip()
    except Exception:
        return "https://toolpipe.dev"


@app.get("/mcp-info")
async def mcp_info():
    """Information about the MCP server endpoint."""
    base = _get_tunnel_url()
    return {
        "name": "ToolPipe MCP Server",
        "version": "1.18.0",
        "protocol": "MCP (Model Context Protocol)",
        "transport": "Streamable HTTP",
        "tools": 156,
        "total_api_endpoints": 230,
        "endpoint": "/mcp",
        "remote_url": f"{base}/mcp",
        "quickstart": f"{base}/quickstart",
        "setup": {
            "claude_desktop": {
                "mcpServers": {
                    "toolpipe": {
                        "url": f"{base}/mcp"
                    }
                }
            },
            "cursor": {
                "mcpServers": {
                    "toolpipe": {
                        "url": f"{base}/mcp"
                    }
                }
            },
            "local_npx": "npx @cosai-labs/toolpipe-mcp-server",
            "npm_package": "@cosai-labs/toolpipe-mcp-server"
        },
        "pricing": {
            "free": {"daily_limit": 100, "signup": "email only"},
            "pro": {"price": "$9.99/mo", "daily_limit": 10000, "payment": "crypto"},
            "enterprise": {"price": "$49.99/mo", "daily_limit": 100000, "payment": "crypto"},
        },
    }


@app.get("/.well-known/mcp.json")
async def well_known_mcp():
    """MCP server discovery endpoint (well-known URI)."""
    base = _get_tunnel_url()
    return {
        "mcp_version": "2025-03-26",
        "name": "ToolPipe",
        "description": "230+ developer tools via MCP: JSON, QR, hash, UUID, DNS, regex, JWT, SQL, XML, YAML, PDF, code review, fake data, Dockerfile gen, and more",
        "url": f"{base}/mcp",
        "transport": "streamable-http",
        "tools_count": 156,
        "total_api_endpoints": 230,
        "npm_package": "@toolpipe/mcp-server",
        "pricing": {
            "free_tier": True,
            "free_daily_limit": 100,
            "pro": {"price_usd": 9.99, "daily_limit": 10000},
            "enterprise": {"price_usd": 49.99, "daily_limit": 100000},
        },
        "setup": {
            "claude_desktop": {"mcpServers": {"toolpipe": {"url": f"{base}/mcp"}}},
            "claude_code": f"claude mcp add toolpipe {base}/mcp",
            "npx": "npx -y @toolpipe/mcp-server",
        },
        "documentation": f"{base}/quickstart",
    }


@app.get("/.well-known/ai-plugin.json")
async def ai_plugin_manifest():
    """OpenAI-compatible plugin manifest for agent discovery."""
    base = _get_tunnel_url()
    return {
        "schema_version": "v1",
        "name_for_human": "ToolPipe Developer Tools",
        "name_for_model": "toolpipe",
        "description_for_human": "230+ free developer utility APIs: JSON formatting, QR codes, hashing, code review, fake data, DNS lookup, and more.",
        "description_for_model": "ToolPipe provides 230+ developer utility APIs. Use this for JSON formatting, QR code generation, hashing (MD5/SHA256/bcrypt), UUID generation, base64 encoding, markdown conversion, regex testing, DNS lookup, SSL checks, code review, fake data generation, Dockerfile generation, JWT creation, and more. All tools work without authentication for the free tier (100 calls/day).",
        "auth": {"type": "none"},
        "api": {"type": "openapi", "url": f"{base}/openapi.json"},
        "logo_url": f"{base}/favicon.ico",
        "contact_email": "toolpipe-ads@sharebot.net",
        "legal_info_url": f"{base}/terms",
    }


@app.get("/postman")
async def postman_collection():
    """Download Postman collection for all ToolPipe API endpoints."""
    postman_file = Path(__file__).parent / "postman-collection.json"
    if postman_file.exists():
        return JSONResponse(
            json.loads(postman_file.read_text()),
            headers={"Content-Disposition": "attachment; filename=toolpipe-postman-collection.json"}
        )
    return JSONResponse({"error": "Collection not found"}, status_code=404)


@app.get("/api/info")
async def api_info():
    """Complete API information and endpoint catalog."""
    base = _get_tunnel_url()
    return {
        "name": "ToolPipe API",
        "version": "1.18.0",
        "base_url": base,
        "total_endpoints": 230,
        "mcp_server": f"{base}/mcp",
        "docs": f"{base}/docs",
        "pricing": f"{base}/pricing",
        "categories": {
            "json_data": [
                "POST /json/format", "POST /api/convert/json-to-yaml", "POST /json/to-csv",
                "POST /api/json/validate-schema", "POST /api/code/format"
            ],
            "text": [
                "POST /text/analyze", "POST /api/text/summarize", "POST /api/text/detect-language",
                "POST /api/text/diff", "POST /api/text/slugify", "POST /api/regex/test",
                "POST /api/lorem-ipsum", "POST /api/markdown/table"
            ],
            "encoding_hashing": [
                "POST /hash/generate", "POST /base64", "POST /api/url/encode-decode",
                "POST /api/html/encode-decode", "POST /api/jwt/decode",
                "GET /uuid/generate", "POST /api/password/generate"
            ],
            "web_network": [
                "GET /dns/lookup", "GET /ip/lookup", "GET /ip/my",
                "GET /meta/extract", "GET /down/check", "GET /seo/analyze",
                "POST /api/http/request", "POST /s/create"
            ],
            "media": [
                "GET /qr/generate", "POST /api/screenshot", "POST /pdf/create",
                "POST /pdf/merge", "POST /pdf/extract-text"
            ],
            "utilities": [
                "GET /color/convert", "POST /api/timestamp/convert", "GET /api/timestamp/now",
                "POST /api/cron/parse", "GET /api/crypto/prices",
                "POST /api/css/minify", "POST /api/js/minify",
                "POST /markdown/to-html", "GET /api/random/quote"
            ],
            "payments": [
                "POST /payments/create", "GET /payments/status", "POST /payments/webhook"
            ]
        },
        "free_tier": {"daily_limit": 100, "signup": "Email only at /api-keys"},
        "paid_tiers": {
            "pro": {"price": "$9.99/mo", "daily_limit": 10000},
            "enterprise": {"price": "$49.99/mo", "daily_limit": 100000}
        }
    }


# --- NEW: AI Agent Utility Endpoints ---


class JSONPathRequest(BaseModel):
    json_data: str
    path: str


@app.post("/api/json/query")
async def json_query(req: JSONPathRequest):
    """Query JSON data using dot-notation paths (e.g., 'users[0].name', 'items.*.price')."""
    try:
        data = json.loads(req.json_data)
    except json.JSONDecodeError as e:
        raise HTTPException(400, f"Invalid JSON: {e}")

    def resolve_path(obj, path_parts):
        if not path_parts:
            return [obj]
        part = path_parts[0]
        rest = path_parts[1:]
        results = []
        if part == "*":
            if isinstance(obj, dict):
                for v in obj.values():
                    results.extend(resolve_path(v, rest))
            elif isinstance(obj, list):
                for item in obj:
                    results.extend(resolve_path(item, rest))
        elif "[" in part and part.endswith("]"):
            key = part[:part.index("[")]
            idx = int(part[part.index("[") + 1:-1])
            target = obj.get(key, obj) if isinstance(obj, dict) and key else obj
            if isinstance(target, list) and 0 <= idx < len(target):
                results.extend(resolve_path(target[idx], rest))
        else:
            if isinstance(obj, dict) and part in obj:
                results.extend(resolve_path(obj[part], rest))
        return results

    parts = req.path.replace("[", ".[").split(".")
    parts = [p for p in parts if p]
    matches = resolve_path(data, parts)
    return {"path": req.path, "matches": matches, "count": len(matches)}


class TemplateRequest(BaseModel):
    template: str
    variables: dict


@app.post("/api/template/render")
async def template_render(req: TemplateRequest):
    """Render a text template with variable substitution. Uses {{variable}} syntax."""
    result = req.template
    for key, value in req.variables.items():
        result = result.replace("{{" + key + "}}", str(value))
    unreplaced = re.findall(r'\{\{(\w+)\}\}', result)
    return {
        "rendered": result,
        "variables_used": list(req.variables.keys()),
        "unreplaced": unreplaced,
    }


class FakeDataRequest(BaseModel):
    type: str = "person"
    count: int = 1
    locale: str = "en"


@app.post("/api/fake/generate")
async def fake_data(req: FakeDataRequest):
    """Generate fake/mock data for testing. Types: person, address, company, email, phone, credit_card, uuid, date, sentence, paragraph, product, url."""
    import random
    import string

    first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Christopher", "Karen"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]
    streets = ["Main St", "Oak Ave", "Cedar Ln", "Elm Dr", "Pine Rd", "Maple Ct", "Birch Way", "1st Ave", "2nd St", "Park Blvd"]
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "Austin"]
    domains = ["gmail.com", "yahoo.com", "outlook.com", "protonmail.com", "example.com", "test.io", "dev.co"]
    companies = ["Acme Corp", "Globex", "Initech", "Umbrella Corp", "Stark Industries", "Wayne Enterprises", "Cyberdyne", "Soylent Corp", "Weyland-Yutani", "Tyrell Corp"]
    tlds = [".com", ".io", ".dev", ".co", ".org", ".net", ".app"]
    products = ["Widget", "Gadget", "Gizmo", "Doohickey", "Thingamajig", "Device", "Module", "Component", "System", "Platform"]
    adjectives = ["Premium", "Ultra", "Pro", "Smart", "Nano", "Mega", "Super", "Quantum", "Hyper", "Elite"]

    count = max(1, min(req.count, 100))
    results = []

    for _ in range(count):
        first = random.choice(first_names)
        last = random.choice(last_names)
        if req.type == "person":
            results.append({
                "first_name": first, "last_name": last,
                "email": f"{first.lower()}.{last.lower()}@{random.choice(domains)}",
                "phone": f"+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}",
                "age": random.randint(18, 85),
                "job": random.choice(["Engineer", "Designer", "Manager", "Analyst", "Developer", "Consultant", "Director", "Scientist"]),
            })
        elif req.type == "address":
            results.append({
                "street": f"{random.randint(100,9999)} {random.choice(streets)}",
                "city": random.choice(cities),
                "state": random.choice(["CA", "NY", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI"]),
                "zip": f"{random.randint(10000, 99999)}",
                "country": "US",
            })
        elif req.type == "company":
            results.append({
                "name": random.choice(companies),
                "industry": random.choice(["Technology", "Finance", "Healthcare", "Education", "Retail", "Manufacturing"]),
                "employees": random.randint(10, 100000),
                "founded": random.randint(1950, 2024),
                "website": f"https://www.{random.choice(companies).lower().replace(' ', '')}{random.choice(tlds)}",
            })
        elif req.type == "email":
            results.append(f"{first.lower()}.{last.lower()}{random.randint(1,999)}@{random.choice(domains)}")
        elif req.type == "phone":
            results.append(f"+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}")
        elif req.type == "credit_card":
            results.append({
                "number": f"4{''.join(str(random.randint(0,9)) for _ in range(15))}",
                "expiry": f"{random.randint(1,12):02d}/{random.randint(25,30)}",
                "cvv": f"{random.randint(100,999)}",
                "type": random.choice(["Visa", "Mastercard", "Amex"]),
            })
        elif req.type == "uuid":
            results.append(str(uuid.uuid4()))
        elif req.type == "date":
            y = random.randint(2000, 2026)
            m = random.randint(1, 12)
            d = random.randint(1, 28)
            results.append(f"{y}-{m:02d}-{d:02d}")
        elif req.type == "product":
            results.append({
                "name": f"{random.choice(adjectives)} {random.choice(products)}",
                "price": round(random.uniform(4.99, 999.99), 2),
                "sku": "".join(random.choices(string.ascii_uppercase + string.digits, k=8)),
                "category": random.choice(["Electronics", "Software", "Hardware", "Accessories", "Services"]),
                "in_stock": random.choice([True, True, True, False]),
            })
        elif req.type == "url":
            results.append(f"https://{''.join(random.choices(string.ascii_lowercase, k=random.randint(5,12)))}{random.choice(tlds)}/{'/'.join(''.join(random.choices(string.ascii_lowercase, k=random.randint(3,8))) for _ in range(random.randint(1,3)))}")
        else:
            words = "lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua".split()
            if req.type == "sentence":
                s = " ".join(random.choice(words) for _ in range(random.randint(8, 20)))
                results.append(s[0].upper() + s[1:] + ".")
            elif req.type == "paragraph":
                sentences = []
                for _ in range(random.randint(3, 8)):
                    s = " ".join(random.choice(words) for _ in range(random.randint(8, 20)))
                    sentences.append(s[0].upper() + s[1:] + ".")
                results.append(" ".join(sentences))
            else:
                results.append(str(uuid.uuid4()))

    return {"type": req.type, "count": len(results), "data": results if count > 1 else results[0]}


class SchemaGenRequest(BaseModel):
    json_data: str


@app.post("/api/json/to-schema")
async def json_to_schema(req: SchemaGenRequest):
    """Generate a JSON Schema from example JSON data. Useful for API documentation and validation."""
    try:
        data = json.loads(req.json_data)
    except json.JSONDecodeError as e:
        raise HTTPException(400, f"Invalid JSON: {e}")

    def infer_schema(obj):
        if obj is None:
            return {"type": "null"}
        if isinstance(obj, bool):
            return {"type": "boolean"}
        if isinstance(obj, int):
            return {"type": "integer"}
        if isinstance(obj, float):
            return {"type": "number"}
        if isinstance(obj, str):
            schema = {"type": "string"}
            if re.match(r'^\d{4}-\d{2}-\d{2}$', obj):
                schema["format"] = "date"
            elif re.match(r'^\d{4}-\d{2}-\d{2}T', obj):
                schema["format"] = "date-time"
            elif re.match(r'^[^@]+@[^@]+\.[^@]+$', obj):
                schema["format"] = "email"
            elif re.match(r'^https?://', obj):
                schema["format"] = "uri"
            return schema
        if isinstance(obj, list):
            if not obj:
                return {"type": "array", "items": {}}
            item_schemas = [infer_schema(item) for item in obj[:10]]
            return {"type": "array", "items": item_schemas[0]}
        if isinstance(obj, dict):
            properties = {}
            required = []
            for k, v in obj.items():
                properties[k] = infer_schema(v)
                required.append(k)
            return {"type": "object", "properties": properties, "required": required}
        return {}

    schema = infer_schema(data)
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    return {"schema": schema, "source_type": type(data).__name__}


class OpenAPIGenRequest(BaseModel):
    name: str = "My API"
    description: str = ""
    endpoints: list


@app.post("/api/openapi/generate")
async def generate_openapi(req: OpenAPIGenRequest):
    """Generate an OpenAPI 3.0 spec from a list of endpoint definitions. Each endpoint: {method, path, summary, request_body, response}."""
    spec = {
        "openapi": "3.0.3",
        "info": {"title": req.name, "description": req.description or f"{req.name} API", "version": "1.0.0"},
        "paths": {},
    }
    for ep in req.endpoints:
        path = ep.get("path", "/unknown")
        method = ep.get("method", "get").lower()
        operation = {
            "summary": ep.get("summary", f"{method.upper()} {path}"),
            "responses": {"200": {"description": "Success"}},
        }
        if ep.get("request_body"):
            operation["requestBody"] = {
                "content": {"application/json": {"schema": {"type": "object"}}},
            }
        if path not in spec["paths"]:
            spec["paths"][path] = {}
        spec["paths"][path][method] = operation
    return {"openapi_spec": spec, "endpoints_count": len(req.endpoints)}


class DataTransformRequest(BaseModel):
    data: str
    operations: list


@app.post("/api/data/transform")
async def data_transform(req: DataTransformRequest):
    """Apply a chain of transformations to data. Operations: sort, filter, map, unique, reverse, flatten, group_by, limit, skip."""
    try:
        data = json.loads(req.data)
    except json.JSONDecodeError as e:
        raise HTTPException(400, f"Invalid JSON: {e}")

    result = data
    applied = []
    for op in req.operations:
        op_type = op.get("type", "")
        try:
            if op_type == "sort" and isinstance(result, list):
                key = op.get("key")
                reverse = op.get("reverse", False)
                if key:
                    result = sorted(result, key=lambda x: x.get(key, "") if isinstance(x, dict) else x, reverse=reverse)
                else:
                    result = sorted(result, reverse=reverse)
                applied.append(f"sort(key={key}, reverse={reverse})")
            elif op_type == "filter" and isinstance(result, list):
                key = op.get("key", "")
                value = op.get("value")
                op_name = op.get("operator", "eq")
                filtered = []
                for item in result:
                    v = item.get(key) if isinstance(item, dict) else item
                    if op_name == "eq" and v == value:
                        filtered.append(item)
                    elif op_name == "ne" and v != value:
                        filtered.append(item)
                    elif op_name == "gt" and v is not None and v > value:
                        filtered.append(item)
                    elif op_name == "lt" and v is not None and v < value:
                        filtered.append(item)
                    elif op_name == "contains" and isinstance(v, str) and str(value) in v:
                        filtered.append(item)
                result = filtered
                applied.append(f"filter({key} {op_name} {value})")
            elif op_type == "unique" and isinstance(result, list):
                seen = set()
                unique = []
                key = op.get("key")
                for item in result:
                    v = item.get(key) if isinstance(item, dict) and key else json.dumps(item, sort_keys=True)
                    if str(v) not in seen:
                        seen.add(str(v))
                        unique.append(item)
                result = unique
                applied.append("unique")
            elif op_type == "reverse" and isinstance(result, list):
                result = list(reversed(result))
                applied.append("reverse")
            elif op_type == "flatten" and isinstance(result, list):
                flat = []
                for item in result:
                    if isinstance(item, list):
                        flat.extend(item)
                    else:
                        flat.append(item)
                result = flat
                applied.append("flatten")
            elif op_type == "limit" and isinstance(result, list):
                n = op.get("n", 10)
                result = result[:n]
                applied.append(f"limit({n})")
            elif op_type == "skip" and isinstance(result, list):
                n = op.get("n", 0)
                result = result[n:]
                applied.append(f"skip({n})")
            elif op_type == "group_by" and isinstance(result, list):
                key = op.get("key", "")
                groups = {}
                for item in result:
                    gk = str(item.get(key, "other")) if isinstance(item, dict) else str(item)
                    groups.setdefault(gk, []).append(item)
                result = groups
                applied.append(f"group_by({key})")
        except Exception as e:
            applied.append(f"ERROR: {op_type}: {e}")

    return {"result": result, "operations_applied": applied, "result_type": type(result).__name__}


class EnvGenRequest(BaseModel):
    variables: dict
    format: str = "dotenv"


@app.post("/api/env/generate")
async def env_generate(req: EnvGenRequest):
    """Generate environment variable files from a dict. Formats: dotenv, docker, yaml, json, shell."""
    lines = []
    if req.format == "dotenv":
        for k, v in req.variables.items():
            v_str = str(v)
            if " " in v_str or '"' in v_str:
                v_str = f'"{v_str}"'
            lines.append(f"{k}={v_str}")
        return {"output": "\n".join(lines), "format": "dotenv", "count": len(req.variables)}
    elif req.format == "docker":
        for k, v in req.variables.items():
            lines.append(f"ENV {k}={v}")
        return {"output": "\n".join(lines), "format": "Dockerfile", "count": len(req.variables)}
    elif req.format == "yaml":
        for k, v in req.variables.items():
            lines.append(f"  {k}: \"{v}\"")
        output = "env:\n" + "\n".join(lines)
        return {"output": output, "format": "yaml", "count": len(req.variables)}
    elif req.format == "shell":
        for k, v in req.variables.items():
            lines.append(f"export {k}=\"{v}\"")
        return {"output": "\n".join(lines), "format": "shell", "count": len(req.variables)}
    else:
        return {"output": json.dumps(req.variables, indent=2), "format": "json", "count": len(req.variables)}


class GitIgnoreRequest(BaseModel):
    languages: list
    extras: list = []


@app.post("/api/gitignore/generate")
async def gitignore_generate(req: GitIgnoreRequest):
    """Generate a .gitignore file for specified languages/frameworks."""
    templates = {
        "python": ["__pycache__/", "*.py[cod]", "*$py.class", "*.so", ".Python", "env/", "venv/", ".env", "*.egg-info/", "dist/", "build/", ".pytest_cache/", ".mypy_cache/"],
        "node": ["node_modules/", "npm-debug.log*", "yarn-debug.log*", ".env", "dist/", "build/", ".next/", ".nuxt/", "coverage/", "*.tsbuildinfo"],
        "java": ["*.class", "*.jar", "*.war", "*.ear", "target/", ".gradle/", "build/", ".idea/", "*.iml"],
        "go": ["*.exe", "*.test", "*.out", "vendor/", ".env"],
        "rust": ["target/", "Cargo.lock", "*.pdb"],
        "ruby": ["*.gem", ".bundle/", "vendor/bundle", ".env", "log/", "tmp/", "coverage/"],
        "swift": [".build/", "Packages/", "*.xcodeproj/", "DerivedData/", ".swiftpm/"],
        "docker": [".env", "docker-compose.override.yml", "*.log"],
        "general": [".DS_Store", "Thumbs.db", "*.swp", "*.swo", "*~", ".vscode/", ".idea/", "*.log", ".env", ".env.local"],
    }

    lines = ["# Generated by ToolPipe .gitignore Generator", ""]
    for lang in req.languages:
        lang_lower = lang.lower()
        if lang_lower in templates:
            lines.append(f"# {lang}")
            lines.extend(templates[lang_lower])
            lines.append("")

    if req.extras:
        lines.append("# Custom")
        lines.extend(req.extras)
        lines.append("")

    output = "\n".join(lines)
    return {"gitignore": output, "languages": req.languages, "total_rules": sum(1 for l in lines if l and not l.startswith("#"))}


class DockerfileRequest(BaseModel):
    language: str
    framework: str = ""
    port: int = 8080


@app.post("/api/dockerfile/generate")
async def dockerfile_generate(req: DockerfileRequest):
    """Generate a Dockerfile for common language/framework combos."""
    templates = {
        "python": f"""FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE {req.port}
CMD ["python", "main.py"]""",
        "node": f"""FROM node:20-slim
WORKDIR /app
COPY package*.json .
RUN npm ci --only=production
COPY . .
EXPOSE {req.port}
CMD ["node", "index.js"]""",
        "go": f"""FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.* .
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /server .

FROM alpine:3.19
COPY --from=builder /server /server
EXPOSE {req.port}
CMD ["/server"]""",
        "rust": f"""FROM rust:1.77-slim AS builder
WORKDIR /app
COPY . .
RUN cargo build --release

FROM debian:bookworm-slim
COPY --from=builder /app/target/release/app /app
EXPOSE {req.port}
CMD ["/app"]""",
        "java": f"""FROM eclipse-temurin:21-jdk-jammy AS builder
WORKDIR /app
COPY . .
RUN ./gradlew build -x test

FROM eclipse-temurin:21-jre-jammy
COPY --from=builder /app/build/libs/*.jar /app.jar
EXPOSE {req.port}
CMD ["java", "-jar", "/app.jar"]""",
    }

    lang = req.language.lower()
    if lang == "python" and req.framework == "fastapi":
        dockerfile = templates["python"].replace('CMD ["python", "main.py"]', f'CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "{req.port}"]')
    elif lang == "python" and req.framework == "flask":
        dockerfile = templates["python"].replace('CMD ["python", "main.py"]', f'CMD ["gunicorn", "--bind", "0.0.0.0:{req.port}", "app:app"]')
    elif lang == "node" and req.framework in ("next", "nextjs"):
        dockerfile = templates["node"].replace('CMD ["node", "index.js"]', f'RUN npm run build\nCMD ["npm", "start"]')
    elif lang in templates:
        dockerfile = templates[lang]
    else:
        dockerfile = f"# Dockerfile for {req.language}\n# Framework: {req.framework or 'none specified'}\nFROM ubuntu:22.04\nWORKDIR /app\nCOPY . .\nEXPOSE {req.port}\nCMD [\"./start.sh\"]"

    return {"dockerfile": dockerfile, "language": req.language, "framework": req.framework or "default", "port": req.port}


# --- High-Value AI Agent Endpoints ---

class WebExtractRequest(BaseModel):
    url: str
    extract: str = "text"  # text, links, images, metadata, structured


@app.post("/api/web/extract")
async def web_extract(req: WebExtractRequest):
    """Extract content from any web page: text, links, images, metadata, or structured data.
    This is a premium tool for AI agents that need to process web content."""
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(req.url, headers={"User-Agent": "ToolPipe/1.0 (API; +https://toolpipe.dev)"})
            html = resp.text
    except Exception as e:
        raise HTTPException(400, f"Failed to fetch URL: {e}")

    soup = BeautifulSoup(html, "html.parser")

    if req.extract == "text":
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        text = soup.get_text(separator="\n", strip=True)
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        return {"url": req.url, "text": "\n".join(lines[:500]), "word_count": len(" ".join(lines).split())}

    elif req.extract == "links":
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("http"):
                links.append({"url": href, "text": a.get_text(strip=True)[:100]})
        return {"url": req.url, "links": links[:200], "count": len(links)}

    elif req.extract == "images":
        images = []
        for img in soup.find_all("img", src=True):
            images.append({"src": img["src"], "alt": img.get("alt", ""), "width": img.get("width"), "height": img.get("height")})
        return {"url": req.url, "images": images[:100], "count": len(images)}

    elif req.extract == "metadata":
        meta = {}
        for tag in soup.find_all("meta"):
            name = tag.get("name", tag.get("property", ""))
            content = tag.get("content", "")
            if name and content:
                meta[name] = content
        title = soup.find("title")
        meta["title"] = title.get_text(strip=True) if title else ""
        return {"url": req.url, "metadata": meta}

    elif req.extract == "structured":
        result = {"title": "", "description": "", "headings": [], "paragraphs": [], "lists": []}
        title = soup.find("title")
        result["title"] = title.get_text(strip=True) if title else ""
        desc = soup.find("meta", {"name": "description"})
        result["description"] = desc.get("content", "") if desc else ""
        for h in soup.find_all(["h1", "h2", "h3", "h4"]):
            result["headings"].append({"level": h.name, "text": h.get_text(strip=True)})
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if len(text) > 20:
                result["paragraphs"].append(text[:500])
        for ul in soup.find_all(["ul", "ol"]):
            items = [li.get_text(strip=True)[:200] for li in ul.find_all("li")]
            if items:
                result["lists"].append(items[:20])
        return {"url": req.url, "structured": result}

    return {"error": "Invalid extract type. Use: text, links, images, metadata, structured"}


class CodeAnalyzeRequest(BaseModel):
    code: str
    language: str = "auto"


@app.post("/api/code/analyze")
async def code_analyze(req: CodeAnalyzeRequest):
    """Analyze code: detect language, count lines, find functions/classes, measure complexity."""
    code = req.code
    lines = code.split("\n")
    total_lines = len(lines)
    blank_lines = sum(1 for l in lines if not l.strip())
    comment_lines = sum(1 for l in lines if l.strip().startswith(("#", "//", "/*", "*", "<!--")))
    code_lines = total_lines - blank_lines - comment_lines

    # Detect language
    lang = req.language.lower() if req.language != "auto" else "unknown"
    if lang == "unknown":
        if "def " in code and "import " in code:
            lang = "python"
        elif "function " in code or "const " in code or "=>" in code:
            lang = "javascript"
        elif "func " in code and "package " in code:
            lang = "go"
        elif "fn " in code and "let " in code:
            lang = "rust"
        elif "class " in code and "public " in code:
            lang = "java"
        elif "struct " in code and "#include" in code:
            lang = "c/c++"
        elif "<html" in code.lower() or "<!doctype" in code.lower():
            lang = "html"

    # Extract functions/classes
    functions = []
    classes = []
    imports = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if lang == "python":
            if stripped.startswith("def "):
                name = stripped.split("(")[0].replace("def ", "")
                functions.append({"name": name, "line": i + 1})
            elif stripped.startswith("class "):
                name = stripped.split("(")[0].split(":")[0].replace("class ", "")
                classes.append({"name": name, "line": i + 1})
            elif stripped.startswith("import ") or stripped.startswith("from "):
                imports.append(stripped)
        elif lang in ("javascript", "typescript"):
            if "function " in stripped:
                match = re.search(r"function\s+(\w+)", stripped)
                if match:
                    functions.append({"name": match.group(1), "line": i + 1})
            elif stripped.startswith("class "):
                match = re.search(r"class\s+(\w+)", stripped)
                if match:
                    classes.append({"name": match.group(1), "line": i + 1})
            elif stripped.startswith("import "):
                imports.append(stripped)
        elif lang == "go":
            if stripped.startswith("func "):
                match = re.search(r"func\s+(?:\([^)]+\)\s+)?(\w+)", stripped)
                if match:
                    functions.append({"name": match.group(1), "line": i + 1})

    # Complexity estimate (based on branching)
    branches = sum(1 for l in lines if any(kw in l for kw in ["if ", "elif ", "else:", "for ", "while ", "switch ", "case ", "catch "]))

    return {
        "language": lang,
        "metrics": {
            "total_lines": total_lines,
            "code_lines": code_lines,
            "blank_lines": blank_lines,
            "comment_lines": comment_lines,
            "avg_line_length": round(sum(len(l) for l in lines) / max(total_lines, 1), 1),
            "max_line_length": max(len(l) for l in lines) if lines else 0,
        },
        "structure": {
            "functions": functions[:50],
            "classes": classes[:50],
            "imports": imports[:30],
            "function_count": len(functions),
            "class_count": len(classes),
        },
        "complexity": {
            "branch_count": branches,
            "estimated_cyclomatic": branches + 1,
            "nesting_depth": max((len(l) - len(l.lstrip())) // 4 for l in lines if l.strip()) if lines else 0,
        },
    }


class SchemaGenRequest(BaseModel):
    data: str
    format: str = "typescript"  # typescript, python, zod, jsonschema


@app.post("/api/schema/generate")
async def schema_generate(req: SchemaGenRequest):
    """Generate type definitions from JSON data. Supports TypeScript, Python, Zod, JSON Schema."""
    try:
        data = json.loads(req.data)
    except json.JSONDecodeError as e:
        raise HTTPException(400, f"Invalid JSON: {e}")

    def infer_type(value, name="Root", depth=0):
        if isinstance(value, bool):
            return {"type": "boolean", "ts": "boolean", "py": "bool", "zod": "z.boolean()"}
        elif isinstance(value, int):
            return {"type": "integer", "ts": "number", "py": "int", "zod": "z.number().int()"}
        elif isinstance(value, float):
            return {"type": "number", "ts": "number", "py": "float", "zod": "z.number()"}
        elif isinstance(value, str):
            return {"type": "string", "ts": "string", "py": "str", "zod": "z.string()"}
        elif value is None:
            return {"type": "null", "ts": "null", "py": "None", "zod": "z.null()"}
        elif isinstance(value, list):
            if not value:
                return {"type": "array", "ts": "any[]", "py": "list", "zod": "z.array(z.any())"}
            item_type = infer_type(value[0], name + "Item", depth + 1)
            return {"type": "array", "ts": f"{item_type['ts']}[]", "py": f"list[{item_type['py']}]", "zod": f"z.array({item_type['zod']})"}
        elif isinstance(value, dict):
            fields = {}
            for k, v in value.items():
                fields[k] = infer_type(v, k.title().replace("_", ""), depth + 1)
            return {"type": "object", "fields": fields, "name": name}
        return {"type": "unknown", "ts": "any", "py": "Any", "zod": "z.any()"}

    schema = infer_type(data)

    if req.format == "typescript":
        def to_ts(s, indent=0):
            if s["type"] == "object":
                lines = [f"{'  ' * indent}interface {s.get('name', 'Root')} {{"]
                for k, v in s.get("fields", {}).items():
                    if v["type"] == "object":
                        lines.append(f"{'  ' * (indent+1)}{k}: {{")
                        for k2, v2 in v.get("fields", {}).items():
                            lines.append(f"{'  ' * (indent+2)}{k2}: {v2.get('ts', 'any')};")
                        lines.append(f"{'  ' * (indent+1)}}};")
                    else:
                        lines.append(f"{'  ' * (indent+1)}{k}: {v.get('ts', 'any')};")
                lines.append(f"{'  ' * indent}}}")
                return "\n".join(lines)
            return f"type Root = {s.get('ts', 'any')};"
        output = to_ts(schema)
    elif req.format == "python":
        def to_py(s, indent=0):
            if s["type"] == "object":
                lines = [f"{'  ' * indent}class {s.get('name', 'Root')}(BaseModel):"]
                for k, v in s.get("fields", {}).items():
                    if v["type"] == "object":
                        lines.append(to_py(v, indent + 1))
                        lines.append(f"{'  ' * (indent+1)}{k}: {v.get('name', 'Dict')}")
                    else:
                        lines.append(f"{'  ' * (indent+1)}{k}: {v.get('py', 'Any')}")
                return "\n".join(lines)
            return f"Root = {s.get('py', 'Any')}"
        output = "from pydantic import BaseModel\n\n" + to_py(schema)
    elif req.format == "zod":
        def to_zod(s):
            if s["type"] == "object":
                fields = []
                for k, v in s.get("fields", {}).items():
                    if v["type"] == "object":
                        fields.append(f"  {k}: {to_zod(v)}")
                    else:
                        fields.append(f"  {k}: {v.get('zod', 'z.any()')}")
                return "z.object({\n" + ",\n".join(fields) + "\n})"
            return s.get("zod", "z.any()")
        output = f'import {{ z }} from "zod";\n\nconst Schema = {to_zod(schema)};'
    else:
        # JSON Schema
        def to_jsonschema(s):
            if s["type"] == "object":
                props = {}
                required = []
                for k, v in s.get("fields", {}).items():
                    if v["type"] == "object":
                        props[k] = to_jsonschema(v)
                    elif v["type"] == "array":
                        props[k] = {"type": "array"}
                    else:
                        props[k] = {"type": v["type"]}
                    required.append(k)
                return {"type": "object", "properties": props, "required": required}
            return {"type": s["type"]}
        output = json.dumps(to_jsonschema(schema), indent=2)

    return {"schema": output, "format": req.format, "detected_type": schema["type"]}


class PromptTemplateRequest(BaseModel):
    template: str
    variables: dict = {}
    system: str = ""


@app.post("/api/prompt/build")
async def prompt_build(req: PromptTemplateRequest):
    """Build structured prompts for LLMs. Supports variable substitution, system/user separation, and template rendering."""
    prompt = req.template
    for key, value in req.variables.items():
        prompt = prompt.replace(f"{{{{{key}}}}}", str(value))
        prompt = prompt.replace(f"${{{key}}}", str(value))

    # Count tokens (rough estimate: 1 token per 4 chars)
    total_chars = len(prompt) + len(req.system)
    estimated_tokens = total_chars // 4

    messages = []
    if req.system:
        system = req.system
        for key, value in req.variables.items():
            system = system.replace(f"{{{{{key}}}}}", str(value))
            system = system.replace(f"${{{key}}}", str(value))
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    return {
        "messages": messages,
        "prompt": prompt,
        "system": messages[0]["content"] if req.system else None,
        "estimated_tokens": estimated_tokens,
        "variables_used": list(req.variables.keys()),
    }


class ApiTestRequest(BaseModel):
    url: str
    method: str = "GET"
    headers: dict = {}
    body: str = ""
    timeout: int = 10


@app.post("/api/test/endpoint")
async def test_endpoint(req: ApiTestRequest):
    """Test any API endpoint and get detailed response metrics. Useful for monitoring, debugging, and validation."""
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=req.timeout, follow_redirects=True) as client:
            kwargs = {"headers": req.headers}
            if req.body:
                kwargs["content"] = req.body
                if "Content-Type" not in req.headers:
                    kwargs["headers"]["Content-Type"] = "application/json"

            resp = await getattr(client, req.method.lower())(req.url, **kwargs)
            elapsed = round((time.time() - start) * 1000, 2)

            # Try to parse response
            content_type = resp.headers.get("content-type", "")
            body = resp.text[:5000]
            is_json = False
            try:
                body = resp.json()
                is_json = True
            except Exception:
                pass

            return {
                "url": req.url,
                "method": req.method,
                "status_code": resp.status_code,
                "response_time_ms": elapsed,
                "headers": dict(resp.headers),
                "body": body,
                "is_json": is_json,
                "content_length": len(resp.content),
                "content_type": content_type,
                "redirected": len(resp.history) > 0,
                "redirect_count": len(resp.history),
            }
    except httpx.TimeoutException:
        elapsed = round((time.time() - start) * 1000, 2)
        return {"url": req.url, "error": "timeout", "response_time_ms": elapsed}
    except Exception as e:
        elapsed = round((time.time() - start) * 1000, 2)
        return {"url": req.url, "error": str(e), "response_time_ms": elapsed}


class CompareTextRequest(BaseModel):
    text1: str
    text2: str


@app.post("/api/text/similarity")
async def text_similarity(req: CompareTextRequest):
    """Calculate text similarity using multiple algorithms: Jaccard, cosine (word-level), Levenshtein ratio."""
    words1 = set(req.text1.lower().split())
    words2 = set(req.text2.lower().split())

    # Jaccard similarity
    intersection = words1 & words2
    union = words1 | words2
    jaccard = len(intersection) / len(union) if union else 0

    # Cosine similarity (word frequency)
    all_words = list(union)
    freq1 = [req.text1.lower().split().count(w) for w in all_words]
    freq2 = [req.text2.lower().split().count(w) for w in all_words]
    dot = sum(a * b for a, b in zip(freq1, freq2))
    mag1 = sum(a * a for a in freq1) ** 0.5
    mag2 = sum(b * b for b in freq2) ** 0.5
    cosine = dot / (mag1 * mag2) if mag1 and mag2 else 0

    # Levenshtein ratio (character level, limited to avoid O(n^2) on huge texts)
    s1 = req.text1[:1000]
    s2 = req.text2[:1000]
    len1, len2 = len(s1), len(s2)
    if max(len1, len2) == 0:
        lev_ratio = 1.0
    else:
        # Simple ratio based on common prefix/suffix + length
        common = sum(1 for a, b in zip(s1, s2) if a == b)
        lev_ratio = common / max(len1, len2)

    return {
        "jaccard_similarity": round(jaccard, 4),
        "cosine_similarity": round(cosine, 4),
        "character_similarity": round(lev_ratio, 4),
        "average_similarity": round((jaccard + cosine + lev_ratio) / 3, 4),
        "common_words": sorted(list(intersection))[:50],
        "unique_to_text1": sorted(list(words1 - words2))[:50],
        "unique_to_text2": sorted(list(words2 - words1))[:50],
    }


# --- IP Geolocation Lookup ---

class IPLookupRequest(BaseModel):
    ip: str

@app.post("/api/ip/lookup")
@app.get("/api/ip/lookup")
async def ip_lookup(request: Request, req: Optional[IPLookupRequest] = None):
    """Look up geolocation, ISP, and network info for any IP address."""
    if request.method == "GET":
        ip = request.query_params.get("ip", "")
    else:
        ip = req.ip if req else ""

    if not ip:
        return JSONResponse({"error": "ip parameter required"}, status_code=400)

    # Validate IP format
    import ipaddress
    try:
        addr = ipaddress.ip_address(ip)
        is_private = addr.is_private
        is_loopback = addr.is_loopback
        is_multicast = addr.is_multicast
        version = addr.version
    except ValueError:
        return JSONResponse({"error": "Invalid IP address"}, status_code=400)

    result = {
        "ip": ip,
        "version": f"IPv{version}",
        "is_private": is_private,
        "is_loopback": is_loopback,
        "is_multicast": is_multicast,
    }

    # Try free geolocation API
    if not is_private and not is_loopback:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as")
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("status") == "success":
                        result.update({
                            "country": data.get("country"),
                            "country_code": data.get("countryCode"),
                            "region": data.get("regionName"),
                            "city": data.get("city"),
                            "zip": data.get("zip"),
                            "latitude": data.get("lat"),
                            "longitude": data.get("lon"),
                            "timezone": data.get("timezone"),
                            "isp": data.get("isp"),
                            "org": data.get("org"),
                            "as_number": data.get("as"),
                        })
        except Exception:
            pass

    return result


# --- Cron Expression Parser ---

class CronParseRequest(BaseModel):
    expression: str
    count: int = 5

@app.post("/api/cron/parse")
@app.get("/api/cron/parse")
async def cron_parse(request: Request, req: Optional[CronParseRequest] = None):
    """Parse and explain a cron expression, show next N scheduled times."""
    if request.method == "GET":
        expression = request.query_params.get("expression", "")
        count = int(request.query_params.get("count", "5"))
    else:
        expression = req.expression if req else ""
        count = req.count if req else 5

    if not expression:
        return JSONResponse({"error": "expression parameter required"}, status_code=400)

    parts = expression.strip().split()
    if len(parts) not in (5, 6, 7):
        return JSONResponse({"error": "Invalid cron expression. Expected 5-7 fields."}, status_code=400)

    field_names = ["minute", "hour", "day_of_month", "month", "day_of_week"]
    if len(parts) >= 6:
        field_names.append("year")
    if len(parts) >= 7:
        field_names.insert(5, "second")

    fields = {}
    for i, name in enumerate(field_names):
        if i < len(parts):
            fields[name] = parts[i]

    # Generate human-readable description
    descriptions = []
    minute = fields.get("minute", "*")
    hour = fields.get("hour", "*")
    dom = fields.get("day_of_month", "*")
    month = fields.get("month", "*")
    dow = fields.get("day_of_week", "*")

    if expression.strip() == "* * * * *":
        descriptions.append("Every minute")
    elif minute != "*" and hour != "*" and dom == "*" and month == "*" and dow == "*":
        descriptions.append(f"At {hour.zfill(2)}:{minute.zfill(2)} every day")
    elif minute == "0" and hour == "*":
        descriptions.append("Every hour at minute 0")
    elif minute.startswith("*/"):
        descriptions.append(f"Every {minute[2:]} minutes")
    elif hour.startswith("*/"):
        descriptions.append(f"Every {hour[2:]} hours at minute {minute}")
    elif dow != "*" and dom == "*":
        day_map = {"0": "Sunday", "1": "Monday", "2": "Tuesday", "3": "Wednesday", "4": "Thursday", "5": "Friday", "6": "Saturday", "7": "Sunday"}
        day_name = day_map.get(dow, dow)
        descriptions.append(f"At {hour.zfill(2)}:{minute.zfill(2)} every {day_name}")
    else:
        descriptions.append(f"minute={minute} hour={hour} day={dom} month={month} weekday={dow}")

    # Calculate next run times (simple approximation)
    from datetime import timedelta
    now = datetime.now(timezone.utc)
    next_times = []

    def matches_field(value, field_str, max_val):
        if field_str == "*":
            return True
        if field_str.startswith("*/"):
            step = int(field_str[2:])
            return value % step == 0
        if "," in field_str:
            return value in [int(v) for v in field_str.split(",")]
        if "-" in field_str:
            low, high = field_str.split("-")
            return int(low) <= value <= int(high)
        return value == int(field_str)

    check_time = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
    attempts = 0
    while len(next_times) < min(count, 10) and attempts < 525960:  # max 1 year of minutes
        if (matches_field(check_time.minute, minute, 59) and
            matches_field(check_time.hour, hour, 23) and
            matches_field(check_time.day, dom, 31) and
            matches_field(check_time.month, month, 12) and
            matches_field(check_time.isoweekday() % 7, dow, 6)):
            next_times.append(check_time.isoformat())
        check_time += timedelta(minutes=1)
        attempts += 1

    return {
        "expression": expression,
        "fields": fields,
        "description": " ".join(descriptions),
        "is_valid": True,
        "next_runs": next_times,
    }


# --- Text Diff Tool ---

class DiffRequest(BaseModel):
    original: str
    modified: str
    context_lines: int = 3

@app.post("/api/diff/text")
async def text_diff(req: DiffRequest):
    """Generate a unified diff between two text inputs."""
    import difflib

    original_lines = req.original.splitlines(keepends=True)
    modified_lines = req.modified.splitlines(keepends=True)

    diff = list(difflib.unified_diff(
        original_lines, modified_lines,
        fromfile="original", tofile="modified",
        n=req.context_lines
    ))

    # Stats
    added = sum(1 for line in diff if line.startswith("+") and not line.startswith("+++"))
    removed = sum(1 for line in diff if line.startswith("-") and not line.startswith("---"))

    return {
        "diff": "".join(diff),
        "stats": {
            "lines_added": added,
            "lines_removed": removed,
            "lines_changed": min(added, removed),
            "original_lines": len(original_lines),
            "modified_lines": len(modified_lines),
        },
        "has_changes": len(diff) > 0,
    }


# --- JWT Decoder ---

class JWTDecodeRequest(BaseModel):
    token: str

@app.post("/api/jwt/decode")
async def jwt_decode(req: JWTDecodeRequest):
    """Decode a JWT token without verification (inspect header and payload)."""
    parts = req.token.strip().split(".")
    if len(parts) not in (2, 3):
        return JSONResponse({"error": "Invalid JWT format. Expected 2 or 3 parts separated by dots."}, status_code=400)

    def decode_part(part):
        # Add padding
        padding = 4 - len(part) % 4
        if padding != 4:
            part += "=" * padding
        try:
            decoded = base64.urlsafe_b64decode(part)
            return json.loads(decoded)
        except Exception:
            return None

    header = decode_part(parts[0])
    payload = decode_part(parts[1]) if len(parts) > 1 else None

    result = {
        "header": header,
        "payload": payload,
        "has_signature": len(parts) == 3,
        "parts_count": len(parts),
    }

    # Check expiration if present
    if payload and isinstance(payload, dict):
        exp = payload.get("exp")
        iat = payload.get("iat")
        nbf = payload.get("nbf")
        now_ts = int(time.time())

        if exp:
            result["expired"] = now_ts > exp
            result["expires_at"] = datetime.fromtimestamp(exp, tz=timezone.utc).isoformat()
        if iat:
            result["issued_at"] = datetime.fromtimestamp(iat, tz=timezone.utc).isoformat()
        if nbf:
            result["not_before"] = datetime.fromtimestamp(nbf, tz=timezone.utc).isoformat()

    return result


# --- Timestamp Converter ---

class TimestampRequest(BaseModel):
    timestamp: Optional[str] = None
    format: str = "all"

@app.post("/api/time/convert")
@app.get("/api/time/convert")
async def time_convert(request: Request, req: Optional[TimestampRequest] = None):
    """Convert between Unix timestamps, ISO 8601, and human-readable formats. Pass no timestamp to get current time."""
    if request.method == "GET":
        ts_input = request.query_params.get("timestamp", None)
    else:
        ts_input = req.timestamp if req else None

    now = datetime.now(timezone.utc)

    if ts_input is None or ts_input == "":
        dt = now
    else:
        ts_input = ts_input.strip()
        dt = None

        # Try Unix timestamp (seconds)
        try:
            ts_float = float(ts_input)
            if ts_float > 1e12:  # milliseconds
                dt = datetime.fromtimestamp(ts_float / 1000, tz=timezone.utc)
            else:
                dt = datetime.fromtimestamp(ts_float, tz=timezone.utc)
        except (ValueError, OverflowError, OSError):
            pass

        # Try ISO format
        if dt is None:
            try:
                dt = datetime.fromisoformat(ts_input.replace("Z", "+00:00"))
            except ValueError:
                pass

        # Try common formats
        if dt is None:
            for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y", "%d/%m/%Y", "%B %d, %Y"]:
                try:
                    dt = datetime.strptime(ts_input, fmt).replace(tzinfo=timezone.utc)
                    break
                except ValueError:
                    continue

        if dt is None:
            return JSONResponse({"error": f"Could not parse timestamp: {ts_input}"}, status_code=400)

    unix_s = int(dt.timestamp())
    unix_ms = int(dt.timestamp() * 1000)

    return {
        "input": ts_input,
        "unix_seconds": unix_s,
        "unix_milliseconds": unix_ms,
        "iso8601": dt.isoformat(),
        "utc": dt.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "date": dt.strftime("%Y-%m-%d"),
        "time": dt.strftime("%H:%M:%S"),
        "day_of_week": dt.strftime("%A"),
        "day_of_year": dt.timetuple().tm_yday,
        "week_number": dt.isocalendar()[1],
        "relative_to_now": f"{abs((now - dt).total_seconds()):.0f} seconds {'ago' if dt < now else 'from now'}",
    }


# --- HTTP Header Analyzer ---

@app.get("/api/headers/analyze")
async def headers_analyze(url: str = Query(...)):
    """Analyze HTTP response headers of any URL for security, caching, and configuration."""
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            resp = await client.head(url)
    except Exception as e:
        return JSONResponse({"error": f"Failed to fetch URL: {str(e)}"}, status_code=400)

    headers = dict(resp.headers)

    # Security analysis
    security = {
        "has_hsts": "strict-transport-security" in headers,
        "has_csp": "content-security-policy" in headers,
        "has_x_frame_options": "x-frame-options" in headers,
        "has_x_content_type_options": "x-content-type-options" in headers,
        "has_referrer_policy": "referrer-policy" in headers,
        "has_permissions_policy": "permissions-policy" in headers,
    }
    security["score"] = sum(1 for v in security.values() if v)
    security["max_score"] = 6
    security["grade"] = "A" if security["score"] >= 5 else "B" if security["score"] >= 3 else "C" if security["score"] >= 1 else "F"

    # Caching analysis
    caching = {
        "cache_control": headers.get("cache-control"),
        "expires": headers.get("expires"),
        "etag": headers.get("etag"),
        "last_modified": headers.get("last-modified"),
        "age": headers.get("age"),
    }

    return {
        "url": url,
        "status_code": resp.status_code,
        "headers": headers,
        "security": security,
        "caching": caching,
        "server": headers.get("server"),
        "content_type": headers.get("content-type"),
        "redirect_count": len(resp.history),
    }


# --- Password Strength Checker ---

class PasswordCheckRequest(BaseModel):
    password: str

@app.post("/api/password/check")
async def password_check(req: PasswordCheckRequest):
    """Check password strength and provide improvement suggestions."""
    pwd = req.password
    length = len(pwd)

    checks = {
        "length_ok": length >= 8,
        "has_uppercase": bool(re.search(r"[A-Z]", pwd)),
        "has_lowercase": bool(re.search(r"[a-z]", pwd)),
        "has_digit": bool(re.search(r"\d", pwd)),
        "has_special": bool(re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", pwd)),
        "no_common_patterns": not bool(re.search(r"(123|abc|password|qwerty|admin|letmein|welcome|monkey|dragon)", pwd.lower())),
        "length_good": length >= 12,
        "length_excellent": length >= 16,
    }

    score = sum([
        min(length, 20) * 2,  # Up to 40 points for length
        10 if checks["has_uppercase"] else 0,
        10 if checks["has_lowercase"] else 0,
        10 if checks["has_digit"] else 0,
        15 if checks["has_special"] else 0,
        15 if checks["no_common_patterns"] else -20,
    ])
    score = max(0, min(100, score))

    if score >= 80:
        strength = "strong"
    elif score >= 60:
        strength = "good"
    elif score >= 40:
        strength = "fair"
    else:
        strength = "weak"

    suggestions = []
    if not checks["length_ok"]:
        suggestions.append("Use at least 8 characters")
    if not checks["length_good"]:
        suggestions.append("Consider using 12+ characters for better security")
    if not checks["has_uppercase"]:
        suggestions.append("Add uppercase letters")
    if not checks["has_lowercase"]:
        suggestions.append("Add lowercase letters")
    if not checks["has_digit"]:
        suggestions.append("Add numbers")
    if not checks["has_special"]:
        suggestions.append("Add special characters (!@#$%^&*)")
    if not checks["no_common_patterns"]:
        suggestions.append("Avoid common words and patterns")

    # Entropy estimation (bits)
    charset_size = 0
    if checks["has_lowercase"]:
        charset_size += 26
    if checks["has_uppercase"]:
        charset_size += 26
    if checks["has_digit"]:
        charset_size += 10
    if checks["has_special"]:
        charset_size += 32
    if charset_size == 0:
        charset_size = 26

    import math
    entropy = length * math.log2(charset_size)

    return {
        "score": score,
        "strength": strength,
        "length": length,
        "checks": checks,
        "suggestions": suggestions,
        "entropy_bits": round(entropy, 1),
        "crack_time_estimate": "centuries" if entropy > 80 else "years" if entropy > 60 else "months" if entropy > 40 else "days" if entropy > 28 else "minutes",
    }


# --- Regex Tester ---

class RegexTestRequest(BaseModel):
    pattern: str
    text: str
    flags: str = ""

@app.post("/api/regex/test")
async def regex_test(req: RegexTestRequest):
    """Test a regex pattern against text and return all matches with groups and positions."""
    flag_map = {"i": re.IGNORECASE, "m": re.MULTILINE, "s": re.DOTALL}
    flags = 0
    for f in req.flags:
        if f in flag_map:
            flags |= flag_map[f]

    try:
        compiled = re.compile(req.pattern, flags)
    except re.error as e:
        return JSONResponse({"error": f"Invalid regex: {str(e)}"}, status_code=400)

    matches = []
    for m in compiled.finditer(req.text):
        match_info = {
            "match": m.group(),
            "start": m.start(),
            "end": m.end(),
            "groups": list(m.groups()),
        }
        if m.groupdict():
            match_info["named_groups"] = m.groupdict()
        matches.append(match_info)
        if len(matches) >= 100:
            break

    return {
        "pattern": req.pattern,
        "flags": req.flags,
        "is_valid": True,
        "match_count": len(matches),
        "matches": matches,
        "text_length": len(req.text),
    }


# --- Lorem Ipsum Generator ---

@app.get("/api/lorem")
async def lorem_ipsum(
    paragraphs: int = Query(3, ge=1, le=20),
    sentences_per_paragraph: int = Query(5, ge=1, le=15),
    format: str = Query("text"),
):
    """Generate lorem ipsum placeholder text."""
    words = [
        "lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit",
        "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore", "et", "dolore",
        "magna", "aliqua", "enim", "ad", "minim", "veniam", "quis", "nostrud",
        "exercitation", "ullamco", "laboris", "nisi", "aliquip", "ex", "ea", "commodo",
        "consequat", "duis", "aute", "irure", "in", "reprehenderit", "voluptate",
        "velit", "esse", "cillum", "fugiat", "nulla", "pariatur", "excepteur", "sint",
        "occaecat", "cupidatat", "non", "proident", "sunt", "culpa", "qui", "officia",
        "deserunt", "mollit", "anim", "id", "est", "laborum", "at", "vero", "eos",
        "accusamus", "iusto", "odio", "dignissimos", "ducimus", "blanditiis",
        "praesentium", "voluptatum", "deleniti", "atque", "corrupti", "quos", "dolores",
        "quas", "molestias", "excepturi", "obcaecati", "cupiditate", "provident",
    ]

    import random
    paras = []
    for p in range(paragraphs):
        sentences = []
        for s in range(sentences_per_paragraph):
            length = random.randint(6, 15)
            sentence_words = [random.choice(words) for _ in range(length)]
            sentence_words[0] = sentence_words[0].capitalize()
            sentences.append(" ".join(sentence_words) + ".")
        paras.append(" ".join(sentences))

    text = "\n\n".join(paras)

    if format == "html":
        html = "".join(f"<p>{p}</p>" for p in paras)
        return {"format": "html", "text": html, "paragraphs": paragraphs}

    return {"format": "text", "text": text, "paragraphs": paragraphs, "word_count": len(text.split())}


# --- Color Palette Generator ---

@app.get("/api/color/palette")
async def color_palette(
    base_color: str = Query("#3498db"),
    scheme: str = Query("complementary"),
    count: int = Query(5, ge=2, le=12),
):
    """Generate color palettes (complementary, analogous, triadic, monochromatic) from a base color."""
    # Parse hex color
    color = base_color.lstrip("#")
    if len(color) != 6:
        return JSONResponse({"error": "Invalid hex color. Use format: #RRGGBB"}, status_code=400)

    r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)

    # RGB to HSL
    r1, g1, b1 = r / 255, g / 255, b / 255
    max_c = max(r1, g1, b1)
    min_c = min(r1, g1, b1)
    l = (max_c + min_c) / 2

    if max_c == min_c:
        h = s = 0
    else:
        d = max_c - min_c
        s = d / (2 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)
        if max_c == r1:
            h = (g1 - b1) / d + (6 if g1 < b1 else 0)
        elif max_c == g1:
            h = (b1 - r1) / d + 2
        else:
            h = (r1 - g1) / d + 4
        h /= 6

    def hsl_to_hex(h, s, l):
        if s == 0:
            rv = gv = bv = int(l * 255)
        else:
            def hue2rgb(p, q, t):
                if t < 0: t += 1
                if t > 1: t -= 1
                if t < 1/6: return p + (q - p) * 6 * t
                if t < 1/2: return q
                if t < 2/3: return p + (q - p) * (2/3 - t) * 6
                return p
            q = l * (1 + s) if l < 0.5 else l + s - l * s
            p = 2 * l - q
            rv = int(hue2rgb(p, q, h + 1/3) * 255)
            gv = int(hue2rgb(p, q, h) * 255)
            bv = int(hue2rgb(p, q, h - 1/3) * 255)
        return f"#{rv:02x}{gv:02x}{bv:02x}"

    colors = [{"hex": base_color, "role": "base"}]

    if scheme == "complementary":
        for i in range(1, count):
            offset = 0.5 if i == 1 else (i * 0.5 / count)
            new_h = (h + offset) % 1.0
            colors.append({"hex": hsl_to_hex(new_h, s, l), "role": f"complement_{i}"})
    elif scheme == "analogous":
        step = 30 / 360
        for i in range(1, count):
            offset = step * (i - count // 2)
            new_h = (h + offset) % 1.0
            colors.append({"hex": hsl_to_hex(new_h, s, l), "role": f"analogous_{i}"})
    elif scheme == "triadic":
        for i in range(1, count):
            new_h = (h + i / 3) % 1.0
            colors.append({"hex": hsl_to_hex(new_h, s, l), "role": f"triadic_{i}"})
    elif scheme == "monochromatic":
        for i in range(1, count):
            new_l = max(0.1, min(0.9, l + (i - count // 2) * 0.15))
            colors.append({"hex": hsl_to_hex(h, s, new_l), "role": f"shade_{i}"})
    else:
        # Split complementary
        for i in range(1, count):
            offset = 150 / 360 if i % 2 == 1 else 210 / 360
            new_h = (h + offset * ((i + 1) // 2)) % 1.0
            colors.append({"hex": hsl_to_hex(new_h, s, l), "role": f"split_{i}"})

    return {
        "base_color": base_color,
        "scheme": scheme,
        "colors": colors[:count],
        "hsl": {"h": round(h * 360, 1), "s": round(s * 100, 1), "l": round(l * 100, 1)},
    }


# --- Slug Generator ---

class SlugRequest(BaseModel):
    text: str
    separator: str = "-"
    max_length: int = 80

@app.post("/api/slug/generate")
async def slug_generate(req: SlugRequest):
    """Generate URL-friendly slugs from text."""
    import unicodedata
    text = unicodedata.normalize("NFKD", req.text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", req.separator, text).strip(req.separator)
    if req.max_length > 0:
        text = text[:req.max_length].rstrip(req.separator)

    return {
        "original": req.text,
        "slug": text,
        "separator": req.separator,
        "length": len(text),
    }


# --- Markdown to Plain Text ---

class MarkdownStripRequest(BaseModel):
    markdown: str

@app.post("/api/markdown/strip")
async def markdown_strip(req: MarkdownStripRequest):
    """Strip markdown formatting and return plain text."""
    text = req.markdown
    # Remove headers
    text = re.sub(r"#{1,6}\s*", "", text)
    # Remove bold/italic
    text = re.sub(r"\*{1,3}(.*?)\*{1,3}", r"\1", text)
    text = re.sub(r"_{1,3}(.*?)_{1,3}", r"\1", text)
    # Remove links
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    # Remove images
    text = re.sub(r"!\[([^\]]*)\]\([^\)]+\)", r"\1", text)
    # Remove code blocks
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    # Remove blockquotes
    text = re.sub(r"^\s*>\s*", "", text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r"^[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)
    # Remove list markers
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
    # Clean up whitespace
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    return {
        "plain_text": text,
        "original_length": len(req.markdown),
        "stripped_length": len(text),
        "reduction_percent": round((1 - len(text) / max(len(req.markdown), 1)) * 100, 1),
    }


# --- AI Agent Tools (Premium) ---

class StructuredExtractRequest(BaseModel):
    text: str
    extract: str = "entities"  # entities, dates, emails, urls, phones, numbers, addresses


@app.post("/api/extract/structured")
async def extract_structured(req: StructuredExtractRequest):
    """Extract structured data from unstructured text. Premium endpoint for AI agents."""
    text = req.text
    results = {}

    if req.extract in ("entities", "all"):
        # Extract emails
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        results["emails"] = list(set(emails))

    if req.extract in ("urls", "all"):
        urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', text)
        results["urls"] = list(set(urls))

    if req.extract in ("phones", "all"):
        phones = re.findall(r'(?:\+?1[-.]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}', text)
        results["phones"] = list(set(phones))

    if req.extract in ("dates", "all"):
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',
            r'\d{1,2}/\d{1,2}/\d{2,4}',
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}',
            r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}',
        ]
        dates = []
        for p in date_patterns:
            dates.extend(re.findall(p, text, re.IGNORECASE))
        results["dates"] = list(set(dates))

    if req.extract in ("numbers", "all"):
        numbers = re.findall(r'(?<!\w)[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?(?!\w)', text)
        results["numbers"] = numbers[:100]

    if req.extract in ("emails", "all") and "emails" not in results:
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        results["emails"] = list(set(emails))

    if req.extract in ("addresses", "all"):
        # Basic US address patterns
        addresses = re.findall(r'\d+\s+[\w\s]+(?:St|Street|Ave|Avenue|Blvd|Boulevard|Rd|Road|Dr|Drive|Ln|Lane|Way|Ct|Court|Pl|Place)\.?\s*,?\s*[\w\s]+,?\s*[A-Z]{2}\s*\d{5}', text, re.IGNORECASE)
        results["addresses"] = addresses[:20]

    return {
        "extract_type": req.extract,
        "text_length": len(text),
        "results": results,
        "total_found": sum(len(v) for v in results.values() if isinstance(v, list)),
    }


class TextTransformRequest(BaseModel):
    text: str
    transforms: list[str] = []  # uppercase, lowercase, title, reverse, sort_lines, unique_lines, trim, number_lines, remove_blank_lines, remove_duplicates


@app.post("/api/text/transform")
async def text_transform(req: TextTransformRequest):
    """Apply multiple text transformations in sequence. Useful for AI agents processing text."""
    text = req.text
    applied = []

    for t in req.transforms:
        t = t.lower().strip()
        if t == "uppercase":
            text = text.upper()
        elif t == "lowercase":
            text = text.lower()
        elif t == "title":
            text = text.title()
        elif t == "reverse":
            text = text[::-1]
        elif t == "reverse_lines":
            text = "\n".join(text.split("\n")[::-1])
        elif t == "sort_lines":
            text = "\n".join(sorted(text.split("\n")))
        elif t == "unique_lines":
            seen = set()
            lines = []
            for line in text.split("\n"):
                if line not in seen:
                    seen.add(line)
                    lines.append(line)
            text = "\n".join(lines)
        elif t == "trim":
            text = "\n".join(line.strip() for line in text.split("\n"))
        elif t == "number_lines":
            text = "\n".join(f"{i+1}. {line}" for i, line in enumerate(text.split("\n")))
        elif t == "remove_blank_lines":
            text = "\n".join(line for line in text.split("\n") if line.strip())
        elif t == "remove_duplicates":
            words = text.split()
            seen = set()
            unique = []
            for w in words:
                if w.lower() not in seen:
                    seen.add(w.lower())
                    unique.append(w)
            text = " ".join(unique)
        else:
            continue
        applied.append(t)

    return {
        "result": text,
        "transforms_applied": applied,
        "original_length": len(req.text),
        "result_length": len(text),
    }


class CompareRequest(BaseModel):
    items: list[str]
    mode: str = "levenshtein"  # levenshtein, jaccard, common_prefix, common_suffix


@app.post("/api/text/compare")
async def text_compare(req: CompareRequest):
    """Compare multiple text strings and find similarities. Useful for deduplication."""
    items = req.items[:20]
    if len(items) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 items to compare")

    def levenshtein(s1, s2):
        if len(s1) < len(s2):
            return levenshtein(s2, s1)
        if len(s2) == 0:
            return len(s1)
        prev_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            curr_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = prev_row[j + 1] + 1
                deletions = curr_row[j] + 1
                substitutions = prev_row[j] + (c1 != c2)
                curr_row.append(min(insertions, deletions, substitutions))
            prev_row = curr_row
        return prev_row[-1]

    comparisons = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a, b = items[i], items[j]
            dist = levenshtein(a, b)
            max_len = max(len(a), len(b))
            similarity = round((1 - dist / max_len) * 100, 1) if max_len > 0 else 100
            comparisons.append({
                "pair": [i, j],
                "distance": dist,
                "similarity_percent": similarity,
            })

    comparisons.sort(key=lambda x: x["similarity_percent"], reverse=True)
    return {
        "item_count": len(items),
        "comparisons": comparisons,
        "most_similar": comparisons[0] if comparisons else None,
        "least_similar": comparisons[-1] if comparisons else None,
    }


class ConvertUnitsRequest(BaseModel):
    value: float
    from_unit: str
    to_unit: str


UNIT_CONVERSIONS = {
    # Length
    ("m", "ft"): 3.28084, ("ft", "m"): 0.3048,
    ("m", "in"): 39.3701, ("in", "m"): 0.0254,
    ("km", "mi"): 0.621371, ("mi", "km"): 1.60934,
    ("cm", "in"): 0.393701, ("in", "cm"): 2.54,
    ("m", "cm"): 100, ("cm", "m"): 0.01,
    ("m", "km"): 0.001, ("km", "m"): 1000,
    ("m", "mm"): 1000, ("mm", "m"): 0.001,
    ("ft", "in"): 12, ("in", "ft"): 1/12,
    ("mi", "ft"): 5280, ("ft", "mi"): 1/5280,
    ("yd", "m"): 0.9144, ("m", "yd"): 1.09361,
    # Weight
    ("kg", "lb"): 2.20462, ("lb", "kg"): 0.453592,
    ("kg", "oz"): 35.274, ("oz", "kg"): 0.0283495,
    ("kg", "g"): 1000, ("g", "kg"): 0.001,
    ("lb", "oz"): 16, ("oz", "lb"): 0.0625,
    ("kg", "st"): 0.157473, ("st", "kg"): 6.35029,
    # Temperature handled separately
    # Volume
    ("l", "gal"): 0.264172, ("gal", "l"): 3.78541,
    ("l", "ml"): 1000, ("ml", "l"): 0.001,
    ("l", "fl_oz"): 33.814, ("fl_oz", "l"): 0.0295735,
    ("l", "cup"): 4.22675, ("cup", "l"): 0.236588,
    # Speed
    ("mph", "kph"): 1.60934, ("kph", "mph"): 0.621371,
    ("m/s", "kph"): 3.6, ("kph", "m/s"): 1/3.6,
    ("m/s", "mph"): 2.23694, ("mph", "m/s"): 0.44704,
    # Data
    ("b", "kb"): 1/1024, ("kb", "b"): 1024,
    ("kb", "mb"): 1/1024, ("mb", "kb"): 1024,
    ("mb", "gb"): 1/1024, ("gb", "mb"): 1024,
    ("gb", "tb"): 1/1024, ("tb", "gb"): 1024,
    ("b", "mb"): 1/(1024*1024), ("mb", "b"): 1024*1024,
    ("b", "gb"): 1/(1024**3), ("gb", "b"): 1024**3,
}


@app.post("/api/convert/units")
@app.get("/api/convert/units")
async def convert_units(req: ConvertUnitsRequest = None, value: float = 0, from_unit: str = "", to_unit: str = ""):
    """Convert between units (length, weight, temperature, volume, speed, data)."""
    if req:
        value, from_unit, to_unit = req.value, req.from_unit, req.to_unit
    from_unit = from_unit.lower().strip()
    to_unit = to_unit.lower().strip()

    if from_unit == to_unit:
        return {"value": value, "from": from_unit, "to": to_unit, "result": value}

    # Temperature special cases
    if from_unit in ("c", "celsius") and to_unit in ("f", "fahrenheit"):
        result = value * 9/5 + 32
    elif from_unit in ("f", "fahrenheit") and to_unit in ("c", "celsius"):
        result = (value - 32) * 5/9
    elif from_unit in ("c", "celsius") and to_unit in ("k", "kelvin"):
        result = value + 273.15
    elif from_unit in ("k", "kelvin") and to_unit in ("c", "celsius"):
        result = value - 273.15
    elif from_unit in ("f", "fahrenheit") and to_unit in ("k", "kelvin"):
        result = (value - 32) * 5/9 + 273.15
    elif from_unit in ("k", "kelvin") and to_unit in ("f", "fahrenheit"):
        result = (value - 273.15) * 9/5 + 32
    elif (from_unit, to_unit) in UNIT_CONVERSIONS:
        result = value * UNIT_CONVERSIONS[(from_unit, to_unit)]
    else:
        raise HTTPException(status_code=400, detail=f"Unknown conversion: {from_unit} to {to_unit}. Supported: length (m,ft,in,km,mi,cm,mm,yd), weight (kg,lb,oz,g,st), temperature (c,f,k), volume (l,gal,ml,fl_oz,cup), speed (mph,kph,m/s), data (b,kb,mb,gb,tb)")

    return {
        "value": value,
        "from": from_unit,
        "to": to_unit,
        "result": round(result, 6),
        "formula": f"{value} {from_unit} = {round(result, 6)} {to_unit}",
    }


# --- New Endpoints: Batch 3 (session 17) ---

class SqlFormatRequest(BaseModel):
    sql: str
    uppercase_keywords: bool = True
    indent: int = 2

@app.post("/api/sql/format")
async def sql_format(req: SqlFormatRequest):
    """Format and prettify SQL queries."""
    keywords = [
        "SELECT", "FROM", "WHERE", "AND", "OR", "JOIN", "LEFT JOIN", "RIGHT JOIN",
        "INNER JOIN", "OUTER JOIN", "CROSS JOIN", "ON", "GROUP BY", "ORDER BY",
        "HAVING", "LIMIT", "OFFSET", "INSERT INTO", "VALUES", "UPDATE", "SET",
        "DELETE FROM", "CREATE TABLE", "ALTER TABLE", "DROP TABLE", "CREATE INDEX",
        "UNION", "UNION ALL", "EXCEPT", "INTERSECT", "AS", "IN", "NOT IN",
        "EXISTS", "NOT EXISTS", "BETWEEN", "LIKE", "IS NULL", "IS NOT NULL",
        "CASE", "WHEN", "THEN", "ELSE", "END", "DISTINCT", "COUNT", "SUM",
        "AVG", "MIN", "MAX", "ASC", "DESC", "WITH",
    ]
    sql = req.sql.strip()
    # Normalize whitespace
    sql = re.sub(r'\s+', ' ', sql)
    indent = " " * req.indent
    # Add newlines before major clauses
    major_clauses = ["SELECT", "FROM", "WHERE", "GROUP BY", "ORDER BY", "HAVING",
                     "LIMIT", "OFFSET", "UNION", "UNION ALL", "EXCEPT", "INTERSECT",
                     "INSERT INTO", "VALUES", "UPDATE", "SET", "DELETE FROM",
                     "CREATE TABLE", "ALTER TABLE", "DROP TABLE", "WITH"]
    for clause in sorted(major_clauses, key=len, reverse=True):
        pattern = re.compile(r'\b' + clause + r'\b', re.IGNORECASE)
        sql = pattern.sub(f"\n{clause if req.uppercase_keywords else clause.lower()}", sql)
    # Add newlines before JOIN clauses
    join_clauses = ["LEFT JOIN", "RIGHT JOIN", "INNER JOIN", "OUTER JOIN", "CROSS JOIN", "JOIN"]
    for clause in sorted(join_clauses, key=len, reverse=True):
        pattern = re.compile(r'\b' + clause + r'\b', re.IGNORECASE)
        sql = pattern.sub(f"\n{indent}{clause if req.uppercase_keywords else clause.lower()}", sql)
    # Indent AND/OR
    for kw in ["AND", "OR"]:
        pattern = re.compile(r'\b' + kw + r'\b', re.IGNORECASE)
        sql = pattern.sub(f"\n{indent}{kw if req.uppercase_keywords else kw.lower()}", sql)
    # Uppercase keywords if requested
    if req.uppercase_keywords:
        for kw in keywords:
            pattern = re.compile(r'\b' + kw + r'\b', re.IGNORECASE)
            sql = pattern.sub(kw, sql)
    return {"formatted": sql.strip(), "original_length": len(req.sql), "formatted_length": len(sql.strip())}


class HtmlStripRequest(BaseModel):
    html: str
    preserve_links: bool = False

@app.post("/api/html/strip")
async def html_strip(req: HtmlStripRequest):
    """Strip HTML tags and return plain text. Optionally preserve link URLs."""
    if req.preserve_links:
        text = re.sub(r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>', r'\2 (\1)', req.html, flags=re.IGNORECASE)
    else:
        text = req.html
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</(p|div|h[1-6]|li|tr)>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&quot;', '"', text)
    text = re.sub(r'&#39;', "'", text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    return {"text": text, "original_length": len(req.html), "text_length": len(text)}


class TextStatsRequest(BaseModel):
    text: str

@app.post("/api/text/stats")
async def text_statistics(req: TextStatsRequest):
    """Get detailed text statistics: word count, char count, reading time, sentence count, etc."""
    text = req.text
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    lines = text.split('\n')

    word_count = len(words)
    char_count = len(text)
    char_no_spaces = len(text.replace(" ", "").replace("\n", "").replace("\t", ""))
    sentence_count = len(sentences)
    paragraph_count = len(paragraphs)
    line_count = len(lines)
    avg_word_length = round(sum(len(w) for w in words) / max(word_count, 1), 1)
    avg_sentence_length = round(word_count / max(sentence_count, 1), 1)
    reading_time_minutes = round(word_count / 238, 1)  # avg adult reading speed
    speaking_time_minutes = round(word_count / 150, 1)  # avg speaking speed

    # Readability (Flesch-Kincaid approximation)
    syllable_count = sum(max(1, len(re.findall(r'[aeiouy]+', w.lower()))) for w in words)
    if word_count > 0 and sentence_count > 0:
        fk_grade = round(0.39 * (word_count/sentence_count) + 11.8 * (syllable_count/word_count) - 15.59, 1)
        flesch_reading = round(206.835 - 1.015 * (word_count/sentence_count) - 84.6 * (syllable_count/word_count), 1)
    else:
        fk_grade = 0
        flesch_reading = 0

    return {
        "characters": char_count,
        "characters_no_spaces": char_no_spaces,
        "words": word_count,
        "sentences": sentence_count,
        "paragraphs": paragraph_count,
        "lines": line_count,
        "avg_word_length": avg_word_length,
        "avg_sentence_length": avg_sentence_length,
        "syllables": syllable_count,
        "reading_time_minutes": reading_time_minutes,
        "speaking_time_minutes": speaking_time_minutes,
        "flesch_reading_ease": flesch_reading,
        "flesch_kincaid_grade": fk_grade,
    }


class NumberFormatRequest(BaseModel):
    number: float
    format: str = "comma"  # comma, words, roman, scientific, binary, hex, octal

@app.post("/api/number/format")
async def number_format(req: NumberFormatRequest):
    """Format numbers in various ways: comma-separated, words, roman numerals, scientific, binary, hex, octal."""
    n = req.number
    result = {}

    if req.format == "comma" or req.format == "all":
        result["comma"] = f"{n:,.2f}" if n != int(n) else f"{int(n):,}"

    if req.format == "scientific" or req.format == "all":
        result["scientific"] = f"{n:.6e}"

    if req.format == "binary" or req.format == "all":
        if n == int(n) and n >= 0:
            result["binary"] = bin(int(n))
        else:
            result["binary"] = "N/A (positive integers only)"

    if req.format == "hex" or req.format == "all":
        if n == int(n) and n >= 0:
            result["hex"] = hex(int(n))
        else:
            result["hex"] = "N/A (positive integers only)"

    if req.format == "octal" or req.format == "all":
        if n == int(n) and n >= 0:
            result["octal"] = oct(int(n))
        else:
            result["octal"] = "N/A (positive integers only)"

    if req.format == "roman" or req.format == "all":
        if 0 < n <= 3999 and n == int(n):
            val = int(n)
            roman = ""
            for (v, s) in [(1000,"M"),(900,"CM"),(500,"D"),(400,"CD"),(100,"C"),(90,"XC"),(50,"L"),(40,"XL"),(10,"X"),(9,"IX"),(5,"V"),(4,"IV"),(1,"I")]:
                while val >= v:
                    roman += s
                    val -= v
            result["roman"] = roman
        else:
            result["roman"] = "N/A (1-3999 only)"

    if req.format == "words" or req.format == "all":
        # Simple English words for numbers
        if n == int(n) and abs(n) < 1e15:
            ones = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
                    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
                    "seventeen", "eighteen", "nineteen"]
            tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
            def num_to_words(num):
                if num == 0: return "zero"
                if num < 0: return "negative " + num_to_words(-num)
                if num < 20: return ones[num]
                if num < 100: return tens[num//10] + ("-" + ones[num%10] if num%10 else "")
                if num < 1000: return ones[num//100] + " hundred" + (" and " + num_to_words(num%100) if num%100 else "")
                for val, name in [(10**12, "trillion"), (10**9, "billion"), (10**6, "million"), (10**3, "thousand")]:
                    if num >= val:
                        return num_to_words(num//val) + " " + name + (" " + num_to_words(num%val) if num%val else "")
                return str(num)
            result["words"] = num_to_words(int(n))
        else:
            result["words"] = "N/A (integers up to trillions)"

    if not result:
        result[req.format] = f"{n}"

    result["original"] = n
    return result


class XmlToJsonRequest(BaseModel):
    xml: str

@app.post("/api/xml/to-json")
async def xml_to_json(req: XmlToJsonRequest):
    """Convert XML to JSON."""
    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(req.xml)
    except ET.ParseError as e:
        raise HTTPException(status_code=400, detail=f"Invalid XML: {e}")

    def elem_to_dict(elem):
        d = {}
        if elem.attrib:
            d["@attributes"] = dict(elem.attrib)
        children = list(elem)
        if children:
            child_dict = {}
            for child in children:
                tag = child.tag
                val = elem_to_dict(child)
                if tag in child_dict:
                    if not isinstance(child_dict[tag], list):
                        child_dict[tag] = [child_dict[tag]]
                    child_dict[tag].append(val)
                else:
                    child_dict[tag] = val
            d.update(child_dict)
        elif elem.text and elem.text.strip():
            if d:
                d["#text"] = elem.text.strip()
            else:
                return elem.text.strip()
        return d if d else None

    return {"root_tag": root.tag, "data": {root.tag: elem_to_dict(root)}}


class YamlValidateRequest(BaseModel):
    yaml_text: str

@app.post("/api/yaml/validate")
async def yaml_validate(req: YamlValidateRequest):
    """Validate YAML syntax and convert to JSON."""
    try:
        import yaml
        data = yaml.safe_load(req.yaml_text)
        return {"valid": True, "json": data, "type": type(data).__name__}
    except ImportError:
        # Manual basic YAML validation
        lines = req.yaml_text.strip().split('\n')
        result = {}
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if ':' in line:
                key, _, val = line.partition(':')
                result[key.strip()] = val.strip()
        return {"valid": True, "json": result, "note": "Basic parsing (PyYAML not available)"}
    except Exception as e:
        return {"valid": False, "error": str(e)}


class EnvParseRequest(BaseModel):
    env_text: str

@app.post("/api/env/parse")
async def env_parse(req: EnvParseRequest):
    """Parse .env file content to JSON. Handles comments, quotes, multiline."""
    result = {}
    for line in req.env_text.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' not in line:
            continue
        key, _, value = line.partition('=')
        key = key.strip()
        value = value.strip()
        # Remove surrounding quotes
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        result[key] = value
    return {"variables": result, "count": len(result)}


@app.get("/api/http-status/{code}")
async def http_status_info(code: int):
    """Get information about an HTTP status code."""
    statuses = {
        100: ("Continue", "The server has received the request headers and the client should proceed to send the request body."),
        101: ("Switching Protocols", "The server is switching protocols as requested by the client."),
        200: ("OK", "The request has succeeded."),
        201: ("Created", "The request has been fulfilled and a new resource has been created."),
        204: ("No Content", "The server has fulfilled the request but there is no content to return."),
        301: ("Moved Permanently", "The requested resource has been permanently moved to a new URL."),
        302: ("Found", "The requested resource temporarily resides at a different URL."),
        304: ("Not Modified", "The resource has not been modified since the last request."),
        400: ("Bad Request", "The server cannot process the request due to a client error."),
        401: ("Unauthorized", "Authentication is required and has failed or not been provided."),
        403: ("Forbidden", "The server understood the request but refuses to authorize it."),
        404: ("Not Found", "The requested resource could not be found."),
        405: ("Method Not Allowed", "The request method is not supported for the requested resource."),
        408: ("Request Timeout", "The server timed out waiting for the request."),
        409: ("Conflict", "The request could not be completed due to a conflict with the current state."),
        410: ("Gone", "The requested resource is no longer available and will not be available again."),
        413: ("Payload Too Large", "The request is larger than the server is willing to process."),
        415: ("Unsupported Media Type", "The media format of the requested data is not supported."),
        418: ("I'm a Teapot", "The server refuses to brew coffee because it is a teapot (RFC 2324)."),
        422: ("Unprocessable Entity", "The request was well-formed but could not be followed due to semantic errors."),
        429: ("Too Many Requests", "The user has sent too many requests in a given amount of time."),
        500: ("Internal Server Error", "The server encountered an unexpected condition that prevented it from fulfilling the request."),
        502: ("Bad Gateway", "The server received an invalid response from the upstream server."),
        503: ("Service Unavailable", "The server is not ready to handle the request, often due to maintenance or overload."),
        504: ("Gateway Timeout", "The server did not receive a timely response from the upstream server."),
    }
    if code in statuses:
        name, desc = statuses[code]
        category = "Informational" if code < 200 else "Success" if code < 300 else "Redirection" if code < 400 else "Client Error" if code < 500 else "Server Error"
        return {"code": code, "name": name, "description": desc, "category": category}
    raise HTTPException(status_code=404, detail=f"Unknown HTTP status code: {code}")


class JwtCreateRequest(BaseModel):
    payload: dict
    secret: str = "your-secret-key"
    algorithm: str = "HS256"

@app.post("/api/jwt/create")
async def jwt_create(req: JwtCreateRequest):
    """Create a JWT token from a payload (for testing/development purposes)."""
    import hmac
    header = {"alg": req.algorithm, "typ": "JWT"}
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b"=").decode()
    # Add standard claims if not present
    payload = dict(req.payload)
    if "iat" not in payload:
        payload["iat"] = int(time.time())
    if "exp" not in payload:
        payload["exp"] = int(time.time()) + 3600  # 1 hour
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()
    signing_input = f"{header_b64}.{payload_b64}"
    signature = hmac.new(req.secret.encode(), signing_input.encode(), hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(signature).rstrip(b"=").decode()
    token = f"{header_b64}.{payload_b64}.{sig_b64}"
    return {"token": token, "header": header, "payload": payload, "expires_in": 3600}


class IpInfoRequest(BaseModel):
    ip: str = ""

@app.get("/api/myip")
async def my_ip(request: Request):
    """Get the caller's IP address and basic info."""
    ip = request.headers.get("x-forwarded-for", request.headers.get("x-real-ip", request.client.host))
    if "," in ip:
        ip = ip.split(",")[0].strip()
    return {
        "ip": ip,
        "user_agent": request.headers.get("user-agent", ""),
        "accept_language": request.headers.get("accept-language", ""),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# --- Webhook Tester ---

WEBHOOK_DB = Path(__file__).parent / "data" / "webhooks.db"
_webhook_lock = threading.Lock()

def _init_webhook_db():
    conn = sqlite3.connect(str(WEBHOOK_DB))
    conn.execute("""CREATE TABLE IF NOT EXISTS webhook_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bin_id TEXT NOT NULL,
        method TEXT,
        path TEXT,
        headers TEXT,
        body TEXT,
        query_params TEXT,
        source_ip TEXT,
        received_at TEXT
    )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_webhook_bin ON webhook_requests(bin_id)")
    conn.commit()
    conn.close()

_init_webhook_db()


@app.post("/api/webhooks/create")
async def create_webhook_bin():
    """Create a unique webhook endpoint for testing. Send requests to /webhooks/{bin_id} and inspect them via /api/webhooks/{bin_id}/requests."""
    bin_id = uuid.uuid4().hex[:12]
    return {
        "bin_id": bin_id,
        "url": f"/webhooks/{bin_id}",
        "inspect_url": f"/api/webhooks/{bin_id}/requests",
        "instructions": f"Send any HTTP request to /webhooks/{bin_id}. Then GET /api/webhooks/{bin_id}/requests to see captured requests.",
        "expires": "Requests stored for 24 hours, max 100 per bin.",
    }


@app.api_route("/webhooks/{bin_id}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def receive_webhook(bin_id: str, request: Request):
    """Capture any HTTP request sent to this webhook bin."""
    body = ""
    try:
        raw = await request.body()
        body = raw.decode("utf-8", errors="replace")[:10000]
    except Exception:
        pass

    headers = dict(request.headers)
    query = dict(request.query_params)
    ip = request.headers.get("x-forwarded-for", request.client.host)
    now = datetime.now(timezone.utc).isoformat()

    with _webhook_lock:
        conn = sqlite3.connect(str(WEBHOOK_DB))
        conn.execute(
            "INSERT INTO webhook_requests (bin_id, method, path, headers, body, query_params, source_ip, received_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (bin_id, request.method, str(request.url.path), json.dumps(headers), body, json.dumps(query), ip, now)
        )
        # Keep max 100 per bin
        conn.execute(
            "DELETE FROM webhook_requests WHERE bin_id = ? AND id NOT IN (SELECT id FROM webhook_requests WHERE bin_id = ? ORDER BY id DESC LIMIT 100)",
            (bin_id, bin_id)
        )
        # Clean entries older than 24h
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
        conn.execute("DELETE FROM webhook_requests WHERE received_at < ?", (cutoff,))
        conn.commit()
        conn.close()

    return {"status": "captured", "bin_id": bin_id, "method": request.method, "timestamp": now}


@app.get("/api/webhooks/{bin_id}/requests")
async def get_webhook_requests(bin_id: str, limit: int = 20):
    """Inspect captured webhook requests for a bin."""
    with _webhook_lock:
        conn = sqlite3.connect(str(WEBHOOK_DB))
        rows = conn.execute(
            "SELECT method, path, headers, body, query_params, source_ip, received_at FROM webhook_requests WHERE bin_id = ? ORDER BY id DESC LIMIT ?",
            (bin_id, min(limit, 100))
        ).fetchall()
        conn.close()
    requests_list = []
    for r in rows:
        requests_list.append({
            "method": r[0], "path": r[1],
            "headers": json.loads(r[2]) if r[2] else {},
            "body": r[3], "query_params": json.loads(r[4]) if r[4] else {},
            "source_ip": r[5], "received_at": r[6],
        })
    return {"bin_id": bin_id, "count": len(requests_list), "requests": requests_list}


# --- Mock API Response Generator ---

class MockApiRequest(BaseModel):
    schema: dict | None = None
    count: int = 1
    format: str = "json"  # json, xml, csv
    template: str | None = None  # "user", "product", "order", "comment", "post"


MOCK_TEMPLATES = {
    "user": {"id": "int", "name": "name", "email": "email", "avatar": "url", "created_at": "date", "role": "choice:admin,user,moderator"},
    "product": {"id": "int", "name": "word", "price": "float", "currency": "choice:USD,EUR,GBP", "category": "choice:electronics,clothing,food,books", "in_stock": "bool", "rating": "float"},
    "order": {"id": "int", "customer_email": "email", "total": "float", "status": "choice:pending,processing,shipped,delivered,cancelled", "items_count": "int", "created_at": "date"},
    "comment": {"id": "int", "author": "name", "text": "sentence", "likes": "int", "created_at": "date"},
    "post": {"id": "int", "title": "sentence", "body": "paragraph", "author": "name", "tags": "tags", "published": "bool", "views": "int"},
}


def _generate_mock_value(field_type: str, idx: int = 0) -> any:
    import random, string
    ft = field_type.lower()
    if ft == "int":
        return random.randint(1, 10000)
    elif ft == "float":
        return round(random.uniform(1, 999.99), 2)
    elif ft == "bool":
        return random.choice([True, False])
    elif ft == "name":
        first = random.choice(["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry", "Ivy", "Jack"])
        last = random.choice(["Smith", "Johnson", "Williams", "Brown", "Jones", "Davis", "Miller", "Wilson", "Moore", "Taylor"])
        return f"{first} {last}"
    elif ft == "email":
        user = ''.join(random.choices(string.ascii_lowercase, k=8))
        domain = random.choice(["gmail.com", "example.com", "mail.org", "test.io"])
        return f"{user}@{domain}"
    elif ft == "url":
        return f"https://example.com/{random.randint(1,999)}"
    elif ft == "date":
        d = random.randint(1609459200, 1775068800)
        return datetime.fromtimestamp(d, tz=timezone.utc).isoformat()
    elif ft == "word":
        return random.choice(["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Theta", "Lambda", "Sigma", "Omega"])
    elif ft == "sentence":
        words = random.choices(["the", "quick", "brown", "fox", "jumped", "over", "lazy", "dog", "a", "simple", "test", "data", "mock", "api", "response"], k=random.randint(5, 12))
        return ' '.join(words).capitalize() + '.'
    elif ft == "paragraph":
        return ' '.join(_generate_mock_value("sentence") for _ in range(random.randint(3, 6)))
    elif ft == "tags":
        all_tags = ["python", "javascript", "api", "web", "data", "ai", "cloud", "dev", "test", "tools"]
        return random.sample(all_tags, k=random.randint(2, 4))
    elif ft.startswith("choice:"):
        options = ft[7:].split(",")
        return random.choice(options)
    elif ft == "uuid":
        return str(uuid.uuid4())
    else:
        return f"value_{idx}"


@app.post("/api/mock/generate")
async def generate_mock_data_v2(req: MockApiRequest):
    """Generate mock API responses. Use templates (user, product, order, comment, post) or custom schemas."""
    schema = req.schema
    if req.template and req.template in MOCK_TEMPLATES:
        schema = MOCK_TEMPLATES[req.template]
    elif not schema:
        schema = MOCK_TEMPLATES["user"]

    count = max(1, min(req.count, 100))
    results = []
    for i in range(count):
        item = {}
        for key, field_type in schema.items():
            item[key] = _generate_mock_value(str(field_type), i)
        results.append(item)

    if req.format == "csv" and results:
        import io, csv
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=results[0].keys())
        writer.writeheader()
        for row in results:
            flat_row = {k: json.dumps(v) if isinstance(v, (list, dict)) else v for k, v in row.items()}
            writer.writerow(flat_row)
        return {"format": "csv", "data": output.getvalue(), "count": count}

    return {"format": "json", "data": results if count > 1 else results[0], "count": count, "template": req.template}


# --- Crontab Generator ---

class CrontabRequest(BaseModel):
    description: str  # e.g. "every 5 minutes", "daily at 3am", "weekdays at noon"


CRON_PATTERNS = {
    "every minute": "* * * * *",
    "every 5 minutes": "*/5 * * * *",
    "every 10 minutes": "*/10 * * * *",
    "every 15 minutes": "*/15 * * * *",
    "every 30 minutes": "*/30 * * * *",
    "every hour": "0 * * * *",
    "every 2 hours": "0 */2 * * *",
    "every 4 hours": "0 */4 * * *",
    "every 6 hours": "0 */6 * * *",
    "every 12 hours": "0 */12 * * *",
    "daily": "0 0 * * *",
    "daily at midnight": "0 0 * * *",
    "daily at noon": "0 12 * * *",
    "daily at 3am": "0 3 * * *",
    "daily at 6am": "0 6 * * *",
    "daily at 9am": "0 9 * * *",
    "weekly": "0 0 * * 0",
    "weekly on monday": "0 0 * * 1",
    "weekly on friday": "0 0 * * 5",
    "weekdays": "0 9 * * 1-5",
    "weekdays at noon": "0 12 * * 1-5",
    "weekdays at 9am": "0 9 * * 1-5",
    "weekends": "0 10 * * 0,6",
    "monthly": "0 0 1 * *",
    "first of month": "0 0 1 * *",
    "last day of month": "0 0 28-31 * *",
    "quarterly": "0 0 1 1,4,7,10 *",
    "yearly": "0 0 1 1 *",
    "annually": "0 0 1 1 *",
}


@app.post("/api/crontab/generate")
async def generate_crontab(req: CrontabRequest):
    """Generate a cron expression from a plain English description."""
    desc = req.description.lower().strip()

    # Direct match
    for pattern_desc, cron in CRON_PATTERNS.items():
        if pattern_desc in desc or desc in pattern_desc:
            return {"description": req.description, "cron": cron, "explanation": pattern_desc}

    # Parse "every N minutes/hours"
    import re
    m = re.match(r"every\s+(\d+)\s+(minute|hour|day|week)", desc)
    if m:
        n, unit = int(m.group(1)), m.group(2)
        if unit == "minute" and 1 <= n <= 59:
            return {"description": req.description, "cron": f"*/{n} * * * *", "explanation": f"Every {n} minutes"}
        elif unit == "hour" and 1 <= n <= 23:
            return {"description": req.description, "cron": f"0 */{n} * * *", "explanation": f"Every {n} hours"}
        elif unit == "day" and 1 <= n <= 30:
            return {"description": req.description, "cron": f"0 0 */{n} * *", "explanation": f"Every {n} days"}

    # Parse "at Xam/pm"
    m = re.search(r"at\s+(\d{1,2})\s*(am|pm)?", desc)
    if m:
        hour = int(m.group(1))
        ampm = m.group(2)
        if ampm == "pm" and hour < 12:
            hour += 12
        elif ampm == "am" and hour == 12:
            hour = 0
        # Check for weekdays
        if "weekday" in desc:
            return {"description": req.description, "cron": f"0 {hour} * * 1-5", "explanation": f"Weekdays at {hour}:00"}
        elif "weekend" in desc:
            return {"description": req.description, "cron": f"0 {hour} * * 0,6", "explanation": f"Weekends at {hour}:00"}
        return {"description": req.description, "cron": f"0 {hour} * * *", "explanation": f"Daily at {hour}:00"}

    # Fallback: return closest match
    best_match = None
    best_score = 0
    desc_words = set(desc.split())
    for pattern_desc, cron in CRON_PATTERNS.items():
        pattern_words = set(pattern_desc.split())
        score = len(desc_words & pattern_words)
        if score > best_score:
            best_score = score
            best_match = (pattern_desc, cron)

    if best_match:
        return {"description": req.description, "cron": best_match[1], "explanation": best_match[0], "note": "Best match, may not be exact"}

    return {"description": req.description, "error": "Could not parse. Try: 'every 5 minutes', 'daily at 3am', 'weekdays at noon'", "examples": list(CRON_PATTERNS.keys())[:10]}


# --- Diff/Patch Generator ---

class DiffRequest(BaseModel):
    original: str
    modified: str
    format: str = "unified"  # unified, context, html


@app.post("/api/diff/generate")
async def generate_diff(req: DiffRequest):
    """Generate a diff/patch between two texts. Supports unified, context, and HTML formats."""
    import difflib
    original_lines = req.original.splitlines(keepends=True)
    modified_lines = req.modified.splitlines(keepends=True)

    if req.format == "context":
        diff = list(difflib.context_diff(original_lines, modified_lines, fromfile="original", tofile="modified"))
    elif req.format == "html":
        differ = difflib.HtmlDiff()
        html = differ.make_table(original_lines, modified_lines, fromdesc="Original", todesc="Modified")
        return {"format": "html", "diff": html}
    else:
        diff = list(difflib.unified_diff(original_lines, modified_lines, fromfile="original", tofile="modified"))

    diff_text = ''.join(diff)
    additions = sum(1 for l in diff if l.startswith('+') and not l.startswith('+++'))
    deletions = sum(1 for l in diff if l.startswith('-') and not l.startswith('---'))

    return {"format": req.format, "diff": diff_text, "additions": additions, "deletions": deletions, "changed": additions + deletions > 0}


# --- OpenAPI Spec Auto-Generator ---

@app.get("/openapi-toolpipe.json")
async def openapi_spec():
    """Full OpenAPI 3.1 specification for all ToolPipe API endpoints."""
    spec = {
        "openapi": "3.1.0",
        "info": {
            "title": "ToolPipe API",
            "description": "130+ free developer utility APIs. JSON formatting, QR codes, hashing, UUID, DNS, regex, JWT, SQL formatting, and more. Free tier: 100 calls/day. Pro: 10,000 calls/day.",
            "version": "1.9.0",
            "contact": {"email": "toolpipe-ads@sharebot.net"},
            "license": {"name": "MIT"},
        },
        "servers": [{"url": "https://toolpipe.dev", "description": "Production"}],
        "paths": {},
        "components": {
            "securitySchemes": {
                "apiKey": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key",
                    "description": "Optional API key for higher rate limits. Get one free at POST /api-keys/register",
                }
            }
        },
    }

    # Auto-generate paths from registered routes
    for route in app.routes:
        if not hasattr(route, "path") or not hasattr(route, "methods"):
            continue
        path = route.path
        if path.startswith("/docs") or path.startswith("/redoc") or path.startswith("/openapi"):
            continue
        if "{page_name}" in path:
            continue

        for method in (route.methods or ["GET"]):
            method_lower = method.lower()
            endpoint_func = getattr(route, "endpoint", None)
            summary = ""
            if endpoint_func and endpoint_func.__doc__:
                summary = endpoint_func.__doc__.strip().split('\n')[0]

            if path not in spec["paths"]:
                spec["paths"][path] = {}

            spec["paths"][path][method_lower] = {
                "summary": summary or path,
                "responses": {"200": {"description": "Success"}},
                "security": [{"apiKey": []}],
            }

    return JSONResponse(spec)


# --- API Stats Endpoint ---

@app.get("/api/stats")
async def api_stats():
    """Public API statistics: total endpoints, tools, uptime, version."""
    route_count = sum(1 for r in app.routes if hasattr(r, "methods") and not r.path.startswith("/docs"))
    return {
        "version": "1.13.0",
        "total_endpoints": route_count,
        "mcp_tools": 135,
        "uptime_start": datetime.now(timezone.utc).isoformat(),
        "pricing": {"free": "100 calls/day", "pro": "$9.99/mo (10k calls/day)", "enterprise": "$49.99/mo (100k calls/day)"},
        "payment_methods": ["ETH", "USDC", "USDT", "DAI", "SOL", "USDC-SPL"],
        "networks": ["Ethereum", "Polygon", "Arbitrum", "Base", "Optimism", "Solana"],
    }


# --- APIs.json for API discovery ---

@app.get("/apis.json")
async def apis_json():
    apis_file = Path(__file__).parent / "apis.json"
    if apis_file.exists():
        return JSONResponse(json.loads(apis_file.read_text()))
    return JSONResponse({"error": "not found"}, status_code=404)


# --- Placeholder Image Generator ---

@app.get("/api/placeholder/{width}x{height}")
@app.get("/api/placeholder/{width}")
async def placeholder_image(width: int, height: int = 0, bg: str = "cccccc", fg: str = "333333", text: str = "", fmt: str = "png"):
    """Generate placeholder images. Usage: /api/placeholder/300x200?bg=eee&fg=333&text=Hello"""
    if width < 1 or width > 4000:
        raise HTTPException(status_code=400, detail="Width must be 1-4000")
    if height == 0:
        height = width
    if height < 1 or height > 4000:
        raise HTTPException(status_code=400, detail="Height must be 1-4000")
    # Sanitize colors
    bg = bg.lstrip("#")[:6]
    fg = fg.lstrip("#")[:6]
    try:
        bg_color = tuple(int(bg[i:i+2], 16) for i in (0, 2, 4))
        fg_color = tuple(int(fg[i:i+2], 16) for i in (0, 2, 4))
    except (ValueError, IndexError):
        bg_color = (204, 204, 204)
        fg_color = (51, 51, 51)

    img = Image.new("RGB", (width, height), bg_color)
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    label = text or f"{width}x{height}"
    # Try to find a reasonable font size
    font_size = min(width, height) // 6
    if font_size < 10:
        font_size = 10
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), label, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((width - tw) / 2, (height - th) / 2), label, fill=fg_color, font=font)

    buf = io.BytesIO()
    img_format = "PNG" if fmt.lower() != "jpg" else "JPEG"
    img.save(buf, format=img_format)
    buf.seek(0)
    media = "image/png" if img_format == "PNG" else "image/jpeg"
    return StreamingResponse(buf, media_type=media, headers={"Cache-Control": "public, max-age=86400"})


# --- Favicon Extractor ---

@app.get("/api/favicon")
async def favicon_extractor(url: str = Query(..., description="Website URL to extract favicon from")):
    """Extract favicon URL from any website."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    parsed = urlparse(url)
    if not parsed.netloc:
        raise HTTPException(status_code=400, detail="Invalid URL")

    favicons = []
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "ToolPipe-Bot/1.0"})
            soup = BeautifulSoup(resp.text, "html.parser")

            # Check link tags
            for link in soup.find_all("link", rel=True):
                rels = [r.lower() for r in link.get("rel", [])]
                if any(r in rels for r in ["icon", "shortcut icon", "apple-touch-icon"]):
                    href = link.get("href", "")
                    if href:
                        if href.startswith("//"):
                            href = "https:" + href
                        elif href.startswith("/"):
                            href = f"{parsed.scheme}://{parsed.netloc}{href}"
                        elif not href.startswith("http"):
                            href = f"{parsed.scheme}://{parsed.netloc}/{href}"
                        sizes = link.get("sizes", "")
                        favicons.append({"url": href, "rel": " ".join(rels), "sizes": sizes})

            # Fallback: /favicon.ico
            if not favicons:
                ico_url = f"{parsed.scheme}://{parsed.netloc}/favicon.ico"
                try:
                    ico_resp = await client.head(ico_url, follow_redirects=True)
                    if ico_resp.status_code == 200:
                        favicons.append({"url": ico_url, "rel": "icon", "sizes": ""})
                except Exception:
                    pass
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Could not fetch URL: {str(e)[:100]}")

    # Google fallback
    google_favicon = f"https://www.google.com/s2/favicons?domain={parsed.netloc}&sz=64"
    return {
        "url": url,
        "domain": parsed.netloc,
        "favicons": favicons,
        "google_proxy": google_favicon,
        "best": favicons[0]["url"] if favicons else google_favicon,
    }


# --- Sitemap Generator ---

@app.post("/api/sitemap/generate")
async def sitemap_generate(request: Request):
    """Generate XML sitemap from a list of URLs."""
    body = await request.json()
    urls = body.get("urls", [])
    base_url = body.get("base_url", "")
    changefreq = body.get("changefreq", "weekly")
    priority = body.get("priority", "0.8")

    if not urls:
        raise HTTPException(status_code=400, detail="Provide a 'urls' array")
    if len(urls) > 50000:
        raise HTTPException(status_code=400, detail="Maximum 50,000 URLs per sitemap")

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for u in urls:
        if isinstance(u, str):
            loc = u if u.startswith("http") else f"{base_url.rstrip('/')}/{u.lstrip('/')}"
            lines.append(f"  <url><loc>{loc}</loc><lastmod>{today}</lastmod><changefreq>{changefreq}</changefreq><priority>{priority}</priority></url>")
        elif isinstance(u, dict):
            loc = u.get("url", u.get("loc", ""))
            if not loc.startswith("http"):
                loc = f"{base_url.rstrip('/')}/{loc.lstrip('/')}"
            freq = u.get("changefreq", changefreq)
            pri = u.get("priority", priority)
            mod = u.get("lastmod", today)
            lines.append(f"  <url><loc>{loc}</loc><lastmod>{mod}</lastmod><changefreq>{freq}</changefreq><priority>{pri}</priority></url>")
    lines.append("</urlset>")
    xml = "\n".join(lines)
    return Response(content=xml, media_type="application/xml", headers={"Content-Disposition": "attachment; filename=sitemap.xml"})


# --- README Generator ---

@app.post("/api/readme/generate")
async def readme_generate(request: Request):
    """Generate a README.md from project metadata."""
    body = await request.json()
    name = body.get("name", "My Project")
    description = body.get("description", "")
    features = body.get("features", [])
    install = body.get("install", "")
    usage = body.get("usage", "")
    license_name = body.get("license", "MIT")
    author = body.get("author", "")
    badges = body.get("badges", [])
    api_endpoints = body.get("api_endpoints", [])
    tech_stack = body.get("tech_stack", [])

    lines = []
    # Title and badges
    lines.append(f"# {name}")
    if badges:
        badge_line = " ".join(f"![{b.get('label', 'badge')}]({b.get('url', '')})" for b in badges if isinstance(b, dict))
        if badge_line:
            lines.append(f"\n{badge_line}")
    if description:
        lines.append(f"\n{description}")

    # Features
    if features:
        lines.append("\n## Features\n")
        for f in features:
            lines.append(f"- {f}")

    # Tech stack
    if tech_stack:
        lines.append("\n## Tech Stack\n")
        for t in tech_stack:
            lines.append(f"- {t}")

    # Installation
    if install:
        lines.append("\n## Installation\n")
        lines.append(f"```bash\n{install}\n```")

    # Usage
    if usage:
        lines.append("\n## Usage\n")
        lines.append(f"```\n{usage}\n```")

    # API endpoints
    if api_endpoints:
        lines.append("\n## API Endpoints\n")
        lines.append("| Method | Endpoint | Description |")
        lines.append("|--------|----------|-------------|")
        for ep in api_endpoints:
            if isinstance(ep, dict):
                lines.append(f"| {ep.get('method', 'GET')} | `{ep.get('path', '')}` | {ep.get('description', '')} |")

    # License
    lines.append(f"\n## License\n\n{license_name}")
    if author:
        lines.append(f"\n## Author\n\n{author}")

    readme = "\n".join(lines)
    return {"readme": readme, "lines": len(lines), "format": "markdown"}


# --- Robots.txt Generator ---

@app.post("/api/robots/generate")
async def robots_generate(request: Request):
    """Generate robots.txt from rules."""
    body = await request.json()
    rules = body.get("rules", [{"user_agent": "*", "allow": ["/"], "disallow": []}])
    sitemap_url = body.get("sitemap", "")
    host = body.get("host", "")

    lines = []
    for rule in rules:
        ua = rule.get("user_agent", "*")
        lines.append(f"User-agent: {ua}")
        for allow in rule.get("allow", []):
            lines.append(f"Allow: {allow}")
        for disallow in rule.get("disallow", []):
            lines.append(f"Disallow: {disallow}")
        crawl_delay = rule.get("crawl_delay")
        if crawl_delay:
            lines.append(f"Crawl-delay: {crawl_delay}")
        lines.append("")
    if sitemap_url:
        lines.append(f"Sitemap: {sitemap_url}")
    if host:
        lines.append(f"Host: {host}")

    txt = "\n".join(lines)
    return Response(content=txt, media_type="text/plain")


# --- CSS Gradient Generator ---

@app.get("/api/gradient")
async def css_gradient(
    colors: str = Query("6c63ff,3b82f6", description="Comma-separated hex colors"),
    direction: str = Query("135deg", description="Gradient direction"),
    type: str = Query("linear", description="linear or radial"),
):
    """Generate CSS gradient code from colors."""
    color_list = [f"#{c.strip().lstrip('#')}" for c in colors.split(",") if c.strip()]
    if len(color_list) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 colors")

    color_str = ", ".join(color_list)
    if type == "radial":
        css = f"background: radial-gradient(circle, {color_str});"
    else:
        css = f"background: linear-gradient({direction}, {color_str});"

    stops = "".join(
        '<stop offset="{}%" stop-color="{}"/>'.format(i * 100 // (len(color_list) - 1), c)
        for i, c in enumerate(color_list)
    )
    preview_svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="100">'
        '<defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="0%">'
        + stops +
        '</linearGradient></defs>'
        '<rect width="400" height="100" fill="url(#g)" rx="8"/></svg>'
    )

    return {
        "css": css,
        "colors": color_list,
        "type": type,
        "direction": direction if type == "linear" else "circle",
        "preview_svg": preview_svg,
    }


# --- Social Meta Tags Generator ---

@app.post("/api/metatags/generate")
async def metatags_generate(request: Request):
    """Generate social media meta tags (Open Graph, Twitter Cards)."""
    body = await request.json()
    title = body.get("title", "")
    description = body.get("description", "")
    url = body.get("url", "")
    image = body.get("image", "")
    site_name = body.get("site_name", "")
    twitter_handle = body.get("twitter_handle", "")
    type_ = body.get("type", "website")

    tags = []
    tags.append(f'<meta charset="UTF-8">')
    tags.append(f'<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    if title:
        tags.append(f'<title>{title}</title>')
        tags.append(f'<meta property="og:title" content="{title}">')
        tags.append(f'<meta name="twitter:title" content="{title}">')
    if description:
        tags.append(f'<meta name="description" content="{description}">')
        tags.append(f'<meta property="og:description" content="{description}">')
        tags.append(f'<meta name="twitter:description" content="{description}">')
    if url:
        tags.append(f'<meta property="og:url" content="{url}">')
    if image:
        tags.append(f'<meta property="og:image" content="{image}">')
        tags.append(f'<meta name="twitter:image" content="{image}">')
        tags.append(f'<meta name="twitter:card" content="summary_large_image">')
    else:
        tags.append(f'<meta name="twitter:card" content="summary">')
    if site_name:
        tags.append(f'<meta property="og:site_name" content="{site_name}">')
    if twitter_handle:
        tags.append(f'<meta name="twitter:site" content="{twitter_handle}">')
    tags.append(f'<meta property="og:type" content="{type_}">')

    return {"html": "\n".join(tags), "tags": tags, "count": len(tags)}


# --- Htaccess Generator ---

@app.post("/api/htaccess/generate")
async def htaccess_generate(request: Request):
    """Generate Apache .htaccess rules."""
    body = await request.json()
    redirects = body.get("redirects", [])
    force_https = body.get("force_https", True)
    www_redirect = body.get("www_redirect", "to_www")  # to_www, to_non_www, none
    cache_static = body.get("cache_static", True)
    block_ips = body.get("block_ips", [])
    custom_errors = body.get("custom_errors", {})
    gzip = body.get("gzip", True)

    lines = ["# Generated by ToolPipe API", ""]

    if force_https:
        lines.extend(["# Force HTTPS", "RewriteEngine On", "RewriteCond %{HTTPS} off", "RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]", ""])

    if www_redirect == "to_www":
        lines.extend(["# Redirect to www", "RewriteCond %{HTTP_HOST} !^www\\. [NC]", "RewriteRule ^(.*)$ https://www.%{HTTP_HOST}/$1 [R=301,L]", ""])
    elif www_redirect == "to_non_www":
        lines.extend(["# Redirect to non-www", "RewriteCond %{HTTP_HOST} ^www\\.(.*)$ [NC]", "RewriteRule ^(.*)$ https://%1/$1 [R=301,L]", ""])

    if gzip:
        lines.extend(["# Enable Gzip", "<IfModule mod_deflate.c>", "  AddOutputFilterByType DEFLATE text/html text/css text/javascript application/javascript application/json", "</IfModule>", ""])

    if cache_static:
        lines.extend(["# Cache static files", "<IfModule mod_expires.c>", "  ExpiresActive On", "  ExpiresByType image/png \"access plus 1 month\"", "  ExpiresByType image/jpeg \"access plus 1 month\"", "  ExpiresByType text/css \"access plus 1 week\"", "  ExpiresByType application/javascript \"access plus 1 week\"", "</IfModule>", ""])

    for r in redirects:
        if isinstance(r, dict):
            lines.append(f"Redirect {r.get('code', 301)} {r.get('from', '')} {r.get('to', '')}")
    if redirects:
        lines.append("")

    for ip in block_ips:
        lines.append(f"Deny from {ip}")
    if block_ips:
        lines.append("")

    for code, page in custom_errors.items():
        lines.append(f"ErrorDocument {code} {page}")

    return Response(content="\n".join(lines), media_type="text/plain")


# --- Interactive API Playground ---

@app.get("/playground", response_class=HTMLResponse)
async def api_playground():
    """Interactive API playground for testing all ToolPipe endpoints."""
    return HTMLResponse(inject_snippet("""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>ToolPipe API Playground - Test 180+ Developer APIs</title>
<meta name="description" content="Interactive playground to test ToolPipe's 180+ developer APIs. JSON formatting, QR codes, hashing, UUID generation, and more. Try free, no signup needed.">
<link rel="canonical" href="https://toolpipe.dev/playground">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0a0a0a;color:#e0e0e0;min-height:100vh}
.header{background:#111;border-bottom:1px solid #2a2a2a;padding:16px 24px;display:flex;align-items:center;gap:16px}
.header h1{font-size:1.4rem;color:#fff}
.header a{color:#6c63ff;text-decoration:none;font-size:0.9rem}
.main{display:grid;grid-template-columns:280px 1fr;height:calc(100vh - 56px)}
.sidebar{background:#111;border-right:1px solid #2a2a2a;overflow-y:auto;padding:12px}
.sidebar input{width:100%;padding:10px 12px;background:#1a1a1a;border:1px solid #2a2a2a;border-radius:8px;color:#e0e0e0;font-size:0.9rem;margin-bottom:12px}
.sidebar input:focus{outline:none;border-color:#6c63ff}
.cat-header{font-size:0.75rem;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:0.5px;padding:8px 4px 4px;margin-top:8px}
.ep-btn{display:block;width:100%;text-align:left;padding:8px 12px;background:none;border:none;color:#cbd5e1;font-size:0.85rem;border-radius:6px;cursor:pointer;margin:1px 0}
.ep-btn:hover,.ep-btn.active{background:#1a1a2e;color:#6c63ff}
.ep-btn .method{display:inline-block;width:40px;font-size:0.7rem;font-weight:700;margin-right:6px}
.ep-btn .method.get{color:#22c55e}.ep-btn .method.post{color:#3b82f6}.ep-btn .method.put{color:#f59e0b}.ep-btn .method.delete{color:#ef4444}
.content{padding:24px;overflow-y:auto}
.endpoint-title{font-size:1.3rem;color:#fff;margin-bottom:8px}
.endpoint-desc{color:#94a3b8;margin-bottom:20px;font-size:0.95rem}
.form-group{margin-bottom:16px}
.form-group label{display:block;color:#cbd5e1;font-weight:600;margin-bottom:6px;font-size:0.85rem}
.form-group input,.form-group textarea,.form-group select{width:100%;padding:10px 14px;background:#1a1a1a;border:1px solid #2a2a2a;border-radius:8px;color:#e0e0e0;font-size:0.9rem;font-family:inherit}
.form-group textarea{font-family:'SF Mono',monospace;min-height:120px;resize:vertical}
.form-group input:focus,.form-group textarea:focus{outline:none;border-color:#6c63ff}
.run-btn{background:#6c63ff;color:#fff;border:none;padding:12px 32px;border-radius:8px;font-size:1rem;font-weight:700;cursor:pointer;margin-top:8px}
.run-btn:hover{background:#5b52e0}
.run-btn:disabled{opacity:0.5;cursor:not-allowed}
.result-box{margin-top:20px;background:#111;border:1px solid #2a2a2a;border-radius:12px;overflow:hidden}
.result-header{display:flex;justify-content:space-between;align-items:center;padding:12px 16px;background:#1a1a1a;border-bottom:1px solid #2a2a2a}
.result-header .status{font-weight:700;font-size:0.85rem}
.status.ok{color:#22c55e}.status.err{color:#ef4444}
.result-body{padding:16px;font-family:'SF Mono',monospace;font-size:0.85rem;white-space:pre-wrap;max-height:400px;overflow-y:auto;line-height:1.5;color:#e0e0e0}
.result-body img{max-width:100%;border-radius:8px;margin:8px 0}
.curl-box{margin-top:12px;background:#1a1a1a;border:1px solid #2a2a2a;border-radius:8px;padding:12px 16px;font-family:'SF Mono',monospace;font-size:0.8rem;color:#94a3b8;position:relative}
.curl-box button{position:absolute;top:8px;right:8px;background:#2a2a2a;color:#cbd5e1;border:none;padding:4px 10px;border-radius:4px;font-size:0.75rem;cursor:pointer}
@media(max-width:768px){.main{grid-template-columns:1fr}.sidebar{display:none}}
</style></head><body>
<div class="header">
<h1>API Playground</h1>
<a href="/">Home</a>
<a href="/pricing">Pricing</a>
<a href="/docs">Docs</a>
</div>
<div class="main">
<div class="sidebar">
<input type="text" id="search" placeholder="Search endpoints..." oninput="filterEndpoints(this.value)">
<div id="endpoint-list"></div>
</div>
<div class="content" id="content">
<h2 style="color:#fff;margin-bottom:12px">Welcome to the ToolPipe API Playground</h2>
<p style="color:#94a3b8;margin-bottom:24px">Select an endpoint from the sidebar to start testing. All endpoints are free for up to 100 calls/day.</p>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px">
<div style="background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;padding:20px;cursor:pointer" onclick="loadEndpoint('json_format')">
<h3 style="color:#fff;font-size:1rem;margin-bottom:6px">JSON Formatter</h3><p style="color:#94a3b8;font-size:0.85rem">Format and validate JSON</p></div>
<div style="background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;padding:20px;cursor:pointer" onclick="loadEndpoint('qr_generate')">
<h3 style="color:#fff;font-size:1rem;margin-bottom:6px">QR Code</h3><p style="color:#94a3b8;font-size:0.85rem">Generate QR codes instantly</p></div>
<div style="background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;padding:20px;cursor:pointer" onclick="loadEndpoint('hash_generate')">
<h3 style="color:#fff;font-size:1rem;margin-bottom:6px">Hash Generator</h3><p style="color:#94a3b8;font-size:0.85rem">MD5, SHA-256, and more</p></div>
<div style="background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;padding:20px;cursor:pointer" onclick="loadEndpoint('uuid_generate')">
<h3 style="color:#fff;font-size:1rem;margin-bottom:6px">UUID Generator</h3><p style="color:#94a3b8;font-size:0.85rem">Generate v4 UUIDs</p></div>
<div style="background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;padding:20px;cursor:pointer" onclick="loadEndpoint('placeholder')">
<h3 style="color:#fff;font-size:1rem;margin-bottom:6px">Placeholder Image</h3><p style="color:#94a3b8;font-size:0.85rem">Generate placeholder images</p></div>
<div style="background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;padding:20px;cursor:pointer" onclick="loadEndpoint('favicon')">
<h3 style="color:#fff;font-size:1rem;margin-bottom:6px">Favicon Extractor</h3><p style="color:#94a3b8;font-size:0.85rem">Get favicons from any URL</p></div>
</div>
</div>
</div>

<script>
const ENDPOINTS = [
{id:'json_format',cat:'Data',name:'JSON Format',method:'POST',path:'/json/format',desc:'Format, minify, or validate JSON data',fields:[{name:'json_string',type:'textarea',label:'JSON String',placeholder:'{"key":"value","nested":{"a":1}}'}],bodyKey:'json_string'},
{id:'hash_generate',cat:'Crypto',name:'Hash Generate',method:'POST',path:'/hash/generate',desc:'Generate hash of text (MD5, SHA-256, etc.)',fields:[{name:'text',type:'input',label:'Text',placeholder:'Hello World'},{name:'algorithm',type:'select',label:'Algorithm',options:['sha256','md5','sha1','sha512']}],body:true},
{id:'uuid_generate',cat:'Generators',name:'UUID Generate',method:'GET',path:'/uuid',desc:'Generate a UUID v4',fields:[],body:false},
{id:'qr_generate',cat:'Generators',name:'QR Code',method:'GET',path:'/qr/generate',desc:'Generate a QR code image',fields:[{name:'text',type:'input',label:'Text/URL',placeholder:'https://toolpipe.dev'}],query:true,isImage:true},
{id:'base64_encode',cat:'Encoding',name:'Base64 Encode',method:'POST',path:'/base64/encode',desc:'Encode text to Base64',fields:[{name:'text',type:'textarea',label:'Text',placeholder:'Hello World'}],body:true},
{id:'base64_decode',cat:'Encoding',name:'Base64 Decode',method:'POST',path:'/base64/decode',desc:'Decode Base64 to text',fields:[{name:'text',type:'textarea',label:'Base64 String',placeholder:'SGVsbG8gV29ybGQ='}],body:true},
{id:'markdown_render',cat:'Text',name:'Markdown Render',method:'POST',path:'/markdown/render',desc:'Render Markdown to HTML',fields:[{name:'text',type:'textarea',label:'Markdown',placeholder:'# Hello\\n\\nThis is **bold** and *italic*.'}],body:true},
{id:'text_stats',cat:'Text',name:'Text Stats',method:'POST',path:'/text/stats',desc:'Word count, character count, reading time',fields:[{name:'text',type:'textarea',label:'Text',placeholder:'Enter your text here to analyze...'}],body:true},
{id:'lorem',cat:'Generators',name:'Lorem Ipsum',method:'GET',path:'/lorem',desc:'Generate lorem ipsum text',fields:[{name:'paragraphs',type:'input',label:'Paragraphs',placeholder:'3'}],query:true},
{id:'ip_lookup',cat:'Network',name:'IP Lookup',method:'GET',path:'/ip/lookup',desc:'Get geolocation for an IP address',fields:[{name:'ip',type:'input',label:'IP Address',placeholder:'8.8.8.8'}],query:true},
{id:'dns_lookup',cat:'Network',name:'DNS Lookup',method:'GET',path:'/dns/lookup',desc:'DNS record lookup',fields:[{name:'domain',type:'input',label:'Domain',placeholder:'google.com'},{name:'type',type:'select',label:'Record Type',options:['A','AAAA','MX','NS','TXT','CNAME','SOA']}],query:true},
{id:'password_check',cat:'Security',name:'Password Check',method:'POST',path:'/password/check',desc:'Check password strength and entropy',fields:[{name:'password',type:'input',label:'Password',placeholder:'MyP@ssw0rd!'}],body:true},
{id:'regex_test',cat:'Text',name:'Regex Test',method:'POST',path:'/regex/test',desc:'Test regular expressions against text',fields:[{name:'pattern',type:'input',label:'Pattern',placeholder:'^[a-z]+@[a-z]+\\\\.[a-z]{2,}$'},{name:'text',type:'textarea',label:'Test String',placeholder:'test@example.com'},{name:'flags',type:'input',label:'Flags',placeholder:'i'}],body:true},
{id:'jwt_decode',cat:'Security',name:'JWT Decode',method:'POST',path:'/jwt/decode',desc:'Decode and inspect a JWT token',fields:[{name:'token',type:'textarea',label:'JWT Token',placeholder:'eyJhbGciOiJIUzI1NiIs...'}],body:true},
{id:'color_palette',cat:'Design',name:'Color Palette',method:'GET',path:'/color/palette',desc:'Generate color palettes',fields:[{name:'base',type:'input',label:'Base Color (hex)',placeholder:'6c63ff'},{name:'count',type:'input',label:'Count',placeholder:'5'}],query:true},
{id:'slug_generate',cat:'Text',name:'Slug Generate',method:'POST',path:'/slug/generate',desc:'Generate URL-friendly slugs',fields:[{name:'text',type:'input',label:'Text',placeholder:'Hello World! This is a Test'}],body:true},
{id:'placeholder',cat:'Design',name:'Placeholder Image',method:'GET',path:'/placeholder/300x200',desc:'Generate placeholder images',fields:[{name:'width',type:'input',label:'Width',placeholder:'300'},{name:'height',type:'input',label:'Height',placeholder:'200'},{name:'bg',type:'input',label:'Background (hex)',placeholder:'cccccc'},{name:'text',type:'input',label:'Text',placeholder:'300x200'}],customUrl:true,isImage:true},
{id:'favicon',cat:'Web',name:'Favicon Extractor',method:'GET',path:'/favicon',desc:'Extract favicon from any website',fields:[{name:'url',type:'input',label:'Website URL',placeholder:'github.com'}],query:true},
{id:'metatags',cat:'Web',name:'Meta Tags Generator',method:'POST',path:'/metatags/generate',desc:'Generate Open Graph and Twitter Card meta tags',fields:[{name:'title',type:'input',label:'Title',placeholder:'My Website'},{name:'description',type:'textarea',label:'Description',placeholder:'A great website'},{name:'url',type:'input',label:'URL',placeholder:'https://example.com'},{name:'image',type:'input',label:'Image URL',placeholder:'https://example.com/og.jpg'}],body:true},
{id:'gradient',cat:'Design',name:'CSS Gradient',method:'GET',path:'/gradient',desc:'Generate CSS gradient code',fields:[{name:'colors',type:'input',label:'Colors (comma-separated hex)',placeholder:'6c63ff,3b82f6,22c55e'},{name:'direction',type:'input',label:'Direction',placeholder:'135deg'},{name:'type',type:'select',label:'Type',options:['linear','radial']}],query:true},
{id:'crontab',cat:'DevOps',name:'Crontab Generator',method:'POST',path:'/crontab/generate',desc:'Generate cron expressions from English',fields:[{name:'description',type:'input',label:'Description',placeholder:'Every Monday at 9am'}],body:true},
{id:'sql_format',cat:'Data',name:'SQL Format',method:'POST',path:'/sql/format',desc:'Format SQL queries',fields:[{name:'sql',type:'textarea',label:'SQL Query',placeholder:'SELECT * FROM users WHERE id=1 AND name="john" ORDER BY created_at DESC'}],body:true},
{id:'diff',cat:'Text',name:'Text Diff',method:'POST',path:'/diff/generate',desc:'Generate diff between two texts',fields:[{name:'text1',type:'textarea',label:'Text 1',placeholder:'Hello World'},{name:'text2',type:'textarea',label:'Text 2',placeholder:'Hello Universe'}],body:true},
{id:'mock',cat:'Generators',name:'Mock Data',method:'POST',path:'/mock/generate',desc:'Generate mock data (users, products, etc.)',fields:[{name:'template',type:'select',label:'Template',options:['user','product','order','comment','post']},{name:'count',type:'input',label:'Count',placeholder:'5'}],body:true},
{id:'myip',cat:'Network',name:'My IP',method:'GET',path:'/myip',desc:'Get your IP address',fields:[],body:false},
{id:'sitemap',cat:'Web',name:'Sitemap Generator',method:'POST',path:'/sitemap/generate',desc:'Generate XML sitemap',fields:[{name:'base_url',type:'input',label:'Base URL',placeholder:'https://example.com'},{name:'urls_text',type:'textarea',label:'URLs (one per line)',placeholder:'/\\n/about\\n/pricing\\n/docs'}],body:true,customBody:true},
{id:'readme',cat:'Generators',name:'README Generator',method:'POST',path:'/readme/generate',desc:'Generate README.md from project info',fields:[{name:'name',type:'input',label:'Project Name',placeholder:'My Project'},{name:'description',type:'textarea',label:'Description',placeholder:'A tool that does X'},{name:'install',type:'input',label:'Install Command',placeholder:'npm install my-project'},{name:'license',type:'input',label:'License',placeholder:'MIT'}],body:true},
];

const categories = {};
ENDPOINTS.forEach(ep => {
  if (!categories[ep.cat]) categories[ep.cat] = [];
  categories[ep.cat].push(ep);
});

function renderSidebar(filter='') {
  const el = document.getElementById('endpoint-list');
  let html = '';
  const f = filter.toLowerCase();
  for (const [cat, eps] of Object.entries(categories).sort()) {
    const filtered = eps.filter(e => !f || e.name.toLowerCase().includes(f) || e.path.toLowerCase().includes(f));
    if (!filtered.length) continue;
    html += '<div class="cat-header">' + cat + '</div>';
    filtered.forEach(ep => {
      html += '<button class="ep-btn" id="btn-'+ep.id+'" onclick="loadEndpoint(\\''+ep.id+'\\')"><span class="method '+ep.method.toLowerCase()+'">'+ep.method+'</span>'+ep.name+'</button>';
    });
  }
  el.innerHTML = html;
}
renderSidebar();

function filterEndpoints(v) { renderSidebar(v); }

function loadEndpoint(id) {
  const ep = ENDPOINTS.find(e => e.id === id);
  if (!ep) return;
  document.querySelectorAll('.ep-btn').forEach(b => b.classList.remove('active'));
  const btn = document.getElementById('btn-'+id);
  if (btn) btn.classList.add('active');

  let html = '<h2 class="endpoint-title"><span class="method '+ep.method.toLowerCase()+'" style="font-size:0.9rem;margin-right:8px">'+ep.method+'</span>/api'+ep.path+'</h2>';
  html += '<p class="endpoint-desc">'+ep.desc+'</p>';
  html += '<form id="ep-form" onsubmit="return runEndpoint(event,\\''+id+'\\')">';
  ep.fields.forEach(f => {
    html += '<div class="form-group"><label>'+f.label+'</label>';
    if (f.type === 'textarea') {
      html += '<textarea name="'+f.name+'" placeholder="'+(f.placeholder||'')+'"></textarea>';
    } else if (f.type === 'select') {
      html += '<select name="'+f.name+'">';
      f.options.forEach(o => html += '<option value="'+o+'">'+o+'</option>');
      html += '</select>';
    } else {
      html += '<input type="text" name="'+f.name+'" placeholder="'+(f.placeholder||'')+'">';
    }
    html += '</div>';
  });
  html += '<button type="submit" class="run-btn" id="run-btn">Run</button></form>';
  html += '<div id="curl-display"></div>';
  html += '<div id="result-display"></div>';
  document.getElementById('content').innerHTML = html;
}

async function runEndpoint(e, id) {
  e.preventDefault();
  const ep = ENDPOINTS.find(e => e.id === id);
  const form = document.getElementById('ep-form');
  const fd = new FormData(form);
  const data = {};
  for (const [k,v] of fd.entries()) { if(v) data[k] = v; }

  const btn = document.getElementById('run-btn');
  btn.disabled = true;
  btn.textContent = 'Running...';

  let url, opts = {headers:{}};
  const base = '/api';

  if (ep.id === 'placeholder') {
    const w = data.width || '300';
    const h = data.height || '200';
    let pUrl = base + '/placeholder/' + w + 'x' + h;
    const params = new URLSearchParams();
    if (data.bg) params.set('bg', data.bg);
    if (data.text) params.set('text', data.text);
    if (params.toString()) pUrl += '?' + params;
    url = pUrl;
    opts.method = 'GET';
  } else if (ep.id === 'sitemap' && ep.customBody) {
    url = base + ep.path;
    const urls = (data.urls_text || '').split('\\n').filter(u => u.trim());
    opts.method = 'POST';
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify({base_url: data.base_url, urls: urls});
  } else if (ep.query || ep.method === 'GET') {
    const params = new URLSearchParams(data);
    url = base + ep.path + (params.toString() ? '?' + params : '');
    opts.method = 'GET';
  } else {
    url = base + ep.path;
    opts.method = 'POST';
    opts.headers['Content-Type'] = 'application/json';
    if (ep.bodyKey) {
      opts.body = JSON.stringify({[ep.bodyKey]: data[ep.bodyKey]});
    } else {
      opts.body = JSON.stringify(data);
    }
  }

  // Show curl
  let curl = 'curl';
  if (opts.method !== 'GET') curl += ' -X ' + opts.method;
  curl += ' "' + location.origin + url + '"';
  if (opts.body) curl += " -H 'Content-Type: application/json' -d '" + opts.body + "'";
  document.getElementById('curl-display').innerHTML = '<div class="curl-box"><button onclick="navigator.clipboard.writeText(this.parentElement.textContent.replace(\\'Copy\\',\\'\\'));this.textContent=\\'Copied!\\'">Copy</button>' + curl + '</div>';

  try {
    const t0 = performance.now();
    const resp = await fetch(url, opts);
    const ms = Math.round(performance.now() - t0);
    const status = resp.status;
    const ok = status >= 200 && status < 400;
    const ct = resp.headers.get('content-type') || '';

    let bodyHtml;
    if (ep.isImage && ok && ct.includes('image')) {
      const blob = await resp.blob();
      const imgUrl = URL.createObjectURL(blob);
      bodyHtml = '<img src="'+imgUrl+'" alt="result">';
    } else if (ct.includes('xml') || ct.includes('text/plain')) {
      const text = await resp.text();
      bodyHtml = text.replace(/</g,'&lt;').replace(/>/g,'&gt;');
    } else {
      const json = await resp.json();
      bodyHtml = JSON.stringify(json, null, 2);
    }

    document.getElementById('result-display').innerHTML =
      '<div class="result-box"><div class="result-header"><span class="status '+(ok?'ok':'err')+'">'+status+'</span><span style="color:#64748b;font-size:0.8rem">'+ms+'ms</span></div><div class="result-body">'+bodyHtml+'</div></div>';
  } catch(err) {
    document.getElementById('result-display').innerHTML =
      '<div class="result-box"><div class="result-header"><span class="status err">Error</span></div><div class="result-body">'+err.message+'</div></div>';
  }
  btn.disabled = false;
  btn.textContent = 'Run';
  return false;
}
</script>
</body></html>"""))


# --- AI/Text Processing APIs ---

@app.post("/api/text/summarize")
async def text_summarize(request: Request):
    """Summarize text using extractive summarization (no AI model needed)."""
    body = await request.json()
    text = body.get("text", "")
    max_sentences = body.get("max_sentences", 3)
    if not text:
        raise HTTPException(status_code=400, detail="text is required")
    import re as _re
    sentences = _re.split(r'(?<=[.!?])\s+', text.strip())
    if len(sentences) <= max_sentences:
        return {"summary": text, "sentence_count": len(sentences), "original_sentences": len(sentences)}
    # Score sentences by word frequency
    words = _re.findall(r'\w+', text.lower())
    freq = {}
    stopwords = {'the','a','an','is','are','was','were','be','been','being','have','has','had','do','does','did','will','would','could','should','may','might','shall','can','need','dare','ought','used','to','of','in','for','on','with','at','by','from','as','into','through','during','before','after','above','below','between','out','off','over','under','again','further','then','once','here','there','when','where','why','how','all','each','every','both','few','more','most','other','some','such','no','nor','not','only','own','same','so','than','too','very','just','because','but','and','or','if','while','that','this','it','its','i','me','my','we','our','you','your','he','him','his','she','her','they','them','their','what','which','who','whom'}
    for w in words:
        if w not in stopwords and len(w) > 2:
            freq[w] = freq.get(w, 0) + 1
    scores = []
    for i, s in enumerate(sentences):
        s_words = _re.findall(r'\w+', s.lower())
        score = sum(freq.get(w, 0) for w in s_words)
        if i == 0:
            score *= 1.5  # First sentence bonus
        scores.append((i, score, s))
    scores.sort(key=lambda x: x[1], reverse=True)
    top = sorted(scores[:max_sentences], key=lambda x: x[0])
    summary = " ".join(s for _, _, s in top)
    return {"summary": summary, "sentence_count": len(top), "original_sentences": len(sentences)}


@app.post("/api/text/keywords")
async def text_keywords(request: Request):
    """Extract keywords from text using TF-based scoring."""
    body = await request.json()
    text = body.get("text", "")
    top_n = min(body.get("top_n", 10), 50)
    if not text:
        raise HTTPException(status_code=400, detail="text is required")
    import re as _re
    words = _re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    stopwords = {'the','and','for','are','but','not','you','all','any','can','had','her','was','one','our','out','has','its','let','say','she','too','use','way','who','how','man','new','now','old','see','get','make','like','just','over','such','take','than','them','very','when','come','could','than','look','only','into','year','also','back','been','call','what','with','this','that','have','from','they','will','would','there','their','which','about','after','other','these','being','first','think','those','might','where','while','still','every','should','before','through','between','because','through','before','between'}
    filtered = [w for w in words if w not in stopwords]
    freq = {}
    for w in filtered:
        freq[w] = freq.get(w, 0) + 1
    sorted_kw = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return {"keywords": [{"word": w, "count": c, "relevance": round(c / max(len(filtered), 1), 4)} for w, c in sorted_kw], "total_words": len(words), "unique_words": len(freq)}


@app.post("/api/text/readability")
async def text_readability(request: Request):
    """Calculate readability scores (Flesch-Kincaid, Coleman-Liau, ARI)."""
    body = await request.json()
    text = body.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="text is required")
    import re as _re
    sentences = _re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    words = _re.findall(r'\b\w+\b', text)
    syllable_count = 0
    for word in words:
        w = word.lower()
        count = 0
        vowels = 'aeiouy'
        if w[0] in vowels:
            count += 1
        for i in range(1, len(w)):
            if w[i] in vowels and w[i-1] not in vowels:
                count += 1
        if w.endswith('e'):
            count -= 1
        if count == 0:
            count = 1
        syllable_count += count
    n_sent = max(len(sentences), 1)
    n_words = max(len(words), 1)
    chars = sum(len(w) for w in words)
    # Flesch-Kincaid Grade Level
    fk_grade = 0.39 * (n_words / n_sent) + 11.8 * (syllable_count / n_words) - 15.59
    # Flesch Reading Ease
    fk_ease = 206.835 - 1.015 * (n_words / n_sent) - 84.6 * (syllable_count / n_words)
    # Coleman-Liau Index
    L = (chars / n_words) * 100
    S = (n_sent / n_words) * 100
    cli = 0.0588 * L - 0.296 * S - 15.8
    # Automated Readability Index
    ari = 4.71 * (chars / n_words) + 0.5 * (n_words / n_sent) - 21.43
    return {
        "flesch_kincaid_grade": round(fk_grade, 1),
        "flesch_reading_ease": round(max(0, min(100, fk_ease)), 1),
        "coleman_liau_index": round(cli, 1),
        "automated_readability_index": round(ari, 1),
        "stats": {"sentences": n_sent, "words": n_words, "syllables": syllable_count, "characters": chars},
        "difficulty": "Easy" if fk_ease >= 60 else "Moderate" if fk_ease >= 30 else "Difficult"
    }


# --- Data Transform APIs ---

@app.post("/api/transform/json-to-csv")
async def json_to_csv(request: Request):
    """Convert JSON array to CSV format."""
    body = await request.json()
    data = body.get("data", [])
    delimiter = body.get("delimiter", ",")
    if not isinstance(data, list) or not data:
        raise HTTPException(status_code=400, detail="data must be a non-empty JSON array")
    if not isinstance(data[0], dict):
        raise HTTPException(status_code=400, detail="Array elements must be objects")
    headers = list(data[0].keys())
    for item in data[1:]:
        for k in item:
            if k not in headers:
                headers.append(k)
    lines = [delimiter.join(headers)]
    for item in data:
        row = []
        for h in headers:
            val = str(item.get(h, ""))
            if delimiter in val or '"' in val or '\n' in val:
                val = '"' + val.replace('"', '""') + '"'
            row.append(val)
        lines.append(delimiter.join(row))
    csv_text = "\n".join(lines)
    return {"csv": csv_text, "rows": len(data), "columns": len(headers), "headers": headers}


@app.post("/api/transform/csv-to-json")
async def csv_to_json_transform(request: Request):
    """Convert CSV text to JSON array."""
    body = await request.json()
    csv_text = body.get("csv", "")
    delimiter = body.get("delimiter", ",")
    if not csv_text:
        raise HTTPException(status_code=400, detail="csv is required")
    import csv as _csv
    reader = _csv.DictReader(io.StringIO(csv_text), delimiter=delimiter)
    rows = list(reader)
    return {"data": rows, "rows": len(rows), "columns": reader.fieldnames}


@app.post("/api/transform/xml-to-json")
async def xml_to_json_transform(request: Request):
    """Convert XML to JSON."""
    body = await request.json()
    xml_text = body.get("xml", "")
    if not xml_text:
        raise HTTPException(status_code=400, detail="xml is required")
    import xml.etree.ElementTree as ET
    def elem_to_dict(elem):
        result = {}
        if elem.attrib:
            result["@attributes"] = dict(elem.attrib)
        if elem.text and elem.text.strip():
            if not list(elem):
                return elem.text.strip()
            result["#text"] = elem.text.strip()
        for child in elem:
            child_data = elem_to_dict(child)
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        return result or None
    try:
        root = ET.fromstring(xml_text)
        return {"json": {root.tag: elem_to_dict(root)}}
    except ET.ParseError as e:
        raise HTTPException(status_code=400, detail=f"Invalid XML: {e}")


# --- Code Generation APIs ---

@app.post("/api/generate/typescript-interface")
async def generate_ts_interface(request: Request):
    """Generate TypeScript interface from JSON object."""
    body = await request.json()
    json_data = body.get("data", body.get("json"))
    name = body.get("name", "Generated")
    if json_data is None:
        raise HTTPException(status_code=400, detail="data (JSON object) is required")
    def infer_type(val, depth=0):
        if val is None:
            return "null"
        if isinstance(val, bool):
            return "boolean"
        if isinstance(val, int) or isinstance(val, float):
            return "number"
        if isinstance(val, str):
            return "string"
        if isinstance(val, list):
            if not val:
                return "any[]"
            types = set(infer_type(v, depth+1) for v in val[:5])
            if len(types) == 1:
                return f"{types.pop()}[]"
            return f"({' | '.join(types)})[]"
        if isinstance(val, dict):
            if depth > 3:
                return "Record<string, any>"
            props = []
            for k, v in val.items():
                props.append(f"  {'  ' * depth}{k}: {infer_type(v, depth+1)};")
            return "{\n" + "\n".join(props) + f"\n{'  ' * depth}}}"
        return "any"
    if isinstance(json_data, dict):
        props = []
        for k, v in json_data.items():
            props.append(f"  {k}: {infer_type(v, 1)};")
        interface = f"interface {name} {{\n" + "\n".join(props) + "\n}"
    elif isinstance(json_data, list) and json_data and isinstance(json_data[0], dict):
        merged = {}
        for item in json_data[:10]:
            for k, v in item.items():
                if k not in merged:
                    merged[k] = v
        props = []
        for k, v in merged.items():
            props.append(f"  {k}: {infer_type(v, 1)};")
        interface = f"interface {name} {{\n" + "\n".join(props) + "\n}"
    else:
        interface = f"type {name} = {infer_type(json_data)};"
    return {"typescript": interface, "name": name}


@app.post("/api/generate/sql-create")
async def generate_sql_create(request: Request):
    """Generate SQL CREATE TABLE from JSON schema or sample data."""
    body = await request.json()
    table_name = body.get("table", "my_table")
    data = body.get("data")
    columns = body.get("columns")
    dialect = body.get("dialect", "postgresql")
    if columns:
        col_defs = []
        for col in columns:
            name = col.get("name", "col")
            dtype = col.get("type", "TEXT")
            nullable = col.get("nullable", True)
            pk = col.get("primary_key", False)
            default = col.get("default")
            line = f"  {name} {dtype.upper()}"
            if pk:
                line += " PRIMARY KEY"
            if not nullable:
                line += " NOT NULL"
            if default is not None:
                line += f" DEFAULT {default}"
            col_defs.append(line)
    elif data and isinstance(data, (dict, list)):
        sample = data[0] if isinstance(data, list) else data
        col_defs = []
        type_map = {str: "TEXT", int: "INTEGER", float: "REAL", bool: "BOOLEAN"}
        for k, v in sample.items():
            sql_type = type_map.get(type(v), "TEXT")
            col_defs.append(f"  {k} {sql_type}")
    else:
        raise HTTPException(status_code=400, detail="Provide 'columns' or 'data'")
    sql = f"CREATE TABLE {table_name} (\n" + ",\n".join(col_defs) + "\n);"
    return {"sql": sql, "table": table_name, "column_count": len(col_defs), "dialect": dialect}


# --- Security/Crypto APIs ---

@app.post("/api/security/csp-generate")
async def csp_generate(request: Request):
    """Generate Content Security Policy header from rules."""
    body = await request.json()
    directives = body.get("directives", {})
    report_uri = body.get("report_uri")
    report_only = body.get("report_only", False)
    if not directives:
        directives = {
            "default-src": ["'self'"],
            "script-src": ["'self'"],
            "style-src": ["'self'", "'unsafe-inline'"],
            "img-src": ["'self'", "data:", "https:"],
            "font-src": ["'self'"],
            "connect-src": ["'self'"],
            "frame-ancestors": ["'none'"],
            "base-uri": ["'self'"],
            "form-action": ["'self'"],
        }
    parts = []
    for directive, values in directives.items():
        if isinstance(values, list):
            parts.append(f"{directive} {' '.join(values)}")
        else:
            parts.append(f"{directive} {values}")
    if report_uri:
        parts.append(f"report-uri {report_uri}")
    csp = "; ".join(parts)
    header_name = "Content-Security-Policy-Report-Only" if report_only else "Content-Security-Policy"
    return {"csp": csp, "header_name": header_name, "header": f"{header_name}: {csp}", "directives_count": len(directives)}


@app.post("/api/security/cors-headers")
async def cors_headers_generate(request: Request):
    """Generate CORS headers configuration."""
    body = await request.json()
    origins = body.get("origins", ["*"])
    methods = body.get("methods", ["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    headers_list = body.get("headers", ["Content-Type", "Authorization"])
    credentials = body.get("credentials", False)
    max_age = body.get("max_age", 86400)
    result_headers = {
        "Access-Control-Allow-Origin": ", ".join(origins) if len(origins) <= 1 else origins[0],
        "Access-Control-Allow-Methods": ", ".join(methods),
        "Access-Control-Allow-Headers": ", ".join(headers_list),
        "Access-Control-Max-Age": str(max_age),
    }
    if credentials:
        result_headers["Access-Control-Allow-Credentials"] = "true"
    nginx = f"""location /api {{
    add_header 'Access-Control-Allow-Origin' '{origins[0]}';
    add_header 'Access-Control-Allow-Methods' '{", ".join(methods)}';
    add_header 'Access-Control-Allow-Headers' '{", ".join(headers_list)}';
    add_header 'Access-Control-Max-Age' '{max_age}';
}}"""
    return {"headers": result_headers, "nginx_config": nginx}


# --- Encoding/Hashing APIs ---

@app.get("/api/encode/url")
async def url_encode(text: str = Query(...)):
    """URL-encode a string."""
    from urllib.parse import quote
    return {"original": text, "encoded": quote(text, safe="")}


@app.get("/api/decode/url")
async def url_decode(text: str = Query(...)):
    """URL-decode a string."""
    from urllib.parse import unquote
    return {"original": text, "decoded": unquote(text)}


@app.get("/api/encode/html")
async def html_encode(text: str = Query(...)):
    """HTML-encode a string."""
    import html as _html
    return {"original": text, "encoded": _html.escape(text)}


@app.get("/api/decode/html")
async def html_decode(text: str = Query(...)):
    """HTML-decode a string."""
    import html as _html
    return {"original": text, "decoded": _html.unescape(text)}


@app.get("/api/hash/file")
async def hash_text_multiple(text: str = Query(...)):
    """Generate multiple hash digests for a string at once."""
    data = text.encode()
    return {
        "input": text,
        "md5": hashlib.md5(data).hexdigest(),
        "sha1": hashlib.sha1(data).hexdigest(),
        "sha256": hashlib.sha256(data).hexdigest(),
        "sha512": hashlib.sha512(data).hexdigest(),
        "blake2b": hashlib.blake2b(data).hexdigest(),
        "blake2s": hashlib.blake2s(data).hexdigest(),
    }


# --- Network/Web APIs ---

@app.get("/api/ssl/check")
async def ssl_check(domain: str = Query(...)):
    """Check SSL certificate details for a domain."""
    import ssl
    import socket
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
            s.settimeout(5)
            s.connect((domain, 443))
            cert = s.getpeercert()
        subject = dict(x[0] for x in cert.get("subject", ()))
        issuer = dict(x[0] for x in cert.get("issuer", ()))
        not_before = cert.get("notBefore", "")
        not_after = cert.get("notAfter", "")
        sans = []
        for san_type, san_value in cert.get("subjectAltName", ()):
            sans.append(san_value)
        return {
            "domain": domain,
            "valid": True,
            "subject": subject,
            "issuer": issuer,
            "not_before": not_before,
            "not_after": not_after,
            "serial_number": cert.get("serialNumber"),
            "version": cert.get("version"),
            "sans": sans,
        }
    except Exception as e:
        return {"domain": domain, "valid": False, "error": str(e)}


@app.get("/api/whois")
async def whois_lookup(domain: str = Query(...)):
    """Basic WHOIS information for a domain."""
    import subprocess
    try:
        result = subprocess.run(["whois", domain], capture_output=True, text=True, timeout=10)
        output = result.stdout
        info = {}
        for line in output.splitlines():
            if ":" in line and not line.startswith("%") and not line.startswith("#"):
                key, _, val = line.partition(":")
                key = key.strip().lower().replace(" ", "_")
                val = val.strip()
                if key and val and key not in info:
                    info[key] = val
        return {"domain": domain, "raw": output[:3000], "parsed": info}
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="whois command not available")
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="WHOIS lookup timed out")


@app.get("/api/headers/get")
async def get_http_headers(url: str = Query(...)):
    """Fetch HTTP response headers from a URL."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            resp = await client.head(url, headers={"User-Agent": "ToolPipe-Bot/1.0"})
            return {
                "url": str(resp.url),
                "status_code": resp.status_code,
                "headers": dict(resp.headers),
                "redirected": str(resp.url) != url,
            }
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch: {e}")


# --- Utility/Developer APIs ---

@app.get("/api/timestamp")
async def timestamp_info(ts: Optional[float] = None):
    """Get current timestamp or convert a Unix timestamp to multiple formats."""
    if ts is None:
        ts = time.time()
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    return {
        "unix": ts,
        "unix_ms": int(ts * 1000),
        "iso8601": dt.isoformat(),
        "rfc2822": dt.strftime("%a, %d %b %Y %H:%M:%S +0000"),
        "date": dt.strftime("%Y-%m-%d"),
        "time": dt.strftime("%H:%M:%S"),
        "day_of_week": dt.strftime("%A"),
        "day_of_year": dt.timetuple().tm_yday,
        "week_number": dt.isocalendar()[1],
        "utc": True,
    }


@app.post("/api/diff/text-detailed")
async def diff_text_detailed(request: Request):
    """Detailed text diff with line-by-line changes."""
    body = await request.json()
    text1 = body.get("text1", body.get("original", ""))
    text2 = body.get("text2", body.get("modified", ""))
    if not text1 and not text2:
        raise HTTPException(status_code=400, detail="text1 and text2 required")
    import difflib
    lines1 = text1.splitlines(keepends=True)
    lines2 = text2.splitlines(keepends=True)
    unified = list(difflib.unified_diff(lines1, lines2, fromfile="original", tofile="modified", lineterm=""))
    additions = sum(1 for l in unified if l.startswith("+") and not l.startswith("+++"))
    deletions = sum(1 for l in unified if l.startswith("-") and not l.startswith("---"))
    return {
        "diff": "\n".join(unified),
        "additions": additions,
        "deletions": deletions,
        "changes": additions + deletions,
        "identical": additions == 0 and deletions == 0,
    }


@app.post("/api/generate/package-json")
async def generate_package_json(request: Request):
    """Generate a package.json file from project metadata."""
    body = await request.json()
    name = body.get("name", "my-project")
    version = body.get("version", "1.0.0")
    description = body.get("description", "")
    author = body.get("author", "")
    license_val = body.get("license", "MIT")
    deps = body.get("dependencies", {})
    dev_deps = body.get("devDependencies", {})
    scripts = body.get("scripts", {"start": "node index.js", "test": "echo \"Error: no test\" && exit 1"})
    main = body.get("main", "index.js")
    pkg = {
        "name": name,
        "version": version,
        "description": description,
        "main": main,
        "scripts": scripts,
        "author": author,
        "license": license_val,
    }
    if deps:
        pkg["dependencies"] = deps
    if dev_deps:
        pkg["devDependencies"] = dev_deps
    return {"package_json": json.dumps(pkg, indent=2), "parsed": pkg}


@app.post("/api/generate/github-actions")
async def generate_github_actions(request: Request):
    """Generate a GitHub Actions workflow YAML."""
    body = await request.json()
    name = body.get("name", "CI")
    language = body.get("language", "node").lower()
    trigger = body.get("trigger", "push")
    node_version = body.get("node_version", "20")
    python_version = body.get("python_version", "3.12")
    if language in ("node", "javascript", "typescript"):
        workflow = f"""name: {name}

on:
  {trigger}:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '{node_version}'
          cache: 'npm'
      - run: npm ci
      - run: npm test
      - run: npm run build --if-present
"""
    elif language == "python":
        workflow = f"""name: {name}

on:
  {trigger}:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '{python_version}'
      - run: pip install -r requirements.txt
      - run: python -m pytest
"""
    else:
        workflow = f"""name: {name}

on:
  {trigger}:
    branches: [main, master]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "Add your build steps here"
"""
    return {"workflow": workflow, "language": language, "filename": f".github/workflows/{name.lower().replace(' ', '-')}.yml"}


@app.post("/api/generate/nginx-config")
async def generate_nginx_config(request: Request):
    """Generate an Nginx server configuration."""
    body = await request.json()
    domain = body.get("domain", "example.com")
    upstream_port = body.get("upstream_port", 3000)
    ssl = body.get("ssl", True)
    static_root = body.get("static_root")
    gzip = body.get("gzip", True)
    config_parts = []
    if gzip:
        config_parts.append("""    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml;
    gzip_min_length 256;""")
    if ssl:
        config = f"""server {{
    listen 80;
    server_name {domain};
    return 301 https://$server_name$request_uri;
}}

server {{
    listen 443 ssl http2;
    server_name {domain};

    ssl_certificate /etc/letsencrypt/live/{domain}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{domain}/privkey.pem;

{'    ' + chr(10).join(config_parts) if config_parts else ''}

    location / {{
        proxy_pass http://127.0.0.1:{upstream_port};
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }}
{f'''
    location /static {{
        alias {static_root};
        expires 30d;
        add_header Cache-Control "public, immutable";
    }}''' if static_root else ''}
}}"""
    else:
        config = f"""server {{
    listen 80;
    server_name {domain};

{'    ' + chr(10).join(config_parts) if config_parts else ''}

    location / {{
        proxy_pass http://127.0.0.1:{upstream_port};
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }}
}}"""
    return {"config": config, "domain": domain, "ssl": ssl}


@app.post("/api/generate/docker-compose")
async def generate_docker_compose(request: Request):
    """Generate a docker-compose.yml from service definitions."""
    body = await request.json()
    services = body.get("services", [])
    version = body.get("version", "3.8")
    if not services:
        services = [{"name": "app", "image": "node:20-alpine", "ports": ["3000:3000"], "environment": {"NODE_ENV": "production"}}]
    svc_yaml = {}
    for svc in services:
        name = svc.get("name", "service")
        entry = {}
        if "image" in svc:
            entry["image"] = svc["image"]
        if "build" in svc:
            entry["build"] = svc["build"]
        if "ports" in svc:
            entry["ports"] = svc["ports"]
        if "environment" in svc:
            entry["environment"] = svc["environment"]
        if "volumes" in svc:
            entry["volumes"] = svc["volumes"]
        if "depends_on" in svc:
            entry["depends_on"] = svc["depends_on"]
        if "restart" not in svc:
            entry["restart"] = "unless-stopped"
        else:
            entry["restart"] = svc["restart"]
        svc_yaml[name] = entry
    import yaml
    compose = {"version": version, "services": svc_yaml}
    try:
        yaml_str = yaml.dump(compose, default_flow_style=False, sort_keys=False)
    except Exception:
        yaml_str = json.dumps(compose, indent=2)
    return {"docker_compose": yaml_str, "service_count": len(services)}


# --- Premium API Endpoints (v1.13.0) ---

@app.post("/api/code/review")
async def code_review(request: Request):
    """Analyze code for bugs, security issues, and improvements. Supports Python, JS, TS, Go, Rust, Java."""
    body = await request.json()
    code = body.get("code", "")
    language = body.get("language", "auto")
    if not code:
        raise HTTPException(status_code=400, detail="code field required")
    if len(code) > 50000:
        raise HTTPException(status_code=400, detail="Code too long (max 50KB)")

    issues = []
    suggestions = []
    stats = {"lines": len(code.splitlines()), "chars": len(code), "language": language}

    # Detect language if auto
    if language == "auto":
        if "def " in code and "import " in code:
            language = "python"
        elif "function " in code or "const " in code or "=>" in code:
            language = "javascript"
        elif "func " in code and "package " in code:
            language = "go"
        elif "fn " in code and "let mut" in code:
            language = "rust"
        elif "public class" in code:
            language = "java"
        else:
            language = "unknown"
        stats["language"] = language

    # Security checks (language-agnostic)
    security_patterns = [
        (r'eval\s*\(', "eval() usage detected: potential code injection vulnerability", "critical"),
        (r'exec\s*\(', "exec() usage detected: potential code injection", "critical"),
        (r'os\.system\s*\(', "os.system() usage: use subprocess with shell=False instead", "high"),
        (r'subprocess\.call\(.*shell\s*=\s*True', "subprocess with shell=True: command injection risk", "high"),
        (r'pickle\.loads?\s*\(', "pickle deserialization: potential arbitrary code execution", "critical"),
        (r'yaml\.load\s*\([^)]*\)(?!.*Loader)', "yaml.load without SafeLoader: code execution risk", "high"),
        (r'innerHTML\s*=', "innerHTML assignment: potential XSS vulnerability", "high"),
        (r'document\.write\s*\(', "document.write: potential XSS", "medium"),
        (r'SELECT.*\+.*["\']', "String concatenation in SQL: potential SQL injection", "critical"),
        (r'f["\'].*SELECT.*\{', "f-string in SQL query: potential SQL injection", "critical"),
        (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password detected", "critical"),
        (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key detected", "high"),
        (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret detected", "high"),
        (r'console\.log\(', "console.log left in code", "low"),
        (r'print\((?!.*#)', "print() statement (remove for production)", "low"),
        (r'TODO|FIXME|HACK|XXX', "TODO/FIXME marker found", "info"),
        (r'except\s*:', "Bare except clause: catches all exceptions including SystemExit", "medium"),
        (r'catch\s*\(\s*\)', "Empty catch block: silently swallows errors", "medium"),
        (r'\.env', ".env file reference: ensure not committed to version control", "medium"),
    ]
    for pattern, msg, severity in security_patterns:
        matches = list(re.finditer(pattern, code, re.IGNORECASE))
        for m in matches:
            line_num = code[:m.start()].count('\n') + 1
            issues.append({"line": line_num, "message": msg, "severity": severity, "pattern": pattern})

    # Code quality checks
    lines = code.splitlines()
    long_lines = [(i+1, len(line)) for i, line in enumerate(lines) if len(line) > 120]
    if long_lines:
        suggestions.append({"type": "style", "message": f"{len(long_lines)} lines exceed 120 chars", "lines": long_lines[:5]})

    empty_blocks = len(re.findall(r'(if|for|while|def|function)\s*.*:\s*\n\s*pass', code))
    if empty_blocks:
        suggestions.append({"type": "quality", "message": f"{empty_blocks} empty code blocks found"})

    # Complexity estimate
    complexity = {
        "functions": len(re.findall(r'(def |function |fn |func )\w+', code)),
        "classes": len(re.findall(r'(class )\w+', code)),
        "loops": len(re.findall(r'(for |while )', code)),
        "conditionals": len(re.findall(r'(if |else |elif |else if)', code)),
        "imports": len(re.findall(r'(import |from .* import |require\(|use )', code)),
    }

    critical_count = sum(1 for i in issues if i["severity"] == "critical")
    high_count = sum(1 for i in issues if i["severity"] == "high")
    score = max(0, 100 - critical_count * 20 - high_count * 10 - len(long_lines) - empty_blocks * 5)

    return {
        "score": min(100, score),
        "grade": "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "D" if score >= 40 else "F",
        "issues": issues,
        "suggestions": suggestions,
        "complexity": complexity,
        "stats": stats,
    }


@app.post("/api/code/explain")
async def code_explain(request: Request):
    """Generate a plain-English explanation of code, including function signatures, flow, and purpose."""
    body = await request.json()
    code = body.get("code", "")
    if not code:
        raise HTTPException(status_code=400, detail="code field required")
    if len(code) > 50000:
        raise HTTPException(status_code=400, detail="Code too long (max 50KB)")

    lines = code.splitlines()
    explanation = []
    functions = []
    classes = []
    imports = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        # Python functions
        m = re.match(r'(async\s+)?def\s+(\w+)\s*\((.*?)\)', stripped)
        if m:
            functions.append({"name": m.group(2), "params": m.group(3), "async": bool(m.group(1)), "line": i+1})
        # JS/TS functions
        m = re.match(r'(export\s+)?(async\s+)?function\s+(\w+)\s*\((.*?)\)', stripped)
        if m:
            functions.append({"name": m.group(3), "params": m.group(4), "async": bool(m.group(2)), "line": i+1})
        # Arrow functions
        m = re.match(r'(export\s+)?(const|let|var)\s+(\w+)\s*=\s*(async\s+)?\(', stripped)
        if m:
            functions.append({"name": m.group(3), "params": "...", "async": bool(m.group(4)), "line": i+1})
        # Classes
        m = re.match(r'class\s+(\w+)', stripped)
        if m:
            classes.append({"name": m.group(1), "line": i+1})
        # Imports
        if stripped.startswith(('import ', 'from ', 'require(', 'use ')):
            imports.append({"statement": stripped, "line": i+1})

    # Generate summary
    parts = []
    if imports:
        parts.append(f"Imports {len(imports)} dependencies")
    if classes:
        parts.append(f"Defines {len(classes)} class(es): {', '.join(c['name'] for c in classes)}")
    if functions:
        parts.append(f"Contains {len(functions)} function(s): {', '.join(f['name'] for f in functions)}")
    parts.append(f"Total: {len(lines)} lines of code")

    return {
        "summary": ". ".join(parts) + ".",
        "functions": functions,
        "classes": classes,
        "imports": imports,
        "line_count": len(lines),
        "has_async": any(f.get("async") for f in functions),
    }


@app.post("/api/openapi/generate")
async def generate_openapi_spec(request: Request):
    """Generate an OpenAPI 3.0 spec from endpoint definitions."""
    body = await request.json()
    title = body.get("title", "My API")
    version = body.get("version", "1.0.0")
    description = body.get("description", "")
    base_url = body.get("base_url", "https://api.example.com")
    endpoints = body.get("endpoints", [])

    if not endpoints:
        raise HTTPException(status_code=400, detail="endpoints array required. Each: {path, method, summary, params?, body?, response?}")

    paths = {}
    for ep in endpoints:
        path = ep.get("path", "/")
        method = ep.get("method", "get").lower()
        summary = ep.get("summary", "")
        params = ep.get("params", [])
        req_body = ep.get("body", None)
        response = ep.get("response", {"type": "object"})

        operation = {"summary": summary, "responses": {"200": {"description": "Success", "content": {"application/json": {"schema": response}}}}}
        if params:
            operation["parameters"] = [{"name": p.get("name"), "in": p.get("in", "query"), "required": p.get("required", False), "schema": {"type": p.get("type", "string")}} for p in params]
        if req_body:
            operation["requestBody"] = {"required": True, "content": {"application/json": {"schema": req_body}}}

        if path not in paths:
            paths[path] = {}
        paths[path][method] = operation

    spec = {
        "openapi": "3.0.3",
        "info": {"title": title, "version": version, "description": description},
        "servers": [{"url": base_url}],
        "paths": paths,
    }
    import yaml
    try:
        yaml_output = yaml.dump(spec, default_flow_style=False, sort_keys=False)
    except Exception:
        yaml_output = None

    return {"spec": spec, "yaml": yaml_output, "endpoint_count": len(endpoints)}


@app.post("/api/data/fake")
async def generate_fake_data(request: Request):
    """Generate realistic fake/mock data for testing. Schemas, users, products, addresses, etc."""
    body = await request.json()
    schema_type = body.get("type", "user")
    count = min(body.get("count", 10), 100)
    locale = body.get("locale", "en")

    import random
    import string

    first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Christopher", "Karen", "Daniel", "Lisa", "Matthew", "Nancy", "Anthony", "Betty", "Mark", "Margaret", "Donald", "Sandra"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson"]
    domains = ["gmail.com", "yahoo.com", "outlook.com", "proton.me", "hey.com", "fastmail.com", "icloud.com"]
    streets = ["Main St", "Oak Ave", "Maple Dr", "Cedar Ln", "Elm St", "Pine Rd", "Washington Blvd", "Park Ave", "Lake Dr", "Hill St"]
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "Austin"]
    states = ["NY", "CA", "IL", "TX", "AZ", "PA", "TX", "CA", "TX", "TX"]
    companies = ["TechCorp", "DataFlow", "CloudNine", "PixelPerfect", "ByteForge", "CodeCraft", "NeuralNet", "QuantumLeap", "SkyBridge", "AeroSoft"]
    products_list = ["Widget Pro", "Gadget Max", "Tool Kit", "Smart Sensor", "Power Bank", "LED Strip", "USB Hub", "Wireless Charger", "Cable Organizer", "Desk Lamp"]
    categories = ["Electronics", "Software", "Hardware", "Services", "Accessories"]

    data = []
    for i in range(count):
        first = random.choice(first_names)
        last = random.choice(last_names)
        uid = uuid.uuid4().hex[:8]

        if schema_type == "user":
            data.append({
                "id": uid,
                "first_name": first,
                "last_name": last,
                "email": f"{first.lower()}.{last.lower()}@{random.choice(domains)}",
                "age": random.randint(18, 80),
                "phone": f"+1{random.randint(200,999)}{random.randint(1000000,9999999)}",
                "created_at": f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}T{random.randint(0,23):02d}:{random.randint(0,59):02d}:00Z",
                "is_active": random.choice([True, True, True, False]),
            })
        elif schema_type == "product":
            price = round(random.uniform(4.99, 299.99), 2)
            data.append({
                "id": uid,
                "name": f"{random.choice(products_list)} {random.choice(['v2', 'Plus', 'Elite', 'Mini', 'XL'])}",
                "price": price,
                "currency": "USD",
                "category": random.choice(categories),
                "in_stock": random.choice([True, True, False]),
                "rating": round(random.uniform(3.0, 5.0), 1),
                "reviews": random.randint(0, 500),
                "sku": f"SKU-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}",
            })
        elif schema_type == "address":
            idx = random.randint(0, len(cities)-1)
            data.append({
                "id": uid,
                "street": f"{random.randint(1, 9999)} {random.choice(streets)}",
                "city": cities[idx],
                "state": states[idx],
                "zip": f"{random.randint(10000, 99999)}",
                "country": "US",
            })
        elif schema_type == "company":
            data.append({
                "id": uid,
                "name": f"{random.choice(companies)} {random.choice(['Inc', 'LLC', 'Corp', 'Ltd', 'GmbH'])}",
                "industry": random.choice(["Technology", "Finance", "Healthcare", "Education", "Retail", "Manufacturing"]),
                "employees": random.randint(10, 50000),
                "revenue": f"${random.randint(1, 500)}M",
                "founded": random.randint(1990, 2024),
                "website": f"https://www.{random.choice(companies).lower()}.com",
            })
        elif schema_type == "transaction":
            data.append({
                "id": uid,
                "amount": round(random.uniform(1.0, 5000.0), 2),
                "currency": random.choice(["USD", "EUR", "GBP", "JPY"]),
                "status": random.choice(["completed", "pending", "failed", "refunded"]),
                "type": random.choice(["purchase", "refund", "transfer", "subscription"]),
                "merchant": random.choice(companies),
                "card_last4": f"{random.randint(1000, 9999)}",
                "timestamp": f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}T{random.randint(0,23):02d}:{random.randint(0,59):02d}:00Z",
            })
        elif schema_type == "event":
            data.append({
                "id": uid,
                "event": random.choice(["page_view", "click", "signup", "purchase", "logout", "error", "api_call"]),
                "user_id": uuid.uuid4().hex[:8],
                "properties": {"source": random.choice(["web", "mobile", "api"]), "version": f"{random.randint(1,5)}.{random.randint(0,9)}.{random.randint(0,9)}"},
                "timestamp": f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}T{random.randint(0,23):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}Z",
            })
        else:
            # Custom: just generate generic objects
            data.append({
                "id": uid,
                "name": f"{first} {last}",
                "value": round(random.uniform(1, 1000), 2),
                "category": random.choice(["A", "B", "C", "D"]),
                "timestamp": f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}T{random.randint(0,23):02d}:{random.randint(0,59):02d}:00Z",
            })

    return {"data": data, "count": len(data), "type": schema_type, "available_types": ["user", "product", "address", "company", "transaction", "event"]}


@app.post("/api/code/minify")
async def minify_code(request: Request):
    """Minify JavaScript, CSS, or HTML code."""
    body = await request.json()
    code = body.get("code", "")
    language = body.get("language", "auto")
    if not code:
        raise HTTPException(status_code=400, detail="code field required")

    original_size = len(code)

    if language == "auto":
        if "<html" in code.lower() or "<!doctype" in code.lower():
            language = "html"
        elif "{" in code and (":" in code) and (";" in code) and ("function" not in code and "var " not in code and "const " not in code):
            language = "css"
        else:
            language = "javascript"

    if language == "javascript" or language == "js":
        # Basic JS minification
        minified = re.sub(r'//[^\n]*', '', code)  # Remove single-line comments
        minified = re.sub(r'/\*[\s\S]*?\*/', '', minified)  # Remove multi-line comments
        minified = re.sub(r'\s*\n\s*', '\n', minified)  # Remove leading/trailing whitespace per line
        minified = re.sub(r'\n+', '\n', minified)  # Collapse multiple newlines
        minified = re.sub(r'\s*([{};,=+\-*/()<>!&|?:])\s*', r'\1', minified)  # Remove spaces around operators
        minified = minified.strip()
    elif language == "css":
        minified = re.sub(r'/\*[\s\S]*?\*/', '', code)
        minified = re.sub(r'\s+', ' ', minified)
        minified = re.sub(r'\s*([{};:,>~+])\s*', r'\1', minified)
        minified = re.sub(r';\s*}', '}', minified)
        minified = minified.strip()
    elif language == "html":
        minified = re.sub(r'<!--[\s\S]*?-->', '', code)
        minified = re.sub(r'>\s+<', '><', minified)
        minified = re.sub(r'\s+', ' ', minified)
        minified = minified.strip()
    else:
        minified = re.sub(r'\s+', ' ', code).strip()

    new_size = len(minified)
    savings = round((1 - new_size / original_size) * 100, 1) if original_size > 0 else 0

    return {
        "minified": minified,
        "original_size": original_size,
        "minified_size": new_size,
        "savings_percent": savings,
        "language": language,
    }


@app.post("/api/code/format")
async def format_code(request: Request):
    """Auto-format/beautify code (JS, CSS, HTML, JSON, SQL)."""
    body = await request.json()
    code = body.get("code", "")
    language = body.get("language", "auto")
    indent = body.get("indent", 2)
    if not code:
        raise HTTPException(status_code=400, detail="code field required")

    if language == "auto" or language == "json":
        try:
            parsed = json.loads(code)
            return {"formatted": json.dumps(parsed, indent=indent, ensure_ascii=False), "language": "json"}
        except Exception:
            if language == "json":
                raise HTTPException(status_code=400, detail="Invalid JSON")

    if language == "auto":
        if "SELECT" in code.upper() or "INSERT" in code.upper() or "CREATE TABLE" in code.upper():
            language = "sql"
        elif "<html" in code.lower():
            language = "html"
        elif "{" in code and ":" in code and ";" in code:
            language = "css"
        else:
            language = "text"

    if language == "sql":
        keywords = ["SELECT", "FROM", "WHERE", "AND", "OR", "JOIN", "LEFT JOIN", "RIGHT JOIN", "INNER JOIN",
                     "ON", "GROUP BY", "ORDER BY", "HAVING", "LIMIT", "INSERT INTO", "VALUES", "UPDATE", "SET",
                     "DELETE FROM", "CREATE TABLE", "ALTER TABLE", "DROP TABLE", "CREATE INDEX", "UNION"]
        formatted = code
        for kw in sorted(keywords, key=len, reverse=True):
            formatted = re.sub(rf'\b{kw}\b', kw, formatted, flags=re.IGNORECASE)
            formatted = re.sub(rf'\b({kw})\b', r'\n\1', formatted, flags=re.IGNORECASE)
        formatted = re.sub(r'\n\s*\n', '\n', formatted).strip()
        return {"formatted": formatted, "language": "sql"}

    if language == "html":
        try:
            soup = BeautifulSoup(code, "html.parser")
            formatted = soup.prettify()
            return {"formatted": formatted, "language": "html"}
        except Exception:
            pass

    return {"formatted": code, "language": language, "note": "Formatting applied where possible"}


@app.post("/api/text/translate-code")
async def translate_code_between_languages(request: Request):
    """Generate equivalent code patterns between languages (Python <-> JS <-> Go <-> Rust)."""
    body = await request.json()
    pattern = body.get("pattern", "")
    from_lang = body.get("from", "python")
    to_lang = body.get("to", "javascript")

    if not pattern:
        raise HTTPException(status_code=400, detail="pattern field required")

    # Common patterns lookup table
    patterns = {
        "http_get": {
            "python": 'import httpx\nresponse = httpx.get("https://api.example.com/data")\ndata = response.json()',
            "javascript": 'const response = await fetch("https://api.example.com/data");\nconst data = await response.json();',
            "typescript": 'const response: Response = await fetch("https://api.example.com/data");\nconst data: any = await response.json();',
            "go": 'resp, err := http.Get("https://api.example.com/data")\nif err != nil {\n    log.Fatal(err)\n}\ndefer resp.Body.Close()\nbody, _ := io.ReadAll(resp.Body)',
            "rust": 'let response = reqwest::get("https://api.example.com/data").await?;\nlet data: serde_json::Value = response.json().await?;',
        },
        "read_file": {
            "python": 'with open("file.txt", "r") as f:\n    content = f.read()',
            "javascript": 'import { readFileSync } from "fs";\nconst content = readFileSync("file.txt", "utf-8");',
            "typescript": 'import { readFileSync } from "fs";\nconst content: string = readFileSync("file.txt", "utf-8");',
            "go": 'content, err := os.ReadFile("file.txt")\nif err != nil {\n    log.Fatal(err)\n}',
            "rust": 'let content = std::fs::read_to_string("file.txt")?;',
        },
        "json_parse": {
            "python": 'import json\ndata = json.loads(json_string)',
            "javascript": 'const data = JSON.parse(jsonString);',
            "typescript": 'const data: Record<string, unknown> = JSON.parse(jsonString);',
            "go": 'var data map[string]interface{}\nerr := json.Unmarshal([]byte(jsonString), &data)',
            "rust": 'let data: serde_json::Value = serde_json::from_str(&json_string)?;',
        },
        "hash_sha256": {
            "python": 'import hashlib\ndigest = hashlib.sha256(data.encode()).hexdigest()',
            "javascript": 'const { createHash } = require("crypto");\nconst digest = createHash("sha256").update(data).digest("hex");',
            "typescript": 'import { createHash } from "crypto";\nconst digest: string = createHash("sha256").update(data).digest("hex");',
            "go": 'h := sha256.Sum256([]byte(data))\ndigest := hex.EncodeToString(h[:])',
            "rust": 'use sha2::{Sha256, Digest};\nlet digest = format!("{:x}", Sha256::digest(data.as_bytes()));',
        },
        "env_var": {
            "python": 'import os\nvalue = os.environ.get("KEY", "default")',
            "javascript": 'const value = process.env.KEY || "default";',
            "typescript": 'const value: string = process.env.KEY ?? "default";',
            "go": 'value := os.Getenv("KEY")\nif value == "" {\n    value = "default"\n}',
            "rust": 'let value = std::env::var("KEY").unwrap_or_else(|_| "default".to_string());',
        },
    }

    available_patterns = list(patterns.keys())
    p = pattern.lower().replace(" ", "_").replace("-", "_")

    if p in patterns:
        result = patterns[p]
        return {
            "pattern": p,
            "from": from_lang,
            "to": to_lang,
            "from_code": result.get(from_lang, "Pattern not available for this language"),
            "to_code": result.get(to_lang, "Pattern not available for this language"),
            "all_languages": {lang: code for lang, code in result.items()},
        }

    return {
        "error": f"Pattern '{pattern}' not found",
        "available_patterns": available_patterns,
        "hint": "Try: http_get, read_file, json_parse, hash_sha256, env_var",
    }


@app.post("/api/schema/validate")
async def validate_json_schema(request: Request):
    """Validate JSON data against a JSON Schema."""
    body = await request.json()
    data = body.get("data")
    schema = body.get("schema")

    if data is None or schema is None:
        raise HTTPException(status_code=400, detail="Both 'data' and 'schema' fields required")

    errors = []

    def validate(obj, sch, path="$"):
        obj_type = sch.get("type")
        if obj_type:
            type_map = {"string": str, "number": (int, float), "integer": int, "boolean": bool, "array": list, "object": dict, "null": type(None)}
            expected = type_map.get(obj_type)
            if expected and not isinstance(obj, expected):
                errors.append({"path": path, "message": f"Expected {obj_type}, got {type(obj).__name__}", "value": str(obj)[:100]})
                return

        if obj_type == "object" and isinstance(obj, dict):
            required = sch.get("required", [])
            for r in required:
                if r not in obj:
                    errors.append({"path": f"{path}.{r}", "message": f"Required field '{r}' is missing"})
            props = sch.get("properties", {})
            for key, prop_schema in props.items():
                if key in obj:
                    validate(obj[key], prop_schema, f"{path}.{key}")

        if obj_type == "array" and isinstance(obj, list):
            items_schema = sch.get("items")
            min_items = sch.get("minItems", 0)
            max_items = sch.get("maxItems", float("inf"))
            if len(obj) < min_items:
                errors.append({"path": path, "message": f"Array has {len(obj)} items, minimum is {min_items}"})
            if len(obj) > max_items:
                errors.append({"path": path, "message": f"Array has {len(obj)} items, maximum is {max_items}"})
            if items_schema:
                for i, item in enumerate(obj[:20]):
                    validate(item, items_schema, f"{path}[{i}]")

        if obj_type == "string" and isinstance(obj, str):
            min_len = sch.get("minLength", 0)
            max_len = sch.get("maxLength", float("inf"))
            if len(obj) < min_len:
                errors.append({"path": path, "message": f"String length {len(obj)} < minLength {min_len}"})
            if len(obj) > max_len:
                errors.append({"path": path, "message": f"String length {len(obj)} > maxLength {max_len}"})
            pattern = sch.get("pattern")
            if pattern and not re.search(pattern, obj):
                errors.append({"path": path, "message": f"String does not match pattern: {pattern}"})
            enum = sch.get("enum")
            if enum and obj not in enum:
                errors.append({"path": path, "message": f"Value must be one of: {enum}"})

        if obj_type in ("number", "integer") and isinstance(obj, (int, float)):
            minimum = sch.get("minimum")
            maximum = sch.get("maximum")
            if minimum is not None and obj < minimum:
                errors.append({"path": path, "message": f"Value {obj} < minimum {minimum}"})
            if maximum is not None and obj > maximum:
                errors.append({"path": path, "message": f"Value {obj} > maximum {maximum}"})

    try:
        validate(data, schema)
    except Exception as e:
        errors.append({"path": "$", "message": f"Validation error: {str(e)}"})

    return {"valid": len(errors) == 0, "errors": errors, "error_count": len(errors)}


@app.post("/api/data/csv-analyze")
async def analyze_csv_data(request: Request):
    """Analyze CSV data: column types, stats, missing values, unique counts."""
    body = await request.json()
    csv_text = body.get("csv", "")
    if not csv_text:
        raise HTTPException(status_code=400, detail="csv field required (CSV text)")

    import csv as csv_mod
    import io as io_mod

    reader = csv_mod.DictReader(io_mod.StringIO(csv_text))
    rows = list(reader)
    if not rows:
        return {"error": "No data rows found"}

    columns = {}
    for col in rows[0].keys():
        values = [r.get(col, "") for r in rows]
        non_empty = [v for v in values if v.strip()]
        missing = len(values) - len(non_empty)
        unique = len(set(non_empty))

        # Detect type
        numeric_count = 0
        numeric_values = []
        for v in non_empty:
            try:
                numeric_values.append(float(v))
                numeric_count += 1
            except ValueError:
                pass

        if numeric_count == len(non_empty) and non_empty:
            col_type = "numeric"
            stats = {
                "min": min(numeric_values),
                "max": max(numeric_values),
                "mean": round(sum(numeric_values) / len(numeric_values), 2),
                "sum": round(sum(numeric_values), 2),
            }
        else:
            col_type = "text"
            lengths = [len(v) for v in non_empty]
            stats = {
                "min_length": min(lengths) if lengths else 0,
                "max_length": max(lengths) if lengths else 0,
                "avg_length": round(sum(lengths) / len(lengths), 1) if lengths else 0,
            }

        columns[col] = {
            "type": col_type,
            "total": len(values),
            "missing": missing,
            "unique": unique,
            "sample": non_empty[:3],
            "stats": stats,
        }

    return {
        "row_count": len(rows),
        "column_count": len(columns),
        "columns": columns,
    }


@app.post("/api/security/headers-check")
async def check_security_headers(request: Request):
    """Analyze HTTP security headers of a URL."""
    body = await request.json()
    url = body.get("url", "")
    if not url:
        raise HTTPException(status_code=400, detail="url field required")
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            resp = await client.get(url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not fetch URL: {str(e)}")

    headers = dict(resp.headers)
    checks = {
        "Strict-Transport-Security": {"present": "strict-transport-security" in {k.lower() for k in headers}, "recommendation": "Add HSTS header: Strict-Transport-Security: max-age=31536000; includeSubDomains", "severity": "high"},
        "Content-Security-Policy": {"present": "content-security-policy" in {k.lower() for k in headers}, "recommendation": "Add CSP header to prevent XSS attacks", "severity": "high"},
        "X-Content-Type-Options": {"present": "x-content-type-options" in {k.lower() for k in headers}, "recommendation": "Add: X-Content-Type-Options: nosniff", "severity": "medium"},
        "X-Frame-Options": {"present": "x-frame-options" in {k.lower() for k in headers}, "recommendation": "Add: X-Frame-Options: DENY or SAMEORIGIN", "severity": "medium"},
        "X-XSS-Protection": {"present": "x-xss-protection" in {k.lower() for k in headers}, "recommendation": "Add: X-XSS-Protection: 1; mode=block", "severity": "low"},
        "Referrer-Policy": {"present": "referrer-policy" in {k.lower() for k in headers}, "recommendation": "Add: Referrer-Policy: strict-origin-when-cross-origin", "severity": "low"},
        "Permissions-Policy": {"present": "permissions-policy" in {k.lower() for k in headers}, "recommendation": "Add Permissions-Policy header", "severity": "low"},
    }

    passed = sum(1 for c in checks.values() if c["present"])
    total = len(checks)
    score = round(passed / total * 100)

    return {
        "url": url,
        "status_code": resp.status_code,
        "score": score,
        "grade": "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 50 else "D" if score >= 30 else "F",
        "checks": checks,
        "passed": passed,
        "total": total,
        "server": headers.get("server", "unknown"),
    }


@app.post("/api/generate/api-client")
async def generate_api_client(request: Request):
    """Generate API client code from endpoint definitions (Python, JS, cURL)."""
    body = await request.json()
    base_url = body.get("base_url", "https://api.example.com")
    endpoints = body.get("endpoints", [])
    language = body.get("language", "python")

    if not endpoints:
        raise HTTPException(status_code=400, detail="endpoints array required")

    if language == "python":
        lines = ['import httpx\n', f'BASE_URL = "{base_url}"\n', 'client = httpx.Client(base_url=BASE_URL)\n']
        for ep in endpoints:
            method = ep.get("method", "GET").upper()
            path = ep.get("path", "/")
            name = ep.get("name", path.replace("/", "_").strip("_"))
            params = ep.get("params", [])
            body_fields = ep.get("body", {})

            param_str = ", ".join([p.get("name", "param") + ': str = ""' for p in params])
            lines.append(f'\ndef {name}({param_str}):')
            if method == "GET":
                if params:
                    param_dict = ", ".join([f'"{p.get("name")}": {p.get("name")}' for p in params])
                    lines.append(f'    return client.get("{path}", params={{{param_dict}}}).json()')
                else:
                    lines.append(f'    return client.get("{path}").json()')
            else:
                lines.append(f'    return client.{method.lower()}("{path}", json={body_fields or {}}).json()')
        code = "\n".join(lines)

    elif language in ("javascript", "js", "typescript", "ts"):
        lines = [f'const BASE_URL = "{base_url}";\n']
        for ep in endpoints:
            method = ep.get("method", "GET").upper()
            path = ep.get("path", "/")
            name = ep.get("name", re.sub(r'[^a-zA-Z0-9]', '_', path).strip("_"))
            params = ep.get("params", [])

            param_str = ", ".join([p.get("name", "param") for p in params])
            lines.append(f'\nasync function {name}({param_str}) {{')
            if method == "GET":
                if params:
                    qs = " + ".join([f'"&{p.get("name")}=" + encodeURIComponent({p.get("name")})' for p in params])
                    lines.append(f'  const res = await fetch(`${{BASE_URL}}{path}?` + {qs});')
                else:
                    lines.append(f'  const res = await fetch(`${{BASE_URL}}{path}`);')
            else:
                lines.append(f'  const res = await fetch(`${{BASE_URL}}{path}`, {{')
                lines.append(f'    method: "{method}",')
                lines.append(f'    headers: {{"Content-Type": "application/json"}},')
                lines.append(f'    body: JSON.stringify({{}}),')
                lines.append(f'  }});')
            lines.append(f'  return res.json();')
            lines.append(f'}}')
        code = "\n".join(lines)

    elif language == "curl":
        lines = []
        for ep in endpoints:
            method = ep.get("method", "GET").upper()
            path = ep.get("path", "/")
            if method == "GET":
                lines.append(f'curl -s "{base_url}{path}"')
            else:
                lines.append(f'curl -s -X {method} "{base_url}{path}" \\')
                lines.append(f'  -H "Content-Type: application/json" \\')
                lines.append(f'  -d \'{{}}\'')
            lines.append("")
        code = "\n".join(lines)
    else:
        code = "Supported languages: python, javascript, typescript, curl"

    return {"code": code, "language": language, "endpoint_count": len(endpoints)}


@app.post("/api/generate/env-template")
async def generate_env_template(request: Request):
    """Generate a .env.example template from a list of environment variables or parse existing .env."""
    body = await request.json()
    env_content = body.get("env", "")
    variables = body.get("variables", [])

    if env_content:
        # Parse existing .env and create template
        lines = []
        for line in env_content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                lines.append(line)
                continue
            if "=" in line:
                key = line.split("=", 1)[0].strip()
                # Mask the value
                if any(s in key.lower() for s in ["secret", "key", "password", "token", "auth"]):
                    lines.append(f"{key}=your_{key.lower()}_here")
                elif any(s in key.lower() for s in ["url", "host", "endpoint"]):
                    lines.append(f"{key}=https://example.com")
                elif any(s in key.lower() for s in ["port"]):
                    lines.append(f"{key}=3000")
                elif any(s in key.lower() for s in ["debug", "verbose", "enable"]):
                    lines.append(f"{key}=false")
                else:
                    lines.append(f"{key}=")
        return {"template": "\n".join(lines), "variable_count": sum(1 for l in lines if "=" in l and not l.startswith("#"))}

    if variables:
        lines = ["# Environment Configuration", "# Generated by ToolPipe", ""]
        for var in variables:
            name = var if isinstance(var, str) else var.get("name", "")
            desc = "" if isinstance(var, str) else var.get("description", "")
            if desc:
                lines.append(f"# {desc}")
            lines.append(f"{name}=")
        return {"template": "\n".join(lines), "variable_count": len(variables)}

    return {"error": "Provide 'env' (existing .env content) or 'variables' (list of var names/objects)"}


# --- New Premium Endpoints v1.15.0 ---

@app.post("/api/prompt/engineer")
async def prompt_engineer(request: Request):
    """Transform a basic prompt into an optimized, structured prompt for LLMs.
    Applies prompt engineering best practices: role, context, constraints, output format."""
    data = await request.json()
    prompt = data.get("prompt", "").strip()
    model = data.get("model", "general").lower()
    style = data.get("style", "detailed").lower()

    if not prompt:
        raise HTTPException(status_code=400, detail="'prompt' field required")

    # Analyze the prompt
    word_count = len(prompt.split())
    has_role = any(w in prompt.lower() for w in ["you are", "act as", "pretend", "role"])
    has_context = any(w in prompt.lower() for w in ["context", "background", "given that"])
    has_constraints = any(w in prompt.lower() for w in ["must", "should", "don't", "avoid", "limit", "constraint"])
    has_output_format = any(w in prompt.lower() for w in ["format", "json", "markdown", "table", "list", "output"])
    has_examples = any(w in prompt.lower() for w in ["example", "for instance", "such as", "e.g."])

    improvements = []
    if not has_role:
        improvements.append("Add a role/persona (e.g., 'You are an expert software engineer')")
    if not has_context:
        improvements.append("Add context about the task or domain")
    if not has_constraints:
        improvements.append("Add constraints (length, tone, what to avoid)")
    if not has_output_format:
        improvements.append("Specify desired output format (JSON, markdown, list, etc.)")
    if not has_examples:
        improvements.append("Include examples of expected input/output")
    if word_count < 20:
        improvements.append("Expand the prompt with more specific details")

    # Build optimized version
    sections = []
    if not has_role:
        sections.append("## Role\nYou are an expert assistant specialized in this task.\n")
    sections.append(f"## Task\n{prompt}\n")
    if not has_context:
        sections.append("## Context\n[Add relevant background information here]\n")
    if not has_constraints:
        sections.append("## Constraints\n- Be concise and accurate\n- Focus on actionable information\n- Avoid unnecessary filler\n")
    if not has_output_format:
        sections.append("## Output Format\nProvide your response in a clear, structured format.\n")

    optimized = "\n".join(sections)

    score = 0
    if has_role: score += 20
    if has_context: score += 20
    if has_constraints: score += 20
    if has_output_format: score += 20
    if has_examples: score += 10
    if word_count >= 20: score += 10

    return {
        "original_prompt": prompt,
        "optimized_prompt": optimized,
        "quality_score": score,
        "word_count": word_count,
        "analysis": {
            "has_role": has_role,
            "has_context": has_context,
            "has_constraints": has_constraints,
            "has_output_format": has_output_format,
            "has_examples": has_examples,
        },
        "improvements": improvements,
        "tips": [
            "Use specific, concrete language instead of vague terms",
            "Break complex tasks into numbered steps",
            "Provide examples of expected output",
            "Specify edge cases to handle",
            "Define the audience for the output",
        ],
    }


@app.post("/api/changelog/generate")
async def generate_changelog(request: Request):
    """Generate a changelog from git commit messages or a list of changes."""
    data = await request.json()
    commits = data.get("commits", [])
    version = data.get("version", "1.0.0")
    date = data.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    format_type = data.get("format", "keepachangelog")

    if not commits:
        raise HTTPException(status_code=400, detail="'commits' array required (list of commit messages or objects with 'message' and optional 'type')")

    categories = {
        "Added": [],
        "Changed": [],
        "Fixed": [],
        "Removed": [],
        "Security": [],
        "Deprecated": [],
        "Other": [],
    }

    for commit in commits:
        msg = commit if isinstance(commit, str) else commit.get("message", "")
        msg = msg.strip()
        if not msg:
            continue

        explicit_type = commit.get("type", "") if isinstance(commit, dict) else ""
        lower = msg.lower()

        if explicit_type:
            type_map = {"feat": "Added", "fix": "Fixed", "security": "Security", "remove": "Removed", "deprecate": "Deprecated"}
            cat = type_map.get(explicit_type, "Changed")
        elif any(lower.startswith(w) for w in ["add", "feat", "new", "create", "implement"]):
            cat = "Added"
        elif any(lower.startswith(w) for w in ["fix", "bug", "patch", "resolve", "correct"]):
            cat = "Fixed"
        elif any(lower.startswith(w) for w in ["remove", "delete", "drop"]):
            cat = "Removed"
        elif any(lower.startswith(w) for w in ["security", "vuln", "cve"]):
            cat = "Security"
        elif any(lower.startswith(w) for w in ["deprecat"]):
            cat = "Deprecated"
        elif any(lower.startswith(w) for w in ["update", "change", "refactor", "improve", "upgrade", "bump"]):
            cat = "Changed"
        else:
            cat = "Other"

        categories[cat].append(msg)

    if format_type == "keepachangelog":
        lines = [f"## [{version}] - {date}\n"]
        for cat, items in categories.items():
            if items:
                lines.append(f"### {cat}")
                for item in items:
                    clean = item.lstrip("- ")
                    lines.append(f"- {clean}")
                lines.append("")
        changelog = "\n".join(lines)
    else:
        lines = [f"# {version} ({date})\n"]
        for cat, items in categories.items():
            if items:
                lines.append(f"**{cat}:**")
                for item in items:
                    lines.append(f"  - {item}")
                lines.append("")
        changelog = "\n".join(lines)

    total = sum(len(v) for v in categories.values())
    return {
        "changelog": changelog,
        "version": version,
        "date": date,
        "total_entries": total,
        "categories": {k: len(v) for k, v in categories.items() if v},
    }


@app.post("/api/license/generate")
async def generate_license(request: Request):
    """Generate a LICENSE file for your project."""
    data = await request.json()
    license_type = data.get("type", "MIT").upper()
    name = data.get("name", "Your Name")
    year = data.get("year", datetime.now(timezone.utc).year)

    templates = {
        "MIT": f"""MIT License

Copyright (c) {year} {name}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.""",
        "APACHE-2.0": f"""                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

Copyright {year} {name}

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.""",
        "GPL-3.0": f"""Copyright (C) {year} {name}

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.""",
        "BSD-3-CLAUSE": f"""BSD 3-Clause License

Copyright (c) {year}, {name}
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.""",
        "ISC": f"""ISC License

Copyright (c) {year}, {name}

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.""",
        "UNLICENSE": f"""This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <https://unlicense.org>""",
    }

    if license_type not in templates:
        return {
            "error": f"Unknown license type. Available: {', '.join(templates.keys())}",
            "available_licenses": list(templates.keys()),
        }

    return {
        "license": templates[license_type],
        "type": license_type,
        "name": name,
        "year": year,
        "spdx_id": license_type,
    }


@app.post("/api/commit/message")
async def generate_commit_message(request: Request):
    """Generate a conventional commit message from a diff or description."""
    data = await request.json()
    diff = data.get("diff", "")
    description = data.get("description", "")
    style = data.get("style", "conventional")

    if not diff and not description:
        raise HTTPException(status_code=400, detail="Provide 'diff' or 'description'")

    text = diff or description
    lower = text.lower()

    # Detect commit type
    if any(w in lower for w in ["fix", "bug", "error", "crash", "issue", "patch"]):
        commit_type = "fix"
        emoji = "bug"
    elif any(w in lower for w in ["add", "new", "feature", "implement", "create"]):
        commit_type = "feat"
        emoji = "sparkles"
    elif any(w in lower for w in ["refactor", "clean", "restructure", "reorganize"]):
        commit_type = "refactor"
        emoji = "recycle"
    elif any(w in lower for w in ["test", "spec", "coverage"]):
        commit_type = "test"
        emoji = "white_check_mark"
    elif any(w in lower for w in ["doc", "readme", "comment", "changelog"]):
        commit_type = "docs"
        emoji = "memo"
    elif any(w in lower for w in ["style", "format", "lint", "whitespace"]):
        commit_type = "style"
        emoji = "art"
    elif any(w in lower for w in ["perf", "optim", "speed", "fast"]):
        commit_type = "perf"
        emoji = "zap"
    elif any(w in lower for w in ["ci", "pipeline", "workflow", "deploy"]):
        commit_type = "ci"
        emoji = "construction_worker"
    elif any(w in lower for w in ["build", "deps", "dependency", "upgrade", "bump"]):
        commit_type = "build"
        emoji = "package"
    else:
        commit_type = "chore"
        emoji = "wrench"

    # Detect scope from file paths
    scope = ""
    import re as _re
    file_patterns = _re.findall(r'[\w/]+\.\w+', text)
    if file_patterns:
        first_file = file_patterns[0]
        parts = first_file.split("/")
        if len(parts) > 1:
            scope = parts[-2] if parts[-2] not in ("src", "lib", "app") else parts[-1].split(".")[0]
        else:
            scope = first_file.split(".")[0]

    # Generate summary
    words = (description or diff[:200]).split()
    summary = " ".join(words[:12]).rstrip(".")
    if len(summary) > 72:
        summary = summary[:69] + "..."

    scope_part = f"({scope})" if scope else ""

    messages = {
        "conventional": f"{commit_type}{scope_part}: {summary.lower()}",
        "gitmoji": f":{emoji}: {summary}",
        "simple": summary,
    }

    return {
        "message": messages.get(style, messages["conventional"]),
        "type": commit_type,
        "scope": scope or None,
        "summary": summary,
        "all_styles": messages,
        "detected_files": file_patterns[:10] if file_patterns else [],
    }


@app.post("/api/api-spec/compare")
async def compare_api_specs(request: Request):
    """Compare two OpenAPI specs and detect breaking changes."""
    data = await request.json()
    old_spec = data.get("old", {})
    new_spec = data.get("new", {})

    if not old_spec or not new_spec:
        raise HTTPException(status_code=400, detail="Both 'old' and 'new' OpenAPI spec objects required")

    old_paths = old_spec.get("paths", {})
    new_paths = new_spec.get("paths", {})

    breaking = []
    non_breaking = []

    # Check removed paths
    for path in old_paths:
        if path not in new_paths:
            breaking.append({"type": "path_removed", "path": path, "severity": "breaking"})
        else:
            old_methods = set(old_paths[path].keys())
            new_methods = set(new_paths[path].keys())
            for method in old_methods - new_methods:
                breaking.append({"type": "method_removed", "path": path, "method": method, "severity": "breaking"})

    # Check added paths
    for path in new_paths:
        if path not in old_paths:
            non_breaking.append({"type": "path_added", "path": path, "severity": "non-breaking"})
        else:
            old_methods = set(old_paths[path].keys())
            new_methods = set(new_paths[path].keys())
            for method in new_methods - old_methods:
                non_breaking.append({"type": "method_added", "path": path, "method": method, "severity": "non-breaking"})

    old_version = old_spec.get("info", {}).get("version", "unknown")
    new_version = new_spec.get("info", {}).get("version", "unknown")

    return {
        "old_version": old_version,
        "new_version": new_version,
        "breaking_changes": breaking,
        "non_breaking_changes": non_breaking,
        "total_breaking": len(breaking),
        "total_non_breaking": len(non_breaking),
        "is_breaking": len(breaking) > 0,
        "summary": f"{len(breaking)} breaking, {len(non_breaking)} non-breaking changes between {old_version} and {new_version}",
    }


@app.post("/api/regex/generate")
async def generate_regex(request: Request):
    """Generate regex patterns from natural language descriptions."""
    data = await request.json()
    description = data.get("description", "").strip().lower()
    test_string = data.get("test", "")

    if not description:
        raise HTTPException(status_code=400, detail="'description' field required")

    # Common regex patterns mapped from descriptions
    patterns = {
        "email": {"pattern": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "description": "Email address"},
        "url": {"pattern": r"https?://[^\s<>\"']+", "description": "HTTP/HTTPS URL"},
        "phone": {"pattern": r"\+?1?\s*\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}", "description": "US phone number"},
        "ip": {"pattern": r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "description": "IPv4 address"},
        "ipv6": {"pattern": r"(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}", "description": "IPv6 address"},
        "date": {"pattern": r"\d{4}-\d{2}-\d{2}", "description": "ISO date (YYYY-MM-DD)"},
        "time": {"pattern": r"\d{2}:\d{2}(:\d{2})?", "description": "Time (HH:MM or HH:MM:SS)"},
        "hex": {"pattern": r"#?[0-9a-fA-F]{6}", "description": "Hex color code"},
        "uuid": {"pattern": r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", "description": "UUID v4"},
        "zip": {"pattern": r"\b\d{5}(-\d{4})?\b", "description": "US ZIP code"},
        "ssn": {"pattern": r"\b\d{3}-\d{2}-\d{4}\b", "description": "SSN format (XXX-XX-XXXX)"},
        "credit": {"pattern": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", "description": "Credit card number"},
        "domain": {"pattern": r"[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?\.[a-zA-Z]{2,}", "description": "Domain name"},
        "slug": {"pattern": r"[a-z0-9]+(?:-[a-z0-9]+)*", "description": "URL slug"},
        "semver": {"pattern": r"\bv?\d+\.\d+\.\d+(?:-[\w.]+)?(?:\+[\w.]+)?\b", "description": "Semantic version"},
        "jwt": {"pattern": r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", "description": "JWT token"},
        "mac": {"pattern": r"([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}", "description": "MAC address"},
        "password": {"pattern": r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", "description": "Strong password (8+ chars, upper, lower, digit, special)"},
        "number": {"pattern": r"-?\d+(?:,\d{3})*(?:\.\d+)?", "description": "Number with optional commas and decimals"},
        "word": {"pattern": r"\b\w+\b", "description": "Single word"},
        "sentence": {"pattern": r"[A-Z][^.!?]*[.!?]", "description": "Sentence"},
        "hashtag": {"pattern": r"#\w+", "description": "Hashtag"},
        "mention": {"pattern": r"@\w+", "description": "@ mention"},
        "markdown_link": {"pattern": r"\[([^\]]+)\]\(([^)]+)\)", "description": "Markdown link"},
        "html_tag": {"pattern": r"<\/?[a-zA-Z][^>]*>", "description": "HTML tag"},
    }

    # Find matching pattern
    matched = []
    for key, val in patterns.items():
        if key in description or any(w in description for w in key.split("_")):
            matched.append(val)

    if not matched:
        # Try to find partial matches
        for key, val in patterns.items():
            if any(w in description for w in [key[:4]]):
                matched.append(val)

    if not matched:
        matched = [{"pattern": r".*", "description": "Could not determine pattern from description. Try using keywords like: email, url, phone, ip, date, uuid, hex, domain, password, number"}]

    # Test against string if provided
    results = []
    for m in matched:
        entry = {"pattern": m["pattern"], "description": m["description"]}
        if test_string:
            import re as _re
            matches = _re.findall(m["pattern"], test_string)
            entry["matches"] = matches[:20]
            entry["match_count"] = len(matches)
        results.append(entry)

    return {
        "query": description,
        "patterns": results,
        "total_patterns": len(results),
    }


# --- Premium Endpoints: High-Value Tools for AI Agents ---

class WebCompareRequest(BaseModel):
    url1: str
    url2: str
    compare: str = "content"  # content, headers, performance, seo


@app.post("/api/web/compare")
async def web_compare(req: WebCompareRequest):
    """Compare two websites side-by-side: content, headers, performance, SEO. Premium."""
    results = {}
    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        try:
            r1 = await client.get(req.url1, headers={"User-Agent": "ToolPipe/1.19.0"})
            r2 = await client.get(req.url2, headers={"User-Agent": "ToolPipe/1.19.0"})
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to fetch URLs: {e}")

    if req.compare in ("content", "all"):
        soup1 = BeautifulSoup(r1.text, "html.parser")
        soup2 = BeautifulSoup(r2.text, "html.parser")
        text1 = soup1.get_text(separator="\n", strip=True)[:2000]
        text2 = soup2.get_text(separator="\n", strip=True)[:2000]
        results["content"] = {
            "url1_title": soup1.title.string if soup1.title else "",
            "url2_title": soup2.title.string if soup2.title else "",
            "url1_text_length": len(text1),
            "url2_text_length": len(text2),
            "url1_links": len(soup1.find_all("a")),
            "url2_links": len(soup2.find_all("a")),
            "url1_images": len(soup1.find_all("img")),
            "url2_images": len(soup2.find_all("img")),
        }

    if req.compare in ("headers", "all"):
        results["headers"] = {
            "url1": dict(r1.headers),
            "url2": dict(r2.headers),
        }

    if req.compare in ("performance", "all"):
        results["performance"] = {
            "url1_status": r1.status_code,
            "url2_status": r2.status_code,
            "url1_size_bytes": len(r1.content),
            "url2_size_bytes": len(r2.content),
            "url1_response_time_ms": r1.elapsed.total_seconds() * 1000 if hasattr(r1, 'elapsed') else None,
            "url2_response_time_ms": r2.elapsed.total_seconds() * 1000 if hasattr(r2, 'elapsed') else None,
        }

    if req.compare in ("seo", "all"):
        for i, (resp, url) in enumerate([(r1, req.url1), (r2, req.url2)], 1):
            soup = BeautifulSoup(resp.text, "html.parser")
            meta_desc = soup.find("meta", attrs={"name": "description"})
            og_title = soup.find("meta", attrs={"property": "og:title"})
            canonical = soup.find("link", attrs={"rel": "canonical"})
            h1s = [h.get_text(strip=True) for h in soup.find_all("h1")]
            results[f"url{i}_seo"] = {
                "url": url,
                "title": soup.title.string if soup.title else "",
                "meta_description": meta_desc["content"] if meta_desc else "",
                "og_title": og_title["content"] if og_title else "",
                "canonical": canonical["href"] if canonical else "",
                "h1_tags": h1s[:5],
                "has_robots_meta": bool(soup.find("meta", attrs={"name": "robots"})),
            }

    return {"comparison": req.compare, "url1": req.url1, "url2": req.url2, "results": results}


class BulkHashRequest(BaseModel):
    texts: list[str]
    algorithm: str = "sha256"


@app.post("/api/bulk/hash")
async def bulk_hash(req: BulkHashRequest):
    """Hash multiple strings in a single call. Premium."""
    if len(req.texts) > 500:
        raise HTTPException(status_code=400, detail="Maximum 500 items per bulk request")
    algo = req.algorithm.lower()
    if algo not in ("md5", "sha1", "sha256", "sha512"):
        raise HTTPException(status_code=400, detail="Supported: md5, sha1, sha256, sha512")
    results = []
    for text in req.texts:
        h = hashlib.new(algo, text.encode()).hexdigest()
        results.append({"input": text[:50], "hash": h})
    return {"algorithm": algo, "count": len(results), "results": results}


class BulkUrlCheckRequest(BaseModel):
    urls: list[str]


@app.post("/api/bulk/url-check")
async def bulk_url_check(req: BulkUrlCheckRequest):
    """Check multiple URLs for availability, status codes, redirects. Premium."""
    if len(req.urls) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 URLs per bulk request")
    results = []
    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
        for url in req.urls:
            try:
                r = await client.head(url, headers={"User-Agent": "ToolPipe/1.19.0"})
                results.append({
                    "url": url, "status": r.status_code, "ok": r.status_code < 400,
                    "content_type": r.headers.get("content-type", ""),
                    "redirected": str(r.url) != url,
                    "final_url": str(r.url) if str(r.url) != url else None,
                })
            except Exception as e:
                results.append({"url": url, "status": None, "ok": False, "error": str(e)[:100]})
    ok_count = sum(1 for r in results if r.get("ok"))
    return {"total": len(results), "ok": ok_count, "failed": len(results) - ok_count, "results": results}


class StructuredExtractRequest(BaseModel):
    url: str
    extract: list[str] = ["title", "description", "links", "headings", "images", "tables", "emails", "phones"]


@app.post("/api/web/structured-extract")
async def structured_extract(req: StructuredExtractRequest):
    """Extract structured data from a webpage: links, emails, phones, tables, headings, metadata. Premium."""
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            r = await client.get(req.url, headers={"User-Agent": "ToolPipe/1.19.0"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch: {e}")

    soup = BeautifulSoup(r.text, "html.parser")
    result = {"url": req.url, "status": r.status_code}

    if "title" in req.extract:
        result["title"] = soup.title.string.strip() if soup.title and soup.title.string else ""

    if "description" in req.extract:
        md = soup.find("meta", attrs={"name": "description"})
        result["description"] = md["content"] if md and md.get("content") else ""

    if "headings" in req.extract:
        result["headings"] = {}
        for level in range(1, 7):
            tags = soup.find_all(f"h{level}")
            if tags:
                result["headings"][f"h{level}"] = [t.get_text(strip=True) for t in tags[:20]]

    if "links" in req.extract:
        links = []
        for a in soup.find_all("a", href=True)[:100]:
            href = a["href"]
            text = a.get_text(strip=True)
            if href.startswith("http"):
                links.append({"text": text[:80], "href": href})
        result["links"] = links
        result["link_count"] = len(soup.find_all("a", href=True))

    if "images" in req.extract:
        imgs = []
        for img in soup.find_all("img", src=True)[:50]:
            imgs.append({"src": img["src"], "alt": img.get("alt", "")[:80]})
        result["images"] = imgs

    if "tables" in req.extract:
        tables = []
        for table in soup.find_all("table")[:5]:
            rows = []
            for tr in table.find_all("tr")[:30]:
                cells = [td.get_text(strip=True)[:100] for td in tr.find_all(["td", "th"])]
                if cells:
                    rows.append(cells)
            if rows:
                tables.append({"rows": len(rows), "cols": len(rows[0]) if rows else 0, "data": rows})
        result["tables"] = tables

    if "emails" in req.extract:
        text = soup.get_text()
        emails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)))
        result["emails"] = emails[:20]

    if "phones" in req.extract:
        text = soup.get_text()
        phones = list(set(re.findall(r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{7,15}', text)))
        result["phones"] = [p.strip() for p in phones[:20] if len(p.strip()) >= 7]

    return result


class DomainIntelRequest(BaseModel):
    domain: str


@app.post("/api/domain/intel")
async def domain_intel(req: DomainIntelRequest):
    """Domain intelligence: DNS, SSL, WHOIS, headers, tech stack detection. Premium."""
    import socket
    domain = req.domain.strip().lower().replace("https://", "").replace("http://", "").split("/")[0]
    result = {"domain": domain}

    # DNS records
    try:
        ips = socket.gethostbyname_ex(domain)
        result["dns"] = {"hostname": ips[0], "aliases": ips[1], "ips": ips[2]}
    except Exception as e:
        result["dns"] = {"error": str(e)[:100]}

    # HTTP headers and tech detection
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            r = await client.get(f"https://{domain}", headers={"User-Agent": "ToolPipe/1.19.0"})
            headers = dict(r.headers)
            result["http"] = {
                "status": r.status_code,
                "server": headers.get("server", ""),
                "powered_by": headers.get("x-powered-by", ""),
                "content_type": headers.get("content-type", ""),
            }
            # Tech stack detection from headers and HTML
            tech = []
            html_lower = r.text[:5000].lower()
            if "wp-content" in html_lower or "wordpress" in html_lower:
                tech.append("WordPress")
            if "shopify" in html_lower:
                tech.append("Shopify")
            if "next" in headers.get("x-powered-by", "").lower() or "__next" in html_lower:
                tech.append("Next.js")
            if "react" in html_lower or "react-root" in html_lower:
                tech.append("React")
            if "vue" in html_lower or "__vue" in html_lower:
                tech.append("Vue.js")
            if "angular" in html_lower or "ng-version" in html_lower:
                tech.append("Angular")
            if "cloudflare" in headers.get("server", "").lower():
                tech.append("Cloudflare")
            if "vercel" in headers.get("server", "").lower() or "x-vercel" in headers:
                tech.append("Vercel")
            if "nginx" in headers.get("server", "").lower():
                tech.append("Nginx")
            if "apache" in headers.get("server", "").lower():
                tech.append("Apache")
            if headers.get("x-frame-options"):
                tech.append("X-Frame-Options")
            if headers.get("strict-transport-security"):
                tech.append("HSTS")
            if headers.get("content-security-policy"):
                tech.append("CSP")
            result["tech_stack"] = tech

            # Security headers score
            security_headers = ["strict-transport-security", "content-security-policy",
                                "x-content-type-options", "x-frame-options", "x-xss-protection",
                                "referrer-policy", "permissions-policy"]
            present = sum(1 for h in security_headers if h in headers)
            result["security_score"] = {
                "score": f"{present}/{len(security_headers)}",
                "grade": "A" if present >= 6 else "B" if present >= 4 else "C" if present >= 2 else "F",
                "present": [h for h in security_headers if h in headers],
                "missing": [h for h in security_headers if h not in headers],
            }
    except Exception as e:
        result["http"] = {"error": str(e)[:100]}

    return result


class BulkDnsRequest(BaseModel):
    domains: list[str]


@app.post("/api/bulk/dns")
async def bulk_dns_lookup(req: BulkDnsRequest):
    """Bulk DNS lookup for multiple domains. Premium."""
    import socket
    if len(req.domains) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 domains per bulk request")
    results = []
    for domain in req.domains:
        d = domain.strip().lower().replace("https://", "").replace("http://", "").split("/")[0]
        try:
            ips = socket.gethostbyname_ex(d)
            results.append({"domain": d, "ips": ips[2], "ok": True})
        except Exception as e:
            results.append({"domain": d, "error": str(e)[:80], "ok": False})
    return {"total": len(results), "resolved": sum(1 for r in results if r["ok"]), "results": results}


class ContentDiffRequest(BaseModel):
    url: str
    previous_hash: str = ""


@app.post("/api/web/monitor")
async def web_monitor(req: ContentDiffRequest):
    """Monitor a URL for changes. Returns content hash for change detection. Premium."""
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            r = await client.get(req.url, headers={"User-Agent": "ToolPipe/1.19.0"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch: {e}")

    soup = BeautifulSoup(r.text, "html.parser")
    # Remove scripts and styles for stable hashing
    for tag in soup.find_all(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    current_hash = hashlib.sha256(text.encode()).hexdigest()

    result = {
        "url": req.url,
        "status": r.status_code,
        "content_hash": current_hash,
        "content_length": len(text),
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }

    if req.previous_hash:
        result["changed"] = current_hash != req.previous_hash
        result["previous_hash"] = req.previous_hash
    else:
        result["changed"] = None
        result["note"] = "First check. Save content_hash and pass it as previous_hash next time to detect changes."

    return result


class ApiTestSuiteRequest(BaseModel):
    base_url: str
    endpoints: list[dict]  # [{"method": "GET", "path": "/health"}, ...]


@app.post("/api/test/suite")
async def api_test_suite(req: ApiTestSuiteRequest):
    """Run a test suite against an API. Tests multiple endpoints and reports results. Premium."""
    if len(req.endpoints) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 endpoints per test suite")
    base = req.base_url.rstrip("/")
    results = []
    passed = 0
    failed = 0

    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
        for ep in req.endpoints:
            method = ep.get("method", "GET").upper()
            path = ep.get("path", "/")
            expected_status = ep.get("expected_status", 200)
            body = ep.get("body")
            headers = ep.get("headers", {})
            url = f"{base}{path}"
            try:
                if method == "GET":
                    r = await client.get(url, headers=headers)
                elif method == "POST":
                    r = await client.post(url, json=body, headers=headers)
                elif method == "PUT":
                    r = await client.put(url, json=body, headers=headers)
                elif method == "DELETE":
                    r = await client.delete(url, headers=headers)
                else:
                    results.append({"path": path, "error": f"Unsupported method: {method}"})
                    failed += 1
                    continue

                ok = r.status_code == expected_status
                if ok:
                    passed += 1
                else:
                    failed += 1
                result_entry = {
                    "method": method, "path": path, "status": r.status_code,
                    "expected": expected_status, "passed": ok,
                    "response_time_ms": round(r.elapsed.total_seconds() * 1000, 1) if hasattr(r, 'elapsed') else None,
                    "content_type": r.headers.get("content-type", ""),
                }
                if not ok:
                    result_entry["response_preview"] = r.text[:200]
                results.append(result_entry)
            except Exception as e:
                failed += 1
                results.append({"method": method, "path": path, "error": str(e)[:100], "passed": False})

    return {
        "base_url": base, "total": len(results), "passed": passed, "failed": failed,
        "success_rate": f"{(passed / len(results) * 100):.1f}%" if results else "0%",
        "results": results,
    }


class SitemapParseRequest(BaseModel):
    url: str


@app.post("/api/web/sitemap")
async def parse_sitemap(req: SitemapParseRequest):
    """Parse a website's sitemap.xml and return all URLs. Premium."""
    sitemap_url = req.url.rstrip("/")
    if not sitemap_url.endswith(".xml"):
        sitemap_url = f"{sitemap_url}/sitemap.xml"
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            r = await client.get(sitemap_url, headers={"User-Agent": "ToolPipe/1.19.0"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch sitemap: {e}")

    if r.status_code != 200:
        raise HTTPException(status_code=404, detail=f"Sitemap not found at {sitemap_url} (status {r.status_code})")

    urls = re.findall(r'<loc>(.*?)</loc>', r.text)
    lastmods = re.findall(r'<lastmod>(.*?)</lastmod>', r.text)

    entries = []
    for i, url in enumerate(urls[:500]):
        entry = {"url": url}
        if i < len(lastmods):
            entry["lastmod"] = lastmods[i]
        entries.append(entry)

    # Check if it's a sitemap index (contains other sitemaps)
    is_index = "<sitemapindex" in r.text.lower()

    return {
        "sitemap_url": sitemap_url,
        "is_index": is_index,
        "total_urls": len(urls),
        "urls": entries,
    }


class RobotsCheckRequest(BaseModel):
    url: str
    user_agent: str = "*"
    path: str = "/"


@app.post("/api/web/robots")
async def check_robots(req: RobotsCheckRequest):
    """Parse robots.txt and check if a path is allowed for a user-agent. Premium."""
    base = req.url.rstrip("/")
    parsed = urlparse(base)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            r = await client.get(robots_url, headers={"User-Agent": "ToolPipe/1.19.0"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch robots.txt: {e}")

    if r.status_code != 200:
        return {"robots_url": robots_url, "exists": False, "allowed": True, "note": "No robots.txt found, all paths allowed."}

    lines = r.text.strip().split("\n")
    rules = {"allow": [], "disallow": [], "sitemaps": []}
    current_agent = None

    for line in lines:
        line = line.strip()
        if line.lower().startswith("user-agent:"):
            current_agent = line.split(":", 1)[1].strip()
        elif line.lower().startswith("disallow:") and (current_agent == req.user_agent or current_agent == "*"):
            path = line.split(":", 1)[1].strip()
            if path:
                rules["disallow"].append(path)
        elif line.lower().startswith("allow:") and (current_agent == req.user_agent or current_agent == "*"):
            path = line.split(":", 1)[1].strip()
            if path:
                rules["allow"].append(path)
        elif line.lower().startswith("sitemap:"):
            rules["sitemaps"].append(line.split(":", 1)[1].strip())

    # Check if the requested path is allowed
    allowed = True
    for disallow in rules["disallow"]:
        if req.path.startswith(disallow):
            allowed = False
            break
    for allow in rules["allow"]:
        if req.path.startswith(allow):
            allowed = True
            break

    return {
        "robots_url": robots_url,
        "exists": True,
        "user_agent": req.user_agent,
        "path": req.path,
        "allowed": allowed,
        "rules": rules,
        "raw_length": len(r.text),
    }


# --- A2A (Agent-to-Agent) Protocol Discovery ---

@app.get("/.well-known/agent.json")
async def a2a_agent_card():
    """A2A Agent Card: allows other AI agents to discover ToolPipe capabilities."""
    return {
        "name": "ToolPipe",
        "description": "225+ developer utility APIs accessible to AI agents. JSON formatting, QR codes, hashing, PDF tools, code review, fake data generation, DNS lookup, JWT handling, SSL checks, and more.",
        "url": "https://toolpipe.dev",
        "version": "1.15.0",
        "protocol_version": "0.1",
        "capabilities": {
            "streaming": False,
            "pushNotifications": False,
        },
        "authentication": {
            "schemes": ["apiKey"],
            "credentials": "Get free API key at POST /api-keys/register with {email}. Free: 100 calls/day. Pro: 10,000 calls/day ($9.99/mo crypto).",
        },
        "skills": [
            {"id": "json_tools", "name": "JSON Tools", "description": "Format, validate, minify, diff JSON. Convert JSON to CSV, XML, TypeScript interfaces, SQL schemas."},
            {"id": "code_tools", "name": "Code Tools", "description": "Code review, explain, minify, format (Python/JS/SQL/CSS/HTML). Generate GitHub Actions, Dockerfiles, nginx configs."},
            {"id": "text_tools", "name": "Text Tools", "description": "Summarize, extract keywords, readability analysis, diff, transform (case, reverse, ROT13), lorem ipsum."},
            {"id": "crypto_tools", "name": "Crypto & Hash", "description": "SHA256/MD5/bcrypt hashing, JWT create/decode, password strength, UUID generation."},
            {"id": "web_tools", "name": "Web Tools", "description": "DNS lookup, WHOIS, SSL check, HTTP headers, meta tag extraction, sitemap generation, SEO analysis."},
            {"id": "data_tools", "name": "Data Generation", "description": "Fake data (users, companies, addresses), mock API responses, CSV analysis, .env templates."},
            {"id": "pdf_tools", "name": "PDF Tools", "description": "Merge, split, compress, watermark, protect PDF files."},
            {"id": "qr_tools", "name": "QR & Image", "description": "QR code generation, placeholder images, favicon extraction, CSS gradients."},
            {"id": "security_tools", "name": "Security", "description": "CSP generation, CORS headers, security headers audit, robots.txt generation."},
            {"id": "payment", "name": "Payment", "description": "Accept crypto payments. Create invoices, verify on-chain transactions across 7 EVM chains + Solana."},
        ],
        "endpoints": {
            "openapi": "/openapi-toolpipe.json",
            "api_catalog": "/apis.json",
            "mcp_config": "/.well-known/mcp.json",
            "pricing": "/api/pricing",
            "register": "/api-keys/register",
            "pay": "/payments/agent-pay",
        },
        "provider": {
            "organization": "COSAI Labs",
            "email": "toolpipe-ads@sharebot.net",
        },
    }


@app.get("/api/agent/discover")
async def agent_discover():
    """Discovery endpoint for AI agents. Returns available tools, pricing, and how to get started."""
    return {
        "service": "ToolPipe",
        "tagline": "230+ developer APIs for AI agents and developers",
        "version": "1.18.0",
        "total_endpoints": 230,
        "mcp_tools": 156,
        "free_tier": {
            "daily_limit": 100,
            "signup": "POST /api-keys/register with {\"email\": \"your@email.com\"}",
            "no_credit_card": True,
        },
        "pro_tier": {
            "price": "$9.99/month",
            "daily_limit": 10000,
            "payment": "Crypto only (no KYC). POST /payments/agent-pay",
        },
        "pay_per_call": {
            "packs": CREDIT_PACKS,
            "buy": "POST /api/credits/buy with {api_key, pack}",
            "verify": "POST /api/credits/verify with {order_id, tx_hash}",
            "balance": "GET /api/credits/balance?api_key=...",
        },
        "popular_tools": [
            {"endpoint": "POST /json/format", "description": "Format/validate/minify JSON"},
            {"endpoint": "GET /qr/generate?text=hello", "description": "Generate QR codes"},
            {"endpoint": "POST /hash/generate", "description": "SHA256/MD5/bcrypt hashing"},
            {"endpoint": "GET /uuid/generate", "description": "Generate UUIDs"},
            {"endpoint": "POST /api/code/review", "description": "AI-powered code review"},
            {"endpoint": "POST /api/data/fake", "description": "Generate fake data"},
            {"endpoint": "GET /api/dns?domain=example.com", "description": "DNS lookup"},
            {"endpoint": "POST /api/jwt/create", "description": "Create JWT tokens"},
            {"endpoint": "GET /api/ssl/check?domain=example.com", "description": "SSL certificate check"},
            {"endpoint": "POST /api/text/summarize", "description": "Text summarization"},
        ],
        "mcp_server": {
            "npm": "npx @cosai-labs/toolpipe-mcp-server",
            "github": "https://github.com/COSAI-Labs/make-money-30day-challenge/tree/master/products/mcp-server",
            "config": "/.well-known/mcp.json",
        },
        "documentation": "/docs",
        "openapi": "/openapi-toolpipe.json",
    }


# --- New Premium Endpoints v1.16.0 ---

@app.get("/api/ip/info")
async def ip_info(ip: str = ""):
    """Get geolocation and ISP info for an IP address. Uses public APIs."""
    if not ip:
        return {"error": "Provide ?ip=1.2.3.4"}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query")
            data = resp.json()
        if data.get("status") == "success":
            return {
                "ip": data.get("query"),
                "country": data.get("country"),
                "country_code": data.get("countryCode"),
                "region": data.get("regionName"),
                "city": data.get("city"),
                "zip": data.get("zip"),
                "lat": data.get("lat"),
                "lon": data.get("lon"),
                "timezone": data.get("timezone"),
                "isp": data.get("isp"),
                "org": data.get("org"),
                "as": data.get("as"),
            }
        return {"error": data.get("message", "Lookup failed"), "ip": ip}
    except Exception as e:
        return {"error": str(e), "ip": ip}


@app.get("/api/ip/my")
async def my_ip(request: Request):
    """Get the caller's IP address and info."""
    client_ip = request.headers.get("cf-connecting-ip") or request.headers.get("x-forwarded-for", "").split(",")[0].strip() or request.client.host
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"http://ip-api.com/json/{client_ip}?fields=status,country,countryCode,regionName,city,timezone,isp,org,query")
            data = resp.json()
        if data.get("status") == "success":
            return {"ip": client_ip, "country": data.get("country"), "city": data.get("city"), "timezone": data.get("timezone"), "isp": data.get("isp")}
    except Exception:
        pass
    return {"ip": client_ip}


@app.post("/api/webhook/test")
async def webhook_test(request: Request, url: str = ""):
    """Send a test webhook to any URL. Useful for debugging webhook handlers."""
    if not url:
        try:
            body = await request.json()
            url = body.get("url", "")
        except Exception:
            pass
    if not url:
        raise HTTPException(status_code=400, detail="Provide url parameter or JSON body with {url}")
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise HTTPException(status_code=400, detail="Invalid URL")

    test_payload = {
        "event": "test",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "toolpipe.dev",
        "data": {
            "message": "This is a test webhook from ToolPipe",
            "id": uuid.uuid4().hex,
        },
    }
    try:
        body_data = {}
        try:
            body_data = await request.json()
        except Exception:
            pass
        if body_data.get("payload"):
            test_payload["data"] = body_data["payload"]

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(url, json=test_payload, headers={"User-Agent": "ToolPipe-Webhook/1.0", "Content-Type": "application/json"})
        return {
            "sent": True,
            "url": url,
            "status_code": resp.status_code,
            "response_body": resp.text[:500],
            "payload_sent": test_payload,
        }
    except Exception as e:
        return {"sent": False, "url": url, "error": str(e)}



@app.post("/api/crontab/validate")
async def validate_crontab(request: Request):
    """Validate and explain a cron expression."""
    body = await request.json()
    expr = body.get("expression", body.get("cron", ""))
    if not expr:
        raise HTTPException(status_code=400, detail="Provide expression (cron expression)")

    parts = expr.strip().split()
    if len(parts) not in (5, 6, 7):
        return {"valid": False, "error": f"Expected 5-7 fields, got {len(parts)}"}

    field_names = ["minute", "hour", "day_of_month", "month", "day_of_week"]
    if len(parts) >= 6:
        field_names.append("year")
    if len(parts) >= 7:
        field_names.append("command")

    fields = {}
    for i, name in enumerate(field_names):
        if i < len(parts):
            fields[name] = parts[i]

    # Basic validation
    ranges = {"minute": (0, 59), "hour": (0, 23), "day_of_month": (1, 31), "month": (1, 12), "day_of_week": (0, 7)}
    errors = []
    for name, (low, high) in ranges.items():
        val = fields.get(name, "*")
        if val == "*" or "/" in val or "," in val or "-" in val:
            continue
        try:
            n = int(val)
            if n < low or n > high:
                errors.append(f"{name}: {n} is out of range [{low}-{high}]")
        except ValueError:
            pass

    # Human-readable description
    desc_parts = []
    m = fields.get("minute", "*")
    h = fields.get("hour", "*")
    dom = fields.get("day_of_month", "*")
    mon = fields.get("month", "*")
    dow = fields.get("day_of_week", "*")

    if m == "*" and h == "*":
        desc_parts.append("Every minute")
    elif m != "*" and h == "*":
        desc_parts.append(f"At minute {m} of every hour")
    elif m == "0" and h != "*":
        desc_parts.append(f"At {h}:00")
    elif m != "*" and h != "*":
        desc_parts.append(f"At {h}:{m.zfill(2)}")
    else:
        desc_parts.append(f"Minute: {m}, Hour: {h}")

    if dom != "*":
        desc_parts.append(f"on day {dom}")
    if mon != "*":
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        try:
            desc_parts.append(f"in {months[int(mon)-1]}")
        except (ValueError, IndexError):
            desc_parts.append(f"in month {mon}")
    if dow != "*":
        days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        try:
            desc_parts.append(f"on {days[int(dow)]}")
        except (ValueError, IndexError):
            desc_parts.append(f"on day of week {dow}")

    return {
        "valid": len(errors) == 0,
        "expression": expr,
        "fields": fields,
        "description": " ".join(desc_parts),
        "errors": errors or None,
    }



@app.get("/.well-known/a2a.json")
async def a2a_discovery():
    """A2A (Agent-to-Agent) protocol discovery."""
    base = _get_tunnel_url()
    return {
        "name": "ToolPipe",
        "description": "Developer utility API service with 240+ endpoints and 166 MCP tools.",
        "version": "1.18.0",
        "protocol": "a2a",
        "capabilities": [
            "json-formatting", "qr-code-generation", "hashing", "uuid-generation",
            "base64-encoding", "dns-lookup", "ssl-check", "code-review",
            "fake-data-generation", "regex-testing", "jwt-operations",
            "dockerfile-generation", "web-scraping", "text-analysis",
        ],
        "endpoints": {
            "rest": f"{base}/docs",
            "mcp": f"{base}/mcp",
            "openapi": f"{base}/openapi.json",
        },
        "authentication": {
            "type": "api_key",
            "header": "X-API-Key",
            "free_tier_available": True,
            "register": f"{base}/api-keys/register",
        },
        "payment": {
            "crypto": True,
            "wallets": {
                "ethereum": "0xBCF464909b748d720fd5DDA25ad3d313Dd4b53D6",
                "solana": "2guKDsPScRpCCKuVEGKBPFvodSNtZF4ArYeSC6oy6pf6",
            },
            "payment_endpoint": f"{base}/payments/create",
        },
    }


@app.get("/.well-known/mcp/server-card.json")
async def mcp_server_card():
    """Smithery.ai MCP server card for auto-discovery."""
    base = _get_tunnel_url()
    return {
        "serverInfo": {
            "name": "ToolPipe",
            "version": "1.18.0",
            "description": "240+ developer utility APIs and 55 MCP tools. JSON formatting, QR codes, hashing, code review, DNS lookup, web scraping, domain intel, bulk operations, web monitoring, and more.",
        },
        "authentication": {
            "required": False,
            "schemes": [],
            "notes": "Free tier: 100 calls/day, no auth needed. For higher limits, register at /api-keys/register",
        },
        "tools": [
            {"name": "json_format", "description": "Format, validate, and minify JSON"},
            {"name": "qr_generate", "description": "Generate QR codes as PNG images"},
            {"name": "hash_generate", "description": "SHA256, MD5, bcrypt hashing"},
            {"name": "uuid_generate", "description": "Generate UUID v4 identifiers"},
            {"name": "base64_encode_decode", "description": "Base64 encoding and decoding"},
            {"name": "dns_lookup", "description": "DNS record lookup for any domain"},
            {"name": "code_review", "description": "AI-powered code review and suggestions"},
            {"name": "code_format", "description": "Format code in 20+ languages"},
            {"name": "fake_data_generate", "description": "Generate realistic fake data"},
            {"name": "regex_test", "description": "Test regex patterns with match highlighting"},
            {"name": "jwt_create", "description": "Create and sign JWT tokens"},
            {"name": "jwt_decode", "description": "Decode and inspect JWT tokens"},
            {"name": "dockerfile_generate", "description": "Generate Dockerfiles from project specs"},
            {"name": "web_extract", "description": "Extract content and metadata from URLs"},
            {"name": "text_summarize", "description": "Summarize long text content"},
            {"name": "css_minify", "description": "Minify CSS stylesheets"},
            {"name": "js_minify", "description": "Minify JavaScript code"},
            {"name": "markdown_to_html", "description": "Convert Markdown to HTML"},
            {"name": "ip_lookup", "description": "GeoIP lookup for IP addresses"},
            {"name": "ssl_check", "description": "Check SSL certificate details"},
            {"name": "whois_lookup", "description": "WHOIS domain information lookup"},
            {"name": "password_generate", "description": "Generate secure random passwords"},
            {"name": "color_convert", "description": "Convert between HEX, RGB, HSL colors"},
            {"name": "cron_parse", "description": "Parse and explain cron expressions"},
            {"name": "timestamp_convert", "description": "Convert between timestamp formats"},
            {"name": "url_shorten", "description": "Create short URLs"},
            {"name": "pdf_create", "description": "Generate PDFs from HTML content"},
            {"name": "screenshot_take", "description": "Take website screenshots"},
            {"name": "commit_message_generate", "description": "Generate git commit messages"},
            {"name": "prompt_engineer", "description": "Improve AI prompts automatically"},
            {"name": "domain_intel", "description": "Domain intelligence: DNS, tech stack, security score (Premium)"},
            {"name": "web_structured_extract", "description": "Extract structured data from webpages (Premium)"},
            {"name": "web_compare", "description": "Compare two websites side-by-side (Premium)"},
            {"name": "bulk_url_check", "description": "Check multiple URLs for availability (Premium)"},
            {"name": "web_monitor", "description": "Monitor URLs for content changes (Premium)"},
            {"name": "api_test_suite", "description": "Run API test suites with pass/fail reporting (Premium)"},
            {"name": "sitemap_parse", "description": "Parse sitemaps and extract all URLs (Premium)"},
            {"name": "robots_check", "description": "Parse robots.txt and check path access (Premium)"},
            {"name": "bulk_dns_lookup", "description": "Bulk DNS lookup for multiple domains (Premium)"},
            {"name": "bulk_hash", "description": "Hash multiple strings in one call (Premium)"},
        ],
        "resources": [],
        "prompts": [],
        "transport": {
            "type": "streamable-http",
            "url": f"{base}/mcp",
        },
        "links": {
            "homepage": base,
            "documentation": f"{base}/docs",
            "pricing": f"{base}/pricing",
            "npm": "https://www.npmjs.com/package/@cosai-labs/toolpipe-mcp-server",
            "github": "https://github.com/COSAI-Labs/make-money-30day-challenge",
        },
    }


# --- Embeddable Widgets (growth: each embed = backlink + traffic) ---

WIDGET_TOOLS = {
    "json": {"title": "JSON Formatter", "endpoint": "/json/format", "placeholder": '{"name":"test","value":42}', "method": "POST", "field": "json"},
    "base64": {"title": "Base64 Encoder", "endpoint": "/base64", "placeholder": "Hello World", "method": "POST", "field": "text"},
    "hash": {"title": "Hash Generator", "endpoint": "/hash/generate", "placeholder": "my text to hash", "method": "POST", "field": "text"},
    "uuid": {"title": "UUID Generator", "endpoint": "/uuid/generate", "method": "GET", "field": None},
    "qr": {"title": "QR Code Generator", "endpoint": "/qr/generate", "placeholder": "https://example.com", "method": "GET", "field": "text"},
    "password": {"title": "Password Generator", "endpoint": "/api/password/generate", "method": "GET", "field": None},
}


@app.get("/embed/{tool}", response_class=HTMLResponse)
async def embed_widget(tool: str, theme: str = "dark"):
    """Embeddable widget for any ToolPipe tool. Add to your site with an iframe."""
    if tool not in WIDGET_TOOLS:
        tools_list = ", ".join(WIDGET_TOOLS.keys())
        raise HTTPException(status_code=404, detail=f"Widget not found. Available: {tools_list}")

    t = WIDGET_TOOLS[tool]
    base = _get_tunnel_url()
    bg = "#1a1a2e" if theme == "dark" else "#ffffff"
    fg = "#e0e0e0" if theme == "dark" else "#333333"
    accent = "#6c63ff"
    input_bg = "#111" if theme == "dark" else "#f5f5f5"
    border = "#2a2a2a" if theme == "dark" else "#ddd"

    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,sans-serif;background:{bg};color:{fg};padding:16px}}
h3{{font-size:1rem;margin-bottom:8px}}
textarea,input{{width:100%;padding:10px;background:{input_bg};color:{fg};border:1px solid {border};border-radius:6px;font-family:monospace;font-size:0.85rem;resize:vertical}}
textarea{{min-height:80px}}
.btn{{padding:8px 16px;background:{accent};color:#fff;border:none;border-radius:6px;cursor:pointer;font-weight:600;margin:8px 0}}
.btn:hover{{opacity:0.9}}
.result{{background:{input_bg};border:1px solid {border};border-radius:6px;padding:10px;margin-top:8px;font-family:monospace;font-size:0.85rem;white-space:pre-wrap;max-height:200px;overflow:auto;display:none}}
.powered{{text-align:right;font-size:0.7rem;margin-top:8px;opacity:0.6}}
.powered a{{color:{accent};text-decoration:none}}
</style></head><body>
<h3>{t['title']}</h3>"""

    if t.get("field") and t.get("placeholder"):
        html += f'<textarea id="input" placeholder="{t["placeholder"]}">{t["placeholder"]}</textarea>'

    html += f"""<button class="btn" onclick="run()">Run</button>
<div class="result" id="result"></div>
<div class="powered">Powered by <a href="{base}" target="_blank">ToolPipe</a></div>
<script>
async function run(){{
  const el=document.getElementById('result');
  el.style.display='block';
  el.textContent='Loading...';
  try{{"""

    if t["method"] == "GET" and not t.get("field"):
        html += f"""
    const r=await fetch('{base}{t["endpoint"]}');
    const d=await r.json();
    el.textContent=JSON.stringify(d,null,2);"""
    elif t["method"] == "GET":
        html += f"""
    const v=document.getElementById('input').value;
    const r=await fetch('{base}{t["endpoint"]}?{t["field"]}='+encodeURIComponent(v));
    if(r.headers.get('content-type')?.includes('image')){{
      el.innerHTML='<img src="'+r.url+'" style="max-width:200px">';
    }}else{{
      const d=await r.json();
      el.textContent=JSON.stringify(d,null,2);
    }}"""
    else:
        html += f"""
    const v=document.getElementById('input').value;
    const r=await fetch('{base}{t["endpoint"]}',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{"{t["field"]}":v}})}});
    const d=await r.json();
    el.textContent=JSON.stringify(d,null,2);"""

    html += """
  }catch(e){el.textContent='Error: '+e.message}
}
</script></body></html>"""

    return HTMLResponse(html)


@app.get("/embed", response_class=HTMLResponse)
async def embed_gallery():
    """Gallery of embeddable widgets with embed codes."""
    base = _get_tunnel_url()
    cards = ""
    for key, t in WIDGET_TOOLS.items():
        cards += f"""<div style="background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;padding:20px;margin-bottom:16px">
<h3 style="color:#fff;margin-bottom:8px">{t['title']}</h3>
<p style="color:#94a3b8;font-size:0.9rem;margin-bottom:12px">Embed this tool on your website:</p>
<code style="background:#111;color:#22c55e;padding:8px 12px;border-radius:6px;font-size:0.8rem;display:block;word-break:break-all">&lt;iframe src="{base}/embed/{key}" width="400" height="300" frameborder="0"&gt;&lt;/iframe&gt;</code>
<div style="margin-top:12px"><iframe src="/embed/{key}?theme=dark" width="100%" height="250" frameborder="0" style="border-radius:8px"></iframe></div>
</div>"""

    html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Embeddable Developer Widgets - ToolPipe</title>
<meta name="description" content="Free embeddable developer tool widgets. JSON formatter, Base64 encoder, hash generator, UUID generator, QR codes. Add to any website with one line of HTML.">
<style>*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:-apple-system,sans-serif;background:#0a0a0a;color:#e0e0e0;padding:40px 20px}}.container{{max-width:800px;margin:0 auto}}h1{{font-size:2rem;color:#fff;margin-bottom:8px}}p.sub{{color:#94a3b8;margin-bottom:32px}}</style>
</head><body><div class="container">
<h1>Embeddable Developer Widgets</h1>
<p class="sub">Add free developer tools to your website. Each widget is a single iframe, no dependencies.</p>
{cards}
</div></body></html>"""
    return HTMLResponse(inject_snippet(html))


@app.get("/demo", response_class=HTMLResponse)
async def demo_page():
    return HTMLResponse(inject_snippet("""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>ToolPipe API Demo - Try 200+ Developer Tools Live</title>
<meta name="description" content="Try ToolPipe's 200+ developer APIs live. JSON formatter, QR codes, hash generator, DNS lookup, web scraper, and more. No signup required.">
<link rel="canonical" href="https://toolpipe.dev/demo">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0a0a0a;color:#e0e0e0;min-height:100vh}
.hero{text-align:center;padding:60px 20px 40px;background:linear-gradient(180deg,#111 0%,#0a0a0a 100%)}
.hero h1{font-size:2.2rem;font-weight:800;margin-bottom:8px}
.hero h1 span{background:linear-gradient(135deg,#6c63ff,#00d4ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.hero p{color:#94a3b8;font-size:1.1rem;max-width:600px;margin:0 auto}
.demos{max-width:900px;margin:0 auto;padding:20px}
.demo-card{background:#111;border:1px solid #1e1e1e;border-radius:12px;margin-bottom:24px;overflow:hidden;transition:border-color 0.2s}
.demo-card:hover{border-color:#333}
.demo-header{padding:20px 24px;display:flex;align-items:center;justify-content:space-between;cursor:pointer}
.demo-header h3{font-size:1.1rem;color:#fff}
.demo-header .method{font-size:0.75rem;padding:3px 8px;border-radius:4px;font-weight:700;font-family:monospace}
.method-get{background:#22c55e22;color:#22c55e}
.method-post{background:#6c63ff22;color:#6c63ff}
.demo-body{padding:0 24px 24px;display:none}
.demo-body.open{display:block}
.demo-input{display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap}
.demo-input input,.demo-input textarea,.demo-input select{flex:1;min-width:200px;padding:10px 14px;background:#1a1a1a;border:1px solid #2a2a2a;border-radius:8px;color:#e0e0e0;font-size:0.9rem;font-family:monospace;outline:none}
.demo-input textarea{min-height:80px;resize:vertical}
.demo-input input:focus,.demo-input textarea:focus{border-color:#6c63ff}
.try-btn{padding:10px 20px;background:#6c63ff;color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:0.9rem;white-space:nowrap}
.try-btn:hover{background:#5b54e6}
.try-btn:disabled{background:#333;cursor:not-allowed}
.demo-result{background:#0d0d0d;border:1px solid #1a1a1a;border-radius:8px;padding:16px;font-family:monospace;font-size:0.85rem;white-space:pre-wrap;word-break:break-all;max-height:400px;overflow-y:auto;display:none;color:#a0a0a0}
.demo-result.visible{display:block}
.demo-result img{max-width:200px;border-radius:8px;margin:8px 0}
.curl-hint{color:#444;font-size:0.75rem;font-family:monospace;margin-top:8px}
.cta{text-align:center;padding:60px 20px;background:linear-gradient(180deg,#0a0a0a 0%,#111 100%)}
.cta h2{font-size:1.5rem;margin-bottom:8px}
.cta p{color:#94a3b8;margin-bottom:24px}
.cta a{display:inline-block;padding:14px 32px;background:#6c63ff;color:#fff;border-radius:10px;text-decoration:none;font-weight:700;margin:0 8px}
.cta a.secondary{background:transparent;border:1px solid #333;color:#94a3b8}
.cta a:hover{opacity:0.9}
.stats{display:flex;gap:32px;justify-content:center;margin:24px 0;flex-wrap:wrap}
.stat{text-align:center}.stat .num{font-size:1.8rem;font-weight:800;color:#6c63ff}.stat .label{color:#64748b;font-size:0.85rem}
</style></head><body>
<div class="hero">
<h1>Try <span>200+ APIs</span> Live</h1>
<p>No signup needed. Click any tool below to test it instantly. When you're ready for more, get a free API key.</p>
<div class="stats">
<div class="stat"><div class="num">238</div><div class="label">Endpoints</div></div>
<div class="stat"><div class="num">0</div><div class="label">Signup Required</div></div>
<div class="stat"><div class="num">100</div><div class="label">Free Calls/Day</div></div>
</div>
</div>
<div class="demos" id="demos">

<div class="demo-card" data-open="true">
<div class="demo-header" onclick="toggle(this)"><h3>JSON Formatter</h3><span class="method method-post">POST</span></div>
<div class="demo-body open">
<div class="demo-input"><textarea id="json-input" placeholder='{"name":"ToolPipe","tools":238,"free":true}'></textarea><button class="try-btn" onclick="tryDemo('json')">Format</button></div>
<div class="demo-result" id="json-result"></div>
<div class="curl-hint">curl -X POST https://toolpipe.dev/api/json/format -H "Content-Type: application/json" -d '{"data":{"example":true}}'</div>
</div></div>

<div class="demo-card">
<div class="demo-header" onclick="toggle(this)"><h3>QR Code Generator</h3><span class="method method-get">GET</span></div>
<div class="demo-body">
<div class="demo-input"><input id="qr-input" value="https://toolpipe.dev" placeholder="URL or text"><button class="try-btn" onclick="tryDemo('qr')">Generate</button></div>
<div class="demo-result" id="qr-result"></div>
<div class="curl-hint">curl "https://toolpipe.dev/qr/generate?text=hello&size=300"</div>
</div></div>

<div class="demo-card">
<div class="demo-header" onclick="toggle(this)"><h3>Hash Generator (SHA-256)</h3><span class="method method-post">POST</span></div>
<div class="demo-body">
<div class="demo-input"><input id="hash-input" value="Hello, World!" placeholder="Text to hash"><button class="try-btn" onclick="tryDemo('hash')">Hash</button></div>
<div class="demo-result" id="hash-result"></div>
<div class="curl-hint">curl -X POST https://toolpipe.dev/api/hash -H "Content-Type: application/json" -d '{"text":"hello","algorithm":"sha256"}'</div>
</div></div>

<div class="demo-card">
<div class="demo-header" onclick="toggle(this)"><h3>UUID Generator</h3><span class="method method-get">GET</span></div>
<div class="demo-body">
<div class="demo-input"><button class="try-btn" onclick="tryDemo('uuid')" style="flex:1">Generate UUID</button></div>
<div class="demo-result" id="uuid-result"></div>
<div class="curl-hint">curl https://toolpipe.dev/api/uuid</div>
</div></div>

<div class="demo-card">
<div class="demo-header" onclick="toggle(this)"><h3>DNS Lookup</h3><span class="method method-get">GET</span></div>
<div class="demo-body">
<div class="demo-input"><input id="dns-input" value="google.com" placeholder="Domain"><button class="try-btn" onclick="tryDemo('dns')">Lookup</button></div>
<div class="demo-result" id="dns-result"></div>
<div class="curl-hint">curl "https://toolpipe.dev/api/dns/lookup?domain=google.com"</div>
</div></div>

<div class="demo-card">
<div class="demo-header" onclick="toggle(this)"><h3>Base64 Encode/Decode</h3><span class="method method-post">POST</span></div>
<div class="demo-body">
<div class="demo-input"><input id="b64-input" value="Hello from ToolPipe!" placeholder="Text to encode"><button class="try-btn" onclick="tryDemo('b64')">Encode</button></div>
<div class="demo-result" id="b64-result"></div>
<div class="curl-hint">curl -X POST https://toolpipe.dev/api/base64/encode -H "Content-Type: application/json" -d '{"text":"hello"}'</div>
</div></div>

<div class="demo-card">
<div class="demo-header" onclick="toggle(this)"><h3>IP Geolocation</h3><span class="method method-get">GET</span></div>
<div class="demo-body">
<div class="demo-input"><button class="try-btn" onclick="tryDemo('ip')" style="flex:1">Get My IP Info</button></div>
<div class="demo-result" id="ip-result"></div>
<div class="curl-hint">curl https://toolpipe.dev/api/ip/my</div>
</div></div>

<div class="demo-card">
<div class="demo-header" onclick="toggle(this)"><h3>Web Scraper</h3><span class="method method-post">POST</span></div>
<div class="demo-body">
<div class="demo-input"><input id="scrape-input" value="https://example.com" placeholder="URL to scrape"><button class="try-btn" onclick="tryDemo('scrape')">Scrape</button></div>
<div class="demo-result" id="scrape-result"></div>
<div class="curl-hint">curl -X POST https://toolpipe.dev/api/scrape -H "Content-Type: application/json" -d '{"url":"https://example.com"}'</div>
</div></div>

<div class="demo-card">
<div class="demo-header" onclick="toggle(this)"><h3>Password Generator</h3><span class="method method-get">GET</span></div>
<div class="demo-body">
<div class="demo-input"><input id="pwd-input" value="16" placeholder="Length" type="number" min="8" max="128"><button class="try-btn" onclick="tryDemo('pwd')">Generate</button></div>
<div class="demo-result" id="pwd-result"></div>
<div class="curl-hint">curl "https://toolpipe.dev/api/password/generate?length=16"</div>
</div></div>

<div class="demo-card">
<div class="demo-header" onclick="toggle(this)"><h3>Markdown to HTML</h3><span class="method method-post">POST</span></div>
<div class="demo-body">
<div class="demo-input"><textarea id="md-input" placeholder="# Hello\n\n**Bold** and *italic*">## ToolPipe API\n\n- 200+ endpoints\n- **Free** tier\n- Pay with crypto</textarea><button class="try-btn" onclick="tryDemo('md')">Convert</button></div>
<div class="demo-result" id="md-result"></div>
<div class="curl-hint">curl -X POST https://toolpipe.dev/api/markdown -H "Content-Type: application/json" -d '{"text":"# Hello"}'</div>
</div></div>

</div>

<div class="cta">
<h2>Ready to integrate?</h2>
<p>Get a free API key for 100 calls/day. Upgrade to Pro for 10,000 calls/day.</p>
<a href="/api-keys">Get Free API Key</a>
<a href="/pricing" class="secondary">View Pricing</a>
</div>

<script>
function toggle(el){el.nextElementSibling.classList.toggle('open')}
document.querySelectorAll('[data-open]').forEach(c=>c.querySelector('.demo-body').classList.add('open'));

async function tryDemo(type){
  const result=document.getElementById(type+'-result');
  result.classList.add('visible');
  result.textContent='Loading...';
  try{
    let r,d;
    switch(type){
      case'json':
        let raw=document.getElementById('json-input').value||'{"example":true}';
        try{raw=JSON.parse(raw)}catch(e){raw={"raw_input":raw}}
        r=await fetch('/api/json/format',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({data:raw})});
        d=await r.json();result.textContent=JSON.stringify(d,null,2);break;
      case'qr':
        const qrText=document.getElementById('qr-input').value||'https://toolpipe.dev';
        result.innerHTML='<img src="/qr/generate?text='+encodeURIComponent(qrText)+'&size=250" alt="QR Code">';break;
      case'hash':
        const hashText=document.getElementById('hash-input').value||'hello';
        r=await fetch('/api/hash',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:hashText,algorithm:'sha256'})});
        d=await r.json();result.textContent=JSON.stringify(d,null,2);break;
      case'uuid':
        r=await fetch('/api/uuid');d=await r.json();result.textContent=JSON.stringify(d,null,2);break;
      case'dns':
        const domain=document.getElementById('dns-input').value||'google.com';
        r=await fetch('/api/dns/lookup?domain='+encodeURIComponent(domain));d=await r.json();result.textContent=JSON.stringify(d,null,2);break;
      case'b64':
        const b64Text=document.getElementById('b64-input').value||'hello';
        r=await fetch('/api/base64/encode',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:b64Text})});
        d=await r.json();result.textContent=JSON.stringify(d,null,2);break;
      case'ip':
        r=await fetch('/api/ip/my');d=await r.json();result.textContent=JSON.stringify(d,null,2);break;
      case'scrape':
        const url=document.getElementById('scrape-input').value||'https://example.com';
        r=await fetch('/api/scrape',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url:url})});
        d=await r.json();result.textContent=JSON.stringify(d,null,2).substring(0,3000);break;
      case'pwd':
        const len=document.getElementById('pwd-input').value||'16';
        r=await fetch('/api/password/generate?length='+len);d=await r.json();result.textContent=JSON.stringify(d,null,2);break;
      case'md':
        const mdText=document.getElementById('md-input').value||'# Hello';
        r=await fetch('/api/markdown',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:mdText})});
        d=await r.json();result.textContent=JSON.stringify(d,null,2);break;
    }
  }catch(e){result.textContent='Error: '+e.message}
}
</script>
</body></html>"""))


@app.get("/api/openapi-lite")
async def openapi_lite():
    """Lightweight OpenAPI summary for marketplace submissions and agent discovery."""
    return {
        "name": "ToolPipe API",
        "version": "1.19.0",
        "description": "238 developer utility APIs. JSON, QR, hash, UUID, DNS, web scraping, code review, fake data, PDF tools, SEO, domain intel, bulk operations, and more.",
        "base_url": "https://toolpipe.dev",
        "docs_url": "https://toolpipe.dev/docs",
        "openapi_url": "https://toolpipe.dev/openapi.json",
        "total_endpoints": 238,
        "free_tier": {"daily_limit": 100, "signup": "POST /api-keys/register with {email}"},
        "paid_tiers": PRICING_TIERS,
        "credits": CREDIT_PACKS,
        "mcp_server": {
            "npm": "npx @cosai-labs/toolpipe-mcp-server",
            "http": "https://toolpipe.dev/mcp",
            "tools": 55,
        },
        "categories": [
            "JSON/XML/YAML formatting", "QR code generation", "Hashing (MD5/SHA/bcrypt)",
            "UUID generation", "DNS/WHOIS/IP lookup", "Web scraping/monitoring",
            "Base64/URL/HTML encoding", "PDF tools (merge/split/text)",
            "Code review/minification", "Fake data generation", "SEO analysis",
            "Domain intelligence", "Bulk operations", "API testing",
            "SQL/regex formatting", "JWT decoding", "Password generation",
            "Markdown conversion", "Cron validation", "Webhook testing",
        ],
        "payment": {
            "method": "crypto (no KYC)",
            "wallets": {
                "evm": WALLET_ADDRESS,
                "solana": SOLANA_WALLET,
            },
            "accepted": ["ETH", "USDC", "USDT", "DAI", "SOL", "BNB"],
            "networks": ["Ethereum", "Polygon", "Base", "Arbitrum", "Optimism", "Solana"],
        },
    }


# --- SEO Pages (catch-all for static content pages, must be LAST) ---

@app.get("/{page_name}", response_class=HTMLResponse)
async def seo_page_handler(page_name: str):
    page_file = SEO_PAGES_DIR / f"{page_name}.html"
    if page_file.exists():
        return HTMLResponse(inject_snippet(page_file.read_text()))
    raise HTTPException(status_code=404, detail="Page not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
