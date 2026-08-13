"""Near-miss B for fastify contenttype array: detect the array but pass it whole to add().

The gold fix iterates the array and calls add() per element. This near-miss DOES detect the
array (so the fix "looks right" structurally — it checks for arrays) but then passes the whole
array object to add() unchanged in both branches, i.e. it forgets to actually iterate. The
content-type parser store gets a single entry whose key is the stringified array, so neither
real type ('application/jsoff' / 'application/ffosj') matches an incoming request -> both POST
assertions fail -> test fails.

Plausible mistake: "I'll handle arrays here and let the lower layer deal with it" — a real
incomplete-refactor smell where the guard exists but the action wasn't wired.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_ct_passthrough.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = ("    if (Array.isArray(contentType)) {\n"
       "      contentType.forEach((type) => this._contentTypeParser.add(type, opts, parser))\n"
       "    } else {\n"
       "      this._contentTypeParser.add(contentType, opts, parser)\n"
       "    }\n")
NEW = ("    if (Array.isArray(contentType)) {\n"
       "      this._contentTypeParser.add(contentType, opts, parser)  // NEAR-MISS B: array passed whole\n"
       "    } else {\n"
       "      this._contentTypeParser.add(contentType, opts, parser)\n"
       "    }\n")


def main():
    p = Path(sys.argv[1]) / "fastify.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: gold block not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (detect array but pass it whole to add) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
