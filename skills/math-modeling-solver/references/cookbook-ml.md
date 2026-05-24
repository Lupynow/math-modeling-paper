# ML 类算法手册

覆盖：XGBoost、LightGBM、随机森林、SVM、BP 神经网络

---

## 0. 前置：EDA 与特征工程（ML 建模的基础）

**C 题评分红线：不做 EDA 直接调包的论文天然低一档。**

### EDA 必做清单
1. 描述性统计表（均值/标准差/最大/最小/分位数）
2. 缺失值检查（每列缺失比例）
3. 分布检查（直方图 + 正态性检验）
4. 相关性分析（热力图 + 散点图矩阵）
5. 异常值检测（箱线图 / 3σ 原则）

### 特征工程清单
1. **缺失值处理**：删除（缺失>50%）/ 均值填补 / KNN 填补 / 多重插补
2. **异常值处理**：盖帽法 / 分箱 / 保留（如异常值有业务意义）
3. **标准化**：Z-score（距离类模型必须）/ Min-Max / RobustScaler
4. **编码**：One-Hot（无序类别）/ Label Encoding（有序类别）/ Target Encoding（高基数类别）
5. **特征构造**：多项式特征 / 交互项 / 领域知识特征 / 时间特征分解
6. **特征选择**：相关性过滤 / 方差阈值 / 逐步回归 / RF 重要性 / SHAP / RFE

---

## 1. XGBoost

### 适用场景
- 表格数据，回归或分类
- 样本>500，特征<10K
- 存在非线性关系、交互效应
- 对预测精度要求高

### 核心公式（简化）

目标函数：
$$\text{Obj} = \sum_{i} L(y_i, \hat{y}_i) + \sum_{k} \Omega(f_k)$$

其中 $\Omega(f_k) = \gamma T + \frac{1}{2}\lambda\|w\|^2$（T 为叶节点数，w 为叶权重）

### 关键设计决策

| 参数 | 含义 | 建议范围 | 调参顺序 |
|------|------|---------|---------|
| n_estimators | 树的数量 | 100-1000 | ①先定 |
| max_depth | 树的最大深度 | 3-10 | ② |
| learning_rate | 学习率 | 0.01-0.3 | ③与 n_estimators 联动 |
| subsample | 样本采样比例 | 0.6-1.0 | ④ |
| colsample_bytree | 特征采样比例 | 0.6-1.0 | ④ |
| reg_alpha / reg_lambda | L1/L2 正则化 | 0-10 | ⑤ |
| min_child_weight | 最小叶节点权重和 | 1-10 | ⑤ |

### 调参策略
1. 先用默认参数跑 baseline
2. 固定 learning_rate=0.1，用 cv 确定 n_estimators
3. 调整 max_depth 和 min_child_weight
4. 调 subsample 和 colsample_bytree
5. 调正则化参数
6. 降低 learning_rate，增加 n_estimators

### Python 模板

见 `code-templates/python/ml/xgboost_template.py`

---

## 2. 随机森林 (Random Forest)

### 适用场景
- 中等样本量(100-1000)
- 需要可解释的特征重要性
- 对异常值和缺失值鲁棒
- baseline 模型首选

### 优势 vs XGBoost
- 不需要精细调参就能获得不错效果
- 对过拟合天然鲁棒（Bagging）
- 特征重要性更直观

### 关键参数
- n_estimators: 100-500
- max_depth: None（不限制）或 5-15
- min_samples_split: 2-10
- max_features: sqrt(n_features)（分类）/ n_features（回归建议 1/3）

### Python 模板

见 `code-templates/python/ml/random_forest_template.py`

---

## 3. SVM（支持向量机）

### 适用场景
- 小样本(<1000)、高维
- 分类边界复杂
- 二分类问题

### 关键注意事项
- **必须标准化**（SVM 对尺度敏感）
- RBF 核需调 C 和 gamma
- 大样本时训练慢，考虑 LinearSVC

---

## 4. BP 神经网络

### 适用场景
- 大样本(>5000)
- 高度非线性
- 图像/序列等非表格数据
- 传统 ML 方法效果不佳时

### 建模竞赛注意事项
- 小数据(<500)慎用神经网络，RF/XGBoost 通常更好
- 需要调参（层数/节点数/学习率/dropout）
- 必须在论文中画网络结构图
- 建议做多次运行取平均（神经网络不稳定）

---

## 5. 模型对比要求（C 题必备）

评审期望看到至少 3 种方法的系统对比：

| 对比维度 | 表格内容 |
|---------|---------|
| 模型 | 线性回归 / 随机森林 / XGBoost / ... |
| 超参数 | 关键参数值 |
| 训练集 R² | ... |
| 测试集 R² | ... |
| MAE / RMSE | ... |
| 训练时间 | ... |

选最终模型时给出理由：不只看精度，还要讨论复杂度、可解释性、过拟合风险。
