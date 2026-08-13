"""Near-miss B for c3: no-strip (join verbatim, duplicate components)."""
import sys
from pathlib import Path
NEAR_MISS = '''
                // NEAR-MISS B: no prefix elimination — join verbatim (duplicate components).
                let path = abs_parent_path.join(path);
'''
def main():
    p = Path(sys.argv[1]) / "crates/ignore/src/dir.rs"
    t = p.read_text()
    start = t.find("                let dirpath = self.0.dir.as_path();")
    end = t.find("\n                for ig in", start)
    if start < 0 or end < 0:
        print("anchor not found"); return 1
    p.write_text(t[:start] + NEAR_MISS.strip() + t[end:])
    print("near-miss B (no-strip) injected")
    return 0
if __name__ == "__main__":
    sys.exit(main())
