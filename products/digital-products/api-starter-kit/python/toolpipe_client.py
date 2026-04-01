"""
ToolPipe API Python Client
Complete SDK for all ToolPipe API endpoints.
"""

import httpx
import time
from typing import Optional
from pathlib import Path


class ToolPipeClient:
    """Production-ready client for ToolPipe API."""

    def __init__(self, base_url: str = "https://toolpipe.dev", api_key: Optional[str] = None, timeout: float = 30.0, max_retries: int = 3):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self._client = httpx.Client(timeout=timeout)

    def _headers(self) -> dict:
        h = {"User-Agent": "ToolPipe-Python/1.0"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        url = f"{self.base_url}{path}"
        for attempt in range(self.max_retries):
            try:
                resp = self._client.request(method, url, headers=self._headers(), **kwargs)
                if resp.status_code == 429:
                    wait = min(2 ** attempt, 30)
                    time.sleep(wait)
                    continue
                resp.raise_for_status()
                return resp
            except httpx.HTTPStatusError:
                raise
            except httpx.HTTPError:
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
        raise Exception("Max retries exceeded")

    # --- QR Code ---

    def generate_qr(self, data: str, size: int = 300) -> bytes:
        """Generate a QR code image. Returns PNG bytes."""
        resp = self._request("POST", "/qr/generate", json={"data": data, "size": size})
        return resp.content

    def generate_qr_url(self, data: str, size: int = 300) -> str:
        """Get URL for QR code generation."""
        from urllib.parse import quote
        return f"{self.base_url}/qr/generate?data={quote(data)}&size={size}"

    # --- Metadata Extraction ---

    def extract_metadata(self, url: str) -> dict:
        """Extract metadata (title, description, OG tags) from a URL."""
        resp = self._request("GET", "/meta/extract", params={"url": url})
        return resp.json()

    # --- Text Analysis ---

    def analyze_text(self, text: str) -> dict:
        """Analyze text: word count, reading time, sentiment, etc."""
        resp = self._request("POST", "/text/analyze", json={"text": text})
        return resp.json()

    # --- Markdown ---

    def markdown_to_html(self, markdown: str) -> dict:
        """Convert Markdown to HTML."""
        resp = self._request("POST", "/markdown/to-html", json={"markdown": markdown})
        return resp.json()

    # --- Hash ---

    def generate_hash(self, text: str, algorithm: str = "sha256") -> dict:
        """Generate hash of text."""
        resp = self._request("POST", "/hash/generate", json={"text": text, "algorithm": algorithm})
        return resp.json()

    # --- Image Processing ---

    def resize_image(self, image_path: str, width: int, height: int) -> bytes:
        """Resize an image. Returns processed image bytes."""
        with open(image_path, "rb") as f:
            resp = self._request("POST", "/image/resize", files={"file": f}, data={"width": width, "height": height})
        return resp.content

    def convert_image(self, image_path: str, target_format: str = "png") -> bytes:
        """Convert image format. Returns processed image bytes."""
        with open(image_path, "rb") as f:
            resp = self._request("POST", "/image/convert", files={"file": f}, data={"format": target_format})
        return resp.content

    # --- JSON/CSV ---

    def json_to_csv(self, data: list[dict]) -> str:
        """Convert JSON array to CSV."""
        resp = self._request("POST", "/json/to-csv", json={"data": data})
        return resp.text

    # --- UUID ---

    def generate_uuid(self, count: int = 1) -> dict:
        """Generate one or more UUIDs."""
        resp = self._request("GET", "/uuid/generate", params={"count": count})
        return resp.json()

    # --- DNS ---

    def dns_lookup(self, domain: str) -> dict:
        """Look up DNS records for a domain."""
        resp = self._request("GET", "/dns/lookup", params={"domain": domain})
        return resp.json()

    # --- SEO ---

    def analyze_seo(self, url: str) -> dict:
        """Analyze SEO of a URL."""
        resp = self._request("GET", "/seo/analyze", params={"url": url})
        return resp.json()

    # --- URL Shortener ---

    def shorten_url(self, url: str, custom_code: Optional[str] = None) -> dict:
        """Create a short URL."""
        payload = {"url": url}
        if custom_code:
            payload["code"] = custom_code
        resp = self._request("POST", "/s/create", json=payload)
        return resp.json()

    # --- Is It Down ---

    def check_down(self, url: str) -> dict:
        """Check if a website is down."""
        resp = self._request("GET", "/down/check", params={"url": url})
        return resp.json()

    # --- IP Lookup ---

    def ip_lookup(self, ip: str) -> dict:
        """Look up geolocation for an IP address."""
        resp = self._request("GET", "/ip/lookup", params={"ip": ip})
        return resp.json()

    def my_ip(self) -> dict:
        """Get your public IP address."""
        resp = self._request("GET", "/ip/my")
        return resp.json()

    # --- PDF Tools ---

    def merge_pdfs(self, pdf_paths: list[str]) -> bytes:
        """Merge multiple PDFs into one. Returns PDF bytes."""
        files = [("files", (Path(p).name, open(p, "rb"), "application/pdf")) for p in pdf_paths]
        resp = self._request("POST", "/pdf/merge", files=files)
        return resp.content

    def pdf_to_text(self, pdf_path: str) -> dict:
        """Extract text from a PDF."""
        with open(pdf_path, "rb") as f:
            resp = self._request("POST", "/pdf/extract-text", files={"file": f})
        return resp.json()

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


# --- Usage Examples ---

if __name__ == "__main__":
    with ToolPipeClient() as client:
        # Generate QR code
        qr_bytes = client.generate_qr("https://toolpipe.dev")
        with open("qr_code.png", "wb") as f:
            f.write(qr_bytes)
        print("QR code saved to qr_code.png")

        # Analyze text
        result = client.analyze_text("Hello world, this is a test of the ToolPipe API.")
        print(f"Text analysis: {result}")

        # DNS lookup
        dns = client.dns_lookup("google.com")
        print(f"DNS records: {dns}")

        # Generate UUIDs
        uuids = client.generate_uuid(5)
        print(f"Generated UUIDs: {uuids}")
