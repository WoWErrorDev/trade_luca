from __future__ import annotations

import json
from dataclasses import asdict

from app.backtest.engine import BacktestResult


def to_json(result: BacktestResult) -> str:
    payload = {"equity_curve": result.equity_curve, "trades": [asdict(trade) for trade in result.trades]}
    return json.dumps(payload, indent=2)


def to_html(result: BacktestResult) -> str:
    return f"<html><body><pre>{to_json(result)}</pre></body></html>"
