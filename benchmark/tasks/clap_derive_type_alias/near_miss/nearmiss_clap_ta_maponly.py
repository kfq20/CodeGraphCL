"""Near-miss B for clap type-alias codegen: qualified the collect, missed the map.

A plausible-but-incomplete attempt: each generated parser line references the stdlib result
type TWICE — once as the map turbofish and once as the collect turbofish. This near-miss
qualifies the collect reference at both arms (OptionVec and Vec) but leaves the map turbofish
bare.

It looks like a real fix (both arms touched, the collect — the more visible one — correctly
qualified) but the bare map turbofish is still shadowed by the user's single-word alias, so
the derive test binary again fails to compile.

Distinct from near-miss A: A fixes one ARM and misses the other; B fixes one REFERENCE KIND
in both arms and misses the other kind.

Runs on HOST. near_miss_base: gold (operates on gold-applied code).
Usage: python3 nearmiss_clap_ta_maponly.py <repo_dir>
"""
import sys
from pathlib import Path

QUALIFIED = ('.map(|v| v.map::<::std::result::Result<#convert_type, clap::Error>, _>(#parse)'
             '.collect::<::std::result::Result<Vec<_>, clap::Error>>())')
# keep collect qualified, revert the map turbofish to the bare single-word form
MAP_BARE = ('.map(|v| v.map::<Result<#convert_type, clap::Error>, _>(#parse)'
            '.collect::<::std::result::Result<Vec<_>, clap::Error>>())  // NEAR-MISS B: map turbofish left bare')


def main():
    p = Path(sys.argv[1]) / "clap_derive/src/derives/args.rs"
    t = p.read_text()
    if t.count(QUALIFIED) < 2:
        print("near-miss B: expected 2 qualified sites (is gold applied?)"); return 1
    p.write_text(t.replace(QUALIFIED, MAP_BARE))
    print("near-miss B (collect qualified, map turbofish left bare) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
