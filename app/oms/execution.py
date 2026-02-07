from __future__ import annotations


def slippage_guard(price: float, max_slippage: float) -> float:
    return price * (1 + max_slippage)
