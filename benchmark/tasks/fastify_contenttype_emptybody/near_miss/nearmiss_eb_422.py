"""Near-miss A for fastify emptybody: keep the empty-body reject but use a different status.

The gold fix REMOVES the zero-length-body early-reject so the custom parser gets empty input.
This near-miss re-adds the reject (so the fix "looks like it touched the right area") but with
status 422 instead of 400 — plausible reasoning "422 is a more precise code for a processable-
but-empty body". The empty-body test still gets a 422 rejection instead of the parsed result,
so it fails.

Injects at the site where gold removed the reject (just before the asString branch in onEnd).

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_eb_422.py <repo_dir>
"""
import sys
from pathlib import Path

ANCHOR = "    if (asString === false) {"
INJECT = ("    if (receivedLength === 0) { reply.code(422).send(new Error('empty body')); return }  // NEAR-MISS A\n"
          "    if (asString === false) {")


def main():
    p = Path(sys.argv[1]) / "lib/ContentTypeParser.js"
    t = p.read_text()
    if t.count(ANCHOR) != 1:
        print(f"near-miss A: anchor count={t.count(ANCHOR)} (is gold applied? should be unique)"); return 1
    if "NEAR-MISS A" in t:
        print("near-miss A: already injected"); return 1
    p.write_text(t.replace(ANCHOR, INJECT, 1))
    print("near-miss A (re-add empty-body reject with status 422) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
