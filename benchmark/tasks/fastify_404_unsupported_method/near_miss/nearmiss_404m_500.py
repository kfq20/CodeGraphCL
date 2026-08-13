"""Near-miss B for fastify 404_unsupported_method: use 500 (server error) instead of 404.

The gold fix swaps 405 -> 404. This near-miss swaps to 500 instead — plausible reasoning "an
unsupported method is an unexpected/erroneous request, 500 signals an error". But the product
spec is 404, and the test asserts statusCode 404, so 500 fails.

Distinct from near-miss A: A keeps the original 405 (spec-arguable); B picks a different wrong
code (500, semantically wrong — 5xx implies a server fault, not a client-side not-found).
Different wrong code, same failing assertion.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_404m_500.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = "  reply.code(404).send(new Error('Not Found'))"
NEW = "  reply.code(500).send(new Error('Unsupported method'))  // NEAR-MISS B: 500 not 404"


def main():
    p = Path(sys.argv[1]) / "lib/handleRequest.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: 404 line not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (use 500 instead of 404) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
