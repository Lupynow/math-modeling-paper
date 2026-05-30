# Math Modeling Skills

> 数学建模竞赛完整工具链：从拿到赛题到交出论文，一条龙解决。

覆盖 **国赛 CUMCM（A/B/C）** 和 **美赛 MCM/ICM（A-F）** 全部题型。

规则和模板基于 **150+ 篇获奖论文**（国赛一等 + 美赛 O/F 奖，2018-2025）的系统分析提炼。

---

## 两个 Skill

### `math-modeling-solver` — 解题

拿到题目不知道怎么下手？solver 帮你五步走到代码。

| 功能 | 能力 |
|------|------|
| 问题拆解 | 自动判定 12 种数学本质类型（预测/优化/机理/网络科学/生态/博弈...），含文献检索关键词生成 |
| 文献检索 | 阶段1.5：拆题后先搜文献，用学术证据支撑模型选择，标注期刊含金量 |
| 模型匹配 | 95+ 场景决策矩阵，每个场景给出首选模型 + 备选 + 边界条件 + 文献支撑 |
| Cookbook | 8 本算法手册（优化/ML/评价/机理/统计/网络/聚类/博弈论） |
| 代码模板 | 22 个 Python + 7 个 MATLAB 可运行模板，含问题适配注释 |
| Playbook | 12 本完整例题走通（国赛 9 + 美赛 3），拆题到代码全流程 |
| 美赛专项 | 模型命名策略、Memo/Letter 框架、Our Work 流程图设计 |

### `math-modeling-paper` — 写作

建模做完了不会写论文？paper 帮你从空白页到排版完成。

| 功能 | 能力 |
|------|------|
| 结构模板 | 国赛/美赛双赛道标准结构 |
| 摘要指导 | 中英双语模板 + 获奖实例 |
| 文献查阅 | 检索策略、期刊含金量分级（SCI Q1-Q4 + 中文核心）、引用格式速查（GB/T 7714/APA/IEEE）、参数溯源 |
| 题型策略 | A/B/C/D/E/F 六题型差异化写作策略 |
| 模型检验 | 灵敏度分析/误差分析/鲁棒性检验方法论 |
| 图表代码 | 六种流程图风格 + 数据图/伪代码规范 + 附录要求 |
| 句式库 | 中英双语学术句式，按章节组织 |
| Memo/Letter | 美赛 B-F 题一页 Memo/Letter 格式模板 |
| 排版检查 | LaTeX/Word 检查清单 |

---

## 安装

### 方式一：`npx skills add`（推荐）

```bash
# 安装全部两个 skill
npx skills add Lupynow/math-modeling-skills --skill '*'

# 或单独安装
npx skills add Lupynow/math-modeling-skills --skill math-modeling-solver
npx skills add Lupynow/math-modeling-skills --skill math-modeling-paper
```

### 方式二：手动安装

```bash
# 1. 克隆到临时目录
git clone https://github.com/Lupynow/math-modeling-skills.git /tmp/math-modeling-skills

# 2. 将 skills/ 下的子目录移到 Claude Code 的 skills 目录
mv /tmp/math-modeling-skills/skills/math-modeling-solver ~/.claude/skills/
mv /tmp/math-modeling-skills/skills/math-modeling-paper ~/.claude/skills/

# 3. 清理
rm -rf /tmp/math-modeling-skills
```

> **为什么不能直接 clone？** Claude Code 只会扫描 `~/.claude/skills/<name>/SKILL.md`（一层目录），仓库的 `skills/` 目录是给 `npx skills` CLI 识别用的。

重启 Claude Code，两个 skill 自动加载。

---

## 工作流

```
拿到赛题
  |
  v
math-modeling-solver
  |-- 阶段1: 拆题分析（12 种问题类型判定 + 检索关键词生成）
  |-- 阶段1.5: 文献检索（搜索类似问题的已有解法，提取方法证据）
  |-- 阶段2: 模型匹配（查决策矩阵 + 文献支撑 + 加载 Cookbook）
  |-- 阶段3: 算法展开 + 代码生成（加载模板填入参数）
  |-- 阶段4: 论文衔接 -> 输出 [PAPER_READY] 草稿片段
  |
  v
math-modeling-paper
  |-- Step 0: 检测 [PAPER_READY] 信号
  |-- Step 1: 确定比赛类型和写作阶段
  |-- Step 2: 加载对应指南（含文献综述写作）
  |-- Step 3: 逐章写作指导
  |
  v
交卷
```

---

## 文件结构

```
math-modeling-skills/
|-- README.md
|-- skills/
    |-- math-modeling-paper/
    |   |-- SKILL.md
    |   |-- references/
    |       |-- abstract-writing.md        (摘要模板 + 获奖实例)
    |       |-- common-phrases.md          (中英学术句式库)
    |       |-- cumcm-guide.md             (国赛各章节写法)
    |       |-- figure-and-code-guide.md   (图表/代码/伪代码规范)
    |       |-- literature-review.md       (文献检索 + 综述写作 + 引用格式)
    |       |-- mcm-icm-guide.md           (美赛各章节写法)
    |       |-- memo-writing.md            (美赛 Memo/Letter)
    |       |-- model-validation.md        (模型检验方法大全)
    |       |-- problem-type-strategies.md (A-F 题型策略)
    |-- math-modeling-solver/
        |-- SKILL.md
        |-- references/
            |-- problem-decomposition.md     (拆题方法论)
            |-- model-selection-matrix.md    (95+ 场景决策矩阵)
            |-- paper-bridge.md              (论文衔接规则)
            |-- mcm-specific-guide.md        (美赛专项指南)
            |-- cookbook-optimization.md     (优化：GA/PSO/SA/LP/DP)
            |-- cookbook-ml.md               (ML：XGBoost/RF/SVM/NN)
            |-- cookbook-evaluation.md       (评价：TOPSIS/AHP/熵权/模糊)
            |-- cookbook-mechanistic.md      (机理：热传导/ODE/几何/光学)
            |-- cookbook-statistical.md      (统计：假设检验/ANOVA/蒙特卡洛)
            |-- cookbook-network.md           (图论：网络流/最短路径/中心性)
            |-- cookbook-clustering.md        (聚类：层次/K-Means/DBSCAN/GMM)
            |-- cookbook-game-theory.md       (博弈：Nash/演化/Stackelberg)
            |-- code-templates/              (29 个可运行模板)
            |-- playbooks/                   (12 本端到端例题)
```

---

## 搭配 Skill

| Skill | 用途 |
|-------|------|
| `nature-figure` | 科研级图表 |
| `nature-polishing` | 美赛英文润色 |
| `xlsx` | 数据清洗分析 |
| `docx` | Word 排版输出 |
| `pdf` | PDF 合并导出 |

---

## License

MIT

---

## 支持

如果这套 skill 对你的竞赛有帮助，欢迎随缘支持一下~

<p align="center">
  <img src="assets/wechat-donate.png" alt="微信赞赏码" width="240">
</p>

---

## 💬 想说的话

项目会长期免费维护，大家正常使用就好。

很多朋友还是学生党，所以完全不需要有任何"必须打赏"的压力。

如果这些内容刚好帮你节省了一些时间、解决了一点问题，
又恰好想请作者喝杯咖啡，那我会非常开心 ☕

你的支持会用于：

- 持续更新内容
- 服务器与工具费用
- 熬夜写文档时的续命奶茶（认真）

无论是否赞赏，都非常感谢你的关注与支持 ❤️

---

## 更新记录

**v1.3.1** (2026-05-27)
- 阶段 1.5 文献检索/综述从可选改为强制，删除「用户可跳过」退路
- `literature-review.md` 升为必读

**v1.3.0** (2026-05-26) — 文献查阅闭环
- 新增 `literature-review.md`：检索策略、期刊分级（SCI Q1-Q4 + 中文核心）、引用格式速查（GB/T 7714 / APA / IEEE）、参数溯源
- 3 本新 Cookbook：网络（图论/网络流/中心性）、聚类（层次/K-Means/DBSCAN/GMM）、博弈论（Nash/演化/Stackelberg）
- 1 本新 Playbook：几何/运动学（板凳龙螺线 + 定日镜光学）
- MATLAB 模板 +2（SA + Monte Carlo），总数 7
- solver 新增阶段 1.5：拆题 → 搜文献 → 证据支撑模型推荐
- 模型推荐输出增加文献证据维度 + 期刊含金量标注

**v1.2.x** (2026-05-25) — 防同质化 + solver 发布
- 模型选择防同质化：候选模型 A/B 替代首选/备选，每子问题至少 2 个候选，新增冲突裁决规则
- 句式库去模板化：从 51 篇获奖论文提取真实句式，每句 3-6 种变体
- 11 个 Playbook 标题改为「解题示例（一种可行路径）」
- 流程图从单一风格扩展为 6 种可选框架
- **`math-modeling-solver` 正式发布**：12 种问题类型判定 + 95+ 场景决策矩阵 + 8 Cookbook + 12 Playbook + 22 Python + 7 MATLAB 模板

**v1.2.0** (2026-05-24)
- 基于 80 篇美赛 2024-2025 O 奖论文系统修订，论文基准升至 150+
- 新增 `memo-writing.md`：美赛 B-F 题一页 Memo/Letter 指导
- 修正：灵敏度 2-4 页 → 1-3 页；参考文献 ≥8 → ≥5；AI Report 强制 → 约 37%
- Our Work 流程图从推荐升级为近乎必须；新增模型命名策略
- D/E/F 题型策略补全

**v1.1.0** (2026-05-24)
- 基于 50+ 篇获奖论文（2018-2024）大幅修订
- 新增 `problem-type-strategies.md`（A/B/C 题型策略）+ `figure-and-code-guide.md`（图表/伪代码规范）
- 修正：摘要 1000 → 500-800 字；模型检验从独立章节 → 嵌入子问题模式；参考文献数下调

**v1.0.0** (2026-05-23)
- `math-modeling-paper` 初始发布，基于 30+ 篇获奖论文
- 覆盖国赛 + 美赛，含结构模板、摘要指南、模型检验、中英句式库

---

## License

MIT
