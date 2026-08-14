"""Near-miss A for fastify_onsend_encapsulated_404: build the per-route copy of the 404 context
but never assign the route's own onSend hooks onto it.

The gold does two things at preReady: (1) copy the root 404 context so each route gets its own,
and (2) assign that route's onSend hook list onto the copy. This near-miss keeps only the copy —
plausible "the encapsulation bug is the shared reference; copying it fixes it" — but the copy still
carries the ROOT instance's onSend (null, since the root registered no hooks), so the plugin's
onSend hook still never runs and the test's third assertion never fires. Caught.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_oe404_copyonly.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = ("        const _404Context = Object.assign({}, _fastify._404Context)\n"
       "        _404Context.onSend = context.onSend\n"
       "        context._404Context = _404Context\n")
NEW = ("        // NEAR-MISS A: copy the 404 context but never assign this route's onSend hooks\n"
       "        const _404Context = Object.assign({}, _fastify._404Context)\n"
       "        context._404Context = _404Context\n")


def main():
    p = Path(sys.argv[1]) / "fastify.js"
    t = p.read_text()
    n = t.count(OLD)
    if n != 1:
        print(f"near-miss A: 404-context copy block count={n} (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (copy the 404 context but don't assign onSend hooks) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
