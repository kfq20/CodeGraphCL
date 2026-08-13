很好。我的判断是：

> **Phase 1 可以正式验收，但验收的是“统一生产框架成立”，不是所有 task 资产都已经达到 benchmark 发布质量。**

现在不要继续围绕 HTTPX/c4 做研究性调试。接下来进入 Phase 2 批量生产，不过开始前先用半天完成一次通用框架质量锁。

## 先做半天的 Quality Lock

我复核 `6b4bc7e` 后发现几个会影响批量生产的通用问题，需要一次性修掉：

1. **Near-miss 失败被错误放行**

   HTTPX near-miss 是 `apply_failed`，但最终 `materialization_result.json` 仍写成 `passed`。所有 `missing/apply_failed/inject_failed/unsupported` 都必须让 Gate 变成 `inconclusive` 或 `failed`，不能算 caught。

2. **Near-miss 数量没有硬约束**

   Schema 应要求至少两个有效 near-miss。当前 c3 只有一个，c4 的一个还没有正确注入。

3. **空 PASS_TO_PASS 被标成通过**

   HTTPX T_B 和 c4 的 `pass_to_pass: []` 不能自动记为 passed。只能：

   * 提供真实 PASS_TO_PASS；
   * 或明确标记 `not_applicable` 并给出理由。

4. **Intervention prompt 仍写死 `cgcl-mat-box`**

   应使用当前任务实际发现的 container，而不是固定 HTTPX 容器。否则 ripgrep agent 可能进入错误测试环境。

5. **补依赖和结果隔离**

   * 添加 `pyproject.toml` 或 requirements，保证干净环境能安装 `jsonschema/PyYAML`；
   * 每次 intervention 使用唯一 `run_id`，不能继续向旧 `results.csv` 追加相同 `ep_000000`；
   * task.yaml 的状态由最新 gate 结果生成，不能在 near-miss 未通过时手写 `executable_gate: passed`。

这些属于框架安全修复，不算改变冻结协议。完成后打一个 `protocol-v1` tag，后续不再改 schema。

## Phase 2：批量生产 Task/Edge Bank

**时间：8 月 14–20 日。**

阶段目标：

> 在冻结协议上批量构建 CodeGraphCL-v0 的任务和经验边，为下一阶段生成真实 task stream 准备数据。

建议目标如下：

| 资产                       |                                             Phase 2 结束目标 |
| ------------------------ | -------------------------------------------------------: |
| 仓库                       |                                               至少 3 个主要仓库 |
| Task families            |                                                    6–8 个 |
| Executable nodes         |                                                  20–30 个 |
| Semantic-audited edges   |                                                  10–15 条 |
| Intervention-ready edges |                                                   至少 8 条 |
| N=1 preflight            |                              所有 intervention-ready edges |
| N=3 causal verification  |                                           只跑 4–6 条有敏感性的边 |
| Motif                    | Update/Stale、Scope/Hard Negative、Direct/Parity，争取一个 Fork |

仓库组合建议：

* **ripgrep**：继续完成 c2→c3→c4；
* **Fastify**：重点找 plugin encapsulation、hook/schema scope；
* **clap**：重点找 builder/derive parity 和 deprecation/update；
* HTTPX 保留为 negative-transfer 与 rejected-task analysis，不再投入主要生产预算。

## 批量生产规则

每个候选 family 都走相同漏斗：

[
\text{Semantic Audit}
\rightarrow
\text{Separability}
\rightarrow
\text{Executable Gate}
\rightarrow
N=1
\rightarrow
N=3
]

严格止损：

* 语义审计最多 2 小时；
* 环境或 verifier 最多半天；
* instruction 泄漏立即 reject；
* Base/Gold 无法稳定复现立即 reject；
* N=1 四组完全饱和且成本也无合理差异，立即停止；
* 只有 N=1 出现 correct benefit 或 wrong/stale harm，才运行 N=3；
* 不为了制造信号修改任务目标或 experience provenance。

特别要注意：Phase 2 的 KPI 不是“成功找到显著结果”，而是生产并筛选足够多的真实候选。Rejected family 也是数据，但至少需要找到若干真正有干预敏感性的边，才能进入 stream construction。

## 给 agent 的总指令

> **Phase 1 验收完成，schema 与 CLI 结构冻结。先用半天完成 protocol-v1 Quality Lock：near-miss 的 missing/apply/inject failure 必须硬失败且至少需要两个；空 PASS_TO_PASS 不得标记 passed；移除 prompt 中固定的 `cgcl-mat-box`；补齐可安装依赖、唯一 run ID 和自动状态同步。完成后打 `protocol-v1` tag。随后进入 Phase 2 批量生产，截止 8 月 20 日达到至少 3 个主要仓库、6–8 个 families、20–30 个 executable nodes、10–15 条 semantic edges 和 8 条 intervention-ready edges。所有候选统一经过 Semantic Audit → Separability → Executable Gate → N=1；只有 N=1 有敏感性的 4–6 条边进入 N=3。单个 family 调试不超过半天，禁止为获得预期信号修改 instruction 或 experience provenance。本阶段不构造正式 task stream。**

Phase 2 完成后，我们才进入真正的 Stream Phase：从 verified edge bank 生成 Diagnostic/Integrated streams，运行 Reset vs Stateful 主实验。
