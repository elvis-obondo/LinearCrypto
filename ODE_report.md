# Crypto Pairs Trading: ODE System Development Report

---

## Why are we using log prices?

When it comes to financial data we are tracking the movement of price across time.

The natural way to think about it is the difference in raw price at different particular points in time.

For example: Coin A goes from $10 to $20. Coin B goes from $100 to $110. Same price movement of $10 but way different economic significance. Coin A sees a 100% price increase and Coin B only sees a 10% price increase. On paper it looks like the same $10 price move.

Therefore the next idea is to use percentage change — that will surely fix our problems!

Carrying over from the previous examples. Let's say Coin A's price movements are: $10 → $20 → $15 and Coin B's movements are: $100 → $110 → $105. The percentage changes would be:

```
Coin A : +100% → −25%
Coin B : +10%  → −5%
```

What is the total percentage change?
```
Coin A : 100% + (−25%) = 75% ?
Coin B : 10%  + (−5%)  = 5%  ?
```

What is the actual percentage change?
```
Coin A : 2 × 0.75 = 1.5   → 50% increase
Coin B : 1.1 × 0.9545 = 1.04995  → ~5% increase
```

Percentage change is multiplicative. This is a pain when the data moves from 3 time periods to millions of time periods across different coins and assets.

However we have a fix. What is multiplication if not repeated addition? What math object treats multiplication as addition? Exponentials.

```
ln(a) + ln(b) = ln(a·b)    ← multiplication becomes addition
e^(ln(a·b)) = a·b          ← exponentiate to get back the price ratio
```

Carrying over from the previous examples:
```
Coin A : ln(20/10) + ln(15/20) = ln(1.5) ≈ 0.405  →  e^0.405 = 1.5  (50% gain) ✓
Coin B : ln(110/100) + ln(105/110) ≈ 0.049         →  e^0.049 = 1.05 (5% gain)  ✓
```

We can take the log of the price ratio directly at each step — no need to compute percentage change first. Log returns are additive, scale-independent, and map cleanly to the ODE framework where we work with rates of change.

---

## How do we find the right pair?

### What each metric is truly asking

**Pearson** asks: is there a constant linear rate of change between these two assets?

This means that when Coin A moves 3%, Coin B moves 5% each and every time. It assumes a constant linear proportional relationship, which we know is not the case with financial markets.

**Spearman** asks: if Coin A had a big day relative to its history, did Coin B also have a big day relative to its history?

The exact magnitude of the move is irrelevant. The focus is strictly on the ordering and ranking. Did they have unusually good days together and unusually bad days together too?

### Why this matters

Consider a calm market: Coin A may move 0.8% and Coin B may move 1%.  
Consider a bull market: Coin A may move 20% and Coin B may move 30%.  
Consider a bear market: Coin A may crash 30% and Coin B may crash 45%.

Spearman still sees the correlation in direction and timing — not necessarily magnitude. Pearson struggles because there is no clear linear relationship and it tries to give a single value that accurately describes the average of all regimes. Big swings in the market contribute significantly more to the Pearson correlation than they should.

Another way to think about it: Pearson is best suited for normally distributed data (bell curve). Spearman is best suited for Student-t distributed data, which has fat tails — meaning outliers are far more likely than a normal distribution predicts. This is typical of financial data, especially crypto.

Pearson squares the deviations. A crash day that is 10 times larger than a normal day gets 100 times the weight in the calculation. One extreme candle can overpower hundreds of normal days of data.

### Why not use Spearman then — it seems obvious?

Not quite. It depends on the type of ODE we use. A linear ODE assumes linear relationships between the two coins, so we need a correlation method that checks for linear relationships that the ODE can accurately model.

The rigorous approach is to plot dS/dt vs S for every possible pair and observe the shape. A straight line pushes toward Pearson and a linear ODE. A curve pushes toward Spearman and a nonlinear ODE. Given project time constraints we proceed with Pearson and a linear ODE.

---

## The Original ODE System

We model each coin as being pulled toward the other at a rate proportional to the spread between them, with coupling constant k derived from their Pearson correlation:

```
dX/dt = −k·(X − Y)
dY/dt = −k·(Y − X)
```

X and Y are cumulative log prices. When X is above Y, X is pulled downward. When Y is below X, Y is pulled upward. Both coins converge toward each other at rate k.

The spread S = X − Y satisfies:

```
dS/dt = −2k·S
```

---

## Solving the ODE System

### Eigenvalue method

Write the system as a matrix equation dy/dt = A·y:

```
A = [[-k,  k],
     [ k, -k]]
```

Find the eigenvalues of A — the values λ where det(A − λI) = 0. For this matrix the eigenvalues are λ₁ = 0 and λ₂ = −2k.

The general solution is:

```
y(t) = c₁·e^(λ₁t)·v₁  +  c₂·e^(λ₂t)·v₂
```

where v₁ and v₂ are the corresponding eigenvectors. Plugging in the initial conditions [X₀, Y₀] solves for c₁ and c₂, giving a closed-form expression evaluable at any time t.

### RK45 method

RK45 is a numerical step-by-step solver. Euler's method uses one slope measurement at the start of each step to predict the next position — fast but inaccurate on curves. RK45 takes four slope measurements per step:

```
k₁ = f(tₙ, yₙ)                       ← slope at start
k₂ = f(tₙ + h/2, yₙ + h·k₁/2)       ← midpoint slope using k₁
k₃ = f(tₙ + h/2, yₙ + h·k₂/2)       ← midpoint slope using k₂
k₄ = f(tₙ + h,   yₙ + h·k₃)         ← end slope using k₃

yₙ₊₁ = yₙ + h·(k₁ + 2k₂ + 2k₃ + k₄) / 6
```

The midpoint measurements get double weight because they describe the solution more accurately than the endpoints. RK45 also adapts its step size h automatically — smaller steps where the curve is complex, larger steps where it is smooth.

---

## Why the Model Failed

The spread equation dS/dt = −2k·S has only one solution: S(t) = S₀·e^(−2kt). The spread decays monotonically to zero and never crosses back. But the actual spread oscillates up and down around a stable level — the model was structurally incapable of capturing this behaviour.

What was missing: a **market factor**. Real spreads are pushed around by external forces — macro events, order flow, market-wide momentum — that temporarily drive the spread away from its equilibrium before mean-reversion pulls it back. The interplay between this external forcing and mean-reversion is what produces oscillation.

---

## The Expanded ODE System

Instead of tracking X and Y separately we compress the system to track their spread S = X − Y directly. We introduce a market factor M representing the external momentum acting on the spread, and define μ as the spread's natural equilibrium level:

```
dS/dt = −κ·(S − μ) + M
dM/dt = −ω²·(S − μ)
```

Where:
- S is the spread between the two coins' cumulative log prices
- μ is the spread's natural equilibrium level (observed from data)
- κ is the mean-reversion rate — how fast the spread is pulled back toward μ
- M is the market factor — external momentum currently acting on the spread
- ω is the oscillation frequency — how strongly the spread displacement drives M

### Why is this a harmonic oscillator?

Defining S\* = S − μ (deviation from equilibrium) and eliminating M algebraically gives:

```
d²S*/dt²  +  κ·dS*/dt  +  ω²·S*  =  0
```

This is the standard damped harmonic oscillator. κ is the damping (mean-reversion pulling the spread back), ω is the spring stiffness (how hard the spread displacement pushes back on M), and S\* is the displacement from equilibrium. When ω > κ/2, the eigenvalues are complex and the spread oscillates while decaying.

### Why undamped?

The full damped form adds a −γ·M term: market momentum fades on its own at rate γ. We chose γ = 0 (undamped) — the market factor's lifetime is already naturally limited by the ω²·S\* restoring force. Adding γ would introduce a third parameter to estimate from limited data.

### How are κ and ω estimated?

Both are estimated jointly by fitting the second-order ODE directly to the observed spread:

```
d²S*/dt²  =  −κ·(dS*/dt)  −  ω²·S*
```

This is a two-predictor linear regression where d²S*/dt² is the target and [dS*/dt, S\*] are the predictors. Estimating them jointly prevents the sequential problem where fitting κ first removes all signal from S\*, leaving nothing for ω² to detect.

---

## Conclusion

The system as built captures the structural idea correctly — a mean-reverting spread driven by an oscillatory market factor. However the 7-day hourly window proved insufficient to reliably identify the oscillation frequency. Parameter estimation from second finite differences amplifies noise, and for this pair and time window the system remained in the overdamped regime (ω < κ/2).

The natural next step is a **stochastic differential equation** (SDE):

```
dS* = (−κ·S* + M) dt  +  σ dW
dM  =  −ω²·S* dt
```

Where σ dW is a Wiener process — the mathematical way to inject randomness. This would capture the jagged, noisy trajectory seen in the phase portrait. The deterministic harmonic oscillator provides the underlying structure; the stochastic term fills in the noise that real markets produce.