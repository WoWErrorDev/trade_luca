from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List

from app.data.store import Bar


def resample_bars(bars: Iterable[Bar], target_tf: int) -> List[Bar]:
    buckets: Dict[int, List[Bar]] = defaultdict(list)
    for bar in bars:
        bucket = bar.ts - (bar.ts % (target_tf * 60))
        buckets[bucket].append(bar)

    resampled = []
    for bucket_ts, items in buckets.items():
        items_sorted = sorted(items, key=lambda item: item.ts)
        open_price = items_sorted[0].open
        close_price = items_sorted[-1].close
        high_price = max(item.high for item in items_sorted)
        low_price = min(item.low for item in items_sorted)
        volume = sum(item.volume for item in items_sorted)
        resampled.append(
            Bar(
                symbol=items_sorted[0].symbol,
                venue=items_sorted[0].venue,
                timeframe=f"{target_tf}m",
                ts=bucket_ts,
                open=open_price,
                high=high_price,
                low=low_price,
                close=close_price,
                volume=volume,
            )
        )
    return sorted(resampled, key=lambda item: item.ts)


def check_integrity(bars: List[Bar]) -> List[str]:
    issues = []
    seen = set()
    for bar in bars:
        key = (bar.symbol, bar.venue, bar.timeframe, bar.ts)
        if key in seen:
            issues.append("duplicate")
        seen.add(key)
    if bars != sorted(bars, key=lambda item: item.ts):
        issues.append("out_of_order")
    return issues
