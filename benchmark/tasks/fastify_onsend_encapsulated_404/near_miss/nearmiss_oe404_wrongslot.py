"""Near-miss B for fastify_onsend_encapsulated_404: copy the 404 context and assign the route's
hooks, but onto the wrong hook slot (onResponse instead of onSend).

The gold assigns the route's onSend hook list onto the copied 404 context's onSend slot, because
onSend is the slot the reply's send path consults when serializing the 404 response. This near-miss
assigns the same hook list onto onResponse — plausible "the hooks need to run when the response is
produced, that's the response hook" — but the send path reads onSend (still the root's null), so the
plugin's onSend hook never runs during 404 serialization. Caught.

Distinct from A: A never assigns the hooks at all (the copy carries the root's hooks); B does assign
them, but to a slot the 404 send path does not read. Different failure axis (missing assignment vs.
wrong destination slot).

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_oe404_wrongslot.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = ("        const _404Context = Object.assign({}, _fastify._404Context)\n"
       "        _404Context.onSend = context.onSend\n"
       "        context._404Context = _404Context\n")
NEW = ("        // NEAR-MISS B: assign this route's hooks to the onResponse slot, not onSend\n"
       "        const _404Context = Object.assign({}, _fastify._404Context)\n"
       "        _404Context.onResponse = context.onSend\n"
       "        context._404Context = _404Context\n")


def main():
    p = Path(sys.argv[1]) / "fastify.js"
    t = p.read_text()
    n = t.count(OLD)
    if n != 1:
        print(f"near-miss B: 404-context copy block count={n} (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (assign route hooks to onResponse instead of onSend) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
