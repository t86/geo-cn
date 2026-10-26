"""Probe interface for China AI engines."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from .models import EngineId, VisibilityResult


@dataclass
class ProbeContext:
    """Optional run context shared across probes."""

    locale: str = "zh-CN"
    market: str = "CN"
    timeout_s: float = 60.0
    dry_run: bool = True
    extra: dict[str, Any] = field(default_factory=dict)


class EngineProbe(ABC):
    """Query brand/keyword → structured VisibilityResult.

    Implementations may call vendor APIs, browser automation, or partner
    Share-of-Voice providers. The default registry wires StubProbe only.
    """

    engine_id: EngineId

    @abstractmethod
    def probe(
        self,
        query: str,
        *,
        brand: str | None = None,
        url: str | None = None,
        context: ProbeContext | None = None,
    ) -> VisibilityResult:
        raise NotImplementedError
