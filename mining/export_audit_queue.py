"""Export a human-readable audit queue: for each motif-grade segment, sample ~5 representative
commits (time-stratified + deprecation-keyword priority) and render a markdown checklist
with the git command to read each one. This is the bridge from metadata recon → semantic
hand-audit (L1-L2 → L3).

Output: mining/out/AUDIT_QUEUE.md  (one section per segment, grouped by repo)
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from repo_config import REPOS  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "mining" / "out"
REPOS_DIR = ROOT / "repos"

SAMPLE_PER_SEGMENT = 5
DEP_WORDS = ("deprecat", "remov", "migrat", "refactor", "renam", "replac", "drop", "stale", "break", "fix")


def _git_show_subject_body(repo: str, sha: str, n_lines: int = 6) -> str:
    """First N lines of commit body (without diff) for the auditor to skim."""
    try:
        r = subprocess.run(
            ["git", "-C", str(REPOS_DIR / repo), "show", "--no-patch",
             f"--format=%s%n%n%b%n--- files ---%n", sha],
            capture_output=True, text=True, timeout=15,
        )
        body = r.stdout.strip()
        # truncate
        lines = body.splitlines()
        return "\n".join(lines[:n_lines])
    except Exception as e:
        return f"(git show failed: {e})"


def sample_commits(seg: dict) -> list[dict]:
    """Time-stratified sample of SAMPLE_PER_SEGMENT commits; prefer deprecation-keyword ones."""
    shas = seg["shas"]
    subjects = seg["subjects"]
    pairs = list(zip(shas, subjects))
    if len(pairs) <= SAMPLE_PER_SEGMENT:
        return [{"sha": s, "subject": sub} for s, sub in pairs]
    # stratified: pick indices evenly across the time-sorted list, but bias toward dep-word hits
    dep_idx = [i for i, (_, sub) in enumerate(pairs) if any(w in sub.lower() for w in DEP_WORDS)]
    chosen: set[int] = set()
    # even spacing
    step = len(pairs) / SAMPLE_PER_SEGMENT
    for k in range(SAMPLE_PER_SEGMENT):
        i = int(k * step)
        chosen.add(min(i, len(pairs) - 1))
    # fill remaining slots with deprecation hits (most motif-relevant for Update)
    for i in dep_idx:
        if len(chosen) >= SAMPLE_PER_SEGMENT:
            break
        chosen.add(i)
    # top up with earliest if still short
    i = 0
    while len(chosen) < SAMPLE_PER_SEGMENT and i < len(pairs):
        chosen.add(i); i += 1
    return [{"sha": pairs[i][0], "subject": pairs[i][1]} for i in sorted(chosen)]


def main() -> None:
    md = ["# CodeGraphCL — Audit Queue (R1 segments → hand-audit)\n",
          "> For each motif-grade segment below: read the sampled commits, decide if a real",
          "> project invariant recurs across them, and if so write an `experience` statement",
          "> + proposed edge type. This promotes a segment from L1-L2 (co-change) to L3",
          "> (semantically audited). Sections sorted repo → flagship-first → commit-count.\n",
          f"> Generated from `mining/out/*.segments.jsonl`. Sample = {SAMPLE_PER_SEGMENT} commits/segment.\n"]

    for name in REPOS:
        spec = REPOS[name]
        seg_path = OUT_DIR / f"{name}.segments.jsonl"
        if not seg_path.exists():
            continue
        segs = [json.loads(l) for l in seg_path.open() if l.strip()]
        grade = [s for s in segs if s["is_motif_grade"]]
        if not grade:
            continue
        # flagship (has FLAGSHIP in audit_hint) first, then by commit count
        grade.sort(key=lambda s: ("FLAGSHIP" not in s["audit_hint"], -s["n_commits"]))
        md.append(f"\n## {name}  ({spec.lang}) — {len(grade)} motif-grade segments\n")
        for s in grade:
            md.append(f"\n### [{s['parent_module']}] {s['n_commits']} commits, "
                      f"span {s['span_days']}d\n")
            md.append(f"- **core files:** {', '.join(s['core_files'][:5])}\n")
            md.append(f"- **hint:** {s['audit_hint']}\n")
            extra = f" …(+{len(s['files'])-8})" if len(s['files']) > 8 else ""
            md.append(f"- **all files touched:** {', '.join(s['files'][:8])}{extra}\n")
            md.append(f"- **first/last:** {s['first_date'][:10]} → {s['last_date'][:10]}\n")
            md.append("- **read these commits:**\n")
            for c in sample_commits(s):
                md.append(f"  - [ ] `{c['sha'][:10]}` {c['subject'][:80]}\n")
                md.append(f"        `git -C repos/{name} show {c['sha'][:12]} | head -60`\n")
    outp = OUT_DIR / "AUDIT_QUEUE.md"
    outp.write_text("".join(md))
    print(f"wrote {outp}")
    print(f"segments queued: {sum(1 for n in REPOS if (OUT_DIR/f'{n}.segments.jsonl').exists())} repos")


if __name__ == "__main__":
    main()
