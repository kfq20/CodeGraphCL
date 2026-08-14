"""Near-miss A for httpx_client_property_convert: cookies setter does NOT coerce (stores raw value).

The gold cookies setter wraps the assigned value: `self._cookies = Cookies(cookies)`. This near-miss
drops the wrapping and stores the raw assignment: `self._cookies = cookies`. Plausible "the setter
just stores what you give it" — but then `client.cookies = {"a": "b"}` leaves a plain dict, so
`isinstance(client.cookies, Cookies)` is False and the CookieJar round-trip test breaks.

Distinct from B: A breaks the cookies axis (headers still coerces); B breaks the headers axis.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_cookies_raw.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = """    @cookies.setter
    def cookies(self, cookies: CookieTypes) -> None:
        self._cookies = Cookies(cookies)"""

NEW = """    @cookies.setter
    def cookies(self, cookies: CookieTypes) -> None:
        # NEAR-MISS A: store raw value, do not coerce into Cookies()
        self._cookies = cookies"""


def main():
    p = Path(sys.argv[1]) / "httpx" / "client.py"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: cookies setter block not found (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (cookies setter does not coerce) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
