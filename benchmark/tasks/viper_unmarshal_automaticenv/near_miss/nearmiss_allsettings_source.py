"""Near-miss A for viper_unmarshal_automaticenv: derive struct keys but keep AllSettings() source.

The gold Unmarshal switches the decode source from v.AllSettings() to
v.getSettings(append(v.AllKeys(), structKeys...)) so that environment variables (consulted by
getSettings for struct-field keys) are surfaced when AutomaticEnv is on. This near-miss keeps the
struct-key derivation but still decodes from v.AllSettings() — plausible "I added the struct key
step" but the source still ignores env vars -> the env-backed fields stay zero -> test FAILS.

Distinct from B: A uses the wrong SOURCE (AllSettings); B uses the right source (getSettings) but
drops the struct keys from the lookup set.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_allsettings_source.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = """	structKeys, err := v.decodeStructKeys(rawVal, opts...)
	if err != nil {
		return err
	}

	// TODO: struct keys should be enough?
	return decode(v.getSettings(append(v.AllKeys(), structKeys...)), defaultDecoderConfig(rawVal, opts...))"""

NEW = """	structKeys, err := v.decodeStructKeys(rawVal, opts...)
	if err != nil {
		return err
	}

	// NEAR-MISS A: struct keys derived, but source is still AllSettings() (env not consulted)
	_ = structKeys
	return decode(v.AllSettings(), defaultDecoderConfig(rawVal, opts...))"""


def main():
    p = Path(sys.argv[1]) / "viper.go"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: Unmarshal gold block not found (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (AllSettings source, env not consulted) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
