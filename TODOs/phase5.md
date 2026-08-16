可以，而且 Phase 5 就应该正式做多模型实验。GLM-5.2 和 Qwen-30B 足够作为第一版模型矩阵：一个能力较强、一个较小，可以同时检验 benchmark 是否区分基础编码能力和持续学习能力。

但要注意：不能仅用“GLM 成功率高于 Qwen”证明持续学习。持续学习能力应看同一模型从 Reset 到 Stateful 的变化。

## Phase 5 核心实验

主实验固定：

| 维度               | 设置                                    |
| ---------------- | ------------------------------------- |
| Benchmark        | `codegraphcl-v1-rc2`，commit `43c4049` |
| Models           | GLM-5.2、Qwen-30B                      |
| Memory condition | Reset、Native Stateful                 |
| Diagnostic       | 70 families，7 motifs                  |
| Integrated       | 25 families                           |
| 首轮重复             | 全量 N=1                                |
| 稳健性重复            | 分层子集 N=3                              |
| 代码环境             | 每个 task 独立 base snapshot              |
| Stateful         | 延续 agent session，不延续代码修改              |
| Reset            | 每个节点创建全新 session                      |

全量 N=1 是：

[
95\ \text{streams}\times 2\ \text{models}\times 2\ \text{conditions}
=380\ \text{stream runs}
]

约对应 1,400 个 task executions。然后从每个 motif 分层选3条，再选5条 Integrated，共26条做额外两个 seed：

[
26\times2\times2\times2=208
]

最终约588条 stream runs，规模对 benchmark paper 已经比较合适。

## Phase 5-0：先跑48条预检

在全量实验前，先执行：

* 每个 motif 取1条，共7条 Diagnostic；
* 取5条 Integrated；
* 两个模型；
* Reset、Stateful 两种模式。

即：

[
12\times2\times2=48\ \text{runs}
]

验收条件：

* infrastructure success ≥95%；
* Stateful 确实复用同一个 session；
* task 之间代码树不污染；
* 两个模型的工具协议都正常；
* reward、tokens、turns、elapsed、tool calls、failure type 完整；
* 不要求 Stateful 一定提升。

这48条通过后立刻启动全量，不再回头修改 benchmark。

## 核心指标

至少报告以下四组：

1. 基础能力：

[
SR_{\text{Reset}}
]

衡量模型本身的代码解决能力。

2. 持续学习增益：

[
\Delta_{\text{CL}}
==================

SR_{\text{Stateful}}-SR_{\text{Reset}}
]

这是主指标。GLM 原始成功率更高，不代表其持续学习更强。

3. 归一化增益：

[
\mathrm{NCLG}
=============

\frac{SR_{\text{Stateful}}-SR_{\text{Reset}}}
{1-SR_{\text{Reset}}}
]

用于缓解强模型 Reset 已经很高、提升空间较小的问题。

4. 效率增益：

* token reduction；
* turn reduction；
* elapsed-time reduction；
* solved-task conditional cost。

有时 Stateful 不提高成功率，但显著减少探索成本，这仍然是有效结果。

## 图结构分析

七类 motif 分别分析：

* Direct：直接经验复用；
* Delayed：随依赖距离增加，增益是否衰减；
* Fork：同一经验能否稳定传播到多个后续任务；
* Join：多条先验组合是否优于单一先验；
* Scope：是否只在正确作用域复用经验；
* Update：能否覆盖旧规则、适应新规则；
* Hard Negative：是否被表面相似但错误的历史误导。

Join、Update 和 Hard Negative 最好在分层子集增加机制对照：

* Join：Reset / Parent-1 / Parent-2 / Both；
* Update：Old-only / Old→Update / Reset；
* Hard Negative：Relevant-only / Distractor-only / Both / Reset。

主实验仍然是 Reset vs Stateful，这些只用于解释机制。

## 论文图表

主结果建议准备：

* 两模型 Reset vs Stateful 总体柱状图；
* `model × motif` 的 CL gain heatmap；
* dependency distance–transfer gain 曲线；
* parent count–performance 曲线；
* Diagnostic–Integrated correlation scatter；
* success–token cost Pareto 图；
* failure taxonomy 堆叠图；
* 雷达图作为摘要图，不作为主要统计证据；
* 3–4个 trajectory case study：正迁移、负迁移、Update 成功、Join 失败或成功。

所有结果按 family macro-average，并使用 family-level paired bootstrap 给出95%置信区间。

## 可以直接给 Agent 的目标

> 进入 Phase 5 Multi-Model Evaluation。固定使用 `codegraphcl-v1-rc2`，禁止修改 benchmark task、edge、stream 和 verifier。接入公司内部 GLM-5.2 与 Qwen-30B，记录精确 model ID、revision、endpoint、context limit、temperature、token budget、tool protocol 和 timeout，保证两模型使用相同 harness 与预算。
>
> 首先完成 Phase 5-0：7条 motif-stratified Diagnostic streams 加5条 Integrated streams，在两个模型上分别运行 Reset 与 Native Stateful，共48条 runs。基础设施成功率达到95%后冻结 execution protocol。
>
> 随后完成95个 stream families的全量 N=1，共380条 runs；再对26个分层 families增加两个 seeds，共追加208条 runs。输出 task-level、stream-level、family-level 和 model-level CSV，以及完整 trajectory manifest。
>
> 主指标为 Reset success、Stateful success、CL gain、normalized CL gain、tokens、turns、elapsed 和 negative-transfer rate。分析 model×condition、model×motif、distance、parent count、scope、update、hard-negative、cross-repo 和 Diagnostic–Integrated correlation。所有统计使用 family macro-average 和 paired bootstrap 95% CI。
>
> 不把“GLM优于Qwen”作为验收条件。Phase 5 的验收标准是实验覆盖完整、协议公平、结果可复现，并能够揭示两个模型在总体能力、经验利用、作用域判断、更新能力和负迁移方面的差异。

这一步完成后，论文就会从“构建了一个 benchmark”进入“benchmark 能系统地区分模型持续学习行为”的主结果阶段。
