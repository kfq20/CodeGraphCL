"""Near-miss B for ripgrep gitignore_skip_bom: off-by-one — strip the BOM on i==1, not i==0.

The gold strips on i==0 (first line). This near-miss strips on i==1 (second line) — a real
off-by-one mistake. The BOM is on the first line, so stripping the second leaves the first-line
BOM intact -> the first-line pattern doesn't match -> caught.

Distinct from A: A strips the wrong END (end vs start); B strips the wrong LINE (i==1 vs i==0).
Different bug location, same end failure.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_bom_offbyone.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = "            let line =\n                if i == 0 { line.trim_start_matches(UTF8_BOM) } else { &line };"
NEW = "            let line =\n                if i == 1 { line.trim_start_matches(UTF8_BOM) } else { &line };  // NEAR-MISS B: off-by-one (i==1 not i==0)"


def main():
    p = Path(sys.argv[1]) / "crates/ignore/src/gitignore.rs"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: BOM trim line not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (off-by-one: strip on i==1 not i==0) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
