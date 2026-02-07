from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class OrderStatus(str, Enum):
    NEW = "NEW"
    SENT = "SENT"
    ACK = "ACK"
    PARTIAL = "PARTIAL"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"


@dataclass
class OrderIntent:
    intent_id: str
    symbol: str
    side: str
    price: float
    qty: float
    venue: str
    order_type: str
    mode: str
    score: float

    def to_dict(self) -> dict:
        return {
            "intent_id": self.intent_id,
            "symbol": self.symbol,
            "side": self.side,
            "price": self.price,
            "qty": self.qty,
            "venue": self.venue,
            "order_type": self.order_type,
            "mode": self.mode,
            "score": self.score,
        }
