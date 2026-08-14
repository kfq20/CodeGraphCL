"""Near-miss B for ripgrep_globset_matches_all: in the LiteralStrategy matches_all, use is_match
only (drop the len==1 guard) — so a 2-glob literal bucket reports all-matched when ANY of its
globs matches.

The gold: LiteralStrategy::matches_all = self.0.len() == 1 && self.is_match(candidate) (a
multi-glob bucket can never have all its globs be the same single path). This near-miss drops the
len==1 guard: matches_all = self.is_match(candidate) — plausible "if the path is in the literal
map, it matches" but for {abc,def} both are in the same LiteralStrategy bucket, and is_match
returns true for "abc" (it's a key) -> matches_all reports true -> the test's
!matches_all("abc") FAILS. Same for BasenameLiteral and Extension.

Distinct from A: A = wrong call at the candidate level (is_match); B = wrong per-strategy impl
(drop the len guard). Different residual.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_matches_all_count_only.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = """    fn matches_all(&self, candidate: &Candidate<'_>) -> bool {
        self.0.len() == 1 && self.is_match(candidate)
    }

    #[inline(never)]
    fn matches_into(
        &self,
        candidate: &Candidate<'_>,
        matches: &mut Vec<usize>,
    ) {
        let patset = self.find_matches(candidate);
        for i in patset.iter() {
            matches.push(self.map[i]);
        }"""

# We target the LAST of the three identical len==1 guards (ExtensionStrategy) — but all three
# are identical, so we replace_all on the single-line guard instead.
GUARD_OLD = "        self.0.len() == 1 && self.is_match(candidate)"
GUARD_NEW = "        self.is_match(candidate)  // NEAR-MISS B: len==1 guard dropped"


def main():
    p = Path(sys.argv[1]) / "crates/globset/src/lib.rs"
    t = p.read_text()
    if GUARD_OLD not in t:
        print("near-miss B: len==1 guard not found (is gold applied?)"); return 1
    count = t.count(GUARD_OLD)
    p.write_text(t.replace(GUARD_OLD, GUARD_NEW))  # replace all 3 (Literal/Basename/Extension)
    print(f"near-miss B (len==1 guard dropped on {count} literal strategies) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
