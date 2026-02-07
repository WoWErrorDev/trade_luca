from app.config import RiskConfig
from app.data.store import DataStore
from app.risk.risk_guard import RiskGuard
from app.strategies.base import Signal


class DummyLogger:
    def info(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass


def test_risk_guard_blocks_when_max_positions(tmp_path):
    store = DataStore(tmp_path / "test.db")
    store.migrate()
    for idx in range(3):
        store.upsert_position(f"SYM{idx}", qty=1.0, avg_price=100)
    config = RiskConfig(max_positions=2)
    guard = RiskGuard(config, store, DummyLogger())
    signal = Signal("BTCUSDT", "LONG", 100, 95, 110, 0.8, {})
    assert guard.can_trade("BTCUSDT", signal) is False
