"""Near-miss A for viper_unmarshal_exact_merge: derive struct keys but keep AllSettings() source.

The gold UnmarshalExact switches the decode source from v.AllSettings() to
v.getSettings(append(v.AllKeys(), structKeys...)) so env-backed fields populate. This near-miss
keeps the struct-key derivation but decodes from v.AllSettings() — plausible "I added the struct
key step" but env vars are still not consulted -> fields stay zero -> test FAILS.

Distinct from B: A uses the wrong SOURCE (AllSettings); B uses the right source (getSettings) but
drops the struct keys from the lookup set.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_allsettings_source.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = """	// TODO: make this optional?
	structKeys, err := v.decodeStructKeys(rawVal, opts...)
	if err != nil {
		return err
	}

	// TODO: struct keys should be enough?
	return decode(v.getSettings(append(v.AllKeys(), structKeys...)), config)"""

NEW = """	// TODO: make this optional?
	structKeys, err := v.decodeStructKeys(rawVal, opts...)
	if err != nil {
		return err
	}

	// NEAR-MISS A: struct keys derived, but source is still AllSettings() (env not consulted)
	_ = structKeys
	return decode(v.AllSettings(), config)"""


def main():
    p = Path(sys.argv[1]) / "viper.go"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: UnmarshalExact gold block not found (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (AllSettings source, env not consulted) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
