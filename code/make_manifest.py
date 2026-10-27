"""Build and verify the package manifest.

SHA256SUMS lists every file in the package except itself (a manifest cannot contain its own hash).
The generator is hashed like any other file. Verification re-hashes each listed file and compares, so a stale manifest is caught
rather than trusted.

Usage:
    python3 make_manifest.py build     # write SHA256SUMS
    python3 make_manifest.py verify    # check every entry, exit nonzero on mismatch
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# The manifest covers the whole package, so it lives at the package root: if this script sits in
# code/, the root is its parent.
ROOT = os.path.dirname(HERE) if os.path.basename(HERE) == "code" else HERE
MANIFEST = os.path.join(ROOT, "SHA256SUMS")
# A manifest cannot list its own hash, so only SHA256SUMS is excluded. The generator itself is an
# ordinary delivered file and is hashed like any other.
EXCLUDE = {"SHA256SUMS"}


def files():
    out = []
    for root, dirs, names in os.walk(ROOT):
        dirs[:] = sorted(d for d in dirs if d not in {"__pycache__", ".git"})
        for n in sorted(names):
            rel = os.path.relpath(os.path.join(root, n), ROOT)
            # EXCLUDE holds bare file names; compare basenames, not relative paths.
            if os.path.basename(rel) in EXCLUDE or rel.endswith(".pyc"):
                continue
            out.append(rel)
    return sorted(out)


def digest(rel):
    h = hashlib.sha256()
    with open(os.path.join(ROOT, rel), "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build():
    lines = [f"{digest(rel)}  {rel}" for rel in files()]
    with open(MANIFEST, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"wrote {MANIFEST} with {len(lines)} entries")


def verify():
    listed, bad, missing = {}, [], []
    for line in open(MANIFEST):
        line = line.strip()
        if not line:
            continue
        h, rel = line.split("  ", 1)
        listed[rel] = h
    present = set(files())
    for rel, h in listed.items():
        if rel not in present:
            missing.append(rel)
        elif digest(rel) != h:
            bad.append(rel)
    extra = sorted(present - set(listed))
    for rel in missing:
        print(f"MISSING  {rel}")
    for rel in bad:
        print(f"MISMATCH {rel}")
    for rel in extra:
        print(f"UNLISTED {rel}")
    listed_names = {os.path.basename(k) for k in listed}
    ok = (not (missing or bad or extra)) and not (listed_names & EXCLUDE)
    print(f"\n{len(listed)} entries checked: {'OK' if ok else 'FAILED'}")
    return 0 if ok else 1


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "verify"
    sys.exit(build() if cmd == "build" else verify())
