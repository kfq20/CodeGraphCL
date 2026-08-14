"""Near-miss B for clap_help_bracket_values: bracket ALL value names as optional.

The gold brackets only value names past the minimum (is_past_min = min_vals <= n, combined
with !is_optional_val for non-positional). This near-miss brackets ALL value names — a
plausible over-generalization: "if some values are optional, make them all optional." But
the test expects <FOO> [BAR] (first required); this produces [FOO] [BAR] -> snapshot
mismatch -> FAILS.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_bv_all.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = "            let is_optional = if self.is_positional() {\n                !required || is_past_min\n            } else {\n                // The caller already brackets an optional value; avoid `[[name]]`\n                !is_optional_val && is_past_min\n            };"
NEW = "            let is_optional = if self.is_positional() {\n                !required || is_past_min\n            } else {\n                // NEAR-MISS B: bracket all values, not just past-min\n                true\n            };"


def main():
    p = Path(sys.argv[1]) / "clap_builder/src/builder/arg.rs"
    t = p.read_text()
    if t.count(OLD) != 1:
        print(f"near-miss B: gold block count={t.count(OLD)}"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (bracket all values as optional) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
