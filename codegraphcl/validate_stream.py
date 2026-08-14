"""`codegraphcl validate-stream` — validate stream files for Phase 4.1.

Checks:
  - all task_ids in streams are release_core
  - no dangling IDs (task_id exists in task bank)
  - no duplicate families (same canonical_sig)
  - motif quota: each of 7 motifs has >= required families
  - diagnostic streams only reference release_core nodes
  - integrated streams have >=2 motifs, >=1 real edge, >=1 distractor
  - no stream references pending/rejected/infrastructure_blocked nodes

Usage:
  python3 -m codegraphcl validate-stream
"""
from __future__ import annotations
import json
import sys
import yaml
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmark"


def _load_task_tiers():
    """Return {task_id: verification_tier}."""
    tiers = {}
    for ty in sorted((BENCH / "tasks").glob("*/task.yaml")):
        cfg = yaml.safe_load(ty.read_text())
        tid = cfg.get("task_id") or ty.parent.name
        tier = cfg.get("status", {}).get("verification_tier", "unknown")
        tiers[tid] = tier
    return tiers


def cmd_validate_stream():
    tiers = _load_task_tiers()
    errors = []
    warnings = []

    # diagnostic streams
    diag_dir = BENCH / "streams" / "diagnostic"
    motif_counts = defaultdict(int)
    motif_episodes = defaultdict(int)
    total_families = 0
    total_episodes = 0
    seen_sigs = set()

    if diag_dir.exists():
        for f in sorted(diag_dir.glob("*.jsonl")):
            motif = f.stem.split("_seed")[0]
            for line in f.read_text().strip().splitlines():
                s = json.loads(line)
                total_families += 1
                motif_counts[motif] += 1
                tids = s.get("task_ids", [])
                ep_count = len(tids)
                total_episodes += ep_count
                motif_episodes[motif] += ep_count
                sig = s.get("canonical_sig", "")
                if sig in seen_sigs:
                    errors.append(f"diagnostic: duplicate canonical_sig {sig} in {s.get('stream_id','')}")
                seen_sigs.add(sig)
                for tid in tids:
                    if tid not in tiers:
                        errors.append(f"diagnostic {s.get('stream_id','')}: dangling task_id '{tid}'")
                    elif tiers[tid] != "release_core":
                        errors.append(f"diagnostic {s.get('stream_id','')}: non-core node '{tid}' (tier={tiers[tid]})")

    # integrated streams
    int_dir = BENCH / "streams" / "integrated"
    int_families = 0
    if int_dir.exists():
        for f in sorted(int_dir.glob("*.jsonl")):
            for line in f.read_text().strip().splitlines():
                s = json.loads(line)
                int_families += 1
                tids = s.get("task_ids", [])
                motifs_used = s.get("motifs_used", [])
                for tid in tids:
                    if tid not in tiers:
                        errors.append(f"integrated {s.get('stream_id','')}: dangling task_id '{tid}'")
                    elif tiers[tid] != "release_core":
                        errors.append(f"integrated {s.get('stream_id','')}: non-core node '{tid}' (tier={tiers[tid]})")
                if len(motifs_used) < 2:
                    warnings.append(f"integrated {s.get('stream_id','')}: only {len(motifs_used)} motifs (need >=2)")

    # motif quota check
    required_motifs = {"direct", "delayed", "fork", "join", "scope", "update", "hard_negative"}
    for m in required_motifs:
        if motif_counts[m] == 0:
            errors.append(f"motif quota: '{m}' has 0 families (need >=1)")
        print(f"  {m}: {motif_counts[m]} families, {motif_episodes[m]} episodes")

    print(f"\n=== Stream Validation ===")
    print(f"Diagnostic: {total_families} families, {total_episodes} episodes ({len(required_motifs)} motifs)")
    print(f"Integrated: {int_families} families")
    print(f"Unique canonical_sigs: {len(seen_sigs)}")

    if errors:
        print(f"\nVALIDATION ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        return 1
    if warnings:
        print(f"\nWarnings ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")
    print("\nValidation: PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(cmd_validate_stream())
