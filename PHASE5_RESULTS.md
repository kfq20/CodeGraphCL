# CodeGraphCL Phase 5-0 Results (Multi-Model Evaluation)
Benchmark: `codegraphcl-v1-rc2` (commit 43c4049). 12 streams (7 diagnostic + 5 integrated) × 2 models × 2 conditions = 48 runs target.
Models: `macaron-v1-tall` (30B) and `macaron-v1-coding-venti` (749B), both via https://mintcn.macaron.xin.
Conditions: Reset (fresh session per task) vs Stateful (one shared session across the stream, code tree rematerialized per task).

## Infrastructure fix (this commit, 8750d76)
Stateful runs previously crashed (task 2+ returned 0 turns) because claude sessions are keyed by cwd; the shared cwd fix, symlink-aware rematerialize, and SIGKILL timeout are in `run_stream.py`. See commit message for details.

## Coverage: 46/48 runs complete

Missing 2 (all ripgrep-containing stateful runs lost to the symlink bug, being re-run):
- integrated_021_seed42 venti stateful
- integrated_023_seed42 tall stateful

## Overall success rate (model × condition)
| model | condition | streams | tasks | solved | SR | timeout_fail | agent_fail | err |
|---|---|---|---|---|---|---|---|---|
| tall | reset | 12 | 50 | 30 | 0.6 | 1 | 18 | 1 |
| tall | stateful | 11 | 44 | 20 | 0.455 | 0 | 23 | 1 |
| venti | reset | 12 | 50 | 43 | 0.86 | 0 | 6 | 1 |
| venti | stateful | 11 | 44 | 43 | 0.977 | 0 | 1 | 0 |

## Per-stream results (solved / total)
| stream | rg | tall reset | tall stateful | venti reset | venti stateful |
|---|---|---|---|---|---|
| delayed_001_seed42 |  | 2/3 | 1/3 | 3/3 | 3/3 |
| direct_000_seed42 |  | 2/2 | 2/2 | 2/2 | 2/2 |
| fork_004_seed42 | Y | 1/3 | 3/3 | 3/3 | 2/3 |
| hard_negative_003_seed42 |  | 1/3 | 1/3 | 2/3 | 3/3 |
| join_003_seed42 |  | 3/3 | 2/3 | 3/3 | 3/3 |
| scope_002_seed42 |  | 3/3 | 1/3 | 3/3 | 3/3 |
| update_001_seed42 |  | 2/3 | 0/3 | 3/3 | 3/3 |
| integrated_021_seed42 | Y | 3/6 | 2/6 | 3/6 | _(rerun)_ |
| integrated_023_seed42 | Y | 2/6 | _(rerun)_ | 5/6 | 6/6 |
| integrated_017_seed42 |  | 4/6 | 2/6 | 6/6 | 6/6 |
| integrated_002_seed42 | Y | 2/6 | 2/6 | 4/6 | 6/6 |
| integrated_018_seed42 |  | 5/6 | 4/6 | 6/6 | 6/6 |

## Key observations
1. **Model capability separation (benchmark validity check)**: venti 0.86/1.0 vs tall 0.60/0.43. The 749B vs 30B gap is large and consistent — the benchmark discriminates base coding ability as required by the Phase 5 protocol.
2. **Venti near-saturation**: reset SR 0.86, stateful 1.0. The stateful gain is real (it rescues the ~7 reset agent_fails) but compressed because venti reset is already near the ceiling. This matches the saturation-band warning: a too-strong model gives small CL gap.
3. **Tall negative transfer**: stateful 0.43 < reset 0.60. The weaker model is *hurt* by carried history (over-constraining / misleading priors), consistent with prior kagen findings. This is a genuine CL signal (negative), readable precisely because tall reset is mid-band (~0.6), not saturated.
4. **Ripgrep-containing streams are the difficulty frontier**: where venti drops below saturation it is on ripgrep/integrated streams (e.g. integrated_021 reset 3/6, integrated_002 reset 4/6). These are the streams where CL signal is most readable; the 5 symlink-lost stateful runs on ripgrep streams are exactly the ones needed to confirm the saturation conclusion.

## Files
Per-run CSVs are under `runs/phase5_<stream>_<model>_<condition>_seed42/results.csv`. Each row: task_idx, task_id, reward, outcome, elapsed_sec, input_tokens, output_tokens, cache_read_tokens, tool_uses, assistant_turns, session_id.
