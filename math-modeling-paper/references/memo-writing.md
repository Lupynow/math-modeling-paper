# 美赛 Memo / Letter 写作指导

美赛部分题目要求撰写备忘录（Memo）或信件（Letter）作为论文的一部分。基于 2024-2025 年 Outstanding 论文的分析，约 40% 的题目涉及 Memo 写作。

---

## 哪些题目会考 Memo

| 题目类型 | Memo 出现频率 | 典型受众 |
|---------|-------------|---------|
| B 题（政策/管理） | 极高 | 政府机构、议会 |
| D 题（工程/环境） | 高 | 委员会、管理局 |
| E 题（生态/可持续） | 中 | 农场主、NGO |
| F 题（社会政策） | 中 | 政策制定者、执法机构 |
| A 题（硬科学） | 极低 | — |
| C 题（数据科学） | 极低 | — |

---

## 标准 Memo 格式

### 政府/机构备忘录（B/D 题）

```
MEMORANDUM

Date: March 15, 2025
To: [收件人全称及职务]
From: Team #25XXXX
Subject: [简洁概括核心建议]

[正文，分 I-VI 部分]

Sincerely,
Team #25XXXX
```

**正文结构**（按重要性递减）：

```
I.   Introduction — 简要回顾问题，说明本文目标（2-3 句）
II.  Executive Summary — 核心发现/建议的一句话汇总（1-2 句）
III. Model Overview — 用了什么模型，为什么（3-5 句，不含公式）
IV.  Key Findings — 每个子问题的量化结果（不需要完整推导，只给结论数据）
V.   Recommendations — 可执行的建议，逐条列出（2-4 条）
VI.  Limitations & Next Steps — 模型局限性和后续工作（2-3 句）
```

**关键原则**：
- **不写公式**：Memo 是给非技术决策者看的，不出现数学公式
- **量化但口语化**：「carbon emissions reduced by 23.7%」而非「the optimization function achieved a minimum at...」
- **一条建议一句话**：每条建议独立成行，方便快速阅读
- **1-2 页**：再重要也不超过 2 页

### 实例（2024 B 题 — 致希腊政府）

```
MEMORANDUM

Date: February 5, 2024
To: Hellenic Ministry of Shipping and Island Policy
From: Team #2407038
Subject: Predictive Model for Locating the Missing Submersible

I. Introduction
The missing submersible in the Ionian Sea presents an urgent search-and-rescue
challenge. This memorandum outlines a computational dynamics model to predict
the submersible's drift trajectory and recommends optimal search strategies.

II. Model Summary
We developed a Lagrangian particle tracking model incorporating ocean current
data (HYCOM), wind drift factors (3.5% of wind speed), and Monte Carlo uncertainty
propagation. The model identifies a primary search zone of 12.4 km² with 94.2%
probability of containment.

III. Key Findings
- Predicted location: 37°52'N, 20°43'E (±1.8 km at 95% CI)
- Search area: 12.4 km² (reduced from initial 50 km²)
- Recommended search pattern: Parallel sweep with 50m line spacing

IV. Recommendations
1. Deploy side-scan sonar in the primary search zone within 6 hours
2. Coordinate aerial surveillance for surface debris in the secondary zone
3. Establish a 24-hour update cycle for model recalibration with new data

V. Limitations
The model assumes steady-state currents over 6-hour windows. Rapid weather
changes may require recalibration.

Sincerely,
Team #2407038
```

---

## 不同受众的写法差异

| 受众 | 语气 | 技术深度 | 建议数量 | 示例 |
|------|------|---------|---------|------|
| 政府部长/议会 | 正式、说服性 | 极低（无公式） | 2-4 条 | B 题 |
| 管理委员会 | 专业但可读 | 低（可提方法名） | 3-5 条 | D 题 |
| 农场主/从业者 | 实用、可操作 | 极低 | 具体操作指南 | E 题 |
| 公众/媒体 | 通俗 | 无 | 1-2 条关键信息 | F 题 optional |

---

## Memo 与正文的关系

- **Memo 是独立文档**：放在正文末尾（附录之前），有自己的页码
- **内容来自正文但重新表达**：不复制正文段落，而是用非技术语言重写
- **先写正文再写 Memo**：正文完成后再把核心结果「翻译」成 Memo

---

## 常见错误

| 错误 | 正确做法 |
|------|---------|
| Memo 里出现公式 | 用自然语言描述关系 |
| 照搬摘要的内容 | 摘要给评委看，Memo 给决策者看，受众不同写法不同 |
| 超过 2 页 | 删减。决策者不会读超过 2 页的备忘录 |
| 没有具体数据 | 「significantly improved」→「reduced waiting time from 45 to 18 minutes」 |
| 缺少日期、收件人 | 正式 Memo 必须有完整抬头 |
| 语气过于学术 | 「We utilized a multi-objective optimization framework」→「We balanced three competing goals: cost, safety, and speed」 |

---

## 快速检查清单

- [ ] 有 Date / To / From / Subject 抬头
- [ ] 全文无数学公式
- [ ] 核心数据用口语化方式呈现（百分比、绝对数值）
- [ ] 建议逐条列出，可执行
- [ ] 长度 ≤ 2 页
- [ ] 受众适合（政府/委员会/从业者）
- [ ] 独立成章（不含在正文其他章节中）
