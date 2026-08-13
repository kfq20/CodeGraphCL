"""Near-miss A for c4: guard only the exact "." dir, missing "./" and subdir-cwd cases.

c4's real fix bails out of prefix-stripping when the search dir is "." (so hidden-file
names starting with "." aren't mangled). This near-miss does the bail but ONLY for the
exact "." path, missing "./" — so r3173's "./" case still fails.

Usage: python3 nearmiss_c4.py <repo_dir>
"""
import sys
from pathlib import Path

# Replace the entire .map_or block's body with a near-miss that only guards exact "."
NEAR_MISS_BODY = '''map_or(path, |ig| {
                            // NEAR-MISS: guard ONLY exact "." — misses "./" and subdir-cwd
                            if ig.0.dir.as_path() == Path::new(".") {
                                return path;
                            }
                            strip_if_is_prefix(
                                "/",
                                strip_if_is_prefix(
                                    strip_if_is_prefix("./", ig.0.dir.as_path()),
                                    path,
                                ),
                            )
                        })'''


def main() -> int:
    repo = Path(sys.argv[1])
    p = repo / "crates/ignore/src/dir.rs"
    t = p.read_text()
    # anchor: the .map_or(path, |ig| { ... }) block. Find the start and its matching close.
    anchor = ".map_or(path, |ig| {"
    i = t.find(anchor)
    if i < 0:
        print("anchor '.map_or(path, |ig| {' not found — is this c4 base?")
        return 1
    # the block ends with "})" before the closing "),\n" of the join(
    # find the "})" that closes .map_or — it's the first "})" after the anchor
    # that's followed by ")," (end of the join call)
    j = i
    depth = 0
    end = -1
    for k in range(i, len(t)):
        if t[k] == '{':
            depth += 1
        elif t[k] == '}':
            depth -= 1
            if depth == 0:
                # this } closes the .map_or closure; the ) after it closes map_or
                end = k + 2  # include "})"
                break
    if end < 0:
        print("could not find end of .map_or block")
        return 1
    p.write_text(t[:i] + NEAR_MISS_BODY + t[end:])
    print("near-miss c4 (guard-only-exact-dot) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
