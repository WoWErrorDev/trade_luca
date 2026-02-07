from app.data.store import DataStore
from app.oms.manager import OrderManager
from app.oms.orders import OrderIntent


class DummyLogger:
    def info(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass


def test_order_idempotency(tmp_path):
    store = DataStore(tmp_path / "test.db")
    store.migrate()
    manager = OrderManager(store, DummyLogger())
    intent = OrderIntent(
        intent_id="abc",
        symbol="BTCUSDT",
        side="LONG",
        price=100.0,
        qty=1.0,
        venue="binance",
        order_type="LIMIT",
        mode="paper",
        score=70,
    )

    class DummyAdapter:
        def submit_order(self, *args, **kwargs):
            return {"status": "ACK"}

    manager.submit_intent(intent, {"binance": DummyAdapter()})
    manager.submit_intent(intent, {"binance": DummyAdapter()})
    rows = store.conn.execute("SELECT COUNT(*) as count FROM orders").fetchone()
    assert rows["count"] == 1
