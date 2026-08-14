"""`codegraphcl atom-lengths <task_dir> [atoms_file]` — check the Phase 3.1 length-control.

Prints per-atom char count and token count (tiktoken if available, else char count) and asserts
the length-match controls for the carrier ablation:
  - short pair: |correct_short - irrelevant_short| / mean <= 5%
  - long pair:  |correct_long  - irrelevant_long|  / mean <= 5%

Also reports the cross-pair ratios so a reviewer can see if correct is longer than irrelevant
(the Phase 3 confound).

Usage:
  python3 -m codegraphcl atom-lengths benchmark/tasks/fastify_decorator_getter atoms_ablation.md
"""
from __future__ import annotations
import re
import sys
from pathlib import Path


def _tokens(text: str) -> int:
    try:
        import tiktoken
        return len(tiktoken.get_encoding("cl100k_base").encode(text))
    except Exception:
        return len(text)


def main(task_dir: str, atoms_file: str = "atoms.md") -> int:
    td = Path(task_dir)
    atoms_path = td / atoms_file
    if not atoms_path.exists():
        print(f"no {atoms_file} in {td}")
        return 1
    t = atoms_path.read_text()
    names = ["correct_short", "irrelevant_short", "correct_long", "irrelevant_long",
             "correct", "wrong", "irrelevant"]
    found = {}
    for n in names:
        m = re.search(rf"<!-- ATOM:{n} -->(.*?)<!-- /ATOM:{n} -->", t, re.S)
        if m:
            body = m.group(1).strip()
            found[n] = (len(body), _tokens(body))
    print(f"{atoms_file} ({task_dir}):")
    for n, (ch, tk) in found.items():
        print(f"  {n:20s}: {ch:5d} chars  {tk:5d} tokens")
    # ablation pairs
    def _ratio(a, b):
        if a not in found or b not in found:
            return None
        ca, ta = found[a]; cb, tb = found[b]
        mean = (ta + cb) / 2 or 1
        return abs(ta - tb) / mean
    short_r = _ratio("correct_short", "irrelevant_short")
    long_r = _ratio("correct_long", "irrelevant_long")
    print()
    if short_r is not None:
        ok = "PASS" if short_r <= 0.05 else "FAIL"
        print(f"  short pair  correct_short vs irrelevant_short: token diff {short_r:.1%}  [{ok} <= 5%]")
    if long_r is not None:
        ok = "PASS" if long_r <= 0.05 else "FAIL"
        print(f"  long pair   correct_long  vs irrelevant_long : token diff {long_r:.1%}  [{ok} <= 5%]")
    # also flag the legacy confound
    if "correct" in found and "irrelevant" in found:
        print(f"  legacy      correct({found['correct'][1]}) vs irrelevant({found['irrelevant'][1]}): "
              f"correct is {found['correct'][1]/max(found['irrelevant'][1],1):.2f}x irrelevant")
    bad = [r for r in (short_r, long_r) if r is not None and r > 0.05]
    return 1 if bad else 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print("usage: atom-lengths <task_dir> [atoms_file]")
        sys.exit(2)
    sys.exit(main(args[0], args[1] if len(args) > 1 else "atoms.md"))
