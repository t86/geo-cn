"""Shared helpers for China engine live probes (stdlib-first)."""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any
from urllib.parse import urlparse


DEFAULT_EXCERPT_CHARS = 800


def env_key(*names: str) -> str | None:
    """Return the first non-empty environment variable among ``names``."""
    for name in names:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return None


def brand_mentioned(text: str | None, brand: str | None) -> bool | None:
    """Casefold / Chinese-substring brand presence. None if brand missing."""
    if not brand:
        return None
    if text is None:
        return None
    hay = text.casefold()
    needle = brand.casefold()
    if needle and needle in hay:
        return True
    # Chinese brands are often exact substrings without casefold benefit
    if brand in text:
        return True
    return False


def host_of(url: str | None) -> str | None:
    if not url:
        return None
    try:
        parsed = urlparse(url if "://" in url else f"https://{url}")
        host = (parsed.hostname or "").lower().removeprefix("www.")
        return host or None
    except Exception:
        return None


def brand_cited(
    text: str | None,
    brand: str | None,
    url: str | None,
    citation_urls: list[str] | None = None,
) -> bool | None:
    """True only when a clear brand URL/domain or ``url`` arg appears.

    Does not treat bare brand-name mention as a citation.
    """
    if not brand and not url:
        return None
    targets: list[str] = []
    brand_host = host_of(url) if url else None
    if brand_host:
        targets.append(brand_host)
    if url:
        targets.append(url.rstrip("/").lower())

    blobs: list[str] = []
    if text:
        blobs.append(text)
    for cu in citation_urls or []:
        blobs.append(cu)

    if not blobs:
        return False if targets else None

    joined = "\n".join(blobs).lower()
    for t in targets:
        if t and t.lower() in joined:
            return True

    # Explicit http(s) links in answer that contain brand token in host
    if brand:
        brand_token = brand.casefold().replace(" ", "")
        for match in re.finditer(r"https?://[^\s\)\]\"\'<>]+", text or "", flags=re.I):
            link = match.group(0)
            h = host_of(link) or ""
            if brand_token and brand_token in h.replace("-", "").replace(".", ""):
                return True
            if brand.casefold() in h:
                return True
    return False


def truncate_excerpt(text: str | None, limit: int = DEFAULT_EXCERPT_CHARS) -> str | None:
    if text is None:
        return None
    cleaned = text.strip()
    if not cleaned:
        return None
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1] + "…"


def http_json(
    method: str,
    url: str,
    *,
    headers: dict[str, str],
    body: dict[str, Any] | None = None,
    timeout_s: float = 60.0,
) -> tuple[int, dict[str, Any] | list[Any] | str]:
    """POST/GET JSON via urllib. Returns (status_code, parsed_or_raw_text)."""
    data = None
    req_headers = dict(headers)
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        req_headers.setdefault("Content-Type", "application/json")
    request = urllib.request.Request(url, data=data, headers=req_headers, method=method.upper())
    try:
        with urllib.request.urlopen(request, timeout=timeout_s) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            code = getattr(resp, "status", None) or resp.getcode()
            try:
                return int(code), json.loads(raw)
            except json.JSONDecodeError:
                return int(code), raw
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload: dict[str, Any] | list[Any] | str = json.loads(raw)
        except json.JSONDecodeError:
            payload = raw
        return int(exc.code), payload
    except urllib.error.URLError as exc:
        raise ConnectionError(f"HTTP {method} {url} failed: {exc}") from exc


def openai_message_content(payload: dict[str, Any]) -> str:
    """Extract assistant text from OpenAI-compatible chat.completions JSON."""
    choices = payload.get("choices") or []
    if not choices:
        return ""
    message = choices[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text") or ""))
            elif isinstance(block, str):
                parts.append(block)
        return "".join(parts)
    return str(content or "")


def is_brand_domain(url: str | None, brand_url: str | None, brand: str | None) -> bool | None:
    if not url:
        return None
    h = host_of(url)
    if not h:
        return None
    brand_h = host_of(brand_url)
    if brand_h and (h == brand_h or h.endswith("." + brand_h)):
        return True
    if brand:
        token = brand.casefold().replace(" ", "")
        compact = h.replace("-", "").replace(".", "")
        if token and token in compact:
            return True
    return False
