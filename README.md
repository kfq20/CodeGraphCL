# CodeGraphCL

A graph-structured benchmark for **continual learning in coding agents**. The thesis: a
coding agent's CL ability is best measured not by history length, but by whether it correctly
**produces, propagates, combines, updates, and suppresses** experience across a task graph —
and whether that experience changes later behavior on real, executable engineering tasks.

> **Status:** research scaffold, R2 complete. One task family (httpx `start_tls`) is
> materialized through the full Executable Task Gate and an intervention harness is running.
> See `R2_MILESTONE.md` for the honest, no-over-claiming status.

---

## What this repo contains

```
CodeGraphCL/
├── docs/
│   ├── CODEGRAPHCL_RESEARCH_PROPOSAL.md   # the full formulation (Task Graph, motifs, protocol)
│   └── ref_codebase.md                    # survey of candidate repos + phased plan
├── TODOs/todo1.md                         # the review that reshaped R1→R2 (read this first)
├── R2_MILESTONE.md                        # ★ current honest status + environment recipe
├── audit/                                 # L3 semantic audits of two task families
│   ├── ripgrep_ignore_precedence_R2.md    #   Update chain (c2→c3→c4)
│   └── httpx_concurrency_R2.md            #   Parity → Update (T_A→T_B→T_C)
├── mining/                                # R1 reconnaissance: co-change → motif segments
│   ├── repo_config.py  cochange_miner.py  motif_segments.py  export_audit_queue.py
│   ├── EXPLORATION_REPORT_R1.md           #   2469 co-change commits → 102 motif segments
│   └── out/  (gitignored — regenerable)
└── harbor_task/                           # ★ the executable task + intervention harness
    ├── environment/Dockerfile             # materialize (py3.7) | agent (+node+claude) targets
    ├── materialize/                       # SWE-bench-style base-fail/gold-pass/near-miss
    │   ├── verify_materialization.py  verify_nearmiss.py  nodes.json  ENV_RECIPE.md
    │   └── {tA,tB,tC}_{source,verifier}.patch
    ├── steps/
    │   ├── tA_start_tls_asyncio/          # anchor task (instruction leak — can't carry CL)
    │   └── tB_start_tls_trio/             # ★ the node with a REAL edge (minimal instruction)
    ├── run_episode.sh / run_tb_episode.sh # oracle + agent episode runners
    ├── run_agent.sh / run_tb_agent.sh     # host claude (macaron endpoint) per condition
    ├── experience_atoms.md / tB_experience_atoms.md   # reset/correct/irrelevant/wrong atoms
    └── intervention_results.md            # ★ the numbers so far
```

## The two gates that matter right now

1. **Executable Task Gate** — can a mined commit become a behaviorally-reliable task?
   base-fail / gold-pass / PASS_TO_PASS / near-miss, all in Docker. **httpx T_A and T_B both
   pass.** The near-miss gate proves the verifier checks behavior, not method-existence.
2. **Causal Dependency Gate** — does history produce a measurable difference? **In progress on
   T_B** (4 arms: reset/correct/irrelevant/wrong). T_B has a real edge: T_A's `start_tls`
   contract is in the code tree, not the prompt — so Reset re-derives it (cost) while Correct
   gets it directly. Pass-rate may saturate; the expected signal is **cost**.

## How to run (on this hostile fuse-overlayfs host)

The host has ~9 recorded quirks (docker stdout dropped, bind-mounts must be empty, root can't
use `--dangerously-skip-permissions`, pytest 4.6 needs py3.7 + pytest-asyncio 0.10, …). All in
`R2_MILESTONE.md` § "Environment findings" and `harbor_task/materialize/ENV_RECIPE.md`.

```bash
# 1. clone the 5 upstream repos (blob-filter, history intact)
bash mining/fetch_repos.sh  # (not yet written; repos are gitignored)

# 2. build the materialize image (py3.7 + pinned 2019 httpx deps + offline wheels baked)
cd harbor_task && docker build -t codegraphcl-httpx-2019:mat -f environment/Dockerfile --target materialize environment/

# 3. start a long-lived container (provides the py3.7 env; claude runs on HOST)
docker run -d --name cgcl-mat-box --mount type=bind,src=/tmp/cgcl_box_pool,dst=/pool \
  -v /tmp/cgcl_wheels:/wheels:ro codegraphcl-httpx-2019:mat sleep infinity

# 4. oracle sanity (free; gold injected; must return reward=1)
bash run_tb_episode.sh oracle tb_oracle

# 5. agent intervention (one condition; macaron endpoint must be in env)
bash run_tb_episode.sh agent tb_reset_1 reset
```

## What is NOT claimed

- **No causal result yet.** T_B arms are running; N is smoke-sized. Nothing is concluded about
  whether history helps.
- **T_A can't carry the CL signal** — its instruction leaks the contract. Documented in
  `harbor_task/intervention_results.md`.
- **T_B/T_C agent results pending** beyond reset; ripgrep audit stands at semantic-only (no
  Rust toolchain on this host).

## Next steps (for whoever picks this up)
1. Finish T_B's correct/irrelevant/wrong arms; compare **cost** (tokens/time/tools) not just
   reward. If Reset saturates at reward=1, that's expected — the edge lives in cost.
2. T_C (Update: `backend.start_tls` → `stream.start_tls`, return new stream) + the
   stale-history arm — the strongest CL test.
3. Fix the T_B hermetic verifier's port reuse across parallel episodes if scaling N.
4. ripgrep materialization (needs Rust toolchain) — its Update chain is audited but un-run.
