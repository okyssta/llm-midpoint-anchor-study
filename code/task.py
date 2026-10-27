"""Task generator for the position-retrieval study.

The unit of control is the RENDERED sequence: every prompt is (shown order,
surface frame), and the gold item is computed from those two, never from an
abstract "direction" that the renderer might have silently changed.

    shown, frame = render(items, k, direction, fmt)
    gold, idx    = gold_of(shown, k, frame, fmt)

Equivalence pairs used in the paper:
    (plain, begin)  ==  (revlist, end)     -> target p_k
    (plain, end)    ==  (revlist, begin)   -> target p_{L-k+1}
A "same question, reversed buffer" rewrite is the second member of each pair.
"""
import random

LETTERS = list("JKLMNOPQRST")  # letters whose alphabet index (10-20) never collides with an
                              # offset 1-4: with A-D in the pool, "3rd" made the model answer "C".

# fmt -> (reverse the printed list, flip the surface frame)
VIEW = {
    "plain":    (False, False),
    "revlist":  (True,  False),   # reversed buffer, same wording
    "revframe": (False, True),    # same buffer, opposite wording
    "revboth":  (True,  True),    # reversed buffer + opposite wording
    "stamped":  (False, False),
    "len":      (False, False),
    "digit":    (False, False),
    "backwards": (False, False),
    "endmark":  (False, False),
    "lastitem": (False, False),
}


def ordinal(k: int) -> str:
    return {1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th"}[k]


def make_items(L: int, seed: int, item_id: int):
    rng = random.Random((seed * 1_000_003) ^ (L * 7919) ^ (item_id * 104_729))
    items = LETTERS[:L]
    rng.shuffle(items)
    return items


def render(items, k, direction, fmt):
    """Return (shown_items, frame) where frame is the anchor the wording names."""
    rev, flip = VIEW[fmt]
    shown = list(reversed(items)) if rev else list(items)
    frame = direction
    if flip:
        frame = "bwd" if direction == "fwd" else "fwd"
    return shown, frame


def gold_of(shown, k, frame, fmt="plain"):
    """Index of the answer inside the shown sequence."""
    L = len(shown)
    if fmt == "lastitem":
        return (L - 1) if frame == "bwd" else 0
    return (k - 1) if frame == "fwd" else (L - k)


def truths(items, k, direction, fmt="plain"):
    """(shown, gold, mirror, neighbours) in the rendered frame.

    `mirror` is the answer to the same offset measured from the *other* anchor
    in the same rendering: the anchor-confusion prediction.
    """
    shown, frame = render(items, k, direction, fmt)
    idx = gold_of(shown, k, frame, fmt)
    gold = shown[idx]
    midx = (len(shown) - 1 - idx)
    mirror = shown[midx]
    neigh = [shown[j] for j in (idx - 1, idx + 1) if 0 <= j < len(shown)]
    return shown, gold, mirror, neigh


def build_prompt(items, k, direction, fmt="plain"):
    L = len(items)
    shown, frame = render(items, k, direction, fmt)
    anchor = "beginning" if frame == "fwd" else "end"
    q = f"What item is at the {ordinal(k)} position from the {anchor}?"
    joined = ", ".join(shown)
    if fmt in ("plain", "revlist", "revframe", "revboth"):
        body = f"Items: {joined}\n"
    elif fmt == "len":
        body = f"The list contains {L} items.\nItems: {joined}\n"
    elif fmt == "stamped":
        body = "Items: " + ", ".join(f"[{i+1}] {x}" for i, x in enumerate(shown)) + "\n"
    elif fmt == "endmark":
        body = f"Items: {joined} END\n"
    elif fmt == "digit":
        q = f"What item is at position {k} counting from the {anchor}?"
        body = f"Items: {joined}\n"
    elif fmt == "backwards":
        q = (f"Counting backwards from the last item as 1, which item is number {k}?"
             if frame == "bwd" else
             f"Counting forwards from the first item as 1, which item is number {k}?")
        body = f"Items: {joined}\n"
    elif fmt == "lastitem":
        q = ("Which item is last in the list?" if frame == "bwd"
             else "Which item is first in the list?")
        body = f"Items: {joined}\n"
    else:
        raise ValueError(fmt)
    return body + "Question: " + q + "\nAnswer with the letter only.\nAnswer:"


def parse_answer(text, items):
    allowed = set(items)
    for ch in text.strip():
        c = ch.upper()
        if c in allowed:
            return c
    return None
