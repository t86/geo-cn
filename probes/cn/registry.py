"""Engine probe registry (stubs by default)."""

from __future__ import annotations

from .base import EngineProbe
from .models import EngineId
from .stub_probe import StubProbe

_REGISTRY: dict[EngineId, EngineProbe] = {
    engine: StubProbe(engine) for engine in EngineId
}


def register_probe(probe: EngineProbe) -> None:
    """Replace or add a probe implementation (e.g. live API adapter)."""
    _REGISTRY[probe.engine_id] = probe


def get_probe(engine: EngineId | str) -> EngineProbe:
    key = EngineId(engine) if isinstance(engine, str) else engine
    return _REGISTRY[key]


def list_engines() -> list[str]:
    return [e.value for e in EngineId]
