"""
AHP（层次分析法）模板
适用：有层级结构的指标体系、专家主观赋权
"""

import numpy as np


def ahp_weight(judgment_matrix):
    """
    从判断矩阵计算权重向量 + 一致性检验

    Parameters:
        judgment_matrix: np.ndarray, 正互反判断矩阵 (n×n)

    Returns:
        weights: 归一化权重向量
        lambda_max: 最大特征值
        CR: 一致性比率
        is_consistent: 是否通过一致性检验
    """
    n = judgment_matrix.shape[0]

    # 特征值法计算权重
    eigenvalues, eigenvectors = np.linalg.eig(judgment_matrix)
    lambda_max = np.max(eigenvalues.real)
    idx = np.argmax(eigenvalues.real)
    w = np.abs(eigenvectors[:, idx].real)
    weights = w / w.sum()

    # 一致性检验
    CI = (lambda_max - n) / (n - 1)
    RI_dict = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41,
               9: 1.45, 10: 1.49, 11: 1.51, 12: 1.54, 13: 1.56, 14: 1.58, 15: 1.59}
    RI = RI_dict.get(n, 1.59)
    CR = CI / RI if RI != 0 else 0
    is_consistent = CR < 0.1

    return weights, lambda_max, CR, is_consistent


def print_ahp_result(name, weights, lambda_max, CR, is_consistent, indicators=None):
    """打印 AHP 结果"""
    print(f"\n===== {name} =====")
    print(f"λ_max = {lambda_max:.4f}")
    print(f"CI = {(lambda_max - len(weights)) / (len(weights) - 1):.4f}")
    print(f"CR = {CR:.4f} {'✓ 通过' if is_consistent else '✗ 不通过！'}")
    print("权重：")
    labels = indicators if indicators else [f"指标{i+1}" for i in range(len(weights))]
    for label, w in zip(labels, weights):
        print(f"  {label}: {w:.4f}")


if __name__ == "__main__":
    # ===== 示例：3 个准则的比较判断矩阵 =====
    # 准则：成本、效率、可靠性
    # 判断矩阵（对称位置互为倒数，对角线为 1）
    #          成本   效率   可靠性
    # 成本      1     1/3    1/5
    # 效率      3      1     1/2
    # 可靠性    5      2      1

    criteria_matrix = np.array([
        [1,     1/3,   1/5],
        [3,     1,     1/2],
        [5,     2,     1  ],
    ])

    criteria_names = ['Cost', 'Efficiency', 'Reliability']
    w, lmax, cr, ok = ahp_weight(criteria_matrix)
    print_ahp_result("准则层权重", w, lmax, cr, ok, criteria_names)

    # ===== 多层级 AHP =====
    # 准则层权重 × 方案层权重 → 综合权重
    # 如果每个准则下各有方案的两两比较矩阵，重复调用 ahp_weight 再组合
