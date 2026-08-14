"""Near-miss A for ripgrep_deadlock_visitor_panic: swallow the join panic — change
handle.join().unwrap() to handle.join().ok(), so the panic from a panicking worker never
propagates to the caller.

The gold propagates the worker panic via handle.join().unwrap() — the unwrap re-panics on the
calling thread, which the #[should_panic] test catches. This near-miss changes unwrap() to ok()
— plausible "I'll handle join errors gracefully instead of crashing" but the #[should_panic]
test expects a panic and now gets none -> the test FAILS (should_panic but did not panic).

Distinct from B: A = swallow the panic (no propagation); B = revert collect-before-spawn
(builder-panic test hangs). Different failure mode (no-panic vs hang).

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_deadlock_no_idlecheck.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = "                handle.join().unwrap();"
NEW = "                handle.join().ok();  // NEAR-MISS A: swallow panic, no propagation"


def main():
    p = Path(sys.argv[1]) / "crates/ignore/src/walk.rs"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: handle.join().unwrap() not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (join().ok() swallows panic — #[should_panic] fails) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
