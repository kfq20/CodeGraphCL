"""Near-miss B for ripgrep_look_around_panic: invert the clamp condition — use bytes.len() when
last_match <= range.end (the NORMAL case) and range.end when last_match > range.end (the
overshoot case). This re-introduces the panic.

The gold: end = if last_match > range.end { bytes.len() } else { min(bytes.len(), range.end) }.
This near-miss swaps the arms: end = if last_match > range.end { range.end } else { bytes.len() }
— plausible "I flipped the polarity" but the overshoot case now uses range.end (< last_match) ->
the slice bytes[last_match..range.end] still inverts -> panics. AND the normal case now uses
bytes.len() which appends too much trailing data (wrong output). The test panics on the overshoot
case -> FAILS.

Distinct from A: A = removes the clamp entirely (uses range.end always); B = inverts the arms
(uses range.end in the overshoot case specifically). Different residual, same panic.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_panic_no_clamp.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = """    let end = if last_match > range.end {
        bytes.len()
    } else {
        std::cmp::min(bytes.len(), range.end)
    };"""
NEW = """    let end = if last_match > range.end {
        std::cmp::min(bytes.len(), range.end)  // NEAR-MISS B: arms inverted — overshoot case still inverts
    } else {
        bytes.len()
    };"""


def main():
    p = Path(sys.argv[1]) / "crates/printer/src/util.rs"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: overshoot clamp not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (arms inverted — overshoot case still inverts) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
