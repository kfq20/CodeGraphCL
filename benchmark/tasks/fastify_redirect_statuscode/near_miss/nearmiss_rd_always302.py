"""Near-miss B for fastify redirect: track the flag but never use it (always default 302).

The gold fix adds the `_hasStatusCode` flag AND uses it in the redirect ternary. This near-miss
sets the flag correctly (so the structural fix "looks done") but leaves the redirect always
defaulting to 302 — the ternary's false-branch — by hardcoding it. Plausible mistake: "I added
the tracking; the default-302 path is the safe fallback" — but the ternary never takes the
true branch's value, so `code(307).redirect('/')` still responds 302. The before-call test
fails (expects 307).

Distinct from near-miss A: A honors the preset too aggressively (breaks the explicit-override
test); B honors it not at all (breaks the preset test). Opposite directions, opposite failing
assertion.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_rd_always302.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = "    code = this._hasStatusCode ? this.res.statusCode : 302"
NEW = "    code = 302  // NEAR-MISS B: flag tracked but never honored"


def main():
    p = Path(sys.argv[1]) / "lib/reply.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: redirect ternary not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (flag tracked but redirect always uses 302) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
