"""Near-miss A for fastify reply_headerssent: invert the guard — set headers ONLY when already
sent.

The gold fix guards the header-setting loop with `if (!res.headersSent)`. This near-miss
inverts it to `if (res.headersSent)` — so headers are set ONLY after they've already been sent
(the opposite of intended). Plausible mistake: misreading the guard polarity. The normal
(no-manual-writeHead) case now SKIPS setting headers entirely -> the customize-headers test
fails (headers missing).

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_hs_invert.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = "  if (!res.headersSent) {"
NEW = "  if (res.headersSent) {  // NEAR-MISS A: inverted guard"


def main():
    p = Path(sys.argv[1]) / "lib/reply.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: headersSent guard not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (invert guard, set headers only when already sent) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
