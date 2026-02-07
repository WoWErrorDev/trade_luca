from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Dict, List

import yaml


@dataclass
class BinanceConfig:
    api_key: str
    api_secret: str
    futures_vs_spot: str = "futures"
    min_volume: float = 1_000_000
    max_spread: float = 0.001
    min_notional: float = 10.0


@dataclass
class IBKRConfig:
    gateway_host: str = "127.0.0.1"
    gateway_port_paper: int = 4002
    gateway_port_live: int = 4001
    client_id: int = 1
    universe_csv: str = "ibkr_universe.csv"
    fx_pairs: List[str] = field(default_factory=lambda: ["EURUSD", "USDJPY", "GBPUSD", "AUDUSD"])
    fut_roots: List[str] = field(default_factory=lambda: ["ES", "NQ", "CL", "GC"])


@dataclass
class RiskConfig:
    risk_per_trade: float = 0.01
    max_total_exposure: float = 1.0
    max_positions: int = 20
    max_exposure_per_symbol: float = 0.1
    max_leverage: float = 3.0
    kill_switch_dd: float = 0.2


@dataclass
class ScoringConfig:
    threshold: float = 60.0


@dataclass
class BacktestConfig:
    window_days: int = 90
    min_trades: int = 20
    max_drawdown: float = 0.2
    min_stability: float = 0.3


@dataclass
class AlertsConfig:
    telegram_token: str | None = None
    telegram_chat_id: str | None = None


@dataclass
class AppConfig:
    mode: str
    venues: List[str]
    timeframes: List[str]
    rolling_backtest_window: str
    binance: BinanceConfig
    ibkr: IBKRConfig
    risk: RiskConfig
    scoring: ScoringConfig
    backtest: BacktestConfig
    alerts: AlertsConfig


class ConfigError(ValueError):
    pass


def _env_or(default: str, env_key: str) -> str:
    value = os.getenv(env_key)
    return value if value is not None else default


def load_config(path: str = "config.yaml") -> AppConfig:
    with open(path, "r", encoding="utf-8") as handle:
        raw: Dict[str, Any] = yaml.safe_load(handle) or {}

    mode = raw.get("mode", "paper")
    venues = raw.get("venues", ["binance"])
    if mode not in {"paper", "live"}:
        raise ConfigError("mode must be paper|live")

    binance_raw = raw.get("binance", {})
    binance = BinanceConfig(
        api_key=_env_or(binance_raw.get("api_key", ""), "BINANCE_API_KEY"),
        api_secret=_env_or(binance_raw.get("api_secret", ""), "BINANCE_API_SECRET"),
        futures_vs_spot=binance_raw.get("futures_vs_spot", "futures"),
        min_volume=binance_raw.get("symbols_filters", {}).get("minVolume", 1_000_000),
        max_spread=binance_raw.get("symbols_filters", {}).get("maxSpread", 0.001),
        min_notional=binance_raw.get("symbols_filters", {}).get("minNotional", 10.0),
    )

    ibkr_raw = raw.get("ibkr", {})
    ibkr = IBKRConfig(
        gateway_host=ibkr_raw.get("gateway_host", "127.0.0.1"),
        gateway_port_paper=ibkr_raw.get("gateway_port_paper", 4002),
        gateway_port_live=ibkr_raw.get("gateway_port_live", 4001),
        client_id=ibkr_raw.get("client_id", 1),
        universe_csv=ibkr_raw.get("universe_csv", "ibkr_universe.csv"),
        fx_pairs=ibkr_raw.get("fx_pairs", ["EURUSD", "USDJPY", "GBPUSD", "AUDUSD"]),
        fut_roots=ibkr_raw.get("fut_roots", ["ES", "NQ", "CL", "GC"]),
    )

    risk_raw = raw.get("risk", {})
    risk = RiskConfig(
        risk_per_trade=risk_raw.get("risk_per_trade", 0.01),
        max_total_exposure=risk_raw.get("max_total_exposure", 1.0),
        max_positions=risk_raw.get("max_positions", 20),
        max_exposure_per_symbol=risk_raw.get("max_exposure_per_symbol", 0.1),
        max_leverage=risk_raw.get("max_leverage", 3.0),
        kill_switch_dd=risk_raw.get("kill_switch_dd", 0.2),
    )

    scoring_raw = raw.get("scoring", {})
    scoring = ScoringConfig(threshold=scoring_raw.get("threshold", 60.0))

    backtest_raw = raw.get("rolling_backtest", {})
    backtest = BacktestConfig(
        window_days=backtest_raw.get("window_days", 90),
        min_trades=backtest_raw.get("min_trades", 20),
        max_drawdown=backtest_raw.get("max_drawdown", 0.2),
        min_stability=backtest_raw.get("min_stability", 0.3),
    )

    alerts_raw = raw.get("alerts", {})
    alerts = AlertsConfig(
        telegram_token=_env_or(alerts_raw.get("telegram_token", ""), "TELEGRAM_TOKEN") or None,
        telegram_chat_id=_env_or(alerts_raw.get("telegram_chat_id", ""), "TELEGRAM_CHAT_ID")
        or None,
    )

    timeframes = raw.get("timeframes", ["1m", "5m", "1h"])
    rolling_backtest_window = raw.get("rolling_backtest_window", "1h")

    return AppConfig(
        mode=mode,
        venues=venues,
        timeframes=timeframes,
        rolling_backtest_window=rolling_backtest_window,
        binance=binance,
        ibkr=ibkr,
        risk=risk,
        scoring=scoring,
        backtest=backtest,
        alerts=alerts,
    )
