"""Near-miss A for clap_help_short_padding: keep the old filter-based logic.

The gold fix removes the `longest_filter` function and changes the padding condition to check
`arg.get_long().is_some()` (without the filter guard). This near-miss reverts both changes —
re-adds the filter function and restores the old filter-guarded padding block. Plausible
reasoning: "the filter was there for a reason, I'll keep it and just fix the test". But the
padding is still wrong for short-only value args (the filter adds SHORT_SIZE for non-positional
short-only args) -> snapshot mismatch on short_with_value -> FAIL.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_sp_nofilter.py <repo_dir>
"""
import sys
from pathlib import Path

# Replacement 1: revert the padding block to the old filter-guarded logic
OLD1 = """            let width = display_width(&arg.to_string());
            let actual_width = if arg.get_long().is_some() {
                width + SHORT_SIZE
            } else {
                width
            };
            longest = longest.max(actual_width);
            debug!(
                "HelpTemplate::write_args: arg={:?} longest={}",
                arg.get_id(),
                longest
            );"""

NEW1 = """            if longest_filter(arg) {  // NEAR-MISS A: keep old filter-based logic
                let width = display_width(&arg.to_string());
                let actual_width = if arg.is_positional() {
                    width
                } else {
                    width + SHORT_SIZE
                };
                longest = longest.max(actual_width);
                debug!(
                    "HelpTemplate::write_args: arg={:?} longest={}",
                    arg.get_id(),
                    longest
                );
            }"""

# Replacement 2: re-add the longest_filter function (removed by gold)
OLD2 = """fn should_show_subcommand(subcommand: &Command) -> bool {
    !subcommand.is_hide_set()
}

#[cfg(test)]"""

NEW2 = """fn should_show_subcommand(subcommand: &Command) -> bool {
    !subcommand.is_hide_set()
}

fn longest_filter(arg: &Arg) -> bool {
    arg.is_takes_value_set() || arg.get_long().is_some() || arg.get_short().is_none()
}

#[cfg(test)]"""


def main():
    p = Path(sys.argv[1]) / "clap_builder/src/output/help_template.rs"
    t = p.read_text()
    if t.count(OLD1) != 1:
        print(f"near-miss A: OLD1 count={t.count(OLD1)}"); return 1
    t = t.replace(OLD1, NEW1, 1)
    if t.count(OLD2) != 1:
        print(f"near-miss A: OLD2 count={t.count(OLD2)}"); return 1
    t = t.replace(OLD2, NEW2, 1)
    p.write_text(t)
    print("near-miss A (keep old filter-based logic, re-add longest_filter) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
