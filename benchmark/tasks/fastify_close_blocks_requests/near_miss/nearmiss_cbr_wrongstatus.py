"""Near-miss B for fastify_close_blocks_requests: check `closing` in routeHandler but send a
500 status instead of 503.

The gold sends a 503 (Service Unavailable) when closing === true. This near-miss keeps the
closing check (the flag IS consulted) but sends a 500 status code and body instead of 503.
Plausible "I reject closing requests" — but the status is wrong. The test checks
`res.statusCode === 503` -> the 500 response fails the assertion. Caught.

Distinct from A: A doesn't check the flag at all (second request gets 200); B checks the flag
but sends the wrong status (second request gets 500). Different failure mode.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_cbr_wrongstatus.py <repo_dir>
"""
import sys
from pathlib import Path

# Gold-applied routeHandler closing block (503 short-circuit).
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

# Near-miss B: check closing but send 500 instead of 503.
WRONG_STATUS = ("  function routeHandler (req, res, params, context) {\n"
                "    if (closing === true) {\n"
                "      // NEAR-MISS B: check closing but send 500 not 503\n"
                "      res.writeHead(500, {\n"
                "        'Content-Type': 'application/json',\n"
                "        'Content-Length': '80',\n"
                "        'Connection': 'close'\n"
                "      })\n"
                "      res.end('{\"error\":\"Internal Server Error\",\"message\":\"Internal Server Error\",\"statusCode\":500}')\n"
                "      setImmediate(() => req.destroy())\n"
                "      return\n"
                "    }\n"
                "\n")


def main():
    p = Path(sys.argv[1]) / "fastify.js"
    t = p.read_text()
    if GOLD_CHECK not in t:
        print("near-miss B: routeHandler closing-check block not found (is gold applied?)"); return 1
    p.write_text(t.replace(GOLD_CHECK, WRONG_STATUS, 1))
    print("near-miss B (check closing but send 500 instead of 503) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
