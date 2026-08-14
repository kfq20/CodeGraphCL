"""Near-miss B for httpx_multipart_header_encoding: HTML5 encoding but missing control chars.

The gold _format_param() includes control characters (0x00-0x1F except 0x1B) in the replacement
table. This near-miss removes the control-char entries, keeping only backslash and double-quote.
Plausible "the visible chars are quote and backslash, control chars are an edge case" — but the
test checks control char encoding (0x1A -> %1A, 0x1C -> %1C, 0x1B passes through). Caught:
test_unicode_with_control_character fails (0x1A and 0x1C not percent-encoded).

Distinct from A: B uses HTML5 encoding (right type) but missing one char class; A uses wrong
encoding entirely.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_no_control_chars.py <repo_dir>
"""
import sys
from pathlib import Path

# Use a regex-based replacement to avoid backslash escaping nightmares.
# We replace the .update() call (which adds control chars) with a no-op.
OLD_MARKER = "_HTML5_FORM_ENCODING_REPLACEMENTS.update("
NEW_MARKER = "pass  # NEAR-MISS B: no control chars in replacement table\nif False: _HTML5_FORM_ENCODING_REPLACEMENTS.update("


def main():
    p = Path(sys.argv[1]) / "httpx" / "multipart.py"
    t = p.read_text()
    if OLD_MARKER not in t:
        print("near-miss B: replacement table update() not found (is gold applied?)")
        return 1
    # Replace the update() call with a no-op so control chars are NOT added
    idx = t.find(OLD_MARKER)
    # find the matching closing paren of the update() call
    paren_depth = 0
    end = idx
    for i in range(idx, len(t)):
        if t[i] == '(':
            paren_depth += 1
        elif t[i] == ')':
            paren_depth -= 1
            if paren_depth == 0:
                end = i + 1
                break
    old_block = t[idx:end]
    new_block = "pass  # NEAR-MISS B: no control chars"
    p.write_text(t[:idx] + new_block + t[end:])
    print("near-miss B (HTML5 encoding but missing control chars) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
