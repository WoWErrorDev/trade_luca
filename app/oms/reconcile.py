from __future__ import annotations

from app.data.store import DataStore


class Reconciler:
    def __init__(self, store: DataStore, logger) -> None:
        self.store = store
        self.logger = logger

    def reconcile(self) -> None:
        orders = []
        self.logger.info("reconcile", extra={"orders": len(orders)})
