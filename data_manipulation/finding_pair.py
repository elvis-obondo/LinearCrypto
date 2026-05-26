from log_returns import get_market_data
import numpy as np
import pandas as pd


def find_most_correlated_pair():
    df = get_market_data()

    corr_matrix = df.corr()

    # Mask the diagonal so a ticker doesn't match itself
    np.fill_diagonal(corr_matrix.values, np.nan)

    # Finds the pair with the highest correlation
    max_corr_val = corr_matrix.stack().max()
    ticker_a, ticker_b = corr_matrix.stack().idxmax()

    print(f"Most correlated pair: {ticker_a} & {ticker_b} (correlation: {max_corr_val:.4f})")

    return df[[ticker_a, ticker_b]], ticker_a, ticker_b, max_corr_val


if __name__ == "__main__":
    pair_returns, ticker_a, ticker_b, corr = find_most_correlated_pair()
    print(pair_returns.head())
