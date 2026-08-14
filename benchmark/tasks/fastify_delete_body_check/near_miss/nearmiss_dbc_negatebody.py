"""Near-miss A for fastify_delete_body_check: negate the body-indicator check so parsing
runs when NO body is present.

The gold checks `contentType !== undefined && (transfer-encoding || content-length)` to
decide whether to parse. This near-miss negates the body-indicator group, changing the
condition to `contentType !== undefined && !(transfer-encoding || content-length)` — so
parsing runs when there is Content-Type but NO body indicator. Plausible "just negate the
inner check" logic error. The test sends Content-Type with no body indicators, so parsing
is triggered and the test FAILS. Caught.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_dbc_negatebody.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = ("      (\n"
       "        headers['transfer-encoding'] !== undefined ||\n"
       "        headers['content-length'] !== undefined\n"
       "      )\n")
NEW = ("      !(\n"
       "        headers['transfer-encoding'] !== undefined ||\n"
       "        headers['content-length'] !== undefined\n"
       "      )\n")


def main():
    p = Path(sys.argv[1]) / "lib/handleRequest.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: body-indicator group not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (negate body-indicator check, parse when no body) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
