from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Protocol

from app.config import AppConfig
from app.data.store import DataStore


@dataclass
class Signal:
    symbol: str
    direction: str
    entry: float
    stop: float
    take_profit: float
    confidence: float
    features: Dict[str, float]


class Strategy(Protocol):
    name: str

    def generate(self, symbol: str, store: DataStore, config: AppConfig) -> Signal:  # noqa: D401
        """Generate a trade signal."""
