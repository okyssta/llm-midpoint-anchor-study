"""Newcombe method 10 for paired proportions, matching statsmodels' reference implementation.

Reference: statsmodels.stats.proportion.confint_proportions_paired (main branch), itself
verified against R's ratesci::moverpairci and PropCIs. The two features our earlier version
missed:

  * the phi coefficient uses Newcombe's n/2 adjustment of a POSITIVE covariance term:
        cov = n11*n22 - n12*n21
        if cov > 0: cov = max(cov - n/2, 0)
        phi = cov / sqrt((n11+n12)(n21+n22)(n11+n21)(n12+n22))
  * phi is defined as 0 when any marginal total is zero.

Table convention: rows are the first classification (backward), columns the second (forward),
success in row 1 / column 1. So n11 = both correct, n12 = backward-only, n21 = forward-only,
n22 = neither, and the interval is for p_backward - p_forward.
"""
import math
from statistics import NormalDist

Z = NormalDist().inv_cdf(0.975)


def z_for_alpha(alpha=0.05):
    """Two-sided normal quantile. stdlib NormalDist, so no hand-rolled approximation."""
    return NormalDist().inv_cdf(1 - alpha / 2.0)


def wilson(k, n, z=Z):
    """Wilson score interval without continuity correction (statsmodels' default)."""
    if n == 0:
        return 0.0, 1.0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def newcombe_paired(n11, n12, n21, n22, alpha=0.05):
    """Newcombe's method 10 interval for p1 - p2 on a paired 2x2 table."""
    z = z_for_alpha(alpha)
    n = n11 + n12 + n21 + n22
    if n <= 0:
        raise ValueError("empty table")
    p1 = (n11 + n12) / n
    p2 = (n11 + n21) / n
    diff = p1 - p2

    l1, u1 = wilson(n11 + n12, n, z)
    l2, u2 = wilson(n11 + n21, n, z)

    marg_prod = (n11 + n12) * (n21 + n22) * (n11 + n21) * (n12 + n22)
    if marg_prod == 0:
        phi = 0.0
    else:
        cov = n11 * n22 - n12 * n21
        if cov > 0:
            cov = max(cov - n / 2.0, 0.0)
        phi = cov / math.sqrt(marg_prod)

    dl, du = p1 - l1, u2 - p2
    low = diff - math.sqrt(max(0.0, dl * dl - 2 * phi * dl * du + du * du))
    dl, du = u1 - p1, p2 - l2
    upp = diff + math.sqrt(max(0.0, dl * dl - 2 * phi * dl * du + du * du))
    return low, upp


def mcnemar_exact(n12, n21):
    """Exact two-sided McNemar p for discordant counts."""
    n = n12 + n21
    if n == 0:
        return 1.0
    k = min(n12, n21)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)
