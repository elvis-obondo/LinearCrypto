import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from log_returns import get_price_levels
from statsmodels.tsa.stattools import coint
import itertools
import numpy as np
import pandas as pd


def compute_spread(price_a: np.ndarray, price_b: np.ndarray):
    beta, alpha = np.polyfit(price_b, price_a, 1)
    spread = price_a - alpha - beta * price_b
    return spread, beta


def half_life(spread: np.ndarray) -> float:
    S = np.asarray(spread, dtype=float)
    lam, _ = np.polyfit(S[:-1], np.diff(S), 1)
    if lam >= 0:
        return np.inf
    return -np.log(2) / lam  # hours


def hurst_exponent(spread: np.ndarray) -> float:
    S = np.asarray(spread, dtype=float)
    lags = [2, 4, 8, 16, 32, 64, 128]
    variances = [np.var(S[lag:] - S[:-lag]) for lag in lags]
    slope, _ = np.polyfit(np.log(lags), np.log(variances), 1)
    return slope / 2


def rolling_coint(price_a: np.ndarray, price_b: np.ndarray, window: int = 2016, stride: int = 24) -> pd.Series:
    pvalues = []
    for i in range(0, len(price_a) - window, stride):
        _, pval, _ = coint(price_a[i:i + window], price_b[i:i + window])
        pvalues.append(pval)
    return pd.Series(pvalues)


def rolling_hedge_ratio(price_a: np.ndarray, price_b: np.ndarray, window: int = 720) -> pd.Series:
    betas = []
    for i in range(len(price_a) - window):
        beta, _ = np.polyfit(price_b[i:i + window], price_a[i:i + window], 1)
        betas.append(beta)
    return pd.Series(betas)


def analyze_top_pairs(top_n: int = 10, window: int = 2016):
    print("Fetching price data...")
    df = get_price_levels()
    tickers = df.columns.tolist()

    pairs = list(itertools.combinations(tickers, 2))
    print(f"Running cointegration scan on {len(pairs)} pairs...")
    coint_results = []
    for a, b in pairs:
        _, pval, _ = coint(df[a].values, df[b].values)
        coint_results.append((a, b, pval))

    coint_df = (
        pd.DataFrame(coint_results, columns=["ticker_a", "ticker_b", "p_value"])
        .sort_values("p_value")
        .head(top_n)
        .reset_index(drop=True)
    )

    print(f"\nRunning diagnostics on top {top_n} pairs (rolling window = {window} bars = {window // 24}d)...")
    rows = []
    for i, row in coint_df.iterrows():
        a, b, pval = row.ticker_a, row.ticker_b, row.p_value
        print(f"  [{i + 1}/{top_n}] {a}/{b}")
        pa, pb = df[a].values, df[b].values

        spread, _ = compute_spread(pa, pb)
        hl_hours = half_life(spread)
        H = hurst_exponent(spread)

        roll_beta = rolling_hedge_ratio(pa, pb, window)
        beta_mean = roll_beta.mean()
        beta_std = roll_beta.std()
        beta_cv = beta_std / abs(beta_mean) if beta_mean != 0 else np.inf

        roll_p = rolling_coint(pa, pb, window)
        coint_stability = (roll_p < 0.05).mean()  # fraction of windows that are cointegrated

        rows.append({
            "ticker_a": a,
            "ticker_b": b,
            "p_value": round(pval, 4),
            "half_life_days": round(hl_hours / 24, 1) if np.isfinite(hl_hours) else np.inf,
            "hurst": round(H, 3),
            "coint_stability": round(coint_stability, 2),
            "beta_mean": round(beta_mean, 3),
            "beta_cv": round(beta_cv, 3),
        })

    summary = pd.DataFrame(rows)

    print("\n--- Pair Diagnostics ---")
    print(summary.to_string(index=False))

    tradeable = summary[
        (summary["half_life_days"].between(1, 30)) &
        (summary["hurst"] < 0.5) &
        (summary["coint_stability"] >= 0.5) &
        (summary["beta_cv"] < 0.1)
    ]
    print()
    if not tradeable.empty:
        print("Tradeable candidates (1-30d half-life, H<0.5, stable coint, β_cv<0.1):")
        print(tradeable[["ticker_a", "ticker_b", "half_life_days", "hurst", "coint_stability", "beta_cv"]].to_string(index=False))
    else:
        print("No pairs pass all tradeable filters.")

    return summary


if __name__ == "__main__":
    analyze_top_pairs()
