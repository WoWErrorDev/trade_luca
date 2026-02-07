from __future__ import annotations

from app.config import AppConfig
from app.data.store import DataStore
from app.strategies.base import Signal


class BreakoutVolStrategy:
    name = "breakout_vol"

    def generate(self, symbol: str, store: DataStore, config: AppConfig) -> Signal:
        bars = store.fetch_bars(symbol, venue="binance", timeframe=config.rolling_backtest_window, limit=30)
        if len(bars) < 20:
            return Signal(symbol, "FLAT", 0, 0, 0, 0, {})
        highs = [bar.high for bar in reversed(bars)]
        lows = [bar.low for bar in reversed(bars)]
        last = bars[0].close
        high_break = max(highs[:-1])
        low_break = min(lows[:-1])
        direction = "FLAT"
        if last > high_break:
            direction = "LONG"
        elif last < low_break:
            direction = "SHORT"
        entry = last
        stop = entry * (0.96 if direction == "LONG" else 1.04)
        take_profit = entry * (1.06 if direction == "LONG" else 0.94)
        confidence = 0.7 if direction != "FLAT" else 0.0
        return Signal(
            symbol=symbol,
            direction=direction,
            entry=entry,
            stop=stop,
            take_profit=take_profit,
            confidence=confidence,
            features={"high_break": high_break, "low_break": low_break},
        )
