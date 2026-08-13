"""Near-miss A for fastify clean_schema_id: only strip $id at the top level (no recursion).

The gold cleanId walks the schema object recursively, deleting $id from every nested object.
This near-miss deletes $id only at the current level and skips the recursive descent into
nested objects. Plausible reasoning — "I'll strip the $id from this schema" — but a nested
schema object keeps its $id, which still conflicts at compile time. The clean-the-$id test
fails (nested $id not removed).

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_cid_shallow.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = ("  for (var key in schema) {\n"
       "    if (key === '$id') delete schema[key]\n"
       "    if (schema[key] !== null && typeof schema[key] === 'object') {\n"
       "      this.cleanId(schema[key])\n"
       "    }\n"
       "  }\n")
NEW = ("  for (var key in schema) {\n"
       "    if (key === '$id') delete schema[key]  // NEAR-MISS A: no recursive descent\n"
       "  }\n")


def main():
    p = Path(sys.argv[1]) / "lib/schemas.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: cleanId body not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (strip $id top-level only, no recursion) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
