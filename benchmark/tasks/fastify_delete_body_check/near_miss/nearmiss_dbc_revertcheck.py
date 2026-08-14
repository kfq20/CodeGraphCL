"""Near-miss B for fastify_delete_body_check: revert the gold condition to the original
`contentType === undefined` check, ignoring body indicators entirely.

The gold inverts the condition to check body indicators (transfer-encoding/content-length)
before parsing. This near-miss replaces the entire gold if/else block with the original
base check: `if (contentType === undefined) { handler } else { parser }`. Plausible "the
original check was fine, just restructure the code" — but the original check triggers
parsing whenever Content-Type is set, regardless of body presence. The test sends
Content-Type: application/json with no body, so the parser runs and the test FAILS. Caught.

Distinct from A: A negates the body-indicator group (logic error in the new condition);
B reverts to the original condition entirely (no body-indicator check at all).

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_dbc_revertcheck.py <repo_dir>
"""
import sys
from pathlib import Path

GOLD = ("    if (\n"
        "      contentType !== undefined &&\n"
        "      (\n"
        "        headers['transfer-encoding'] !== undefined ||\n"
        "        headers['content-length'] !== undefined\n"
        "      )\n"
        "    ) {\n"
        "      context.contentTypeParser.run(contentType, handler, request, reply)\n"
        "    } else {\n"
        "      handler(reply)\n"
        "    }\n")

BASE = ("    if (contentType === undefined) {\n"
        "      handler(reply)\n"
        "    } else {\n"
        "      context.contentTypeParser.run(contentType, handler, request, reply)\n"
        "    }\n")


def main():
    p = Path(sys.argv[1]) / "lib/handleRequest.js"
    t = p.read_text()
    if GOLD not in t:
        print("near-miss B: gold if/else block not found (is gold applied?)"); return 1
    p.write_text(t.replace(GOLD, BASE, 1))
    print("near-miss B (revert to original contentType === undefined check) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
