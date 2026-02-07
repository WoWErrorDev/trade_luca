from __future__ import annotations

from app.config import RiskConfig
from app.data.store import DataStore
from app.strategies.base import Signal


class RiskGuard:
    def __init__(self, config: RiskConfig, store: DataStore, logger) -> None:
        self.config = config
        self.store = store
        self.logger = logger
        self.equity = 1_000_000.0
        self.peak_equity = self.equity

    def can_trade(self, symbol: str, signal: Signal) -> bool:
        if signal.direction == "FLAT":
            return False
        positions = self.store.list_positions()
        if len(positions) >= self.config.max_positions:
            return False
        exposure = sum(abs(row["qty"] * row["avg_price"]) for row in positions)
        if exposure / self.equity > self.config.max_total_exposure:
            return False
        drawdown = (self.peak_equity - self.equity) / self.peak_equity
        if drawdown > self.config.kill_switch_dd:
            return False
        return True
