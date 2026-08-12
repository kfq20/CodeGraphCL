"""Near-miss for ripgrep c4 (anti-hardcoding control).

c4's fix: when the search dir is literally `.`, bail out of prefix-stripping early so a
hidden file's leading `.` is not mangled. A plausible-but-wrong version handles only the
bare `.` case and misses `./` (and the subdir-cwd case), so the r3173 test still fails.

Usage (run inside the container against the work tree):
  python3 nearmiss_c4.py <repo_dir> [A]
"""
import sys
from pathlib import Path

# near-miss: guard ONLY the exact "." dir, missing "./" and the subdir-cwd path.
NEAR_MISS = '''
                            // NEAR-MISS: guard only the exact "." dir; misses "./" and the
                            // subdir-cwd case, so hidden-file whitelists still break there.
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
'''


def main() -> int:
    repo = Path(sys.argv[1])
    p = repo / "crates/ignore/src/dir.rs"
    t = p.read_text()
    # anchor on c3-era block (c4 base has c3's strip_if_is_prefix nest)
    anchor = "                            strip_if_is_prefix("
    i = t.find(anchor)
    if i < 0:
        print("anchor not found — is this c4 base?")
        return 1
    # replace from the anchor through the closing of that nested call
    end = t.find("\n                        }", i)
    if end < 0:
        print("block end not found")
        return 1
    p.write_text(t[:i] + NEAR_MISS.strip("\n") + t[end:])
    print("near-miss c4 injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
