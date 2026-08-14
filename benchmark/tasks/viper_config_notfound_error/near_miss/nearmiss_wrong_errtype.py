"""Near-miss A for viper_config_notfound_error: return a generic error instead of ConfigFileNotFoundError.

The gold ReadInConfig checks afero.Exists and returns `ConfigFileNotFoundError{name: filename,
locations: ""}` when the file is absent. This near-miss returns a generic `fmt.Errorf` instead —
plausible "return a not-found error" but the wrong concrete type. The test asserts
`assert.IsType(ConfigFileNotFoundError{...}, err)`, so a generic error fails the type check ->
test FAILS.

Distinct from B: A returns the wrong TYPE on the absent branch; B checks existence but guards the
wrong branch (present), leaving the absent branch to fall through to the raw read error.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_wrong_errtype.py <repo_dir>
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
	if !exists {
		// NEAR-MISS A: generic error, not ConfigFileNotFoundError
		return fmt.Errorf("config file not found: %s", filename)
	}"""


def main():
    p = Path(sys.argv[1]) / "viper.go"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: afero.Exists block not found (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (generic error instead of ConfigFileNotFoundError) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
