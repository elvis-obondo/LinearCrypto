from finding_pair import find_most_correlated_pair
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

WEEK_STEPS = 7 * 24  # 1-hour candles
MU = 0.05            # spread equilibrium level


def load_data():
    pair_returns, ticker_a, ticker_b, k = find_most_correlated_pair()
    week_levels = pair_returns.cumsum().iloc[-WEEK_STEPS:]
    actual_spread = week_levels[ticker_a].to_numpy() - week_levels[ticker_b].to_numpy()
    return week_levels, ticker_a, ticker_b, k, actual_spread


def estimate_parameters(actual_spread):
    S_star = actual_spread - MU   # centre around equilibrium
    dS     = np.diff(S_star)      # dS*/dt  (same as diff of actual since MU is constant)
    d2S    = np.diff(dS)

    # Joint fit of d²S*/dt² = -κ·(dS*/dt) - ω²·S* — both parameters at once
    # X      = np.column_stack([-dS[:-1], -S_star[1:-1]])
    # params, _, _, _ = np.linalg.lstsq(X, d2S, rcond=None)
    # kappa  = max(float(params[0]), 0.0)
    # omega2 = max(float(params[1]), 0.0)
    # omega  = np.sqrt(omega2)
    kappa  = 0.05   # hardcoded: slow mean-reversion
    omega  = 0.20   # hardcoded: satisfies ω > κ/2, ~31hr oscillation period
    omega2 = omega ** 2

    S0    = S_star[0]                        # initial condition in S* space
    M_est = dS + kappa * S_star[:-1]         # M = dS*/dt + κ·S*
    M0    = float(M_est[0])

    return kappa, omega, omega2, S0, M0, M_est


def ode_system(kappa, omega2):
    def system(_t, y):
        S, M = y
        return [-kappa * S + M, -omega2 * S]
    return system


def solve_numerically(kappa, omega2, S0, M0, T):
    t_span = (0, T - 1)
    t_eval = np.arange(T, dtype=float)
    sol = solve_ivp(ode_system(kappa, omega2), t_span, [S0, M0],
                    t_eval=t_eval, method='RK45')
    return sol, t_eval


def solve_analytically(kappa, omega2, S0, M0, t_eval):
    A = np.array([[-kappa, 1.0],
                  [-omega2, 0.0]])
    eigenvalues, eigenvectors = np.linalg.eig(A)
    c = np.linalg.solve(eigenvectors, np.array([S0, M0]))

    analytical_SM = sum(
        (c[i] * np.exp(eigenvalues[i] * t_eval) * eigenvectors[:, i:i+1]).real
        for i in range(2)
    )
    return analytical_SM, eigenvalues


def plot_results(ticker_a, ticker_b, kappa, omega, actual_spread, M_est,
                 sol, t_eval, analytical_SM):
    _, axes = plt.subplots(2, 1, figsize=(12, 10))

    # --- Top: spread comparison ---
    axes[0].plot(actual_spread, label="Actual spread", alpha=0.7)
    axes[0].plot(sol.t, sol.y[0] + MU, label="RK45", linestyle="--")
    axes[0].plot(t_eval, analytical_SM[0] + MU, label="Eigenvalue solution", linestyle=":", linewidth=2)
    axes[0].axhline(0, color="black", linewidth=0.8, linestyle=":")
    axes[0].set_title(f"Spread: {ticker_a} - {ticker_b}  |  κ={kappa:.4f}  ω={omega:.4f}  (last 7 days)")
    axes[0].set_xlabel("1-hour candle")
    axes[0].set_ylabel("Cumulative log return (spread)")
    axes[0].legend()

    # --- Bottom: phase portrait in (S, M) space ---
    
    S_grid = np.linspace(actual_spread.min(), actual_spread.max(), 16)
    M_grid = np.linspace(M_est.min(), M_est.max(), 16)
    Sg, Mg  = np.meshgrid(S_grid, M_grid)
    dSg     = -kappa * Sg + Mg
    dMg     = -omega**2 * Sg
    speed   = np.sqrt(dSg**2 + dMg**2) + 1e-10

    axes[1].quiver(Sg, Mg, dSg / speed, dMg / speed,
                   speed, cmap="coolwarm", alpha=0.5)
    axes[1].plot(actual_spread[:-1], M_est,
                 color="steelblue", alpha=0.4, linewidth=0.8, label="Actual trajectory")
    axes[1].plot(sol.y[0], sol.y[1],
                 color="orange", linewidth=1.5, linestyle="--", label="RK45 trajectory")
    axes[1].scatter([actual_spread[0]], [M_est[0]], color="green", zorder=5, label="Initial condition")
    axes[1].axhline(0, color="black", linewidth=0.5)
    axes[1].axvline(0, color="black", linewidth=0.5)
    axes[1].set_xlabel("S  (spread)")
    axes[1].set_ylabel("M  (market factor)")
    axes[1].set_title("Phase portrait: (S, M) space  —  spiral = oscillation")
    axes[1].legend()

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    week_levels, ticker_a, ticker_b, k, actual_spread = load_data()
    kappa, omega, omega2, S0, M0, M_est = estimate_parameters(actual_spread)

    sol, t_eval       = solve_numerically(kappa, omega2, S0, M0, len(week_levels))
    analytical_SM, eigenvalues = solve_analytically(kappa, omega2, S0, M0, t_eval)

    print(f"Pair: {ticker_a} & {ticker_b} | κ = {kappa:.4f} | ω = {omega:.4f} | S0 = {S0:.6f}")
    print(f"Oscillating: {omega > kappa / 2}")
    print(f"Eigenvalues: {eigenvalues}")

    plot_results(ticker_a, ticker_b, kappa, omega, actual_spread, M_est,
                 sol, t_eval, analytical_SM)
