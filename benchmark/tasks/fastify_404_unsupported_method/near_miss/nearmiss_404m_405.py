"""Near-miss A for fastify 404_unsupported_method: keep the 405 (base behavior).

The gold fix swaps 405 -> 404 for the unsupported-method case. This near-miss keeps the original
405 (the method-not-allowed code) — plausible reasoning "an unsupported method IS a method-not-
allowed; 405 is the spec-correct code". The test asserts statusCode 404, so 405 fails.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_404m_405.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = "  reply.code(404).send(new Error('Not Found'))"
NEW = "  reply.code(405).send(new Error('Method Not Allowed'))  // NEAR-MISS A: keep 405"


def main():
    p = Path(sys.argv[1]) / "lib/handleRequest.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: 404 line not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (keep 405 for unsupported method) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
