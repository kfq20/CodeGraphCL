"""Near-miss A for httpx_json_encoding_detection: only BOM detection, no null-byte heuristic.

The gold guess_json_utf() checks BOM patterns first, then uses a null-byte count heuristic to
detect non-BOM utf-16/32 content. This near-miss keeps only the BOM checks and removes the
null-byte logic. Plausible "BOM is the standard encoding-detection approach" — but non-BOM
content (the common case) returns None, and json() falls back to .text which fails on
non-utf-8 content without a charset header. Caught: test_json_without_specified_encoding (utf-32-be
content, no charset) falls back to utf-8 decode -> UnicodeDecodeError.

Distinct from B: A fails on non-BOM content (returns None); B fails on endianness (wrong decode).

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_bom_only.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = """    nullcount = sample.count(_null)
    if nullcount == 0:
        return "utf-8"
    if nullcount == 2:
        if sample[::2] == _null2:  # 1st and 3rd are null
            return "utf-16-be"
        if sample[1::2] == _null2:  # 2nd and 4th are null
            return "utf-16-le"
        # Did not detect 2 valid UTF-16 ascii-range characters
    if nullcount == 3:
        if sample[:3] == _null3:
            return "utf-32-be"
        if sample[1:] == _null3:
            return "utf-32-le"
        # Did not detect a valid UTF-32 ascii-range character
    return None"""

NEW = """    # NEAR-MISS A: BOM-only detection, no null-byte heuristic
    return None"""


def main():
    p = Path(sys.argv[1]) / "http3" / "utils.py"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: null-byte heuristic block not found (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (BOM-only detection, no null-byte heuristic) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
