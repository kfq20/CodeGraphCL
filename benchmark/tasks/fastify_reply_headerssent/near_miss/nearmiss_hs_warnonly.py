"""Near-miss B for fastify reply_headerssent: add the warning but still run the header loop
(no guard).

The gold fix guards the header loop with `if (!res.headersSent) { ...loop... } else { warn }`.
This near-miss adds the warning (so the fix "looks done") but runs the header-setting loop
UNCONDITIONALLY — the guard is missing, so when headers are already sent the loop still calls
setHeader -> throws. Plausible mistake: "I added the warning, the loop is fine" — the warn-else
was wired but the guard on the loop body was forgotten. The writeHead test crashes (same as
base).

Distinct from near-miss A: A inverts the guard (normal case loses headers); B removes the guard
(writeHead case crashes). Different failure case.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_hs_warnonly.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = ("  if (!res.headersSent) {\n"
       "    for (var key in reply._headers) {\n"
       "      res.setHeader(key, reply._headers[key])\n"
       "    }\n"
       "  } else {\n"
       "    res.log.warn('response will send, but you shouldn\\'t use res.writeHead in stream mode')\n"
       "  }\n")
NEW = ("  for (var key in reply._headers) {\n"
       "    res.setHeader(key, reply._headers[key])\n"
       "  }  // NEAR-MISS B: guard removed, loop always runs\n"
       "  if (res.headersSent) {\n"
       "    res.log.warn('response will send, but you shouldn\\'t use res.writeHead in stream mode')\n"
       "  }\n")


def main():
    p = Path(sys.argv[1]) / "lib/reply.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: headersSent guard block not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (warn added but header loop unguarded -> writeHead crashes) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
