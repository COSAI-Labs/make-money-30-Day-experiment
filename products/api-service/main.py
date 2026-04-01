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
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlparse

import httpx
import markdown
import qrcode
from bs4 import BeautifulSoup
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
from pydantic import BaseModel, HttpUrl

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


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(client_ip):
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded. Max 100 requests per minute."},
        )
    response = await call_next(request)
    return response


# --- Health ---

LANDING_HTML = Path(__file__).parent / "landing.html"
TOOLS_HTML = Path(__file__).parent.parent / "web-tools" / "index.html"


@app.get("/", response_class=HTMLResponse)
async def root():
    if LANDING_HTML.exists():
        return HTMLResponse(LANDING_HTML.read_text())
    return HTMLResponse("<h1>ToolPipe API</h1><p><a href='/docs'>API Docs</a></p>")


@app.get("/tools", response_class=HTMLResponse)
async def tools_page():
    if TOOLS_HTML.exists():
        return HTMLResponse(TOOLS_HTML.read_text())
    return HTMLResponse("<h1>Tools coming soon</h1>")


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


# --- SEO Analyzer ---

SEO_HTML = Path(__file__).parent.parent / "seo-analyzer" / "index.html"


@app.get("/seo", response_class=HTMLResponse)
async def seo_page():
    if SEO_HTML.exists():
        return HTMLResponse(SEO_HTML.read_text())
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
