"""Near-miss A for clap conflict_usage: don't dedup — pass raw conflict_ids to the usage builder.

The gold collects conflict_ids into a FlatSet (dedup) THEN passes the deduped &conflict_ids to
build_conflict_err_usage. This near-miss skips the FlatSet collect — passes the raw conflict_ids
iterator to the usage builder. Plausible "the builder will handle uniqueness" — but the builder
iterates raw, so duplicates appear in the usage string. Same as base. Caught.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_cu_nodedup.py <repo_dir>
"""
import sys
from pathlib import Path

# gold passes &conflict_ids (the FlatSet's into_vec). Near-miss A: pass the raw iterator (revert
# to building conflicts without dedup, and pass raw conflict_ids to the usage builder).
OLD = ("        let usg = self.build_conflict_err_usage(matcher, &conflict_ids);\n")
NEW = ("        let usg = self.build_conflict_err_usage(matcher, conflict_ids.as_slice());  // NEAR-MISS A: raw, no dedup\n")


def main():
    p = Path(sys.argv[1]) / "clap_builder/src/parser/validator.rs"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: build_conflict_err_usage call not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (pass raw conflict_ids to usage builder, no dedup) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
