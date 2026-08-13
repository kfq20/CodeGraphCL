"""Near-miss A for clap default_value_os: the "helper-but-not-at-required-site" fix.

A plausible-but-incomplete attempt: the gold commit introduces `find_default_method` (matches
both default_value and default_value_os) and uses it at THREE sites. This near-miss keeps the
helper AND keeps it at the two diagnostic guards (bool/Option in attrs.rs), but reverts the
`required` computation in args.rs (gen_augment) back to the old `has_method("default_value")`.

It looks like a real fix (helper present, two of three sites updated) but the test still
panics: the required-path was never taught about default_value_os, so the defaulted arg
stays required and debug_assert fails ("required and can't have a default value").

Runs on HOST (rust:slim has no python3). near_miss_base: gold (operates on gold-applied code).
Usage: python3 nearmiss_clap_guardonly.py <repo_dir>
"""
import sys
from pathlib import Path


def main():
    args = Path(sys.argv[1]) / "clap_derive/src/derives/args.rs"
    a = args.read_text()
    old = 'let required = attrs.find_default_method().is_none() && !override_required;'
    new = ('let required = !attrs.has_method("default_value") && !override_required; '
           ' // NEAR-MISS A: reverted required-path to old has_method')
    if old not in a:
        print("near-miss A: args.rs gold required-site not found (is gold applied?)"); return 1
    args.write_text(a.replace(old, new))
    print("near-miss A (helper kept, required-path reverted to has_method) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
