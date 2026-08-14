"""Near-miss A for viper_default_decode_hook: method ignores v.decodeHook (always uses default).

The gold defaultDecoderConfig method reads `v.decodeHook` and, if set, uses it as the DecodeHook
(instead of the default composed hook). This near-miss always uses the default composed hook and
ignores `v.decodeHook` — plausible "use the standard hook chain" but the user-supplied custom hook
(string->map) never runs, so the JSON string value is not decoded into a map[string]string ->
test FAILS.

Distinct from B: A reads the wrong thing in the method (ignores the field); B stores the option into
the wrong field in the setter.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_ignore_field.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = """func (v *Viper) defaultDecoderConfig(output any, opts ...DecoderConfigOption) *mapstructure.DecoderConfig {
	decodeHook := v.decodeHook
	if decodeHook == nil {
		decodeHook = mapstructure.ComposeDecodeHookFunc(
			mapstructure.StringToTimeDurationHookFunc(),
			// mapstructure.StringToSliceHookFunc(","),
			stringToWeakSliceHookFunc(","),
		)
	}

	c := &mapstructure.DecoderConfig{
		Metadata:         nil,
		WeaklyTypedInput: true,
		DecodeHook:       decodeHook,
	}"""

NEW = """func (v *Viper) defaultDecoderConfig(output any, opts ...DecoderConfigOption) *mapstructure.DecoderConfig {
	// NEAR-MISS A: ignore v.decodeHook, always use the default composed hook
	decodeHook := mapstructure.ComposeDecodeHookFunc(
		mapstructure.StringToTimeDurationHookFunc(),
		// mapstructure.StringToSliceHookFunc(","),
		stringToWeakSliceHookFunc(","),
	)

	c := &mapstructure.DecoderConfig{
		Metadata:         nil,
		WeaklyTypedInput: true,
		DecodeHook:       decodeHook,
	}"""


def main():
    p = Path(sys.argv[1]) / "viper.go"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: defaultDecoderConfig method body not found (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (method ignores v.decodeHook) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
