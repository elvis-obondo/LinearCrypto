from log_returns import get_price_levels
from statsmodels.tsa.stattools import coint
import itertools
import numpy as np
import pandas as pd


def find_most_cointegrated_pair(top_n=10):
    df = get_price_levels()
    tickers = df.columns.tolist()
    results = []

    pairs = list(itertools.combinations(tickers, 2))
    print(f"Testing {len(pairs)} pairs...")

    for a, b in pairs:
        _, pvalue, _ = coint(df[a], df[b])
        results.append((a, b, pvalue))

    results_df = pd.DataFrame(results, columns=["ticker_a", "ticker_b", "p_value"])
    results_df = results_df.sort_values("p_value").reset_index(drop=True)

    print(f"\nTop {top_n} most cointegrated pairs:")
    print(results_df.head(top_n).to_string(index=False))

    best = results_df.iloc[0]
    print(f"\nBest pair: {best.ticker_a} & {best.ticker_b}  (p={best.p_value:.4f})")
    return results_df, df[[best.ticker_a, best.ticker_b]], best.ticker_a, best.ticker_b




# My attempt of recreating the cointegration code
def find_coint(top_n =10):
    df = get_price_levels()
    tickers = df.columns.tolist()
    results = []

    pairs = list(itertools.combinations(tickers,2))

    for a,b in pairs:
        _, p_value, _= coint(df[a],df[b])
        results.append((df[a],df[b],p_value))

    results_df = pd.DataFrame(results,columns=["ticker_a","ticker_b","p_value"])
    results_df=results_df.sort_values("p_value").reset_index(drop=True)
    best = results_df.iloc[0]
   
    return results_df, df[[best.ticker_a,best.ticker_b]], best.ticker_a,best.ticker_b


if __name__ == "__main__":
    find_most_cointegrated_pair()


