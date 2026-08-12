# CodeGraphCL: A Graph-Structured Benchmark for Continual Learning in Coding Agents

## Research Proposal

**工作题目**  
**CodeGraphCL: Diagnosing Continual Learning in Coding Agents through Experience-Dependent Task Graphs**

**一句话概括**  
CodeGraphCL 将 coding-agent continual learning 建模为一个由真实工程任务、类型化经验依赖和可控图结构组成的 Task Graph，并通过对历史信息进行干预，诊断 Agent 是否能够正确地提取、保持、迁移、组合、更新和抑制经验。

---

## 1. 研究背景

今天的 coding benchmark 大多将任务视为相互独立的单次问题：给定一个仓库快照和一条指令，Agent 修改代码，Verifier 判断是否通过。这种设置适合测量单任务工程能力，却无法回答长期使用 coding agent 时更重要的一组问题：

- Agent 完成前一个任务后，是否真的学到了后续可复用的项目经验？
- 当用户不再重复解释项目约定时，Agent 能否主动从历史中恢复它？
- 当同一原则需要迁移到另一个模块时，Agent 是否能够正确泛化？
- 当后续任务需要组合多段历史时，Agent 能否同时找到并使用它们？
- 当旧规则已经过期，或者历史只是表面相关时，Agent 能否避免负迁移？
- 历史即便没有提高成功率，是否减少了重复搜索、文件读取、测试和用户澄清？

现有长上下文或 memory benchmark 往往把“记忆”简化为事实召回、文本检索或对话问答；现有 coding benchmark 则主要关注单任务解决能力。真实的软件维护位于两者之间：历史经验必须改变后续的工具调用、工程决策、代码产物或完成成本，并且最终效果需要通过可执行测试来验证。

本研究认为，持续学习不应只被表示为一条很长的 session。更清晰的表示是一个 **Experience-dependent Task Graph**：节点是工程任务，边表示前序任务产生的一项经验会影响后续任务。不同局部图结构对应不同的持续学习能力。

---

## 2. 核心研究命题

> Coding-agent continual learning 的核心，不是历史长度本身，而是 Agent 能否在任务图上正确处理经验的产生、传播、组合、更新和失效。

这一命题包含三层判断。

### 2.1 持续学习的价值不只体现在更高难度

一个有价值的持续学习系统，不一定能让基础模型解决原本完全无法解决的高难度算法题。更常见的价值是：

- 用户不必反复输入项目背景；
- Agent 不必反复读取相同文件；
- 已经发现过的环境陷阱无需再次试错；
- 项目约定能在后续模块中保持一致；
- 同等质量下减少 token、工具调用、测试轮次和时间。

因此，CodeGraphCL 同时关注**正确性收益**和**效率收益**。

### 2.2 时间先后不等于持续学习依赖

两个任务发生在同一 session、同一用户或同一仓库中，并不足以建立一条边。只有当前序经验会因果性地改变后续行为时，才能称为经验依赖。

### 2.3 不同图结构对应不同能力

直接迁移、延迟召回、多目标迁移、多经验组合、规则更新和错误历史抑制，并不是同一种能力。一个系统可能在 Direct 上表现良好，却在 Join 或 Stale History 上失败。Benchmark 应报告能力画像，而不只是一个总分。

---

## 3. 问题定义

### 3.1 Task Node

一个任务节点记为：

```text
T_i = (E_i, I_i, V_i, G_i, P_i, R_i)
```

其中：

- `E_i`：冻结的代码与执行环境；
- `I_i`：用户可见指令；
- `V_i`：行为级 Verifier；
- `G_i`：参考 Gold change，仅作为可解性证据；
- `P_i`：任务完成后产生的经验集合；
- `R_i`：完成当前任务需要的历史经验集合。

节点来自真实 commit、PR、issue 与测试变化。一个节点对应一个语义完整、可独立验收的工程目标，不要求与一次模型调用或一个 commit 严格一一对应。

### 3.2 Experience

经验记为：

```text
e = (statement, type, scope, validity, provenance)
```

可能的类型包括：

- architecture fact；
- interface contract；
- project policy；
- workflow / environment knowledge；
- failure lesson；
- user or team preference；
- progress / state；
- policy revision。

经验必须能够改变后续行动，而不是只支持一个字符串问答。

### 3.3 Typed Experience Edge

若任务 `T_i` 产生经验 `e`，并且 `T_j` 的行为、成功率或成本会因 `e` 而变化，则建立：

```text
T_i ──e,type──> T_j
```

每条边至少记录：

```yaml
from: T_i
to: T_j
experience: e
edge_type: required | beneficial | delayed | invalidates | hard_negative
scope: ...
expected_effect: correctness | efficiency | negative_transfer | mixed
rediscovery_cost: low | medium | high
provenance: commit | issue | session | test
status: proposed | semantically_audited | executable_verified | rejected
```

### 3.4 两张约束图

CodeGraphCL 区分：

1. `G_exp`：经验依赖图；
2. `G_code`：代码版本、接口与 artifact 的工程依赖图。

合法 Stream 必须满足：

```text
G_valid = G_exp ∪ G_code
```

并从 `G_valid` 的合法拓扑序中生成。这样可以避免打乱 commit 时间后出现接口缺失、Patch 冲突或未来实现泄漏。

### 3.5 Snapshot-isolated Execution

主设置采用 Snapshot-isolated Stream：

- 每个节点运行在自己的冻结、可复现环境中；
- 后续任务不会继承前序 Agent 修改后的工作区；
- Stateful 条件只延续原生 Agent session 和其中自然形成的上下文；
- Reset 条件为每个节点开启新 session；
- 两组当前任务的指令、代码、工具和预算保持一致。

该设置将“经验延续”与“文件状态延续”解耦，更适合测量 Agent 是否真正利用了历史经验。持续工作区可以作为后续独立赛道，而不与主结果混合。

---

## 4. Graph Motif 与能力分类

CodeGraphCL 将局部图结构定义为能力测量单元。

| Motif | 结构 | 主要能力 |
|---|---|---|
| Direct Transfer | `A → B` | 立即提取并复用经验 |
| Delayed Recall | `A → … → B` | 跨任务和上下文压缩保持经验 |
| Fork | `A → {B,C}` | 将同一原则迁移到多个目标 |
| Join | `{A,B} → C` | 组合多段互补历史 |
| Scope | `A→B`，但 `A↛C` | 判断经验适用边界 |
| Hard Negative | `A≈B`，但 `A↛B` | 抑制表面相关但因果无关的历史 |
| Wrong History | `Wrong(A) → B` | 识别并抵抗错误经验 |
| Stale / Update | `A_old → U → B` | 更新、覆盖或局部失效旧规则 |
| Integrated Graph | 多 motif 重叠 | 在真实长程历史中协调多种能力 |

Motif 不是简单的任务标签。一条长 Stream 可以同时包含多个 motif；同一个节点或边也可以参与多个局部结构。

---

## 5. Benchmark 组织方式

### 5.1 三层资产

```text
Task Bank
  ↓
Experience / Edge Bank
  ↓
Motif-aware Stream Generator
```

**Task Bank** 保存自包含节点及其 Base、Gold 和 Verifier。  
**Edge Bank** 保存经验依赖、来源、作用域和验证状态。  
**Stream Generator** 根据目标 motif、长度、距离和干扰类型，从 Verified Graph 中生成 Stream。

### 5.2 Family 与 Episode

Benchmark 使用两级标识：

```text
family_id   = target + parent experience set + motif + intervention
episode_id  = family 的具体合法线性化和随机化实例
```

如果两个 Stream 只有无关节点顺序不同，而 target、父经验、delay bucket 和历史有效性相同，则属于同一个 family。最终应按 family 做宏平均，避免拓扑排序较多的结构获得过高权重。

### 5.3 Diagnostic Streams

每条 Stream 突出一个主要 motif，使失败能够被归因。例如：

```text
Direct:  A → B
Delayed: A → D1 → D2 → B
Join:    {A1,A2,A3} → B
Update:  A_old → U → B
```

Diagnostic 层用于能力画像、系统比较、消融和训练信号构造。

### 5.4 Integrated Streams

Integrated Stream 同时包含多种 motif，模拟真实长期维护。例如一条流中可以同时存在：

- 一个短距离 Direct edge；
- 一个跨多步 Delayed edge；
- 一个 Fork；
- 一个多父 Join；
- 一个 Hard Negative。

它用于测试长上下文、经验选择、错误传播和多能力协调，但不替代 Diagnostic 层。

---

## 6. 数据构建方法

### 6.1 仓库与任务来源

论文版本使用可公开复现的开源仓库。具体仓库名单留待独立调研，但选择标准应包括：

- 有较完整的 commit / PR / issue 历史；
- 源码和测试随功能变化共同演化；
- 能在合理资源内离线构建和测试；
- 存在跨任务复用的架构、协议、配置、安全或工作流决策；
- License 允许发布派生 benchmark artifact。

### 6.2 从 Commit 构造 Task

```text
筛选源码与测试共同变化的 commit / commit range
→ 验证旧版本失败、正确版本通过
→ 恢复用户级工程目标
→ 必要时进行语义切片
→ 构造独立行为 Verifier
→ 生成 Task Node
```

Commit 是任务和 Gold 的证据，不一定是任务边界。多个相关 commit 可以共同形成一个任务；混杂 commit 需要保留一条因果一致的行为路径。

### 6.3 从 Task 长出 Edge

```text
真实历史中发现重复决策或跨模块约束
→ 显式抽取 Experience
→ 匹配 produces / requires
→ 进行作用域与重新发现成本审计
→ 构造历史干预
→ 通过对照实验验证边
```

真实数据提供图结构和经验分布的先验，但不能单独证明因果。边的最终升级依赖受控 replay。

### 6.4 Verifier 原则

Verifier 必须检查外部行为，而不是精确匹配 Gold 的模块、函数名或实现布局。每个任务至少需要：

- Base fail；
- Gold pass；
- alternative-correct implementation pass；
- PASS_TO_PASS regressions；
- hidden edge cases；
- semantic mutations killed；
- anti-hardcoding / no-leak controls。

Gold 是任务可解的存在性证明，不是唯一标准答案。

### 6.5 Stream 生成约束

生成器不能枚举所有排列，而应：

1. 合并 `G_exp` 与 `G_code`；
2. 排除环、接口不兼容和 future leakage；
3. 按 motif 与能力覆盖选择子图；
4. 使用 partial-order reduction 合并无意义换序；
5. 调节 delay、干扰相似度、父节点缺失和历史有效性；
6. 重新运行环境与 Verifier controls；
7. 只将通过验证的组合加入 Stream Bank。

---

## 7. 因果评测设计

### 7.1 主比较

主结果保持简单：

- **Reset**：每个任务使用新 Agent session；
- **Stateful**：整个 Stream 延续一个普通原生 Agent session。

两组只在历史访问上不同。主 Stateful 不注入人工优化的 notes、Oracle summary 或 task-specific RAG。

### 7.2 历史干预组

为验证边和诊断能力，可加入：

- **Oracle Experience**：提供最小且正确的历史经验；
- **Missing Parent**：删除 Join 的一个或多个父经验；
- **Irrelevant History**：提供无关历史；
- **Hard-negative History**：提供表面相似但因果无关的历史；
- **Wrong History**：提供错误决策；
- **Stale History**：提供曾经正确但已经失效的规则；
- **Scoped Update**：仅在部分模块更新旧规则。

边只有在正确历史带来稳定收益，而错误或无关历史不能获得同样收益时，才具有因果可信度。

### 7.3 质量与效率指标

**质量指标**：

- task success / behavioral score；
- family macro score；
- integrated stream completion；
- negative-transfer rate；
- longest successful dependency distance；
- join success by parent count。

**效率指标**：

- wall-clock time；
- input / output tokens；
- tool calls；
- file reads and searches；
- repeated reads；
- test runs and failed commands；
- user clarification count。

效率收益必须在质量约束下报告。例如比较通过任务上的成本，或报告 quality-cost Pareto frontier，避免通过少做工作获得虚假效率提升。

### 7.4 Graph-aware 报告

每个系统输出能力向量：

```text
[Direct, Delayed, Fork, Join, Scope, Update, Hard-negative, Integrated]
```

总分使用 family-level macro average，同时单独报告 Integrated performance。不能用一个总分掩盖某些 motif 的系统性失败。

---

## 8. 研究问题

### RQ1：历史是否带来可测量收益？

Stateful 相比 Reset 是否提高成功率，或在质量不下降时减少重复探索成本？

### RQ2：Graph Motif 是否对应可区分的能力？

不同系统是否呈现稳定且不同的 motif performance profile？Direct 表现能否预测 Join、Update 或 Hard-negative 表现？

### RQ3：图结构如何影响难度？

研究 source-target distance、父节点数量、分支数、干扰相似度、历史长度与目标欠指定程度对结果的影响。

### RQ4：Agent 能否正确选择历史？

Agent 是否会被文本相似但因果无关的任务误导？作用域判断和错误历史抑制能力有多强？

### RQ5：Agent 能否更新经验？

当规则发生全局或局部更新时，Agent 能否覆盖旧规则，同时在未变化作用域中保留旧经验？

### RQ6：Diagnostic 能力能否预测综合表现？

单 motif 测试能否解释 Integrated Stream 的成功与失败？不同 motif 是否存在明显的交互效应？

### RQ7：能力能否跨图与跨仓库泛化？

在未见 target、未见 edge、未见 motif composition 和未见 repository 上，持续学习系统能否保持收益？

---

## 9. 数据划分与泛化设置

普通随机划分 episode 容易导致相同 target 或边泄漏。建议提供：

- **Seen-repo / unseen-episode**：仅测试同 family 的顺序鲁棒性；
- **Seen-repo / unseen-edge**：目标仓库已见，但依赖关系未见；
- **Seen-repo / unseen-target**：相同经验类型迁移到新目标；
- **Unseen motif composition**：训练见过原子 motif，测试其组合；
- **Unseen repository**：完整跨仓库泛化；
- **Longer horizon**：测试长度和依赖距离超过训练分布。

数据划分单位优先是 repo、target、edge 和 graph family，而不是随机 episode。

---

## 10. 预期核心贡献

1. **Formulation**：提出 Experience-dependent Task Graph，将 coding-agent continual learning 从长对话概念转化为结构化、可干预的问题。
2. **Capability Taxonomy**：用 graph motif 定义并区分经验保持、迁移、组合、作用域判断、更新与抑制等能力。
3. **Benchmark**：从公开仓库真实工程历史构造可执行、Snapshot-isolated 的 Diagnostic 与 Integrated Streams。
4. **Causal Protocol**：通过 Reset、Stateful、Oracle、Missing、Wrong、Stale 和 Hard-negative 历史干预验证经验边。
5. **Graph-aware Metrics**：同时测量正确性、效率、负迁移和长程依赖，并按 family 而非拓扑排列宏平均。
6. **Empirical Findings**：揭示现有 coding agents 或 memory systems 在不同 motif 上的能力差异，以及原子能力与综合表现之间的关系。

方法贡献是否加入 graph-aware memory / retrieval 模型，可在 baseline 调研和初步实验后决定。Benchmark paper 本身不应依赖一个新方法才能成立。

---

## 11. 可证伪假设

论文应提前明确可能失败的判断：

- **H1**：至少部分任务 family 存在稳定的 Stateful > Reset 正确性或效率收益；
- **H2**：不同 motif 上的系统排名或性能差异并不完全一致；
- **H3**：依赖距离和父节点数量增加会系统性降低表现；
- **H4**：文本相似度高的 hard negative 会造成显著错误检索或负迁移；
- **H5**：Diagnostic motif score 对 Integrated performance 有解释力，但不能完全预测；
- **H6**：结构化历史选择比无差别保留全部历史更能控制长程成本或负迁移。

若 motif 之间高度相关、Stateful 没有稳定收益或边无法通过因果验证，论文的核心主张需要被削弱。这些结果也应被视为研究发现，而不是通过继续手工调题掩盖。

---

## 12. Validity Threats

### 12.1 人工构造偏差

边和欠指定指令可能过度依赖作者判断。缓解方式包括真实 provenance、双人语义审计、明确 Edge Contract 和历史干预验证。

### 12.2 Verifier 与 Gold 耦合

若测试限制实现形状，可能测到代码模仿而非任务完成。需要 alternative-correct 和 mutation controls。

### 12.3 Snapshot 非真实连续工作区

Snapshot-isolated 牺牲了文件状态延续，但换来对经验变量更干净的控制。论文需要明确其测量边界，并将 cumulative-worktree 作为补充设置。

### 12.4 Task 难度混淆

Stateful 失败可能来自基础 coding 能力不足，而非 CL 能力。需要 Oracle Experience 判断：历史信息充分时任务是否可解。

### 12.5 Repo 与语言偏差

有限仓库可能使经验类型和图结构分布不具代表性。需要覆盖多语言、不同项目类型，并按 repo 报告结果。

### 12.6 组合数量虚高

大量合法拓扑序可能只是同一能力的轻微换序。必须使用 family/episode 分层、partial-order reduction 和 family macro。

### 12.7 历史泄漏

未来接口、Gold、solution path 或前序文件可能泄漏答案。需要容器隔离、canary、filesystem audit 和 transcript audit。

---

## 13. Paper Outline

### 1. Introduction

- 单任务 coding benchmark 与真实长期维护之间的缺口；
- 持续学习不仅是事实记忆或长上下文；
- Task Graph 作为可诊断 formulation；
- 主要贡献概览。

### 2. Related Work

- coding-agent benchmarks；
- continual / lifelong learning for agents；
- long-term memory and long-horizon interaction；
- graph-structured evaluation and workflow benchmarks；
- commit-derived software engineering tasks。

本节的具体 benchmark 与 baseline 名单由独立调研补充。

### 3. CodeGraphCL Formulation

- Task、Experience、Typed Edge；
- Experience Graph 与 Code Evolution Graph；
- Snapshot-isolated semantics；
- causal definition of a valid edge。

### 4. Graph Motifs as Continual-Learning Capabilities

- Direct、Delayed、Fork、Join；
- Scope、Hard Negative；
- Update、Stale 和 Wrong History；
- Diagnostic 与 Integrated graphs。

### 5. Benchmark Construction

- 开源仓库筛选；
- commit-to-task pipeline；
- experience and edge mining；
- behavioral verifier；
- constrained stream generation；
- family/episode 去重与数据划分。

### 6. Experimental Protocol

- Stateful / Reset 主比较；
- history intervention；
- correctness and efficiency metrics；
- graph-aware aggregation；
- isolation and reproducibility。

### 7. Main Results

- 总体 Stateful–Reset gap；
- motif capability profiles；
- Diagnostic 与 Integrated 结果；
- correctness-efficiency trade-off。

### 8. Analysis

- distance scaling；
- parent-count and join ablation；
- hard-negative / wrong-history robustness；
- rule update and staleness；
- cross-repo / unseen-composition generalization；
- failure taxonomy and case studies。

### 9. Discussion

- Graph formulation 对 memory、harness 和 training 的启示；
- Benchmark 测量边界；
- 从 Snapshot-isolated 扩展到 cumulative workspace；
- 数据规模化与社区扩展。

### 10. Conclusion

- 重申持续学习应被测量为任务图上的经验处理能力，而非单纯长上下文保持。

---

## 14. 关键图表规划

1. **Figure 1 — 核心概念图**：Single-task evaluation 与 CodeGraphCL 对比；
2. **Figure 2 — Motif taxonomy**：九类图结构及对应能力；
3. **Figure 3 — Construction pipeline**：Commit → Task → Experience Edge → Stream；
4. **Figure 4 — Causal interventions**：同一 target 的 Reset / Oracle / Wrong / Stateful；
5. **Figure 5 — Capability radar or heatmap**：不同系统的 motif profile；
6. **Figure 6 — Scaling curves**：distance、parent count、stream length；
7. **Table 1 — Dataset statistics**：Repo、Task、Edge、Family、语言与 Verifier；
8. **Table 2 — Main results**：Diagnostic macro、Integrated、效率、负迁移；
9. **Table 3 — Generalization**：unseen edge / composition / repository；
10. **Table 4 — Validity controls**：Base、Gold、alternative、mutation、leakage。

---

## 15. 建议推进阶段

### Phase A：冻结定义

- Task / Experience / Edge schema；
- motif taxonomy；
- Snapshot-isolated protocol；
- family equivalence；
- edge promotion gate。

### Phase B：Reference Implementation

- 使用 LivingBench 跑通完整 pipeline；
- 建立 Diagnostic 与 Integrated 两层任务；
- 验证 motif 是否产生不同能力画像；
- 校准 Stream Generator 与统计方式。

LivingBench 在这一阶段是方法开发与内部验证案例，不必进入论文公开数据。

### Phase C：公开数据构建

- 根据独立调研选择开源仓库；
- 建立真实 Task Bank；
- 审计 Experience Edges；
- 逐步扩充 motif coverage；
- 冻结公开测试集。

### Phase D：实验与分析

- 完成主比较和历史干预；
- 形成 capability profile；
- 验证可证伪假设；
- 完成跨 repo 与未见组合实验。

### Phase E：发布

- 发布自包含任务、Verifier、Graph metadata 和评测工具；
- 提供可复算数据统计与数据卡；
- 明确许可证、失败案例和已知限制。

---

## 16. 当前决策与开放问题

### 已确定

- 论文以 Task Graph 为核心，而非附属组织方式；
- 主执行语义使用 Snapshot-isolated；
- 同时提供 Diagnostic 和 Integrated Streams；
- 主基线比较为原生 Stateful 与 per-task Reset；
- Verifier 与 Gold 解耦；
- 按 family 宏平均，episode 只用于顺序和环境随机化；
- 内部 LivingBench 用于 Reference Implementation，论文数据使用开源仓库。

### 待独立调研或实验决定

- 最终使用哪些开源仓库；
- 与哪些已有 benchmark 进行对比或复用；
- 选择哪些模型、runtime harness 和 memory baselines；
- 是否提出 graph-aware retrieval / memory 方法；
- 最终数据规模和语言覆盖；
- cumulative-worktree 是否进入主文或附录；
- graph-aware training 是否作为论文主实验或后续工作。

## 最终定位

CodeGraphCL 不以“拥有最难的 coding tasks”为主要卖点。它希望解决的是一个更基础的问题：

> 当 coding agent 在一个项目中持续工作时，我们如何知道它究竟学会了什么、何时能够复用、何时应该组合、何时必须更新，以及何时应该忽略历史？

Task Graph 为这些问题提供统一的表示，Graph Motif 提供能力分类，历史干预提供因果证据，可执行 Verifier 则保证最终测量落在真实工程行为上。
