from app.data.feed import resample_bars
from app.data.store import Bar


def test_resample_no_duplicates():
    bars = [
        Bar("BTCUSDT", "binance", "1m", 0, 1, 2, 0.5, 1.5, 10),
        Bar("BTCUSDT", "binance", "1m", 60, 1.5, 2.2, 1.4, 2.0, 12),
        Bar("BTCUSDT", "binance", "1m", 120, 2.0, 2.5, 1.9, 2.3, 11),
    ]
    resampled = resample_bars(bars, target_tf=2)
    timestamps = [bar.ts for bar in resampled]
    assert len(timestamps) == len(set(timestamps))
