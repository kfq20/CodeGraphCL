#!/usr/bin/env python3
"""Build the agent prompt for one intervention condition + emit an audit manifest.

Replaces the fragile shell `sed /^## X/` extractor (which silently returned empty for the
HTML-marker atom format, making 3 of 4 T_B arms run with no prefix at all — the bug that
invalidated the first run).

Contract:
  - atoms live in an atoms file delimited by `<!-- ATOM:<name> -->` ... `<!-- /ATOM:<name> -->`
  - reset -> empty prefix (legal)
  - correct/irrelevant/wrong -> the atom text; EMPTY prefix is a HARD error (exit 2)
  - writes <outdir>/manifest.json: condition, prefix_chars, prefix_sha256, prompt_sha256,
    instruction_sha256, model, base_url (host part), budget_sec
  - the full prompt is also written to <outdir>/prompt.txt for audit

Usage: build_prompt.py <atoms_file> <instruction_file> <condition> <episode_container_workdir> <outdir>
"""
import hashlib
import json
import os
import sys


def extract_atom(atoms_file: str, name: str) -> str:
    """Return the text between <!-- ATOM:name --> and <!-- /ATOM:name --> (stripped)."""
    text = open(atoms_file).read()
    open_tag = f"<!-- ATOM:{name} -->"
    close_tag = f"<!-- /ATOM:{name} -->"
    i = text.find(open_tag)
    if i < 0:
        return ""
    i += len(open_tag)
    j = text.find(close_tag, i)
    if j < 0:
        return ""
    return text[i:j].strip()


def sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def main():
    if len(sys.argv) != 6:
        print("usage: build_prompt.py <atoms> <instruction> <condition> <container_workdir> <outdir>", file=sys.stderr)
        return 2
    atoms_file, instr_file, condition, cwd, outdir = sys.argv[1:6]
    os.makedirs(outdir, exist_ok=True)

    instruction = open(instr_file).read().strip()

    if condition == "reset":
        prefix = ""
    else:
        prefix = extract_atom(atoms_file, condition)
        if not prefix:
            print(f"ERROR: condition '{condition}' produced an EMPTY prefix — atoms file "
                  f"missing or marker malformed. Refusing to run (would be a silent reset).",
                  file=sys.stderr)
            return 2

    docker_hint = (
        "You are working in the repository at your current directory. To run Python (3.7 + the "
        "project's deps, not on the host), use:\n"
        f"  docker exec cgcl-mat-box bash -c 'cd {cwd} && python3 -m pytest -q -p no:cacheprovider -o addopts= ...'\n"
        "When done, output a one-line summary of what you implemented."
    )
    prompt = f"{prefix}\n\n---\n\n{instruction}\n\n---\n{docker_hint}" if prefix else f"{instruction}\n\n---\n{docker_hint}"

    manifest = {
        "condition": condition,
        "prefix_chars": len(prefix),
        "prefix_sha256": sha(prefix),
        "instruction_sha256": sha(instruction),
        "prompt_sha256": sha(prompt),
        "container_workdir": cwd,
        "model": os.environ.get("CGCL_MODEL", "macaron-v1-coding-venti"),
        "base_url": os.environ.get("ANTHROPIC_BASE_URL", "https://mintcn.macaron.xin"),
        "budget_sec": 600,
    }
    with open(os.path.join(outdir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    with open(os.path.join(outdir, "prompt.txt"), "w") as f:
        f.write(prompt)
    print(json.dumps(manifest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
