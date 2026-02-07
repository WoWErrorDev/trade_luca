from __future__ import annotations

import statistics

from app.config import AppConfig
from app.data.store import DataStore
from app.strategies.base import Signal


class MeanReversionStrategy:
    name = "mean_reversion"

    def generate(self, symbol: str, store: DataStore, config: AppConfig) -> Signal:
        bars = store.fetch_bars(symbol, venue="binance", timeframe=config.rolling_backtest_window, limit=40)
        if len(bars) < 30:
            return Signal(symbol, "FLAT", 0, 0, 0, 0, {})
        closes = [bar.close for bar in reversed(bars)]
        mean = statistics.mean(closes)
        std = statistics.pstdev(closes) or 1.0
        zscore = (closes[-1] - mean) / std
        if zscore > 1.0:
            direction = "SHORT"
        elif zscore < -1.0:
            direction = "LONG"
        else:
            direction = "FLAT"
        entry = closes[-1]
        stop = entry * (0.97 if direction == "LONG" else 1.03)
        take_profit = entry * (1.02 if direction == "LONG" else 0.98)
        confidence = min(abs(zscore) / 3.0, 1.0)
        return Signal(
            symbol=symbol,
            direction=direction,
            entry=entry,
            stop=stop,
            take_profit=take_profit,
            confidence=confidence,
            features={"zscore": zscore, "mean": mean},
        )
