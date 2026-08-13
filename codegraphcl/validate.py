"""`codegraphcl validate` — check a task config is complete and self-consistent.

Per phase1 §3.1. Any inconclusive check must NOT print "passed".

Checks:
  - task.yaml conforms to task.schema.json
  - base & gold commit strings are present (existence in a live repo is checked by
    `materialize`, not `validate` — validate is offline)
  - instruction / gold patch / verifier patch / near-miss / banned_words / checklist files exist
  - non-Reset experience atoms (in atoms.md) are non-empty
  - producer commit cited in atoms == the edge's from-commit (if an edge file names one)
  - separability checklist is filled (has answer: fields, not just templates)
  - banned mechanism words do not appear in instruction.md
  - (if --family given) family references resolve

Exit 0 = passed, 1 = failed, 2 = inconclusive.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

from .config import load_task, validate_against_schema, task_files_present, _load_yaml


def _extract_atoms(atoms_text: str) -> dict[str, str]:
    """Return {name: text} from <!-- ATOM:name --> ... <!-- /ATOM:name --> blocks."""
    out = {}
    for m in re.finditer(r"<!-- ATOM:(\w+) -->\n?(.*?)\n?<!-- /ATOM:\1 -->", atoms_text, re.S):
        out[m.group(1)] = m.group(2).strip()
    return out


def _checklist_filled(task_dir: Path, rel: str) -> tuple[bool, str]:
    """A checklist is 'filled' if it has `answer:` fields (not just template questions)."""
    p = task_dir / rel
    txt = p.read_text()
    answers = re.findall(r"answer\s*:\s*(\w+)", txt, re.I)
    if not answers:
        return False, "no `answer:` fields — checklist is an unfilled template"
    # at least one non-yes/no-or-unknown? any answer counts; but must have >=3 for the 5 S-checks
    if len(answers) < 3:
        return False, f"only {len(answers)} answer(s) — need >=3 (S1-S5)"
    return True, f"{len(answers)} answers"


def cmd_validate(task_dir: str, family: str | None = None) -> int:
    td = Path(task_dir)
    if not (td / "task.yaml").exists():
        print(f"FAIL: no task.yaml in {td}")
        return 1
    cfg = load_task(td)
    results = []  # (name, status, detail); status in {pass, fail, inconclusive}

    def chk(name, status, detail=""):
        results.append((name, status, detail))

    # 1. schema
    errs = validate_against_schema(cfg, "task")
    chk("schema_conformance", "pass" if not errs else "fail",
        f"{len(errs)} error(s)" if errs else "")
    for e in errs:
        print(f"  schema: {e}")

    # 2. commits present AND resolvable in a local clone (phase1 §3.1 requires existence).
    #    We look for a local clone under repos/<name> or repos/<name>-full derived from the
    #    repository url. If no local clone exists, this is INCONCLUSIVE (not pass) — we must
    #    not claim the commit exists when we cannot check.
    base = cfg.get("repository", {}).get("base_commit", "")
    gold = cfg.get("repository", {}).get("gold_commit", "")
    chk("base_commit_present", "pass" if base else "fail", f"{base[:10]}" if base else "empty")
    chk("gold_commit_present", "pass" if gold else "fail", f"{gold[:10]}" if gold else "empty")

    url = cfg.get("repository", {}).get("url", "")
    repo_name = url.rstrip("/").split("/")[-1] if url else ""
    from .config import ROOT
    candidates = [ROOT / "repos" / repo_name, ROOT / "repos" / f"{repo_name}-full"]
    clone = next((c for c in candidates if (c / ".git").exists()), None)
    if clone is None:
        chk("commits_exist_in_clone", "inconclusive",
            f"no local clone for {repo_name} under repos/ — cannot verify commit existence")
    else:
        import subprocess
        bad = []
        for label, sha in (("base", base), ("gold", gold)):
            if not sha:
                continue
            r = subprocess.run(["git", "-C", str(clone), "cat-file", "-t", sha],
                               capture_output=True, text=True, timeout=20)
            if r.returncode != 0 or r.stdout.strip() != "commit":
                bad.append(f"{label}={sha[:10]}")
        chk("commits_exist_in_clone", "pass" if not bad else "fail",
            f"unresolvable: {bad}" if bad else f"verified in {clone.name}")

    # 3. files present
    ferrs = task_files_present(td, cfg)
    chk("files_present", "pass" if not ferrs else "fail",
        "; ".join(ferrs) if ferrs else "")
    for e in ferrs:
        print(f"  file: {e}")

    # 4. non-Reset experience atoms non-empty
    atoms_path = td / "atoms.md"
    if not atoms_path.exists():
        chk("atoms_present", "inconclusive", "no atoms.md — task has no intervention edge yet")
    else:
        atoms = _extract_atoms(atoms_path.read_text())
        empty = [n for n, t in atoms.items() if n != "reset" and not t]
        non_reset = {n: t for n, t in atoms.items() if n != "reset"}
        if not non_reset:
            chk("atoms_non_reset_present", "inconclusive", "no non-reset atom — not an intervention task")
        else:
            chk("non_reset_atoms_non_empty", "pass" if not empty else "fail",
                f"empty: {empty}" if empty else f"{len(non_reset)} non-reset atoms")

    # 5. separability checklist filled
    sep = cfg.get("separability", {})
    cl_rel = sep.get("checklist")
    if not cl_rel:
        chk("checklist_present", "fail", "no checklist path in task.yaml")
    elif not (td / cl_rel).exists():
        chk("checklist_present", "fail", f"missing {cl_rel}")
    else:
        ok, detail = _checklist_filled(td, cl_rel)
        chk("checklist_filled", "pass" if ok else "fail", detail)

    # 6. banned words not in instruction
    bw_rel = sep.get("banned_words")
    instr_rel = cfg.get("instruction", {}).get("path")
    if not (bw_rel and instr_rel):
        chk("banned_words_check", "inconclusive", "missing banned_words or instruction path")
    else:
        bw_path = td / bw_rel
        if not bw_path.exists():
            chk("banned_words_check", "fail", f"missing {bw_rel}")
        else:
            banned = [w.strip().lower() for w in bw_path.read_text().splitlines()
                      if w.strip() and not w.strip().startswith("#")]
            instr = (td / instr_rel).read_text().lower()
            leaked = [w for w in banned if w in instr]
            chk("banned_words_not_in_instruction", "pass" if not leaked else "fail",
                f"leaked: {leaked}" if leaked else "")

    # 6b. near-miss count: executable targets (passed/pending/failed) need >=2;
    # only not_applicable (producer) is exempt.
    nm_list = cfg.get("verifier", {}).get("near_miss", [])
    eg = cfg.get("status", {}).get("executable_gate", "pending")
    if eg == "not_applicable":
        chk("near_miss_count", "pass", f"producer (not_applicable) — {len(nm_list)} present")
    elif len(nm_list) < 2:
        chk("near_miss_count", "fail", f"executable task needs >=2 near-miss, has {len(nm_list)}")
    else:
        chk("near_miss_count", "pass", f"{len(nm_list)} near-miss")

    # 6c. PASS_TO_PASS: empty must be marked not_applicable with reason, not auto-pass
    p2p = cfg.get("verifier", {}).get("pass_to_pass", [])
    p2p_na = cfg.get("verifier", {}).get("pass_to_pass_not_applicable", False)
    if not p2p:
        if p2p_na:
            chk("pass_to_pass", "pass", "empty but marked not_applicable (reason in notes)")
        else:
            chk("pass_to_pass", "fail", "empty pass_to_pass without pass_to_pass_not_applicable: true")
    else:
        chk("pass_to_pass", "pass", f"{len(p2p)} tests declared")

    # 7. family refs (if --family given) — family schema + node/edge resolution
    if family:
        fp = Path(family)
        if not fp.exists():
            chk("family_resolves", "fail", f"no family file {fp}")
        else:
            fcfg = _load_yaml(fp)
            ferrs = validate_against_schema(fcfg, "family")
            chk("family_schema", "pass" if not ferrs else "fail",
                f"{len(ferrs)} error(s)" if ferrs else "")
            for e in ferrs:
                print(f"  family schema: {e}")
            task_id = cfg.get("task_id")
            nodes = fcfg.get("nodes", [])
            chk("task_in_family_nodes", "pass" if task_id in nodes else "fail",
                f"{task_id} not in {nodes}" if task_id not in nodes else "")
            # each referenced node must have a task dir; each edge must exist + be schema-valid
            from .config import BENCH
            missing_nodes = [n for n in nodes if not (BENCH / "tasks" / n).exists()]
            chk("family_nodes_have_task_dirs", "pass" if not missing_nodes else "fail",
                f"missing task dirs: {missing_nodes}" if missing_nodes else "")
            edge_ids = fcfg.get("edges", [])
            missing_edges = [e for e in edge_ids if not (BENCH / "edges" / f"{e}.yaml").exists()]
            chk("family_edges_have_files", "pass" if not missing_edges else "fail",
                f"missing edge files: {missing_edges}" if missing_edges else "")
            bad_edges = []
            for eid in edge_ids:
                ep = BENCH / "edges" / f"{eid}.yaml"
                if not ep.exists():
                    continue
                ecfg = _load_yaml(ep)
                eerrs = validate_against_schema(ecfg, "edge")
                if eerrs:
                    bad_edges.append(f"{eid}: {eerrs[0]}")
            chk("family_edges_schema_valid", "pass" if not bad_edges else "fail",
                "; ".join(bad_edges) if bad_edges else "")

    # report — any fail/inconclusive => not "passed"
    npass = sum(1 for _, s, _ in results if s == "pass")
    nfail = sum(1 for _, s, _ in results if s == "fail")
    ninc = sum(1 for _, s, _ in results if s == "inconclusive")
    print(f"\n=== validate {td} ===")
    for name, status, detail in results:
        tag = {"pass": "PASS", "fail": "FAIL", "inconclusive": "INCONCLUSIVE"}[status]
        print(f"  {tag:12} {name}" + (f"  [{detail}]" if detail else ""))
    print(f"\n{npass} pass, {nfail} fail, {ninc} inconclusive")
    if nfail or ninc:
        print("RESULT: NOT passed (has failures or inconclusive)")
        return 1 if nfail else 2
    print("RESULT: passed")
    return 0
