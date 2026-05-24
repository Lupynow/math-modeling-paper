"""
随机森林 回归/分类模板
适用：表格数据、中等样本、需要可解释性
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt


def train_random_forest(X_train, X_test, y_train, y_test):
    """训练随机森林并评估"""
    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=None,
        min_samples_split=5,
        min_samples_leaf=2,
        max_features='sqrt',
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    print(f"\n===== 随机森林 评估结果 =====")
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

    # 特征重要性图
    plt.figure(figsize=(8, 5))
    plt.barh(importance['feature'][::-1], importance['importance'][::-1])
    plt.xlabel('Importance')
    plt.title('Random Forest Feature Importance')
    plt.tight_layout()
    plt.savefig('rf_importance.png', dpi=150)
    plt.close()

    return model, {'r2': r2, 'mae': mae, 'rmse': rmse}


if __name__ == "__main__":
    from xgboost_template import load_data, feature_engineering
    from sklearn.preprocessing import StandardScaler

    X, y = load_data()
    X = feature_engineering(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train), columns=X.columns)
    X_test_scaled = pd.DataFrame(scaler.transform(X_test), columns=X.columns)

    model, metrics = train_random_forest(X_train_scaled, X_test_scaled, y_train, y_test)
