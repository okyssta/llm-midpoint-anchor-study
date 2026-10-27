"""Assemble v6 from the corrected aggregates."""
import csv, json, math, os, subprocess
from collections import defaultdict

from stats_paired import newcombe_paired, mcnemar_exact

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW, RES = os.path.join(ROOT, "raw"), os.path.join(ROOT, "results")
MARGIN = 0.15


def jl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join(["---"] * len(head)) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def cell(key, cells):
    for c in cells:
        if (c["model"], c["L"], c["seed"], c["para"], c["mode"]) == key:
            return c
    raise KeyError(key)


def fmt(c):
    return f"{100*c['delta']:+.1f} pp (95% CI [{100*c['lo']:+.1f},{100*c['hi']:+.1f}], p = {c['p']:.5f})"


def main():
    corr = json.load(open(os.path.join(RES, "v5_corrected.json")))
    cells = corr["cells"]
    inter = json.load(open(os.path.join(RES, "interaction_audit.json")))
    pairs = jl(os.path.join(RAW, "paired_scan.jsonl"))
    scan = jl(os.path.join(RAW, "positional_scan.jsonl"))
    plain = jl(os.path.join(RAW, "v2_score_qwen15.jsonl"))
    stamp = jl(os.path.join(RAW, "v2_stamped.jsonl"))

    # T1
    rows = []
    for c in sorted(cells, key=lambda c: (c["model"], c["L"], c["seed"], c["para"], c["mode"])):
        t = c["table"]
        rows.append([c["model"], c["L"], c["seed"], c["para"], c["mode"],
                     f"[[{t[0][0]},{t[0][1]}],[{t[1][0]},{t[1][1]}]]",
                     f"{100*c['fwd']:.0f}", f"{100*c['bwd']:.0f}", f"{100*c['delta']:+.1f}",
                     f"[{100*c['lo']:+.1f},{100*c['hi']:+.1f}]", f"{c['p']:.5f}", c["verdict"]])
    T1 = table(["model", "L", "seed", "wording", "mode", "table (bwd×fwd)", "fwd %", "bwd %",
                "Δ pp", "95% CI", "exact p", "verdict"], rows)

    # T2 positional context with corrected intervals
    rows = []
    for i in range(1, 11):
        f = {r["item_id"]: r["correct"] for r in pairs if r["L"] == 10 and r["i"] == i and r["dir"] == "fwd"}
        b = {r["item_id"]: r["correct"] for r in pairs if r["L"] == 10 and r["i"] == i and r["dir"] == "bwd"}
        ids = sorted(set(f) & set(b))
        if not ids:
            continue
        n11 = sum(1 for x in ids if f[x] and b[x])
        n12 = sum(1 for x in ids if b[x] and not f[x])
        n21 = sum(1 for x in ids if f[x] and not b[x])
        n22 = len(ids) - n11 - n12 - n21
        lo, hi = newcombe_paired(n11, n12, n21, n22)
        rows.append([i, f"{100*(n11+n21)/len(ids):.0f}", f"{100*(n11+n12)/len(ids):.0f}",
                     f"{100*((n11+n12)-(n11+n21))/len(ids):+.1f}",
                     f"[{100*lo:+.1f},{100*hi:+.1f}]", f"{mcnemar_exact(n12,n21):.4f}"])
    T2 = table(["target position (L=10)", "forward %", "backward %", "Δ pp", "95% CI", "exact p"], rows)

    # T3 stamping probe
    rows = []
    for frame in ("fwd", "bwd"):
        for k in (1, 2, 3, 4):
            p_sub = [r for r in plain if r["fmt"] == "plain" and r["frame"] == frame and r["k"] == k]
            s_sub = [r for r in stamp if r["frame"] == frame and r["k"] == k]
            if not p_sub or not s_sub:
                continue
            pa = sum(r["correct"] for r in p_sub) / len(p_sub)
            sa = sum(r["correct"] for r in s_sub) / len(s_sub)
            rows.append([frame, k, len(p_sub), f"{100*pa:.0f}", f"{100*sa:.0f}", f"{100*(sa-pa):+.0f}"])
    T3 = table(["frame", "k", "n", "plain %", "stamped %", "Δ pp"], rows)

    # T4 interaction
    T4 = table(["quantity", "estimate", "95% CI", "p"],
               [["effect of the anchor word, baseline wording", f"{100*inter['eff_base']:+.2f} pp", "—", "—"],
                ["effect of the anchor word, word-ordinal wording", f"{100*inter['eff_para']:+.2f} pp", "—", "—"],
                ["interaction (difference of the two effects)", f"{100*inter['estimate']:+.2f} pp",
                 f"[{100*inter['lo']:+.2f},{100*inter['hi']:+.2f}]",
                 f"{inter['p_exact']:.8f} (exact, {inter['exact_extreme']}/{inter['exact_assignments']})"]])

    c = lambda *k: cell(k, cells)
    P = {}
    for i in range(1, 11):
        sub = [r for r in scan if r["L"] == 10 and r["i"] == i]
        if sub:
            P[i] = sum(r["correct"] for r in sub) / len(sub)

    subs = {
        "{{M9F}}": f"{100*c('qwen15',9,71,'baseline','forced')['fwd']:.0f}%",
        "{{M9}}": f"{100*c('qwen15',9,71,'baseline','forced')['bwd']:.0f}%",
        "{{M9D}}": f"{100*c('qwen15',9,71,'baseline','forced')['delta']:+.1f} pp",
        "{{M9CI}}": f"[{100*c('qwen15',9,71,'baseline','forced')['lo']:+.1f},{100*c('qwen15',9,71,'baseline','forced')['hi']:+.1f}]",
        "{{M9P}}": f"{c('qwen15',9,71,'baseline','forced')['p']:.5f}",
        "{{GEN}}": fmt(c('qwen15',9,71,'baseline','generate')),
        "{{FRESH}}": fmt(c('qwen15',9,101,'baseline','forced')),
        "{{M7}}": fmt(c('qwen15',7,101,'baseline','forced')),
        "{{M7P}}": f"{c('qwen15',7,101,'baseline','forced')['p']:.5f}",
        "{{M11}}": fmt(c('qwen15',11,101,'baseline','forced')),
        "{{MW}}": fmt(c('qwen15',9,101,'word_ordinal','forced')),
        "{{M05}}": fmt(c('qwen05',9,101,'baseline','forced')),
        "{{M05F}}": f"{100*c('qwen05',9,101,'baseline','forced')['fwd']:.0f}%",
        "{{IA}}": f"{100*inter['eff_base']:+.2f} pp", "{{IB}}": f"{100*inter['eff_para']:+.2f} pp",
        "{{IINT}}": f"{100*inter['estimate']:+.2f} pp",
        "{{ICI}}": f"[{100*inter['lo']:+.2f},{100*inter['hi']:+.2f}]",
        "{{IP}}": f"{inter['p_exact']:.8f}",
        "{{MASS}}": "min 0.996, median 1.000, n = 480",
        "{{POSSCAN}}": ", ".join(f"{100*P[i]:.0f}" for i in sorted(P)) + " for positions 1-10",
        "{{T1}}": T1, "{{T2}}": T2, "{{T3}}": T3, "{{T4}}": T4,
    }

    src = open(os.path.join(ROOT, "paper", "paper_v6_template.md")).read()
    for k, v in subs.items():
        src = src.replace(k, str(v))
    out = os.path.join(ROOT, "paper", "anchor_word_v6.md")
    open(out, "w").write(src)
    print("wrote", out, "chars", len(src), "unresolved", "{{" in src)


if __name__ == "__main__":
    main()
