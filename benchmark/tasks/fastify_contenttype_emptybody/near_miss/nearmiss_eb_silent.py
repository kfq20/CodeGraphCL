"""Near-miss B for fastify emptybody: silently no-op on empty body (don't parse, don't reject).

The gold fix lets the empty body reach the custom parser. This near-miss, on an empty body,
returns early WITHOUT sending a response or calling the parser — plausible reasoning "an empty
body is a no-op, nothing to do". The custom parser never runs and no response is sent, so the
test (expects a 200 with the parsed empty result) fails / times out.

Injects at the site where gold removed the reject (just before the asString branch in onEnd).

Distinct from near-miss A: A rejects with a (wrong) status; B silently drops. Different failure
mode (422 response vs no response).

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_eb_silent.py <repo_dir>
"""
import sys
from pathlib import Path

ANCHOR = "    if (asString === false) {"
INJECT = ("    if (receivedLength === 0) { return }  // NEAR-MISS B: silent no-op on empty\n"
          "    if (asString === false) {")


def main():
    p = Path(sys.argv[1]) / "lib/ContentTypeParser.js"
    t = p.read_text()
    if t.count(ANCHOR) != 1:
        print(f"near-miss B: anchor count={t.count(ANCHOR)}"); return 1
    if "NEAR-MISS B" in t:
        print("near-miss B: already injected"); return 1
    p.write_text(t.replace(ANCHOR, INJECT, 1))
    print("near-miss B (silent no-op on empty body, no parse no response) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
