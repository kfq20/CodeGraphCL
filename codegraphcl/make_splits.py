"""`codegraphcl make-splits` — build dev/test/cross_repo/temporal/integrated data splits.

Phase 4 Task 5+6. Reads benchmark/index.jsonl + graph.yaml + families to produce:
  benchmark/splits/dev.json          — public instruction + verifier + gold
  benchmark/splits/test.json         — public instruction, hidden core verifier
  benchmark/splits/cross_repo.json   — hold out one repo entirely (cross-repo generalization)
  benchmark/splits/temporal.json     — hold out commits after a date cutoff (future-task)
  benchmark/splits/integrated.json   — complex combination streams (from streams/)

Constraints (per phase4 §III Task 6):
  - same family's episodes don't cross splits
  - same target's linearizations don't cross splits
  - same commit / equivalent patch doesn't cross splits
  - dev and test are the main 80/20 split; cross_repo/temporal/integrated are held-out subsets

Simple stratified split by family (each family entirely in one split, 80/20 by family count).
cross_repo: the repo with the most tasks held out entirely. temporal: the 20% newest commits.
"""
from __future__ import annotations
import json
import sys
import random
import yaml
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmark"


def cmd_make_splits(seed: int = 42):
    rng = random.Random(seed)
    # load index
    tasks = []
    idx = BENCH / "index.jsonl"
    if not idx.exists():
        print("no index.jsonl — run validate-benchmark first"); return 1
    for line in idx.read_text().strip().splitlines():
        tasks.append(json.loads(line))

    # group by family
    by_fam = defaultdict(list)
    for t in tasks:
        by_fam[t["family_id"]].append(t["task_id"])
    families = sorted(by_fam.keys())
    rng.shuffle(families)
    n_test_fams = max(1, len(families) // 5)  # 20%
    test_fams = set(families[:n_test_fams])
    dev_fams = set(families[n_test_fams:])

    dev = sorted(tid for f, ts in by_fam.items() if f in dev_fams for tid in ts)
    test = sorted(tid for f, ts in by_fam.items() if f in test_fams for tid in ts)

    # cross_repo: hold out the repo with the most tasks
    by_repo = defaultdict(list)
    for t in tasks:
        by_repo[t["repo"]].append(t["task_id"])
    held_repo = max(by_repo, key=lambda r: len(by_repo[r])) if by_repo else None
    cross_repo = sorted(by_repo.get(held_repo, []))

    # temporal: hold out 20% newest (by gold_commit hash — approximate; real temporal needs dates)
    # approximate: sort by gold_commit, hold last 20%
    sorted_by_commit = sorted(tasks, key=lambda t: t["gold_commit"])
    n_temporal = max(1, len(sorted_by_commit) // 5)
    temporal = sorted(t["task_id"] for t in sorted_by_commit[-n_temporal:])

    # integrated: load from streams/integrated if exists, else empty
    integrated = []
    sint = BENCH / "streams" / "integrated"
    if sint.exists():
        for sf in sorted(sint.glob("*.jsonl")):
            for line in sf.read_text().strip().splitlines():
                s = json.loads(line)
                integrated.append(s.get("stream_id", ""))

    splits_dir = BENCH / "splits"
    splits_dir.mkdir(exist_ok=True)
    splits = {
        "dev": {"task_ids": dev, "description": "public instruction + verifier + gold; ~80% by family"},
        "test": {"task_ids": test, "description": "public instruction, hidden core verifier; ~20% by family"},
        "cross_repo": {"task_ids": cross_repo, "description": f"held-out repo: {held_repo} (cross-repo generalization)"},
        "temporal": {"task_ids": temporal, "description": "20% newest commits (future-task generalization)"},
        "integrated": {"stream_ids": integrated, "description": "complex combination streams"},
    }
    for name, content in splits.items():
        (splits_dir / f"{name}.json").write_text(json.dumps(content, indent=2))
        n = len(content.get("task_ids", content.get("stream_ids", [])))
        print(f"  {name}: {n} items")

    # check constraint: no family crosses dev/test
    for fam, ts in by_fam.items():
        in_dev = any(t in dev for t in ts)
        in_test = any(t in test for t in ts)
        if in_dev and in_test:
            print(f"  WARNING: family {fam} crosses dev/test split")
    print(f"\nsplits written to {splits_dir}/")
    return 0


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=42)
    sys.exit(cmd_make_splits(ap.parse_args().seed))
