from __future__ import annotations

from app.config import AppConfig
from app.data.store import DataStore
from app.strategies.base import Signal


class TrendStrategy:
    name = "trend"

    def generate(self, symbol: str, store: DataStore, config: AppConfig) -> Signal:
        bars = store.fetch_bars(symbol, venue="binance", timeframe=config.rolling_backtest_window, limit=50)
        if len(bars) < 20:
            return Signal(symbol, "FLAT", 0, 0, 0, 0, {})
        closes = [bar.close for bar in reversed(bars)]
        fast = sum(closes[-5:]) / 5
        slow = sum(closes[-20:]) / 20
        direction = "LONG" if fast > slow else "SHORT" if fast < slow else "FLAT"
        entry = closes[-1]
        stop = entry * (0.98 if direction == "LONG" else 1.02)
        take_profit = entry * (1.04 if direction == "LONG" else 0.96)
        confidence = min(abs(fast - slow) / entry, 1.0)
        return Signal(
            symbol=symbol,
            direction=direction,
            entry=entry,
            stop=stop,
            take_profit=take_profit,
            confidence=confidence,
            features={"fast": fast, "slow": slow},
        )
