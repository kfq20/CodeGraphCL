"""Near-miss B for viper_default_decode_hook: WithDecodeHook nil-guard is inverted.

The gold WithDecodeHook setter guards `if h == nil { return }` so a non-nil hook is stored into
v.decodeHook. This near-miss inverts the guard to `if h != nil { return }` — plausible "guard
against storing" but backwards: a non-nil hook returns early and is never stored, so v.decodeHook
stays nil, defaultDecoderConfig falls back to the default composed hook, and the user-supplied
custom hook (string->map) never runs -> the JSON string value is not decoded into a
map[string]string -> test FAILS.

Distinct from A: B is a wrong guard in the SETTER (hook never stored); A ignores the field in the
METHOD (hook stored but never read).

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_wrong_store.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = """// WithDecodeHook sets a default decode hook for mapstructure.
func WithDecodeHook(h mapstructure.DecodeHookFunc) Option {
	return optionFunc(func(v *Viper) {
		if h == nil {
			return
		}

		v.decodeHook = h
	})
}"""

NEW = """// WithDecodeHook sets a default decode hook for mapstructure.
func WithDecodeHook(h mapstructure.DecodeHookFunc) Option {
	return optionFunc(func(v *Viper) {
		// NEAR-MISS B: inverted nil-guard — non-nil hook returns early, never stored
		if h != nil {
			return
		}

		v.decodeHook = h
	})
}"""


def main():
    p = Path(sys.argv[1]) / "viper.go"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: WithDecodeHook setter not found (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (inverted nil-guard, hook never stored) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
