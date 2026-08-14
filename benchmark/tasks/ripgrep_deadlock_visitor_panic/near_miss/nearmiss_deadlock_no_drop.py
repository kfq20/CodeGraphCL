"""Near-miss B for ripgrep_deadlock_visitor_panic: revert the collect-before-spawn — move Worker
construction back inside the scope as two chained .map() calls (the base pattern), so a
builder.build() panic after the first spawn leaves that worker waiting for partners never created.

The gold collects ALL Worker structs into a Vec BEFORE entering the scope (so a builder.build()
panic happens before any thread is alive and propagates cleanly). This near-miss reverts to the
base pattern: the first .map() constructs the Worker (calling builder.build()), the second .map()
spawns it — so a panic in builder.build() on the 2nd iteration happens AFTER the 1st worker was
already spawned, and the 1st worker waits for a partner that was never created -> the
panic_in_parallel_builder #[should_panic] test HANGS -> `timeout 30` kills it -> rc=124 -> FAIL.

Distinct from A: A = swallow the join panic (#[should_panic] fails: no panic); B = revert
collect-before-spawn (#[should_panic_builder] hangs: partner never created). Different failure
mode, same overall fail.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_deadlock_no_drop.py <repo_dir>
"""
import sys
from pathlib import Path

# The gold pattern: collect workers into a Vec BEFORE the scope, then spawn from the Vec.
# The base pattern: two chained .map() calls INSIDE the scope (construct then spawn).
OLD = """        let workers: Vec<_> = stacks
            .into_iter()
            .map(|stack| Worker {
                visitor: builder.build(),
                stack,
                quit_now: quit_now.clone(),
                active_workers: active_workers.clone(),
                max_depth: self.max_depth,
                min_depth: self.min_depth,
                max_filesize: self.max_filesize,
                follow_links: self.follow_links,
                skip: self.skip.clone(),
                filter: self.filter.clone(),
            })
            .collect();
        std::thread::scope(|s| {
            let handles: Vec<_> = workers
                .into_iter()
                .map(|worker| s.spawn(|| worker.run()))
                .collect();"""
NEW = """        // NEAR-MISS B: reverted to base pattern — construct inside scope, not collected before
        std::thread::scope(|s| {
            let handles: Vec<_> = stacks
                .into_iter()
                .map(|stack| Worker {
                    visitor: builder.build(),
                    stack,
                    quit_now: quit_now.clone(),
                    active_workers: active_workers.clone(),
                    max_depth: self.max_depth,
                    min_depth: self.min_depth,
                    max_filesize: self.max_filesize,
                    follow_links: self.follow_links,
                    skip: self.skip.clone(),
                    filter: self.filter.clone(),
                })
                .map(|worker| s.spawn(|| worker.run()))
                .collect();"""


def main():
    p = Path(sys.argv[1]) / "crates/ignore/src/walk.rs"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: collect-before-spawn block not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (reverted to base spawn pattern — builder-panic hangs) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
