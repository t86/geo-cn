"""Live DeepSeek visibility probe.

Primary path: OpenAI-compatible chat completions at api.deepseek.com.
Optional web_search path: Anthropic-compatible messages + web_search_20250305
when context.extra["web_search"] or DEEPSEEK_WEB_SEARCH=1.
"""

from __future__ import annotations

import os
from typing import Any
from urllib.parse import urlparse

from ..base import EngineProbe, ProbeContext
from ..models import CitationHit, EngineId, ProbeStatus, VisibilityResult
from .common import (
    brand_cited,
    brand_mentioned,
    env_key,
    http_json,
    openai_message_content,
    truncate_excerpt,
)

CHAT_URL = "https://api.deepseek.com/chat/completions"
ANTHROPIC_URL = "https://api.deepseek.com/anthropic/v1/messages"
DEFAULT_MODEL = "deepseek-flash"
FALLBACK_MODELS = ("deepseek-chat", "deepseek-v4-flash")
SYSTEM_PROMPT = (
    "你是简短的中文助手，用于 GEO 可见度探测。"
    "只根据已知或检索到的信息回答，不要编造事实、链接或引用。"
)


class DeepSeekProbe(EngineProbe):
    engine_id = EngineId.DEEPSEEK

    def probe(
        self,
        query: str,
        *,
        brand: str | None = None,
        url: str | None = None,
        context: ProbeContext | None = None,
    ) -> VisibilityResult:
        ctx = context or ProbeContext()
        api_key = env_key("DEEPSEEK_API_KEY")
        if not api_key:
            return VisibilityResult(
                engine=self.engine_id,
                query=query,
                status=ProbeStatus.STUB,
                brand=brand,
                notes=[
                    "No DEEPSEEK_API_KEY set; returning stub (no live call).",
                    "Export DEEPSEEK_API_KEY to enable measured DeepSeek probes.",
                ],
                raw={"adapter": "deepseek", "reason": "missing_api_key"},
            )

        if ctx.dry_run:
            return VisibilityResult(
                engine=self.engine_id,
                query=query,
                status=ProbeStatus.STUB,
                brand=brand,
                notes=[
                    "dry_run=True: skipped live DeepSeek call. Pass --live / dry_run=False.",
                ],
                raw={"adapter": "deepseek", "reason": "dry_run"},
            )

        want_search = bool(
            (ctx.extra or {}).get("web_search")
            or os.environ.get("DEEPSEEK_WEB_SEARCH", "").strip() in {"1", "true", "TRUE", "yes"}
        )
        notes: list[str] = []
        try:
            if want_search:
                result = self._probe_with_web_search(
                    query, brand=brand, url=url, api_key=api_key, timeout_s=ctx.timeout_s, notes=notes
                )
                if result is not None:
                    return result
                notes.append(
                    "Anthropic web_search path failed or unavailable; fell back to plain chat."
                )
            return self._probe_chat(
                query, brand=brand, url=url, api_key=api_key, timeout_s=ctx.timeout_s, notes=notes
            )
        except Exception as exc:  # noqa: BLE001 — surface as ERROR, never crash CLI
            return VisibilityResult(
                engine=self.engine_id,
                query=query,
                status=ProbeStatus.ERROR,
                brand=brand,
                error=str(exc),
                notes=notes + [f"DeepSeek probe exception: {exc}"],
                raw={"adapter": "deepseek"},
            )

    def _probe_chat(
        self,
        query: str,
        *,
        brand: str | None,
        url: str | None,
        api_key: str,
        timeout_s: float,
        notes: list[str],
    ) -> VisibilityResult:
        model = DEFAULT_MODEL
        status_code, payload = self._post_chat(api_key, model, query, timeout_s)
        if status_code == 400 and isinstance(payload, dict):
            notes.append(
                f"model={DEFAULT_MODEL} returned HTTP 400; trying fallback models {FALLBACK_MODELS}."
            )
            for alt in FALLBACK_MODELS:
                status_code, payload = self._post_chat(api_key, alt, query, timeout_s)
                if status_code < 400:
                    model = alt
                    break

        if status_code >= 400:
            err = _error_message(payload) or f"HTTP {status_code}"
            return VisibilityResult(
                engine=self.engine_id,
                query=query,
                status=ProbeStatus.ERROR,
                brand=brand,
                error=err,
                notes=notes + [f"DeepSeek chat failed: {err}"],
                raw={"adapter": "deepseek", "http_status": status_code, "model": model},
            )

        if not isinstance(payload, dict):
            return VisibilityResult(
                engine=self.engine_id,
                query=query,
                status=ProbeStatus.ERROR,
                brand=brand,
                error="Unexpected non-JSON DeepSeek response",
                notes=notes,
                raw={"adapter": "deepseek", "body": str(payload)[:500]},
            )

        answer = openai_message_content(payload)
        excerpt = truncate_excerpt(answer)
        cited = brand_cited(answer, brand, url, citation_urls=[])
        notes.append(f"path=chat model={model}; citations=[] (chat API does not expose sources).")
        return VisibilityResult(
            engine=self.engine_id,
            query=query,
            status=ProbeStatus.MEASURED,
            brand=brand,
            answer_excerpt=excerpt,
            brand_mentioned=brand_mentioned(answer, brand),
            brand_cited=cited,
            citations=[],
            notes=notes,
            raw={"adapter": "deepseek", "path": "chat", "model": model, "usage": payload.get("usage")},
        )

    def _post_chat(
        self, api_key: str, model: str, query: str, timeout_s: float
    ) -> tuple[int, dict[str, Any] | list[Any] | str]:
        body = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": query},
            ],
            "stream": False,
            "thinking": {"type": "disabled"},
        }
        return http_json(
            "POST",
            CHAT_URL,
            headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
            body=body,
            timeout_s=timeout_s,
        )

    def _probe_with_web_search(
        self,
        query: str,
        *,
        brand: str | None,
        url: str | None,
        api_key: str,
        timeout_s: float,
        notes: list[str],
    ) -> VisibilityResult | None:
        body = {
            "model": DEFAULT_MODEL,
            "max_tokens": 2048,
            "messages": [{"role": "user", "content": query}],
            "tools": [
                {
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": 3,
                }
            ],
            "thinking": {"type": "disabled"},
        }
        try:
            status_code, payload = http_json(
                "POST",
                ANTHROPIC_URL,
                headers={
                    "x-api-key": api_key,
                    "Authorization": f"Bearer {api_key}",
                    "anthropic-version": "2023-06-01",
                    "Accept": "application/json",
                },
                body=body,
                timeout_s=timeout_s,
            )
        except ConnectionError as exc:
            notes.append(f"web_search connection error: {exc}")
            return None

        if status_code >= 400 or not isinstance(payload, dict):
            notes.append(f"web_search HTTP {status_code}: {_error_message(payload)}")
            return None

        text_parts: list[str] = []
        citations: list[CitationHit] = []
        citation_urls: list[str] = []
        content = payload.get("content") or []
        if isinstance(content, list):
            for block in content:
                if not isinstance(block, dict):
                    continue
                btype = block.get("type")
                if btype == "text":
                    text_parts.append(str(block.get("text") or ""))
                    for cit in block.get("citations") or []:
                        if isinstance(cit, dict):
                            cu = cit.get("url")
                            if cu:
                                citation_urls.append(str(cu))
                            citations.append(
                                CitationHit(
                                    title=cit.get("title"),
                                    url=cu,
                                    snippet=cit.get("cited_text") or cit.get("snippet"),
                                    position=len(citations) + 1,
                                    is_brand_domain=_host_match(cu, url, brand),
                                )
                            )
                elif btype in {"web_search_tool_result", "web_search_result"}:
                    for item in _flatten_search_results(block):
                        cu = item.get("url")
                        if cu:
                            citation_urls.append(str(cu))
                        citations.append(
                            CitationHit(
                                title=item.get("title"),
                                url=cu,
                                snippet=item.get("snippet") or item.get("page_age"),
                                position=len(citations) + 1,
                                is_brand_domain=_host_match(cu, url, brand),
                            )
                        )

        answer = "".join(text_parts) or str(payload.get("content") or "")
        notes.append("path=anthropic_web_search model=deepseek-flash")
        return VisibilityResult(
            engine=self.engine_id,
            query=query,
            status=ProbeStatus.MEASURED,
            brand=brand,
            answer_excerpt=truncate_excerpt(answer),
            brand_mentioned=brand_mentioned(answer, brand),
            brand_cited=brand_cited(answer, brand, url, citation_urls=citation_urls),
            citations=citations,
            notes=notes,
            raw={"adapter": "deepseek", "path": "anthropic_web_search", "stop_reason": payload.get("stop_reason")},
        )


def _error_message(payload: dict[str, Any] | list[Any] | str | None) -> str:
    if payload is None:
        return ""
    if isinstance(payload, str):
        return payload[:400]
    if isinstance(payload, list):
        return str(payload)[:400]
    err = payload.get("error")
    if isinstance(err, dict):
        return str(err.get("message") or err)[:400]
    if isinstance(err, str):
        return err[:400]
    msg = payload.get("message")
    if msg:
        return str(msg)[:400]
    return str(payload)[:400]


def _flatten_search_results(block: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    content = block.get("content")
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict):
                if item.get("type") in {"web_search_result", "search_result"} or item.get("url"):
                    out.append(item)
                elif isinstance(item.get("content"), list):
                    out.extend(_flatten_search_results(item))
    results = block.get("search_results") or block.get("results")
    if isinstance(results, list):
        for item in results:
            if isinstance(item, dict):
                out.append(item)
    return out


def _host_match(link: str | None, brand_url: str | None, brand: str | None) -> bool | None:
    if not link:
        return None
    try:
        h = (urlparse(link).hostname or "").lower().removeprefix("www.")
    except Exception:
        return None
    if brand_url:
        try:
            bh = (urlparse(brand_url if "://" in brand_url else f"https://{brand_url}").hostname or "")
            bh = bh.lower().removeprefix("www.")
            if bh and (h == bh or h.endswith("." + bh)):
                return True
        except Exception:
            pass
    if brand and brand.casefold() in h:
        return True
    return False
