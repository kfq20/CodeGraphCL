"""Near-miss B for clap type-alias codegen: qualified but via a relative path.

A plausible-but-wrong attempt: instead of the bare single-word form, this near-miss qualifies
the type as `std::result::Result` (relative path, no leading `::`). The reasoning is sound in
spirit ("name the stdlib result explicitly") and reads like a careful fix — but without the
leading `::`, the path `std::...` is resolved relative to the current crate/scope first. For a
user whose crate or module exposes a `std` item, the relative path still resolves to the wrong
thing; more importantly, the leading-`::` absolute-path form is what robustly defeats alias
shadowing at the use site. The single-word alias here still wins for the bare symbol, and the
relative `std::result::Result` form is not what the gold commit settled on.

In practice for THIS test the relative path happens to also resolve (no `std` alias), so this
near-miss is the weaker of the two — but it is the canonical "qualified wrong" mistake (missing
leading `::`), and the verifier catches it whenever a shadow is actually in play.

Runs on HOST. near_miss_base: gold (operates on gold-applied code).
Usage: python3 nearmiss_clap_ta_localpath.py <repo_dir>
"""
import sys
from pathlib import Path

QUALIFIED = ('.map(|v| v.map::<::std::result::Result<#convert_type, clap::Error>, _>(#parse)'
             '.collect::<::std::result::Result<Vec<_>, clap::Error>>())')
# drop the leading :: on both occurrences -> relative std path (the canonical "qualified wrong")
REL = ('.map(|v| v.map::<std::result::Result<#convert_type, clap::Error>, _>(#parse)'
       '.collect::<std::result::Result<Vec<_>, clap::Error>>())  // NEAR-MISS B: relative path')


def main():
    p = Path(sys.argv[1]) / "clap_derive/src/derives/args.rs"
    t = p.read_text()
    if t.count(QUALIFIED) < 2:
        print("near-miss B: expected 2 qualified sites (is gold applied?)"); return 1
    p.write_text(t.replace(QUALIFIED, REL))
    print("near-miss B (qualified via relative std:: path, no leading ::) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
