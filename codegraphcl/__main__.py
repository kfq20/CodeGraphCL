"""codegraphcl — unified, config-driven CLI for CodeGraphCL task construction & intervention.

Subcommands (phase1):
  validate <task_dir> [--family <family.yaml>]
  materialize <task_dir>            (phase1 day2)
  prompt-preview <edge.yaml>        (phase1 day3)
  intervene <edge.yaml> --n 1 --seed 42   (phase1 day3)

No task-specific names in this package (no httpx/ripgrep/r829/start_tls/fixed-SHA/fixed
container). Everything task-specific lives in task dirs as data.
"""
from __future__ import annotations
import argparse
import sys


def main() -> int:
    ap = argparse.ArgumentParser(prog="python -m codegraphcl", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="check a task config is complete + self-consistent")
    v.add_argument("task_dir")
    v.add_argument("--family", default=None)

    m = sub.add_parser("materialize", help="run base-fail/gold-pass/PASS_TO_PASS/near-miss")
    m.add_argument("task_dir")
    m.add_argument("--run-id", default=None)
    m.add_argument("--container", default=None,
                   help="explicit container name to exec into (else discover by image)")

    pp = sub.add_parser("prompt-preview", help="generate 4 prompts + check distinctness")
    pp.add_argument("edge_yaml")

    iv = sub.add_parser("intervene", help="run N-agent intervention")
    iv.add_argument("edge_yaml")
    iv.add_argument("--n", type=int, default=1)
    iv.add_argument("--seed", type=int, default=42)
    iv.add_argument("--conditions", default="reset,correct,irrelevant,wrong")

    sm = sub.add_parser("summarize", help="aggregate a run's results")
    sm.add_argument("run_dir")

    al = sub.add_parser("atom-lengths", help="check Phase 3.1 atom length-match controls")
    al.add_argument("task_dir")
    al.add_argument("atoms_file", nargs="?", default="atoms.md")

    vb = sub.add_parser("validate-benchmark", help="build index+graph, validate the full benchmark, report Phase 4 gaps")

    rs = sub.add_parser("run-stream", help="Phase 5: run a stream of tasks in Reset/Stateful mode")
    rs.add_argument("--stream-id", required=True)
    rs.add_argument("--model", required=True)
    rs.add_argument("--condition", required=True, choices=["reset","stateful"])
    rs.add_argument("--seed", type=int, default=42)

    ms = sub.add_parser("make-splits", help="build dev/test/cross_repo/temporal/integrated splits")
    ms.add_argument("--seed", type=int, default=42)

    gs = sub.add_parser("generate-streams", help="build Diagnostic/Integrated task streams from the Experience Graph")
    gs.add_argument("--type", default="diagnostic", choices=["diagnostic", "integrated"])
    gs.add_argument("--motif", default=None, choices=["direct","delayed","fork","join","scope","update","hard_negative"])
    gs.add_argument("--distance", type=int, default=3)
    gs.add_argument("--parent-count", type=int, default=2)
    gs.add_argument("--distractor", type=int, default=0)
    gs.add_argument("--distractor-similarity", default="medium", choices=["high","medium","low"])
    gs.add_argument("--stale", action="store_true")
    gs.add_argument("--wrong", action="store_true")
    gs.add_argument("--missing-parent", action="store_true")
    gs.add_argument("--length", type=int, default=6)
    gs.add_argument("--count", type=int, default=10)
    gs.add_argument("--seed", type=int, default=42)

    args = ap.parse_args()

    if args.cmd == "validate":
        from .validate import cmd_validate
        return cmd_validate(args.task_dir, family=args.family)
    elif args.cmd == "materialize":
        from .materialize import cmd_materialize
        return cmd_materialize(args.task_dir, run_id=args.run_id, container=args.container)
    elif args.cmd == "prompt-preview":
        from .intervene import cmd_prompt_preview
        return cmd_prompt_preview(args.edge_yaml)
    elif args.cmd == "intervene":
        from .intervene import cmd_intervene
        return cmd_intervene(args.edge_yaml, n=args.n, seed=args.seed,
                             conditions=args.conditions.split(","))
    elif args.cmd == "summarize":
        from .summarize import cmd_summarize
        return cmd_summarize(args.run_dir)
    elif args.cmd == "atom-lengths":
        from .atom_lengths import main as al_main
        return al_main(args.task_dir, args.atoms_file)
    elif args.cmd == "validate-benchmark":
        from .validate_benchmark import cmd_validate_benchmark
        return cmd_validate_benchmark()
    elif args.cmd == "run-stream":
        from .run_stream import cmd_run_stream
        return cmd_run_stream(args)
    elif args.cmd == "make-splits":
        from .make_splits import cmd_make_splits
        return cmd_make_splits(args.seed)
    elif args.cmd == "generate-streams":
        from .generate_streams import cmd_generate
        return cmd_generate(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
