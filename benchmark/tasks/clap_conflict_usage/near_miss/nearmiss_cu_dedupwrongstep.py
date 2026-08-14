"""Near-miss B for clap conflict_usage: dedup the conflict STRINGS, not the conflict IDS — so
the usage builder still receives duplicate ids.

The gold dedups conflict_ids (the ids) into a FlatSet BEFORE mapping to strings and passing
to the usage builder. This near-miss dedups AFTER mapping to strings (collect the string vec,
then dedup the strings) but still passes the raw (un-deduped) conflict_ids to
build_conflict_err_usage. Plausible "I deduped the output" — but the usage builder reads the
ids, not the strings, so duplicates persist in the usage line. Caught.

Distinct from A: A passes raw ids with NO dedup anywhere; B dedups the strings (wasted) but
still passes raw ids to the builder. Both fail the same test, different bug location.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_cu_dedupwrongstep.py <repo_dir>
"""
import sys
from pathlib import Path

# gold: `let conflict_ids = conflict_ids.collect::<FlatSet<_>>().into_vec();` then passes
# &conflict_ids (deduped). Near-miss B: collect into a Vec (no FlatSet dedup) so the ids stay
# duplicated, but still build the conflicts string vec (looks done).
OLD = "        let conflict_ids = conflict_ids\n            .collect::<FlatSet<_>>()\n            .into_vec();\n"
NEW = "        let conflict_ids = conflict_ids\n            .collect::<Vec<_>>();  // NEAR-MISS B: Vec, no FlatSet dedup\n"


def main():
    p = Path(sys.argv[1]) / "clap_builder/src/parser/validator.rs"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: FlatSet collect not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (collect into Vec not FlatSet — no id dedup) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
