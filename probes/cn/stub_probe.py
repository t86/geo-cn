"""Honest stub probe — never invents live citations."""

from __future__ import annotations

from .base import EngineProbe, ProbeContext
from .models import EngineId, ProbeStatus, VisibilityResult

ENGINE_NOTES: dict[EngineId, str] = {
    EngineId.DOUBAO: "Stub only. Wire Bytespider-aware crawl checks + Doubao answer capture later.",
    EngineId.DEEPSEEK: "Stub only. Official crawler docs sparse; prefer measured chat/search adapters.",
    EngineId.TONGYI: "Stub only. Consider Qwen API / 通义联网 adapters + YisouSpider robots checks.",
    EngineId.KIMI: "Stub only. Kimi has official SearchBot docs; good first live adapter candidate.",
    EngineId.ERNIE: "Stub only. Prefer Baidu AI search / 文心 adapters + Baiduspider path.",
    EngineId.YUANBAO: "Stub only. Prefer Sogou + WeChat 公众号 distribution signals.",
}


class StubProbe(EngineProbe):
    def __init__(self, engine_id: EngineId) -> None:
        self.engine_id = engine_id

    def probe(
        self,
        query: str,
        *,
        brand: str | None = None,
        url: str | None = None,
        context: ProbeContext | None = None,
    ) -> VisibilityResult:
        ctx = context or ProbeContext()
        notes = [
            ENGINE_NOTES[self.engine_id],
            "status=stub: no live engine call was made; fields that need measurement are null.",
            f"locale={ctx.locale} market={ctx.market} dry_run={ctx.dry_run}",
        ]
        if url:
            notes.append(f"target_url_provided={url}")
        return VisibilityResult(
            engine=self.engine_id,
            query=query,
            status=ProbeStatus.STUB,
            brand=brand,
            brand_mentioned=None,
            brand_cited=None,
            citations=[],
            competitor_mentions=[],
            raw={"adapter": "stub", "url": url},
            notes=notes,
        )
