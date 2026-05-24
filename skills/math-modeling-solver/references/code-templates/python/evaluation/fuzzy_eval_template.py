"""
模糊综合评价模板
适用：含定性/模糊指标的评价问题
"""

import numpy as np


def triangular_mf(x, a, b, c):
    """三角隶属函数"""
    if x <= a or x >= c:
        return 0.0
    elif a < x <= b:
        return (x - a) / (b - a + 1e-10)
    else:  # b < x < c
        return (c - x) / (c - b + 1e-10)


def trapezoid_mf(x, a, b, c, d):
    """梯形隶属函数"""
    if x <= a or x >= d:
        return 0.0
    elif b <= x <= c:
        return 1.0
    elif a < x < b:
        return (x - a) / (b - a + 1e-10)
    else:  # c < x < d
        return (d - x) / (d - c + 1e-10)


def fuzzy_evaluate(indicators, weights, membership_funcs, grades):
    """
    模糊综合评价

    Parameters:
        indicators: np.ndarray, 指标值 (n_criteria,)
        weights: np.ndarray, 权重 (n_criteria,)
        membership_funcs: list of callable, 每个指标的隶属函数
            func(value) -> np.ndarray of shape (n_grades,)
        grades: list, 评语等级名称

    Returns:
        B: 综合隶属度向量
        result: 加权平均去模糊化后的等级索引
        grade_value: 加权平均得分
    """
    n_crit = len(indicators)
    n_grades = len(grades)

    # 构建隶属度矩阵 R (n_crit × n_grades)
    R = np.zeros((n_crit, n_grades))
    for i in range(n_crit):
        R[i, :] = membership_funcs[i](indicators[i])

    # 模糊合成 M(·,+)
    B = weights @ R

    # 去模糊化：加权平均法
    grade_scores = np.arange(1, n_grades + 1)
    grade_score = np.dot(B, grade_scores)

    # 最大隶属度原则
    result = np.argmax(B)

    return B, result, grade_score


if __name__ == "__main__":
    # ===== 示例：评价某系统的综合表现 =====
    grades = ['Very Poor', 'Poor', 'Fair', 'Good', 'Excellent']

    # 例：指标值
    indicators = np.array([78, 0.85, 3.2])

    # 各指标的隶属函数（输出长度为 n_grades 的向量）
    def mf_indicator1(x):
        """指标1（连续值 → 5 个等级的隶属度）"""
        return np.array([
            triangular_mf(x, -np.inf, 20, 50),   # Very Poor
            triangular_mf(x, 20, 50, 70),         # Poor
            triangular_mf(x, 50, 70, 85),         # Fair
            triangular_mf(x, 70, 85, 95),         # Good
            triangular_mf(x, 85, 100, np.inf),    # Excellent
        ])

    def mf_indicator2(x):
        """指标2（比例 → 隶属度）"""
        return np.array([
            trapezoid_mf(x, -np.inf, -np.inf, 0.3, 0.5),
            trapezoid_mf(x, 0.3, 0.5, 0.6, 0.7),
            trapezoid_mf(x, 0.6, 0.7, 0.8, 0.85),
            trapezoid_mf(x, 0.8, 0.85, 0.9, 0.95),
            trapezoid_mf(x, 0.9, 0.95, np.inf, np.inf),
        ])

    def mf_indicator3(x):
        """指标3"""
        return np.array([
            triangular_mf(x, -np.inf, 1, 2),
            triangular_mf(x, 1, 2, 3),
            triangular_mf(x, 2, 3, 4),
            triangular_mf(x, 3, 4, 5),
            triangular_mf(x, 4, 5, np.inf),
        ])

    membership_funcs = [mf_indicator1, mf_indicator2, mf_indicator3]
    weights = np.array([0.35, 0.35, 0.30])

    B, result, grade_score = fuzzy_evaluate(indicators, weights, membership_funcs, grades)

    print("===== 模糊综合评价结果 =====")
    for i, g in enumerate(grades):
        bar = '█' * int(B[i] * 40)
        print(f"{g:12s}: {B[i]:.4f} {bar}")
    print(f"\n最大隶属度: {grades[result]} (第 {result+1} 级)")
    print(f"加权平均得分: {grade_score:.2f} / {len(grades)}")
