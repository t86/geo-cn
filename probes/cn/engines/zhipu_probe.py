"""Live 智谱 (Zhipu / BigModel) visibility probe.

Prefer chat.completions + web_search tool (OpenAI-compatible HTTPS).
Fallback: standalone /paas/v4/web_search for URL visibility.
"""

from __future__ import annotations

from typing import Any

from ..base import EngineProbe, ProbeContext
from ..models import CitationHit, EngineId, ProbeStatus, VisibilityResult
from .common import (
    brand_cited,
    brand_mentioned,
    env_key,
    http_json,
    is_brand_domain,
    openai_message_content,
    truncate_excerpt,
)

CHAT_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
WEB_SEARCH_URL = "https://open.bigmodel.cn/api/paas/v4/web_search"
PRIMARY_MODEL = "glm-4-flash"
FALLBACK_MODEL = "glm-4-air"
SYSTEM_PROMPT = (
    "你是简短的中文助手，用于 GEO 可见度探测。"
    "结合联网搜索结果回答，不要编造未出现的事实或链接。"
)


class ZhipuProbe(EngineProbe):
    engine_id = EngineId.ZHIPU

    def probe(
        self,
        query: str,
        *,
        brand: str | None = None,
        url: str | None = None,
        context: ProbeContext | None = None,
    ) -> VisibilityResult:
        ctx = context or ProbeContext()
        api_key = env_key("ZHIPU_API_KEY", "BIGMODEL_API_KEY")
        if not api_key:
            return VisibilityResult(
                engine=self.engine_id,
                query=query,
                status=ProbeStatus.STUB,
                brand=brand,
                notes=[
                    "No ZHIPU_API_KEY or BIGMODEL_API_KEY set; returning stub.",
                    "Export ZHIPU_API_KEY (or BIGMODEL_API_KEY) for measured 智谱 probes.",
                ],
                raw={"adapter": "zhipu", "reason": "missing_api_key"},
            )

        if ctx.dry_run:
            return VisibilityResult(
                engine=self.engine_id,
                query=query,
                status=ProbeStatus.STUB,
                brand=brand,
                notes=["dry_run=True: skipped live 智谱 call. Pass --live / dry_run=False."],
                raw={"adapter": "zhipu", "reason": "dry_run"},
            )

        notes: list[str] = []
        try:
            chat_result = self._probe_chat_web_search(
                query, brand=brand, url=url, api_key=api_key, timeout_s=ctx.timeout_s, notes=notes
            )
            if chat_result is not None:
                return chat_result
            notes.append("chat+web_search failed; falling back to /paas/v4/web_search only.")
            return self._probe_web_search_only(
                query, brand=brand, url=url, api_key=api_key, timeout_s=ctx.timeout_s, notes=notes
            )
        except Exception as exc:  # noqa: BLE001
            return VisibilityResult(
                engine=self.engine_id,
                query=query,
                status=ProbeStatus.ERROR,
                brand=brand,
                error=str(exc),
                notes=notes + [f"Zhipu probe exception: {exc}"],
                raw={"adapter": "zhipu"},
            )

    def _probe_chat_web_search(
        self,
        query: str,
        *,
        brand: str | None,
        url: str | None,
        api_key: str,
        timeout_s: float,
        notes: list[str],
    ) -> VisibilityResult | None:
        model = PRIMARY_MODEL
        status_code, payload = self._post_chat(api_key, model, query, timeout_s)
        if status_code >= 400:
            notes.append(
                f"model={PRIMARY_MODEL} HTTP {status_code}: {_err(payload)}; trying {FALLBACK_MODEL}."
            )
            model = FALLBACK_MODEL
            status_code, payload = self._post_chat(api_key, model, query, timeout_s)

        if status_code >= 400 or not isinstance(payload, dict):
            notes.append(f"chat+web_search failed HTTP {status_code}: {_err(payload)}")
            return None

        answer = openai_message_content(payload)
        citations, citation_urls = _extract_zhipu_citations(payload, brand_url=url, brand=brand)
        # Also scan message for web_search tool payloads some SDK shapes nest under message
        message = ((payload.get("choices") or [{}])[0].get("message") or {})
        if not citations:
            extra_c, extra_u = _citations_from_obj(message, brand_url=url, brand=brand)
            citations.extend(extra_c)
            citation_urls.extend(extra_u)

        notes.append(
            f"path=chat_web_search model={model} "
            f"(primary={PRIMARY_MODEL}; fallback={FALLBACK_MODEL} if needed)."
        )
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
            raw={
                "adapter": "zhipu",
                "path": "chat_web_search",
                "model": model,
                "usage": payload.get("usage"),
                "web_search_present": bool(citations),
            },
        )

    def _post_chat(
        self, api_key: str, model: str, query: str, timeout_s: float
    ) -> tuple[int, dict[str, Any] | list[Any] | str]:
        body: dict[str, Any] = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": query},
            ],
            "tools": [
                {
                    "type": "web_search",
                    "web_search": {
                        "enable": True,
                        "search_engine": "search_pro",
                        "search_result": True,
                        "count": 8,
                    },
                }
            ],
            "stream": False,
        }
        return http_json(
            "POST",
            CHAT_URL,
            headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
            body=body,
            timeout_s=timeout_s,
        )

    def _probe_web_search_only(
        self,
        query: str,
        *,
        brand: str | None,
        url: str | None,
        api_key: str,
        timeout_s: float,
        notes: list[str],
    ) -> VisibilityResult:
        body = {
            "search_query": query[:70],
            "search_engine": "search_pro",
            "search_intent": False,
            "count": 8,
        }
        status_code, payload = http_json(
            "POST",
            WEB_SEARCH_URL,
            headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
            body=body,
            timeout_s=timeout_s,
        )
        if status_code >= 400 or not isinstance(payload, dict):
            err = _err(payload) or f"HTTP {status_code}"
            return VisibilityResult(
                engine=self.engine_id,
                query=query,
                status=ProbeStatus.ERROR,
                brand=brand,
                error=err,
                notes=notes + [f"web_search-only failed: {err}"],
                raw={"adapter": "zhipu", "http_status": status_code},
            )

        citations: list[CitationHit] = []
        citation_urls: list[str] = []
        results = (
            payload.get("search_result")
            or payload.get("search_results")
            or payload.get("data")
            or []
        )
        if isinstance(results, dict):
            results = results.get("search_result") or results.get("results") or []
        if isinstance(results, list):
            for i, item in enumerate(results, start=1):
                if not isinstance(item, dict):
                    continue
                link = item.get("link") or item.get("url")
                if link:
                    citation_urls.append(str(link))
                citations.append(
                    CitationHit(
                        title=item.get("title"),
                        url=link,
                        snippet=item.get("content") or item.get("snippet") or item.get("media"),
                        position=i,
                        is_brand_domain=is_brand_domain(link, url, brand),
                    )
                )

        # Synthetic excerpt: list titles for visibility debugging (not model prose)
        titles = [c.title for c in citations if c.title]
        excerpt = truncate_excerpt("；".join(titles) if titles else None)
        mentioned = None
        if brand:
            blob = " ".join(
                filter(
                    None,
                    [excerpt or ""]
                    + [c.title or "" for c in citations]
                    + [c.snippet or "" for c in citations]
                    + citation_urls,
                )
            )
            mentioned = brand_mentioned(blob, brand)

        notes.append("path=web_search_only engine=search_pro (no chat synthesis).")
        return VisibilityResult(
            engine=self.engine_id,
            query=query,
            status=ProbeStatus.MEASURED,
            brand=brand,
            answer_excerpt=excerpt,
            brand_mentioned=mentioned,
            brand_cited=brand_cited(None, brand, url, citation_urls=citation_urls),
            citations=citations,
            notes=notes,
            raw={"adapter": "zhipu", "path": "web_search_only", "result_count": len(citations)},
        )


def _extract_zhipu_citations(
    payload: dict[str, Any], *, brand_url: str | None, brand: str | None
) -> tuple[list[CitationHit], list[str]]:
    citations: list[CitationHit] = []
    urls: list[str] = []
    # Top-level web_search / search_result (observed in some BigModel responses)
    for key in ("web_search", "search_result", "search_results", "citations"):
        block = payload.get(key)
        c, u = _citations_from_obj(block, brand_url=brand_url, brand=brand)
        citations.extend(c)
        urls.extend(u)
    # choices[].message.*
    for choice in payload.get("choices") or []:
        if not isinstance(choice, dict):
            continue
        msg = choice.get("message") or {}
        c, u = _citations_from_obj(msg, brand_url=brand_url, brand=brand)
        citations.extend(c)
        urls.extend(u)
        for key in ("web_search", "search_result", "search_results", "citations"):
            c, u = _citations_from_obj(msg.get(key), brand_url=brand_url, brand=brand)
            citations.extend(c)
            urls.extend(u)
    # Deduplicate by URL while keeping order
    seen: set[str] = set()
    deduped: list[CitationHit] = []
    dedup_urls: list[str] = []
    for hit in citations:
        key = (hit.url or "") + "|" + (hit.title or "")
        if key in seen:
            continue
        seen.add(key)
        hit.position = len(deduped) + 1
        deduped.append(hit)
        if hit.url:
            dedup_urls.append(hit.url)
    return deduped, dedup_urls


def _citations_from_obj(
    obj: Any, *, brand_url: str | None, brand: str | None
) -> tuple[list[CitationHit], list[str]]:
    citations: list[CitationHit] = []
    urls: list[str] = []
    if obj is None:
        return citations, urls
    if isinstance(obj, list):
        for i, item in enumerate(obj, start=1):
            if isinstance(item, dict):
                link = item.get("link") or item.get("url") or item.get("source_url")
                if link:
                    urls.append(str(link))
                if link or item.get("title") or item.get("content") or item.get("snippet"):
                    citations.append(
                        CitationHit(
                            title=item.get("title") or item.get("name"),
                            url=link,
                            snippet=item.get("content") or item.get("snippet") or item.get("media"),
                            position=i,
                            is_brand_domain=is_brand_domain(link, brand_url, brand),
                        )
                    )
            elif isinstance(item, str) and item.startswith("http"):
                urls.append(item)
                citations.append(
                    CitationHit(
                        url=item,
                        position=i,
                        is_brand_domain=is_brand_domain(item, brand_url, brand),
                    )
                )
        return citations, urls
    if isinstance(obj, dict):
        for key in ("search_result", "search_results", "results", "citations", "web_search"):
            if key in obj:
                c, u = _citations_from_obj(obj[key], brand_url=brand_url, brand=brand)
                citations.extend(c)
                urls.extend(u)
        # Single result-shaped dict
        if obj.get("link") or obj.get("url"):
            link = obj.get("link") or obj.get("url")
            urls.append(str(link))
            citations.append(
                CitationHit(
                    title=obj.get("title"),
                    url=link,
                    snippet=obj.get("content") or obj.get("snippet"),
                    position=1,
                    is_brand_domain=is_brand_domain(link, brand_url, brand),
                )
            )
    return citations, urls


def _err(payload: dict[str, Any] | list[Any] | str | None) -> str:
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
    if payload.get("msg"):
        return str(payload["msg"])[:400]
    if payload.get("message"):
        return str(payload["message"])[:400]
    return str(payload)[:400]

