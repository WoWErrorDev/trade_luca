from __future__ import annotations


def size_from_risk(equity: float, risk_per_trade: float, stop_distance: float) -> float:
    if stop_distance <= 0:
        return 0
    risk_amount = equity * risk_per_trade
    return risk_amount / stop_distance
