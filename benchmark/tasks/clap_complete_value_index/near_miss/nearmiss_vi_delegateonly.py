"""Near-miss B for clap_complete_value_index: make the inherent complete_at return empty.

The gold inherent method ArgValueCompleter::complete_at (in custom.rs) delegates
to self.0.complete_at(...), which the dynamic engine calls (complete.rs) to get
candidates. This near-miss changes that inherent method to return an empty vec
instead — plausible reasoning "return empty, let the caller handle it". But the
engine relies on this method to produce candidates, so every position now gets
nothing -> the test's assertions for both slot 0 and slot 1 FAIL.

Distinct from near-miss A: A still returns candidates (the wrong set at slot 1);
B returns no candidates at all (empty set everywhere).

Note: targeting the inherent method (not the trait default) because the test's
completer overrides complete_at on the trait, so the trait default is never
reached — the inherent method is the one on the engine's call path.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_vi_delegateonly.py <repo_dir>
"""
import sys
from pathlib import Path

# Gold-applied custom.rs inherent method body (exactly one occurrence).
OLD = (
    "    pub fn complete_at(&self, arg_index: usize, current: &OsStr) -> Vec<CompletionCandidate> {\n"
    "        self.0.complete_at(arg_index, current)\n"
    "    }"
)
NEW = (
    "    pub fn complete_at(&self, arg_index: usize, current: &OsStr) -> Vec<CompletionCandidate> {\n"
    "        let _ = (arg_index, current);  // NEAR-MISS B: return empty, do not delegate\n"
    "        Vec::new()\n"
    "    }"
)


def main():
    p = Path(sys.argv[1]) / "clap_complete/src/engine/custom.rs"
    t = p.read_text()
    if t.count(OLD) != 1:
        print(f"near-miss B: gold block count={t.count(OLD)}")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (inherent complete_at returns empty vec) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
