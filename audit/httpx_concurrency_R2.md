# Audit R2 — httpx / concurrency (start_tls Parity+Update chain)

> Promotes the R1 `httpx/concurrency` segment from **L1–L2 (co-change)** to **L3 (semantically
> audited)**. Motif labels are audited hypotheses, NOT causally verified yet.
>
> **CORRECTION (post-review):** This is NOT a Fork motif in the strict sense, and the family
> is NOT a Join. The true structure is a linear chain `T_A → T_B → T_C`:
> - `T_A → T_B`: a contract propagates to a second backend — **Direct / Parity** (not Fork;
>   Fork requires two *independent* targets; here T_B subsumes T_A).
> - `T_B → T_C`: an established contract is revised — **Update**.
> - feeding the T_A/T_B contract to T_C: **Stale History** (the old "mutate in place" is stale).
> This is **not** Join: T_A and T_B are not two non-overlapping combinable sources; T_B
> already inherits and extends T_A.
>
> **Edge strength correction:** the original "T_A's experience is *required* to solve T_B"
> is **too strong**. T_B's Base snapshot already *contains* T_A's code (`ConcurrencyBackend.start_tls`
> signature + asyncio impl + test are all in the tree at T_B's base). A Reset agent can read
> that code and re-derive the contract. So the edge is **beneficial, not required**: experience
> should reduce the *cost* of locating and re-deriving the contract (fewer reads, fewer test
> attempts, faster first correct attempt), not gate success. The experiment must measure cost
> metrics, not only pass rate; if Reset saturates near 100%, the edge lives in cost, not correctness.

## 1. The chain

| node | sha | date | subject | locus |
|---|---|---|---|---|
| T_A (producer) | `1872ae873b` | 2019-08-24 | Add `ConcurrencyBackend.start_tls()` (#263) | `base.py` + `asyncio.py` |
| T_B (target 1) | `38a136833f` | 2019-10-10 | Add `start_tls` to Trio backend (#467) | `trio.py` + `test_concurrency.py` |
| T_C (target 2) | `644e8fc5b6` | 2019-10-20 | Make start_tls a method on streams & return a new stream (#484) | `base.py` + `asyncio.py` + `trio.py` |

**Ancestry:** `merge-base --is-ancestor T_A T_B` = YES; T_B is-ancestor T_C = (to confirm) —
linear on `master`. Each task's `Base = parent(sha)`, snapshot-isolated (proposal §3.5):
experience propagates only via agent session memory, not via file state.
**Key caveat:** because the trunk is linear and T_A's code lands *before* T_B, T_B's Base
**already contains T_A's implementation** — the contract is re-derivable by reading the tree.
This is why the edge is beneficial-not-required.

## 2. The recurring invariant — asyncio/trio backend parity

httpx (2019) abstracted concurrency behind `ConcurrencyBackend` (`base.py`) with two concrete
backends `AsyncioBackend` (`asyncio.py`) and `TrioBackend` (`trio.py`). The invariant under
repeated revision: *both backends expose the same `ConcurrencyBackend` interface with
behaviorally-equal semantics*. `start_tls` is the cleanest instance:
- T_A *introduces* `start_tls` on `ConcurrencyBackend` (abstract) + `AsyncioBackend` (impl) + a test.
- T_B *propagates* it to `TrioBackend`, matching the signature T_A established.
- T_C *revises* the contract: `start_tls` moves from the backend onto the stream and returns a *new* stream.

## 3. The candidate experience-dependency edges (beneficial, not required)

### Edge `T_A ──e,parity──> T_B`  (Direct / Parity; beneficial)

| field | value |
|---|---|
| **Producer task (T_A)** | Declare `start_tls` on `ConcurrencyBackend` (abstract stub) + implement on `AsyncioBackend` + add `test_start_tls_on_socket_stream`. |
| **Experience atom (e)** | *`start_tls` is part of the `ConcurrencyBackend` interface contract, signature `(stream, hostname, ssl_context, timeout) -> stream`; implementing it for a backend means wrapping the existing transport in an SSL layer so the returned stream reports a cipher.* (The precise signature is a *real product contract* T_A established, so naming it is not leakage — it's the lesson.) |
| **Evidence** | T_A: `base.py` abstract stub (L116-124) + `asyncio.py` impl (L194-237) + new test. T_B: `trio.py` `start_tls` with the *same signature* (L171-196). |
| **Consumer decision (T_B)** | To add `start_tls` to Trio, the agent must decide the signature, the return shape, and the timeout semantics. T_A's contract points at the right family of answers. **However** — since T_B's Base already contains T_A's code, a Reset agent can re-derive this by reading `base.py`/`asyncio.py`. So the experience reduces *cost* (locating the contract, fewer false starts), not *solvability*. |
| **Scope** | `httpx/concurrency/{base,asyncio,trio}.py` + `tests/test_concurrency.py`, 2019 backend era. |
| **Alternative explanation** | Plausible: both touch backend files by necessity. **Rejected as full explanation:** T_B's `start_tls` signature is byte-identical to T_A's abstract declaration — T_B is causally downstream of T_A's contract, not coincidental overlap. |
| **Leakage check** | The atom names the interface contract + behavioral expectation, NOT `AsyncioBackend`, `trio.SSLStream`, or `loop.start_tls`. An agent given the atom + T_B's task could plausibly arrive at T_B's fix. **Passes.** |
| **Cost metrics that matter** (since pass-rate may saturate): time, tokens, tool calls, file reads, test attempts, whether first attempt picks the right signature/return. |

### Edge `T_B ──e,update──> T_C`  (Update; the real CL test)

T_C revises the contract T_A/T_B established: `backend.start_tls(stream, ...)` → `stream.start_tls(...)`,
returning a *new* stream. **This is the strongest CL edge in the family** — a genuine
revision where the old contract is *stale*. Feeding the T_A/T_B "mutate in place" atom to T_C
is the **Stale History intervention**: it should either mislead (agent writes the old shape) or
at minimum cost extra time to reconcile against the now-different code.

## 4. Corrected family

| node | commit | role | motif (corrected) |
|---|---|---|---|
| T_A | `1872ae873b` | establish `start_tls` contract + asyncio impl + test | anchor |
| T_B | `38a136833f` | propagate to Trio backend | **Parity** (beneficial, not required) |
| T_C | `644e8fc5b6` | revise contract: move to stream, return new stream | **Update** |
| T_neg (stale intervention) | synthetic | feed T_A/T_B "mutate in place" atom to T_C | **Stale History** |

**Experience atoms (corrected, no leakage):**
1. *(T_A)* `start_tls` is a `ConcurrencyBackend` method, signature `(stream, hostname, ssl_context, timeout) -> stream`; it wraps the transport in SSL and the stream reports a cipher afterward. *(signature is a real product contract — naming it is legitimate)*
2. *(T_B → T_C, stale)* The contract was *revised*: `start_tls` moved onto the stream and returns a *new* stream, not mutate-in-place. Atom #1's shape is **stale for T_C**.

**Removed from consumer decision (per review):** "the test must be parametrized across backends."
Benchmark measures behavioral correctness, not gold's test-writing style. An agent that writes
a correct Trio `start_tls` but doesn't refactor the test into a parametrized form must still
pass the hidden verifier. The verifier checks behavior, not test layout.

**Hard-negative redesign (per review):** the original "never strip / each backend independent"
was too obviously wrong. A stronger design uses a *scope-plausible but inapplicable* experience:
e.g., the global-gitignore relative-to-CWD rule (a real invariant from httpx's transport layer,
correct in its own scope but irrelevant to Trio `start_tls`'s signature/return). This tests
whether the agent understands experience *scope*, not whether it rejects an absurd statement.

## 5. Materialization plan (per TODO §3)

For each of {T_A, T_B, T_C}: Base=parent(sha); split source/verifier patches;
`Base+verifier` FAIL; `Base+source+verifier` PASS; Base existing tests PASS_TO_PASS.
Reject mixed/dep-bump commits (all three are clean single-purpose — verified by `--stat`).
T_C is an intentional contract revision — flag it; its base-fail is *structural*
(old `start_tls` shape vs new verifier asserting new-stream return), the legitimate
"intentional update" case.

## 6. Decision

**Proceed to materialize {T_A, T_B, T_C} in Docker (python:3.7 + pytest 4.6.11 +
pytest-asyncio 0.10.0 + trio).** Edges are **beneficial candidate** edges pending
intervention results; pass-rate may saturate, so the experiment reports **cost metrics**
alongside correctness. T_C is the strongest CL test (Update + Stale).
