"""The midpoint condition, replicated. One cell per invocation.

Condition: odd length L, middle position i=(L+1)/2, both anchor labels naming the SAME
ordinal and addressing the SAME item on the SAME list:
    forward  : "What item is at the {i}-th position from the beginning?"
    backward : "What item is at the {i}-th position from the end?"
Everything except the anchor word is identical, so any paired difference is a direction
effect with ordinal magnitude held fixed.

Modes:
  forced   one forward pass, argmax over the bare-letter ids (validated scorer)
  generate greedy decoding, up to 6 tokens, first in-list letter parsed from the output

Every row records model, L, i, seed, paraphrase, mode, item, gold, prediction and correctness.
"""
import argparse, json, os, re
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from task import make_items, LETTERS

torch.set_num_threads(2)
ORD = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th", 6: "6th", 7: "7th", 8: "8th", 9: "9th"}
WORD = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth", 6: "sixth",
        7: "seventh", 8: "eighth", 9: "ninth"}


def question(i, direction, para):
    anchor = "beginning" if direction == "fwd" else "end"
    if para == "baseline":
        return f"What item is at the {ORD[i]} position from the {anchor}?"
    if para == "word_ordinal":
        return f"Which item is {WORD[i]} from the {anchor}?"
    if para == "counting":
        return f"Counting from the {anchor}, which item is number {i}?"
    raise ValueError(para)


def build(items, i, direction, para):
    return (f"Items: {', '.join(items)}\nQuestion: {question(i, direction, para)}\n"
            f"Answer with the letter only.\nAnswer:")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen2.5-1.5B-Instruct")
    ap.add_argument("--tag", default="qwen15")
    ap.add_argument("--L", type=int, default=9)
    ap.add_argument("--seed", type=int, default=101)
    ap.add_argument("--para", default="baseline")
    ap.add_argument("--mode", default="forced", choices=["forced", "generate"])
    ap.add_argument("--items", type=int, default=24)
    ap.add_argument("--out", default=None,
                    help="JSONL destination; defaults to <repo>/raw/midpoint.jsonl")
    args = ap.parse_args()
    if args.out is None:
        args.out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "raw", "midpoint.jsonl")

    i = (args.L + 1) // 2
    tok = AutoTokenizer.from_pretrained(args.model)
    tok.pad_token = tok.eos_token
    tok.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(args.model, dtype=torch.float32,
                                                 low_cpu_mem_usage=True).eval()
    lid = {c: tok.encode(c, add_special_tokens=False)[0] for c in LETTERS}

    fout = open(args.out, "a")
    for direction in ("fwd", "bwd"):
        texts, metas = [], []
        for j in range(args.items):
            items = make_items(args.L, args.seed, j)
            texts.append(build(items, i, direction, args.para))
            metas.append((j, items, items[i - 1]))
        prompts = [tok.apply_chat_template(
            [{"role": "system", "content": "You answer with a single letter."},
             {"role": "user", "content": t}], tokenize=False, add_generation_prompt=True)
            for t in texts]
        enc = tok(prompts, return_tensors="pt", padding=True)
        with torch.inference_mode():
            if args.mode == "forced":
                lp = torch.log_softmax(model(**enc).logits[:, -1, :].float(), -1)
                preds = []
                for row, (_, items, _g) in zip(lp, metas):
                    sc = {c: float(row[lid[c]]) for c in items}
                    preds.append(max(sc, key=sc.get))
            else:
                out = model.generate(**enc, max_new_tokens=6, do_sample=False,
                                     pad_token_id=tok.pad_token_id)
                texts_out = tok.batch_decode(out[:, enc["input_ids"].shape[1]:], skip_special_tokens=True)
                preds = []
                for raw, (_, items, _g) in zip(texts_out, metas):
                    m = re.search(r"[A-T]", raw)
                    preds.append(m.group(0) if m else None)
        for (j, items, gold), pred, raw in zip(metas, preds, ["-"] * len(preds)):
            fout.write(json.dumps(dict(
                model=args.tag, L=args.L, i=i, seed=args.seed, para=args.para, mode=args.mode,
                dir=direction, item_id=j, items="".join(items), gold=gold, pred=pred,
                correct=int(pred == gold))) + "\n")
        fout.flush()
        print(f"[{args.tag} L={args.L} i={i} seed={args.seed} {args.para} {args.mode} {direction}] done", flush=True)
    fout.close()


if __name__ == "__main__":
    main()
