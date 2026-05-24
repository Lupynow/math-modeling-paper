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
| 问题拆解 | 自动判定 12 种数学本质类型（预测/优化/机理/网络科学/生态…） |
| 模型匹配 | 95+ 场景决策矩阵，每个场景给出首选模型 + 备选 + 边界条件 |
| Cookbook | 5 本算法手册：优化（GA/PSO/NSGA-II/CVaR）、ML（XGBoost/RF/GMM）、评价（TOPSIS/AHP/熵权/模糊）、机理（热传导/ODE/几何/光学）、统计（ANOVA/贝叶斯/时间序列/灰色关联） |
| 代码模板 | 22 个 Python + 7 个 MATLAB 可运行模板，含问题适配注释 |
| Playbook | 11 本完整例题走通（国赛 8 + 美赛 3），每本含拆题→选模型→公式→代码→结果全流程 |
| 美赛专项 | 模型命名策略、Memo/Letter/Policy Brief 写作框架、Our Work 流程图设计、可迁移性检验 |

### `math-modeling-paper` — 写作

建模做完了不会写论文？paper 帮你从空白页到排版完成。

| 功能 | 能力 |
|------|------|
| 结构模板 | 国赛/美赛双赛道标准结构（含页数建议和每节要点） |
| 摘要指导 | 中英双语模板 + 获奖实例 + 十大常见错误 |
| 题型策略 | A/B/C/D/E/F 六题型差异化写作策略（图表偏好、评审侧重、常见误区） |
| 模型检验 | 灵敏度分析、误差分析、鲁棒性检验的完整方法论 |
| 图表代码 | 流程图/数据图/伪代码规范 + 附录代码要求 |
| 句式库 | 中英双语学术句式，按章节组织 |
| Memo/Letter | 美赛 B-F 题一页 Memo/Letter 的格式、模板、实例 |
| 排版检查 | LaTeX/Word 检查清单 |

---

## 安装

```bash
cd ~/.claude/skills/
git clone https://github.com/Lupynow/math-modeling-skills.git
```

重启 Claude Code，两个 skill 自动加载。说出你的赛题，solver 自动触发；要写论文时，paper 随时待命。

---

## 工作流

```
拿到赛题
  │
  ▼
math-modeling-solver
  ├─ 阶段1：拆题分析（12 种问题类型自动判定）
  ├─ 阶段2：模型匹配（查 95+ 场景决策矩阵 + 加载对应 Cookbook）
  ├─ 阶段3：算法展开 + 代码生成（加载代码模板，填入问题参数）
  └─ 阶段4：论文衔接 → 输出 [PAPER_READY] 论文草稿片段
  │
  ▼
math-modeling-paper
  ├─ Step 0：检测 [PAPER_READY] 信号，加载草稿片段
  ├─ Step 1：确定比赛类型和写作阶段（规划/写作/润色/检查）
  ├─ Step 2：加载对应指南（国赛/美赛 + 专项 reference）
  └─ Step 3：逐章写作指导（目的→结构→内容→红线）
  │
  ▼
交卷 🎓
```

---

## 文件结构

```
math-modeling-skills/           # 仓库根目录
├── README.md
├── SKILL.md                    # math-modeling-paper 主文件
├── references/
│   ├── abstract-writing.md
│   ├── common-phrases.md
│   ├── cumcm-guide.md
│   ├── figure-and-code-guide.md
│   ├── mcm-icm-guide.md
│   ├── memo-writing.md
│   ├── model-validation.md
│   └── problem-type-strategies.md
└── math-modeling-solver/       # solver skill（子目录）
    ├── SKILL.md
    └── references/
        ├── problem-decomposition.md       # 拆题方法论
        ├── model-selection-matrix.md      # 模型决策矩阵
        ├── paper-bridge.md               # 论文衔接层
        ├── mcm-specific-guide.md         # 美赛专项指南
        ├── cookbook-optimization.md      # 优化类算法手册
        ├── cookbook-ml.md                # ML 类算法手册
        ├── cookbook-evaluation.md        # 评价类方法手册
        ├── cookbook-mechanistic.md       # 机理类建模手册
        ├── cookbook-statistical.md       # 统计类方法手册
        ├── code-templates/              # 29 个代码模板
        │   ├── python/  (22 files)
        │   └── matlab/  (7 files)
        └── playbooks/                   # 11 本例题走通
```

---

## 搭配 Skill

| Skill | 用途 |
|-------|------|
| `nature-figure` | 科研级图表（多面板、统一配色、期刊规范） |
| `nature-polishing` | 美赛英文润色（Nature 风格学术表达） |
| `xlsx` | 数据清洗与探索性分析 |
| `docx` | Word 排版输出 |
| `pdf` | PDF 合并导出 |

---

## License

MIT
