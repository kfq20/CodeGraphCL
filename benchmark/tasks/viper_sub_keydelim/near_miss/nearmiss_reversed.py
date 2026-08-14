"""Near-miss B for viper_sub_keydelim: copy keyDelim in the reversed direction.

The gold Sub() adds `subv.keyDelim = v.keyDelim` (parent -> sub). This near-miss reverses the
assignment to `v.keyDelim = subv.keyDelim` (sub -> parent) — plausible "set the key delimiter"
but backwards: it overwrites the PARENT's delimiter with the (empty) sub-viper's default instead
of copying the parent's delimiter into the sub-viper. subv.keyDelim stays empty -> test FAILS.

Distinct from A: B assigns in the wrong direction; A copies a wrong field.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_reversed.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = "subv.keyDelim = v.keyDelim"

NEW = "v.keyDelim = subv.keyDelim  # NEAR-MISS B: reversed assignment direction"


def main():
    p = Path(sys.argv[1]) / "viper.go"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: keyDelim copy line not found (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (reversed assignment direction) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
