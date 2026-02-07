from __future__ import annotations

import math
from typing import List

from app.config import AppConfig
from app.data.store import DataStore
from app.edge.metrics import EdgeMetrics


class RollingBacktest:
    def __init__(self, config: AppConfig, store: DataStore, logger) -> None:
        self.config = config
        self.store = store
        self.logger = logger

    def evaluate(self, symbol: str) -> EdgeMetrics:
        bars = self.store.fetch_bars(symbol, venue="binance", timeframe=self.config.rolling_backtest_window, limit=200)
        if len(bars) < 50:
            return EdgeMetrics(0, 0, 0, 0, 0, 1, 0, 0, False)
        returns = []
        for idx in range(1, len(bars)):
            prev = bars[idx].close
            curr = bars[idx - 1].close
            if prev == 0:
                continue
            returns.append((curr - prev) / prev)
        if not returns:
            return EdgeMetrics(0, 0, 0, 0, 0, 1, 0, 0, False)
        ev = sum(returns) / len(returns)
        wins = [ret for ret in returns if ret > 0]
        losses = [ret for ret in returns if ret < 0]
        winrate = len(wins) / len(returns)
        avg_win = sum(wins) / len(wins) if wins else 0
        avg_loss = abs(sum(losses) / len(losses)) if losses else 0.0001
        profit_factor = avg_win / avg_loss if avg_loss else 0
        max_dd = self._max_drawdown(returns)
        stability = 1 - math.fabs((max(returns) - min(returns)))
        valid = (
            ev > 0
            and len(returns) >= self.config.backtest.min_trades
            and stability >= self.config.backtest.min_stability
            and max_dd <= self.config.backtest.max_drawdown
        )
        return EdgeMetrics(
            ev=ev,
            winrate=winrate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            max_drawdown=max_dd,
            trade_count=len(returns),
            stability_score=stability,
            valid=valid,
        )

    def _max_drawdown(self, returns: List[float]) -> float:
        equity = 1.0
        peak = 1.0
        max_dd = 0.0
        for ret in returns:
            equity *= 1 + ret
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak
            if dd > max_dd:
                max_dd = dd
        return max_dd
