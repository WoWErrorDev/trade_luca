from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Dict, List

from app.config import AppConfig


@dataclass
class IBKRContract:
    symbol: str
    exchange: str
    sec_type: str


class IBKRAdapter:
    def __init__(self, config: AppConfig, logger) -> None:
        self.config = config
        self.logger = logger

    def discover_symbols(self) -> List[IBKRContract]:
        contracts = [
            IBKRContract(symbol="AAPL", exchange="SMART", sec_type="STK"),
            IBKRContract(symbol="MSFT", exchange="SMART", sec_type="STK"),
        ]
        self.logger.info("ibkr_discover", extra={"count": len(contracts)})
        return contracts

    def submit_order(self, symbol: str, side: str, price: float, qty: float, order_type: str) -> Dict[str, str]:
        client_order_id = hashlib.sha256(f"{symbol}:{side}:{price}:{qty}".encode()).hexdigest()[:16]
        self.logger.info(
            "ibkr_order_submit",
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
