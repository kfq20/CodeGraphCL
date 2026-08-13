"""Near-miss B for fastify json_charset: keep the exact-match (don't substring-match).

The gold fix relaxes the JSON check to a substring match so charset-suffixed forms are
recognized. This near-miss keeps the exact-match (the bare form only) but DOES add the charset
guard — plausible reasoning "I'll preserve an existing charset, but only recognize bare JSON".
The JSON+charset test still fails the recognition (exact match misses the charset-suffixed
form) — same failure as base.

Distinct from near-miss A: A fails the charset-PRESERVATION assertion (recognition works,
charset clobbered); B fails the RECOGNITION (charset-suffixed JSON not treated as JSON).
Different assertion.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_jc_exact.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = "contentType.indexOf('application/json') > -1"
NEW = "contentType === 'application/json'  // NEAR-MISS B: keep exact match"


def main():
    p = Path(sys.argv[1]) / "lib/reply.js"
    t = p.read_text()
    if t.count(OLD) != 1:
        print(f"near-miss B: substring-match count={t.count(OLD)} (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (keep exact JSON match, don't substring-match) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
