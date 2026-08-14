"""Near-miss A for clap default_values_if: apply only the FIRST conditional default value.

The gold fix stores a list of conditional default values and the parser feeds every one of
them into the matches. This near-miss keeps the widened storage (so it still compiles) but has
the parser take only the first entry — plausible "a conditional default is still one value,
I just need to unwrap the new container", which is exactly the shape of the pre-existing code.

The test configures an argument that takes two values with a conditional default of
["df1", "df2"]; with only one value applied the two-value expectation is not met, so the test
fails at RUNTIME.

Distinct from near-miss B: A compiles and fails at runtime (wrong number of values applied);
B fails at compile time (type mismatch in the builder).

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_dv_single.py <repo_dir>
"""

import sys
from pathlib import Path

REL = "clap_builder/src/parser/parser.rs"

OLD = (
    "                            let arg_values =\n"
    "                                default.iter().map(|os_str| os_str.to_os_string()).collect();\n"
)
NEW = (
    "                            // NEAR-MISS A: only the first conditional default is applied\n"
    "                            let arg_values = vec![default.first().unwrap().to_os_string()];\n"
)


def main():
    p = Path(sys.argv[1]) / REL
    t = p.read_text()
    if t.count(OLD) != 1:
        print(f"near-miss A: gold block count={t.count(OLD)} in {REL} (expected 1)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (only first conditional default applied) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
