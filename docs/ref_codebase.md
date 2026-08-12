## 结论

最适合 CodeGraphCL 的不是“算法题式的小仓库”，也不是一开始就上 Django、Kubernetes 这种超大型工程，而是一组具有以下特征的中型基础设施仓库：

* 存在反复出现的工程约束，例如同步/异步一致性、配置优先级、插件作用域、API 双实现、协议版本或 schema 演进；
* 单个任务可以离线复现，并有可靠行为测试；
* 同一约束会跨多个 commit、模块或版本反复出现，天然形成 required、beneficial、scope、update、hard-negative 等边；
* 最终再加入一个跨模块应用仓库，验证经验是否能支持 integrated task。

因此我推荐采用一个 **“4 个诊断型仓库 + 1 个集成型仓库”** 的核心组合：

> **HTTPX + Viper + Fastify + clap，最后用 PocketBase 做集成验证。**

如果现在只选三个，我会选：

> **HTTPX、Viper、Fastify。**

另外，需要对 proposal 中的“真实开发任务”与现在的“合成 task”做一个边界处理：主论文数据最好仍然来自真实 commit/PR/issue；合成部分用于构造受控的 task family 和 history intervention，而不是把随机 mutation 描述成真实软件工程任务。

---

## 仓库筛选结果

以下评级是针对 CodeGraphCL setting，而不是对项目本身质量的评价。

| 级别 | 仓库                                                                              | 最自然的 experience/task graph                                                   | 执行与 verifier                                                                                                                  | 建议用途                                   |
| -- | ------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | -------------------------------------- |
| A+ | [encode/httpx](https://github.com/encode/httpx)                                 | sync/async parity、client/top-level API、transport、proxy、redirect、auth、timeout | BSD-3-Clause；pytest；网络测试有显式 marker；项目声称保持完整测试覆盖                                                                               | 最平衡的核心诊断仓库                             |
| A+ | [spf13/viper](https://github.com/spf13/viper)                                   | config/env/flag/default 优先级、alias、key normalization、reload、unmarshal         | MIT；Go 测试快；大量源码与 `_test.go` 配对；可只使用本地配置路径                                                                                     | Scope、Hard Negative、Stale/Update 的最佳仓库 |
| A+ | [fastify/fastify](https://github.com/fastify/fastify)                           | plugin encapsulation、hook 生命周期、decorator、schema、runtime/type parity          | MIT；单测、集成测试、类型测试和 coverage 都完善，见其 [package.json](https://github.com/fastify/fastify/blob/main/package.json)                   | 最适合研究作用域与跨接口 Join                      |
| A  | [clap-rs/clap](https://github.com/clap-rs/clap)                                 | builder/derive parity、help/error、completion、deprecated/unstable API          | MIT/Apache-2.0；测试强，但 Rust 编译和输出 snapshot 成本较高；[贡献规则](https://github.com/clap-rs/clap/blob/master/CONTRIBUTING.md)明确记录兼容性与弃用约束 | Fork/Join/Update；适合验证框架                |
| A  | [pocketbase/pocketbase](https://github.com/pocketbase/pocketbase)               | schema migration、validation、hooks、access rule、auth、API response              | MIT；Go + embedded SQLite，不需要独立数据库；官方使用 `go test ./...`                                                                        | 最合适的 integrated application repo       |
| A− | [go-git/go-git](https://github.com/go-git/go-git)                               | memory/filesystem storage parity、porcelain/plumbing、协议版本、跨平台路径               | Apache-2.0；纯 Go，但部分 fixture、网络和平台相关测试需要隔离                                                                                     | 第二阶段协议与存储扩展                            |
| A− | [BurntSushi/ripgrep](https://github.com/BurntSushi/ripgrep)                     | ignore/glob precedence、type filter、text/JSON 输出、preprocessor、跨平台行为           | MIT/Unlicense；集成测试强；Rust 编译成本中等                                                                                               | 快速验证合成环境及 CLI 行为                       |
| A− | [python-jsonschema/jsonschema](https://github.com/python-jsonschema/jsonschema) | 不同 draft 的语义范围、format、reference resolution、旧规则失效                             | MIT；可结合官方 [JSON Schema Test Suite](https://github.com/json-schema-org/JSON-Schema-Test-Suite)建立外部行为 verifier                  | 最干净的 Scope/Update 对照组                  |
| B+ | [pallets/click](https://github.com/pallets/click)                               | nested command、context、parameter inheritance、help、lazy loading               | BSD-3-Clause；Python 环境便宜，pytest 与 typing 测试完善                                                                                 | clap 的低成本替代或语言对照                       |
| B  | [npm/node-semver](https://github.com/npm/node-semver)                           | range intersection、prerelease、coerce、不同 API 表面一致性                            | ISC；测试极快且确定性高                                                                                                                 | pipeline control，不适合承担主要论文结论           |

### 为什么前三个最合适

**HTTPX** 的优势是一个工程行为经常需要同时出现在 sync client、async client、顶层快捷 API 和 transport 层。它天然产生 Fork 和 Join，而不是人为把两个无关任务连起来。代理、环境变量、重定向和认证还可以产生很好的 hard negative。

**Viper** 的项目契约非常明确：显式设置、flag、环境变量、配置文件、远程配置和 default 之间存在固定优先级；alias、大小写和 reload 又会改变适用范围。这几乎直接对应 proposal 中的 Scope、Wrong History、Stale/Update 和 Hard Negative。

**Fastify** 的 encapsulation 是非常强的“经验作用域”：父插件、子插件、兄弟插件中的 decorator、hook 和 schema 是否可见，存在明确而可执行的边界。同时它有 runtime tests 和 TypeScript type tests，能避免 verifier 只覆盖单一表面。

---

## 推荐的构建路线

### 1. 先把 synthetic task 定义成“graph-native task family”

不建议直接使用“随机 mutation → 修复单个 failing test”的独立任务生成方法。每个合成 family 应围绕一个真实项目 invariant 构造，例如：

| 仓库         | 候选 task family                                                                     | 可形成的边                               |
| ---------- | ---------------------------------------------------------------------------------- | ----------------------------------- |
| HTTPX      | 先修复 sync option propagation；再处理 async 对应路径；target 修改共享 transport 或 proxy 行为        | Fork、Join、Required、Hard Negative    |
| Viper      | 先建立 config/env precedence；再处理 alias/key normalization；target 组合 reload 与 unmarshal | Required、Scope、Wrong History、Update |
| Fastify    | 先学习 plugin encapsulation；再学习 hook ordering；target 修改嵌套插件的 decorator/schema 行为      | Scope、Join、Hard Negative            |
| clap       | builder API 与 derive macro 分别实现相同行为；target 同步 help/completion/error surface        | Fork、Join、Update                    |
| PocketBase | schema/migration 与 validation/hook 各自演进；target 影响 auth、access rule 和 API response  | Delayed、Join、Integrated             |

每个 family 最少应包含：

* 2 个 producer task；
* 1 个真正依赖这些经验的 target；
* 1 个表面相似但经验不适用的 hard negative；
* 如果仓库历史允许，再增加 1 个 stale/update node。

这样生成的不是一组孤立 bug，而是可以做经验干预的局部图。

### 2. 分阶段推进

**Phase 0：先验证基础设施**

使用 clap 和 ripgrep。它们已经有 [SWE-smith](https://github.com/SWE-bench/SWE-smith) 的仓库环境配置；公开实验中，ripgrep 和 clap 都成功产生过可验证的合成实例。不过只应复用 Docker、测试命令和日志解析，不要直接继承单 mutation 的任务语义。

SWE-smith 也出现过只运行部分测试、漏收集测试而导致 reward hacking 的问题，见其 [verifier exploit 讨论](https://github.com/SWE-bench/SWE-smith/issues/24)。CodeGraphCL 应强制检查：

* FAIL_TO_PASS；
* PASS_TO_PASS；
* 测试收集数量；
* gold patch 后完整回归；
* 是否意外跳过测试。

**Phase 1：核心诊断数据**

使用 HTTPX、Viper、Fastify：

* 每个仓库先做 4–6 个 family；
* 每个 family 约 4–6 个节点；
* 总计约 60–100 个 task nodes；
* 优先覆盖 Direct、Fork、Join、Scope、Hard Negative 和 Update。

这个规模已经足够检查经验检索和 causal intervention 是否有可测信号。

**Phase 2：集成验证**

使用 PocketBase 构造 2–3 个较大的 task graph，目标跨越：

* database/schema；
* application validation；
* hooks/events；
* auth/access control；
* HTTP API。

这部分数量不需要多，但应成为论文中证明经验依赖不只存在于小型库接口上的主要证据。

**Phase 3：泛化**

加入 go-git 和 jsonschema：

* go-git 检验 storage/backend/protocol 泛化；
* jsonschema 检验规范版本和 stale experience；
* Click 或 node-semver 作为低成本 control。

### 3. 建议的 repo 准入门槛

在正式纳入之前，我建议每个仓库通过以下 mining gate：

* 冷启动构建不超过约 15 分钟；
* 缓存后的目标 verifier 不超过约 2 分钟，完整回归不超过约 10 分钟；
* 默认路径不依赖公网或外部服务；
* 能挖到至少 20 个“源码与测试共同变化”的候选 commit；
* 最终能验证至少 8 个任务节点、3 种 graph motif；
* 至少出现一个非人为牵强的 Scope、Update 或 Hard Negative；
* base snapshot 必须失败、gold 必须通过，并保持 PASS_TO_PASS；
* 与 [SWE-bench](https://github.com/swe-bench/SWE-bench)、[Multi-SWE-bench](https://github.com/multi-swe-bench/multi-swe-bench) 及 SWE-smith 已有实例做 commit-level 去重。

---

## 暂不建议放进首批的仓库

* **Django、pytest、Pydantic**：历史和任务都丰富，但与已有软件工程 benchmark 重叠较高，而且环境与任务归因更复杂。
* **Kubernetes、DuckDB、大型数据库**：更适合最终压力测试；不适合早期迭代 verifier 和图标注。
* **Miniflux**：任务质量不错，但依赖 PostgreSQL，执行成本明显高于 PocketBase。
* **Axios、ESLint、Zod**：可以作为后续 JavaScript/TypeScript 泛化，但 monorepo、工具链或大版本迁移会增加 snapshot 管理成本。
* **mitmproxy**：协议和安全任务很好，但 TLS、平台和网络相关测试会削弱可重复性。
* **只有纯算法行为的小仓库**：例如仅做解析或数据结构的库，可以作为 pipeline control，但很难支撑“经验依赖的软件工程任务”这一核心论点。

最终建议是：**用 clap/ripgrep 快速跑通生成和执行基础设施；用 HTTPX/Viper/Fastify 建主实验；用 PocketBase 做 integrated claim；go-git/jsonschema 留作泛化与消融。** 所有仓库本身都是宽松许可证，但发布 benchmark 时仍需单独审计测试 fixture、子模块和复制数据的许可证。
