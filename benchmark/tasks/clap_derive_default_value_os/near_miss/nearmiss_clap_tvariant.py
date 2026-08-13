"""Near-miss B for clap default_value_os: the "matched the wrong sibling" fix.

A plausible-but-wrong attempt: the gold helper matches `default_value` and `default_value_os`.
clap's derive actually has THREE default forms — `default_value` (str), `default_value_os`
(os str), and `default_value_t` (typed, `#[clap(default_value_t = ...)]`). This near-miss
"fixes the consistency" by matching the pair {default_value, default_value_t} instead of
{default_value, default_value_os} — a genuinely plausible confusion (the _t and _os suffixes
are easy to mix up, and default_value_t is the more commonly used form in examples).

The test uses `default_value_os`, which this helper does NOT match, so the arg stays
required and debug_assert panics — caught.

Runs on HOST. near_miss_base: gold (operates on gold-applied code).
Usage: python3 nearmiss_clap_tvariant.py <repo_dir>
"""
import sys
from pathlib import Path


def main():
    attrs = Path(sys.argv[1]) / "clap_derive/src/attrs.rs"
    t = attrs.read_text()
    # the gold helper matches default_value OR default_value_os; swap _os for _t
    old = ('.find(|m| m.name == "default_value" || m.name == "default_value_os")')
    new = ('.find(|m| m.name == "default_value" || m.name == "default_value_t")  // NEAR-MISS B: wrong sibling')
    if old not in t:
        print("near-miss B: gold find_default_method body not found (is gold applied?)"); return 1
    attrs.write_text(t.replace(old, new))
    print("near-miss B (helper matches default_value_t, not _os) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
