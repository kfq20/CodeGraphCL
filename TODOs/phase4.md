你这里的 “Face Forward” 我按 **Phase 4** 理解。下面这版可以直接交给 Agent。核心是立即从少量 edge 诊断转向完整 benchmark 建设，Phase 3 封存，不再继续微调。

# Phase 4：CodeGraphCL-v1 Benchmark Scale-Up

**周期：8–10 天**

## 一、阶段目标

Phase 4 的唯一目标是：

> 将当前候选 Task/Edge Bank 扩展并冻结为 CodeGraphCL-v1：一个覆盖多个真实仓库、编程语言和 Graph Motif，能够生成 Diagnostic 与 Integrated Task Streams，并支持后续完整多模型评测的 benchmark。

Phase 4 不要求证明 Stateful 优于 Reset，也不要求每条 edge 独立通过 N=3/N=5 因果实验。Phase 3 的 edge intervention 与 carrier ablation 作为 protocol validity analysis 封存。

整体流程为：

[
\text{Task Bank}
\rightarrow
\text{Experience Graph}
\rightarrow
\text{Stream Generator}
\rightarrow
\text{Benchmark Split}
\rightarrow
\text{Executable Smoke Test}
]

完整 benchmark 上的多模型结论放到 Phase 5。

---

## 二、规模与质量目标

### 2.1 Benchmark 规模

| 资产                          | 最低验收标准 |  理想目标 |
| --------------------------- | -----: | ----: |
| 开源仓库                        |      5 |   6–8 |
| 编程语言                        |      3 |     4 |
| Executable tasks            |     60 |    80 |
| Core evaluation tasks       |     40 |    60 |
| Task families               |     18 | 25–30 |
| Semantic + executable edges |     40 |    60 |
| Graph motifs                |      6 |     7 |
| Diagnostic stream families  |     40 |    60 |
| Diagnostic episodes         |    200 |   300 |
| Integrated stream families  |     20 |    30 |
| Intervention-audit subset   |     10 |    15 |

当前已有资产全部作为 seed bank 保留，但 rejected、external-provenance 和 infrastructure-blocked 资产不能计入正式图规模。

### 2.2 Motif 配额

| Motif            | 最低数量 | 测量能力        |
| ---------------- | ---: | ----------- |
| Direct / Parity  |    8 | 直接经验复用      |
| Delayed Transfer |    5 | 长距离保留       |
| Scope            |    6 | 作用域判断       |
| Update / Stale   |    8 | 更新和遗忘旧规则    |
| Fork             |    4 | 一条经验向多个任务传播 |
| Join             |    4 | 多父经验组合      |
| Hard Negative    |  8 组 | 忽略表面相似历史    |

同一 edge 可以参与不同 stream，但不能因为排列方式不同重复计入 edge 数量。

### 2.3 Task 质量分层

所有任务统一分为：

```yaml
verification_tier:
  - semantic_candidate
  - executable_candidate
  - release_core
  - rejected
  - infrastructure_blocked
```

`executable_candidate` 至少满足：

* Base fail；
* Gold pass；
* PASS_TO_PASS 或明确 N/A；
* 至少两个不同机制的 near-miss；
* instruction 不泄漏实现；
* behavior-level verifier；
* clean materialization 连续成功两次。

`release_core` 进一步满足：

* verifier 不依赖 Gold 的具体函数名或代码布局；
* 无空测试、skip、字符串匹配假阳性；
* hidden tests 可稳定运行；
* 至少在一个替代实现或语义 mutation 上验证 verifier；
* instruction 经过人工可读性审计。

论文主结果使用 `release_core`，其他 executable tasks 可进入扩展集和分析集。

---

## 三、执行任务

### Task 1：冻结 Phase 3

最多投入半天：

* 修复并测试 `atom_lengths.py`；
* 将 Phase 3 报告固定为最终版本；
* 标记 `phase3-final`；
* 不再围绕 prose atom 或少量 edge 增加实验；
* Phase 3 结果进入论文的 validity analysis，而不是主结果。

### Task 2：批量扩展 Task Bank

优先使用已有环境和历史数据：

* Fastify；
* Clap；
* ripgrep；
* HTTPX 的新 family，不再使用 rejected `start_tls` family；
* Viper，使用 test-function-level fingerprints；
* 新增 1–3 个构建快速、测试稳定的中型基础设施仓库。

统一生产流程：

```text
commit candidate
→ 用户级任务目标
→ base/gold 恢复
→ verifier 构造
→ near-miss
→ materialization
→ family/motif 标注
```

生产约束：

* 每个主要 repo 至少贡献 8 个任务；
* 单一 repo 不得超过正式任务总数的 30%；
* 单个 task 的环境或 verifier 调试最多 2 小时；
* 单个 semantic audit 最多 30 分钟；
* 超时立即标记 blocked/rejected，不允许拖慢批量生产；
* 不为了满足数量拆分一个自然任务；
* 不把 test-only commit 当成独立 coding task；
* 不用极小格式修复大量填充 benchmark。

### Task 3：扩展 Experience Graph

正式 edge 必须：

* `from` 和 `to` 解析到两个不同的 Task Node；
* producer 严格早于 consumer；
* 两端任务均为 executable；
* experience 仅包含 producer-era knowledge；
* 有明确的 diff、test 或 commit-message 证据；
* 对应可描述的工程决策，而不是文件共现；
* 不存在 future leakage；
* external commit 只作为 provenance，不进入正式 Task Graph。

Edge metadata 至少包括：

```yaml
edge_id:
from:
to:
edge_type:
motif:
experience:
  invariant:
  scope:
  provenance:
  validity_interval:
evidence:
  ancestry:
  diff_relation:
  test_relation:
  human_audit:
intervention_status:
  not_sampled | screened | supported | rejected | blocked
```

不再逐条运行高成本 N=3。只从不同 repo 和 motif 分层抽取 10–15 条 edge，进行 intervention protocol audit。其余 edge 依靠语义审计、可执行端点以及 Phase 5 的聚合实验评估。

### Task 4：实现 Stream Generator

新增统一接口，例如：

```bash
python -m codegraphcl generate-streams \
  --type diagnostic \
  --motif update \
  --distance 2-3 \
  --count 20 \
  --seed 42
```

Generator 必须支持：

* stream length；
* motif；
* dependency distance；
* parent count；
* distractor 数量；
* distractor 相似度；
* stale/wrong history；
* missing parent；
* repo/language constraint；
* deterministic seed。

Diagnostic templates 至少包括：

```text
Direct:       A → B
Delayed:      A → D1 → D2 → B
Fork:         A → {B1, B2}
Join:         {A1, A2} → B
Scope:        A → B_in / B_out
Update:       A_old → U → B
HardNegative: A → H_similar → B
```

Integrated Stream 要求：

* 每条包含 5–10 个任务；
* 至少包含两类 motif；
* 至少一条真实经验边；
* 至少一个 distractor；
* 可以包含 stale/update；
* 不得出现 code incompatibility 或 future leakage。

### Task 5：控制组合膨胀

Benchmark 不能通过拓扑排列虚增规模。必须实现：

* canonical stream signature；
* family equivalence；
* partial-order reduction；
* 重复 episode 检测；
* family-level macro averaging。

建议 family 定义为：

[
\text{family}
=============

(\text{target},\text{parent set},\text{motif},
\text{delay bucket},\text{intervention})
]

如果两个 stream 只有无关任务顺序不同，应属于同一个 family。

### Task 6：建立数据划分

至少提供：

* `dev`：公开 instruction、verifier 和 Gold；
* `test`：公开 instruction，隐藏核心 verifier；
* `cross_repo`：至少保留一个 repo 测试跨仓库泛化；
* `temporal`：按 commit 时间测试未来任务；
* `integrated`：复杂组合流。

约束：

* 同一 family 的不同 episode 不能跨 split；
* 同一 target 的不同线性化不能跨 split；
* 同一 commit 或等价 patch 不能跨 split；
* 记录与 SWE-bench 等已有 benchmark 的去重结果。

### Task 7：Benchmark-level Smoke Test

Phase 4 不做完整多模型实验，但必须确认全链路可运行：

1. 所有正式 task 重新 materialize；
2. 所有 edge 通过 graph validation；
3. 所有 stream 通过静态检查；
4. 分层抽取至少 10% Diagnostic families；
5. 用一个固定模型运行 Reset 和 Native Stateful；
6. 抽取至少 5 条 Integrated Streams 做端到端测试。

Smoke Test 检查：

* Stateful 是否延续同一个 agent session；
* Reset 是否真正新建 session；
* 每个节点是否从独立 base snapshot 开始；
* 前一任务的代码修改是否没有污染下一任务；
* reward、tokens、turns、tools、elapsed 是否完整；
* 中间节点失败是否正确记录；
* infrastructure success rate 是否达到 95%。

Smoke Test 不要求 Stateful 优于 Reset。

---

## 四、验收标准与交付物

### 4.1 Phase 4 通过标准

Phase 4 必须同时满足：

* ≥5 个 repo、≥3 种语言；
* ≥60 个 executable tasks；
* ≥40 个 release-core tasks；
* ≥18 个 families；
* ≥40 条正式 Experience Graph edges；
* ≥6 类 motif；
* ≥40 个 Diagnostic families；
* ≥200 个 Diagnostic episodes；
* ≥20 个 Integrated stream families；
* ≥10 条 edge 完成 intervention audit；
* 所有正式 edge 无自环、端点完整、无 future leakage；
* 所有正式 stream 无代码版本冲突；
* family 去重和 partial-order reduction 生效；
* smoke infrastructure success rate ≥95%；
* 至少一个 cross-repo split；
* 不以 Stateful 正向提升作为验收条件。

如果任务总量达成但 release-core 不足，不得通过增加低质量任务补数，应明确冻结为 RC，并列出剩余升级任务。

### 4.2 必须提交的工件

```text
BENCHMARK_V1_REPORT.md
DATA_CARD.md
LICENSES.md

benchmark/
├── index.jsonl
├── graph.yaml
├── tasks/
├── edges/
├── families/
├── splits/
│   ├── dev.json
│   ├── test.json
│   ├── temporal.json
│   └── cross_repo.json
└── streams/
    ├── diagnostic/
    └── integrated/

codegraphcl/
├── generate_streams.py
├── validate_benchmark.py
├── validate_stream.py
└── summarize_benchmark.py

runs/
├── phase4_materialization.csv
├── phase4_intervention_audit.csv
└── phase4_stream_smoke.csv
```

`BENCHMARK_V1_REPORT.md` 必须报告：

* repo、language、task、family、edge 和 motif 统计；
* executable/release-core 比例；
* graph degree、dependency distance、parent count 分布；
* Diagnostic/Integrated stream 分布；
* rejected 和 infrastructure-blocked 数量；
* intervention audit 覆盖；
* smoke test 结果；
* 数据划分和去重；
* Phase 5 完整实验矩阵；
* 当前 benchmark 允许和不允许支持的论文 claim。

---

## 可直接给 Agent 的指令

> Phase 3 完成必要的 checker 修复后立即冻结，不再围绕少量 edge 或 prose carrier 做追加诊断。现在进入 Phase 4：CodeGraphCL-v1 Benchmark Scale-Up。本阶段目标是规模化构建完整 benchmark，而不是获得单条正向因果结果。
>
> 在 8–10 天内，将当前 seed bank 扩展到至少 5 个真实开源仓库、3 种语言、60 个 executable tasks、40 个 release-core tasks、18 个 families、40 条 semantic-audited executable edges、6 类 motifs、40 个 Diagnostic stream families、200 个 Diagnostic episodes 和 20 个 Integrated stream families。
>
> 所有 task 必须通过 Base fail、Gold pass、PASS_TO_PASS 或明确 N/A、两个不同 near-miss、behavior-level verifier、instruction separability 和两次 clean materialization。Release-core task 还需通过 verifier independence、hidden-test stability 和替代实现或 semantic mutation 检查。单 task 调试不超过 2 小时，超时立即标记 blocked/rejected。
>
> 所有正式 edge 的 from/to 必须解析到两个不同的 executable Task Nodes，producer 严格早于 consumer，experience 仅含 producer-era knowledge。External commit 只能作为 provenance。所有 edge 做语义审计，只按 repo 和 motif 分层抽取 10–15 条进行 intervention audit，不再逐条运行 N=3/N=5。
>
> 实现 motif-aware Stream Generator，支持 Direct、Delayed、Fork、Join、Scope、Update/Stale 和 Hard Negative，以及 distance、parent count、distractor 和 stream length 控制。使用 canonical signature、family equivalence 和 partial-order reduction，禁止通过无关节点排列虚增 benchmark。
>
> 主执行协议保持 snapshot-isolated：每个 task 使用独立 base snapshot；Native Stateful 只延续 agent session，不延续修改后的代码树；Reset 每个节点开启新 session。按 family 构建 dev/test/temporal/cross-repo splits。
>
> Phase 4 只运行 benchmark-level smoke：全部 task 重新 materialize、全部 graph/stream 静态验证，并抽取至少 10% Diagnostic families 和 5 条 Integrated Streams，使用一个固定模型测试 Reset 与 Native Stateful。验收指标是基础设施成功率 ≥95%，不要求 Stateful 优于 Reset。
>
> 完成后提交完整 Task/Edge/Family/Stream Bank、生成器、validator、splits、Data Card、License 清单和 `BENCHMARK_V1_REPORT.md`，冻结版本为 `CodeGraphCL-v1-rc1`。Phase 5 再在完整 benchmark 上运行多模型 Reset vs Native Stateful，并分析 motif、distance、parent count、negative transfer、跨 repo 泛化和 Diagnostic–Integrated correlation。
