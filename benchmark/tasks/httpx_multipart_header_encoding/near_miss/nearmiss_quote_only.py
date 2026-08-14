"""Near-miss A for httpx_multipart_header_encoding: use urllib quote() instead of HTML5 encoding.

The gold _format_param() uses an HTML5 form encoding replacement table (regex-based) that
passes through non-ASCII as UTF-8 bytes, escapes backslashes, and percent-encodes control chars.
This near-miss replaces _format_param with a urllib quote()-based version (the old approach).
Plausible "just fix the safe set on the existing quote()" — but quote() percent-encodes non-ASCII
bytes, which the test doesn't expect (unicode should pass through as UTF-8). Caught:
test_unicode fails (quote percent-encodes \xc3\xa4 -> %C3%A4).

Distinct from B: A uses wrong encoding entirely (quote); B uses right encoding but missing
control chars.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_quote_only.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = """def _format_param(name: str, value: typing.Union[str, bytes]) -> bytes:
    if isinstance(value, bytes):
        value = value.decode()
        \n    def replacer(match: typing.Match[str]) -> str:
        return _HTML5_FORM_ENCODING_REPLACEMENTS[match.group(0)]

    value = _HTML5_FORM_ENCODING_RE.sub(replacer, value)
    return f'{name}="{value}"'.encode()"""

NEW = """def _format_param(name: str, value: typing.Union[str, bytes]) -> bytes:
    # NEAR-MISS A: use urllib quote() instead of HTML5 form encoding
    from urllib.parse import quote
    if isinstance(value, bytes):
        value = value.decode()
    encoded = quote(value, encoding="utf-8")
    return f'{name}="{encoded}"'.encode("ascii")"""


def main():
    p = Path(sys.argv[1]) / "httpx" / "multipart.py"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: _format_param body not found (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (urllib quote() instead of HTML5 encoding) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
