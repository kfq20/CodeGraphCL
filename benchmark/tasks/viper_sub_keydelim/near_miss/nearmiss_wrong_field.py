"""Near-miss A for viper_sub_keydelim: copy a different parent field instead of keyDelim.

The gold Sub() adds `subv.keyDelim = v.keyDelim` so the sub-viper honors the custom "::" delimiter.
This near-miss copies a different parent field (configName) instead — plausible "copy a parent
attribute into the sub-viper" but the wrong one. subv.keyDelim stays empty (the default "."),
so `subv.Get("steve@hacker.com::created")` returns nil -> test FAILS.

Distinct from B: A copies a wrong field; B assigns in the wrong direction (overwrites the parent).

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_wrong_field.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = "subv.keyDelim = v.keyDelim"

NEW = "subv.configName = v.configName  # NEAR-MISS A: wrong field copied"


def main():
    p = Path(sys.argv[1]) / "viper.go"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: keyDelim copy line not found (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (wrong field copied instead of keyDelim) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
