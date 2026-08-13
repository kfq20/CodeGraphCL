# Causal Dependency Gate v1 (CodeGraphCL)

The gate that decides whether an edge is a **causally verified experience edge** — i.e. whether
the CodeGraphCL measurement reflects acquisition/use of historical experience rather than generic
coding ability. Used in Phase 3. This document is the pre-registered spec; results are judged
against it, not post-hoc.

## Why a gate

An edge `producer -> consumer` claims the producer's engineering decision, carried as a prior,
changes how the consumer is solved. To be a *causal* claim (not a correlation), the prior must be
the thing that moves the outcome, and rival explanations must be ruled out. The gate is a sequence
of filters that each eliminate one rival explanation.

## The funnel

```
Semantic Audit -> Mechanism Audit -> Separability -> Executable Gate
-> Reset Calibration (N=2) -> 4-arm N=1 -> N=3 screening -> Confirmation
```

### Gate 1 — Semantic Audit

The edge must be real, not inferred from co-occurrence:
- producer commit strictly precedes consumer (`git merge-base --is-ancestor producer consumer`)
- experience statement contains ONLY producer-era knowledge (no consumer discovery leaked)
- producer and consumer operate on the SAME engineering decision
- the consumer's verifier can actually distinguish the correct path from the competing path(s)

Reject if: ancestry fails; statement references consumer-specific discovery; the "edge" is just
"two commits touched the same file."

### Gate 2 — Mechanism Audit (phase3 §2.2)

A YAML block on the edge answering five questions. Every field must be concrete:

```yaml
mechanism_audit:
  reusable_decision:        # what producer established (a decision, not a patch)
  plausible_path_correct:   # consumer path that follows producer's rule
  plausible_path_competing: # consumer path that violates it — must be surface-plausible
  why_instruction_does_not_disambiguate:  # why the symptom-only instruction can't pick the path
  why_correct_history_selects_path:        # how the prior points at the correct path
  why_wrong_history_is_plausible:          # why the stale/wrong prior is a real, not absurd, principle
```

Reject if: the competing path is absurd; reset could trivially derive the answer (consumer tree
already has a full mirror impl / explicit interface / telling comment); the gold patch is a
>100-150-line structural refactor where reset runs the timeout wall.

### Gate 3 — Instruction–Experience Separability

The instruction (symptom) must NOT contain: the function/file/field to change; the ownership or
scope; the precedence order; the specific mechanism; "move from A to B" revision direction; or a
near-rewrite of the producer experience. It may only describe: the observed error, input+output,
expected behavior, reproduction.

Banned-words list per task; `codegraphcl validate` enforces.

### Gate 4 — Executable Gate (existing standard)

base-fail / gold-pass / PASS_TO_PASS-or-NA / ≥2 near-miss from different wrong implementations /
verifier checks external behavior. Node tier = `executable_candidate`.

### Gate 5 — Reset Calibration (N=2)

Before any 4-arm, run Reset twice:
- **0/2 success, both near timeout** → `too_hard`, stop.
- **2/2 success, very low cost** → `saturated_easy`, stop (unless correct history may sharply
  cut exploration cost — keep as efficiency candidate only).
- **≥1 success, not all at the wall** → proceed to 4-arm N=1.

The wall-clock band (e.g. 200–400s) is NOT a hard rule; it is model/machine-dependent. The
portable signal is success-rate in a non-saturated band (roughly 20–80%) under fixed model+budget.

### Gate 6 — 4-arm N=1 preflight

Conditions: Reset / Correct / Irrelevant / Wrong-or-Stale. Escalate to N=3 only if one of:
1. Correct succeeds while Reset or Irrelevant fails;
2. all succeed but Correct clearly fewer turns/tools/runs;
3. Wrong/Stale produces mechanism-consistent failure that Correct avoids;
4. trajectory shows Correct entering the right implementation path earlier, with a
   mechanism-consistent decision difference.

Stop immediately if all-4-succeed with no cost gap, or all-4-fail.

Atom controls (phase3 §3.2): token length within ~10–15%; same format/density; no condition
names (`correct`/`wrong`/`stale`); Irrelevant from same repo + similar granularity but unrelated
to the target mechanism; Wrong/Stale a plausible-but-wrong engineering principle; Correct has no
target file / code / gold impl.

### Gate 7 — N=3 screening (block-randomized)

Not an effect estimate — a screen. Block-randomized; same model/timeout/temperature/tools;
opaque episode IDs; save prompt_sha256 + atom_sha256 + model flag + image digest + harness
commit. Correctness primary, efficiency secondary. Never conclude from a single fastest run.

Status classification after N=3:
| status | meaning |
|---|---|
| `rejected_no_ordering` | no stable direction across conditions |
| `rejected_reversed` | Correct persistently worse than controls |
| `rejected_saturated` | all succeed or all fail |
| `intervention_sensitive` | Correct's directional advantage reproduces |
| `negative_transfer_sensitive` | Wrong/Stale's mechanism-consistent harm reproduces |
| `infrastructure_blocked` | cannot get reliable reward |

### Gate 8 — Confirmation (`causally_verified_v0`)

Minimum standard:
- Correct has a **repeated** directional advantage vs Reset AND Irrelevant;
- Wrong/Stale does NOT get the same advantage;
- the advantage may be success-rate OR efficiency without quality loss;
- trajectory audit is consistent with the pre-registered mechanism;
- the result is NOT explained by atom length, instruction leakage, the timeout wall, or an
  infrastructure error.

Finalists may be extended to N=5/condition; the paper's main experiment may go to N=8–10.

## Anti-tampering rule

Do NOT modify the instruction, the experience provenance, the Gold patch, or the verifier to
obtain a positive result. Negative results (rejected_*), abandoned edges, and infrastructure
failures are retained and reported.

## Natural Stateful (separate, does not gate the edge)

For each `causally_verified_v0` edge: run Natural Stateful (producer→consumer in one native agent
session) vs Reset consumer, N=2 (ideal N=3). Record: producer success; whether the producer
trajectory actually hit the decision; whether the consumer reused files/tests/principles/failures;
Stateful vs Reset success+cost; if Stateful failed, the mode (unextracted / unretained /
unretrieved / misapplied). Valid outcomes: stateful-benefit, oracle-only-benefit,
negative-transfer, no-retention/use. All four are publishable; Natural Stateful is NOT required to
beat Reset for the edge to count as causally verified.
