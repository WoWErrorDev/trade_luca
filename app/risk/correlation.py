from __future__ import annotations

from typing import Dict, List


def rolling_correlation(returns: Dict[str, List[float]]) -> Dict[str, Dict[str, float]]:
    symbols = list(returns.keys())
    matrix: Dict[str, Dict[str, float]] = {symbol: {} for symbol in symbols}
    for i, sym_a in enumerate(symbols):
        for sym_b in symbols[i + 1 :]:
            series_a = returns[sym_a]
            series_b = returns[sym_b]
            if len(series_a) != len(series_b) or not series_a:
                corr = 0.0
            else:
                mean_a = sum(series_a) / len(series_a)
                mean_b = sum(series_b) / len(series_b)
                cov = sum((a - mean_a) * (b - mean_b) for a, b in zip(series_a, series_b))
                var_a = sum((a - mean_a) ** 2 for a in series_a)
                var_b = sum((b - mean_b) ** 2 for b in series_b)
                denom = (var_a * var_b) ** 0.5
                corr = cov / denom if denom else 0.0
            matrix[sym_a][sym_b] = corr
            matrix[sym_b][sym_a] = corr
    return matrix
