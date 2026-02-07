from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from app.config import AppConfig
from app.data.store import DataStore
from app.strategies.base import Signal


@dataclass
class EdgeMetrics:
    ev: float
    winrate: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    max_drawdown: float
    trade_count: int
    stability_score: float
    valid: bool


@dataclass
class ScoreBreakdown:
    total: float
    components: Dict[str, float]

    def to_dict(self) -> Dict[str, float]:
        return {"total": self.total, **self.components}


class ScoreCalculator:
    def __init__(self, config: AppConfig, store: DataStore, logger) -> None:
        self.config = config
        self.store = store
        self.logger = logger

    def score(self, symbol: str, signal: Signal, metrics: EdgeMetrics) -> ScoreBreakdown:
        ev_component = max(min(metrics.ev * 100, 40), -40)
        confidence_component = signal.confidence * 20
        stability_component = metrics.stability_score * 20
        liquidity_component = 10
        penalty = 0
        total = ev_component + confidence_component + stability_component + liquidity_component - penalty
        components = {
            "ev": ev_component,
            "confidence": confidence_component,
            "stability": stability_component,
            "liquidity": liquidity_component,
            "penalty": penalty,
        }
        return ScoreBreakdown(total=total, components=components)
