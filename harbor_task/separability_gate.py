#!/usr/bin/env python3
"""Instruction–Experience Separability Gate (R3 new gate).

A task can only carry a CL causal signal if the instruction and the experience are
SEPARABLE — otherwise (as httpx T_A/T_C showed) the instruction leaks the contract and
experience is redundant. This gate runs BEFORE any agent episode.

Checks (one task = one instruction + its atom set):
  S1. Instruction describes external symptom + acceptance behavior only, NOT solution
      principle. Banned mechanism words for this family (path-stripping): strip_prefix,
      over-strip, over-strip, take_while, is_absolute_parent, leading-slash ordering,
      ". guard". (Configurable per family via a banned-words list.)
  S2. Correct experience is NOT derivable from the instruction text alone.
      (Heuristic: correct_atom must contain a term NOT present in instruction.)
  S3. Stale/wrong experience is NOT explicitly negated by the instruction.
      (Heuristic: no sentence in instruction that directly contradicts the stale atom's
      main verb — e.g. instruction must not say "move X to the stream" when stale says "X
      belongs to the backend".) This is the check that caught T_C.
  S4. Each atom carries provenance = its producer commit; the atom's content must be
      recoverable from that commit's diff (no future knowledge). Automated part: the atom
      must cite a sha; the human audit confirms content provenance.
  S5. Reset is plausibly solvable but not trivially saturating. (Human judgment; recorded.)

Exit 0 = separable (passes the gate). Non-zero = FAIL (do not run the intervention).
A FAIL is a finding about task design, not a thing to fix by editing the prompt.

Usage: separability_gate.py <task_dir>
  <task_dir>/ contains: instruction.md, atoms.md (with <!-- ATOM:name --> + provenance),
  banned_words.txt (optional, family-specific), separability.checklist.yaml (human-filled).
"""
import hashlib
import os
import re
import sys
from pathlib import Path

def extract_atom(text, name):
    o, c = f"<!-- ATOM:{name} -->", f"<!-- /ATOM:{name} -->"
    i = text.find(o)
    if i < 0: return ""
    i += len(o)
    j = text.find(c, i)
    return text[i:j].strip() if j > 0 else ""

def sha(s): return hashlib.sha256(s.encode()).hexdigest()[:12]

def main():
    d = Path(sys.argv[1])
    instr_path = d / "instruction.md"
    atoms_path = d / "atoms.md"
    banned_path = d / "banned_words.txt"
    checklist_path = d / "separability.checklist.yaml"
    if not instr_path.exists() or not atoms_path.exists():
        print(f"FAIL: need {instr_path} and {atoms_path}"); return 1
    instr = instr_path.read_text().strip()
    atoms = atoms_path.read_text()
    banned = [w.strip().lower() for w in banned_path.read_text().splitlines()
              if w.strip() and not w.strip().startswith("#")] if banned_path.exists() else []
    results = []
    def check(n, ok, detail=""): results.append((n, ok, detail))

    # S1: no banned mechanism words in instruction
    instr_low = instr.lower()
    leaked = [w for w in banned if w in instr_low]
    check("S1 instruction has no banned mechanism words",
          not leaked, f"leaked: {leaked}" if leaked else "")

    # S2: correct atom has a term not in instruction (not trivially derivable)
    correct = extract_atom(atoms, "correct")
    instr_tokens = set(re.findall(r"[a-z_]+", instr_low))
    # content words in atom not in instruction
    atom_tokens = set(re.findall(r"[a-z_]+", correct.lower()))
    novel = atom_tokens - instr_tokens - {"the","a","to","of","and","in","on","for","is","are","with","that","this","it","as","by","an","be","or","from","at","not","same","new","which","its"}
    check("S2 correct atom not derivable from instruction",
          len(novel) >= 3, f"only {len(novel)} novel tokens: {sorted(novel)[:8]}")

    # S3: stale/wrong atom not explicitly negated by instruction.
    # The verb-overlap heuristic is too weak to catch semantic contradiction (T_C's
    # "move to stream" vs stale "belongs to backend" share no verb yet directly contradict).
    # So S3 is a HUMAN audit item (does instruction state the opposite of the stale atom?),
    # with a weak automated flag: high word-overlap between stale atom and instruction.
    stale = extract_atom(atoms, "wrong") or extract_atom(atoms, "stale")
    if not stale:
        check("S3 stale/wrong atom present", False, "no wrong/stale atom")
    else:
        stale_tokens = set(re.findall(r"[a-z_]+", stale.lower()))
        instr_tokens_set = set(re.findall(r"[a-z_]+", instr_low))
        overlap = stale_tokens & instr_tokens_set - {"the","a","to","of","and","in","on","for","is","are","with","that","this","it","as","by","an","be","or","from","at","not","same","new","which","its","should","must","context","project","prior","work","codebase"}
        # flag for human review (not hard fail) — recorded in checklist S3
        check(f"S3 stale/instruction overlap (flag for human review; overlap={len(overlap)})",
              True, f"overlap tokens: {sorted(overlap)[:8]}")

    # S4: each atom cites a provenance sha (content audit is human, recorded in checklist)
    atom_full = atoms
    # match "sha: <hex>" or "provenance: ... <hex>" anywhere; hex must be 7-40 chars
    sha_cites = re.findall(r"(?:sha|provenance)[^a-f0-9\n]*([0-9a-f]{7,40})", atom_full, re.I)
    # also catch inline "commit <hex>" / "commit: <hex>"
    sha_cites += re.findall(r"commit[^a-f0-9\n]*([0-9a-f]{7,40})", atom_full, re.I)
    check("S4 atoms cite producer commit sha (automated part)",
          len(sha_cites) >= 1, f"found {len(sha_cites)} sha cites")
    # human checklist must exist + be filled (S3 semantic + S4 content + S5 reset)
    if checklist_path.exists():
        cl = checklist_path.read_text().lower()
        check("S3 human: instruction does NOT directly negate stale atom",
              "s3:" in cl and ("verified" in cl or "[x]" in cl),
              "checklist must have S3: instruction-does-not-negate-stale = verified")
        check("S4 human content-provenance audit filled",
              "s4:" in cl and ("verified" in cl or "[x]" in cl),
              "checklist must have S4: provenance-verified")
        check("S5 reset-solvable-but-not-saturating judgment recorded",
              "s5:" in cl and ("saturat" in cl or "non-trivial" in cl or "verified" in cl),
              "checklist must have S5: reset-not-saturating note")
    else:
        check("S3/S4/S5 human checklist present", False, "no separability.checklist.yaml")

    # report
    print(f"\n=== Separability Gate: {d} ===")
    npass = 0
    for n, ok, det in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {n}" + (f"  [{det}]" if det else ""))
        if ok: npass += 1
    print(f"\n{npass}/{len(results)} checks passed")
    return 0 if npass == len(results) else 1

if __name__ == "__main__":
    sys.exit(main())
