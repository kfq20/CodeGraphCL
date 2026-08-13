# Phase 2.1 closeout — corrected status after review

Written after the 6-correction review of the phase2 report. This supersedes any earlier claim
that phase2 was "complete" on the causal-verification axis.

## What phase2 delivers (accepted)

A **runnable candidate Task/Edge Bank** — not yet a Verified Graph that can emit a formal task
stream.

| asset | target | actual | status |
|---|---|---|---|
| executable nodes | 20-30 | 20 (all 4/4 gate, each with 2 near-miss) | MET (as **candidates**) |
| families | 6-8 | 8 active family IDs + 1 rejected (httpx) | MET; 9 family YAMLs now on disk |
| semantic edges | 10-15 | 10 (incl. 2 rejected httpx) | MET |
| protocol-ready edges | >=8 | **8** (NOT 9) | lower bound MET |

**Why 8 and not 9:** `httpx_tA_to_tB` cannot count. Its producer node `httpx_tA` has
`separability_gate: failed` (the instruction leaks the contract: signature + loop.start_tls hint
+ cipher behavior) and `executable_gate: not_applicable`. Its near-miss set is empty and the old
N=3 result came from the pre-unification runner. It is a **diagnostic-only** edge, kept as
negative-transfer evidence, and is now marked `semantic_audit: failed` /
`causal_verification: rejected` so it stops being counted.

**Node tier:** all 20 nodes are marked `verification_tier: executable_candidate`. They pass the
materialize gate and near-miss anti-hardcoding, but final publish still requires the
**alternative-correct implementation control** from the proposal (>=1 plausible-but-different
patch that ALSO passes the verifier), to rule out that the verifier only accepts the gold shape.

## What phase2 does NOT deliver (not accepted)

**Causal screening is incomplete.** Of the 8 protocol-ready edges:

| coverage | count | edges |
|---|---|---|
| full 4-arm N=1 | 4 | c4->c5, hasheader->removeheader, clap newline, c3->c4 |
| reset-only probe | 1 | c2->c3 (infra-failed; reward-path bug — now fixed, re-run in flight) |
| not run | 3 | getschemas->cleanid, emptybody->array, c1->cef (runs in flight) |

N=3 was run on exactly 1 edge (c3->c4), which correctly **did not escalate**.

## How the negative result must be stated

**Defensible (what the data supports):**

> In the edges screened so far, no edge passed the Causal Dependency Gate; the one edge escalated
> to N=3 did not reproduce N=1's condition ordering.

**NOT defensible (earlier over-reads, now retracted):**

- ~~"The current 20-node bank has been shown to contain no causal experience edge."~~ — 3 active
  edges were never run and 1 was only a failed reset probe.
- ~~"correct is the worst prior" / "variance dominates at the wall"~~ — n=3 per condition is a
  **screening** sample, not a statistical estimate of a causal effect. The N=3 raw result supports
  **non-escalation**, not a negative causal effect.

## Screening criterion — corrected

The earlier "reset solves in 200–400s" framing is a **working hypothesis tied to this model and
this machine**, not a portable rule. Wall-clock shifts with model and hardware.

The more reliable criterion: **under a fixed model and fixed budget, screen on the reset arm's
success rate landing in a non-saturated band (~20–80%).** ~100% reset = too easy (pass-rate
saturates); ~0% = too hard. Run the cheap reset-only probe first; only spend a 4-arm when reset
lands in the non-saturated band.

## Reproducibility fixes shipped this round

| gap | fix |
|---|---|
| `CGCL_MODEL` written to manifest but NOT passed to the agent | `claude --model {model}` now passed explicitly (verified: run manifest records `claude_model_flag`, smoke-tested rc=0) |
| run manifest thin | now records `prompt_sha256`, `atom_sha256`, `image_digest`, `harness_commit` |
| `summarize.py` missing (CLI imported it -> ImportError) | added; regenerates `SUMMARY.md` from `results.csv` with a `Source CSV:` pointer |
| N=1 SUMMARY <-> raw CSV path drift | fixed by regenerating all 12 run summaries through `summarize.py` |
| `protocol-v1` tag | confirmed present on origin (`a27e53c`) |
| c2->c3 `infra_fail` | root cause found: `ripgrep_c3/verifier/test.sh` wrote `printf "$PASS"` — empty PASS wrote an empty reward file (-> "ERR" -> infra_fail) and counts >1 are also classified infra_fail. Now writes binary 0/1; the count stays in `test-stdout.txt` for offline partial-credit analysis |

## Remaining before Phase 3

1. Finish the 3 in-flight fastify edge N=1s -> coverage becomes 7 full N=1 + 1 (c2->c3 re-run).
2. Land the c2->c3 re-run as either a clean N=1 or a documented abandon.
3. Add alternative-correct implementation controls to promote nodes from
   `executable_candidate` to released.
4. Only then re-state any bank-level causal claim.
