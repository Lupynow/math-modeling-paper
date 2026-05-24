# 网络科学与运筹优化 Playbook（MCM D 题）

## 匹配条件
- 特征词：network flow、dynamic network、time-expanded graph、water level regulation、dam scheduling、stakeholder optimization、multi-objective、NSGA-II、linear programming、transportation network、congestion、queueing theory、traffic optimization、graph theory、accessibility、betweenness centrality
- 比赛类型：美赛 MCM/ICM
- 题目类型：D 题（网络科学 / 运筹学）
- 数学本质：动态网络流建模 + 多目标优化 + 利益相关者效用函数

## 典型题目索引
- 2025 MCM D：Baltimore 交通网络重建（排队论 + A*/GA + 蒙特卡洛 + ADP 近似动态规划）
- 2024 MCM D：Great Lakes 水位调控（动态流网络 + 时滞互相关 + LP + NSGA-II）

## 通用解题框架（6步）

### Step 1：将物理/工程系统抽象为网络模型
将湖泊、城市、交通节点抽象为有向图 \(G = (V, E)\)，边权表示流量或通行时间。

**标准抽象套路**（2024 D2417004/2429211）：
- 节点 = 五大湖（Superior, Michigan+Huron, Erie, Ontario）+ 大西洋（sink）
- 边 = 连接水道/河流，方向为自然流向
- 可控制边 = Soo Locks 和 Moses-Saunders Dam 两条弧
- 确定各边容量 \(\mu_i\) 和传递时间 \(\tau_i\)（关键：lag time）

**时滞互相关法确定 lag**（2024 D2429211）：
- 对各湖水位时间序列做 time-lagged cross-correlation
- 取相关性最大处的 lag 值作为两湖间水流传递时间
- 示例结果：Superior->Michigan 约 1 个月，Superior->Ontario 约 3 个月
- 构建完整的 lag matrix

### Step 2：建立动态网络流模型（时间展开图）
用 Ford-Fulkerson 时间展开法将动态流转化为静态流：
- 对时间轴离散化（如以天为步长）
- 为每个时间点复制一组节点
- 按 lag time 连接跨时步的有向边
- 得到增广网络 \(N^\circ = (V, E, \mu, V^+, V^-)\)，可直接用静态流算法

**2025 变体（交通网络）**：
- 用排队论计算拥堵指数（congestion index）
- 用 A* 算法计算可达性（accessibility），GA 优化路径
- 节点介数中心性（Betweenness Centrality）识别关键节点
- 蒙特卡洛模拟处理不规则区域的覆盖计算

### Step 3：定义利益相关者效用函数
枚举所有利益相关者，为每个构建 utility function。

**2024 Great Lakes 六类**：
1. Shipping companies：偏好高且稳定的水位
2. Docks/Montreal harbor：偏好低且稳定的水位
3. Environmentalists：偏好自然年际波动（正弦振荡模拟）
4. Riparian property owners：偏好低水位 + 小振幅 + 高频波动（利于沙滩补给）
5. Recreational boaters：偏好稍高于平均水位
6. Hydropower：偏好稳定在 7000 m³/s 附近

将各 stakeholder 的偏好量化为目标水位的正弦曲线 \(h_{ideal}(t)\)，振幅和频率按需求调整。

### Step 4：建立多目标优化模型
**LP 路径**（2024 D2429211）：
- 决策变量：每个时间步 Soo Locks 和 Moses-Saunders 的放水量 \(x_t, y_t\)
- 目标：minimize \(\sum \omega_i |h_{i,t} - \hat{h}_{i,t}| + (1-\omega_i)|f_t - \hat{f}_t|\)
- 约束：水位转移方程、洪水/枯水上下界、水坝最大放水能力
- 双层结构：Macroschedule（月级 LP）+ Microschedule（小时级 LP）

**NSGA-II 路径**（2024 D2417004）：
- 决策变量：水位 H 和水流 Q
- 多目标：最大化各利益相关者收益函数 + 最小化各利益相关者成本函数
- 编码：实数编码水位值，GA 操作（选择、交叉、变异）
- 输出 Pareto 前沿，从中选取均衡方案

### Step 5：气象/物理因素精细化修正
**规则曲线（Rule Curves）**（2024 D2417004）：
- 基于 NTS（Net Total Supply）的滑动规则曲线
- 高于历史平均 NTS 时增加放水，低于时减少放水
- 水位-放水联动：水位高于平均时增加释放防洪水

**风合成模型**：
- 将多站点风向分解为东向和北向分量
- 计算合成风程（fetch）\(C = \sqrt{C_N^2 + C_E^2}\)
- 风程越大，下风侧水位越高，需增加泄水补偿

**冰堵与融雪**：冬季冰堵减少 St. Lawrence 流量需要上游补偿放水，春季融雪需预判 Ottawa River 暴涨。

### Step 6：利益相关者权重自适应与结果验证
**权重调整机制**（2024 D2429211）：
- 初始权重 \(w_0\) 运行模型 5 个月预测
- 执行前 2 个月计划，计算每个 stakeholder 的实际误差 \(\varepsilon_i = \sum |h_t - \hat{h}_t|\)
- 下轮权重 \(w_{i, next} = \varepsilon_i / \sum_k \varepsilon_k\) ——偏差大的 group 下一轮获得更高权重
- 保证长期公平性

**鲁棒性检验**：
- 用 25th/50th/75th 分位数降雨数据分别运行，观察 Lake Ontario 水位稳定性
- 重点结论：有效调度 Lake Superior 是 Lake Ontario 水位达标的关键

## 关键陷阱
1. **忽略时滞导致模型失实**：Superior->Ontario 有约 3 个月的传递延迟，忽略此 lag 会导致下游调度完全错位。必须用时滞互相关或物理模型确定 lag matrix。
2. **利益相关者权重分配不当**：等权重看似公平，但 stakeholder 的 utility 曲线形状不同（有的需要正弦波动，有的需要恒定），等权重下某些群体被系统性牺牲。需要权重自适应机制。
3. **只建单一时间尺度模型**：月度 macro-schedule 满足长期目标，但日度 micro-schedule 对 stakeholder 的直接影响更大（如 Montreal 港口的工作时间）。两层级嵌套是必须的。
4. **线性回归的参数检查不足**：用线性回归拟合湖高-流出关系时要检查 R² 和残差分布。2024 D2429211 的 Niagara River 回归 R²=0.928，Detroit River R²=0.850，均在可接受范围，但低于 0.7 的需要考虑非线性模型。
5. **低估气象因素对网络容量的影响**：冰堵使冬季河流量下降、融雪使春季暴涨、风使湖面倾斜——这些因素会临时改变边的有效容量，纯静态容量约束无法应对。

## 完整例题走通：2024 MCM D -- Dynamic Dams Model (D2429211)

### 题目拆解
- **Task 1**：建立 Great Lakes 动态流网络模型，确定最优水位。数学本质：**时间展开图 + 线性规划**。
- **Task 2**：考虑利益相关者需求，给出水坝调度方案。数学本质：**多目标优化 + 自适应权重**。
- **Task 3**：双层调度（Macro + Micro）。数学本质：**双层 LP嵌套**。
- **Task 4**：模型洞察与敏感性分析。数学本质：**分位数情景分析**。

### 模型选择
| 子问题 | 核心模型 | 备选方案 | 选择理由 |
|--------|---------|---------|---------|
| 网络流建模 | 时间展开图 + LP | NSGA-II 纯启发式 | LP 有最优性保证、速度快（Simplex）、可解释（白盒），适合政策建议场景 |
| Lag 确定 | 时滞互相关（TLCC） | Granger 因果检验 | TLCC 直观且与物理水流传播一致，月度数据粒度足够 |
| 利益相关者建模 | 正弦理想曲线 + 自适应权重 | AHP 固定权重 | 水位问题天然有年周期，正弦拟合自然；自适应权重避免"一锤定音"的不公平 |
| 微观调度 | 日内 LP（Microschedule） | 贪心规则曲线 | LP 可 look-ahead，在约束内实现最优；贪心规则曲线不如 LP 灵活 |

### 核心公式
**时间展开网络水位转移**：
\[
h_{1,t} = h_{1,t-1} - x_{t-1} + r_{1,t-1}
\]
\[
h_{2,t} = h_{2,t-1} + s_1 x_{t-L_1} - (\alpha_2 h_{2,t-1} + \beta_2) + r_{2,t-1}
\]
其中 \(L_1\) 是 Superior->Michigan 的传递月数，\(\alpha, \beta\) 来自高度-流出回归。

**Microschedule LP**：
\[
\min \alpha_1 |h_t - \hat{h}_t| + \alpha_2 |f_t - \hat{f}_t|
\]
\[
\text{s.t. } h_t = h_{t-1} + F_t - x_t,\quad f_t = \omega f_{t-1} + k(1-\omega)x_t
\]

### 代码思路
**Macroschedule LP 架构**：
1. 数据准备：用 TLCC 确定所有边 lag，用线性回归确定 flow-height 参数 \((\alpha_i, \beta_i)\)
2. 构建时间展开图：为 T 个时间步复制节点，按 lag 连接
3. 设定利益相关者理想水位曲线（正弦函数族）
4. 用 `scipy.optimize.linprog` 或 `cvxpy` 求解 LP
5. 输出各时间步的最优放水量和水位轨迹

**Microschedule LP 分时调度**：
1. 从 Macroschedule 获取当日总放水目标 \(H_{target}\)
2. 以小时为步长，优化日内逐时放水量
3. 目标：minimize 水位偏差 + 流速偏差

### Memo/Letter 要点
- 收件人：IJC Leadership（International Joint Commission）
- 要点：模型如何比 Plan 2014 更优（动态 look-ahead + 自适应权重 + 双层调度）
- 给出具体的 rule curves 参数建议表（类似 D2417004 的 Table 2/3）
- 强调气候韧性：能适应降雨量的分位数波动
- 用一页清晰传达核心建议，避免数学细节堆砌

### 结果解读
- Lake Superior 的调度非鲁棒（受降雨影响大），但 Lake Ontario 非常稳定——说明"上游吸收波动，下游享受稳定"是有效策略
- Macroschedule + Microschedule 的衔接：Macro 给出日总量，Micro 优化日内分配，日内流速误差可控制在 1.5% 以内
- 当降雨处于 75th 分位数时，仅 Lake Superior 有明显水位升高，其余四湖接近理想曲线——系统整体鲁棒

### 论文亮点（含"Our Work"图描述）
1. **时间展开图的工程直觉**：将动态流转化为静态流是网络流理论的经典技巧，但在 MCM 论文中出现频率极低——这本身就是差异化亮点。"Our Work"图应展示原始网络 -> 时间展开 -> 双层调度 pipeline 的三级结构。
2. **从"静态 rule curve"到"动态 look-ahead LP"**：Plan 2014 本质是固定阈值 rule curve，论文的 LP 方案能在给定降雨预测下提前规划 4 个月——这是从 reactive 到 proactive 的范式转变。
3. **自适应权重机制**：不是静态赋权，而是每 2 个月根据实际偏差重分配权重——体现"数据驱动的公平"。需在图中展示权重随时间演化的动态过程。
4. **双层调度的工程完备性**：Macro 保长期目标，Micro 保短期满意度——两个 LP 形式统一、参数可解释、代码可复用。"Our Work"流程图中应明确展示 Macro -> Micro 的数据流和反馈环。
