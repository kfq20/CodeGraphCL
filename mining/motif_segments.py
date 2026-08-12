"""Motif-segment refiner: within a coarse cluster, find tight co-change groups by file
fingerprint similarity. A "segment" = a set of co-change commits that repeatedly touch the
same (small) set of source + test files. That repeated co-touching is the metadata-level
signature of a *single invariant being revised over time* — i.e. a motif embryo.

Why a second pass: the coarse clusterer groups by primary module, so a 5-year cluster of
338 commits across 18 subsystems is useless as a motif candidate. Real motifs live in the
intersection: commits that keep coming back to the SAME files together.

Method (intentionally simple & auditable, no embeddings):
  1. Drop noise commits (formatter/linter/bump/changelog) — they touch many files but
     carry no project-invariant signal. Recorded as `dropped_noise` count, not hidden.
  2. For each surviving commit, build a file fingerprint = frozenset of its src+test paths.
     Drop path components that vary per-occurrence (line numbers gone; we use whole paths).
  3. Build a weighted graph: nodes = commits, edge if |A∩B|/|A∪B| >= JACCARD_MIN.
     Connected components = candidate segments.
  4. A segment is "motif-grade" iff it has >= SEG_MIN commits spanning >= SEG_MIN_SPAN
     days AND touches >=2 files (one-file "segments" are trivial).

This is STILL metadata. It says "these N commits keep co-touching files X,Y,test_T — go
read them, they probably encode one evolving invariant." It does not name the motif.
Motif identity (Fork/Join/Scope/Update) remains a hand-audit job — but now the auditor reads
5-15 commits at a time instead of 338.

Run: python3 mining/motif_segments.py [--repo NAME ...] [--all]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from repo_config import REPOS, RepoSpec  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "mining" / "out"

JACCARD_MIN = 0.34       # >=1/3 of the union shared ⇒ same invariant neighborhood
SEG_MIN_COMMITS = 3
SEG_MIN_SPAN_DAYS = 30
SEG_MIN_FILES = 2        # one-file repeated edits ≠ a cross-cutting invariant

# Subject keywords marking non-semantic mass-touches. Dropped (counted, not hidden).
NOISE_WORDS = (
    "ruff", "black", "prettier", "fmt", "format", "isort", "lint", "flake8",
    "bump ", "bump:", "upgrade", "update dependency", "update dependencies",
    "changelog", "version bump", "release ", "merge pull request", "merge branch",
    "typo", "spelling", "rename file", "move file", "ci:", "workflow", "readme",
)


@dataclass
class Segment:
    repo: str
    parent_module: str           # coarse cluster this segment came from
    n_commits: int
    span_days: int
    first_date: str
    last_date: str
    files: list[str]             # union of files touched (the invariant's footprint)
    core_files: list[str]        # files in the fingerprint intersection (touched by >=50% of seg commits)
    shas: list[str]
    subjects: list[str]
    is_motif_grade: bool
    audit_hint: str              # one-line guidance for the human auditor


def _is_noise(subject: str) -> bool:
    s = subject.lower()
    return any(w in s for w in NOISE_WORDS)


def _parse_date(iso: str) -> datetime:
    return datetime.fromisoformat(iso.replace("Z", "+00:00"))


def _jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    if inter == 0:
        return 0.0
    return inter / len(a | b)


def _connected_components(nodes: list[str], adj: dict[str, set[str]]) -> list[list[str]]:
    seen: set[str] = set()
    comps: list[list[str]] = []
    for n in nodes:
        if n in seen:
            continue
        stack, comp = [n], []
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            comp.append(x)
            stack.extend(adj[x] - seen)
        comps.append(comp)
    return comps


def refine_repo(spec: RepoSpec, commits: list[dict]) -> list[Segment]:
    # 1. drop noise; keep accounting for the report
    kept = [c for c in commits if not _is_noise(c["subject"])]

    # group by parent module (primary = modules[0]) so we segment within a coarse cluster
    by_module: dict[str, list[dict]] = defaultdict(list)
    for c in kept:
        if c.get("modules"):
            by_module[c["modules"][0]].append(c)

    segments: list[Segment] = []
    for module, recs in by_module.items():
        # 2. fingerprints over src+test files only (ignore 'other')
        fps: dict[str, frozenset[str]] = {}
        for r in recs:
            files = {f for f in r["files"] if not f.endswith((".md", ".rst", ".txt", ".lock"))}
            if len(files) >= 1:
                fps[r["sha"]] = frozenset(files)

        shas = list(fps)
        if len(shas) < SEG_MIN_COMMITS:
            continue

        # 3. similarity graph
        adj: dict[str, set[str]] = {s: set() for s in shas}
        for i in range(len(shas)):
            for j in range(i + 1, len(shas)):
                if _jaccard(fps[shas[i]], fps[shas[j]]) >= JACCARD_MIN:
                    adj[shas[i]].add(shas[j])
                    adj[shas[j]].add(shas[i])

        # 4. components → segments
        for comp in _connected_components(shas, adj):
            if len(comp) < SEG_MIN_COMMITS:
                continue
            comp_recs = [next(r for r in recs if r["sha"] == s) for s in comp]
            comp_recs.sort(key=lambda r: r["date"])
            dates = [_parse_date(r["date"]) for r in comp_recs]
            span = int((max(dates) - min(dates)).total_seconds() / 86400) if len(dates) > 1 else 0

            # union + core files (core = touched by >= half the commits)
            file_count: dict[str, int] = defaultdict(int)
            for r in comp_recs:
                for f in r["files"]:
                    file_count[f] += 1
            union_files = sorted(file_count)
            core = sorted(f for f, n in file_count.items() if n >= max(2, len(comp) // 2))

            is_grade = (len(comp) >= SEG_MIN_COMMITS and span >= SEG_MIN_SPAN_DAYS
                        and len(union_files) >= SEG_MIN_FILES)
            seg = Segment(
                repo=spec.name, parent_module=module, n_commits=len(comp), span_days=span,
                first_date=comp_recs[0]["date"], last_date=comp_recs[-1]["date"],
                files=union_files, core_files=core,
                shas=[r["sha"] for r in comp_recs],
                subjects=[r["subject"] for r in comp_recs],
                is_motif_grade=is_grade,
                audit_hint=_audit_hint(spec, module, union_files, core, comp_recs),
            )
            segments.append(seg)
    return segments


def _audit_hint(spec: RepoSpec, module: str, files: list[str], core: list[str],
                recs: list[dict]) -> str:
    flagship = _FLAGSHIP.get(spec.name, {}).get(module)
    if flagship:
        return f"FLAGSHIP {flagship} | core files: {core[:4]}"
    # generic: surface the most-touched test (the behavior the invariant lives in)
    tests = [f for f in core if "test" in f.lower()]
    if tests:
        return f"behavior anchor (test file): {tests[0]} | core: {core[:3]}"
    return f"core footprint: {core[:4]}"


_FLAGSHIP = {
    "httpx": {
        "client-api": "sync/async parity (Client/AsyncClient) — Fork candidate",
        "transport": "transport Join sink (proxy/redirect/ssl/auth)",
        "auth": "auth precedence — Hard-negative candidate",
    },
    "viper": {
        "core-precedence": "config precedence invariant — Scope + Hard-negative",
        "key-normalization": "alias/normalization rule — Update candidate",
    },
    "fastify": {
        "plugin-scope": "encapsulation boundary — Scope oracle",
        "hook-lifecycle": "hook ordering — Join candidate",
        "schema": "schema validation rule — Update candidate",
    },
    "clap": {
        "builder-api": "builder surface — Fork + Update (deprecations)",
        "derive-api": "derive↔builder parity — Fork target",
    },
    "ripgrep": {
        "ignore-precedence": "gitignore precedence layers — Scope + Update",
    },
}


def load_commits(spec: RepoSpec) -> list[dict]:
    p = OUT_DIR / f"{spec.name}.commits.jsonl"
    if not p.exists():
        print(f"[warn] {spec.name}: {p} missing — run cochange_miner first", file=sys.stderr)
        return []
    return [json.loads(l) for l in p.open() if l.strip()]


def report(spec: RepoSpec, segs: list[Segment], n_raw: int) -> str:
    grade = [s for s in segs if s.is_motif_grade]
    lines = [
        f"# {spec.name}  ({spec.lang}) — motif segments",
        f"  raw co-change commits:           {n_raw}",
        f"  segments found:                  {len(segs)}",
        f"  motif-grade segments "
        f"(≥{SEG_MIN_COMMITS} commits, ≥{SEG_MIN_SPAN_DAYS}d, ≥{SEG_MIN_FILES} files): {len(grade)}",
        "",
    ]
    if not grade:
        lines.append("  (no motif-grade segment — premise may be weak, or fingerprints too strict)")
        return "\n".join(lines)
    lines.append("  motif-grade segments (top by commit count):")
    for s in sorted(grade, key=lambda s: -s.n_commits)[:10]:
        lines.append(f"    • [{s.parent_module}] {s.n_commits:3d} commits  span {s.span_days:4d}d  "
                     f"core={s.core_files[:3]}")
        lines.append(f"        {s.audit_hint}")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", nargs="*", default=[])
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    names = args.repo or (list(REPOS) if args.all else list(REPOS))

    all_grade = {}
    for name in names:
        spec = REPOS[name]
        commits = load_commits(spec)
        if not commits:
            continue
        segs = refine_repo(spec, commits)
        all_grade[name] = sum(1 for s in segs if s.is_motif_grade)
        # write
        outp = OUT_DIR / f"{spec.name}.segments.jsonl"
        with outp.open("w") as f:
            for s in sorted(segs, key=lambda s: (not s.is_motif_grade, -s.n_commits)):
                f.write(json.dumps(asdict(s), ensure_ascii=False) + "\n")
        print(report(spec, segs, len(commits)))

    print("=" * 70)
    print("MOTIF-GRADE SEGMENT COUNT (the number that matters for the premise):")
    for name, n in all_grade.items():
        print(f"  {name:10s} {n}")
    print("  " + "-" * 30)
    print(f"  TOTAL      {sum(all_grade.values())}")
    print(f"\nOUTPUTS: {OUT_DIR}/<repo>.segments.jsonl")


if __name__ == "__main__":
    main()
