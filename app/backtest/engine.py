from __future__ import annotations

from dataclasses import dataclass
from typing import List

from app.strategies.base import Signal


@dataclass
class BacktestResult:
    equity_curve: List[float]
    trades: List[Signal]


class BacktestEngine:
    def run(self, signals: List[Signal]) -> BacktestResult:
        equity = 1.0
        curve = [equity]
        for signal in signals:
            equity *= 1 + (0.001 if signal.direction == "LONG" else -0.001)
            curve.append(equity)
        return BacktestResult(equity_curve=curve, trades=signals)
