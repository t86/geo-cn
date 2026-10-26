"""Per-engine adapter modules.

Live implementations:
- deepseek_probe.DeepSeekProbe — DEEPSEEK_API_KEY
- zhipu_probe.ZhipuProbe — ZHIPU_API_KEY or BIGMODEL_API_KEY

Registered automatically via probes.cn.registry.refresh_registry() when keys are set.
"""

from .deepseek_probe import DeepSeekProbe
from .zhipu_probe import ZhipuProbe

__all__ = ["DeepSeekProbe", "ZhipuProbe"]
