"""Near-miss A for ripgrep_crlf_preserve_terminator: append a hard-coded CRLF (b"\\r\\n") instead
of the actual trimmed terminator slice.

The gold re-appends the slice returned by trim_line_terminator (which is the ACTUAL terminator
that was removed — could be \\r\\n, \\n, or empty). This near-miss hard-codes b"\\r\\n" —
plausible "I know it's CRLF mode so I'll put \\r\\n back" but wrong for non-CRLF lines and
wrong for lines that had no terminator. The test's first sub-case (no replacement) still passes
(it doesn't use the replace path), but the second sub-case (with replacement) gets a hard-coded
\\r\\n appended even when the line had one — actually that coincidentally matches for the CRLF
test case. So instead, make it append b"\\n" (wrong terminator) — the CRLF test expects \\r\\n
and gets \\n -> assertion FAILS.

Distinct from B: A = wrong value (hardcoded \\n); B = wrong condition (append unconditionally
even when none was trimmed, which for the CRLF test coincidentally still appends \\r\\n — so B
must append a WRONG value unconditionally to fail). Here A appends the wrong terminator value.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_crlf_wrong_term.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = "    dst.extend(line_terminator);"
NEW = "    dst.extend(b\"\\n\");  // NEAR-MISS A: hard-coded \\n instead of the real terminator"


def main():
    p = Path(sys.argv[1]) / "crates/printer/src/util.rs"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: dst.extend(line_terminator) not found (is gold applied?)"); return 1
    # Only replace in replace_with_captures_in_context (the second occurrence; the first is in
    # the closure). Find the LAST occurrence (the one after the trailing slice extend).
    idx = t.rfind(OLD)
    if idx == -1:
        print("near-miss A: could not locate occurrence"); return 1
    p.write_text(t[:idx] + NEW + t[idx+len(OLD):])
    print("near-miss A (hard-coded \\n instead of real terminator) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
