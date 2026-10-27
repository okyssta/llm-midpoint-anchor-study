"""Validate the published results against a fresh recomputation from the saved predictions.

This does NOT rerun any model. It copies the repository to a temporary directory, runs the
documented analysis pipeline there (recompute_v5.py, assemble_v6.py), and compares the regenerated
numbers with the committed ones. Floats are compared with an absolute tolerance of 1e-9: the pipeline
is deterministic, but libm and interpreter differences can move the last bits without changing any
result (see docs/REPRODUCIBILITY.md).

Exit status is nonzero on any mismatch. The committed files are never written.
"""
import filecmp
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOL = 1e-9
EXACT_P = 2 / 4096


def copy_repo(dst):
    ignore = shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.html")
    shutil.copytree(ROOT, dst, ignore=ignore)


def run(cmd, cwd):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-3000:])
        print(r.stderr[-3000:])
        raise SystemExit(f"command failed: {' '.join(cmd)}")
    return r.stdout


def compare(a, b, path="", worst=[0.0], errors=[]):
    """Recursive compare; ints/strings exact, floats within TOL."""
    if type(a) is not type(b) and not (isinstance(a, (int, float)) and isinstance(b, (int, float))):
        errors.append(f"{path}: type {type(a).__name__} vs {type(b).__name__}")
        return
    if isinstance(a, dict):
        if set(a) != set(b):
            errors.append(f"{path}: key sets differ ({sorted(set(a) ^ set(b))[:5]})")
            return
        for k in a:
            compare(a[k], b[k], f"{path}.{k}", worst, errors)
    elif isinstance(a, list):
        if len(a) != len(b):
            errors.append(f"{path}: length {len(a)} vs {len(b)}")
            return
        for i, (x, y) in enumerate(zip(a, b)):
            compare(x, y, f"{path}[{i}]", worst, errors)
    elif isinstance(a, bool) or isinstance(a, str) or a is None:
        if a != b:
            errors.append(f"{path}: {a!r} vs {b!r}")
    elif isinstance(a, (int, float)):
        d = abs(float(a) - float(b))
        worst[0] = max(worst[0], d)
        if d > TOL:
            errors.append(f"{path}: {a!r} vs {b!r} (|d|={d:.3e})")
    else:
        if a != b:
            errors.append(f"{path}: {a!r} vs {b!r}")


def main():
    worst = [0.0]
    errors = []
    with tempfile.TemporaryDirectory() as tmp:
        work = os.path.join(tmp, "repo")
        copy_repo(work)
        run([sys.executable, "code/recompute_v5.py"], work)
        run([sys.executable, "code/assemble_v6.py"], work)

        for rel in ("results/v5_corrected.json", "results/interaction_audit.json"):
            committed = json.load(open(os.path.join(ROOT, rel)))
            regenerated = json.load(open(os.path.join(work, rel)))
            compare(committed, regenerated, rel, worst, errors)

        csv_committed = os.path.join(ROOT, "results", "per_item_indicators.csv")
        csv_regen = os.path.join(work, "results", "per_item_indicators.csv")
        if not filecmp.cmp(csv_committed, csv_regen, shallow=False):
            errors.append("results/per_item_indicators.csv: byte comparison differs")

        md_committed = os.path.join(ROOT, "paper", "anchor_word_v6.md")
        md_regen = os.path.join(work, "paper", "anchor_word_v6.md")
        if not filecmp.cmp(md_committed, md_regen, shallow=False):
            errors.append("paper/anchor_word_v6.md: assembled text differs from the committed source")

        exact = json.load(open(os.path.join(work, "results", "interaction_audit.json")))["p_exact"]
        if abs(exact - EXACT_P) > 1e-15:
            errors.append(f"interaction p_exact: {exact!r} != 2/4096")

    if errors:
        print("FAILED — regenerated results differ from the committed records:")
        for e in errors[:40]:
            print("  -", e)
        print(f"\n{len(errors)} mismatch(es); worst float deviation {worst[0]:.3e}")
        return 1

    print("PASS — regenerated results match the committed records")
    print(f"  tolerance        {TOL:.0e}")
    print(f"  worst deviation  {worst[0]:.3e}")
    print(f"  interaction p    2/4096 = {EXACT_P!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
