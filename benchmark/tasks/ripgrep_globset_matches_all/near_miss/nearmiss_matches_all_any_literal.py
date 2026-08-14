"""Near-miss A for ripgrep_globset_matches_all: in matches_all_candidate, revert to calling
strat.is_match (the any-match check) instead of strat.matches_all.

The gold calls strat.matches_all(path) in matches_all_candidate (the per-strategy all-match
check). This near-miss reverts to strat.is_match(path) — plausible "matches_all = every strategy
bucket has a match" but it's the original bug: two distinct globs in the same literal bucket
still fool it into reporting all-matched when only one matches. The test
matches_all_literals ({abc,def}, !matches_all("abc")) FAILS.

Distinct from B: A = wrong call at the candidate level (is_match); B = wrong per-strategy
impl (count). Different residual.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_matches_all_any_literal.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = "            if !strat.matches_all(path) {"
NEW = "            if !strat.is_match(path) {  // NEAR-MISS A: any-match instead of all-match"


def main():
    p = Path(sys.argv[1]) / "crates/globset/src/lib.rs"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: matches_all_candidate call not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (is_match instead of matches_all in candidate) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
