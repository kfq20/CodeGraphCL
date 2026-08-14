"""Near-miss B for clap default_values_if: widen the storage but don't rewrap the old entry point.

The gold fix widens the conditional-default storage to hold a list AND rewraps the value taken
by the pre-existing single-value conditional entry point so it becomes a one-element list. This
near-miss keeps the widened storage and the new list-valued methods but drops the rewrap —
plausible "I only changed the container type, the old method still pushes its one value".

The old entry point now hands a bare single value to a slot that holds a list, so the crate
fails to COMPILE and the test target never runs.

Distinct from near-miss A: B fails at compile time in the builder (type mismatch); A compiles
and fails at runtime in the parser (only one value applied).

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_dv_wrongtype.py <repo_dir>
"""

import sys
from pathlib import Path

REL = "clap_builder/src/builder/arg.rs"

OLD = (
    "            default\n"
    "                .into_resettable()\n"
    "                .into_option()\n"
    "                .map(|os_str| vec![os_str]),\n"
)
NEW = (
    "            // NEAR-MISS B: storage widened to a list, but this value is not rewrapped\n"
    "            default.into_resettable().into_option(),\n"
)


def main():
    p = Path(sys.argv[1]) / REL
    t = p.read_text()
    if t.count(OLD) != 1:
        print(f"near-miss B: gold block count={t.count(OLD)} in {REL} (expected 1)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (single-value entry point not rewrapped -> type mismatch) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
