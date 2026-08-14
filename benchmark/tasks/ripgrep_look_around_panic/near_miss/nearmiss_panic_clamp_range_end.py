"""Near-miss A for ripgrep_look_around_panic: clamp end to range.end (not bytes.len()) when
last_match > range.end — so the slice bytes[last_match..end] still inverts (end < last_match)
and still panics.

The gold: end = if last_match > range.end { bytes.len() } else { min(bytes.len(), range.end) }.
This near-miss uses end = range.end unconditionally — plausible "I'll just use range.end as the
end" but when last_match > range.end the slice bytes[last_match..range.end] still has
end < last_match -> panics. The test (which triggers exactly this case) still panics -> FAILS.

Distinct from B: A = wrong clamp target (range.end, still inverts); B = no clamp at all (base).
Different residual, same panic.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_panic_clamp_range_end.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = """    let end = if last_match > range.end {
        bytes.len()
    } else {
        std::cmp::min(bytes.len(), range.end)
    };"""
NEW = """    let end = std::cmp::min(bytes.len(), range.end);  // NEAR-MISS A: no overshoot clamp, still inverts"""


def main():
    p = Path(sys.argv[1]) / "crates/printer/src/util.rs"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: overshoot clamp not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (clamp to range.end — still inverts) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
