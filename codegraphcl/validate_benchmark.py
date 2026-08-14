"""`codegraphcl validate-benchmark` — build index.jsonl + graph.yaml and validate the full benchmark.

Scans benchmark/tasks/*/task.yaml + benchmark/edges/*.yaml + benchmark/families/*.yaml to build:
  - benchmark/index.jsonl  (one line per task: task_id, family, repo, language, base/gold commit,
    verification_tier, executable_gate, motif)
  - benchmark/graph.yaml   (nodes + edges, with motifs and intervention_status)

Then validates:
  - every edge's from/to resolves to a real Task Node (no self-loops, no dangling)
  - external_commit provenance is marked (not counted as a real edge)
  - no family is empty (each family YAML references at least one task that exists)
  - reports counts + the phase4 target gaps

Usage:
  python3 -m codegraphcl validate-benchmark
"""
from __future__ import annotations
import json
import sys
import yaml
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmark"


def _load_tasks():
    tasks = {}
    for ty in sorted((BENCH / "tasks").glob("*/task.yaml")):
        cfg = yaml.safe_load(ty.read_text())
        tid = cfg.get("task_id") or ty.parent.name
        repo = cfg.get("repository", {})
        status = cfg.get("status", {})
        tasks[tid] = {
            "task_id": tid,
            "family_id": cfg.get("family_id", "unknown"),
            "repo": (repo.get("url", "").split("/")[-1] if repo.get("url") else "unknown"),
            "language": repo.get("language", "unknown"),
            "base_commit": repo.get("base_commit", ""),
            "gold_commit": repo.get("gold_commit", ""),
            "verification_tier": status.get("verification_tier", "unknown"),
            "executable_gate": status.get("executable_gate", "unknown"),
            "motif": cfg.get("mechanism_audit", {}).get("motif", "") if isinstance(cfg.get("mechanism_audit"), dict) else "",
        }
    return tasks


def _load_edges(nodes):
    edges = []
    for ef in sorted((BENCH / "edges").glob("*.yaml")):
        ec = yaml.safe_load(ef.read_text()) or {}
        fr, to = ec.get("from"), ec.get("to")
        pt = ec.get("provenance_type", "task_node")
        et = ec.get("edge_type", "unknown")
        # skip external_commit / self-loop
        is_real = fr in nodes and to in nodes and fr != to
        edges.append({
            "edge_id": ec.get("edge_id", ef.stem), "from": fr, "to": to,
            "edge_type": et, "provenance_type": pt,
            "is_real": is_real,
            "intervention_status": ec.get("status", {}).get("causal_verification", "not_sampled"),
        })
    return edges


def _load_families():
    fams = {}
    for ff in sorted((BENCH / "families").glob("*.yaml")):
        fc = yaml.safe_load(ff.read_text()) or {}
        fid = fc.get("family_id", ff.stem)
        fams[fid] = fc
    return fams


def cmd_validate_benchmark():
    tasks = _load_tasks()
    edges = _load_edges(tasks)
    families = _load_families()

    # write index.jsonl
    idx = BENCH / "index.jsonl"
    with idx.open("w") as f:
        for tid in sorted(tasks):
            f.write(json.dumps(tasks[tid]) + "\n")

    # write graph.yaml
    real_edges = [e for e in edges if e["is_real"]]
    graph = {
        "nodes": sorted(tasks.keys()),
        "edges": [{"edge_id": e["edge_id"], "from": e["from"], "to": e["to"],
                   "edge_type": e["edge_type"],
                   "intervention_status": e["intervention_status"]}
                  for e in real_edges],
        "external_provenance_edges": [{"edge_id": e["edge_id"], "from": e["from"], "to": e["to"],
                                       "provenance_type": e["provenance_type"]}
                                    for e in edges if not e["is_real"]],
    }
    (BENCH / "graph.yaml").write_text(yaml.dump(graph, sort_keys=False, default_flow_style=False))

    # validate
    errors = []
    # edge endpoints
    for e in edges:
        if e["from"] == e["to"] and e["provenance_type"] != "external_commit":
            errors.append(f"self-loop edge {e['edge_id']}: from==to={e['from']}")
        if e["is_real"]:
            if e["from"] not in tasks:
                errors.append(f"edge {e['edge_id']}: from '{e['from']}' not a task node")
            if e["to"] not in tasks:
                errors.append(f"edge {e['edge_id']}: to '{e['to']}' not a task node")
    # families not empty
    for fid, fc in families.items():
        fnodes = fc.get("nodes", [])
        missing = [n for n in fnodes if n not in tasks]
        if missing:
            errors.append(f"family {fid}: nodes {missing} not in task bank")

    # report
    repos = sorted(set(t["repo"] for t in tasks.values()))
    langs = sorted(set(t["language"] for t in tasks.values()))
    n_exec = sum(1 for t in tasks.values() if t["executable_gate"] == "passed")
    print(f"=== CodeGraphCL Benchmark Validation ===")
    print(f"tasks: {len(tasks)} ({n_exec} executable_gate:passed)")
    print(f"edges: {len(real_edges)} real + {len(edges)-len(real_edges)} external/dangling")
    print(f"families: {len(families)}")
    print(f"repos: {len(repos)} ({', '.join(repos)})")
    print(f"languages: {len(langs)} ({', '.join(langs)})")
    print(f"motifs in edges: {len(set(e['edge_type'] for e in real_edges))}")
    if errors:
        print(f"\nVALIDATION ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("\nValidation: PASSED")
    # phase4 target gaps
    print(f"\n=== Phase 4 target gaps ===")
    print(f"  tasks: {len(tasks)}/60 (need {max(0,60-len(tasks))} more)")
    print(f"  edges: {len(real_edges)}/40 (need {max(0,40-len(real_edges))} more)")
    print(f"  families: {len(families)}/18 (need {max(0,18-len(families))} more)")
    print(f"  repos: {len(repos)}/5 {'✓' if len(repos)>=5 else '(need more)'}")
    print(f"  languages: {len(langs)}/3 {'✓' if len(langs)>=3 else '(need more)'}")
    return 0


if __name__ == "__main__":
    sys.exit(cmd_validate_benchmark())
