from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RuntimeStore:
    latest_analysis: dict[str, Any] | None = None
    latest_explanation: dict[str, Any] | None = None
    latest_recommendations: dict[str, Any] | None = None


_store = RuntimeStore()



def get_runtime_store() -> RuntimeStore:
    return _store
