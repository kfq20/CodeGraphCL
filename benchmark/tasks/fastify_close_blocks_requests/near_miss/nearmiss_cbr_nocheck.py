"""Near-miss A for fastify_close_blocks_requests: set the `closing` flag (flag declaration +
preReady/onClose wiring intact) but DON'T check it in routeHandler.

The gold checks `if (closing === true)` at the top of routeHandler and short-circuits with a
503. This near-miss keeps the flag and the preReady/onClose wiring (the flag IS set to true
when close() fires) but removes the routeHandler check entirely — so the second request goes
through the normal lifecycle and gets 200, not 503. Plausible "I added the flag, the handler
consults it" — but the handler never consults it. Caught.

Distinct from B: B checks the flag but sends the wrong status (500); A doesn't check at all.
Different failure mode.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_cbr_nocheck.py <repo_dir>
"""
import sys
from pathlib import Path

# Gold-applied routeHandler closing block (the 503 short-circuit).
GOLD_CHECK = ("  function routeHandler (req, res, params, context) {\n"
             "    if (closing === true) {\n"
             "      res.writeHead(503, {\n"
             "        'Content-Type': 'application/json',\n"
             "        'Content-Length': '80',\n"
             "        'Connection': 'close'\n"
             "      })\n"
             "      res.end('{\"error\":\"Service Unavailable\",\"message\":\"Service Unavailable\",\"statusCode\":503}')\n"
             "      setImmediate(() => req.destroy())\n"
             "      return\n"
             "    }\n"
             "\n")

# Near-miss A: remove the closing check — routeHandler goes straight to the normal lifecycle.
BASE_HANDLER = ("  function routeHandler (req, res, params, context) {\n"
                "    // NEAR-MISS A: closing flag is set but never checked — normal lifecycle runs\n")


def main():
    p = Path(sys.argv[1]) / "fastify.js"
    t = p.read_text()
    if GOLD_CHECK not in t:
        print("near-miss A: routeHandler closing-check block not found (is gold applied?)"); return 1
    p.write_text(t.replace(GOLD_CHECK, BASE_HANDLER, 1))
    print("near-miss A (set closing flag but don't check it in routeHandler) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
