from app.data.store import DataStore
from app.oms.reconcile import Reconciler


class DummyLogger:
    def info(self, *args, **kwargs):
        pass


def test_reconcile_keeps_orders(tmp_path):
    store = DataStore(tmp_path / "test.db")
    store.migrate()
    store.save_order("intent", "BTCUSDT", "LONG", 100, 1, "ACK", "binance")
    reconciler = Reconciler(store, DummyLogger())
    reconciler.reconcile()
    row = store.get_order("intent")
    assert row is not None
