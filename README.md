<div align="center">

# 🛡️ BaselineGuard

**零依赖 · 离线优先 · 面向 AI 编码代理的 Web 平台 Baseline 守卫**

*Zero-dependency · Offline-first · Web platform Baseline guard for AI coding agents*

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Dependencies](https://img.shields.io/badge/runtime%20deps-0-brightgreen)](pyproject.toml)
[![Tests](https://img.shields.io/badge/tests-67%20passed-success)](scripts/test.sh)
[![Offline](https://img.shields.io/badge/network-none-orange)](README.md)

[简体中文](#zh-cn) · [繁體中文](#zh-tw) · [English](#en)

</div>

---

<a id="zh-cn"></a>

# 简体中文

## 🎉 项目介绍

**BaselineGuard** 是一个**零第三方依赖、纯 Python 标准库、完全离线**的命令行工具：它扫描你的 HTML / CSS / JavaScript 源码，找出其中用到的 Web 平台特性，按「Baseline 兼容基线」判定哪些能用、哪些需要人工确认、哪些必须删掉；同时把这份策略**自动生成给 AI 编码代理阅读的上下文文件**（`AGENTS.md` / `CLAUDE.md` / `.cursorrules`），从源头约束代理生成的代码。

**它解决的真实痛点：**

| 痛点 | 现状 | BaselineGuard 的做法 |
| --- | --- | --- |
| 🤖 AI 编码代理知识过时或过度超前 | 代理常写出已废弃的 `<center>`，或冒出尚未普及的 View Transitions | 把「允许 / 需审批 / 禁止」三张清单写进代理上下文，生成前先约束 |
| 📄 最佳实践文档只能「读」，不能「执行」 | 文档无法进 CI，也没人检查代码是否遵守 | 一条命令变成 CI 门禁，带语义化退出码 |
| 🌐 兼容性查询依赖在线服务 | 构建期拉数据、内网不可用、结果不稳定 | 规则集随包分发，扫描全程零网络请求 |
| 🧩 团队基线各不相同 | 「我们支持到哪一年」全靠口头约定 | `--baseline 2021` 把约定变成可版本化的策略文件 |

**自研差异化亮点：** 与「静态知识库 / 规则文档」类项目不同，BaselineGuard 是**可执行的策略引擎 + 代理上下文生成器**：规则集带年份语义可按目标基线裁剪；上下文写入采用**标记块幂等替换**，重复运行只更新机器生成区、绝不覆盖开发者手写内容；报告同时输出 `text` / `json` / `markdown` 三种格式，可直接贴进 PR 或喂给其他工具。

**灵感来源：** 参考了 2026-11-15 GitHub Trending 日榜增长第一的 [GoogleChrome/modern-web-guidance-src](https://github.com/GoogleChrome/modern-web-guidance-src) 所提出的「*Keep your coding agent up to date with the latest web best practices*」这一**产品理念与用户痛点**。本项目**仅参考产品逻辑，未复制其任何代码或文档内容**，规则数据、检测引擎、策略模型、上下文生成与全部工程实现均为 100% 独立自研，采用 MIT 协议开源。

> 📌 本项目属于**插件 / 脚本 / 工具库 / CLI 类**项目：按发布规范无需上传跨平台二进制与 Release 附件，完整的安装、集成与使用步骤全部写在本 README 中，开箱即用。

---

## ✨ 核心特性

- 📚 **41 条内置规则**，覆盖 CSS、HTML、JS / Web API，四级状态：`widely`（广泛可用）/ `newly`（新近可用）/ `limited`（支持有限）/ `deprecated`（已废弃）。
- 🚦 **双维度策略引擎**：`--baseline 2021` 按年份裁剪 `widely` 规则；`--allow-newly` / `--allow-limited` 独立控制风险等级 —— 年份与风险等级互不混淆，判定逻辑可解释、可测试。
- 🔍 **注释掩码检测**：扫描前先屏蔽 `/* */`、`<!-- -->` 与整行 `//` 注释，且**保持字符长度与换行不变**，因此行号列号与源码严格一致；`https://` 之类的 URL 不会被误伤。
- 🧹 **同一规则同一行自动去重**，自动跳过 `node_modules` / `dist` / `.git` 等生成目录，并限制超大文件，避免压缩产物制造噪声。
- 🤖 **代理上下文生成**：一键产出 `AGENTS.md` / `CLAUDE.md` / `.cursorrules` / Markdown 策略块，内含给 AI 代理的 5 条明确指令与 ALLOW / REVIEW / DENY 三张清单。
- ♻️ **幂等写入**：`<!-- baselineguard:begin -->` … `<!-- baselineguard:end -->` 标记块，重复执行只替换标记内内容，手写段落原样保留。
- 📊 **三种报告格式**：终端友好的 `text`、机器可读的 `json`、适合贴 PR 的 `markdown`。
- 🚪 **CI 就绪**：`--fail-on error|warning|none` 控制退出码（0 / 1），参数错误返回 2；可写 `$GITHUB_STEP_SUMMARY`。
- 🧩 **自定义规则集**：`--rules` 支持 `replace`（完全替换）与 `extend`（覆盖单条 + 新增）两种模式，附 `rules validate` 预校验。
- 🌍 **跨平台**：Windows / macOS / Linux 通用，Python 3.9+，无编译器、无 wheel、无网络、无环境变量陷阱。
- 📦 **单文件分发**：`scripts/build.sh` 用标准库 `zipapp` 产出 `dist/baselineguard.pyz`，拷到任何机器 `python3 baselineguard.pyz` 即可运行。

---

## 🚀 快速开始

**环境要求：** Python **3.9+**（已在 3.9 / 3.10 / 3.11 / 3.12 / 3.13 上纳入 CI）、任意操作系统、**零第三方依赖**、**无需联网**。

```bash
# 方式 A：零安装，克隆即用（推荐先试）
git clone https://github.com/gitstq/BaselineGuard.git
cd BaselineGuard
PYTHONPATH=src python3 -m baselineguard --version
PYTHONPATH=src python3 -m baselineguard scan . --baseline widely

# 方式 B：安装成全局命令
python3 -m pip install -e .
baselineguard scan ./src --format markdown

# 方式 C：打包成单文件，随处运行
bash scripts/build.sh
python3 dist/baselineguard.pyz scan ./src
```

**三条最常用命令（可直接复制）：**

```bash
# 1) 扫描并把报告写进文件（CI 里最常用）
baselineguard scan ./src --baseline 2021 --format json --fail-on error -o report.json

# 2) 生成给 AI 编码代理的策略文件
baselineguard context --baseline 2023 --format agents-md --out AGENTS.md

# 3) 检查自定义规则集是否合法
baselineguard rules validate examples/custom-rules.json
```

**验证安装是否成功：**

```bash
bash scripts/test.sh     # 67 项单元测试
bash scripts/demo.sh     # 60 秒可复现演示
```

> 💡 Windows PowerShell 用 `$env:PYTHONPATH="src"; python -m baselineguard scan .`；zipapp 则为 `python dist\baselineguard.pyz scan .`。

---

## 📖 详细使用指南

### 4.1 `scan` —— 扫描与判定

```bash
baselineguard scan PATH [选项]
```

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `PATH` | `.` | 单个文件或目录 |
| `--baseline` | `widely` | 目标基线：`2018`…`2025` 等年份，或预设 `widely`(2021) / `newly`(2024) / `limited`(9999) |
| `--format` | `text` | `text` / `json` / `markdown` |
| `--fail-on` | `error` | `error`（仅违规阻断）/ `warning`（警告也阻断）/ `none`（永不阻断） |
| `--allow-newly` | 关闭 | 把 `newly` 降为 `info` |
| `--allow-limited` | 关闭 | 把 `limited` 从 `error` 降为 `warning` |
| `--rules FILE` | 内置 | 自定义规则集 JSON |
| `--include GLOB` / `--exclude GLOB` | 无 | 相对路径 glob，可重复 |
| `--include-docs` | 关闭 | 同时扫描 `.md` / `.mdx` |
| `--no-ignore` | 关闭 | 不跳过 `node_modules` / `dist` / `.git` 等 |
| `-o, --output FILE` | stdout | 写入文件 |
| `--quiet` | 关闭 | 静默（仍写 `--output`） |

**判定规则（重要，避免误解）：**

| 规则状态 | 默认严重度 | 说明 |
| --- | --- | --- |
| `widely`，年份 ≤ 目标年份 | `info` | 在承诺基线内，允许使用 |
| `widely`，年份 > 目标年份 | `warning` | 广泛可用的时间晚于项目承诺 |
| `newly` | `warning` | 尚未进入 Widely Baseline；**提高年份不会自动放行**，须显式 `--allow-newly` |
| `limited` | `error` | 四大引擎未全部支持；`--allow-limited` 可降为 `warning` |
| `deprecated` | `error` | 永远禁止，无任何开关可放宽 |

> 🧠 设计取舍：年份只作用于 `widely`，风险等级由独立开关控制。因为「2023 年新近可用」与「2023 年已广泛可用」是**性质不同**的两件事，用同一个数字去放行会掩盖风险。

**演示输出（运行 `bash scripts/demo.sh` 即可复现；📷 截图 / 🎞️ 演示动图位置预留于此）：**

```text
BaselineGuard 1.0.0 | offline Web platform Baseline guard
Target : widely (widely <= 2021) | allow-newly=false allow-limited=false fail-on=none
Ruleset: baselineguard-default-ruleset 1.0.0 (41 rules, builtin)
Scan   : 3 files / 57 lines in 1 ms | root=tests/fixtures

[X] ERROR   - violations that break the policy (3)
  [html-marquee] <marquee>  (deprecated)
    sample.html:11:3  <marquee behavior="scroll">legacy ticker</marquee>
    why      : Deprecated or removed Web feature; must not appear in new code.
    action   : Replace with CSS animations (transform / @keyframes).
  [css-view-transitions] CSS View Transitions  (limited)
    sample.css:16:3  view-transition-name: hero;
    action   : Not available in all major engines. Always wrap with @supports ...

Result : FAILED  (error=3, warning=8, info=15, total=26)  exit=1
```

### 4.2 `context` —— 生成 AI 编码代理策略

```bash
baselineguard context --baseline 2023 --format agents-md --out AGENTS.md
baselineguard context --format claude-md --out CLAUDE.md
baselineguard context --format cursorrules --out .cursorrules
baselineguard context --format markdown --stdout   # 只预览，不写文件
```

| `--format` | 默认输出 | 标记语法 |
| --- | --- | --- |
| `agents-md` | `AGENTS.md` | HTML 注释标记 |
| `claude-md` | `CLAUDE.md` | HTML 注释标记 |
| `cursorrules` | `.cursorrules` | `# baselineguard:begin/end`，纯文本无表格 |
| `markdown` | `WEB_BASELINE_POLICY.md` | HTML 注释标记 |

生成块内含：**5 条给代理的明确指令**（生成前先查清单、禁止 DENY 项、REVIEW 项需人工批准且必须写降级方案、不要为「更新」而重写可用代码、检查新依赖是否偷带新特性）以及 ALLOW / REVIEW / DENY 三张带 MDN 链接的清单。

**幂等性示例**（第二次运行只更新标记块，`status` 为 `unchanged` / `updated`）：

```bash
baselineguard context --out AGENTS.md
# context created: AGENTS.md (allow/review/deny policy for 41 rules, baseline widely)
baselineguard context --out AGENTS.md
# context unchanged: AGENTS.md (...)
```

### 4.3 `rules` —— 规则集管理

```bash
baselineguard rules list --status newly
baselineguard rules list --format json
baselineguard rules show css-has
baselineguard rules validate examples/custom-rules.json
baselineguard rules list --rules examples/custom-rules.json
```

自定义规则集示例（`mode: extend` = 覆盖内置 `css-nesting` + 新增一条私有规则）：

```json
{
  "mode": "extend",
  "rules": [
    {
      "id": "project-legacy-widget",
      "name": "Legacy jQuery widget bootstrap",
      "category": "script",
      "status": "deprecated",
      "baseline_year": null,
      "applies_to": ["script"],
      "patterns": ["legacyWidget\\.init\\s*\\("],
      "suggestion": "Migrate to the Web Component in src/components/.",
      "reference": "https://example.com/internal/migration-guide"
    }
  ]
}
```

完整字段说明见 [examples/README.md](examples/README.md)。九个字须齐全，`patterns` 为 Python `re` 正则（JSON 中反斜杠要双写），`validate` 会检查状态枚举、正则合法性、ID 唯一性与重复。

### 4.4 集成进 CI（可直接复制）

```yaml
# .github/workflows/baseline.yml
name: Web Baseline gate
on: [push, pull_request]
jobs:
  gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - name: Install (no third-party runtime deps)
        run: python3 -m pip install -e .
      - name: Baseline gate
        run: |
          baselineguard scan ./src --baseline 2021 --fail-on warning \
            --format markdown >> "$GITHUB_STEP_SUMMARY"
      - name: Machine-readable report
        if: always()
        run: baselineguard scan ./src --format json --fail-on none -o report.json
```

**退出码约定：** `0` = 通过（或 `--fail-on none`），`1` = 命中阻断级别，`2` = 参数 / 路径 / 规则集错误。`--fail-on none` 配合 `--format json -o` 适合「只收集、不阻断」的观测场景。

### 4.5 典型使用场景

| 场景 | 命令 |
| --- | --- |
| 🏗️ 新项目立项，锁定保守基线 | `baselineguard context --baseline widely --out AGENTS.md` |
| 🔍 老代码体检，找出废弃标签 | `baselineguard scan . --format markdown --fail-on none` |
| 🚦 PR 门禁，禁止 `limited` 特性 | `baselineguard scan ./src --fail-on error` |
| 🤖 给 Claude / Cursor / Codex 投放策略 | `baselineguard context --format claude-md --out CLAUDE.md` |
| 🧩 团队私有规范 | `baselineguard scan . --rules team-rules.json` |
| 📈 基线升级评估 | 对比 `--baseline 2021` 与 `--baseline 2024` 的 `warning` 数量 |

### 4.6 ❓ 常见问题

<details>
<summary><b>会误报吗？如何抑制？</b></summary>

注释已被掩码，但**字符串字面量内的文本仍可能命中**（例如文档字符串里写了 `document.write`）。用 `--exclude 'docs/**'` 排除，或在自定义规则集里把该 `patterns` 改得更具体。检测目标是「特性是否出现」这一信号，而非完整语义解析。
</details>

<details>
<summary><b>和 caniuse / browserslist / Babel 有什么区别？</b></summary>

那些解决「运行时 / 构建期兼容性数据与转译」；BaselineGuard 解决「**策略治理**」：把团队承诺的基线写进版本库、让 AI 代理在写代码前就读到、并在 CI 里对源码做门禁。二者互补，不冲突。
</details>

<details>
<summary><b>需要联网吗？会读取我的密钥或环境变量吗？</b></summary>

完全不联网，不读取任何环境变量、不读取 `.env`、不发起任何 HTTP 请求。规则集随包分发（zipapp 内也可读），扫描仅访问你显式指定的路径。
</details>

<details>
<summary><b>为什么用正则而不是 AST？</b></summary>

零依赖是硬约束，且需要同时处理混合了 HTML / CSS / JS 的 `.vue` / `.svelte` / `.astro` 文件。正则足以识别「特性出现」这个信号，扫描 57 行仅 1 ms；若未来需要精确语义，可作为可选插件扩展而不污染零依赖内核。
</details>

<details>
<summary><b>规则里的年份权威吗？</b></summary>

`baseline_year` 是一份**可维护的社区快照**，用于策略裁剪，不是权威兼容性断言，也不替代真机测试。团队可用 `--rules` 覆盖；规则集自带 `version`，升级时会记录在 CHANGELOG。
</details>

<details>
<summary><b>支持哪些文件？</b></summary>

`.css/.scss/.less`、`.html/.htm/.vue/.svelte/.astro`、`.js/.mjs/.cjs/.jsx/.ts/.tsx/.mts/.cts`；`.md/.mdx` 需 `--include-docs`。`.vue` 等单文件组件会同时按 markup + css + script 三类检测。
</details>

---

## 💡 设计思路与迭代规划

**设计理念**

1. **策略即代码**：把「我们兼容到哪一年」从口头约定变成 `--baseline` 参数与可提交的 `AGENTS.md`，Code Review 有据可依。
2. **约束前移**：与其事后 review AI 生成的代码，不如在生成前就把 ALLOW / REVIEW / DENY 清单交给代理 —— 这是本项目相对「静态最佳实践文档」最核心的差异化。
3. **零依赖优先**：只用标准库（`argparse` / `re` / `pathlib` / `dataclasses` / `unittest` / `zipapp` / `importlib.resources`），换来「内网可用、无供应链风险、无版本地狱、跨平台零编译」。
4. **可解释胜于智能**：规则、状态、年份、建议、MDN 链接全部显式可读；每条 finding 都带 `why` 与 `action`，不输出黑盒分数。

**技术选型**

| 选择 | 原因 |
| --- | --- |
| Python 3.9+ 标准库 | 跨平台、CI 镜像自带、无第三方依赖 |
| 规则集用 JSON 而非代码 | 可版本化、可 `validate`、可被其他工具消费、可由非开发者维护 |
| `dataclass(frozen=True)` | 规则 / 策略 / finding 不可变，测试确定性高 |
| `zipapp` | 标准库内建，产出单文件 `.pyz`，无 wheel 无编译 |
| `importlib.resources` | 规则集在源码树、安装包、zipapp 三种形态下都能读取 |

**🗺️ 迭代路线图**

- **v1.1**：规则集扩容至 80+；规则集带 SHA-256 自校验，便于团队锁定版本。
- **v1.2**：新增 SARIF 输出，接入 GitHub Code Scanning 的行级注解。
- **v1.3**：提供 `--explain <rule-id>` 与离线规则集 diff 报告（比较两个基线版本）。
- **v2.0**：可选 AST 插件接口（核心仍保持零依赖）；更多代理格式适配。

**社区贡献方向**：补充规则、修正年份、新增语言版本的 README、更多 CI 平台示例（GitLab CI / Jenkins / 腾讯工蜂）、以及针对框架模板的误报优化。

---

## 📦 打包与部署指南

> 按项目分类规则，BaselineGuard 属于**工具库 / CLI 类**，因此**不提供 Windows / macOS / Linux 二进制与 Release 附件**，也不做跨平台可执行打包 —— 纯 Python 本身就跨平台，避免了「上传无法运行的产物」的风险。安装与集成步骤见上文「快速开始」与「CI 集成」。

| 分发方式 | 命令 | 适用场景 |
| --- | --- | --- |
| 🟢 源码零安装 | `PYTHONPATH=src python3 -m baselineguard ...` | 内网、临时扫描、CI 免安装 |
| 🔵 可编辑安装 | `python3 -m pip install -e .` | 本地开发、获得 `baselineguard` 命令 |
| 🟣 单文件 zipapp | `bash scripts/build.sh` → `dist/baselineguard.pyz` | 拷贝分发、离线机器、无 pip 环境 |
| ⚪ 发布到 PyPI（维护者可选） | `python3 -m build && python3 -m twine upload dist/*` | 仅发布者需要 `build`/`twine`，**不是运行时依赖** |

**兼容环境矩阵**

| 项 | 支持范围 |
| --- | --- |
| Python | 3.9 / 3.10 / 3.11 / 3.12 / 3.13（CI 矩阵验证） |
| 操作系统 | Windows / macOS / Linux（含 WSL、Git Bash） |
| 运行时第三方依赖 | **无** |
| 网络 | **不需要**（扫描与上下文生成全程离线） |
| 最小权限 | 只需读取待扫描目录、写入 `--output` / `--out` 指定文件 |
| 构建要求 | Python 3.9+ 与 bash（Windows 可用 Git Bash / WSL） |

**部署检查清单**：`bash scripts/test.sh` → `bash scripts/build.sh` → `python3 dist/baselineguard.pyz rules validate src/baselineguard/data/rules.json` → 在目标机器跑一次 `scan --format json --fail-on none`。

**注意事项**

- `.gitignore` 已排除 `.env`、`*.secret`、构建产物与生成报告，避免误提交凭据。
- `--no-ignore` 会扫描 `node_modules`，通常很慢且噪声大，仅用于排查。
- 单文件超过 2 MB 会被跳过（多为压缩产物），可用 `--include` 精确指定。
- 策略变更请同步更新 `AGENTS.md` 并在 PR 中说明，避免代理仍按旧清单生成代码。

---

## 🤝 贡献指南

欢迎提交 Issue 与 PR！请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

**三条硬性约定**：① 不得引入任何运行时第三方依赖；② 不得在扫描期发起网络请求；③ 代码与规则数据必须为原创，不得复制其他项目实现。

```bash
git clone https://github.com/gitstq/BaselineGuard.git
cd BaselineGuard
bash scripts/test.sh    # 提交前必须通过
bash scripts/demo.sh    # 复现演示
```

**提交信息遵循 Angular 规范**：`feat:` / `fix:` / `docs:` / `test:` / `refactor:` / `chore:`，例如 `feat: detect CSS anchor positioning`。

**PR 要求**：一个 PR 只做一件事；附上测试输出；若改动用户可见行为，必须同步更新本 README 的**三个语言版本**；不要提交生成报告、`dist/*.pyz` 或任何凭据文件。

**Issue 请附**：完整命令、`--format json` 报告、Python 版本、操作系统，以及可复现的最小源码片段。

---

## 📄 开源协议说明

本项目采用 **MIT License** —— Copyright (c) 2026 gitstq。详见 [LICENSE](LICENSE)：可自由使用、复制、修改、合并、发布、分发、再授权与商用，只需保留版权与许可声明；软件按「现状」提供，不含任何担保。

规则集中的 `reference` 字段仅指向 MDN 等公开文档供查阅，**不包含任何从第三方复制的代码或文档内容**；规则的模式、分级与建议文案均为本项目独立编写。内置规则集 `baselineguard-default-ruleset 1.0.0` 同样按 MIT 提供。

---
---

<a id="zh-tw"></a>

# 繁體中文

## 🎉 專案介紹

**BaselineGuard** 是一套**零第三方依賴、純 Python 標準庫、完全離線**的命令列工具。它掃描 HTML / CSS / JavaScript 原始碼，辨識當中用到的 Web 平台特性，依「Baseline 相容基準」判定哪些可用、哪些需要人工確認、哪些必須移除；同時把這份策略**自動產生成給 AI 編碼代理閱讀的上下文檔**（`AGENTS.md` / `CLAUDE.md` / `.cursorrules`），從源頭約束代理產生的程式碼。

**它解決的真實痛點：**

| 痛點 | 現況 | BaselineGuard 的做法 |
| --- | --- | --- |
| 🤖 AI 代理知識過時或過度超前 | 常寫出已淘汰的 `<center>`，或冒出尚未普及的 View Transitions | 把「允許 / 需審核 / 禁止」三張清單寫進代理上下文，生成前先約束 |
| 📄 最佳實踐文件只能「讀」不能「執行」 | 文件進不了 CI，也沒人檢查程式碼是否遵守 | 一條指令變成 CI 關卡，附語意化結束碼 |
| 🌐 相容性查詢依賴線上服務 | 建置期拉資料、內網不可用、結果不穩定 | 規則集隨套件散佈，掃描全程零網路請求 |
| 🧩 團隊基準各自表述 | 「我們支援到哪一年」全靠口頭約定 | `--baseline 2021` 把約定變成可版本化的策略檔 |

**自研差異化亮點：** 相較於「靜態知識庫 / 規則文件」類專案，BaselineGuard 是**可執行的策略引擎 + 代理上下文產生器**：規則集帶年份語意，可依目標基準裁剪；上下文寫入採用**標記區塊冪等替換**，重複執行只更新機器產生區，絕不覆蓋開發者手寫內容；報告同時輸出 `text` / `json` / `markdown`，可直接貼進 PR 或交給其他工具。

**靈感來源：** 參考 2026-11-15 GitHub Trending 日榜成長第一的 [GoogleChrome/modern-web-guidance-src](https://github.com/GoogleChrome/modern-web-guidance-src) 提出的「*Keep your coding agent up to date with the latest web best practices*」**產品理念與使用者痛點**。本專案**僅參考產品邏輯，未複製其任何程式碼或文件內容**；規則資料、偵測引擎、策略模型、上下文產生與全部工程實作皆為 100% 獨立自研，以 MIT 授權開源。

> 📌 本專案屬**外掛 / 指令稿 / 工具庫 / CLI 類**：依發布規範無需上傳跨平台執行檔與 Release 附件，完整安裝、整合與使用步驟皆寫於本 README，開箱即用。

---

## ✨ 核心特性

- 📚 **41 條內建規則**，涵蓋 CSS、HTML、JS / Web API，四種狀態：`widely`（廣泛可用）/ `newly`（新近可用）/ `limited`（支援有限）/ `deprecated`（已淘汰）。
- 🚦 **雙維度策略引擎**：`--baseline 2021` 依年份裁剪 `widely` 規則；`--allow-newly` / `--allow-limited` 獨立控制風險等級 —— 年份與風險不混為一談，判定可解釋、可測試。
- 🔍 **註解遮罩偵測**：掃描前先屏蔽 `/* */`、`<!-- -->` 與整行 `//` 註解，且**保持字元長度與換行不變**，行號欄位與原始碼嚴格一致；`https://` 之類 URL 不會被誤傷。
- 🧹 **同一規則同一行自動去重**，自動略過 `node_modules` / `dist` / `.git` 等產生目錄，並限制超大檔案，避免壓縮產物製造雜訊。
- 🤖 **代理上下文產生**：一鍵產出 `AGENTS.md` / `CLAUDE.md` / `.cursorrules` / Markdown 策略區塊，內含給 AI 代理的 5 條明確指示與 ALLOW / REVIEW / DENY 三張清單。
- ♻️ **冪等寫入**：`<!-- baselineguard:begin -->` … `<!-- baselineguard:end -->` 標記區塊，重複執行只替換標記內內容，手寫段落原樣保留。
- 📊 **三種報告格式**：終端友善的 `text`、機器可讀的 `json`、適合貼 PR 的 `markdown`。
- 🚪 **CI 就緒**：`--fail-on error|warning|none` 控制結束碼（0 / 1），參數錯誤回傳 2；可寫入 `$GITHUB_STEP_SUMMARY`。
- 🧩 **自訂規則集**：`--rules` 支援 `replace`（完全取代）與 `extend`（覆寫單條 + 新增），附 `rules validate` 預先校驗。
- 🌍 **跨平台**：Windows / macOS / Linux 通用，Python 3.9+，無編譯器、無 wheel、無網路、無環境變數陷阱。
- 📦 **單檔散佈**：`scripts/build.sh` 以標準庫 `zipapp` 產出 `dist/baselineguard.pyz`，複製到任何機器用 `python3 baselineguard.pyz` 即可執行。

---

## 🚀 快速開始

**環境需求：** Python **3.9+**（CI 已涵蓋 3.9 / 3.10 / 3.11 / 3.12 / 3.13）、任意作業系統、**零第三方依賴**、**無需連網**。

```bash
# 方式 A：零安裝，克隆即用（建議先試）
git clone https://github.com/gitstq/BaselineGuard.git
cd BaselineGuard
PYTHONPATH=src python3 -m baselineguard --version
PYTHONPATH=src python3 -m baselineguard scan . --baseline widely

# 方式 B：安裝成全域指令
python3 -m pip install -e .
baselineguard scan ./src --format markdown

# 方式 C：打包成單檔，隨處執行
bash scripts/build.sh
python3 dist/baselineguard.pyz scan ./src
```

**三條最常用的指令（可直接複製）：**

```bash
# 1) 掃描並把報告寫入檔案（CI 最常用）
baselineguard scan ./src --baseline 2021 --format json --fail-on error -o report.json

# 2) 產生給 AI 編碼代理的策略檔
baselineguard context --baseline 2023 --format agents-md --out AGENTS.md

# 3) 檢查自訂規則集是否合法
baselineguard rules validate examples/custom-rules.json
```

**驗證安裝：**

```bash
bash scripts/test.sh     # 67 項單元測試
bash scripts/demo.sh     # 60 秒可重現展示
```

> 💡 Windows PowerShell 請用 `$env:PYTHONPATH="src"; python -m baselineguard scan .`；zipapp 則為 `python dist\baselineguard.pyz scan .`。

---

## 📖 詳細使用指南

### 4.1 `scan` —— 掃描與判定

```bash
baselineguard scan PATH [選項]
```

| 參數 | 預設值 | 說明 |
| --- | --- | --- |
| `PATH` | `.` | 單一檔案或目錄 |
| `--baseline` | `widely` | 目標基準：`2018`…`2025` 等年份，或預設 `widely`(2021) / `newly`(2024) / `limited`(9999) |
| `--format` | `text` | `text` / `json` / `markdown` |
| `--fail-on` | `error` | `error`（僅違規阻斷）/ `warning`（警告也阻斷）/ `none`（永不阻斷） |
| `--allow-newly` | 關閉 | 將 `newly` 降為 `info` |
| `--allow-limited` | 關閉 | 將 `limited` 從 `error` 降為 `warning` |
| `--rules FILE` | 內建 | 自訂規則集 JSON |
| `--include GLOB` / `--exclude GLOB` | 無 | 相對路徑 glob，可重複 |
| `--include-docs` | 關閉 | 一併掃描 `.md` / `.mdx` |
| `--no-ignore` | 關閉 | 不略過 `node_modules` / `dist` / `.git` 等 |
| `-o, --output FILE` | stdout | 寫入檔案 |
| `--quiet` | 關閉 | 靜默（仍寫入 `--output`） |

**判定規則（重要，避免誤解）：**

| 規則狀態 | 預設嚴重度 | 說明 |
| --- | --- | --- |
| `widely`，年份 ≤ 目標年份 | `info` | 在承諾基準內，允許使用 |
| `widely`，年份 > 目標年份 | `warning` | 廣泛可用的時間晚於專案承諾 |
| `newly` | `warning` | 尚未進入 Widely Baseline；**提高年份不會自動放行**，須明確 `--allow-newly` |
| `limited` | `error` | 四大引擎未全部支援；`--allow-limited` 可降為 `warning` |
| `deprecated` | `error` | 永遠禁止，無任何開關可放寬 |

> 🧠 設計取捨：年份只作用於 `widely`，風險等級由獨立開關控制。因為「2023 年新近可用」與「2023 年已廣泛可用」是**性質不同**的兩件事，用同一個數字放行會掩蓋風險。

**展示輸出（執行 `bash scripts/demo.sh` 即可重現；📷 截圖 / 🎞️ 展示動圖位置預留於此）：**

```text
BaselineGuard 1.0.0 | offline Web platform Baseline guard
Target : widely (widely <= 2021) | allow-newly=false allow-limited=false fail-on=none
Ruleset: baselineguard-default-ruleset 1.0.0 (41 rules, builtin)
Scan   : 3 files / 57 lines in 1 ms | root=tests/fixtures

[X] ERROR   - violations that break the policy (3)
  [html-marquee] <marquee>  (deprecated)
    sample.html:11:3  <marquee behavior="scroll">legacy ticker</marquee>
    why      : Deprecated or removed Web feature; must not appear in new code.
    action   : Replace with CSS animations (transform / @keyframes).

Result : FAILED  (error=3, warning=8, info=15, total=26)  exit=1
```

### 4.2 `context` —— 產生 AI 編碼代理策略

```bash
baselineguard context --baseline 2023 --format agents-md --out AGENTS.md
baselineguard context --format claude-md --out CLAUDE.md
baselineguard context --format cursorrules --out .cursorrules
baselineguard context --format markdown --stdout   # 只預覽，不寫檔
```

| `--format` | 預設輸出 | 標記語法 |
| --- | --- | --- |
| `agents-md` | `AGENTS.md` | HTML 註解標記 |
| `claude-md` | `CLAUDE.md` | HTML 註解標記 |
| `cursorrules` | `.cursorrules` | `# baselineguard:begin/end`，純文字無表格 |
| `markdown` | `WEB_BASELINE_POLICY.md` | HTML 註解標記 |

產生區塊含：**5 條給代理的明確指示**（生成前先查清單、禁止 DENY 項、REVIEW 項需人工核准且必須寫降級方案、不要為了「更新」而重寫可用程式碼、檢查新依賴是否偷帶新特性）以及 ALLOW / REVIEW / DENY 三張附 MDN 連結的清單。

**冪等性範例**（第二次執行只更新標記區塊，狀態為 `unchanged` / `updated`）：

```bash
baselineguard context --out AGENTS.md
# context created: AGENTS.md (allow/review/deny policy for 41 rules, baseline widely)
baselineguard context --out AGENTS.md
# context unchanged: AGENTS.md (...)
```

### 4.3 `rules` —— 規則集管理

```bash
baselineguard rules list --status newly
baselineguard rules list --format json
baselineguard rules show css-has
baselineguard rules validate examples/custom-rules.json
baselineguard rules list --rules examples/custom-rules.json
```

自訂規則集範例（`mode: extend` = 覆寫內建 `css-nesting` + 新增一條私有規則）：

```json
{
  "mode": "extend",
  "rules": [
    {
      "id": "project-legacy-widget",
      "name": "Legacy jQuery widget bootstrap",
      "category": "script",
      "status": "deprecated",
      "baseline_year": null,
      "applies_to": ["script"],
      "patterns": ["legacyWidget\\.init\\s*\\("],
      "suggestion": "Migrate to the Web Component in src/components/.",
      "reference": "https://example.com/internal/migration-guide"
    }
  ]
}
```

完整欄位說明見 [examples/README.md](examples/README.md)。九個欄位缺一不可，`patterns` 為 Python `re` 正則（JSON 中反斜線要雙寫），`validate` 會檢查狀態列舉、正則合法性、ID 唯一性與重複。

### 4.4 整合進 CI（可直接複製）

```yaml
# .github/workflows/baseline.yml
name: Web Baseline gate
on: [push, pull_request]
jobs:
  gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - name: Install (no third-party runtime deps)
        run: python3 -m pip install -e .
      - name: Baseline gate
        run: |
          baselineguard scan ./src --baseline 2021 --fail-on warning \
            --format markdown >> "$GITHUB_STEP_SUMMARY"
      - name: Machine-readable report
        if: always()
        run: baselineguard scan ./src --format json --fail-on none -o report.json
```

**結束碼約定：** `0` = 通過（或 `--fail-on none`），`1` = 命中阻斷等級，`2` = 參數 / 路徑 / 規則集錯誤。`--fail-on none` 搭配 `--format json -o` 適合「只收集、不阻斷」的觀測情境。

### 4.5 典型使用情境

| 情境 | 指令 |
| --- | --- |
| 🏗️ 新專案立項，鎖定保守基準 | `baselineguard context --baseline widely --out AGENTS.md` |
| 🔍 舊碼健檢，找出淘汰標籤 | `baselineguard scan . --format markdown --fail-on none` |
| 🚦 PR 關卡，禁止 `limited` 特性 | `baselineguard scan ./src --fail-on error` |
| 🤖 投放策略給 Claude / Cursor / Codex | `baselineguard context --format claude-md --out CLAUDE.md` |
| 🧩 團隊私有規範 | `baselineguard scan . --rules team-rules.json` |
| 📈 基準升級評估 | 比較 `--baseline 2021` 與 `--baseline 2024` 的 `warning` 數量 |

### 4.6 ❓ 常見問題

<details>
<summary><b>會誤報嗎？如何抑制？</b></summary>

註解已被遮罩，但**字串常值內的文字仍可能命中**（例如文件字串寫了 `document.write`）。可用 `--exclude 'docs/**'` 排除，或在自訂規則集中把 `patterns` 寫得更具體。偵測目標是「特性是否出現」這個訊號，而非完整語意解析。
</details>

<details>
<summary><b>和 caniuse / browserslist / Babel 有何不同？</b></summary>

那些解決「執行期 / 建置期相容性資料與轉譯」；BaselineGuard 解決「**策略治理**」：把團隊承諾的基準寫進版本庫、讓 AI 代理在寫程式前就讀到、並在 CI 對原始碼設關卡。兩者互補，不衝突。
</details>

<details>
<summary><b>需要連網嗎？會讀取我的金鑰或環境變數嗎？</b></summary>

完全不連網，不讀取任何環境變數、不讀取 `.env`、不發出任何 HTTP 請求。規則集隨套件散佈（zipapp 內亦可讀），掃描只存取你明確指定的路徑。
</details>

<details>
<summary><b>為何用正則而非 AST？</b></summary>

零依賴是硬約束，且需同時處理混合 HTML / CSS / JS 的 `.vue` / `.svelte` / `.astro`。正則足以辨識「特性出現」這個訊號，掃描 57 行僅 1 ms；未來若需精確語意，可做成選用外掛而不污染零依賴核心。
</details>

<details>
<summary><b>規則裡的年份權威嗎？</b></summary>

`baseline_year` 是一份**可維護的社群快照**，用於策略裁剪，不是權威相容性宣告，也不取代實機測試。團隊可用 `--rules` 覆寫；規則集自帶 `version`，升級會記錄於 CHANGELOG。
</details>

<details>
<summary><b>支援哪些檔案？</b></summary>

`.css/.scss/.less`、`.html/.htm/.vue/.svelte/.astro`、`.js/.mjs/.cjs/.jsx/.ts/.tsx/.mts/.cts`；`.md/.mdx` 需 `--include-docs`。`.vue` 等單檔元件會同時按 markup + css + script 三類偵測。
</details>

---

## 💡 設計思路與迭代規劃

**設計理念**

1. **策略即程式碼**：把「我們相容到哪一年」從口頭約定變成 `--baseline` 參數與可提交的 `AGENTS.md`，Code Review 有據可依。
2. **約束前移**：與其事後 review AI 產生的程式碼，不如在生成前就把 ALLOW / REVIEW / DENY 清單交給代理 —— 這是本專案相對於「靜態最佳實踐文件」最核心的差異化。
3. **零依賴優先**：只用標準庫（`argparse` / `re` / `pathlib` / `dataclasses` / `unittest` / `zipapp` / `importlib.resources`），換來「內網可用、無供應鏈風險、無版本地獄、跨平台零編譯」。
4. **可解釋勝過智慧**：規則、狀態、年份、建議、MDN 連結全部顯式可讀；每條 finding 都帶 `why` 與 `action`，不輸出黑盒分數。

**技術選型**

| 選擇 | 原因 |
| --- | --- |
| Python 3.9+ 標準庫 | 跨平台、CI 映像內建、無第三方依賴 |
| 規則集用 JSON 而非程式碼 | 可版本化、可 `validate`、可被其他工具取用、非開發者也能維護 |
| `dataclass(frozen=True)` | 規則 / 策略 / finding 不可變，測試確定性高 |
| `zipapp` | 標準庫內建，產出單檔 `.pyz`，無 wheel 無編譯 |
| `importlib.resources` | 規則集在原始碼樹、安裝套件、zipapp 三種形態都能讀取 |

**🗺️ 迭代路線圖**

- **v1.1**：規則集擴充至 80+；規則集附 SHA-256 自校驗，方便團隊鎖定版本。
- **v1.2**：新增 SARIF 輸出，接入 GitHub Code Scanning 的行級註解。
- **v1.3**：提供 `--explain <rule-id>` 與離線規則集 diff 報告（比較兩個基準版本）。
- **v2.0**：可選 AST 外掛介面（核心仍零依賴）；更多代理格式支援。

**社群貢獻方向**：補充規則、修正年份、新增 README 語言版本、更多 CI 平台範例（GitLab CI / Jenkins / 騰訊工蜂），以及針對框架樣板的誤報優化。

---

## 📦 打包與部署指南

> 依專案分類規則，BaselineGuard 屬**工具庫 / CLI 類**，因此**不提供 Windows / macOS / Linux 執行檔與 Release 附件**，也不做跨平台可執行打包 —— 純 Python 本身即跨平台，避免「上傳無法執行的產物」的風險。安裝與整合步驟見上文「快速開始」與「CI 整合」。

| 散佈方式 | 指令 | 適用情境 |
| --- | --- | --- |
| 🟢 原始碼零安裝 | `PYTHONPATH=src python3 -m baselineguard ...` | 內網、臨時掃描、CI 免安裝 |
| 🔵 可編輯安裝 | `python3 -m pip install -e .` | 本機開發、取得 `baselineguard` 指令 |
| 🟣 單檔 zipapp | `bash scripts/build.sh` → `dist/baselineguard.pyz` | 複製散佈、離線機器、無 pip 環境 |
| ⚪ 發佈至 PyPI（維護者選用） | `python3 -m build && python3 -m twine upload dist/*` | 僅發佈者需要 `build`/`twine`，**非執行期依賴** |

**相容環境矩陣**

| 項目 | 支援範圍 |
| --- | --- |
| Python | 3.9 / 3.10 / 3.11 / 3.12 / 3.13（CI 矩陣驗證） |
| 作業系統 | Windows / macOS / Linux（含 WSL、Git Bash） |
| 執行期第三方依賴 | **無** |
| 網路 | **不需要**（掃描與上下文產生全程離線） |
| 最小權限 | 僅需讀取待掃描目錄、寫入 `--output` / `--out` 指定檔案 |
| 建置需求 | Python 3.9+ 與 bash（Windows 可用 Git Bash / WSL） |

**部署檢查清單**：`bash scripts/test.sh` → `bash scripts/build.sh` → `python3 dist/baselineguard.pyz rules validate src/baselineguard/data/rules.json` → 在目標機器跑一次 `scan --format json --fail-on none`。

**注意事項**

- `.gitignore` 已排除 `.env`、`*.secret`、建置產物與生成報告，避免誤提交憑據。
- `--no-ignore` 會掃描 `node_modules`，通常很慢且雜訊多，僅供疑難排解。
- 單檔超過 2 MB 會被略過（多為壓縮產物），可用 `--include` 精確指定。
- 策略變更請同步更新 `AGENTS.md` 並於 PR 說明，避免代理仍按舊清單生成程式碼。

---

## 🤝 貢獻指南

歡迎提交 Issue 與 PR！請先閱讀 [CONTRIBUTING.md](CONTRIBUTING.md)。

**三條硬性約定**：① 不得引入任何執行期第三方依賴；② 不得在掃描期發出網路請求；③ 程式碼與規則資料必須原創，不得複製其他專案實作。

```bash
git clone https://github.com/gitstq/BaselineGuard.git
cd BaselineGuard
bash scripts/test.sh    # 提交前必須通過
bash scripts/demo.sh    # 重現展示
```

**提交訊息遵循 Angular 規範**：`feat:` / `fix:` / `docs:` / `test:` / `refactor:` / `chore:`，例如 `feat: detect CSS anchor positioning`。

**PR 要求**：一個 PR 只做一件事；附上測試輸出；若改動使用者可見行為，必須同步更新本 README 的**三個語言版本**；不要提交生成報告、`dist/*.pyz` 或任何憑據檔案。

**Issue 請附**：完整指令、`--format json` 報告、Python 版本、作業系統，以及可重現的最小原始碼片段。

---

## 📄 開源協議說明

本專案採用 **MIT License** —— Copyright (c) 2026 gitstq。詳見 [LICENSE](LICENSE)：可自由使用、複製、修改、合併、發佈、散佈、再授權與商用，只需保留版權與授權聲明；軟體依「現狀」提供，不含任何擔保。

規則集中的 `reference` 欄位僅指向 MDN 等公開文件供查閱，**不包含任何從第三方複製的程式碼或文件內容**；規則的模式、分級與建議文案皆為本專案獨立撰寫。內建規則集 `baselineguard-default-ruleset 1.0.0` 同樣依 MIT 提供。

---
---

<a id="en"></a>

# English

## 🎉 Introduction

**BaselineGuard** is a **zero-dependency, standard-library-only, fully offline** CLI tool. It scans your HTML / CSS / JavaScript sources, identifies the Web platform features in use, and decides — against a declared *Baseline* policy — which are allowed, which need a human decision, and which must be removed. It also **generates policy context for AI coding agents** (`AGENTS.md` / `CLAUDE.md` / `.cursorrules`), so the agent is constrained *before* it writes a single line.

**The pain it addresses:**

| Problem | Status quo | What BaselineGuard does |
| --- | --- | --- |
| 🤖 Agents are outdated *or* too bleeding-edge | They emit deprecated `<center>` tags, or casually reach for View Transitions | Ships ALLOW / REVIEW / DENY lists into the agent context up front |
| 📄 Best-practice docs can be read, not enforced | Docs never make it into CI; nobody checks compliance | One command becomes a CI gate with meaningful exit codes |
| 🌐 Compatibility lookups need the network | Build-time fetches, broken in air-gapped environments, unstable results | The rule set ships inside the package; scanning makes zero network calls |
| 🧩 Every team has an unwritten baseline | "Which year do we support?" is folklore | `--baseline 2021` turns the agreement into a versioned policy file |

**What makes it different:** unlike a static knowledge base or a guidance document, BaselineGuard is an **executable policy engine plus an agent-context generator**. Rules carry year semantics so they can be cropped to a target baseline; context insertion uses **idempotent marker blocks**, so re-running only refreshes the machine-generated region and never overwrites hand-written content; reports come in `text`, `json` and `markdown` for terminals, tools and pull requests respectively.

**Inspiration:** this project references the *product idea and user pain* behind [GoogleChrome/modern-web-guidance-src](https://github.com/GoogleChrome/modern-web-guidance-src) — "*Keep your coding agent up to date with the latest web best practices*" — which was the fastest-growing repository on GitHub Trending daily on 2026-11-15. **No code or documentation was copied from that project.** The rule data, detection engine, policy model, context generator and all engineering work here are 100% independently developed and released under MIT.

> 📌 BaselineGuard is a **plugin / script / library / CLI** project. Per the release policy it ships **no platform binaries and no Release assets**; complete installation and integration instructions live in this README instead.

---

## ✨ Features

- 📚 **41 built-in rules** across CSS, HTML, JS and Web APIs, in four statuses: `widely`, `newly`, `limited`, `deprecated`.
- 🚦 **Two-axis policy**: `--baseline 2021` crops `widely` rules by year, while `--allow-newly` / `--allow-limited` control risk levels independently. Years and risk are deliberately *not* conflated, so every verdict is explainable and testable.
- 🔍 **Comment-masked detection**: `/* */`, `<!-- -->` and whole-line `//` comments are blanked before matching **without changing length or newlines**, so reported line/column numbers match the source exactly; URLs such as `https://` are never damaged.
- 🧹 Same-rule/same-line deduplication, automatic skipping of `node_modules` / `dist` / `.git` and a size cap on generated bundles keep the signal clean.
- 🤖 **Agent context generation**: emits `AGENTS.md`, `CLAUDE.md`, `.cursorrules` or plain Markdown with five explicit instructions and ALLOW / REVIEW / DENY tables.
- ♻️ **Idempotent writes**: `<!-- baselineguard:begin -->` … `<!-- baselineguard:end -->` — repeated runs replace only the marked block and preserve everything you wrote around it.
- 📊 Three report formats plus a `--quiet` / `-o` combination suitable for CI artefacts.
- 🚪 **CI-ready**: `--fail-on error|warning|none` controls the exit code (0 / 1); usage errors return 2; Markdown can be appended to `$GITHUB_STEP_SUMMARY`.
- 🧩 **Custom rule sets**: `--rules` with `replace` or `extend` mode, plus `rules validate` for pre-flight checks.
- 🌍 **Cross-platform**: Windows / macOS / Linux, Python 3.9+, no compiler, no wheels, no network, no env-var traps.
- 📦 **Single-file distribution**: `scripts/build.sh` uses the standard-library `zipapp` module to produce `dist/baselineguard.pyz` — copy it anywhere and run `python3 baselineguard.pyz`.

---

## 🚀 Quick Start

**Requirements:** Python **3.9+** (CI covers 3.9 / 3.10 / 3.11 / 3.12 / 3.13), any OS, **zero third-party dependencies**, **no network access needed**.

```bash
# Option A: no install at all (best for a first try)
git clone https://github.com/gitstq/BaselineGuard.git
cd BaselineGuard
PYTHONPATH=src python3 -m baselineguard --version
PYTHONPATH=src python3 -m baselineguard scan . --baseline widely

# Option B: install as a command
python3 -m pip install -e .
baselineguard scan ./src --format markdown

# Option C: build a single file and run it anywhere
bash scripts/build.sh
python3 dist/baselineguard.pyz scan ./src
```

**The three commands you will use most (copy-paste ready):**

```bash
# 1) Scan and write a report (the CI workhorse)
baselineguard scan ./src --baseline 2021 --format json --fail-on error -o report.json

# 2) Generate policy context for AI coding agents
baselineguard context --baseline 2023 --format agents-md --out AGENTS.md

# 3) Validate a custom rule set
baselineguard rules validate examples/custom-rules.json
```

**Verify your setup:**

```bash
bash scripts/test.sh     # 67 unit tests
bash scripts/demo.sh     # reproducible 60-second demo
```

> 💡 On Windows PowerShell use `$env:PYTHONPATH="src"; python -m baselineguard scan .`; for the zipapp use `python dist\baselineguard.pyz scan .`.

---

## 📖 Detailed Usage

### 4.1 `scan` — detect and judge

```bash
baselineguard scan PATH [options]
```

| Option | Default | Meaning |
| --- | --- | --- |
| `PATH` | `.` | A file or a directory |
| `--baseline` | `widely` | A year (`2018`…`2025`) or preset `widely`(2021) / `newly`(2024) / `limited`(9999) |
| `--format` | `text` | `text` / `json` / `markdown` |
| `--fail-on` | `error` | `error` (block on violations) / `warning` (also block on warnings) / `none` |
| `--allow-newly` | off | Downgrade `newly` to `info` |
| `--allow-limited` | off | Downgrade `limited` from `error` to `warning` |
| `--rules FILE` | built-in | Custom rule-set JSON |
| `--include GLOB` / `--exclude GLOB` | none | Relative-path globs, repeatable |
| `--include-docs` | off | Also scan `.md` / `.mdx` |
| `--no-ignore` | off | Do not skip `node_modules` / `dist` / `.git` etc. |
| `-o, --output FILE` | stdout | Write to a file |
| `--quiet` | off | Suppress stdout (still honours `--output`) |

**Verdict rules (read this — it avoids surprises):**

| Rule status | Default severity | Meaning |
| --- | --- | --- |
| `widely`, year ≤ target | `info` | Inside the promised baseline; allowed |
| `widely`, year > target | `warning` | Became widely available after the project's commitment |
| `newly` | `warning` | Not yet Widely Baseline; **raising the year does not auto-allow it** — use `--allow-newly` |
| `limited` | `error` | Not supported in all four major engines; `--allow-limited` downgrades to `warning` |
| `deprecated` | `error` | Always forbidden; no flag can relax it |

> 🧠 Design choice: the year applies only to `widely`; risk levels have their own switches. "Newly available in 2023" and "widely available in 2023" are **different kinds of facts**, and letting one number authorise both would hide real risk.

**Sample output** (run `bash scripts/demo.sh` to reproduce; 📷 screenshot / 🎞️ demo GIF placeholder):

```text
BaselineGuard 1.0.0 | offline Web platform Baseline guard
Target : widely (widely <= 2021) | allow-newly=false allow-limited=false fail-on=none
Ruleset: baselineguard-default-ruleset 1.0.0 (41 rules, builtin)
Scan   : 3 files / 57 lines in 1 ms | root=tests/fixtures

[X] ERROR   - violations that break the policy (3)
  [html-marquee] <marquee>  (deprecated)
    sample.html:11:3  <marquee behavior="scroll">legacy ticker</marquee>
    why      : Deprecated or removed Web feature; must not appear in new code.
    action   : Replace with CSS animations (transform / @keyframes).
  [css-view-transitions] CSS View Transitions  (limited)
    sample.css:16:3  view-transition-name: hero;
    action   : Not available in all major engines. Always wrap with @supports ...

Result : FAILED  (error=3, warning=8, info=15, total=26)  exit=1
```

### 4.2 `context` — generate agent policy

```bash
baselineguard context --baseline 2023 --format agents-md --out AGENTS.md
baselineguard context --format claude-md --out CLAUDE.md
baselineguard context --format cursorrules --out .cursorrules
baselineguard context --format markdown --stdout   # preview only
```

| `--format` | Default output | Marker syntax |
| --- | --- | --- |
| `agents-md` | `AGENTS.md` | HTML comment markers |
| `claude-md` | `CLAUDE.md` | HTML comment markers |
| `cursorrules` | `.cursorrules` | `# baselineguard:begin/end`, plain text, no tables |
| `markdown` | `WEB_BASELINE_POLICY.md` | HTML comment markers |

The generated block contains **five explicit instructions for the agent** (consult the lists before writing, never introduce a DENY feature, REVIEW features need human approval *and* a documented fallback, do not rewrite working code merely to "modernise" it, and check that new dependencies do not smuggle in out-of-policy features) plus ALLOW / REVIEW / DENY tables with MDN links.

**Idempotency** (the second run only refreshes the marked block):

```bash
baselineguard context --out AGENTS.md
# context created: AGENTS.md (allow/review/deny policy for 41 rules, baseline widely)
baselineguard context --out AGENTS.md
# context unchanged: AGENTS.md (...)
```

### 4.3 `rules` — manage rule sets

```bash
baselineguard rules list --status newly
baselineguard rules list --format json
baselineguard rules show css-has
baselineguard rules validate examples/custom-rules.json
baselineguard rules list --rules examples/custom-rules.json
```

A custom rule set (`mode: extend` overrides built-in `css-nesting` and adds a private rule):

```json
{
  "mode": "extend",
  "rules": [
    {
      "id": "project-legacy-widget",
      "name": "Legacy jQuery widget bootstrap",
      "category": "script",
      "status": "deprecated",
      "baseline_year": null,
      "applies_to": ["script"],
      "patterns": ["legacyWidget\\.init\\s*\\("],
      "suggestion": "Migrate to the Web Component in src/components/.",
      "reference": "https://example.com/internal/migration-guide"
    }
  ]
}
```

See [examples/README.md](examples/README.md) for all nine required fields. `patterns` are Python `re` regexes (escape backslashes in JSON); `validate` checks status enums, regex validity, unique IDs and duplicates.

### 4.4 CI integration (copy-paste ready)

```yaml
# .github/workflows/baseline.yml
name: Web Baseline gate
on: [push, pull_request]
jobs:
  gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - name: Install (no third-party runtime deps)
        run: python3 -m pip install -e .
      - name: Baseline gate
        run: |
          baselineguard scan ./src --baseline 2021 --fail-on warning \
            --format markdown >> "$GITHUB_STEP_SUMMARY"
      - name: Machine-readable report
        if: always()
        run: baselineguard scan ./src --format json --fail-on none -o report.json
```

**Exit codes:** `0` = passed (or `--fail-on none`), `1` = blocking findings, `2` = bad arguments / path / rule set. Use `--fail-on none --format json -o` for observe-only collection.

### 4.5 Typical scenarios

| Scenario | Command |
| --- | --- |
| 🏗️ New project, lock a conservative baseline | `baselineguard context --baseline widely --out AGENTS.md` |
| 🔍 Audit legacy code for deprecated tags | `baselineguard scan . --format markdown --fail-on none` |
| 🚦 PR gate against `limited` features | `baselineguard scan ./src --fail-on error` |
| 🤖 Feed policy to Claude / Cursor / Codex | `baselineguard context --format claude-md --out CLAUDE.md` |
| 🧩 Team-private conventions | `baselineguard scan . --rules team-rules.json` |
| 📈 Evaluate a baseline upgrade | Compare `warning` counts for `--baseline 2021` vs `--baseline 2024` |

### 4.6 ❓ FAQ

<details>
<summary><b>Does it produce false positives? How do I suppress them?</b></summary>

Comments are masked, but **text inside string literals can still match** (e.g. a doc string mentioning `document.write`). Exclude those paths with `--exclude 'docs/**'`, or make the rule's `patterns` more specific. The detector targets the signal "this feature appears", not full semantic parsing.
</details>

<details>
<summary><b>How is this different from caniuse / browserslist / Babel?</b></summary>

Those solve runtime/build-time compatibility *data and transpilation*. BaselineGuard solves **policy governance**: commit the team's promise to the repo, let the AI agent read it *before* generating code, and gate source code in CI. They are complementary, not competing.
</details>

<details>
<summary><b>Does it need the network? Does it read my secrets or env vars?</b></summary>

No network at all. It reads no environment variables, no `.env` files, and makes no HTTP requests. The rule set is bundled (readable inside a zipapp too); scanning only touches the path you explicitly pass.
</details>

<details>
<summary><b>Why regexes instead of an AST?</b></summary>

Zero dependencies is a hard constraint, and the tool must handle `.vue` / `.svelte` / `.astro` files that mix HTML, CSS and JS. Regexes are sufficient for the "feature appeared" signal — 57 lines scan in 1 ms. If precise semantics are ever needed, an optional AST plugin can be added without polluting the dependency-free core.
</details>

<details>
<summary><b>Are the baseline years authoritative?</b></summary>

`baseline_year` is a **maintainable community snapshot** used for policy cropping, not an authoritative compatibility claim and not a substitute for real-device testing. Override it with `--rules`; the rule set carries its own `version` and changes are recorded in CHANGELOG.
</details>

<details>
<summary><b>Which files are supported?</b></summary>

`.css/.scss/.less`, `.html/.htm/.vue/.svelte/.astro`, `.js/.mjs/.cjs/.jsx/.ts/.tsx/.mts/.cts`; `.md/.mdx` requires `--include-docs`. Single-file components are checked against markup + css + script categories simultaneously.
</details>

---

## 💡 Design & Roadmap

**Design principles**

1. **Policy as code.** Turn "which year do we support?" from folklore into a `--baseline` flag and a committed `AGENTS.md`, so reviews have something concrete to point at.
2. **Shift the constraint left.** Rather than reviewing AI-generated code after the fact, hand the agent ALLOW / REVIEW / DENY lists *before* it writes. This is the core difference from a static best-practice document.
3. **Zero dependencies first.** Standard library only (`argparse`, `re`, `pathlib`, `dataclasses`, `unittest`, `zipapp`, `importlib.resources`) buys air-gapped usability, no supply-chain surface, no version hell and no cross-platform compilation.
4. **Explainable beats clever.** Rules, statuses, years, guidance and MDN links are all explicit; every finding carries a `why` and an `action`, never a black-box score.

**Technology choices**

| Choice | Why |
| --- | --- |
| Python 3.9+ stdlib | Cross-platform, preinstalled in CI images, zero third-party deps |
| JSON rule set, not code | Versionable, validatable, consumable by other tools, editable by non-developers |
| `dataclass(frozen=True)` | Immutable rules / policies / findings make tests deterministic |
| `zipapp` | Built into the stdlib; produces a single `.pyz` with no wheels and no compiler |
| `importlib.resources` | The rule set loads from the source tree, an installed package and a zipapp alike |

**🗺️ Roadmap**

- **v1.1**: grow the rule set to 80+; add SHA-256 rule-set pinning for teams.
- **v1.2**: SARIF output for GitHub Code Scanning line annotations.
- **v1.3**: `--explain <rule-id>` and an offline rule-set diff between two baselines.
- **v2.0**: optional AST plugin interface (core stays dependency-free) and more agent formats.

**Where to contribute**: new rules, year corrections, additional README languages, CI examples for other platforms (GitLab CI, Jenkins), and false-positive tuning for framework templates.

---

## 📦 Packaging & Deployment

> Per the project classification rules, BaselineGuard is a **library / CLI tool**, so it ships **no Windows / macOS / Linux binaries and no Release assets** and does not attempt cross-platform executable packaging — pure Python is already cross-platform, which avoids the risk of publishing artefacts that cannot run. Installation and integration are documented above.

| Distribution | Command | Best for |
| --- | --- | --- |
| 🟢 Source, no install | `PYTHONPATH=src python3 -m baselineguard ...` | Air-gapped networks, one-off scans, install-free CI |
| 🔵 Editable install | `python3 -m pip install -e .` | Local development, getting the `baselineguard` command |
| 🟣 Single-file zipapp | `bash scripts/build.sh` → `dist/baselineguard.pyz` | Copy-and-run, offline machines, no pip available |
| ⚪ Publish to PyPI (maintainers only) | `python3 -m build && python3 -m twine upload dist/*` | Only publishers need `build`/`twine` — **not a runtime dependency** |

**Compatibility matrix**

| Item | Supported |
| --- | --- |
| Python | 3.9 / 3.10 / 3.11 / 3.12 / 3.13 (CI matrix) |
| OS | Windows / macOS / Linux (including WSL and Git Bash) |
| Runtime third-party deps | **None** |
| Network | **Not required** (scanning and context generation are fully offline) |
| Least privilege | Read the target directory; write only to `--output` / `--out` |
| Build requirements | Python 3.9+ and bash (Git Bash / WSL on Windows) |

**Deployment checklist**: `bash scripts/test.sh` → `bash scripts/build.sh` → `python3 dist/baselineguard.pyz rules validate src/baselineguard/data/rules.json` → run one `scan --format json --fail-on none` on the target machine.

**Caveats**

- `.gitignore` excludes `.env`, `*.secret`, build artefacts and generated reports so credentials are never committed by accident.
- `--no-ignore` scans `node_modules`: slow and noisy, use only when debugging.
- Files over 2 MB are skipped (usually minified bundles); use `--include` to target them explicitly.
- When the policy changes, regenerate `AGENTS.md` and mention it in the PR so agents do not keep following a stale list.

---

## 🤝 Contributing

Issues and PRs are welcome — please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

**Three hard rules**: ① no third-party runtime dependencies; ② no network calls during scanning; ③ code and rule data must be original, never copied from another project.

```bash
git clone https://github.com/gitstq/BaselineGuard.git
cd BaselineGuard
bash scripts/test.sh    # must pass before submitting
bash scripts/demo.sh    # reproduce the demo
```

**Commit messages follow the Angular convention**: `feat:` / `fix:` / `docs:` / `test:` / `refactor:` / `chore:`, e.g. `feat: detect CSS anchor positioning`.

**PR checklist**: one concern per PR; include the test output; if user-visible behaviour changes, update **all three language sections** of this README; never commit generated reports, `dist/*.pyz` or credentials.

**For issues, please include**: the full command, a `--format json` report, Python version, OS, and a minimal source snippet that reproduces the finding.

---

## 📄 License

Released under the **MIT License** — Copyright (c) 2026 gitstq. See [LICENSE](LICENSE): you may use, copy, modify, merge, publish, distribute, sublicense and sell copies, provided the copyright and permission notices are retained; the software is provided "as is", without warranty of any kind.

The `reference` fields in the rule set merely point to public documentation such as MDN; **no code or documentation was copied from third parties**. Patterns, classifications and guidance text are written independently for this project. The built-in `baselineguard-default-ruleset 1.0.0` is provided under MIT as well.
