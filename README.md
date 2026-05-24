# Math Modeling Skills

> 数学建模竞赛完整工具链：从拿到赛题到交出论文，一条龙解决。

覆盖 **国赛 CUMCM（A/B/C）** 和 **美赛 MCM/ICM（A-F）** 全部题型。

规则和模板基于 **96 篇获奖论文**（72 篇国赛一等 + 24 篇美赛 O/F 奖，2018-2025）的系统分析提炼。

---

## 两个 Skill

### `math-modeling-solver` — 解题

拿到题目不知道怎么下手？solver 帮你四步走到代码。

| 功能 | 能力 |
|------|------|
| 问题拆解 | 自动判定 12 种数学本质类型（预测/优化/机理/网络科学/生态...） |
| 模型匹配 | 95+ 场景决策矩阵，每个场景给出首选模型 + 备选 + 边界条件 |
| Cookbook | 5 本算法手册（优化/ML/评价/机理/统计） |
| 代码模板 | 22 个 Python + 7 个 MATLAB 可运行模板，含问题适配注释 |
| Playbook | 11 本完整例题走通（国赛 8 + 美赛 3），拆题到代码全流程 |
| 美赛专项 | 模型命名策略、Memo/Letter 框架、Our Work 流程图设计 |

### `math-modeling-paper` — 写作

建模做完了不会写论文？paper 帮你从空白页到排版完成。

| 功能 | 能力 |
|------|------|
| 结构模板 | 国赛/美赛双赛道标准结构 |
| 摘要指导 | 中英双语模板 + 获奖实例 |
| 题型策略 | A/B/C/D/E/F 六题型差异化写作策略 |
| 模型检验 | 灵敏度分析/误差分析/鲁棒性检验方法论 |
| 图表代码 | 流程图/数据图/伪代码规范 + 附录要求 |
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
  |-- 阶段1: 拆题分析（12 种问题类型判定）
  |-- 阶段2: 模型匹配（查决策矩阵 + 加载 Cookbook）
  |-- 阶段3: 算法展开 + 代码生成（加载模板填入参数）
  |-- 阶段4: 论文衔接 -> 输出 [PAPER_READY] 草稿片段
  |
  v
math-modeling-paper
  |-- Step 0: 检测 [PAPER_READY] 信号
  |-- Step 1: 确定比赛类型和写作阶段
  |-- Step 2: 加载对应指南
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
    |       |-- abstract-writing.md
    |       |-- common-phrases.md
    |       |-- cumcm-guide.md
    |       |-- figure-and-code-guide.md
    |       |-- mcm-icm-guide.md
    |       |-- memo-writing.md
    |       |-- model-validation.md
    |       |-- problem-type-strategies.md
    |-- math-modeling-solver/
        |-- SKILL.md
        |-- references/
            |-- problem-decomposition.md
            |-- model-selection-matrix.md
            |-- paper-bridge.md
            |-- mcm-specific-guide.md
            |-- cookbook-optimization.md
            |-- cookbook-ml.md
            |-- cookbook-evaluation.md
            |-- cookbook-mechanistic.md
            |-- cookbook-statistical.md
            |-- code-templates/ (29 files)
            |-- playbooks/ (11 files)
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
