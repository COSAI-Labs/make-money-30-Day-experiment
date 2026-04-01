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
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
from pydantic import BaseModel, HttpUrl
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.pagesizes import letter

app = FastAPI(
    title="ToolPipe API",
    description="Developer utility APIs: QR codes, screenshots, metadata extraction, markdown conversion, image processing, and more.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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


# --- OxaPay Crypto Payment Integration ---
OXAPAY_MERCHANT_KEY = os.environ.get("OXAPAY_MERCHANT_KEY", "sandbox")
OXAPAY_API_URL = "https://api.oxapay.com/v1/payment/invoice"
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


async def create_oxapay_invoice(amount: float, email: str, tier: str, order_id: str, callback_url: str, return_url: str) -> dict:
    payload = {
        "merchant": OXAPAY_MERCHANT_KEY,
        "amount": amount,
        "currency": "USD",
        "lifetime": 60,
        "callback_url": callback_url,
        "return_url": return_url,
        "email": email,
        "order_id": order_id,
        "description": f"ToolPipe {tier.title()} Plan",
        "fee_paid_by_payer": 1,
    }
    if OXAPAY_MERCHANT_KEY == "sandbox":
        payload["sandbox"] = True

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(OXAPAY_API_URL, json=payload)
            data = resp.json()

        if data.get("status") == 200 and data.get("data"):
            track_id = data["data"].get("track_id", "")
            payment_url = data["data"].get("payment_url", "")
            now = datetime.now(timezone.utc).isoformat()
            with _payments_lock:
                conn = sqlite3.connect(str(PAYMENTS_DB))
                conn.execute(
                    "INSERT OR REPLACE INTO payments (track_id, order_id, email, tier, amount, status, payment_url, created_at) VALUES (?, ?, ?, ?, ?, 'pending', ?, ?)",
                    (track_id, order_id, email, tier, amount, payment_url, now)
                )
                conn.commit()
                conn.close()
            return {"success": True, "payment_url": payment_url, "track_id": track_id, "order_id": order_id}
        return {"success": False, "error": data.get("message", "Payment creation failed"), "fallback": "crypto_direct"}
    except Exception:
        # OxaPay API unavailable (Cloudflare, network, etc.), record intent and show direct crypto address
        now = datetime.now(timezone.utc).isoformat()
        with _payments_lock:
            conn = sqlite3.connect(str(PAYMENTS_DB))
            conn.execute(
                "INSERT OR REPLACE INTO payments (track_id, order_id, email, tier, amount, status, created_at) VALUES (?, ?, ?, ?, ?, 'awaiting_direct', ?)",
                (order_id, order_id, email, tier, amount, now)
            )
            conn.commit()
            conn.close()
        return {
            "success": False,
            "fallback": "crypto_direct",
            "message": "Automated payment temporarily unavailable. Send crypto directly.",
            "crypto_address": "0xBCF464909b748d720fd5DDA25ad3d313Dd4b53D6",
            "networks": "Ethereum, Polygon, Arbitrum, Base, Optimism",
            "accepted": "ETH, USDC, USDT, DAI, any ERC-20",
            "amount_usd": amount,
            "order_id": order_id,
            "instructions": f"Send ${amount} worth of crypto to the address above, then email toolpipe-ads@sharebot.net with your tx hash and order ID ({order_id}) to activate your {tier} plan."
        }


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
<br><span style="color:#475569;">50+ free developer tools by ToolPipe. No signup, no tracking. <a href="/donate" style="color:#6c63ff;text-decoration:none;">Support us</a></span>
</div></div>
"""


def inject_snippet(html: str) -> str:
    """Inject analytics and monetization snippet into HTML pages."""
    if "</body>" in html:
        return html.replace("</body>", INJECT_SNIPPET + "</body>")
    return html + INJECT_SNIPPET


def serve_html(path: Path, track_path: str = "") -> HTMLResponse:
    """Serve an HTML file with injected analytics/monetization."""
    if path.exists():
        return HTMLResponse(inject_snippet(path.read_text()))
    return HTMLResponse("<h1>Page not found</h1>", status_code=404)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(client_ip):
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded. Max 100 requests per minute."},
        )

    # Track pageviews for page requests
    path = str(request.url.path)
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
    return serve_html(TOOLS_HTML)


@app.get("/invoice", response_class=HTMLResponse)
async def invoice_page():
    return serve_html(INVOICE_HTML)


@app.get("/api")
async def api_info():
    return {
        "service": "ToolPipe API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": [
            "/qr/generate",
            "/meta/extract",
            "/markdown/to-html",
            "/text/analyze",
            "/hash/generate",
            "/image/resize",
            "/image/convert",
            "/json/to-csv",
            "/uuid/generate",
            "/dns/lookup",
            "/color/convert",
            "/base64",
        ],
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
        "/donate", "/api-keys", "/api-consulting", "/polymarket",
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
<a href="mailto:toolpipe-project@sharebot.net?subject=ToolPipe Pro" style="display:block;background:#6c63ff;color:#fff;text-align:center;padding:10px;border-radius:8px;margin-top:12px;font-weight:600;">Upgrade to Pro</a>
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

    result = await create_oxapay_invoice(
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
    """OxaPay sends payment status updates here."""
    try:
        data = await request.json()
    except Exception:
        body = await request.body()
        try:
            data = json.loads(body)
        except Exception:
            return {"status": "error", "message": "Invalid payload"}

    track_id = data.get("trackId", data.get("track_id", ""))
    status = data.get("status", "")
    order_id = data.get("orderId", data.get("order_id", ""))

    if status in ("Paid", "Confirming", "Complete", "paid", "complete"):
        now = datetime.now(timezone.utc).isoformat()
        with _payments_lock:
            conn = sqlite3.connect(str(PAYMENTS_DB))
            # Find payment record
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
                # Upgrade the API key
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


# --- Pricing Page ---

@app.get("/pricing", response_class=HTMLResponse)
async def pricing_page():
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
<p class="sub">70+ developer APIs. Pay with crypto. No KYC needed.</p>

<div class="tiers">
<div class="tier">
<h2>Free</h2>
<div class="price">$0 <span>/mo</span></div>
<div class="period">No credit card required</div>
<ul>
<li>100 requests/day</li>
<li>All 70+ endpoints</li>
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
<li>All 70+ endpoints</li>
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
<li>All 70+ endpoints</li>
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
<div class="faq-item"><h3>What endpoints are included?</h3><p>All plans include access to all 70+ endpoints: JSON formatting, PDF tools, QR codes, hash generation, UUID, DNS lookup, image processing, text analysis, and more. See <a href="/docs" style="color:#6c63ff">/docs</a> for the full list.</p></div>
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
        } else if (data.fallback === 'crypto_direct') {
            status.innerHTML = '<strong>Send crypto directly:</strong><br>' +
              '<code style="color:#22c55e;word-break:break-all">' + (data.crypto_address || '0xBCF464909b748d720fd5DDA25ad3d313Dd4b53D6') + '</code><br>' +
              '<small>Amount: $' + (data.amount_usd || selectedTier === 'pro' ? '9.99' : '49.99') + ' in ETH/USDC/USDT</small><br>' +
              '<small>Then email <a href="mailto:toolpipe-ads@sharebot.net" style="color:#6c63ff">toolpipe-ads@sharebot.net</a> with tx hash + order: ' + (data.order_id || '') + '</small>';
            status.style.color = '#f59e0b';
            status.style.display = 'block';
            btn.textContent = 'Pay with Crypto';
            btn.disabled = false;
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


# --- SEO Pages (catch-all for static content pages) ---

@app.get("/{page_name}", response_class=HTMLResponse)
async def seo_page_handler(page_name: str):
    # Only serve known SEO pages to avoid catching API routes
    page_file = SEO_PAGES_DIR / f"{page_name}.html"
    if page_file.exists():
        return HTMLResponse(inject_snippet(page_file.read_text()))
    raise HTTPException(status_code=404, detail="Page not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
