"""Near-miss B for httpx_json_encoding_detection: swap utf-16/32 endianness in null-byte logic.

The gold guess_json_utf() returns "utf-16-be" when sample[::2] == _null2 (1st and 3rd are null)
and "utf-16-le" when sample[1::2] == _null2 (2nd and 4th are null). Similarly for utf-32-be/le.
This near-miss swaps the be/le returns. Plausible "I got the endianness backwards" — the
detected encoding is wrong, so json() decodes with the wrong endianness. Caught:
test_json_without_specified_encoding (utf-32-be content) detects "utf-32-le" -> wrong decode
-> garbled JSON -> json parse error or wrong data.

Distinct from A: B detects an encoding (wrong one); A returns None (no detection).

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_wrong_null_logic.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = """    if nullcount == 2:
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

NEW = """    if nullcount == 2:
        if sample[::2] == _null2:  # 1st and 3rd are null
            return "utf-16-le"  # NEAR-MISS B: swapped endianness
        if sample[1::2] == _null2:  # 2nd and 4th are null
            return "utf-16-be"  # NEAR-MISS B: swapped endianness
        # Did not detect 2 valid UTF-16 ascii-range characters
    if nullcount == 3:
        if sample[:3] == _null3:
            return "utf-32-le"  # NEAR-MISS B: swapped endianness
        if sample[1:] == _null3:
            return "utf-32-be"  # NEAR-MISS B: swapped endianness
        # Did not detect a valid UTF-32 ascii-range character
    return None"""


def main():
    p = Path(sys.argv[1]) / "http3" / "utils.py"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: null-byte heuristic block not found (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (swapped be/le endianness in null-byte logic) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
