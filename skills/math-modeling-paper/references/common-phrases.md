# 常用学术句式库（中英双语）

按章节组织，句式来自历年获奖论文的提炼。

---

## 一、摘要

### 国赛句式

**开篇**：
- 针对[题目]中的[X]问题，本文……
- 本文围绕[核心问题]，从[角度1]、[角度2]、[角度3]三个层面展开研究。

**各问题方法+结果**：
- 针对问题X，采用[方法]建立[模型]，[求解方式]。结果表明，[核心数值结论]。
- 对于问题X，在问题(X-1)的基础上进一步考虑[因素]，建立[模型]。通过[算法]求得[最优值/最优解]为[数值]。
- 问题X的[求解/分析]表明，[关键发现]，[数值]较[基准]提升了[百分比]。

**模型检验收尾**：
- 通过[灵敏度分析/蒙特卡洛模拟/交叉验证]对模型进行检验，结果显示[关键参数]在[范围]内变动时，模型输出保持稳定，表明模型具有良好的鲁棒性。
- [误差分析方法]表明模型精度满足要求（R²=[值]，RMSE=[值]）。

**关键词**：
多目标优化、灰色预测(GM(1,1))、主成分分析、层次分析法(AHP)、熵权法、TOPSIS、聚类分析、遗传算法(GA)、粒子群算法(PSO)、模拟退火(SA)、灵敏度分析、综合评价、时间序列预测(ARIMA)、神经网络(BP/LSTM)、回归分析、模糊综合评价

### 美赛句式

**Hook**:
- [Evocative statement]. But behind [phenomenon] lies [hidden complexity].
- [Bold claim about the problem's importance]. Yet [gap/challenge] remains unresolved.
- "How can we [core question]?" This question drives our investigation.

**Model introduction**:
- We propose [ACRONYM] ([Model Name]), a [brief descriptor] that [key capability].
- Our framework integrates [Method A], [Method B], and [Method C] to [goal].
- Unlike existing approaches that [limitation], our model [innovation].

**Results**:
- Our model achieves [metric] = [value], with [coverage/confidence] for [interval].
- [Entity] is predicted to [outcome] with [value], followed by [entity] at [value].
- Sensitivity analysis via [method] reveals that [parameter] (elasticity [value]) and [parameter] ([value]) are the dominant predictors.
- The model demonstrates robust performance, with results remaining stable under [condition].

---

## 二、问题重述

### 国赛句式

- 本文研究的核心问题是……
- 题目要求[概括]，具体可分为以下[X]个子问题：……
- 问题X的核心挑战在于[难点]，需要在[约束]下寻找[目标]。

### 美赛句式

- The problem requires us to...
- Specifically, we are tasked with: (1) ..., (2) ..., (3) ...
- The central challenge lies in balancing [trade-off A] against [trade-off B].
- This problem can be decomposed into [N] interconnected sub-problems: ...

---

## 三、问题分析

### 国赛句式（注意：是"为什么"，不是"将做什么"）

**判断问题类型**：
- 问题X本质上是一个[预测/评价/优化/分类/机理分析]问题。
- 该问题的数学本质是[描述]，输入为[X]，期望输出为[Y]。

**说明方法选择理由**：
- 常用方法有[A]、[B]和[C]。[A]的优点在于……但缺点是……；[B]适合……但要求……；考虑到本题[数据/约束/目标的特征]，本文选用[C]，因为……
- 方法[A]和方法[B]均能处理该类问题，但[A]假设……这在本问题中不成立，故选用[B]。

**问题递进关系**：
- 问题X的[输出]可作为问题(X+1)的[输入/初值]，两个问题存在[递进/并列/互补]关系。
- 问题X的建模思路需要在问题(X-1)的基础上[扩展/细化/泛化]。

### 美赛句式

**Problem characterization**:
- Task X is fundamentally a [prediction/classification/optimization/causal inference] problem.
- The mathematical structure involves [description], with [input features] mapped to [output targets].

**Method selection rationale**:
- Standard approaches include [A], [B], and [C]. While [A] excels at ..., it assumes ..., which does not hold in our setting. [B] requires ..., which is unavailable. We therefore adopt [C] because ...
- The choice of [method] over alternatives is motivated by three considerations: (i) ..., (ii) ..., and (iii) ...
- Prior work by [citation] demonstrates that [method] is particularly effective when [condition present in our problem].

---

## 四、模型假设

### 国赛句式

- [假设内容]。这一假设的合理性在于[理由]，且在[条件]下已被广泛验证。
- 考虑到[实际情况]，本文假设[简化条件]。去掉该假设将导致[后果]，使其成为必要简化。
- 在[研究周期/特定条件]内，假设[因素]保持[状态]是合理的，因为[证据/引用]。

### 美赛句式

- **Assumption X: [statement].** Justification: [reasoning]. This assumption is supported by [literature citation or data evidence].
- We assume [condition] for the following reasons: (1) ..., (2) ...
- Relaxing this assumption would require [complexity], which lies beyond the scope of this paper but represents a natural extension.

### 禁止写的废话（中英均适用）
- ~~假设数据真实可靠~~ ← 数据由题目给定，不需要假设
- ~~假设忽略偶然因素~~ ← 太笼统，没说忽略了什么
- ~~假设题目所给参数准确~~ ← 同上
- ~~假设问题在理想条件下考虑~~ ← 没说清楚什么是"理想条件"
- ~~假设不考虑突发情况/极端事件~~ ← 不服务任何具体建模

---

## 五、数据处理

### 国赛句式

- 原始数据包含[X]条记录、[Y]个变量。经初步检查，发现[变量]存在[缺失比例]的缺失值，以及[描述]的异常值。
- 缺失值采用[均值/中位数/KNN/多重插补]填补，因为[理由]。
- 异常值使用[3σ准则/箱线图(IQR)/孤立森林]检测，共识别[X]个异常点，[删除/以边界值替换/Winsorize处理]。
- 为消除[量纲/数量级]差异对后续建模的影响，采用[Z-score标准化/Min-Max归一化]处理。
- 经[处理]后，数据[质量描述]满足[建模要求]。

### 美赛句式

- The raw dataset comprises [N] observations across [M] variables. Preliminary inspection reveals [X%] missingness in [variable] and [description of outlier patterns].
- Missing values were imputed using [method] because [justification]. This approach preserves [property] while avoiding [pitfall].
- Outliers were identified via [method] at the [α] significance level. [N] points were [treated/capped/retained] because [reasoning].
- Features were standardized using [Z-score/Min-Max] to ensure commensurability across [different scales/units].
- Exploratory Data Analysis (EDA) reveals [key patterns]: [finding 1], [finding 2]. These observations inform our subsequent modeling choices.

---

## 六、模型建立与求解

### 国赛句式

**模型选择理由**：
- 综合以上分析，选用[模型名称]，主要原因有三：(1)……；(2)……；(3)……

**建立模型**：
- 设[X]为[定义]，则目标函数可表示为：……
- 约束条件包括：(1)……；(2)……；(3)……
- 其中，第[公式]式表示[含义]，[参数]的取值依据为[来源]。

**求解**：
- 本文采用[算法]进行求解，算法流程如图[X]所示。
- [算法名]的核心步骤为：(1)……；(2)……；(3)……，迭代终止条件为[条件]。
- 收敛过程如图[X]所示，算法在[迭代次数]次后达到[收敛阈值]。

**结果展示与分析**：
- 图[X]展示了[内容]。从图中可以看出，[发现]。
- 表[X]列出了[内容]。数据显示，[趋势/对比]。
- [结果数值]表明，[解释]。这一结果的物理/实际含义是[含义]。
- 对比[X]与[Y]，可以发现[差异]，其原因是[分析]。

### 美赛句式

**Model conceptualization**:
- We conceptualize this task as a [framework] problem and design [ACRONYM] to address it.
- The key insight underlying our approach is that [intuition]. This motivates the following formulation.

**Model formulation**:
- Let [symbol] denote [definition]. The objective is to [goal]:
  ```
  [equation block]
  ```
  where [term 1] captures [meaning 1] and [term 2] penalizes [meaning 2].

**Algorithm presentation**:
- Algorithm 1 summarizes the solution procedure.
- The algorithm converges when [condition], typically within [K] iterations.

**Results interpretation**:
- Figure [X] reveals that [finding]. This pattern suggests that [interpretation], consistent with [theory/expectation].
- Table [X] reports [metrics]. Notably, [comparison] shows [key insight].
- These results imply that [practical implication]. From a policy/decision perspective, this means [application].

---

## 七、模型检验

参考 `model-validation.md` 获取完整方法和句式。

**通用句式**：
- 为验证模型的[可靠性/稳定性/精度]，本文进行[类型]分析。
- 选取[参数]作为灵敏度分析对象，将其取值在[基准值]基础上分别变动±[X]%和±[Y]%，观察[输出]的变化。
- 结果表明，[参数]对模型输出影响[最大/较大/有限]，当[参数]变化[X]%时，[输出]变化[Y]%。

---

## 八、优缺点与改进

### 国赛句式

**优点**（每条以"本模型"开头）：
- 本模型将[领域知识]与[数学方法]相结合，[具体优点描述]。
- 本模型通过[技术手段]处理了[问题]，提高了[某方面的性能]。
- 本模型采用[方法]代替传统[方法]，在[场景]下表现出更好的[特性]。

**缺点**（针对本模型的局限）：
- 本模型假设[条件]，当[条件不满足]时可能产生[偏差/误差]。
- 本模型将[因素]简化为[简化形式]，未考虑[更复杂的情况]，后续可引入[改进方法]。
- 本模型的[参数]依赖于[估计/经验公式]，若[条件变化]则需重新[校准]。

### 美赛句式

**Strengths**:
- [S1] A key strength of our approach is [specific feature], which enables [capability] that simpler models cannot achieve.
- [S2] Unlike [alternative approach] that [limitation], our [ACRONYM] model [advantage].
- [S3] The integration of [component A] with [component B] provides a [synergistic benefit].

**Weaknesses** (paired with concrete improvements):
- [W1] Our model assumes [specific assumption]. When this does not hold (e.g., under [scenario]), [consequence]. Future work could relax this assumption by [concrete method].
- [W2] The computational cost of [component] scales as [complexity], which may limit applicability to [large-scale settings]. Parallelization or [optimization technique] could address this.
- [W3] We treat [factor] as [simplified treatment], neglecting [real-world complexity]. Incorporating [method] would improve fidelity.

---

## 九、参考文献

### 格式要点

**中文期刊**：
```
[序号] 作者. 论文题目[J]. 期刊名, 年份, 卷(期): 起止页码.
```

**英文期刊**：
```
[序号] Author A, Author B. Title of article[J]. Journal Name, Year, Volume(Issue): Pages.
```

**教材/专著**：
```
[序号] 作者. 书名[M]. 出版地: 出版社, 年份.
```

**国标**：
```
[序号] 标准编号, 标准名称[S].
```

### 警示列表（绝对不能引用）
- CSDN 博客（https://blog.csdn.net/...）
- 知乎文章
- 百度百科/维基百科
- AI 工具输出（ChatGPT, DeepSeek 等）
- 个人博客/公众号
- 未发表的手稿/preprint（可引用 arXiv 但需说明未 peer-review）

---

## 十、过渡与连接词

### 中文论文

**序列**：首先，其次，再次，最后；第一步，第二步
**因果**：因此，由此可见，这导致，其原因在于；由于，基于此
**对比**：然而，相反，另一方面；相比之下，与之相对
**递进**：此外，不仅如此，进一步地；更进一步说
**总结**：综上所述，总而言之，整体而言

### 英文论文

**Sequence**: First, / Subsequently, / Furthermore, / Finally,
**Causality**: Therefore, / Consequently, / As a result, / This suggests that / This finding indicates that
**Contrast**: However, / In contrast, / On the other hand, / Conversely, / Nevertheless,
**Addition**: Moreover, / Additionally, / In addition, / It is also worth noting that
**Emphasis**: Notably, / Importantly, / It should be emphasized that / Of particular significance is
**Summary**: In summary, / Overall, / Taken together, / In conclusion,
