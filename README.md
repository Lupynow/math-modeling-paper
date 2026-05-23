# Math Modeling Paper - 数学建模竞赛论文写作 Skill

> 基于 30+ 篇获奖论文（国赛一等/美赛 Outstanding）与 12 场实际参赛经验的反向工程，覆盖 CUMCM（国赛）和 MCM/ICM（美赛）全流程论文写作指导。

## 这个 Skill 解决什么问题

数学建模比赛的**核心瓶颈往往不在建模能力，而在论文写作**。通过分析从三等奖到一等奖的论文差距，我们发现：

| 得分差异 | 关键因素 |
|---------|---------|
| 摘要缺量化结果 | 三等奖/优秀奖论文摘要只写方法不写结果，一等奖论文每问必有具体数值 |
| 模型检验缺失 | 低分论文跳过灵敏度分析/误差分析，优秀论文用 2-5 页做检验 |
| 参考文献用 CSDN | 低分论文引用博客/AI 工具，优秀论文引用期刊论文和教材 |
| 问题分析=方法罗列 | "我们将用 XX 方法"vs"因为 XX 特点，选择 YY 方法而非 ZZ" |
| 优缺点评算法不评模型 | "线性回归简单直观"(评算法) vs "本模型将产量假设为线性，未考虑交互效应"(评本模型) |

## 功能覆盖

- **双赛道支持**：国赛 (CUMCM) + 美赛 (MCM/ICM)，含差异化评审标准
- **全流程指导**：结构规划 → 逐节写作 → 润色优化 → 格式检查
- **摘要专项**：中英双语模板 + 实例 + 十大常见错误
- **模型检验大全**：5 种检验方法 + Sobol' 全局灵敏度分析代码 + 三级要求
- **常用句式库**：中英双语学术句式，按章节组织
- **LaTeX / Word 双输出**：排版检查清单

## 安装

### 方式一：通过 .skill 文件安装

1. 下载 `math-modeling-paper.skill`
2. 在 Claude Code 中运行：
```bash
claude install math-modeling-paper.skill
```

### 方式二：手动安装

将本仓库克隆到 Claude Code 的 skills 目录：

```bash
# Claude Code skills 目录
cd ~/.claude/skills/
git clone https://github.com/<your-username>/math-modeling-paper.git
```

## 使用方式

在 Claude Code 中，提及以下任一内容即可自动触发：

```
帮我写国赛论文的摘要
检查这篇美赛论文的模型检验部分
怎么写灵敏度分析
模型假设怎么写才不废话
论文参考文献格式检查
把这篇中文论文翻译润色成美赛英文
```

Skill 会先确认比赛类型和当前阶段，然后提供针对性指导。

## 文件结构

```
math-modeling-paper/
├── SKILL.md                         # 主文件：使用流程、结构模板、分节规则、红线
└── references/
    ├── cumcm-guide.md               # 国赛逐节详细写法指南
    ├── mcm-icm-guide.md             # 美赛逐节详细写法指南
    ├── abstract-writing.md          # 摘要模板+实例+常见错误（中英双语）
    ├── model-validation.md          # 5 种检验方法+Python 代码+检查清单
    └── common-phrases.md            # 中英双语学术句式库（按章节组织）
```

## 设计依据

此 Skill 的规则和模板来自对以下材料的系统分析：

- **30 篇 2025 MCM/ICM Outstanding/Finalist 论文**
- **72 篇 2018-2024 CUMCM 一等/优秀论文**
- **12 场实际参赛经验**（数维杯一等/二等、APMCM 二等、MathorCup、国赛省三、美赛等）
- **官方评审标准**（CUMCM 格式规范 2024-2026、MCM/ICM 官方指南）

核心发现：**从三等奖到一等奖，论文结构完整性和模型检验是最大区分器。**

## License

MIT

## 贡献

欢迎提交 Issue 和 PR。如果你有获奖论文的写作经验想要融入此 Skill，请分享你的模板和句式。
