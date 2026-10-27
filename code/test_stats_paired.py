"""Regression tests for the paired-interval routine, the exact permutation test, and the
non-default confidence levels.

Reference values: statsmodels.stats.proportion.confint_proportions_paired (main branch), whose own
docstring is verified against R ratesci::moverpairci and PropCIs. The 95% case is pinned to that
docstring exactly; the 90% and 99% cases are pinned to values computed from the published formula
with stdlib normal quantiles, and are additionally checked for nesting.

Run: python3 test_stats_paired.py   (exits nonzero if any check fails)
"""
import itertools
import json
import os
import sys
from statistics import NormalDist

from stats_paired import newcombe_paired, mcnemar_exact, z_for_alpha

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(os.path.dirname(HERE), "results")

METHOD10 = [
    ([[10, 5], [2, 20]], -0.0643926050711, 0.2211160178958, "statsmodels reference example"),
    ([[4, 0], [8, 12]], -0.5123, -0.1156, "original midpoint lists"),
    ([[4, 0], [9, 11]], -0.5523, -0.1484, "fresh midpoint lists"),
    ([[0, 0], [24, 0]], -1.0, -0.8049, "forward always correct, backward always wrong"),
]

ALPHA_REF = {
    0.10: (-0.041837249706366125, 0.200085172825556),
    0.05: (-0.06439260507116959, 0.22111601789582339),
    0.01: (-0.10668894700591058, 0.2599315956899507),
}


def approx(a, b, tol):
    return abs(a - b) <= tol


def check(cond, msg):
    print(f"{'PASS' if cond else 'FAIL'}  {msg}")
    return cond


def test_reference_cases():
    ok = True
    for tab, lo_exp, hi_exp, label in METHOD10:
        tol = 1e-9 if "reference example" in label else 1e-3
        lo, hi = newcombe_paired(*tab[0], *tab[1])
        ok &= check(approx(lo, lo_exp, tol) and approx(hi, hi_exp, tol),
                    f"{label}: [{lo:+.6f},{hi:+.6f}] expected [{lo_exp:+.6f},{hi_exp:+.6f}]")
    return ok


def test_normal_quantiles():
    """The bug this replaces: _norm_isf(0.005) returned a negative value."""
    ok = True
    for alpha, expected in [(0.10, 1.6448536269514722), (0.05, 1.959963984540054),
                            (0.01, 2.5758293035489004)]:
        z = z_for_alpha(alpha)
        ok &= check(approx(z, expected, 1e-9) and z > 0,
                    f"z(alpha={alpha}) = {z!r} expected {expected!r}")
    ok &= check(approx(NormalDist().inv_cdf(0.995), 2.5758293035489004, 1e-9),
                "NormalDist().inv_cdf(0.995) is +2.5758 (the case that used to return negative)")
    return ok


def test_confidence_levels():
    ok = True
    for alpha, (lo_exp, hi_exp) in sorted(ALPHA_REF.items()):
        lo, hi = newcombe_paired(10, 5, 2, 20, alpha=alpha)
        ok &= check(approx(lo, lo_exp, 1e-10) and approx(hi, hi_exp, 1e-10),
                    f"{100*(1-alpha):.0f}% interval [{lo:+.12f},{hi:+.12f}] expected "
                    f"[{lo_exp:+.12f},{hi_exp:+.12f}]")
    lo90, hi90 = newcombe_paired(10, 5, 2, 20, alpha=0.10)
    lo95, hi95 = newcombe_paired(10, 5, 2, 20, alpha=0.05)
    lo99, hi99 = newcombe_paired(10, 5, 2, 20, alpha=0.01)
    ok &= check(lo99 < lo95 < lo90 < hi90 < hi95 < hi99, "90% interval nested inside 95% inside 99%")
    return ok


def test_symmetry():
    lo, hi = newcombe_paired(10, 5, 2, 20)
    lo2, hi2 = newcombe_paired(10, 2, 5, 20)     # transpose: swap the classifications
    return check(approx(lo2, -hi, 1e-9) and approx(hi2, -lo, 1e-9),
                 f"transpose symmetry: [{lo2:+.9f},{hi2:+.9f}] vs [{-hi:+.9f},{-lo:+.9f}]")


def test_identical_and_boundary():
    ok = True
    for tab, label in [((12, 0, 0, 12), "identical margins"), ((0, 0, 0, 24), "all wrong"),
                       ((24, 0, 0, 0), "all right")]:
        lo, hi = newcombe_paired(*tab)
        ok &= check(approx(lo, -hi, 1e-9) and hi > 0.01,
                    f"{label}: symmetric, non-degenerate [{lo:+.6f},{hi:+.6f}]")
    lo, hi = newcombe_paired(0, 0, 24, 0)
    ok &= check(approx(lo, -1.0, 1e-12) and approx(hi, -0.804872, 1e-5),
                f"perfect discordance: [{lo:+.6f},{hi:+.6f}] (not [0,0], not [-1,-1])")
    return ok


def test_mcnemar():
    ok = True
    for b, c, exp in [(0, 8, 0.0078125), (0, 9, 0.00390625), (3, 3, 1.0), (2, 6, 0.2890625)]:
        got = mcnemar_exact(b, c)
        ok &= check(approx(got, exp, 1e-12), f"McNemar {b}/{c}: {got:.7f} expected {exp:.7f}")
    return ok


def test_margin_classification():
    """Full precision decides the verdict; -14.84 must not be rounded to -15."""
    ok = True
    for tab, label in [((4, 0, 8, 12), "original midpoint"), ((4, 0, 9, 11), "fresh midpoint")]:
        lo, hi = newcombe_paired(*tab)
        ok &= check(-0.15 < hi < 0, f"{label}: upper {100*hi:.4f}pp below 0, above -15pp margin")
    return ok


def exact_permutation_p(terms):
    """Enumerate all sign assignments of the nonzero terms; zeros leave the statistic unchanged."""
    nz = [t for t in terms if t != 0]
    obs = abs(sum(terms))
    extreme = 0
    for signs in itertools.product((1, -1), repeat=len(nz)):
        if abs(sum(s * t for s, t in zip(signs, nz))) >= obs - 1e-12:
            extreme += 1
    return extreme, 2 ** len(nz), extreme / 2 ** len(nz)


def test_exact_permutation():
    ok = True
    synthetic = [0] * 12 + [-1] * 11 + [-2]
    extreme, total, p = exact_permutation_p(synthetic)
    ok &= check(total == 4096 and extreme == 2 and approx(p, 0.00048828125, 1e-15),
                f"synthetic 12 zeros / 11 x -1 / 1 x -2: {extreme}/{total} -> p = {p!r}")

    path = os.path.join(RESULTS, "interaction_audit.json")
    if os.path.exists(path):
        terms = [t["interaction"] for t in json.load(open(path))["terms"]]
        e, n, p = exact_permutation_p(terms)
        ok &= check(n == 4096 and e == 2 and approx(p, 0.00048828125, 1e-15),
                    f"stored interaction terms: {e}/{n} -> p = {p!r}")
        ok &= check(sum(terms) == -13, f"stored terms sum to {sum(terms)} (expected -13)")
    return ok


def main():
    tests = [test_reference_cases(), test_normal_quantiles(), test_confidence_levels(),
             test_symmetry(), test_identical_and_boundary(), test_mcnemar(),
             test_margin_classification(), test_exact_permutation()]
    print("\nALL PASS" if all(tests) else "\nSOME FAILED")
    return 0 if all(tests) else 1


if __name__ == "__main__":
    sys.exit(main())
