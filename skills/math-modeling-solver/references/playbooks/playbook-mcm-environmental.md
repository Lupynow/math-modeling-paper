# 美赛 E 题：环境科学与生态建模

## 匹配条件
- 特征词："环境""生态""物种""种群""食物链""可持续发展""碳排放""气候""自然灾害""污染""保护""保险"
- 比赛类型：美赛 MCM/ICM
- 题目类型：E
- 数学本质：生态系统建模 + 环境评估 + 优化/政策

## 典型题目索引
- 2025 MCM E：Forest-to-Agriculture Ecosystem Transition（森林转农田生态影响）
- 2024 MCM E：Extreme Weather Property Insurance（极端天气财产保险）
- 2023 MCM E：Drought in the Colorado River Basin
- 2022 MCM E：Carbon Sequestration（森林碳汇）

## 通用解题框架

### Step 1：生态系统机制建模
构建食物链/食物网模型（Lotka-Volterra 或 Holling 功能响应），或碳/水循环模型，或极端事件统计模型。E 题核心是"理解自然系统的数学规律"。

### Step 2：数据处理与参数估计
从题目数据或文献中提取关键参数（物种增长率、捕食率、碳排放因子等）。善用文献综述补充参数（这是美赛加分项）。

### Step 3：多情景模拟
设置不同情景（如不同气候情景 RCP 4.5/8.5，不同政策力度），用 Monte Carlo 或 ODE 数值求解模拟长期演变。

### Step 4：构建评价指标体系
设计生态健康/可持续性/经济影响等指标。常用 Shannon-Wiener 多样性指数、生态系统服务价值、成本效益比。

### Step 5：优化与政策建议
基于模拟结果，优化政策参数（如补贴力度、保险定价、保护区面积）。输出具体可操作的建议。

### Step 6：可迁移性检验
将模型应用到另一个区域/生态系统，验证通用性（美赛标配）。

## 关键陷阱
- **生态模型过于简化**：单用 Lotka-Volterra 而不考虑环境承载力、年龄结构等多因素
- **参数无出处**：生态参数不能瞎编，必须引用文献或从数据估计
- **忽略反馈循环**：生态系统有正负反馈，单向因果链不够
- **政策建议太空泛**：必须给出具体数值（如"建议补贴 $X/亩"），不能只说"应该加强保护"
- **忘记 Letter**：E 题必须写给农民/社区/决策者的信

## 完整例题走通：2024 MCM E 题 — 极端天气财产保险

参考论文：E_2401102, E_2410889

### 题目拆解
- 问题一（保险定价模型）：统计/预测 — 基于历史极端天气数据建立保险精算模型
- 问题二（需求-风险均衡）：优化 — 在保险公司利润和居民可负担性之间找平衡
- 问题三（政策建议）：决策 — 提出具体的保险方案和风险分担机制

### 模型选择
论文使用了以下模型（注意美赛命名风格）：
- **AFC/LFC 保险定价模型**（Lane's model）：精算定价核心
- **Cobb-Douglas EER 计算**：经济-环境-风险三元效用函数
- **DEMI 模型（Demand-Risk Equilibrium Model for Insurance）**：双目标优化（需求最大化 vs 风险最小化）
- **Marshallian 需求曲线**：分析价格对保险购买意愿的影响
- **ARIMA 模型**：极端天气频率预测

### 核心公式
Lane's AFC 保险定价：
$$P = E[L] + \lambda \cdot \sigma(L)$$
其中 $E[L]$ 为期望损失，$\sigma(L)$ 为损失标准差，$\lambda$ 为风险载荷因子。

DEMI 双目标优化：
$$\max_{p} \quad \alpha \cdot D(p) - (1-\alpha) \cdot R(p)$$
其中 $D(p)$ 为保险需求函数，$R(p)$ 为风险敞口，$\alpha$ 为社会偏好权重。

### 代码思路
1. 用 ARIMA 预测极端天气频率
2. Monte Carlo 模拟损失分布（10,000 次）
3. 对每个价格档位计算需求-风险均衡点
4. 绘制 Pareto 前沿，选最优定价

### Memo/Letter 要点
- 写给：FEMA（联邦紧急事务管理局）或保险公司 CEO
- Hook 句："Our model shows that a 15% premium increase can reduce bankruptcy risk by 40% while maintaining 80% affordability."
- 核心数据：建议保费区间、投保率预测、财政影响
- 行动建议：3 条具体政策措施

### 论文亮点
- 模型命名精美：DEMI、AFC/LFC 形成命名体系
- 需求曲线从真实数据拟合（Marshallian demand）
- 双目标 Pareto 前沿可视化展示 trade-off
- 可迁移性：将模型从 Florida 迁移到 California 检验
- "Our Work" 流程图以保险定价为核心，展示数据→定价→均衡→政策 全链路
