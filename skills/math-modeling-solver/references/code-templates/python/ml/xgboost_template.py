"""
XGBoost 回归/分类模板
适用：表格数据、非线性预测
问题适配点：
  1. 修改 load_data() 加载实际数据
  2. 选择回归(XGBRegressor)或分类(XGBClassifier)
  3. 调整特征工程
  4. 调整超参数
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import xgboost as xgb
import matplotlib.pyplot as plt
import seaborn as sns


def load_data():
    """加载数据"""
    # TODO: 替换为实际数据加载
    # df = pd.read_csv('data.csv') 或 pd.read_excel('data.xlsx')
    # 生成演示数据
    np.random.seed(42)
    n = 500
    X = pd.DataFrame({
        'feature_1': np.random.randn(n),
        'feature_2': np.random.randn(n),
        'feature_3': np.random.randn(n),
        'feature_4': np.random.randn(n),
    })
    y = (3 * X['feature_1'] + 2 * X['feature_2'] ** 2
         - 1.5 * X['feature_3'] + 0.5 * X['feature_4'] * X['feature_1']
         + np.random.randn(n) * 0.5)
    return X, y


def eda(df):
    """探索性数据分析"""
    print("=" * 50)
    print("描述性统计")
    print("=" * 50)
    print(df.describe())

    print("\n缺失值检查：")
    print(df.isnull().sum())

    # 相关性热力图
    plt.figure(figsize=(10, 8))
    sns.heatmap(df.corr(), annot=True, cmap='RdBu_r', center=0, fmt='.2f')
    plt.title('Correlation Heatmap')
    plt.tight_layout()
    plt.savefig('correlation_heatmap.png', dpi=150)
    plt.close()


def feature_engineering(X, y=None, is_train=True):
    """特征工程"""
    X = X.copy()

    # 1. 缺失值处理
    for col in X.columns:
        if X[col].isnull().sum() > 0:
            X[col] = X[col].fillna(X[col].median())  # 数值→中位数

    return X


def train_xgboost(X_train, X_test, y_train, y_test):
    """训练 XGBoost 并评估"""
    # 基础模型
    model = xgb.XGBRegressor(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=1,
        reg_lambda=1,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train,
              eval_set=[(X_train, y_train), (X_test, y_test)],
              verbose=False)

    y_pred = model.predict(X_test)

    # 评估指标
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    print(f"\n===== XGBoost 评估结果 =====")
    print(f"R² = {r2:.4f}")
    print(f"MAE = {mae:.4f}")
    print(f"RMSE = {rmse:.4f}")

    # 特征重要性
    importance = pd.DataFrame({
        'feature': X_train.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    print(f"\n特征重要性：")
    print(importance.to_string(index=False))

    # 预测 vs 真实值
    plt.figure(figsize=(6, 6))
    plt.scatter(y_test, y_pred, alpha=0.5, s=10)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=1)
    plt.xlabel('True Values')
    plt.ylabel('Predictions')
    plt.title(f'XGBoost: R² = {r2:.4f}')
    plt.tight_layout()
    plt.savefig('xgboost_pred_vs_true.png', dpi=150)
    plt.close()

    return model, {'r2': r2, 'mae': mae, 'rmse': rmse}


def hyperparameter_tuning(X_train, y_train):
    """超参数网格搜索"""
    param_grid = {
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.05, 0.1],
        'n_estimators': [200, 300, 500],
        'subsample': [0.7, 0.8, 1.0],
    }
    xgb_model = xgb.XGBRegressor(random_state=42, n_jobs=-1)
    grid = GridSearchCV(xgb_model, param_grid, cv=5,
                        scoring='r2', n_jobs=-1, verbose=1)
    grid.fit(X_train, y_train)
    print(f"\n最优参数: {grid.best_params_}")
    print(f"最优 R²: {grid.best_score_:.4f}")
    return grid.best_estimator_


if __name__ == "__main__":
    X, y = load_data()

    # EDA
    eda(X)

    # 特征工程
    X = feature_engineering(X)

    # 划分
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # 标准化（XGBoost 不必须，但做 baseline 对比时需要）
    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train), columns=X.columns)
    X_test_scaled = pd.DataFrame(scaler.transform(X_test), columns=X.columns)

    # 训练 XGBoost
    model, metrics = train_xgboost(X_train_scaled, X_test_scaled, y_train, y_test)

    # 超参数优化（可选）
    # best_model = hyperparameter_tuning(X_train_scaled, y_train)
