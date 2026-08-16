结论：Phase 4 的规模化资产基本建成了，但目前还不能视为真正冻结的 `v1-rc1`。问题不是 benchmark 路线失败，而是 Agent 把“达到目录数量”误当成了“通过发布门槛”。

我核验 `1a38b33` 后的实际情况：

| 项目                              |                                        仓库实际状态 | 判断                                                               |
| ------------------------------- | --------------------------------------------: | ---------------------------------------------------------------- |
| repo / language / task / family |                               5 / 4 / 65 / 34 | ✅                                                                |
| executable gate passed          |                         60，另有 2 pending、3 N/A | ✅ 但应称“60 executable”，不是 65                                       |
| 正式 executable edges             |                                            35 | ❌ 不是 41；6 条边连接了 pending/N/A 节点                                   |
| Diagnostic streams              | 10 条，全部是 `hard_negative`，共 30 个 task episodes | ❌ 不是 70 条/7 motifs，也未达到 40 families、200 episodes                 |
| Integrated streams              |                                          25 条 | ⚠️ 数量达到，但 10/25 含非 release/non-executable 节点                     |
| release_core                    |                                  YAML 标签写成 60 | ❌ 缺少逐任务证据；24 个 YAML 注释仍明确写着“尚未发布、需要 alternative-correct control” |
| Phase 4 smoke                   |                               仅 5 个 task 重新物化 | ❌ 没有 Diagnostic Reset/Stateful 与 5 条 Integrated 端到端模型运行          |
| 冻结 tag                          |                         远端 tag 实际指向 `9847e93` | ❌ 不是汇报中的 `1a38b33`                                               |
| 报告/Data Card/License            | 仍写 `IN PROGRESS`、0 release-core、Viper pending | ❌ 文档没有冻结                                                         |

最核心的生成器 bug 是：七类 diagnostic motif 每次都写到同一个 `streams_seed42.jsonl`，后一次覆盖前一次，所以最终只剩 10 条 hard-negative。[generate_streams.py](sandbox:/workspace/scratch/faa0d0a7cc34/CodeGraphCL-review/codegraphcl/generate_streams.py)

另外，项目自己的 validator 虽然输出 `PASSED`，但它目前只检查 task/edge/family/repo/language 数量，不检查 release-core 证据、stream 分布、正式 edge 端点和 smoke 完整性。因此这个 `PASSED` 不能作为冻结依据。

## 现在给 Agent 的 Phase 4.1 目标

> 暂停新增 task、repo 和小型因果实验。Phase 4.1 的唯一目标是在 1–2 天内完成 CodeGraphCL-v1 的 release audit，修复生成、验证和文档一致性，并冻结一个机器可复现的 `codegraphcl-v1-rc2`。
>
> 1. 将没有逐任务 release 证据的节点恢复为 `executable_candidate`。优先审核至少 40 个核心节点；每个 `release_core` 必须记录 verifier independence、hidden-test stability、alternative-correct implementation 或 semantic mutation、instruction audit 的独立证据。不得用两个重复 SHA 的全局案例替代 60 个任务的逐任务验证。
> 2. 正式 edge 的两个端点必须都是 executable task。当前只有 35 条合格边；从已有 60 个任务中补足或重新审计至少 5 条，不得使用 `httpx_tA/tB/tC`、`ripgrep_c2` 等 pending/N/A 节点补数。
> 3. 修复 stream generator：不同 motif 使用独立文件或一次性合并输出，禁止覆盖；显式区分 `family_id` 与 `episode_id`；生成至少 40 个 Diagnostic families、200 个 episodes，覆盖 Direct、Delayed、Fork、Join、Scope、Update/Stale、Hard Negative。所有正式 stream 只能引用 release-core 节点。
> 4. Integrated streams 保留至少 20 个 family，但必须真正由拓扑 motif 构成，不能仅把随机跨 repo distractor 标记为 multi-motif；清除包含 pending、rejected、diagnostic-only 节点的 stream。
> 5. 扩展 `validate-benchmark` 并补充 `validate_stream.py`，让以下任一问题直接失败：错误 tier、非 executable edge 端点、motif 配额不足、stream 覆盖写、重复 family、dangling ID、非 core 正式节点、缺失报告或 smoke 工件。
> 6. 按原 Phase 4 协议完成 smoke：所有正式任务重新 materialize；至少 10% Diagnostic families 用同一个固定模型运行 Reset 与 Native Stateful；至少 5 条 Integrated streams 做完整端到端运行。记录 session continuity、snapshot isolation、reward、tokens、turns、tools、elapsed 和 infrastructure failure。
> 7. 从机器结果重新生成 `BENCHMARK_V1_REPORT.md`、`DATA_CARD.md`、`LICENSES.md` 及三个 Phase 4 CSV。报告不得手工填写与 validator 不一致的数字。
> 8. 不移动已经发布的 `rc1` tag。验收全部通过后，在最终 commit 上创建 `codegraphcl-v1-rc2`，并记录 commit SHA、数据清单 hash 和生成命令。
>
> 验收输出必须是一张机器生成的表，至少包括：release-core 数、正式 executable edge 数、各 motif family/episode 数、Integrated family 数、非 core 引用数、全量 materialization 成功率、模型 smoke 成功率以及 tag 指向。

相关原始要求就在 [Phase 4 计划](sandbox:/workspace/scratch/faa0d0a7cc34/CodeGraphCL-review/TODOs/phase4.md)，当前报告和 smoke 证据分别见 [BENCHMARK_V1_REPORT.md](sandbox:/workspace/scratch/faa0d0a7cc34/CodeGraphCL-review/BENCHMARK_V1_REPORT.md) 与 [phase4_smoke.csv](sandbox:/workspace/scratch/faa0d0a7cc34/CodeGraphCL-review/runs/phase4_smoke.csv)。

完成这个短收尾后，就应立即进入多模型 Phase 5：在同一个 `rc2` 上跑 GLM-5.2 与 Qwen-30B，比较 Reset/Stateful、七类图结构、distance、parent count、负迁移、跨 repo 和轨迹差异。那才是论文的主结果阶段。
