"""`codegraphcl summarize <run_dir>` — aggregate an intervention run's results.csv.

Reads runs/<run_dir>/results.csv, computes per-condition pass-rate + mean cost, and writes a
SUMMARY.md next to the CSV (so the prose summary always reflects the actual raw data — fixes
the N=1 SUMMARY <-> raw CSV path mismatch where hand-written summaries drifted from the CSV).

Usage:
  python3 -m codegraphcl summarize runs/intervene_ripgrep_c3_to_c4_seed42_1786611149
"""
from __future__ import annotations
import csv
import sys
from collections import defaultdict
from pathlib import Path


def cmd_summarize(run_dir: str) -> int:
    rd = Path(run_dir)
    csv_path = rd / "results.csv"
    if not csv_path.exists():
        print(f"no results.csv in {rd}")
        return 1

    rows = list(csv.DictReader(csv_path.open()))
    if not rows:
        print("results.csv is empty (header only) — no episodes completed")
        (rd / "SUMMARY.md").write_text(f"# {rd.name}\n\nNo episodes completed.\n")
        return 0

    n = len(rows)
    # per-condition aggregate
    by_cond = defaultdict(list)
    for r in rows:
        by_cond[r["condition"]].append(r)

    lines = [f"# summarize — {rd.name}", "",
             f"Source CSV: `{csv_path}` (the authoritative raw data for this summary).",
             f"Episodes: {n}  ({len(by_cond)} conditions: {', '.join(sorted(by_cond))})", "",
             "| condition | solved/N | reward-series | mean turns | mean elapsed | mean out_tok |",
             "|---|---|---|---|---|---|"]
    # canonical order; unknown conditions appended
    order = [c for c in ("reset", "correct", "irrelevant", "wrong", "stale") if c in by_cond]
    order += [c for c in sorted(by_cond) if c not in order]
    for c in order:
        rs = by_cond[c]
        solved = sum(int(r["reward"]) for r in rs if r["reward"] in ("0", "1"))
        series = "[" + ",".join(r["reward"] for r in rs) + "]"
        def _mean(key):
            vs = [int(r[key]) for r in rs if r.get(key) and r[key] != "NA"]
            return f"{sum(vs)/len(vs):.0f}" if vs else "NA"
        lines.append(f"| {c} | {solved}/{len(rs)} | {series} | {_mean('assistant_turns')} | "
                     f"{_mean('elapsed_sec')}s | {_mean('output_tokens')} |")

    # infra fails
    infra = [r for r in rows if r["outcome"] == "infra_fail"]
    if infra:
        lines.append("")
        lines.append(f"**infra_fail episodes: {len(infra)}** "
                     f"({', '.join(r['episode_id']+':'+r['condition'] for r in infra)}) — reward "
                     "not written; exclude from pass-rate stats or treat as failure per study design.")

    summary = "\n".join(lines) + "\n"
    out_path = rd / "SUMMARY.md"
    out_path.write_text(summary)
    print(summary)
    print(f"\nwrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(cmd_summarize(sys.argv[1] if len(sys.argv) > 1 else ""))
