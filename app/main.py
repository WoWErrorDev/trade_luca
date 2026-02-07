from __future__ import annotations

import argparse
import sys
from typing import List

from app.adapters.binance_adapter import BinanceAdapter
from app.adapters.ibkr_adapter import IBKRAdapter
from app.config import AppConfig, load_config
from app.data.store import DataStore
from app.monitoring.logger import get_logger
from app.monitoring.alerts import Alerts
from app.universe import UniverseBuilder
from app.risk.risk_guard import RiskGuard
from app.oms.manager import OrderManager
from app.edge.rolling_backtest import RollingBacktest
from app.strategies.trend import TrendStrategy
from app.strategies.mean_reversion import MeanReversionStrategy
from app.strategies.breakout_vol import BreakoutVolStrategy
from app.edge.metrics import ScoreCalculator


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Multi-market auto-trading bot")
    parser.add_argument("--mode", choices=["paper", "live"], default=None)
    parser.add_argument("--venue", choices=["binance", "ibkr", "both"], default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--once", action="store_true")
    return parser.parse_args(argv)


def build_venues(config: AppConfig, venue: str | None) -> List[str]:
    if venue is None:
        return config.venues
    if venue == "both":
        return ["binance", "ibkr"]
    return [venue]


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    config = load_config()
    if args.mode:
        config.mode = args.mode
    venues = build_venues(config, args.venue)

    logger = get_logger()
    alerts = Alerts(config.alerts, logger)
    store = DataStore("trading.db")
    store.migrate()

    adapters = {}
    if "binance" in venues:
        adapters["binance"] = BinanceAdapter(config, logger)
    if "ibkr" in venues:
        adapters["ibkr"] = IBKRAdapter(config, logger)

    universe_builder = UniverseBuilder(config, adapters, store, logger)
    risk_guard = RiskGuard(config.risk, store, logger)
    order_manager = OrderManager(store, logger)

    strategies = [TrendStrategy(), MeanReversionStrategy(), BreakoutVolStrategy()]
    backtester = RollingBacktest(config, store, logger)
    scorer = ScoreCalculator(config, store, logger)

    def run_cycle() -> None:
        universe = universe_builder.refresh()
        logger.info("universe", extra={"size": len(universe)})
        candidates = []
        for symbol in universe:
            metrics = backtester.evaluate(symbol)
            if not metrics.valid:
                continue
            for strategy in strategies:
                signal = strategy.generate(symbol, store, config)
                if signal.direction == "FLAT":
                    continue
                score = scorer.score(symbol, signal, metrics)
                if score.total < config.scoring.threshold:
                    logger.info(
                        "candidate_rejected",
                        extra={"symbol": symbol, "score": score.to_dict()},
                    )
                    continue
                candidates.append((symbol, signal, score))

        candidates.sort(key=lambda item: item[2].total, reverse=True)
        logger.info(
            "top_candidates",
            extra={
                "count": len(candidates),
                "top": [
                    {
                        "symbol": symbol,
                        "score": score.total,
                        "breakdown": score.to_dict(),
                    }
                    for symbol, _, score in candidates[:10]
                ],
            },
        )

        for symbol, signal, score in candidates:
            if not risk_guard.can_trade(symbol, signal):
                logger.warning(
                    "risk_block",
                    extra={"symbol": symbol, "reason": "risk_guard"},
                )
                continue
            intent = order_manager.build_intent(symbol, signal, score, config.mode)
            if args.dry_run:
                logger.info("dry_run_trade", extra={"intent": intent.to_dict()})
                continue
            order_manager.submit_intent(intent, adapters)

    try:
        run_cycle()
        if not args.once:
            logger.warning("only_once_supported", extra={"reason": "loop disabled"})
    except Exception as exc:  # noqa: BLE001
        logger.exception("fatal", extra={"error": str(exc)})
        alerts.send("Fatal error: " + str(exc))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
