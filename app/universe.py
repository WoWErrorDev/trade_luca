from __future__ import annotations

import csv
import time
from typing import Dict, List

from app.adapters.binance_adapter import BinanceAdapter, BinanceSymbol
from app.adapters.ibkr_adapter import IBKRAdapter, IBKRContract
from app.config import AppConfig
from app.data.store import DataStore


class UniverseBuilder:
    def __init__(self, config: AppConfig, adapters: Dict[str, object], store: DataStore, logger) -> None:
        self.config = config
        self.adapters = adapters
        self.store = store
        self.logger = logger
        self.cache: Dict[str, List[str]] = {}
        self.last_refresh = 0.0

    def refresh(self) -> List[str]:
        now = time.time()
        if now - self.last_refresh < 1800 and self.cache:
            return self.cache.get("symbols", [])

        symbols: List[str] = []
        if "binance" in self.adapters:
            adapter: BinanceAdapter = self.adapters["binance"]
            symbols.extend(self._filter_binance(adapter.discover_symbols()))
        if "ibkr" in self.adapters:
            adapter = self.adapters["ibkr"]
            symbols.extend(self._filter_ibkr(adapter))

        self.cache["symbols"] = symbols
        self.last_refresh = now
        return symbols

    def _filter_binance(self, symbols: List[BinanceSymbol]) -> List[str]:
        results = []
        for item in symbols:
            if item.status != "TRADING":
                continue
            if item.volume < self.config.binance.min_volume:
                continue
            if item.spread > self.config.binance.max_spread:
                continue
            if item.min_notional < self.config.binance.min_notional:
                continue
            results.append(item.symbol)
        return results

    def _filter_ibkr(self, adapter: IBKRAdapter) -> List[str]:
        csv_symbols: List[str] = []
        try:
            with open(self.config.ibkr.universe_csv, "r", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                for row in reader:
                    csv_symbols.append(row["symbol"])
        except FileNotFoundError:
            self.logger.warning("ibkr_csv_missing", extra={"path": self.config.ibkr.universe_csv})

        contracts = adapter.discover_symbols()
        valid = {contract.symbol for contract in contracts}
        results = [symbol for symbol in csv_symbols if symbol in valid]
        results.extend([contract.symbol for contract in contracts if contract.sec_type == "FX"])
        return list(dict.fromkeys(results))
