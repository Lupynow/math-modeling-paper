# 美赛 F 题：政策分析与社会科学建模

## 匹配条件
- 特征词："政策""法规""非法""监管""评估""利益相关者""成本效益""社会""公平""国际""政府""NGO""可持续发展目标"
- 比赛类型：美赛 MCM/ICM
- 题目类型：F
- 数学本质：多准则决策 + 利益相关者分析 + 政策影响评估

## 典型题目索引
- 2025 MCM F：Global Plastic Waste Treaty（全球塑料废物条约）
- 2024 MCM F：Illegal Wildlife Trade（非法野生动植物贸易）
- 2023 MCM F：Green GDP（绿色 GDP）
- 2022 MCM F：Global Equity and Climate Change（全球公平与气候变化）

## 通用解题框架

### Step 1：利益相关者识别与画像
列出所有相关方（政府、企业、NGO、公众、国际组织等），用 Power-Resources-Interest 三角或 Stakeholder Salience 模型做画像。这是 F 题不同于其他题型的第一步。

### Step 2：多准则评价建模
构建评价指标体系，融合定量数据（经济指标）和定性判断（政策文本）。常用 EWM + AHP 混合赋权，或模糊综合评价。

### Step 3：政策方案设计与量化
设计 2-3 个备选政策方案，用数学模型量化每个方案的影响（经济、社会、环境三维度）。

### Step 4：影响评估与预测
用多元回归、系统动力学或 Agent-Based Model 预测政策实施后的效果。善用"反事实分析"（有政策 vs 无政策对比）。

### Step 5：方案比选与推荐
用 TOPSIS/VIKOR/成本效益分析 对比方案，给出排名和推荐理由。

### Step 6：可迁移性检验
将分析框架应用到另一个国家/地区，验证框架的通用性。

## 关键陷阱
- **只做评价不做建模**：F 题不是写政治论文，必须有数学模型（评价模型、预测模型、优化模型至少各一个）
- **利益相关者分析太浅**：不能只说"A 关心钱、B 关心环境"，要量化他们的偏好（效用函数、权重向量）
- **政策建议无量化支撑**："应该加强执法"不是建模结论。要说"模型显示执法投入增加 30% 可减少非法贸易 22%"
- **忽略公平性维度**：F 题评审重视公平性（代际公平、南北公平），模型需体现
- **忘记 Policy Brief 格式**：输出必须包含一页 Policy Brief，写给决策者

## 完整例题走通：2024 MCM F 题 — 非法野生动植物贸易

参考论文：F_2413565, F_2422054

### 题目拆解
- 问题一（客户画像）：评价/聚类 — 识别非法贸易的客户群体特征
- 问题二（项目设计）：优化/匹配 — 设计替代生计项目，匹配客户需求
- 问题三（影响力评估）：预测/因果 — 评估项目对减少非法贸易的效果
- 问题四（政策建议）：决策 — 5 年实施计划

### 模型选择
论文使用了以下模型（美赛命名风格）：
- **Client Triangle Profile Model**（客户三角画像模型）：EWM + AHP，三维向量（权力/资源/利益）刻画每种客户
- **Win-Win Model**（双赢模型）：仿射映射(Affine mapping)，将客户需求映射到项目特征空间
- **Complement Vector Model**（互补向量模型）：余弦相似度 + 最大匹配，为客户匹配最合适的替代生计
- **Impact Model**：多元线性回归（MLR），评估项目对 5 个 SDG 指标的影响
- **Leslie-Gower 捕食模型**：预测物种数量恢复轨迹

### 核心公式
客户三角画像：
$$\vec{P}_{client} = (w_{power}, w_{resources}, w_{interest})$$
三维权重由 EWM + AHP 综合确定。

互补匹配得分：
$$S_{ij} = \cos(\vec{v}_i, \vec{p}_j) = \frac{\vec{v}_i \cdot \vec{p}_j}{|\vec{v}_i| \cdot |\vec{p}_j|}$$
其中 $\vec{v}_i$ 为项目特征向量，$\vec{p}_j$ 为客户需求向量。

影响模型（MLR）：
$$\Delta SDG_k = \beta_0 + \beta_1 \cdot Investment + \beta_2 \cdot Coverage + \beta_3 \cdot Duration + \varepsilon$$

### 代码思路
1. 用 AHP 确定 Power/Resources/Interest 三维权重
2. 对每个客户计算三角向量
3. 余弦相似度矩阵计算（客户 × 项目）
4. 匈牙利算法做最大权匹配
5. 多元回归评估影响
6. Monte Carlo 做敏感性分析

### Policy Brief 要点
- 写给：CITES（濒危野生动植物种国际贸易公约）秘书长
- Hook："Our Win-Win Model shows that a $2.3B investment in alternative livelihoods can reduce illegal wildlife trade by 34% within 5 years."
- 核心数据：客户画像分布、匹配成功率预测、各 SDG 影响量化、预算分配建议
- 行动路线图：Phase 1 (Year 1-2) / Phase 2 (Year 3-4) / Phase 3 (Year 5)

### 论文亮点
- 从数据中提取客户画像（不是拍脑袋），每个客户有具体的三维权重
- Win-Win Model 命名暗示"保护与发展双赢"的政治正确性
- 仿射映射 + 余弦相似度 + 最大匹配 三层模型链衔接流畅
- 5 个 SDG 指标的影响量化使政策建议有据可依
- "Our Work" 流程图以 Power-Resources-Interest 三角为核心视觉元素
