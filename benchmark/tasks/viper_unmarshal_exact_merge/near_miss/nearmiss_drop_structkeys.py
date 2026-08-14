"""Near-miss B for viper_unmarshal_exact_merge: getSettings source but drop the struct keys.

The gold UnmarshalExact feeds `append(v.AllKeys(), structKeys...)` into getSettings. This near-miss
calls getSettings with only AllKeys() (dropping structKeys) — plausible "use getSettings (env-aware)
and the existing keys" but the struct-derived keys are missing -> env vars shadowed by struct-field
names are not consulted -> test FAILS.

Distinct from A: B uses the right SOURCE (getSettings) but drops the struct keys; A uses the wrong
source (AllSettings) but keeps the derivation step.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_drop_structkeys.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = """	return decode(v.getSettings(append(v.AllKeys(), structKeys...)), config)"""

NEW = """	// NEAR-MISS B: getSettings source, but structKeys dropped from the lookup set
	return decode(v.getSettings(v.AllKeys()), config)"""


def main():
    p = Path(sys.argv[1]) / "viper.go"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: getSettings(append(...)) line not found (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (structKeys dropped from getSettings) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
