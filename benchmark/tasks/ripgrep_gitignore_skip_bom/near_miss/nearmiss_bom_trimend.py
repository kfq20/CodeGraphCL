"""Near-miss A for ripgrep gitignore_skip_bom: strip the BOM from the END of the first line,
not the start.

The gold strips the BOM from the START (trim_start_matches) on i==0. This near-miss strips from
the END (trim_end_matches) — plausible "I'll trim the BOM" but wrong end. The BOM is at the
start, so trimming the end leaves it -> the first-line pattern still doesn't match -> caught.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_bom_trimend.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = "            let line =\n                if i == 0 { line.trim_start_matches(UTF8_BOM) } else { &line };"
NEW = "            let line =\n                if i == 0 { line.trim_end_matches(UTF8_BOM) } else { &line };  // NEAR-MISS A: trim end, not start"


def main():
    p = Path(sys.argv[1]) / "crates/ignore/src/gitignore.rs"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: BOM trim line not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (trim_end instead of trim_start) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
