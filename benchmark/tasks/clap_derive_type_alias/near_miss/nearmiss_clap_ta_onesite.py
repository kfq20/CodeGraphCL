"""Near-miss A for clap type-alias codegen: fixed only the Option-Vec site.

A plausible-but-incomplete attempt: the gold fix qualifies the stdlib result type at BOTH
generated-parser sites (Ty::OptionVec and Ty::Vec). This near-miss keeps the qualification at
the OptionVec site but reverts the plain Vec site to the bare single-word form.

It looks like a real fix (one site correctly qualified) but the test struct has a plain
`Vec<String>` field, so the reverted site still emits a bare reference that the test's alias
shadows -> the derive test binary again fails to compile.

Runs on HOST (rust:slim has no python3). near_miss_base: gold (operates on gold-applied code).
Usage: python3 nearmiss_clap_ta_onesite.py <repo_dir>
"""
import sys
from pathlib import Path

QUALIFIED = ('.map(|v| v.map::<::std::result::Result<#convert_type, clap::Error>, _>(#parse)'
             '.collect::<::std::result::Result<Vec<_>, clap::Error>>())')
BARE = ('.map(|v| v.map::<Result<#convert_type, clap::Error>, _>(#parse)'
        '.collect::<Result<Vec<_>, clap::Error>>())  // NEAR-MISS A: Vec site left unqualified')


def main():
    p = Path(sys.argv[1]) / "clap_derive/src/derives/args.rs"
    t = p.read_text()
    n = t.count(QUALIFIED)
    if n < 2:
        print(f"near-miss A: expected 2 qualified sites, found {n} (is gold applied?)"); return 1
    # revert only the SECOND occurrence (the Ty::Vec arm; OptionVec comes first in the file)
    head, sep, tail = t.rpartition(QUALIFIED)
    p.write_text(head + BARE + tail)
    print("near-miss A (only OptionVec site qualified; Vec site reverted) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
