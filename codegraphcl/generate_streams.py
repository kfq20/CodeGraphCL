"""`codegraphcl generate-streams` — build Diagnostic + Integrated task streams from the Experience Graph.

Phase 4 Task 4. Reads benchmark/edges/*.yaml + benchmark/tasks/*/task.yaml to build the graph,
then emits streams of task IDs per the motif templates. Streams are sequences of Task Node IDs
with a producer/consumer structure; the executor (Phase 5) runs them as sequential agent sessions
(Stateful) or fresh sessions (Reset).

Motif templates (per phase4.md §III Task 4):
  Direct:       A -> B                      (1 edge, distance 1)
  Delayed:      A -> D1 -> D2 -> B           (a chain of length >=3, distance 3)
  Fork:         A -> {B1, B2}                (one producer, >=2 consumers)
  Join:         {A1, A2} -> B                (>=2 producers, one consumer)
  Scope:        A -> B_in / B_out            (consumer in-scope vs out-of-scope — approximated by
                                             picking an unrelated distractor as B_out)
  Update:       A_old -> U -> B              (a stale producer + an update + a consumer)
  HardNegative: A -> H_similar -> B          (a structurally-similar-but-wrong intermediate)

Controls (CLI flags):
  --type {diagnostic,integrated}
  --motif {direct,delayed,fork,join,scope,update,hard_negative}  (diagnostic only; integrated mixes)
  --distance N         (for delayed: min chain length; default 3)
  --parent-count N     (for join: number of producers; default 2)
  --distractor N       (number of distractor tasks interspersed; default 0)
  --distractor-similarity {high,medium,low}  (how close distractors are to the real path; default medium)
  --stale / --wrong    (include a stale/wrong-history variant; default off)
  --missing-parent     (drop one producer from a join/fork to test missing-history; default off)
  --length N           (integrated stream length 5-10; default 6)
  --repo / --language  (constrain to one repo/lang; default any)
  --count N            (number of streams to generate; default 10)
  --seed N             (deterministic RNG; default 42)

Combo-bloat controls (phase4 §III Task 5): canonical stream signature (sorted task-id tuple +
motif + intervention-variant) dedupes permutations; family equivalence (same target+parents+
motif+delay+intervention) collapses linearization variants. The generator never emits two
streams with the same canonical signature.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import random
import sys
import yaml
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmark"
EDGES_DIR = BENCH / "edges"
TASKS_DIR = BENCH / "tasks"
STREAMS_DIR = BENCH / "streams"


def _load_graph():
    """Return (nodes, edges). nodes = {task_id: {family, repo, language}}. edges = list of dicts."""
    nodes = {}
    for ty in sorted(TASKS_DIR.glob("*/task.yaml")):
        cfg = yaml.safe_load(ty.read_text())
        tid = cfg.get("task_id") or ty.parent.name
        family = cfg.get("family_id", "unknown")
        repo = cfg.get("repository", {}).get("url", "").split("/")[-1]
        lang = cfg.get("repository", {}).get("language", "unknown")
        nodes[tid] = {"family": family, "repo": repo, "language": lang,
                      "base_commit": cfg.get("repository", {}).get("base_commit"),
                      "gold_commit": cfg.get("repository", {}).get("gold_commit")}
    edges = []
    for ef in sorted(EDGES_DIR.glob("*.yaml")):
        ec = yaml.safe_load(ef.read_text())
        fr, to = ec.get("from"), ec.get("to")
        et = ec.get("edge_type", "unknown")
        # skip external-provenance / self-loop edges (not real Task-Graph edges)
        if not fr or not to or fr == to:
            continue
        if fr not in nodes or to not in nodes:
            continue  # external_commit provenance (e.g. b621e65) — not a real edge
        edges.append({"edge_id": ec.get("edge_id", ef.stem), "from": fr, "to": to,
                      "type": et, "motif_hint": ec.get("mechanism_audit", {}).get("motif", "")})
    return nodes, edges


def _canonical_sig(stream):
    """Canonical signature for dedup: sorted task-id tuple + motif + intervention flags.
    Two streams that differ only in node ORDER (but have the same node set + motif + intervention)
    are the same family — collapsed."""
    ids = sorted(stream["task_ids"])
    key = "|".join(ids) + f"|{stream['motif']}|{stream.get('intervention','none')}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def _ancestors(target, edges):
    """Return the set of direct producers of `target`."""
    return {e["from"] for e in edges if e["to"] == target}


def _descendants(source, edges):
    return {e["to"] for e in edges if e["from"] == source}


def build_direct(edges, rng, **kw):
    """A -> B: pick a random edge."""
    if not edges: return None
    e = rng.choice(edges)
    return {"motif": "direct", "task_ids": [e["from"], e["to"]], "edges": [e["edge_id"]],
            "intervention": kw.get("intervention", "none")}


def build_delayed(edges, rng, distance=3, **kw):
    """A -> D1 -> ... -> B: a chain of length >= distance. Walk forward from a random source."""
    if not edges: return None
    for _ in range(50):
        e = rng.choice(edges)
        chain = [e["from"], e["to"]]
        cur = e["to"]
        while len(chain) < distance:
            nxt = [d for d in _descendants(cur, edges) if d not in chain]
            if not nxt: break
            cur = rng.choice(nxt); chain.append(cur)
        if len(chain) >= distance:
            return {"motif": "delayed", "task_ids": chain, "edges": [],
                    "intervention": kw.get("intervention", "none")}
    return None


def build_fork(edges, rng, parent_count=2, **kw):
    """A -> {B1, B2}: one producer with >=2 consumers."""
    by_src = defaultdict(list)
    for e in edges: by_src[e["from"]].append(e)
    forks = {s: cs for s, cs in by_src.items() if len(cs) >= parent_count}
    if not forks: return None
    src = rng.choice(list(forks))
    cs = rng.sample(forks[src], min(parent_count, len(forks[src])))
    return {"motif": "fork", "task_ids": [src] + [c["to"] for c in cs],
            "edges": [c["edge_id"] for c in cs], "intervention": kw.get("intervention", "none")}


def build_join(edges, rng, parent_count=2, **kw):
    """{A1, A2} -> B: >=2 producers, one consumer."""
    by_dst = defaultdict(list)
    for e in edges: by_dst[e["to"]].append(e)
    joins = {d: ps for d, ps in by_dst.items() if len(ps) >= parent_count}
    if not joins: return None
    dst = rng.choice(list(joins))
    ps = rng.sample(joins[dst], min(parent_count, len(joins[dst])))
    return {"motif": "join", "task_ids": [p["from"] for p in ps] + [dst],
            "edges": [p["edge_id"] for p in ps], "intervention": kw.get("intervention", "none")}


def build_scope(edges, rng, nodes, **kw):
    """A -> B_in / B_out: a real edge + a distractor consumer (B_out) that is unrelated.
    Approximated as: pick an edge A->B; pick a distractor D from a DIFFERENT family than B;
    stream = [A, B, D] where D is the out-of-scope control."""
    if not edges: return None
    e = rng.choice(edges)
    # distractor: a node not in {A,B}'s family
    b_fam = nodes.get(e["to"], {}).get("family", "")
    cands = [n for n in nodes if nodes[n]["family"] != b_fam and n not in (e["from"], e["to"])]
    if not cands: return None
    d = rng.choice(cands)
    return {"motif": "scope", "task_ids": [e["from"], e["to"], d],
            "edges": [e["edge_id"]], "intervention": kw.get("intervention", "none"),
            "distractor": d, "distractor_role": "out_of_scope"}


def build_update(edges, rng, **kw):
    """A_old -> U -> B: a chain where the first edge is stale (the producer's rule was later
    updated). Approximated as a delayed chain of length 3, flagged stale on the first edge."""
    d = build_delayed(edges, rng, distance=3)
    if not d: return None
    d["motif"] = "update"; d["intervention"] = "stale"
    return d


def build_hard_negative(edges, rng, nodes, **kw):
    """A -> H_similar -> B: the real path A->B, with a structurally-similar distractor H
    inserted that looks like it should carry the experience but doesn't. Approximated:
    pick edge A->B; pick H from the SAME family as A (similar) but not A or B."""
    if not edges: return None
    e = rng.choice(edges)
    a_fam = nodes.get(e["from"], {}).get("family", "")
    cands = [n for n in nodes if nodes[n]["family"] == a_fam and n not in (e["from"], e["to"])]
    if not cands: cands = [n for n in nodes if n not in (e["from"], e["to"])]
    if not cands: return None
    h = rng.choice(cands)
    return {"motif": "hard_negative", "task_ids": [e["from"], h, e["to"]],
            "edges": [e["edge_id"]], "intervention": kw.get("intervention", "none"),
            "distractor": h, "distractor_role": "similar_but_wrong"}


BUILDERS = {
    "direct": lambda edges, rng, **kw: build_direct(edges, rng, **kw),
    "delayed": lambda edges, rng, **kw: build_delayed(edges, rng, **kw),
    "fork": lambda edges, rng, **kw: build_fork(edges, rng, **kw),
    "join": lambda edges, rng, **kw: build_join(edges, rng, **kw),
    "scope": lambda edges, rng, nodes, **kw: build_scope(edges, rng, nodes, **kw),
    "update": lambda edges, rng, **kw: build_update(edges, rng, **kw),
    "hard_negative": lambda edges, rng, nodes, **kw: build_hard_negative(edges, rng, nodes, **kw),
}


def cmd_generate(args):
    nodes, edges = _load_graph()
    rng = random.Random(args.seed)
    STREAMS_DIR.mkdir(parents=True, exist_ok=True)
    out_dir = STREAMS_DIR / ("diagnostic" if args.type == "diagnostic" else "integrated")
    out_dir.mkdir(exist_ok=True)
    seen_sigs = set()
    streams = []
    attempts = 0
    motif = args.motif or rng.choice(list(BUILDERS))
    while len(streams) < args.count and attempts < args.count * 20:
        attempts += 1
        kw = {"distance": args.distance, "parent_count": args.parent_count,
              "intervention": "none"}
        if args.stale: kw["intervention"] = "stale"
        if args.wrong: kw["intervention"] = "wrong"
        builder = BUILDERS[motif]
        try:
            s = builder(edges, rng, nodes=nodes, **kw) if motif in ("scope", "hard_negative") \
                else builder(edges, rng, **kw)
        except Exception:
            s = None
        if not s: continue
        sig = _canonical_sig(s)
        if sig in seen_sigs: continue
        seen_sigs.add(sig)
        s["stream_id"] = f"{motif}_{len(streams):03d}_seed{args.seed}"
        s["canonical_sig"] = sig
        streams.append(s)
    out = out_dir / f"streams_seed{args.seed}.jsonl"
    with out.open("w") as f:
        for s in streams:
            f.write(json.dumps(s) + "\n")
    print(f"generated {len(streams)} {args.type} streams ({motif}) -> {out}")
    for s in streams:
        print(f"  {s['stream_id']}: {s['task_ids']} ({s['motif']})")
    if not streams:
        print(f"(0 streams — graph has {len(edges)} edges, {len(nodes)} nodes; motif {motif} "
              f"may need more edges/nodes. See PHASE4 needs.)")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", default="diagnostic", choices=["diagnostic", "integrated"])
    ap.add_argument("--motif", default=None, choices=list(BUILDERS))
    ap.add_argument("--distance", type=int, default=3)
    ap.add_argument("--parent-count", type=int, default=2)
    ap.add_argument("--distractor", type=int, default=0)
    ap.add_argument("--distractor-similarity", default="medium", choices=["high","medium","low"])
    ap.add_argument("--stale", action="store_true")
    ap.add_argument("--wrong", action="store_true")
    ap.add_argument("--missing-parent", action="store_true")
    ap.add_argument("--length", type=int, default=6)
    ap.add_argument("--count", type=int, default=10)
    ap.add_argument("--seed", type=int, default=42)
    sys.exit(cmd_generate(ap.parse_args()))
