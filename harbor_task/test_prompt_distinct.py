#!/usr/bin/env python3
"""Test: the 4 conditions produce 4 distinct prompts (catches the silent-empty-prefix bug).

This is the regression test for the G1.1 bug where sed extracted 0 bytes for 3/4 arms.
Run before any episode batch: `python3 test_prompt_distinct.py <atoms> <instruction>`.
Exits 0 iff reset/correct/irrelevant/wrong yield 4 distinct prompt_sha256 AND the 3 non-reset
prefixes are non-empty.
"""
import subprocess
import sys
import tempfile
import json

ATOMS = sys.argv[1]
INSTR = sys.argv[2]
CONDITIONS = ["reset", "correct", "irrelevant", "wrong"]

def build(cond):
    d = tempfile.mkdtemp()
    r = subprocess.run([sys.executable, __file__.replace("test_prompt_distinct.py", "build_prompt.py"),
                        ATOMS, INSTR, cond, "/pool/test/work", d],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"FAIL: build_prompt for {cond} exited {r.returncode}: {r.stderr.strip()}")
        sys.exit(1)
    return json.loads(r.stdout)

manifests = {c: build(c) for c in CONDITIONS}

# 1. non-reset prefixes must be non-empty
for c in CONDITIONS[1:]:
    if manifests[c]["prefix_chars"] == 0:
        print(f"FAIL: {c} has empty prefix (the G1.1 bug)")
        sys.exit(1)
print(f"OK: all 3 non-reset prefixes non-empty: " +
      ", ".join(f"{c}={manifests[c]['prefix_chars']}c" for c in CONDITIONS[1:]))

# 2. all 4 prompt_sha256 distinct
hashes = {c: manifests[c]["prompt_sha256"] for c in CONDITIONS}
if len(set(hashes.values())) != 4:
    # reset vs another being equal is the real failure
    dups = [c for c in CONDITIONS if list(hashes.values()).count(hashes[c]) > 1]
    print(f"FAIL: prompt hashes not all distinct — duplicates: {dups}")
    for c in CONDITIONS:
        print(f"  {c}: prefix_sha={manifests[c]['prefix_sha256'][:12]} prompt_sha={hashes[c][:12]}")
    sys.exit(1)
print(f"OK: 4 distinct prompt_sha256: " + ", ".join(f"{c}={hashes[c][:8]}" for c in CONDITIONS))
sys.exit(0)
