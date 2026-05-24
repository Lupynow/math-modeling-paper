# Math Modeling Solver — 数学建模竞赛解题指导

> 从拆题到代码的完整建模方案。与 `math-modeling-paper` 形成"解题→写作"配对。

## 功能

- **四阶段解题工作流**：拆题分析 → 模型匹配 → 算法展开+代码生成 → 论文衔接
- **模型决策矩阵**：覆盖 8 种问题本质类型，每种含首选/备选模型及选择理由
- **算法 Cookbook**：GA/PSO/SA/LP/XGBoost/RF/AHP/TOPSIS 等算法的问题适配指南
- **可运行代码模板**：Python + MATLAB，含问题适配注释
- **论文桥接**：输出可直接嵌入 `math-modeling-paper` 的论文片段

## 安装

```bash
cd ~/.claude/skills/
git clone https://github.com/Lupynow/math-modeling-solver.git
```

重启 Claude Code 即可自动加载。

## 使用方式

```
这道题怎么建模：[粘贴赛题文本]
2024 国赛 A 题板凳龙用什么模型？
我已经拆完题了，帮我选模型：[分析文本]
给我写一个带约束的 GA 代码框架
C 题数据预测，XGBoost 和随机森林怎么选？
```

## 搭配使用

- `math-modeling-paper`：解题完成后切换到论文写作
- `nature-figure`：科研级图表
- `xlsx`：数据清洗与分析

## 文件结构

```
math-modeling-solver/
├── SKILL.md
└── references/
    ├── problem-decomposition.md
    ├── model-selection-matrix.md
    ├── paper-bridge.md
    ├── cookbook-optimization.md
    ├── cookbook-ml.md
    ├── cookbook-evaluation.md
    ├── cookbook-mechanistic.md    (P1)
    ├── cookbook-statistical.md    (P1)
    ├── code-templates/
    │   ├── python/
    │   └── matlab/
    └── playbooks/                 (P1/P2)
```

## License

MIT
