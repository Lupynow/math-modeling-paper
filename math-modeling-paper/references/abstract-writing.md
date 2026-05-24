# 摘要写作指南（中英双语）

摘要/Summary Sheet 是评审的第一印象，决定论文是否进入下一轮审阅。

---

## 国赛摘要模板

> **篇幅**：约 500-800 字，严格控制在 1 页内。过短（<400 字）则量化结果不够，过长（>900 字）则溢出 1 页。

### 标准结构

```
针对[题目核心问题]，本文首先对原始数据进行[清洗/特征提取/标准化等处理]，
在此基础上分别建立[模型1]、[模型2]和[模型3]，对三个问题依次求解。

针对问题一，[方法描述]建立[模型名称]，[求解方式]。结果表明，[核心量化结论1]。
具体而言，[补充细节数据]。

针对问题二，基于问题一的[输出/结果]，进一步考虑[因素/约束]，建立[模型名称]。
采用[求解算法]求得[最优解/核心结果]。对比分析表明，[关键对比结论和数值]。

针对问题三，[拓展/应用/预测]。通过[方法]得到[结果]，
[结论的现实意义]。

通过[误差分析/灵敏度分析/蒙特卡洛模拟]验证模型有效性。
结果表明，[关键参数]在[范围]变动时，[结论]保持稳定，
模型具有[良好]的鲁棒性。

关键词：[3-5个核心词，用中英文均可]
```

### 实例（2025国赛无人机论文的摘要）

> 针对多无人机协同烟幕干扰任务的投放参数优化问题，本文建立了三维几何遮蔽判定模型，结合多种优化算法对单机到多机的投放策略进行系统求解。
>
> 针对问题一（单架无人机投放单枚烟幕弹），建立三维运动学和遮蔽判定模型，通过时间扫描法求得最优遮蔽时长为1.396秒。
>
> 针对问题二（单机多弹），基于CMA-ES算法优化投放时序，将遮蔽时长提升至4.474秒，提升幅度达220%。
>
> 针对问题三（多机单弹），采用SCE-UA全局优化算法求解，结合24关键点简化策略，最优遮蔽时长为6.403秒。
>
> 针对问题四（多机多弹协同任务分配），将问题抽象为组合优化模型，采用贪心算法(MAA)求解，最优遮蔽时长达10.44秒。
>
> 针对问题五（考虑威胁的全要素协同），构建三阶段决策框架，最优遮蔽时长为17.55秒。
>
> 通过蒙特卡洛模拟和龙卷风图对模型进行稳定性与灵敏度分析，验证了模型在不同参数扰动下的可靠性。
>
> 关键词：烟幕干扰；三维遮蔽判定；CMA-ES；SCE-UA；灵敏度分析；多无人机协同

**分析这个实例为什么好**：
- 每一问都有具体数值（1.396s, 4.474s, 6.403s, 10.44s, 17.55s）
- 每一问都交代了方法和模型
- 数字有递进逻辑（越来越大，符合问题从简单到复杂的逻辑）
- 最后一段提到了模型检验（蒙特卡洛+龙卷风图）
- 关键词精选了方法+领域词

### 实例2（2020 C 题 信贷决策 — 数据/ML 类）

> 针对中小微企业信贷风险的量化评估与决策问题，本文基于多源异构数据，建立了从数据清洗、特征选择到集成学习的全流程信贷决策模型。
>
> 针对问题一，对 123 家有信贷记录企业的进销项发票数据进行清洗与特征工程，提取了 23 个信贷评估指标，采用 Voting 策略融合 XGBoost、随机森林与逻辑回归，模型 AUC 达 99.42%，准确率 97.6%。
>
> 针对问题二，将问题一的特征体系迁移至 302 家无信贷记录企业，通过聚类分析对企业进行信用分级，给出四级信用评级的划分标准及对应利率策略。
>
> 针对问题三，综合考虑企业信贷风险与银行收益目标，建立多目标非线性规划模型，求得 26 个行业的最优信贷策略组合，银行总收益较基准方案提升 12.8%。
>
> 通过 K-fold 交叉验证（K=5）和 Bootstrap 重采样验证模型稳定性，结果表明模型在不同数据划分下准确率波动不超过 1.2%，具有较强的泛化能力。
>
> 关键词：信贷风险评估；集成学习；XGBoost；多目标优化；特征工程；Voting 融合

### 实例3（2018 B 题 RGV 动态调度 — 优化/决策类）

> 针对智能加工系统中 RGV 的动态调度问题，本文建立了基于多原则比较与蒙特卡洛模拟的两阶段调度模型。
>
> 针对问题一（单工序无故障），设计就近原则、FIFO 和 HRRN（高响应比优先）三种调度策略，通过蒙特卡洛模拟对比分析，HRRN 策略下系统在 8h 内完成加工 383 件，效率达 49.125 件/h。
>
> 针对问题二（双工序无故障），提出基于 0-1 规划的工序分配模型，以最小化系统空闲时间为目标，8h 加工量提升至 360 件，较单工序策略提升 34.8%。
>
> 针对问题三（考虑故障概率），引入故障概率分布（λ=0.01），建立基于 Markov 过程的随机调度模型，通过动态规划求出最优维护阈值，系统可用度提升至 97.3%。
>
> 通过 1000 次蒙特卡洛仿真验证模型在不同工况下的鲁棒性，调度策略在故障率 ±20% 波动时，系统效率变化率 <5%。
>
> 关键词：RGV 动态调度；0-1 规划；蒙特卡洛模拟；HRRN 策略；Markov 过程；动态规划

> **三个实例的共同点**：①每问都有具体数值；②方法名+结果对应清晰；③结尾都有检验总结句；④关键词覆盖领域+方法。这四条是所有获奖论文摘要的底线要求。

---

## 美赛 Summary Sheet 模板

### 标准结构

```
[Hook - 1 sentence, rhetorical or vivid]
"Even the hardest stone steps wear down over time — can we quantify centuries of foot traffic from the marks it leaves behind?"

[Problem Statement - 1-2 sentences]
We develop an integrated framework to model stair wear patterns, estimate historical visitor flow, and provide preservation recommendations for heritage sites.

[Task/Model 1 - Name (ACRONYM), method summary, key results with numbers]
We propose the Wear Volume Model (WVM) based on Archard's wear law, incorporating foot pressure distribution and material hardness. Historical visitor flow at the Temple of Heaven is estimated at 12,700 ± 2,100 daily during peak dynastic periods, with wear depth predictions achieving R² = 0.94 against measured data.

[Task/Model 2 - Same pattern]
To determine artifact age from wear patterns, we develop the Wear Dating Model (WDM) combining radiocarbon calibration with incremental wear accumulation. ...

[Task/Model 3 - Same pattern]
...

[Key validation findings - uncertainty, sensitivity]
Sobol' sensitivity analysis reveals that material hardness (index 0.43) and moisture content (index 0.31) are the dominant parameters controlling wear rates. Bootstrap validation yields 94.7% coverage for 95% confidence intervals.

Keywords: [6-8 technical keywords in English]
```

### 实例（2025 MCM Problem C Outstanding Paper）

> Golden competition, glorious shine. As the Olympic Games stand for the highest honor in sports, accurate prediction and interpretability are equally important. We develop a multi-layer framework combining Bayesian networks, deep learning, and natural language processing to forecast medal counts and analyze the influence of the Great Coach Effect.
>
> For Task 1, we propose the HARMONIE model (Hierarchical Aggregated Recursive Multi-Output Network for Integrated Estimation), integrating Static Bayesian Network, Dynamic Bayesian Network, and LSTM with temporal dimensionality expansion. Our model achieves NRMSE = 0.07, with 93.2% interval coverage for 95% prediction intervals. The US is predicted to lead with 39 gold, 45 silver, 43 bronze medals in 2028.
>
> For Task 2, ... [detailed results with numbers]
>
> For Task 3, ... [detailed results with numbers]
>
> For Task 4, ... [detailed results with numbers]
>
> Sobol' global sensitivity analysis identifies GDP (elasticity 0.42), host nation advantage (+12.3% medal boost), and recent performance trajectory as the dominant predictors. Extreme scenario analysis demonstrates robust model stability under GDP shocks up to ±15%.
>
> Keywords: Olympic medal prediction; Bayesian network; LSTM; Sobol' sensitivity analysis; Bootstrap uncertainty quantification; Great Coach Effect; SHAP interpretability; Elasticity analysis

---

## 摘要的十大常见错误

| # | 错误 | 后果 | 正确做法 |
|---|------|------|---------|
| 1 | 只写方法不写结果 | 评委不知道你得出了什么 | 每个问题至少一个具体数字 |
| 2 | 结果太模糊（"效果良好"） | 像没做出来 | 给出精确数值和对比 |
| 3 | 第一段大段复述背景 | 浪费最宝贵的空间 | 1-2句话带过 |
| 4 | 关键词太少或太泛 | 检索不到你的论文 | 3-8个，领域+方法 |
| 5 | 美赛没给模型起名 | 缺乏辨识度 | 创意名称+缩写 |
| 6 | 没提模型检验 | 暗示你没做检验 | 至少一句总结灵敏度/误差分析 |
| 7 | 数值没有单位 | 数值无意义 | 每个数字必须有单位 |
| 8 | 国赛摘要超过1页 | 格式违规 | 严格控制在1页内 |
| 9 | 美赛没有Hook句 | 开头平淡 | 一句有修辞感的开头 |
| 10 | 结果之间缺乏逻辑递进 | 像三个不相关的任务 | 展示问题递进和结果演变 |
