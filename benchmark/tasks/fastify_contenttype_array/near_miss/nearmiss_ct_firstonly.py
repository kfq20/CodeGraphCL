"""Near-miss A for fastify contenttype array: register only the first element.

The gold fix iterates the array, calling add() for EACH content type. This near-miss detects
the array but registers only the FIRST element (and ignores the rest). The reasoning is
plausible — "the first type is the canonical one; the others are aliases that resolve to it" —
but the test registers two DISTINCT custom types and asserts BOTH parse. Only the first is
registered, so the second POST (application/ffosj) hits no parser and the test fails.

Runs on HOST. near_miss_base: gold (operates on gold-applied code).
Usage: python3 nearmiss_ct_firstonly.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = ("    if (Array.isArray(contentType)) {\n"
       "      contentType.forEach((type) => this._contentTypeParser.add(type, opts, parser))\n"
       "    } else {\n")
NEW = ("    if (Array.isArray(contentType)) {\n"
       "      this._contentTypeParser.add(contentType[0], opts, parser)  // NEAR-MISS A: first only\n"
       "    } else {\n")


def main():
    p = Path(sys.argv[1]) / "fastify.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: gold array-handling block not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (register only first array element) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
