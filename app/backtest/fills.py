from __future__ import annotations


def apply_fees(price: float, fee_rate: float) -> float:
    return price * (1 + fee_rate)


def apply_slippage(price: float, slippage: float) -> float:
    return price * (1 + slippage)
