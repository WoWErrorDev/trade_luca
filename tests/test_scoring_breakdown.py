from app.config import AppConfig, AlertsConfig, BacktestConfig, BinanceConfig, IBKRConfig, RiskConfig, ScoringConfig
from app.data.store import DataStore
from app.edge.metrics import EdgeMetrics, ScoreCalculator
from app.strategies.base import Signal


class DummyLogger:
    def info(self, *args, **kwargs):
        pass


def build_config() -> AppConfig:
    return AppConfig(
        mode="paper",
        venues=["binance"],
        timeframes=["1m"],
        rolling_backtest_window="1h",
        binance=BinanceConfig(api_key="", api_secret=""),
        ibkr=IBKRConfig(),
        risk=RiskConfig(),
        scoring=ScoringConfig(),
        backtest=BacktestConfig(),
        alerts=AlertsConfig(),
    )


def test_scoring_breakdown_keys(tmp_path):
    store = DataStore(tmp_path / "test.db")
    store.migrate()
    config = build_config()
    calc = ScoreCalculator(config, store, DummyLogger())
    metrics = EdgeMetrics(0.01, 0.5, 0.02, 0.01, 2.0, 0.1, 30, 0.5, True)
    signal = Signal("BTCUSDT", "LONG", 100, 95, 110, 0.8, {})
    score = calc.score("BTCUSDT", signal, metrics)
    breakdown = score.to_dict()
    assert "total" in breakdown
    assert "ev" in breakdown
    assert "confidence" in breakdown
