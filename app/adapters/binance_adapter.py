from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from typing import Dict, List

from app.config import AppConfig


@dataclass
class BinanceSymbol:
    symbol: str
    volume: float
    bid: float
    ask: float
    min_notional: float
    status: str

    @property
    def spread(self) -> float:
        if self.ask <= 0:
            return 1.0
        return (self.ask - self.bid) / self.ask


class BinanceAdapter:
    def __init__(self, config: AppConfig, logger) -> None:
        self.config = config
        self.logger = logger
        self.last_universe_fetch = 0.0

    def discover_symbols(self) -> List[BinanceSymbol]:
        self.last_universe_fetch = time.time()
        symbols = [
            BinanceSymbol(symbol="BTCUSDT", volume=2_000_000_000, bid=30000, ask=30010, min_notional=10, status="TRADING"),
            BinanceSymbol(symbol="ETHUSDT", volume=1_000_000_000, bid=2000, ask=2001, min_notional=10, status="TRADING"),
        ]
        self.logger.info("binance_discover", extra={"count": len(symbols)})
        return symbols

    def submit_order(self, symbol: str, side: str, price: float, qty: float, order_type: str) -> Dict[str, str]:
        client_order_id = hashlib.sha256(f"{symbol}:{side}:{price}:{qty}".encode()).hexdigest()[:16]
        self.logger.info(
            "binance_order_submit",
            extra={
                "symbol": symbol,
                "side": side,
                "price": price,
                "qty": qty,
                "type": order_type,
                "client_order_id": client_order_id,
            },
        )
        return {"status": "ACK", "client_order_id": client_order_id}
