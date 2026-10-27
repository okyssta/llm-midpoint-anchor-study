"""Recompute every paired cell with the corrected Newcombe method 10, and audit the interaction.

Outputs
  results/v5_corrected.json      every cell: table, proportions, interval, McNemar, verdict
  results/per_item_indicators.csv  one row per item per condition: four correctness flags
  results/interaction_audit.json   explicit per-item interaction terms and permutation detail
"""
import csv, itertools, json, math, os, random
from collections import defaultdict

from stats_paired import newcombe_paired, mcnemar_exact

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW, RES = os.path.join(ROOT, "raw"), os.path.join(ROOT, "results")
MARGIN = 0.15


def jl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def table_of(f, b):
    ids = sorted(set(f) & set(b))
    n11 = sum(1 for i in ids if f[i] and b[i])
    n12 = sum(1 for i in ids if b[i] and not f[i])   # backward only
    n21 = sum(1 for i in ids if f[i] and not b[i])   # forward only
    n22 = len(ids) - n11 - n12 - n21
    return ids, (n11, n12, n21, n22)


def classify(n11, n12, n21, n22, lo, hi):
    n = n11 + n12 + n21 + n22
    fwd = (n11 + n21) / n
    if fwd < 0.15:
        return "no headroom"
    if hi < -MARGIN:
        return "reduction, margin cleared"
    if hi < 0:
        return "reduction, margin not cleared"
    if lo > 0:
        return "backward higher"
    return "no reduction detected"


def main():
    mid = jl(os.path.join(RAW, "midpoint.jsonl"))
    pairs = jl(os.path.join(RAW, "paired_scan.jsonl"))

    o = defaultdict(lambda: {"fwd": {}, "bwd": {}})
    for r in mid:
        o[(r["model"], r["L"], r["seed"], r["para"], r["mode"])][r["dir"]][r["item_id"]] = r["correct"]

    cells = []
    for key in sorted(o):
        model, L, seed, para, mode = key
        c = o[key]
        if not c["fwd"] or not c["bwd"]:
            continue
        ids, (n11, n12, n21, n22) = table_of(c["fwd"], c["bwd"])
        lo, hi = newcombe_paired(n11, n12, n21, n22)
        n = len(ids)
        cells.append(dict(model=model, L=L, seed=seed, para=para, mode=mode, n=n,
                          table=[[n11, n12], [n21, n22]],
                          fwd=(n11 + n21) / n, bwd=(n11 + n12) / n,
                          delta=(n11 + n12) / n - (n11 + n21) / n,
                          lo=lo, hi=hi, p=mcnemar_exact(n12, n21),
                          verdict=classify(n11, n12, n21, n22, lo, hi)))

    # original seeded cell lives in paired_scan (seed 71, forced choice)
    f = {r["item_id"]: r["correct"] for r in pairs if r["L"] == 9 and r["i"] == 5 and r["dir"] == "fwd"}
    b = {r["item_id"]: r["correct"] for r in pairs if r["L"] == 9 and r["i"] == 5 and r["dir"] == "bwd"}
    ids, tab = table_of(f, b)
    lo, hi = newcombe_paired(*tab)
    orig = dict(model="qwen15", L=9, seed=71, para="baseline", mode="forced", n=len(ids),
                table=[[tab[0], tab[1]], [tab[2], tab[3]]], fwd=sum(f.values()) / len(ids),
                bwd=sum(b.values()) / len(ids), delta=(tab[0] + tab[1]) / len(ids) - (tab[0] + tab[2]) / len(ids),
                lo=lo, hi=hi, p=mcnemar_exact(tab[1], tab[2]), verdict=classify(*tab, lo, hi))
    cells.append(orig)

    # per-item indicators for independent reanalysis
    with open(os.path.join(RES, "per_item_indicators.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["model", "L", "seed", "wording", "mode", "item_id", "forward_correct", "backward_correct"])
        for (model, L, seed, para, mode), c in sorted(o.items()):
            for i in sorted(set(c["fwd"]) & set(c["bwd"])):
                w.writerow([model, L, seed, para, mode, i, int(c["fwd"][i]), int(c["bwd"][i])])

    # interaction, defined per item and checked against the reported estimate
    A = o[("qwen15", 9, 101, "baseline", "forced")]
    B = o[("qwen15", 9, 101, "word_ordinal", "forced")]
    ids = sorted(set(A["fwd"]) & set(A["bwd"]) & set(B["fwd"]) & set(B["bwd"]))
    terms = []
    for i in ids:
        eA = A["bwd"][i] - A["fwd"][i]
        eB = B["bwd"][i] - B["fwd"][i]
        terms.append(dict(item_id=i, fwd_base=int(A["fwd"][i]), bwd_base=int(A["bwd"][i]),
                          fwd_para=int(B["fwd"][i]), bwd_para=int(B["bwd"][i]),
                          eff_base=eA, eff_para=eB, interaction=eA - eB))
    obs = sum(t["interaction"] for t in terms) / len(terms)

    # Exact enumeration: zeros leave the statistic unchanged, so only the nonzero terms are
    # sign-permuted. 12 nonzero terms -> 2**12 = 4096 assignments, small enough to enumerate.
    nz = [t["interaction"] for t in terms if t["interaction"] != 0]
    obs_sum = abs(sum(t["interaction"] for t in terms))
    extreme = 0
    for signs in itertools.product((1, -1), repeat=len(nz)):
        if abs(sum(s * t for s, t in zip(signs, nz))) >= obs_sum - 1e-12:
            extreme += 1
    total_perms = 2 ** len(nz)
    p_exact = extreme / total_perms

    rng = random.Random(0)
    n_boot, n_perm = 10000, 100000
    boots = sorted(sum(rng.choice(terms)["interaction"] for _ in terms) / len(terms)
                   for _ in range(n_boot))
    ge = 0
    for _ in range(n_perm):
        tot = 0
        for t in terms:
            eA, eB = t["eff_base"], t["eff_para"]
            if rng.random() < 0.5:
                eA, eB = eB, eA
            tot += eA - eB
        if abs(tot / len(terms)) >= abs(obs):
            ge += 1
    p_perm = (ge + 1) / (n_perm + 1)          # plus-one correction, Monte Carlo cross-check

    inter = dict(definition="(bwd_base - fwd_base) - (bwd_para - fwd_para), per item",
                 n=len(terms), estimate=obs,
                 lo=boots[int(0.025 * n_boot)], hi=boots[int(0.975 * n_boot)],
                 n_boot=n_boot, n_perm=n_perm, seed=0,
                 p_exact=p_exact, exact_extreme=extreme, exact_assignments=total_perms,
                 n_nonzero=len(nz), p_perm=p_perm, ge=ge,
                 eff_base=sum(t["eff_base"] for t in terms) / len(terms),
                 eff_para=sum(t["eff_para"] for t in terms) / len(terms),
                 terms=terms)

    json.dump(dict(margin=MARGIN, alpha=0.05, cells=cells), open(os.path.join(RES, "v5_corrected.json"), "w"), indent=1)
    json.dump(inter, open(os.path.join(RES, "interaction_audit.json"), "w"), indent=1)

    print(f"{'model':8s} {'L':>2s} {'seed':>4s} {'wording':13s} {'mode':8s} {'table':16s} {'Δpp':>6s} {'95% CI':>16s} {'p':>8s}  verdict")
    for c in sorted(cells, key=lambda c: (c["model"], c["L"], c["seed"], c["para"], c["mode"])):
        t = c["table"]
        print(f"{c['model']:8s} {c['L']:2d} {c['seed']:4d} {c['para']:13s} {c['mode']:8s} "
              f"[[{t[0][0]},{t[0][1]}],[{t[1][0]},{t[1][1]}]]".ljust(0)
              + f" {100*c['delta']:+6.1f} [{100*c['lo']:+6.1f},{100*c['hi']:+6.1f}] {c['p']:8.5f}  {c['verdict']}")
    print(f"\ninteraction {100*obs:+.4f} pp  95% CI [{100*inter['lo']:+.2f},{100*inter['hi']:+.2f}]")
    print(f"  exact two-sided p = {extreme}/{total_perms} = {p_exact!r}  ({len(nz)} nonzero terms)")
    print(f"  Monte Carlo cross-check: {ge} exceedances / {n_perm}, plus-one p = {p_perm:.8f}")
    print(f"effect baseline {100*inter['eff_base']:+.2f}  paraphrase {100*inter['eff_para']:+.2f}")


if __name__ == "__main__":
    main()
