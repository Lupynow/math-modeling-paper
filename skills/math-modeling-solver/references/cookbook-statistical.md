# 统计分析手册

覆盖：假设检验、方差分析、实验设计与优化、蒙特卡洛模拟、贝叶斯推断、成分数据分析、时间序列分析、灰色关联分析

---

## 统计方法选择速查

| 问题类型 | 推荐方法 |
|---------|---------|
| 两组均值是否有显著差异 | t 检验 / Mann-Whitney U |
| 多组均值比较 | 单因素 ANOVA + Tukey HSD |
| 分类变量独立性 | 卡方检验 |
| 多因素 + 交互效应 | 双因素 ANOVA |
| 因素筛选（因素 > 5） | Plackett-Burman 设计 |
| 因素优化 + 曲面 | RSM 响应曲面法 |
| 小样本、贫信息、不确定性强 | 灰色关联分析 |
| 成分比例数据（和为 1） | 成分数据分析（CLR 变换） |
| 时序预测 | ARIMA / SARIMA / Prophet |
| 参数不确定性传播 | 蒙特卡洛模拟 |
| 先验知识 + 数据更新 | 贝叶斯推断 |

---

## 1. 假设检验

### 核心概念

| 概念 | 含义 |
|------|------|
| 原假设 $H_0$ | 默认立场（无差异、无关联），假定为真 |
| 备择假设 $H_1$ | 与原假设对立的主张 |
| 显著性水平 $\alpha$ | 犯第 I 类错误的概率上限，通常取 0.05 |
| p 值 | 在 $H_0$ 为真时，观察到当前结果（或更极端）的概率 |
| 第 I 类错误 | $H_0$ 为真但拒绝 $H_0$（假阳性） |
| 第 II 类错误 | $H_0$ 为假但未拒绝 $H_0$（假阴性） |

**判断规则**：若 $p < \alpha$，拒绝 $H_0$，结果具有统计显著性。

### t 检验

**单样本 t 检验**：检验样本均值是否等于已知值 $\mu_0$。

$$t = \frac{\bar{x} - \mu_0}{s / \sqrt{n}} \sim t(n-1)$$

**独立样本 t 检验**：比较两组独立样本的均值。

$$t = \frac{\bar{x}_1 - \bar{x}_2}{\sqrt{\frac{s_1^2}{n_1} + \frac{s_2^2}{n_2}}}$$

前提：两组方差齐性时用 Student's t，不齐时用 Welch's t。

**配对 t 检验**：同一对象前后两次测量。

$$t = \frac{\bar{d}}{s_d / \sqrt{n}}, \quad d_i = x_{i,\text{after}} - x_{i,\text{before}}$$

```python
from scipy.stats import ttest_ind, ttest_rel, ttest_1samp

# 独立样本 t 检验
stat, p = ttest_ind(group_a, group_b, equal_var=False)  # Welch

# 配对 t 检验
stat, p = ttest_rel(before, after)
```

### 卡方检验

**独立性检验**：检验两个分类变量是否独立。

$$\chi^2 = \sum_{i=1}^{r} \sum_{j=1}^{c} \frac{(O_{ij} - E_{ij})^2}{E_{ij}}$$

其中 $E_{ij} = (行合计_i \times 列合计_j) / 总计$。

**拟合优度检验**：检验观测分布是否符合理论分布。

```python
from scipy.stats import chi2_contingency

# 独立性检验（列联表）
chi2, p, dof, expected = chi2_contingency(observed_table)
```

### Mann-Whitney U 检验（非参数替代）

当数据不满足正态性假设时，替代独立样本 t 检验。基于秩和而非原始值，对离群值鲁棒。

```python
from scipy.stats import mannwhitneyu
stat, p = mannwhitneyu(group_a, group_b, alternative='two-sided')
```

### 多重比较校正

当同时进行 $k$ 次假设检验时，族错误率（FWER）膨胀。Bonferroni 校正将 $\alpha$ 调整为 $\alpha/k$。

$$p_{\text{adj}} = \min(k \cdot p, 1)$$

```python
from statsmodels.stats.multitest import multipletests
reject, p_adj, _, _ = multipletests(raw_p_values, method='bonferroni')
```

### 典型赛题

- **2024B 生产决策**：需判断新工艺是否显著提升良品率（单侧 t 检验），并结合序贯抽样减少检验成本
- **2020C 信贷风险评估**：检验不同信用等级企业的违约率是否存在显著差异（卡方独立性检验）

---

## 2. 方差分析 (ANOVA)

### 单因素 ANOVA

比较 $k$ 个组的均值是否相等。

$$H_0: \mu_1 = \mu_2 = \cdots = \mu_k$$

**平方和分解**：

$$SS_T = SS_B + SS_W$$

$$SS_B = \sum_{j=1}^{k} n_j (\bar{x}_j - \bar{x})^2, \quad SS_W = \sum_{j=1}^{k} \sum_{i=1}^{n_j} (x_{ij} - \bar{x}_j)^2$$

**F 统计量**：

$$F = \frac{MS_B}{MS_W} = \frac{SS_B / (k-1)}{SS_W / (N-k)} \sim F(k-1, N-k)$$

**效应量**：

$$\eta^2 = \frac{SS_B}{SS_T}$$

```python
import pingouin as pg
# 单因素 ANOVA + 效应量
result = pg.anova(data=df, dv='value', between='group', detailed=True)
```

### 双因素 ANOVA（含交互效应）

**平方和分解**：

$$SS_T = SS_A + SS_B + SS_{AB} + SS_E$$

分别检验因素 A 的主效应、因素 B 的主效应、以及 A 与 B 的交互效应。

MATLAB 实现：

```matlab
% 单因素
[p, tbl, stats] = anova1(data, group);

% 双因素（含交互）
[p, tbl, stats] = anova2(data, reps);  % reps = 重复次数

% 多因素
[p, tbl, stats] = anovan(y, {A, B, C}, 'model', 'interaction');
```

### 前提条件检验

| 条件 | 检验方法 | Python |
|------|---------|--------|
| 正态性 | Shapiro-Wilk | `scipy.stats.shapiro(residuals)` |
| 方差齐性 | Levene | `scipy.stats.levene(*groups)` |

**不正态/方差不齐时的对策**：
- 数据变换：对数变换 $\log(x)$、Box-Cox 变换
- 改用非参数方法：Kruskal-Wallis 检验

```python
from scipy.stats import kruskal
stat, p = kruskal(*groups)
```

### 事后检验：Tukey HSD

ANOVA 显著后，需要确定哪些组间有差异。

$$HSD = q_{\alpha}(k, N-k) \cdot \sqrt{\frac{MS_W}{n}}$$

```python
pg.pairwise_tukey(data=df, dv='value', between='group')
```

### 典型赛题

- **2021B 乙醇制备 C4 烯烃**：双因素方差分析——催化剂组合（Co 负载量 + Co/SiO2 比例）对 C4 烯烃收率的影响，检验主效应和交互效应后确定最优配比

---

## 3. 实验设计与优化 (DOE/RSM)

### 正交设计

适用于多因素多水平实验，用最少的实验次数覆盖所有因素组合。

常用正交表：$L_9(3^4)$ 表示 4 因素 3 水平只需 9 次实验（全因子需 $3^4 = 81$ 次）。

**步骤**：因素/水平选择 $\to$ 选正交表 $\to$ 表头设计 $\to$ 实验实施 $\to$ 极差/方差分析 $\to$ 最优水平组合

### 响应曲面法 (RSM)

当因素与响应间存在非线性关系时，用二次回归模型逼近。

$$y = \beta_0 + \sum_{i=1}^{k} \beta_i x_i + \sum_{i=1}^{k} \beta_{ii} x_i^2 + \sum_{i<j} \beta_{ij} x_i x_j + \varepsilon$$

**中心复合设计 (CCD)** 和 **Box-Behnken 设计 (BBD)** 是两种最常用的 RSM 实验设计。

```python
import statsmodels.api as sm

# 二次回归
X_quad = np.column_stack([X, X**2])  # 加权二次项
model = sm.OLS(y, sm.add_constant(X_quad)).fit()

# 绘制等高线图
x1_grid, x2_grid = np.meshgrid(np.linspace(...), np.linspace(...))
# 用模型预测 grid 上的响应值，plt.contourf
```

### Plackett-Burman 筛选设计

当备选因素较多（>5）时，先用 PB 设计筛选显著因素，再对显著因素做 RSM 优化。PB 设计能以 $N$ 次实验考察 $N-1$ 个因素（$N$ 为 4 的倍数）。

### 最优条件确定

- **岭分析（Ridge Analysis）**：在约束区域内搜索最优响应点
- **期望函数法（Desirability Function）**：多响应优化时，将每个响应转为 0-1 期望值，求几何平均最大化

### 典型赛题

- **2021B 催化剂组合优化**：先用正交设计筛选 Co 负载量、Co/SiO2 比、温度、乙醇浓度四个因素，再用 RSM 对显著因素精细优化，绘制等高线图确定 C4 烯烃收率最大的工艺条件

---

## 4. 蒙特卡洛模拟

### 基本流程

1. 定义输入变量的概率分布（正态、均匀、三角等）
2. 从各分布独立随机抽样 $N$ 次
3. 对每组抽样计算模型输出
4. 统计输出的分布特征（均值、方差、分位数、置信区间）

### 随机数生成与抽样

```python
import numpy as np

np.random.seed(42)  # 可复现

# 常用分布
samples = np.random.normal(loc=5, scale=2, size=10000)      # 正态
samples = np.random.uniform(low=0, high=1, size=10000)       # 均匀
samples = np.random.triangular(0, 1, 3, size=10000)          # 三角
samples = np.random.lognormal(mean=0, sigma=1, size=10000)   # 对数正态
```

MATLAB 对照：

```matlab
rng(42);
samples = randn(10000, 1) * 2 + 5;     % 正态
samples = rand(10000, 1);               % 均匀 [0,1]
```

### 收敛判断

随模拟次数 $N$ 增大，输出的 $(1-\alpha)$ 置信区间宽度应收敛。画出区间宽度 vs $N$ 的曲线，当宽度不再显著缩小时可停止。

```python
def mc_convergence(model_fn, sample_fn, N_max, batch_size):
    means, ci_widths = [], []
    for n in range(batch_size, N_max + 1, batch_size):
        data = model_fn(sample_fn(n))
        means.append(np.mean(data))
        ci = np.percentile(data, [2.5, 97.5])
        ci_widths.append(ci[1] - ci[0])
    return means, ci_widths
```

### 方差减小技术

| 技术 | 原理 | 适用场景 |
|------|------|---------|
| 对偶变量 | 成对使用 $U$ 和 $1-U$，负相关抵消方差 | 单调函数 |
| 控制变量 | 引入已知期望的相关变量校正估计 | 存在高相关辅助变量 |
| 重要性抽样 | 在重要区域多抽样，加权修正 | 稀有事件概率 |
| 拉丁超立方 | 分层抽样，每层均匀覆盖 | 多维参数空间探索 |

### 典型应用

- **鲁棒性检验**：参数在 $\pm20\%$ 范围随机扰动，检验结论是否稳定
- **风险评估**：现金流/收益的 VaR（Value at Risk）和 CVaR
- **参数灵敏度**：Sobol 指数 / Morris 方法

参考模板：`code-templates/python/optimization/monte_carlo_template.py`

---

## 5. 贝叶斯推断

### 贝叶斯定理

$$P(\theta \mid D) \propto P(D \mid \theta) \times P(\theta)$$

后验 $\propto$ 似然 $\times$ 先验。先验编码已有知识，似然编码新数据，后验融合两者。

### 共轭先验速查

| 似然 | 先验 | 后验 |
|------|------|------|
| Binomial | Beta($\alpha, \beta$) | Beta($\alpha + k, \beta + n - k$) |
| Normal(unknown $\mu$, known $\sigma^2$) | Normal($\mu_0, \tau^2$) | Normal（解析形式） |
| Poisson | Gamma($\alpha, \beta$) | Gamma($\alpha + \sum x_i, \beta + n$) |

共轭先验的优势：后验有闭式解，无需 MCMC，计算快速。

### 后验推断

- **MAP 估计**（最大后验）：$\hat{\theta}_{\text{MAP}} = \arg\max_\theta P(\theta \mid D)$
- **可信区间**：$P(a \leq \theta \leq b \mid D) = 0.95$，与频率学派的置信区间概念不同

```python
# Beta-Binomial 共轭：p 的后验
# 先验：Beta(2, 2)，观测：10 次中 7 次成功
alpha_post = 2 + 7
beta_post = 2 + 3
# 后验均值 = alpha_post / (alpha_post + beta_post)
# 95% 等尾可信区间
from scipy.stats import beta
ci_low, ci_high = beta.ppf([0.025, 0.975], alpha_post, beta_post)
```

### 贝叶斯序贯决策

每次观测后更新后验分布，判断是否满足停止条件（如后验概率超过阈值）。典型场景：生产线上逐步抽样，判断批次是否合格。

```python
def bayesian_sequential(x, prior_alpha, prior_beta, threshold=0.95):
    a, b = prior_alpha, prior_beta
    for i, obs in enumerate(x):
        a += obs
        b += 1 - obs
        prob = beta.cdf(threshold, a, b)  # P(θ > threshold | D)
        if prob > 0.99 or prob < 0.01:
            return i + 1, a, b, prob  # 提前停止
    return len(x), a, b, prob
```

### 典型赛题

- **2024B 生产决策**：利用序贯检验 + 贝叶斯更新，每一批抽样后更新良品率的后验分布，当有足够把握判断是否达标时停止抽样，最小化检测成本

---

## 6. 成分数据分析

### 核心问题

成分数据满足 $\sum_{j=1}^{D} x_j = 1$（或 100%），各分量非负。传统统计方法（如欧氏距离、Pearson 相关）在单纯形空间上失效，因为变量间存在伪相关（一个分量增加必然导致其他分量减少）。

### 对数比变换

| 变换 | 公式 | 特点 |
|------|------|------|
| ALR（加性对数比） | $\text{ALR}(x)_j = \ln(x_j / x_D)$ | 以最后一个成分为参考，非等距 |
| CLR（中心化对数比） | $\text{CLR}(x)_j = \ln(x_j / g(x))$ | 几何均值 $g(x)$ 为参考，等距，共线性 |
| ILR（等距对数比） | 序贯二元划分 | 正交坐标，适用于回归/分类 |

其中 $g(x) = \left(\prod_{j=1}^{D} x_j\right)^{1/D}$ 为几何均值。

**推荐流程**：原始成分数据 $\xrightarrow{\text{CLR}}$ 变换后数据 $\to$ 聚类/分类/降维。

### Aitchison 几何

- **Aitchison 距离**：$d_a(x, y) = \sqrt{\sum_{j=1}^{D} \left(\ln\frac{x_j}{g(x)} - \ln\frac{y_j}{g(y)}\right)^2}$
- 在处理成分数据时，所有距离、均值、方差都应在 Aitchison 几何框架下进行

```python
import numpy as np

def clr_transform(X):
    """X: (n_samples, n_components), 每行和为 1"""
    X_safe = np.where(X <= 0, 1e-16, X)  # 处理零值
    g = np.exp(np.mean(np.log(X_safe), axis=1, keepdims=True))
    return np.log(X_safe / g)

# CLR 变换后可接标准 K-Means
from sklearn.cluster import KMeans
X_clr = clr_transform(compositional_data)
labels = KMeans(n_clusters=3).fit_predict(X_clr)
```

### 典型赛题

- **2022C 古代玻璃成分分析**：玻璃各氧化物成分之和为 100%，属于典型成分数据。先用 CLR 变换解除单纯形约束，再对变换后数据做 K-Means 聚类以区分不同类别的古代玻璃，最后用 LDA 判别新样本的类型

---

## 7. 时间序列分析

### 分解模型

**加法模型**：$Y_t = T_t + S_t + R_t$

**乘法模型**：$Y_t = T_t \times S_t \times R_t$

乘法模型适用于季节波动幅度随趋势增大的情况（如销售额随市场增长而波动变大）。

```python
from statsmodels.tsa.seasonal import seasonal_decompose
result = seasonal_decompose(series, model='additive', period=12)
result.trend, result.seasonal, result.resid
```

### 自相关分析

| 函数 | 用途 |
|------|------|
| ACF（自相关函数） | 识别 MA(q) 阶数：ACF 在滞后 q 后截尾 |
| PACF（偏自相关函数） | 识别 AR(p) 阶数：PACF 在滞后 p 后截尾 |

### 平稳性检验

非平稳序列无法直接建模 ARIMA。用 ADF 检验（Augmented Dickey-Fuller）：

$$H_0: \text{存在单位根（非平稳）}$$

$p < 0.05$ 则拒绝 $H_0$，序列平稳。若不平稳，通过差分使序列平稳化。

### ARIMA 建模

ARIMA(p, d, q)：p=自回归阶数，d=差分阶数，q=移动平均阶数。

**建模流程**：平稳性检验 $\to$ 差分（确定 d）$\to$ ACF/PACF 定阶（确定 p, q）$\to$ 参数估计 $\to$ 残差白噪声检验

**SARIMA**：加入季节项 $(P, D, Q, s)$，s 为季节周期（如月度数据 s=12）。

```python
from statsmodels.tsa.arima.model import ARIMA
model = ARIMA(series, order=(p, d, q))
result = model.fit()
forecast = result.forecast(steps=12)
```

### 备选方法

- **Prophet**：Facebook 开源，内置节假日效应和变点检测，对缺失值鲁棒，适合业务预测
- **指数平滑 (ETS)**：Holt-Winters 方法，支持趋势和季节性

### 评估指标

$$MAE = \frac{1}{n}\sum |y_i - \hat{y}_i|, \quad MAPE = \frac{1}{n}\sum \left|\frac{y_i - \hat{y}_i}{y_i}\right| \times 100\%$$

$$RMSE = \sqrt{\frac{1}{n}\sum (y_i - \hat{y}_i)^2}$$

**残差白噪声检验（Ljung-Box）**：$H_0$ 为残差无自相关（即模型已提取完所有结构信息）。$p > 0.05$ 表示残差为白噪声，模型充分。

```python
from statsmodels.stats.diagnostic import acorr_ljungbox
lb_result = acorr_ljungbox(result.resid, lags=[10, 20], return_df=True)
```

### 典型赛题

- **2023C 蔬菜定价与补货**：蔬果销量有强周度和季节性模式，需用 SARIMA 或 Prophet 预测各品种销量，结合成本与损耗率制定最优定价和补货策略

---

## 8. 灰色关联分析 (GRA)

### 适用场景

- 样本量小（$n < 20$）
- 信息不完全、贫信息
- 不确定性强，传统统计方法假设不满足

灰色系统理论由邓聚龙教授提出，核心思想是利用已知的小部分信息去提取有价值的内容。

### 步骤

**Step 1: 数据标准化**

对原始序列做无量纲化处理（常用初值化或均值化）：

$$x_i'(k) = \frac{x_i(k)}{x_1(k)} \quad \text{或} \quad \frac{x_i(k)}{\bar{x}(k)}$$

**Step 2: 计算关联系数**

$$\xi_i(k) = \frac{\min_i \min_k |x_0(k) - x_i(k)| + \rho \cdot \max_i \max_k |x_0(k) - x_i(k)|}{|x_0(k) - x_i(k)| + \rho \cdot \max_i \max_k |x_0(k) - x_i(k)|}$$

其中 $x_0$ 为参考序列（理想方案），$\rho$ 为分辨系数，通常取 0.5。

**Step 3: 计算关联度并排序**

$$\gamma_i = \frac{1}{n} \sum_{k=1}^{n} \xi_i(k)$$

$\gamma_i$ 越大，第 $i$ 个比较序列与参考序列越接近。

### 分辨系数选择

- $\rho$ 越小，关联系数间差异越大，分辨率越高
- 通常取 $\rho = 0.5$，若需更精细区分也可取 $\rho = 0.3$
- **Deng 氏关联度**（默认）vs **绝对关联度**：后者用斜率差代替绝对差，对序列变化趋势更敏感

```python
import numpy as np

def grey_relational_grade(reference, comparison, rho=0.5):
    """reference, comparison: (n_features,) 的一维数组"""
    ref = reference / reference[0]  # 初值化
    comp = comparison / comparison[0] if comparison.ndim == 1 \
           else comparison / comparison[:, 0:1]
    diff = np.abs(ref - comp)
    rho_max = rho * diff.max()
    xi = (diff.min() + rho_max) / (diff + rho_max)
    return xi.mean()
```

### 典型赛题

- **2022C 古代玻璃成分分析**：将各样品视为序列，用 GRA 分析玻璃各成分之间的关联程度（如铅钡玻璃中 PbO 与 BaO 的关联度），辅助判定玻璃类型和风化机理

---

## 9. 通用统计工具速查

| 分析类型 | Python | MATLAB |
|---------|--------|--------|
| t 检验 | `scipy.stats.ttest_ind` / `ttest_rel` | `ttest2` / `ttest` |
| Mann-Whitney | `scipy.stats.mannwhitneyu` | `ranksum` |
| 方差分析 | `statsmodels.formula.api.ols` + `anova_lm` | `anova1` / `anovan` |
| Kruskal-Wallis | `scipy.stats.kruskal` | `kruskalwallis` |
| 卡方检验 | `scipy.stats.chi2_contingency` | `crosstab` |
| 正态性检验 | `scipy.stats.shapiro` | `jbtest` / `lillietest` |
| 方差齐性 | `scipy.stats.levene` | `vartestn` |
| 相关分析 | `scipy.stats.pearsonr` / `spearmanr` | `corr` / `corrcoef` |
| 线性回归 | `statsmodels.api.OLS` / `sklearn.linear_model` | `fitlm` / `regress` |
| 逻辑回归 | `sklearn.linear_model.LogisticRegression` | `fitglm` / `mnrfit` |
| ARIMA | `statsmodels.tsa.arima.model.ARIMA` | `arima` / `estimate` |
| 多重比较 | `statsmodels.stats.multitest.multipletests` | `multcompare` |
| Tukey HSD | `pingouin.pairwise_tukey` | `multcompare(stats)` |
| CLR 变换 | 手动实现 `np.log(x / g(x))` | 无内置，同 Python 逻辑 |

---

## 常见陷阱与对策

| 陷阱 | 对策 |
|------|------|
| 不做正态性/方差齐性检验就直接 t 检验 | 先做 Shapiro-Wilk + Levene，不过则改用非参数检验 |
| 多次 t 检验代替 ANOVA（I 类错误膨胀） | 用 ANOVA + 事后比较 |
| 忽略交互效应直接做主效应分析 | 双因素 ANOVA 先检验交互项是否显著 |
| 成分数据直接用普通聚类 | CLR/ILR 变换后再分析 |
| 时序不检验平稳性直接 ARIMA | 先做 ADF 检验，差分至平稳 |
| p 值不显著就声称"无差异" | 考虑检验功效是否足够（样本量是否过小） |
| 忽略多重比较校正 | 大于 3 组比较时必须用 Bonferroni/Tukey HSD |
