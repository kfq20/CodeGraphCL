"""Near-miss B for fastify_header_schema_case: re-key the header schema's properties map, but
normalize the names to upper case instead of lower case.

The gold re-keys the properties map to LOWER case, because that is the case Node.js gives incoming
header names. This near-miss normalizes to upper case — plausible "header names are canonically
written capitalized (Content-Type, Y-Test), so normalize the schema that way" — but the request's
key is 'y-test', which does not match the schema's 'Y-TEST', so the declared type is still skipped
and the echoed value stays the string '3'. Caught.

Distinct from A: A never re-keys at all (original casing survives); B does re-key, normalizing
consistently but to the case the runtime does not use. Different failure axis (missing normalization
vs. wrong normalization target).

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_hsc_uppercase.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = "        headersSchemaLowerCase.properties[k.toLowerCase()] = properties[k]\n"
NEW = ("        // NEAR-MISS B: normalize property names to upper case, not lower case\n"
       "        headersSchemaLowerCase.properties[k.toUpperCase()] = properties[k]\n")


def main():
    p = Path(sys.argv[1]) / "lib/validation.js"
    t = p.read_text()
    n = t.count(OLD)
    if n != 1:
        print(f"near-miss B: properties re-key line count={n} (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (re-key properties to upper case instead of lower case) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
