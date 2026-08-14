"""Near-miss B for httpx_client_property_convert: headers setter does NOT coerce (stores raw value).

The gold headers setter wraps the assigned value: `self._headers = Headers(headers)`. This near-miss
drops the wrapping and stores the raw assignment: `self._headers = headers`. Plausible "the setter
just stores what you give it" — but then `client.headers = {"a": "b"}` leaves a plain dict, so
`isinstance(client.headers, Headers)` is False and the case-normalization (["A"] == "b") breaks.

Distinct from A: B breaks the headers axis (cookies still coerces); A breaks the cookies axis.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_headers_raw.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = """    @headers.setter
    def headers(self, headers: HeaderTypes) -> None:
        self._headers = Headers(headers)"""

NEW = """    @headers.setter
    def headers(self, headers: HeaderTypes) -> None:
        # NEAR-MISS B: store raw value, do not coerce into Headers()
        self._headers = headers"""


def main():
    p = Path(sys.argv[1]) / "httpx" / "client.py"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: headers setter block not found (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (headers setter does not coerce) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
