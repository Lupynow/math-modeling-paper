# 美赛 (MCM/ICM) 专项指南

基于 2024-2025 年 24 篇 O/F 奖论文分析。

---

## 1. 美赛题型全景

| 题号 | 类型 | 典型领域 | 需 Memo/Letter |
|------|------|---------|---------------|
| A | Continuous (连续型) | 物理/工程/生态机理 | 否 |
| B | Discrete (离散型) | 优化/调度/系统动力学 | **是 — Memo** |
| C | Data Insights (数据洞察) | 数据科学/ML/统计 | **是 — Memo** |
| D | OR/Network Science | 运筹学/网络科学 | **是 — Memo/Letter** |
| E | Environmental Science | 环境科学/生态 | **是 — Letter** |
| F | Policy | 政策/社会科学 | **是 — Letter/Policy Brief** |

---

## 2. 模型命名策略（核心竞争力）

美赛论文**必须**给模型起创意名称+缩写。

### 模式 1：描述性首字母缩写（推荐）
- BDS = Biomass-Diversity-Stability Assessment Model
- DEMI = Demand-Risk Equilibrium Model for Insurance
- SIAMOS = Strategic Importance Assessment Model for Olympic Sports
- CEAOM = Comprehensive Equipment Allocation Optimization Model

### 模式 2：隐喻/艺术化
- "The Triangular Balance"（三角平衡）
- "Unlocking the Abyss"（深海探索）
- "Step Chronicles"（台阶磨损分析）

### 命名规则
1. 缩写 3-7 字母，能发音更好
2. 首次出现给全称：`BDS (Biomass-Diversity-Stability) Assessment Model`
3. 多个模型统一命名风格
4. **禁**：直接叫 "Model 1"、"Optimization Model"

---

## 3. Memo/Letter 写作框架

### Memo（写给决策者/机构）
```
TO: [机构名]
FROM: Team #[编号]
DATE: [日期]
SUBJECT: [核心建议一句话]

正文(3-4段):
1. Hook + 核心结论
2. 方法概述（非技术语言）
3. 关键发现 + 量化结果（必须带数字）
4. 行动建议（具体可操作）

关键词: 3-5个
```

### Letter（写给公众/社区）
```
Dear [受众],

1. 背景 + 我们做了什么（1段）
2. 关键发现（1-2段，带数据）
3. 建议/呼吁（1段）
4. 总结（1段）

Sincerely,
Team #[编号]
```

**关键**: 非技术语言、必须有数字、1页以内。

---

## 4. "Our Work" 流程图设计

美赛每篇论文都有一个整页流程图（标志性特征）。

### 结构
```
[数据/输入] → [模型1: 名称] → [中间结果]
                              ↓
[外部因素] → [模型2: 名称] → [中间结果]
                              ↓
[反馈循环] → [模型3: 名称] → [最终输出]
                              ↓
                   [检验/验证] → [结论/建议]
```

### 设计原则
- 颜色区分：数据(蓝)、模型(橙)、结果(绿)、检验(灰)
- 箭头标注传递的数据类型
- 如有反馈，务必画出反馈回路
- 放在 Introduction 末尾

---

## 5. 模型可迁移性检验（美赛标配）

美赛几乎必定检验模型的可迁移性。

| 原场景 | 迁移场景 |
|--------|---------|
| Wimbledon 男单 | Wimbledon 女单 / 乒乓球 |
| Juneau, Alaska | Jiuzhaigou, China |
| Ionian Sea | Caribbean Sea |

**标准句式**: "To test generalizability, we applied the model to [different scenario]..."

---

## 6. 美赛 vs 国赛差异速查

| 维度 | 国赛 (CUMCM) | 美赛 (MCM/ICM) |
|------|-------------|---------------|
| 语言 | 中文 | 英文 |
| 题数 | 3 (A/B/C) | 6 (A/B/C/D/E/F) |
| 模型命名 | 不必须 | **必须**（创意缩写） |
| Memo/Letter | 不涉及 | **B-F 题标配** |
| Our Work 图 | 推荐 | **近乎必须** |
| 模型可迁移性 | 罕见 | **标配** |
| 灵敏度分析 | 嵌入子问题 | 独立成节(1-3页) |
| Summary Sheet | 正文第一页 | 独立页(400-550词) |
| 文献综述 | 不必须 | ~60%论文包含 |
| AI Usage Report | 建议 | ~37%论文包含 |
| 评审侧重 | 方法正确性、模型检验 | 建模创新性、写作表达 |

---

## 7. D/E/F 题特有模型

**D 题（网络科学）**: 动态流网络、Ford-Fulkerson、最大流/最小割、网络鲁棒性、节点重要性

**E 题（环境科学）**: Lotka-Volterra、Holling 功能响应、食物网、碳循环核算、生态系统服务

**F 题（政策）**: 利益相关者画像、政策影响评估、成本效益分析、多准则决策(MCDM)
