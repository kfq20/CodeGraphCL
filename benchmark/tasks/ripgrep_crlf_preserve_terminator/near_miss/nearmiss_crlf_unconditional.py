"""Near-miss B for ripgrep_crlf_preserve_terminator: make trim_line_terminator return an empty
slice even when it DID trim a terminator (so the re-append in the replace path appends nothing).

The gold makes trim_line_terminator RETURN the removed terminator slice (&buf[end..orig_end]),
which the Replacer re-appends. This near-miss changes the return to always &[] (empty) —
plausible "I trimmed it, so I'll return empty / the trim is done" but the caller needs the actual
slice to re-append. With an empty return, dst.extend(line_terminator) appends nothing, so the
output is "hello\\nworld" (no \\r\\n) -> the assertion FAILS.

Distinct from A: A corrupts the CONSUMER (hardcodes the wrong value \\n in the extend call); B
corrupts the PRODUCER (returns empty from trim). Both leave the terminator missing, but at
different layers.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_crlf_unconditional.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = """        let orig_end = line.end();
        *line = line.with_end(end);
        &buf[end..orig_end]
    } else {
        &[]"""
NEW = """        let orig_end = line.end();
        *line = line.with_end(end);
        &[]  // NEAR-MISS B: return empty instead of &buf[end..orig_end]
    } else {
        &[]"""


def main():
    p = Path(sys.argv[1]) / "crates/printer/src/util.rs"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: trim_line_terminator return block not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (trim returns empty — terminator lost) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
