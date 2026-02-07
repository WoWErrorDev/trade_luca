from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Iterable, List, Optional


@dataclass
class Bar:
    symbol: str
    venue: str
    timeframe: str
    ts: int
    open: float
    high: float
    low: float
    close: float
    volume: float


class DataStore:
    def __init__(self, path: str) -> None:
        self.path = path
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row

    def migrate(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bars (
                symbol TEXT,
                venue TEXT,
                timeframe TEXT,
                ts INTEGER,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL,
                PRIMARY KEY (symbol, venue, timeframe, ts)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                intent_id TEXT PRIMARY KEY,
                symbol TEXT,
                side TEXT,
                price REAL,
                qty REAL,
                status TEXT,
                venue TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS positions (
                symbol TEXT PRIMARY KEY,
                qty REAL,
                avg_price REAL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS scores (
                symbol TEXT,
                ts INTEGER,
                score REAL,
                breakdown TEXT
            )
            """
        )
        self.conn.commit()

    def upsert_bars(self, bars: Iterable[Bar]) -> None:
        cursor = self.conn.cursor()
        cursor.executemany(
            """
            INSERT OR REPLACE INTO bars
            (symbol, venue, timeframe, ts, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    bar.symbol,
                    bar.venue,
                    bar.timeframe,
                    bar.ts,
                    bar.open,
                    bar.high,
                    bar.low,
                    bar.close,
                    bar.volume,
                )
                for bar in bars
            ],
        )
        self.conn.commit()

    def fetch_bars(self, symbol: str, venue: str, timeframe: str, limit: int = 500) -> List[Bar]:
        cursor = self.conn.cursor()
        rows = cursor.execute(
            """
            SELECT * FROM bars
            WHERE symbol=? AND venue=? AND timeframe=?
            ORDER BY ts DESC
            LIMIT ?
            """,
            (symbol, venue, timeframe, limit),
        ).fetchall()
        return [
            Bar(
                symbol=row["symbol"],
                venue=row["venue"],
                timeframe=row["timeframe"],
                ts=row["ts"],
                open=row["open"],
                high=row["high"],
                low=row["low"],
                close=row["close"],
                volume=row["volume"],
            )
            for row in rows
        ]

    def get_order(self, intent_id: str) -> Optional[sqlite3.Row]:
        cursor = self.conn.cursor()
        return cursor.execute("SELECT * FROM orders WHERE intent_id=?", (intent_id,)).fetchone()

    def save_order(self, intent_id: str, symbol: str, side: str, price: float, qty: float, status: str, venue: str) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO orders (intent_id, symbol, side, price, qty, status, venue)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (intent_id, symbol, side, price, qty, status, venue),
        )
        self.conn.commit()

    def list_positions(self) -> List[sqlite3.Row]:
        cursor = self.conn.cursor()
        return cursor.execute("SELECT * FROM positions").fetchall()

    def upsert_position(self, symbol: str, qty: float, avg_price: float) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO positions (symbol, qty, avg_price)
            VALUES (?, ?, ?)
            """,
            (symbol, qty, avg_price),
        )
        self.conn.commit()
