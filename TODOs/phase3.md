## Phase 3：Causally Verified Edge Construction

**建议周期：2026 年 8 月 14–19 日，最多 5 天。**

### 一、阶段定位与核心目标

Phase 1 验证了统一构建协议，Phase 2/2.1 建立了候选 Task/Edge Bank，并完成了第一轮因果筛选。当前已经拥有：

* 3 个主要开源仓库；
* 20 个 executable candidate nodes；
* 9 个 task families；
* 8 条完成筛选或明确放弃的 ready edges；
* 0 条通过 Causal Dependency Gate 的 verified beneficial edge。

因此，Phase 3 不再追求增加普通 task 数量，也不正式构造大规模 task stream，而是解决 benchmark 当前唯一的 construct validity 问题：

> 找到一小批能够通过受控历史干预验证的经验边，证明 CodeGraphCL 测量的是历史经验的获取、选择和使用，而不只是普通 coding 能力。

Phase 3 的最终目标是：

> 构建至少 2 条、争取 3 条跨仓库且覆盖不同 motif 的 causally verified experience edges，并对这些边完成自然 Stateful pilot，为 Phase 4 的 Diagnostic Stream construction 提供最小 Verified Graph。

需要特别区分：

* **Causal intervention** 用于验证 edge 是否真实存在；
* **Natural Stateful vs Reset** 用于测量 agent 是否能自然获取和利用该经验。

Natural Stateful 不必获得正向结果。只要 Correct History 的受控干预稳定有效，而自然 Stateful 没有效果，也可以说明 agent 无法自然提取、保留或调用有效经验。

---

## 二、生产目标与候选选择

### 2.1 数量目标

| 资产                           |                 最低目标 | 理想目标 |
| ---------------------------- | -------------------: | ---: |
| 新审计 semantic edge candidates |                    8 |   12 |
| 通过 Separability Gate         |                    6 |    8 |
| 通过 Executable Gate           |                    6 |    8 |
| 完成 Reset calibration         |  所有 executable edges |   所有 |
| 完成四臂 N=1                     |                    6 |    8 |
| 进入 N=3 screening             |                    3 |    5 |
| 通过重复筛选                       |                    2 |    3 |
| Causally verified edges      |                    2 |    3 |
| 仓库覆盖                         |                    2 |    3 |
| Motif 覆盖                     |                  2 类 |  3 类 |
| Natural Stateful pilot       | 每条 verified edge N=2 |  N=3 |

如果达到 2–3 条 verified edges，应立即停止继续挖掘，进入 Phase 4，不为了扩大数量继续消耗时间。

### 2.2 候选 edge 的硬性条件

每条候选边在物化前必须明确回答以下问题：

1. **Producer 产生了什么经验？**

   必须是 producer 任务中真实出现的工程决策，而不是从 consumer 的 Gold patch 反推出来的答案。

2. **Consumer 为什么可能需要该经验？**

   Consumer 必须存在至少两条表面合理的解决路径，其中一条违反 producer 建立的规则。

3. **正确经验如何改变解决路径？**

   正确历史应该帮助 agent 更早选择正确模块、作用域、优先级、生命周期或兼容策略，而不是直接描述代码修改。

4. **Reset 为什么不能一眼推导答案？**

   如果 consumer 的代码树中已经存在完整 mirror implementation、明确接口或直接注释，Reset agent 很容易重新推导，经验边通常不具有可测性。

5. **Wrong/Stale experience 为什么具有真实迷惑性？**

   错误经验不能是显然荒谬的文本，而应当对应历史上曾经合理、局部正确或表面相似的实现原则。

建议为每条边在 YAML 中增加：

```yaml
mechanism_audit:
  reusable_decision: ...
  plausible_path_correct: ...
  plausible_path_competing: ...
  why_instruction_does_not_disambiguate: ...
  why_correct_history_selects_path: ...
  why_wrong_history_is_plausible: ...
```

### 2.3 优先寻找的工程机制

优先级建议如下：

1. **Scope / ownership**

   例如状态、schema、hook、cache 应属于当前 plugin、request、instance 还是 global scope。

2. **Precedence / conflict resolution**

   例如配置来源、schema、header、ignore rule 同时存在时的覆盖顺序。

3. **Lifecycle / cache invalidation**

   例如缓存何时共享、何时刷新、跨 root 或跨 request 时能否复用。

4. **Builder–derive / multi-surface parity**

   但要求 parity 契约不能直接完整地暴露在 consumer 代码树中。

5. **Scoped Update / Stale**

   曾经正确的规则只在部分模块或新版本中失效，而不是 instruction 直接说“把旧实现替换成新实现”。

本轮不再优先投入：

* 增加 getter/setter；
* 增加换行符；
* 增加简单 API method；
* 一到五行即可完成的局部补丁；
* consumer 代码树中已经存在完整参考实现的 mirror task；
* Gold patch 超过约 100–150 行、Reset 经常跑满 timeout 的结构性重构。

---

## 三、统一构建与因果验证协议

### 3.1 Edge-first 构建漏斗

每条候选边统一经过：

[
\text{Semantic Audit}
\rightarrow
\text{Mechanism Audit}
\rightarrow
\text{Separability}
\rightarrow
\text{Executable Gate}
\rightarrow
\text{Reset Calibration}
\rightarrow
N{=}1
\rightarrow
N{=}3
\rightarrow
\text{Confirmation}
]

#### Gate 1：Semantic Audit

需要确认：

* producer commit 严格早于 consumer；
* experience statement 只包含 producer-era knowledge；
* producer 和 consumer 操作的是同一工程决策；
* 不能只凭文件共同变化或文本相似建立 edge；
* consumer verifier 确实能够区分正确路径和竞争路径。

#### Gate 2：Instruction–Experience Separability

Instruction 只允许描述：

* 用户观察到的错误；
* 输入与错误输出；
* 期望的外部行为；
* 必要的复现步骤。

Instruction 不允许包含：

* 应修改的函数、字段或文件；
* 正确的 ownership 或 scope；
* precedence 顺序；
* 应使用的具体实现机制；
* “move from A to B”之类修订方向；
* producer experience 的近义改写。

#### Gate 3：Executable Gate

继续执行现有标准：

* Base fail；
* Gold pass；
* PASS_TO_PASS 或明确说明 not applicable；
* 至少两个有效 near-miss；
* near-miss 必须对应不同的错误实现；
* verifier 检查外部行为，不匹配 Gold patch；
* 标记为 `verification_tier: executable_candidate`。

### 3.2 Experience atom 控制

Correct、Irrelevant 和 Wrong/Stale 三个 atom 应尽量满足：

* token 长度差异不超过约 10%–15%；
* 使用相同的格式、语气和信息密度；
* 不出现 `correct`、`wrong`、`stale` 等条件名称；
* Irrelevant atom 来自同一仓库、相近技术粒度，但与 target 机制无关；
* Wrong/Stale atom 是合理但错误的工程原则；
* Correct atom 不得包含目标文件、具体代码或 Gold 实现。

否则，agent 的耗时差异可能来自 prompt 长度和叙述方式，而不是经验内容。

### 3.3 Reset calibration

在完整四臂实验前，先运行 Reset N=2：

* **0/2 成功且两次都接近 timeout**：标记 `too_hard`，停止；
* **2/2 成功且成本很低**：标记 `saturated_easy`，通常停止；
* **至少一次成功，且未全部贴着 timeout wall**：允许进入四臂 N=1；
* 如果成功率饱和，但正确经验可能显著减少探索成本，可保留为 efficiency candidate。

不要把固定的 200–400 秒作为硬标准。主要依据应是固定模型和预算下的成功率、timeout 情况和探索成本。

### 3.4 四臂 N=1 preflight

条件保持为：

* Reset；
* Correct；
* Irrelevant；
* Wrong 或 Stale。

只有出现以下情况之一时进入 N=3：

1. Correct 成功，而 Reset 或 Irrelevant 失败；
2. Correct 与其他组均成功，但 turns/tool calls/test runs 明显更少；
3. Wrong/Stale 产生与机制一致的失败，而 Correct 没有；
4. Correct 更早进入正确实现路径，trajectory 中能观察到机制一致的决策差异。

如果四臂全部成功且成本无合理差异，或四臂全部失败，立即停止。

### 3.5 N=3 screening 与确认

N=3 仍作为筛选，不作为最终效应估计。必须：

* block-randomized；
* 使用相同模型、timeout、temperature 和工具权限；
* 使用 opaque episode ID；
* 保存 prompt/atom hash、model flag、image digest、harness commit；
* correctness 为主指标，效率为次指标；
* 不使用单次最快耗时作为结论。

N=3 后可按以下状态分类：

| 状态                            | 判断                     |
| ----------------------------- | ---------------------- |
| `rejected_no_ordering`        | 四组没有稳定方向               |
| `rejected_reversed`           | Correct 持续差于控制组        |
| `rejected_saturated`          | 四组全部成功或全部失败            |
| `intervention_sensitive`      | Correct 的方向性优势得到重复     |
| `negative_transfer_sensitive` | Wrong/Stale 的机制性伤害得到重复 |
| `infrastructure_blocked`      | 无法获得可靠 reward          |

对通过 N=3 的 finalist，再追加到每组总计 N=5。如果资源允许，论文主实验阶段扩展到 N=8 或 N=10。

`causally_verified_v0` 的最低标准：

* Correct 相比 Reset 和 Irrelevant 存在重复的方向性优势；
* Wrong/Stale 不能获得与 Correct 相同的优势；
* 优势可以是成功率，也可以是在质量不下降情况下的效率；
* trajectory audit 与预注册机制一致；
* 结果不是由 atom 长度、instruction leakage、timeout wall 或基础设施错误解释的。

---

## 四、Natural Stateful Pilot 与阶段验收

### 4.1 Natural Stateful 不作为 edge 成立的前提

每条 `causally_verified_v0` edge 运行：

* Stateful：producer→consumer，同一原生 agent session；
* Reset：consumer 使用全新 session；
* 每组至少 N=2，理想 N=3。

需要记录：

* producer 是否成功；
* producer trajectory 中是否实际遇到该工程决策；
* consumer 是否复用了相关文件、测试、原则或失败经验；
* Stateful 与 Reset 的成功率和成本；
* Stateful 失败属于未提取、未保留、未检索还是错误应用。

Natural Stateful 的可能结论包括：

1. **Stateful benefit**：自然历史产生正迁移；
2. **Oracle-only benefit**：正确经验有价值，但 agent 没有自然提取或调用；
3. **Negative transfer**：agent 保留了错误或过期经验；
4. **No retention/use**：producer 经历了经验，但 consumer 行为与 Reset 无差异。

这四种结果都可以进入论文。

### 4.2 Phase 3 通过标准

Phase 3 判定为完整通过，需要同时满足：

* 至少审计 8 条新的 edge candidate；
* 至少 6 条完成 executable + separability；
* 所有 executable edges 完成 Reset calibration 和 N=1；
* 至少 3 条进入 N=3；
* 至少 2 条成为 `causally_verified_v0`；
* verified edges 来自至少 2 个仓库；
* verified edges 覆盖至少 2 种工程机制或 motif；
* 每条 verified edge 完成 natural Stateful pilot；
* 所有否定、放弃和 infrastructure failure 均保留；
* 不因结果不符合预期修改 instruction、experience provenance 或 verifier。

### 4.3 如果没有达到正向数量目标

如果完成 8–12 条针对性候选边后，仍然没有 2 条通过：

* Phase 3 仍可以视为“筛选工作完成”；
* 但项目不能声称已经构造出完整的 causally grounded CL benchmark；
* 应将论文定位调整为 graph-based benchmark construction framework 与 feasibility study；
* 实验重点转向为何真实 commit dependency 不产生可测 CL 信号；
* 不再无限制增加 task 或修改任务来追求正结果。

### 4.4 必须提交的工件

建议最终提交：

```text
PHASE3_REPORT.md
benchmark/
├── edges/
├── families/
├── tasks/
└── protocols/
    └── causal_dependency_gate_v1.md
runs/
├── phase3_screening.csv
├── intervene_<edge>_n1_*/
├── intervene_<edge>_n3_*/
└── stateful_<edge>_*/
```

`PHASE3_REPORT.md` 至少包含：

1. 候选漏斗统计；
2. 每条边的 mechanism audit；
3. Reset calibration 结果；
4. N=1 与 N=3 四臂结果；
5. Verified/Rejected/Blocked 分类；
6. Natural Stateful pilot；
7. 允许写入论文和不允许写入论文的结论；
8. Phase 4 可使用的 Verified Graph 清单。

---

## 可直接交给 agent 的总指令

> Phase 2.1 已正式验收。现在进入 Phase 3：Causally Verified Edge Construction，截止 2026 年 8 月 19 日，最多投入 5 天。本阶段停止扩充普通 task 数量，也不正式批量构造 task streams。核心目标是从真实开源工程历史中构建至少 2 条、争取 3 条跨至少 2 个仓库并覆盖至少 2 类 motif 的 causally verified experience edges，为 CodeGraphCL 的 construct validity 提供证据。
>
> 请从 edge 反向选择 consumer task。每条候选边必须先写 mechanism audit，明确 producer 产生的可复用工程决策、consumer 中至少两条表面合理的实现路径、正确经验如何排除错误路径，以及 instruction 为什么没有直接消除这种歧义。优先寻找 plugin scope、ownership、precedence、cache lifecycle、builder–derive parity 和 scoped update；停止优先投入 getter、换行、简单 API completion 和超大结构性重构。
>
> 每条候选统一经过 Semantic Audit → Mechanism Audit → Separability → Executable Gate → Reset N=2 Calibration → 四臂 N=1 → N=3 Screening。Correct、Irrelevant、Wrong/Stale atoms 必须格式一致、技术粒度相近，token 长度差异控制在约 10%–15%，不能包含条件名称或 Gold 实现。Instruction 只能描述外部错误和期望行为，不能泄漏函数、文件、作用域、优先级、ownership 或修订方向。
>
> Reset N=2 如果两次都贴着 timeout 失败，则标记 too-hard；如果两次都快速成功且无效率空间，则标记 saturated-easy。只有非饱和边进入四臂 N=1。只有 Correct 显示合理方向的 correctness/efficiency benefit，或 Wrong/Stale 显示机制一致的伤害，才进入 N=3。N=3 是筛选门控，不进行统计性过度解读。通过者追加到每组总计 N=5，满足 Correct 相比 Reset 和 Irrelevant 有重复优势、Wrong/Stale 不获得同等优势、trajectory 与预注册机制一致，才标记为 `causally_verified_v0`。
>
> 对每条 `causally_verified_v0` edge，再运行至少 N=2 的自然 producer→consumer Stateful 与 Reset consumer pilot。Natural Stateful 不要求必须优于 Reset；Oracle-only benefit、无自然复用和 negative transfer 都是有效实验结果。不得为了获得正向结果修改 instruction、experience provenance、Gold 或 verifier。达到 2–3 条 verified edges 后立即停止 Phase 3，并提交 `PHASE3_REPORT.md`、完整 screening 表、干预运行、Natural Stateful pilot 和可供 Phase 4 使用的 Verified Graph 清单。
