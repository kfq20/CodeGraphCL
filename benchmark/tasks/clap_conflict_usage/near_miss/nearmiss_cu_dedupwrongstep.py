"""Near-miss B for clap conflict_usage: unroll+dedup the conflict STRINGS, not the ids —
so the usage builder still receives raw (un-unrolled) group ids.

The gold unrolls groups and dedups the conflict IDS into a FlatSet, then passes the deduped
ids to build_conflict_err_usage. This near-miss dedups the conflict STRINGS (the rendered
display names) instead — it builds the conflicts vec correctly (deduped strings) but passes
the ORIGINAL raw conflict_ids parameter (with group IDs like "group") to the usage builder.
Plausible "I deduped the conflicts" — but the usage builder reads the IDS, not the strings,
so the group ID "group" doesn't match arg ID "a" → --a stays in usage → FAILS.

Distinct from A: A skips unroll+dedup entirely; B dedups the strings (wasted) but passes raw
ids to the builder. Both fail the same test, different bug location.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_cu_dedupwrongstep.py <repo_dir>
"""
import sys
from pathlib import Path

# gold: `let usg = self.build_conflict_err_usage(matcher, &conflict_ids);` where conflict_ids
# is the deduped vec. Near-miss B: pass the original raw parameter by renaming the deduped
# vec and keeping the original name for the usage builder call.
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
            .into_vec();
        let conflicts = conflict_ids
            .iter()
            .map(|c_id| {
                let c_arg = self.cmd.find(c_id).expect(INTERNAL_ERROR_MSG);
                c_arg.to_string()
            })
            .collect();

        let former_arg = self.cmd.find(name).expect(INTERNAL_ERROR_MSG);
        let usg = self.build_conflict_err_usage(matcher, &conflict_ids);"""
NEW = """        let deduped_ids = conflict_ids
            .iter()
            .flat_map(|c_id| {
                if self.cmd.find_group(c_id).is_some() {
                    self.cmd.unroll_args_in_group(c_id)
                } else {
                    vec![c_id.clone()]
                }
            })
            .collect::<FlatSet<_>>()
            .into_vec();
        let conflicts = deduped_ids
            .iter()
            .map(|c_id| {
                let c_arg = self.cmd.find(c_id).expect(INTERNAL_ERROR_MSG);
                c_arg.to_string()
            })
            .collect();

        let former_arg = self.cmd.find(name).expect(INTERNAL_ERROR_MSG);
        let usg = self.build_conflict_err_usage(matcher, conflict_ids);  // NEAR-MISS B: raw ids"""


def main():
    p = Path(sys.argv[1]) / "clap_builder/src/parser/validator.rs"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: gold block not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (dedup strings not ids, pass raw ids to usage builder) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
