"""Near-miss B for viper_config_notfound_error: guard the wrong branch (present), not absent.

The gold ReadInConfig returns ConfigFileNotFoundError when `!exists`. This near-miss inverts the
guard to return the error when the file DOES exist (`if exists`) — plausible "guard the existence
check" but backwards: when the file is absent, the guard does not fire and execution falls through to
afero.ReadFile, which returns the raw path error (not a ConfigFileNotFoundError). The test asserts
`assert.IsType(ConfigFileNotFoundError{...}, err)`, so the raw path error fails the type check ->
test FAILS.

Distinct from A: B leaves the absent branch to fall through (wrong branch guarded); A returns the
wrong type on the correct (absent) branch.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_inverted_guard.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = """	exists, err := afero.Exists(v.fs, filename)
	if err != nil {
		return err
	}
	if !exists {
		return ConfigFileNotFoundError{name: filename, locations: ""}
	}"""

NEW = """	exists, err := afero.Exists(v.fs, filename)
	if err != nil {
		return err
	}
	// NEAR-MISS B: inverted guard — fires when file EXISTS, absent falls through to read error
	if exists {
		return ConfigFileNotFoundError{name: filename, locations: ""}
	}"""


def main():
    p = Path(sys.argv[1]) / "viper.go"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: afero.Exists block not found (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (inverted guard, absent falls through) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
