from __future__ import annotations

import hashlib

from app.data.store import DataStore
from app.edge.metrics import ScoreBreakdown
from app.oms.orders import OrderIntent
from app.strategies.base import Signal


class OrderManager:
    def __init__(self, store: DataStore, logger) -> None:
        self.store = store
        self.logger = logger

    def build_intent(self, symbol: str, signal: Signal, score: ScoreBreakdown, mode: str) -> OrderIntent:
        intent_id = hashlib.sha256(
            f"{symbol}:{signal.direction}:{signal.entry}:{signal.stop}:{signal.take_profit}".encode()
        ).hexdigest()
        qty = max(1.0, signal.confidence * 10)
        return OrderIntent(
            intent_id=intent_id,
            symbol=symbol,
            side=signal.direction,
            price=signal.entry,
            qty=qty,
            venue="binance",
            order_type="LIMIT",
            mode=mode,
            score=score.total,
        )

    def submit_intent(self, intent: OrderIntent, adapters: dict) -> None:
        if self.store.get_order(intent.intent_id):
            self.logger.info("order_idempotent", extra={"intent_id": intent.intent_id})
            return
        adapter = adapters.get(intent.venue)
        if adapter is None:
            self.logger.error("adapter_missing", extra={"venue": intent.venue})
            return
        result = adapter.submit_order(intent.symbol, intent.side, intent.price, intent.qty, intent.order_type)
        self.store.save_order(
            intent.intent_id,
            intent.symbol,
            intent.side,
            intent.price,
            intent.qty,
            result.get("status", "SENT"),
            intent.venue,
        )
        self.logger.info("order_sent", extra={"intent": intent.to_dict(), "result": result})
