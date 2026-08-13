"""Near-miss A for c3: over-strip (strip first path component unconditionally)."""
import sys
from pathlib import Path
NEAR_MISS = '''
                // NEAR-MISS A: strip the first path component unconditionally (over-strip).
                let mut comps = path.components();
                comps.next();
                let path = abs_parent_path.join(comps.as_path());
'''
def main():
    p = Path(sys.argv[1]) / "crates/ignore/src/dir.rs"
    t = p.read_text()
    start = t.find("                let dirpath = self.0.dir.as_path();")
    end = t.find("\n                for ig in", start)
    if start < 0 or end < 0:
        print("anchor not found"); return 1
    p.write_text(t[:start] + NEAR_MISS.strip() + t[end:])
    print("near-miss A (over-strip) injected")
    return 0
if __name__ == "__main__":
    sys.exit(main())
