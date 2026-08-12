"""Near-miss controls for ripgrep c3 (anti-hardcoding gate).

Two near-miss implementations of the c3 fix — both COMPILE and are plausible-looking, but
behaviorally wrong. If the verifier catches both (4 FAIL_TO_PASS tests stay FAIL), it proves
the verifier tests real ignore/path behavior, not implementation shape.

near-miss A (over-strip — the c2 failure mode, but a different plausible encoding):
  strip the FULL search path's first component unconditionally (drops a real dir component).

near-miss B (no-strip — the pre-c2 failure mode):
  join abs_parent_path with the raw search path verbatim, no prefix elimination at all
  (reproduces duplicate-component bug c2 fixed).

Both edit crates/ignore/src/dir.rs at the same hunk c3 touches. Applied on c3 BASE
(no c3 source). Expect: the 4 FAIL_TO_PASS tests still FAIL (reward=0).

Usage: python3 nearmiss_c3.py <repo_dir> <A|B>
"""
import sys, re
from pathlib import Path

A = '''
                // NEAR-MISS A: strip the first path component unconditionally (over-strip).
                let mut comps = path.components();
                comps.next();
                let path = abs_parent_path.join(comps.as_path());
'''
B = '''
                // NEAR-MISS B: no prefix elimination — join verbatim (duplicate components).
                let path = abs_parent_path.join(path);
'''

def main():
    repo = Path(sys.argv[1]); which = sys.argv[2]
    p = repo / "crates/ignore/src/dir.rs"
    t = p.read_text()
    # anchor: the c3 hunk location. On c3 BASE (c2 applied), the code is c2's strip block.
    # Replace the whole c2 block (from `let dirpath = self.0.dir.as_path();` to the closing
    # of the `let path = match strip_prefix(path_prefix, path) {...};`) with the near-miss.
    start = t.find("                let dirpath = self.0.dir.as_path();")
    if start < 0:
        print("anchor not found — is this c3 base?"); return 1
    # the block ends before "                for ig in" (the line after the path block)
    end = t.find("\n                for ig in", start)
    if end < 0:
        print("block end not found"); return 1
    repl = A.strip() if which == "A" else B.strip()
    p.write_text(t[:start] + repl + t[end:])
    print(f"near-miss {which} injected")
    return 0

if __name__ == "__main__":
    sys.exit(main())
