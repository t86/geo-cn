"""Structured visibility results for China AI engine probes."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class EngineId(str, Enum):
    DOUBAO = "doubao"
    DEEPSEEK = "deepseek"
    TONGYI = "tongyi"
    KIMI = "kimi"
    ERNIE = "ernie"
    YUANBAO = "yuanbao"


class ProbeStatus(str, Enum):
    """How the result was produced."""

    STUB = "stub"  # No live call; placeholders only
    MEASURED = "measured"  # Real API / browser / partner data
    ERROR = "error"
    UNSUPPORTED = "unsupported"


@dataclass
class CitationHit:
    """One cited or mentioned source in an engine answer."""

    title: str | None = None
    url: str | None = None
    snippet: str | None = None
    position: int | None = None
    is_brand_domain: bool | None = None


@dataclass
class VisibilityResult:
    """Contract output: query a brand/keyword → structured visibility."""

    engine: EngineId
    query: str
    status: ProbeStatus
    brand: str | None = None
    answer_excerpt: str | None = None
    brand_mentioned: bool | None = None
    brand_cited: bool | None = None
    citations: list[CitationHit] = field(default_factory=list)
    competitor_mentions: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["engine"] = self.engine.value
        data["status"] = self.status.value
        return data
