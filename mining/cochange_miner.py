"""Co-change miner: find commits where source + test files change together, cluster them
by subsystem, and flag clusters that have enough commits over enough time to be candidate
graph-motif seeds (Fork/Join/Scope/Update all need a *sequence* of related commits, not
one-off changes).

This is deliberately a *reconnaissance* tool. It does NOT claim to identify motifs from
git metadata alone — motif identity is a semantic judgment (does task_B actually depend on
experience from task_A?). What it can do is narrow 5 repos × thousands of commits down to
a few hundred candidate commits worth hand-reading, and tell us whether ref_codebase's
central premise (that these repos *naturally* produce repeated cross-cutting constraints)
is load-bearing or hand-wavy.

Contract:
- Input: a cloned repo at ../repos/<name> (blob-filter clone is fine; git log works).
- Output (JSONL to mining/out/<name>.clusters.jsonl + .commits.jsonl + a human report):
    per-commit: {repo, sha, date, subject, n_src, n_test, n_other, modules, files}
    per-cluster: {module, n_commits, span_days, shas, subjects, motif_hypotheses}
  A cluster is "motif-candidate" iff n_commits >= MIN_COMMITS and span_days >= MIN_SPAN.

Run: python3 mining/cochange_miner.py [--repo NAME ...] [--all]
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable

# Make repo_config importable regardless of cwd.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from repo_config import REPOS, RepoSpec, classify, module_of  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
REPOS_DIR = ROOT / "repos"
OUT_DIR = ROOT / "mining" / "out"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# A cluster needs a real sequence to seed a motif edge.
MIN_COMMITS = 3          # ≥3 co-change commits in one subsystem
MIN_SPAN_DAYS = 14       # spread over ≥2 weeks ⇒ not one frantic afternoon
# How many recent commits to scan per repo (0 = all). 0 keeps the honest full history.
DEFAULT_LIMIT = 0
# Skip merge commits — they re-touch everything and fake co-change signal.
SKIP_MERGES = True


# ---------------------------------------------------------------- data types
@dataclass
class CommitRec:
    repo: str
    sha: str
    date: str          # ISO 8601
    subject: str
    n_src: int
    n_test: int
    n_other: int
    modules: list[str]
    files: list[str]


@dataclass
class Cluster:
    repo: str
    module: str
    n_commits: int
    span_days: int
    first_date: str
    last_date: str
    shas: list[str]
    subjects: list[str]
    modules_touched: list[str]   # all subsystems seen in the cluster (for cross-subsystem join hint)
    motif_hypotheses: list[str]  # text hints, NOT verified
    is_motif_candidate: bool


# ---------------------------------------------------------------- git plumbing
def _git(repo_dir: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo_dir), *args],
        check=True, capture_output=True, text=True,
    )
    return result.stdout


def iter_commits(repo_dir: Path, limit: int = 0) -> Iterable[tuple[str, str, str, str]]:
    """Yield (sha, iso_date, subject, ) for each commit. Date in author ISO for stable ordering."""
    fmt = "%H%x1f%aI%x1f%s"  # sha ⒟ date ⒟ subject, unit-separated
    args = ["log", f"--format={fmt}"]
    if SKIP_MERGES:
        args.append("--no-merges")
    if limit and limit > 0:
        args.append(f"-{limit}")
    out = _git(repo_dir, args)
    for line in out.splitlines():
        if not line.strip():
            continue
        sha, date, subject = line.split("\x1f", 2)
        yield sha, date, subject


def commit_files(repo_dir: Path, sha: str) -> list[str]:
    """All file paths changed by `sha` (A/C/M/D/R).

    Uses `git diff-tree` (tree-only) instead of `git show --name-only`: on a blob-filter
    clone (--filter=blob:none) the blobs are absent, and `show` needs to materialize them.
    diff-tree walks the tree objects, which are always present, so it works on partial clones
    without a network round-trip per commit.
    """
    out = _git(repo_dir, ["diff-tree", "--no-commit-id", "--name-only", "-r", sha])
    return [p for p in out.splitlines() if p.strip()]


# ---------------------------------------------------------------- core
def build_commit_records(spec: RepoSpec, limit: int) -> list[CommitRec]:
    repo_dir = REPOS_DIR / spec.name
    if not repo_dir.exists():
        print(f"[warn] {spec.name}: repo not found at {repo_dir}", file=sys.stderr)
        return []
    recs: list[CommitRec] = []
    for sha, date, subject in iter_commits(repo_dir, limit):
        files = commit_files(repo_dir, sha)
        n_src = n_test = n_other = 0
        modules: set[str] = set()
        kept_files: list[str] = []
        for f in files:
            kind = classify(spec, f)
            if kind == "ignore":
                continue
            kept_files.append(f)
            if kind == "src":
                n_src += 1
            elif kind == "test":
                n_test += 1
            else:
                n_other += 1
            modules.add(module_of(spec, f))
        # Co-change = source AND test changed together. This is the signal we mine.
        if n_src == 0 or n_test == 0:
            continue
        recs.append(CommitRec(
            repo=spec.name, sha=sha, date=date, subject=subject.strip(),
            n_src=n_src, n_test=n_test, n_other=n_other,
            modules=sorted(modules), files=kept_files,
        ))
    return recs


def cluster_by_module(recs: list[CommitRec], spec: RepoSpec) -> list[Cluster]:
    """Group co-change commits by their primary module (first module in the sorted list).

    Clustering is intentionally coarse — its job is to surface candidates, not to be the
    final task-boundary. The hand-audit step re-slices commits into task nodes.
    """
    by_module: dict[str, list[CommitRec]] = defaultdict(list)
    for r in recs:
        if not r.modules:
            continue
        primary = r.modules[0]
        by_module[primary].append(r)

    clusters: list[Cluster] = []
    for module, recs_in in sorted(by_module.items()):
        recs_in.sort(key=lambda r: r.date)
        dates = [datetime.fromisoformat(r.date.replace("Z", "+00:00")) for r in recs_in]
        span_days = int((max(dates) - min(dates)).total_seconds() / 86400) if len(dates) > 1 else 0
        all_mods: set[str] = set()
        for r in recs_in:
            all_mods.update(r.modules)
        is_candidate = len(recs_in) >= MIN_COMMITS and span_days >= MIN_SPAN_DAYS
        clusters.append(Cluster(
            repo=spec.name, module=module, n_commits=len(recs_in), span_days=span_days,
            first_date=recs_in[0].date, last_date=recs_in[-1].date,
            shas=[r.sha for r in recs_in],
            subjects=[r.subject for r in recs_in],
            modules_touched=sorted(all_mods),
            motif_hypotheses=_hypothesize_motifs(module, recs_in, spec),
            is_motif_candidate=is_candidate,
        ))
    return clusters


def _hypothesize_motifs(module: str, recs: list[CommitRec], spec: RepoSpec) -> list[str]:
    """Cheap, explicit, *unverified* motif hints. Each hint names a motif and WHY it's
    plausible from metadata only. Never assert a motif — always flag for hand-audit."""
    hints: list[str] = []
    subsys = set()
    for r in recs:
        subsys.update(r.modules)
    n = len(recs)
    repo = spec.name

    # Fork/Join hint: a single subsystem's commits touch >1 distinct subsystem.
    # Fork = one source invariant spreads to ≥2 targets; Join = one target pulls from ≥2 sources.
    if len(subsys) >= 2:
        hints.append(f"Fork/Join? commits in '{module}' also touch {sorted(subsys - {module})} "
                     f"(cross-subsystem co-change ⇒ experience may carry). NEEDS hand-audit.")

    # Update/Stale hint: subject keywords suggesting deprecation, refactor, migration, removal.
    dep_words = ("deprecat", "remov", "migrat", "refactor", "renam", "replac", "drop", "stale", "break")
    dep_subjects = [r.subject for r in recs if any(w in r.subject.lower() for w in dep_words)]
    if dep_subjects:
        hints.append(f"Update/Stale? {len(dep_subjects)}/{n} commits use deprecate/migrate/remove/refactor "
                     f"language ⇒ possible rule-revision chain. NEEDS hand-audit.")

    # Hard-negative hint: many commits, similar subject prefix → possibly look-alike-but-unrelated.
    # (Weak; just flags density worth a second look.)
    if n >= 6:
        hints.append(f"Hard-negative density? {n} commits in '{module}' over "
                     f"{_span(recs)} days — check whether some are surface-similar but causally unrelated.")

    # Repo-specific flagship hints so the auditor sees the intended motif immediately.
    flagship = _FLAGSHIP_HINTS.get(repo, {}).get(module)
    if flagship:
        hints.append(f"FLAGSHIP target: {flagship}")
    return hints


_FLAGSHIP_HINTS = {
    "httpx": {
        "client-api": "sync/async parity — Client & AsyncClient must stay behaviorally equal (Fork).",
        "toplevel-api": "top-level shortcuts mirror client methods (Fork from client-api).",
        "transport": "transport layer is the Join sink: proxy/redirect/ssl/auth all funnel here.",
    },
    "viper": {
        "core-precedence": "explicit > flag > env > config > default precedence — Scope + Hard-negative ground truth.",
        "key-normalization": "alias / case-insensitive key rules — Update candidate (normalization changed over time).",
    },
    "fastify": {
        "plugin-scope": "parent/child/sibling encapsulation boundary — executable Scope oracle.",
        "hook-lifecycle": "hook ordering + decorator interaction — Join motif.",
        "type-parity": "TS types mirror runtime — Fork across runtime↔type surface.",
    },
    "clap": {
        "builder-api": "builder ↔ derive parity (Fork); deprecations here seed Update chains.",
        "derive-api": "derive must match builder surface (Fork target).",
        "help-output": "help/error/completion output snapshot — Update under versioning.",
    },
    "ripgrep": {
        "ignore-precedence": "gitignore / glob precedence layers — Scope + Update candidate.",
        "cli-flags": "flag precedence & override — Hard-negative candidate.",
    },
}


def _span(recs: list[CommitRec]) -> int:
    if len(recs) < 2:
        return 0
    dates = [datetime.fromisoformat(r.date.replace("Z", "+00:00")) for r in recs]
    return int((max(dates) - min(dates)).total_seconds() / 86400)


# ---------------------------------------------------------------- reporting
def write_outputs(spec: RepoSpec, recs: list[CommitRec], clusters: list[Cluster]) -> None:
    commits_path = OUT_DIR / f"{spec.name}.commits.jsonl"
    clusters_path = OUT_DIR / f"{spec.name}.clusters.jsonl"
    with commits_path.open("w") as f:
        for r in recs:
            f.write(json.dumps(asdict(r), ensure_ascii=False) + "\n")
    with clusters_path.open("w") as f:
        for c in sorted(clusters, key=lambda c: (not c.is_motif_candidate, -c.n_commits)):
            f.write(json.dumps(asdict(c), ensure_ascii=False) + "\n")


def report(spec: RepoSpec, recs: list[CommitRec], clusters: list[Cluster]) -> str:
    cands = [c for c in clusters if c.is_motif_candidate]
    lines = [
        f"# {spec.name}  ({spec.lang})",
        f"  co-change commits (src+test together): {len(recs)}",
        f"  clusters (by primary module):          {len(clusters)}",
        f"  motif-candidate clusters "
        f"(≥{MIN_COMMITS} commits, ≥{MIN_SPAN_DAYS}d span): {len(cands)}",
        "",
    ]
    if not cands:
        lines.append("  (no motif-candidate clusters — premise weak for this repo)")
        return "\n".join(lines)
    lines.append("  top motif-candidate clusters:")
    for c in sorted(cands, key=lambda c: -c.n_commits)[:8]:
        lines.append(f"    • {c.module:24s} {c.n_commits:3d} commits  "
                     f"span {c.span_days:4d}d  subsys={c.modules_touched}")
        for h in c.motif_hypotheses[:3]:
            lines.append(f"        - {h}")
    return "\n".join(lines)


# ---------------------------------------------------------------- entry
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", nargs="*", default=[], help="repo names to mine (default: all)")
    ap.add_argument("--all", action="store_true", help="mine all configured repos")
    ap.add_argument("--limit", type=int, default=DEFAULT_LIMIT,
                    help=f"max commits per repo (0=all) [default {DEFAULT_LIMIT}]")
    args = ap.parse_args()

    names = args.repo or (list(REPOS) if args.all else list(REPOS))
    unknown = [n for n in names if n not in REPOS]
    if unknown:
        ap.error(f"unknown repo(s): {unknown}; configured: {list(REPOS)}")

    summary = []
    for name in names:
        spec = REPOS[name]
        recs = build_commit_records(spec, args.limit)
        clusters = cluster_by_module(recs, spec)
        write_outputs(spec, recs, clusters)
        rep = report(spec, recs, clusters)
        summary.append(rep)
        print(rep)
    print("\n" + "=" * 70)
    print("OUTPUTS:")
    print(f"  per-repo commits:   {OUT_DIR}/<repo>.commits.jsonl")
    print(f"  per-repo clusters:  {OUT_DIR}/<repo>.clusters.jsonl")


if __name__ == "__main__":
    main()
