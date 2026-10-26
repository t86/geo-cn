"""Engine probe registry — stubs by default; live DeepSeek/智谱 when keys present."""

from __future__ import annotations

import os

from .base import EngineProbe
from .models import EngineId
from .stub_probe import StubProbe

_REGISTRY: dict[EngineId, EngineProbe] = {}


def _has_deepseek_key() -> bool:
    return bool(os.environ.get("DEEPSEEK_API_KEY", "").strip())


def _has_zhipu_key() -> bool:
    return bool(
        os.environ.get("ZHIPU_API_KEY", "").strip()
        or os.environ.get("BIGMODEL_API_KEY", "").strip()
    )


def refresh_registry() -> dict[EngineId, EngineProbe]:
    """Rebuild registry from env. Safe to call after exporting API keys."""
    global _REGISTRY
    registry: dict[EngineId, EngineProbe] = {engine: StubProbe(engine) for engine in EngineId}

    if _has_deepseek_key():
        from .engines.deepseek_probe import DeepSeekProbe

        registry[EngineId.DEEPSEEK] = DeepSeekProbe()
    if _has_zhipu_key():
        from .engines.zhipu_probe import ZhipuProbe

        registry[EngineId.ZHIPU] = ZhipuProbe()

    _REGISTRY = registry
    return _REGISTRY


def register_probe(probe: EngineProbe) -> None:
    """Replace or add a probe implementation (e.g. live API adapter)."""
    _REGISTRY[probe.engine_id] = probe


def get_probe(engine: EngineId | str) -> EngineProbe:
    if not _REGISTRY:
        refresh_registry()
    key = EngineId(engine) if isinstance(engine, str) else engine
    return _REGISTRY[key]


def list_engines() -> list[str]:
    return [e.value for e in EngineId]


def live_engines() -> list[str]:
    """Engine IDs currently backed by a non-stub adapter (based on env keys)."""
    if not _REGISTRY:
        refresh_registry()
    out: list[str] = []
    for eid, probe in _REGISTRY.items():
        if type(probe).__name__ != "StubProbe":
            out.append(eid.value)
    return out


# Populate on import
refresh_registry()
