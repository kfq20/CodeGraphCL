"""Near-miss A for fastify_header_schema_case: copy the header schema before compiling, but never
re-key its properties map with lower-cased names.

The gold does two things: (1) copy the header schema so the user's original object is not mutated,
and (2) re-key the copy's `properties` map with lower-cased header names. This near-miss keeps only
the copy — plausible "the schema needed to be normalized into its own object before compiling; the
copy is the fix" — but the copied properties map still holds the original-cased 'Y-Test' key, which
never matches the request's lower-cased 'y-test', so the declared type is still skipped and the
echoed value stays the string '3'. Caught.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_hsc_copyonly.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = ("    if (headers.properties) {\n"
       "      const properties = headers.properties\n"
       "      for (const k in properties) {\n"
       "        if (properties.hasOwnProperty(k) !== true) continue\n"
       "        headersSchemaLowerCase.properties[k.toLowerCase()] = properties[k]\n"
       "      }\n"
       "    }\n")
NEW = ("    // NEAR-MISS A: copy the schema but never re-key its properties map\n")


def main():
    p = Path(sys.argv[1]) / "lib/validation.js"
    t = p.read_text()
    n = t.count(OLD)
    if n != 1:
        print(f"near-miss A: properties re-key block count={n} (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (copy the header schema but don't re-key properties) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
