"""Near-miss B for fastify clean_schema_id: strip the wrong key (id, not $id).

The gold cleanId deletes the '$id' key (the JSON-Schema identifier). This near-miss recurses
correctly but deletes the un-prefixed 'id' key instead. Plausible reasoning — "strip the id so
it doesn't conflict" — but the conflict is specifically with the $-prefixed $id (JSON-Schema),
and plain 'id' is a different field that may legitimately exist. The $id stays, the conflict
remains, and the clean-the-$id test fails.

Distinct from near-miss A: A recurses not at all (top-level only); B recurses correctly but
targets the wrong key. Different failure shape (A leaves nested $id, B leaves ALL $id).

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_cid_wrongkey.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = "    if (key === '$id') delete schema[key]"
NEW = "    if (key === 'id') delete schema[key]  // NEAR-MISS B: wrong key (id not $id)"


def main():
    p = Path(sys.argv[1]) / "lib/schemas.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: cleanId $id line not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (strip 'id' instead of '$id') injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
