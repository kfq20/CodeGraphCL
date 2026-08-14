"""Near-miss A for clap conflict_usage: skip unrolling groups — pass raw conflict_ids to usage.

The gold unrolls group conflict_ids into their member args AND dedups via FlatSet before
passing to build_conflict_err_usage. This near-miss skips the unroll+dedup entirely: collects
the raw conflict_ids (including group IDs like "group") into a Vec and passes THAT to the
usage builder. Plausible "just pass the ids as-is, the builder handles them" — but the
usage builder filters by checking if each present arg is in conflicting_keys; a group ID
like "group" never matches an arg ID like "a", so --a is NOT filtered out and appears in
the usage line → same as base → FAILS.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_cu_nodedup.py <repo_dir>
"""
import sys
from pathlib import Path

# gold: `let conflict_ids = conflict_ids.iter().flat_map(...).collect::<FlatSet<_>>().into_vec();`
# then `let usg = self.build_conflict_err_usage(matcher, &conflict_ids);`
# Near-miss A: replace the FlatSet collect with a simple Vec collect (no unroll of groups,
# no dedup). We change the flat_map to just clone the ids without unrolling.
OLD = """        let conflict_ids = conflict_ids
            .iter()
            .flat_map(|c_id| {
                if self.cmd.find_group(c_id).is_some() {
                    self.cmd.unroll_args_in_group(c_id)
                } else {
                    vec![c_id.clone()]
                }
            })
            .collect::<FlatSet<_>>()
            .into_vec();"""
NEW = """        let conflict_ids = conflict_ids
            .iter()
            .cloned()
            .collect::<Vec<_>>();  // NEAR-MISS A: no unroll, no dedup — raw ids"""


def main():
    p = Path(sys.argv[1]) / "clap_builder/src/parser/validator.rs"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: gold block not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (skip unroll+dedup, pass raw ids to usage builder) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
