"""
TOPSIS（逼近理想解排序法）模板
适用：多指标综合评价、已有数据和权重
问题适配：修改 decision_matrix 和 weights
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def topsis(matrix, weights, indicator_types):
    """
    TOPSIS 法

    Parameters:
        matrix: np.ndarray, (n_alternatives, n_criteria) 决策矩阵
        weights: np.ndarray, (n_criteria,) 指标权重（和=1）
        indicator_types: list, 每个指标的类别：
            'pos' — 极大型（越大越好）
            'neg' — 极小型（越小越好）
            'mid' — 中间型（tuple: (best_value, tolerance)）
            'interval' — 区间型（tuple: (low, high, tolerance)）

    Returns:
        C: np.ndarray, 各方案的相对贴近度
        ranking: np.ndarray, 排名（1-based）
    """
    n_alt, n_crit = matrix.shape
    X = matrix.astype(float).copy()

    # Step 1: 正向化
    for j in range(n_crit):
        itype = indicator_types[j]
        if itype == 'neg':
            X[:, j] = X[:, j].max() - X[:, j]
        elif isinstance(itype, tuple) and itype[0] == 'mid':
            best, tol = itype[1], itype[2] if len(itype) > 2 else 0.1
            M = np.max(np.abs(X[:, j] - best))
            X[:, j] = 1 - np.abs(X[:, j] - best) / M if M > 0 else X[:, j]
        elif isinstance(itype, tuple) and itype[0] == 'interval':
            low, high, tol = itype[1], itype[2], itype[3] if len(itype) > 3 else 0.1
            M = max(low - X[:, j].min(), X[:, j].max() - high)
            for i in range(n_alt):
                if X[i, j] < low:
                    X[i, j] = 1 - (low - X[i, j]) / M if M > 0 else 1
                elif X[i, j] > high:
                    X[i, j] = 1 - (X[i, j] - high) / M if M > 0 else 1
                else:
                    X[i, j] = 1

    # Step 2: 向量归一化
    Z = X / np.sqrt((X ** 2).sum(axis=0))

    # Step 3: 加权矩阵
    V = Z * weights

    # Step 4: 正负理想解
    V_plus = V.max(axis=0)
    V_minus = V.min(axis=0)

    # Step 5: 距离
    D_plus = np.sqrt(((V - V_plus) ** 2).sum(axis=1))
    D_minus = np.sqrt(((V - V_minus) ** 2).sum(axis=1))

    # Step 6: 相对贴近度
    C = D_minus / (D_plus + D_minus + 1e-10)

    # 排名
    ranking = C.argsort()[::-1].argsort() + 1

    return C, ranking


def plot_topsis_results(alternatives, C):
    """TOPSIS 结果可视化"""
    sorted_idx = C.argsort()[::-1]
    alt_sorted = [alternatives[i] for i in sorted_idx]
    C_sorted = C[sorted_idx]

    plt.figure(figsize=(8, 5))
    colors = plt.cm.RdYlGn(C_sorted)
    plt.barh(range(len(alt_sorted)), C_sorted, color=colors, edgecolor='gray')
    plt.yticks(range(len(alt_sorted)), alt_sorted)
    plt.xlabel('Relative Closeness (C)')
    plt.title('TOPSIS Results')
    for i, v in enumerate(C_sorted):
        plt.text(v + 0.01, i, f'{v:.4f}', va='center')
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # ===== 示例数据 =====
    alternatives = ['Scheme A', 'Scheme B', 'Scheme C', 'Scheme D']

    # 决策矩阵：4 个方案 × 4 个指标
    # 指标：成本(越小越好), 效率(越大越好), 可靠性(越大越好), 环保度(越大越好)
    matrix = np.array([
        [100, 85, 0.95, 80],
        [120, 92, 0.88, 75],
        [95,  78, 0.92, 90],
        [110, 88, 0.90, 85],
    ])

    # 权重（熵权法计算或主观给定）
    weights = np.array([0.25, 0.30, 0.25, 0.20])

    # 指标类型
    indicator_types = ['neg', 'pos', 'pos', 'pos']

    C, ranking = topsis(matrix, weights, indicator_types)

    print("===== TOPSIS 评价结果 =====")
    for i, alt in enumerate(alternatives):
        print(f"{alt}: C = {C[i]:.4f}, Ranking = {ranking[i]}")

    plot_topsis_results(alternatives, C)
