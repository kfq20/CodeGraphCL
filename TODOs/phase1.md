# Phase 1 Instruction：冻结 CodeGraphCL 的统一任务生产协议

## 1. 阶段目标与最终完成标准

截止 **2026 年 8 月 17 日**，完成 CodeGraphCL 第一阶段：

> 将现有 HTTPX 和 ripgrep 实验重构为统一、配置驱动的 Task → Edge → Family 构建与验证系统，使后续新增任务不再需要复制和修改一套专用 shell runner。

第一阶段结束时，必须能够使用同一组通用命令：

1. 验证一个 task 配置是否完整；
2. 构建对应 Docker 环境；
3. 执行 Base-fail、Gold-pass、PASS_TO_PASS 和 near-miss；
4. 检查 instruction 与 experience 是否可分离；
5. 生成 Reset、Correct、Irrelevant、Wrong/Stale 四种实验条件；
6. 执行 N=1 intervention smoke test；
7. 保存统一格式的结果、manifest、patch 和 verifier 日志。

第一阶段不是正式构建完整 task stream，也不要求扩大到新仓库。需要使用三个代表性任务验收统一协议：

* HTTPX T_B：已有 Python 任务和有效 negative-transfer 结果；
* ripgrep c3：当前已通过 Base-fail 和 Gold-pass；
* ripgrep c4：作为第一个完全通过新协议新增和物化的任务。

最终要求是：

> 新增一个 task 时，只需要提供配置、instruction、patch 和 verifier，不需要再编写 `run_xxx_agent.sh`、`run_xxx_episode.sh`、`run_xxx_batch.sh` 等任务专用脚本。

---

## 2. 建立统一的数据结构

请在仓库中建立清晰的 benchmark 资产目录。可以根据现有目录做小幅调整，但必须统一，不允许 HTTPX 和 ripgrep 各有一套格式。

建议结构：

```text
benchmark/
├── tasks/
│   ├── httpx_tB/
│   │   ├── task.yaml
│   │   ├── instruction.md
│   │   ├── gold.patch
│   │   ├── verifier/
│   │   └── near_miss/
│   ├── ripgrep_c3/
│   └── ripgrep_c4/
├── edges/
│   ├── httpx_tA_to_tB.yaml
│   ├── ripgrep_c2_to_c3.yaml
│   └── ripgrep_c3_to_c4.yaml
├── families/
│   ├── httpx_start_tls.yaml
│   └── ripgrep_ignore_path.yaml
└── schemas/
    ├── task.schema.json
    ├── edge.schema.json
    └── family.schema.json
```

### 2.1 `task.yaml`

每个任务至少包含：

```yaml
schema_version: 1
task_id: ripgrep_c3
family_id: ripgrep_ignore_path

repository:
  url: https://github.com/BurntSushi/ripgrep
  base_commit: f722268...
  gold_commit: 14f4957b3d...
  language: rust

instruction:
  path: instruction.md

environment:
  dockerfile: ...
  image: ...
  workdir: /workspace/repo
  build_timeout_sec: 900

patches:
  gold: gold.patch
  verifier: verifier.patch

verifier:
  command: cargo test --test integration r829
  timeout_sec: 300
  fail_to_pass:
    - ...
  pass_to_pass:
    - ...
  near_miss:
    - near_miss/over_strip.patch
    - near_miss/no_strip.patch

separability:
  banned_words: banned_words.txt
  checklist: separability.checklist.yaml

status:
  semantic_audit: passed
  separability_gate: pending
  executable_gate: pending
  intervention_preflight: pending
```

字段名称可以适当调整，但语义不能缺失。禁止在 runner 中写死 task ID、commit、容器名、测试选择器和 patch 路径。

### 2.2 `edge.yaml`

每条经验边至少包含：

```yaml
schema_version: 1
edge_id: ripgrep_c3_to_c4
from: ripgrep_c3
to: ripgrep_c4
edge_type: beneficial_update

experience:
  statement: ...
  type: path_canonicalization_rule
  scope: crates/ignore/src/dir.rs
  provenance:
    repository: ripgrep
    commit: 14f4957b3d
  validity: valid_for_c4

conditions:
  reset: null
  correct: correct
  irrelevant: irrelevant
  stale: stale_from_c2

expected_effect:
  correctness: possible
  efficiency: possible
  negative_transfer: possible

status:
  semantic_audit: passed
  causal_verification: pending
```

必须区分以下状态：

* `proposed`
* `semantically_audited`
* `executable_verified`
* `intervention_smoke`
* `causally_verified`
* `rejected`

不能只写模糊的 `complete`。

### 2.3 `family.yaml`

每个 family 至少记录：

```yaml
family_id: ripgrep_ignore_path
repository: ripgrep

nodes:
  - ripgrep_c2
  - ripgrep_c3
  - ripgrep_c4

edges:
  - ripgrep_c2_to_c3
  - ripgrep_c3_to_c4

structure:
  type: update_chain
  order:
    - ripgrep_c2
    - ripgrep_c3
    - ripgrep_c4

diagnostic_targets:
  - target: ripgrep_c3
    conditions:
      - reset
      - oracle_revision
      - irrelevant
      - stale_from_c2
  - target: ripgrep_c4
    conditions:
      - reset
      - correct_from_c3
      - irrelevant
      - stale_from_c2
```

第一阶段只需要定义 family，不需要正式运行多节点 Stateful stream。

---

## 3. 实现通用命令入口

请建立统一的 Python CLI，例如：

```bash
python -m codegraphcl validate benchmark/tasks/ripgrep_c3
python -m codegraphcl materialize benchmark/tasks/ripgrep_c3
python -m codegraphcl prompt-preview benchmark/edges/ripgrep_c3_to_c4
python -m codegraphcl intervene benchmark/edges/ripgrep_c3_to_c4 --n 1 --seed 42
python -m codegraphcl summarize runs/<run_id>
```

现有 shell 脚本可以暂时作为底层实现，但上层入口必须统一。通用代码中不得出现：

* `httpx`
* `ripgrep`
* `start_tls`
* `r829`
* 固定 SHA
* `/vePFS-Mindverse/...`
* 固定容器名，如 `cgcl-rg-box`
* condition 名称出现在 agent 可见路径中

### 3.1 `validate`

必须检查：

* task、edge、family 配置符合 schema；
* Base 和 Gold commit 均存在；
* instruction、patch、verifier 文件存在；
* 非 Reset experience 不为空；
* producer commit 与 experience provenance 一致；
* Separability checklist 已人工填写；
* banned mechanism words 没有出现在 instruction 中；
* family 引用的 node 和 edge 都存在。

任何检查 inconclusive 都不能输出 `passed`。

### 3.2 `materialize`

统一执行：

1. Checkout Base；
2. Base + Verifier，必须产生目标行为失败；
3. Base + Gold + Verifier，必须通过；
4. 记录 Base 上原本通过的 PASS_TO_PASS 集合；
5. Gold 后重新运行同一集合；
6. 任一原测试从通过变成失败，则任务拒绝；
7. 应用至少两个 near-miss；
8. near-miss 如果通过 verifier，则任务拒绝。

输出：

```text
runs/<run_id>/
├── run_manifest.json
├── materialization_result.json
├── base_fail.log
├── gold_pass.log
├── pass_to_pass.log
├── near_miss_1.log
└── near_miss_2.log
```

`materialization_result.json` 必须明确区分：

* `passed`
* `task_failure`
* `verifier_failure`
* `environment_failure`
* `timeout`
* `inconclusive`

### 3.3 `prompt-preview`

在正式调用 agent 前生成四种 prompt，并检查：

* 非 Reset prefix 非空；
* 四种 prefix hash 不同；
* instruction hash 完全相同；
* condition 名称不出现在 prompt、工作目录或 episode ID 中；
* 保存 `prefix_chars`、`prefix_sha256`、`instruction_sha256`；
* agent 可见 prompt 与 manifest 中记录的 prompt 完全一致。

Episode ID 使用：

```text
ep_000001
ep_000002
```

禁止使用：

```text
ripgrep_wrong_1
batch_correct_2
```

### 3.4 `intervene`

第一阶段只要求 N=1 smoke test，但必须支持：

```bash
--conditions reset,correct,irrelevant,wrong
--n 1
--seed 42
```

每次运行保存：

* opaque episode ID；
* condition，仅保存在 agent 不可见的 manifest；
* model 和 harness 版本；
* Base commit；
* instruction/prefix hash；
* agent 最终 patch；
* reward；
* failure taxonomy；
* elapsed time；
* input/output/cache tokens；
* tool calls；
* assistant turns；
* verifier stdout；
* trajectory 文件位置及 hash。

Timeout 后如果已有 patch，仍然运行 verifier，并标记为 `timeout_solved` 或 `timeout_failed`，不能简单记成普通 reward 0。

---

## 4. 使用三个任务验收协议

### 4.1 HTTPX T_B：迁移已有任务

不要重新设计 HTTPX T_B。将现有 instruction、hermetic TLS verifier、Gold patch、near-miss 和 N=3 结果迁入统一格式。

验收：

* 通用 `validate` 通过；
* 通用 `materialize` 能复现 Base-fail、Gold-pass 和 near-miss；
* 原始实验状态记录为：

```text
negative transfer verified
positive transfer not observed
edge status: partial / diagnostic-only
```

保留历史无效实验记录，但明确标记为 voided，不删除。

### 4.2 ripgrep c3：补齐完整 Executable Gate

当前已有：

* Base-fail；
* Gold-pass；
* 两个局部 PASS_TO_PASS 测试。

还需要：

1. 两个 near-miss，例如：

   * 继续使用 c2 的粗粒度 prefix strip；
   * 完全取消相对化或只处理 `./rust` 而不处理 `rust`。

2. 添加：

   * `banned_words.txt`
   * `separability.checklist.yaml`

3. 人工确认：

   * c2 atom 只包含 c2 当时知道的“避免重复路径”；
   * 不包含 c3 才发现的 over-strip 原理；
   * instruction 不出现 `strip_prefix`、over-strip、path-component ordering 等实现提示；
   * stale-from-c2 不被 instruction 直接否定。

完成后用通用 runner 跑 N=1：

* Reset
* Oracle Revision
* Irrelevant
* Stale-from-c2

这里只做 preflight，不直接扩 N=3。

### 4.3 ripgrep c4：证明新协议可以生产新任务

c4 必须从头通过统一协议，不允许复制一套 `run_c4_*.sh`。

需要完成：

* task 配置；
* instruction；
* Gold/Verifier patch；
* Base-fail；
* Gold-pass；
* PASS_TO_PASS；
* 两个 near-miss；
* Separability Gate；
* 四种 experience condition；
* N=1 intervention preflight。

c4 的条件必须是：

* Reset；
* Correct-from-c3；
* Irrelevant；
* Stale-from-c2。

如果 c4 四种条件全部饱和，记录为无分离，不允许修改 instruction 追求想要的结果。第一阶段验收关注的是 pipeline 可复用，不要求一定得到 positive transfer。

---

## 5. 时间安排、禁止事项与交付报告

### Day 1

* 定义 task/edge/family schema；
* 实现 `validate`；
* 将 HTTPX T_B 迁入统一格式。

### Day 2

* 实现通用 `materialize`；
* 完成 ripgrep c3 near-miss 和 Separability checklist；
* 用通用命令复现 c3 完整 Executable Gate。

### Day 3

* 实现 `prompt-preview` 和通用 `intervene`；
* 迁移 opaque ID、manifest、failure taxonomy、token 统计；
* 在 HTTPX T_B 或 ripgrep c3 上完成一次通用 N=1 smoke。

### Day 4

* 使用新协议物化 ripgrep c4；
* 完成 c4 N=1 intervention preflight。

### Day 5

* 修复跨任务复用问题；
* 完成文档、示例命令和结果汇总；
* 提交 `PHASE1_REPORT.md`。

### 第一阶段禁止事项

* 不新增第四个 task 或新仓库；
* 不运行大规模 N=3/N=5；
* 不继续调整 HTTPX instruction；
* 不为了制造显著差异修改 experience；
* 不复制新的任务专用 runner；
* 不将 environment error 记为 task failure；
* 不将 skipped、inconclusive 或 partial PASS_TO_PASS 写成通过；
* 不删除失败或 rejected family 的记录；
* 不提前构造正式 Stateful task stream。

### 最终交付

提交：

```text
PHASE1_REPORT.md
```

内容必须包括：

1. 最终目录和 schema；
2. 五个通用命令及运行示例；
3. HTTPX T_B、ripgrep c3、ripgrep c4 的 gate 表；
4. 每个任务的状态和拒绝原因；
5. N=1 intervention preflight 结果；
6. 当前 executable node、audited edge、intervention-ready edge 数量；
7. 下一阶段批量生产新 family 时的标准操作流程；
8. 尚未解决的工程问题，不得隐藏。

第一阶段最终验收标准：

> 在一个干净工作目录中，HTTPX T_B 和 ripgrep c3 能通过同一套通用命令完成验证；ripgrep c4 能在不新增任务专用 runner 的情况下完成配置、物化和 N=1 intervention。达到这一标准后，统一协议冻结，第二阶段只允许修复通用框架 bug，不再为单个 task 改变数据格式和执行流程。
