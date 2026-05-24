"""
熵权法模板
适用：数据驱动的客观赋权
"""

import numpy as np
import pandas as pd


def entropy_weight(matrix):
    """
    熵权法计算指标权重

    Parameters:
        matrix: np.ndarray, (n_samples, n_criteria) 原始数据矩阵
                所有指标应为极大型（正向化之后）

    Returns:
        weights: np.ndarray, 归一化权重向量（和=1）
        entropy: np.ndarray, 各指标的信息熵
    """
    n, m = matrix.shape
    X = matrix.astype(float).copy()

    # Step 1: Min-Max 标准化（平移避免 0）
    X_min = X.min(axis=0)
    X_max = X.max(axis=0)
    # 处理所有值相同的列
    range_val = X_max - X_min
    range_val[range_val == 0] = 1
    P = (X - X_min) / range_val
    P = P + 1e-10  # 避免 log(0)

    # Step 2: 归一化（每列和为 1）
    P = P / P.sum(axis=0)

    # Step 3: 信息熵
    k = 1.0 / np.log(n)
    entropy = -k * (P * np.log(P)).sum(axis=0)

    # Step 4: 差异系数 → 权重
    d = 1 - entropy
    weights = d / d.sum()

    return weights, entropy


if __name__ == "__main__":
    # 示例数据：5 个样本 × 4 个指标
    matrix = np.array([
        [85, 90, 78, 92],
        [76, 88, 82, 85],
        [90, 75, 88, 90],
        [82, 85, 90, 88],
        [88, 92, 75, 80],
    ])

    criteria = ['Efficiency', 'Cost', 'Reliability', 'Eco-score']

    weights, entropy = entropy_weight(matrix)

    print("===== 熵权法结果 =====")
    for i, name in enumerate(criteria):
        print(f"{name}: entropy = {entropy[i]:.4f}, weight = {weights[i]:.4f}")
    print(f"权重和 = {weights.sum():.4f}")
