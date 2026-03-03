import numpy as np
import matplotlib.pyplot as plt
from log_returns import get_market_data
from numpy.lib.stride_tricks import sliding_window_view

def calculate_synthetic_asset(window_size=100):
    # 1. Retrieve the log-returns for both assets
    sol_ret, kmno_ret = get_market_data()
    
    # 2. Define the weights from Eigen-Decomposition
    weights = np.array([-0.70710678, 0.70710678])
    
    # 3. Combine returns and calculate Spread Returns
    combined_rets = np.vstack([sol_ret, kmno_ret])
    spread_returns = weights @ combined_rets
    
    # 4. Calculate the Cumulative Spread (The "Synthetic Price")
    cumulative_spread = np.cumsum(spread_returns)
    
    # 5. Vectorized Rolling Z-Score
    windows = sliding_window_view(cumulative_spread, window_shape=window_size)
    rolling_mean = np.mean(windows, axis=1)
    rolling_std = np.std(windows, axis=1)
    
    # Align the spread values to the rolling window output
    current_values = cumulative_spread[window_size - 1:]
    
    # Calculate Z-Score
    z_scores = (current_values - rolling_mean) / (rolling_std + 1e-9)
    
    return cumulative_spread, z_scores, window_size

def plot_synthetic_asset(cumulative_spread, z_scores, window_size):
    # Align the spread data for plotting (it must match z_score length)
    aligned_spread = cumulative_spread[window_size - 1:]
    time_axis = np.arange(len(z_scores))

    # Create two subplots that share the same X-axis
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True, 
                                   gridspec_kw={'height_ratios': [2, 1]})

    # --- Top Plot: Cumulative Spread ---
    ax1.plot(time_axis, aligned_spread, color='royalblue', label='Synthetic Spread Price')
    ax1.set_title(f'Synthetic Asset Analysis (Window: {window_size})', fontsize=14)
    ax1.set_ylabel('Cumulative Log-Return')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper left')

    # --- Bottom Plot: Z-Score ---
    ax2.plot(time_axis, z_scores, color='black', linewidth=1, label='Z-Score')
    
    # Add horizontal threshold lines
    ax2.axhline(0, color='gray', linestyle='--')
    ax2.axhline(2.0, color='red', linestyle='--', alpha=0.5)
    ax2.axhline(-2.0, color='green', linestyle='--', alpha=0.5)

    # Shade the areas where the "Rubber Band" is stretched
    ax2.fill_between(time_axis, z_scores, 2.0, where=(z_scores >= 2.0), color='red', alpha=0.3)
    ax2.fill_between(time_axis, z_scores, -2.0, where=(z_scores <= -2.0), color='green', alpha=0.3)

    ax2.set_ylabel('Z-Score (Std Dev)')
    ax2.set_xlabel('Time Steps (5m Intervals)')
    ax2.set_ylim(-4, 4) # Focus on the relevant statistical range
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper left')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    cum_spread, z_scores, win_size = calculate_synthetic_asset(window_size=100)
    plot_synthetic_asset(cum_spread, z_scores, win_size)