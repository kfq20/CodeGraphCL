"""Near-miss A for fastify get_shared_schemas: return the schema ids, not the schema map.

The gold fix returns the store MAP (id -> schema) as a shallow copy. This near-miss returns
the list of KEYS instead — the schema ids. Plausible reasoning — "getSchemas should give me all
the schemas' names so I can look them up" — but the test asserts a deepEqual against the
expected map, so an array of ids fails the deepEqual (wrong shape). Caught.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_sch_keys.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = "  return Object.assign({}, this.store)"
NEW = "  return Object.keys(this.store)  // NEAR-MISS A: return ids, not the map"


def main():
    p = Path(sys.argv[1]) / "lib/schemas.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: getSchemas return not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (return schema ids, not the map) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
