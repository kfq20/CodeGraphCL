"""Near-miss B for c4: no guard at all — keep c3's strip logic unchanged (mangles hidden files).

c4's fix adds a `.`-dir bail. This near-miss omits it entirely (keeps c3's behavior),
so hidden-file names starting with "." get their leading "." stripped -> r3173 fails.

Usage: python3 nearmiss_c4_noguard.py <repo_dir>
"""
import sys
from pathlib import Path

# This near-miss makes NO change to the c3 strip block (it's already the c3 behavior
# at c4 base). So we just verify the base behavior fails r3173 — which it does (base-fail).
# To make this a real near-miss (not just "base"), we add a plausible-but-wrong comment
# that claims to handle the case, but the code is unchanged.
NEAR_MISS_MARKER = '''// NEAR-MISS B: claim to handle .-dir/hidden-file scope, but no actual guard added
'''


def main() -> int:
    repo = Path(sys.argv[1])
    p = repo / "crates/ignore/src/dir.rs"
    t = p.read_text()
    # Insert a misleading comment before the strip block (code unchanged -> still mangles)
    anchor = ".map_or(path, |ig| {"
    i = t.find(anchor)
    if i < 0:
        print("anchor not found — is this c4 base?")
        return 1
    # insert the marker comment just before the anchor (code unchanged)
    p.write_text(t[:i] + NEAR_MISS_MARKER + t[i:])
    print("near-miss c4 (no-guard, misleading comment) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
