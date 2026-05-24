"""
灰色关联分析 (Grey Relational Analysis, GRA) 模板
适用：小样本、贫信息的多指标综合评价
参考：Deng Julong (1989) — 灰色系统理论

问题适配点：
  1. 修改 data_matrix —— 替换为实际评价数据（行=方案, 列=指标）
  2. 修改 indicator_types —— 每个指标的方向：'pos'(越大越好) 或 'neg'(越小越好)
  3. 修改 reference_type —— 'manual' 手动指定参考序列, 'auto' 自动取最优值
  4. 调整 rho —— 分辨系数（通常 0.5，数据噪声大时可适当增大）
  5. 如需加权，修改 weights 或在 _calculate_grades 中传入
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class GreyRelationalAnalysis:
    """灰色关联分析框架"""

    def __init__(self, data_matrix: np.ndarray,
                 indicator_types: List[str],
                 rho: float = 0.5):
        """
        Parameters
        ----------
        data_matrix : shape (n_alternatives, n_indicators) 原始数据矩阵
        indicator_types : 各指标方向，'pos' 或 'neg'
        rho : 分辨系数，默认 0.5
        """
        self.X_raw = np.array(data_matrix, dtype=float)
        self.n_alt, self.n_ind = self.X_raw.shape
        self.indicator_types = indicator_types
        self.rho = rho

        self.X_norm: Optional[np.ndarray] = None   # 归一化后矩阵
        self.ref_seq: Optional[np.ndarray] = None   # 参考序列
        self.xi: Optional[np.ndarray] = None         # 关联系数矩阵
        self.grades: Optional[np.ndarray] = None     # 关联度

    def normalize(self, method: str = 'minmax'):
        """
        数据归一化（Min-Max 方法，同时处理指标方向）。

        对于 'pos' 指标：x_norm = (x - min) / (max - min)
        对于 'neg' 指标：x_norm = (max - x) / (max - min)
        """
        X = self.X_raw.copy()
        X_norm = np.zeros_like(X)

        for j in range(self.n_ind):
            col = X[:, j]
            col_min, col_max = col.min(), col.max()
            denom = col_max - col_min
            if denom == 0:
                X_norm[:, j] = 1.0  # 所有方案相同 → 归一化为1
            else:
                if self.indicator_types[j] == 'pos':
                    X_norm[:, j] = (col - col_min) / denom
                else:  # 'neg'
                    X_norm[:, j] = (col_max - col) / denom

        self.X_norm = X_norm
        return X_norm

    def set_reference(self, ref_type: str = 'auto',
                      manual_ref: Optional[np.ndarray] = None):
        """
        设定参考序列（理想方案）。

        Parameters
        ----------
        ref_type : 'auto' 自动取每个指标的最优值（1.0），
                   'manual' 手动指定
        manual_ref : 手动参考序列（需与指标数一致）
        """
        if self.X_norm is None:
            self.normalize()

        if ref_type == 'auto':
            self.ref_seq = np.ones(self.n_ind)  # 归一化后最优值 = 1
        elif ref_type == 'manual' and manual_ref is not None:
            self.ref_seq = np.array(manual_ref, dtype=float)
        else:
            raise ValueError("ref_type 必须为 'auto' 或 'manual'（且提供 manual_ref）")

        # TODO: 若需自定义参考序列，传 ref_type='manual' 和具体值
        return self.ref_seq

    def calculate_coefficients(self) -> np.ndarray:
        """
        计算灰色关联系数（Deng 氏公式）。

        xi_{ij} = (delta_min + rho * delta_max) / (delta_ij + rho * delta_max)

        Returns
        -------
        xi : shape (n_alt, n_ind) 关联系数矩阵
        """
        if self.ref_seq is None:
            self.set_reference()

        delta = np.abs(self.X_norm - self.ref_seq)  # 绝对差矩阵
        delta_min = delta.min()
        delta_max = delta.max()

        if delta_max == 0:
            self.xi = np.ones_like(delta)
        else:
            self.xi = (delta_min + self.rho * delta_max) / (delta + self.rho * delta_max)

        return self.xi

    def calculate_grades(self, weights: Optional[np.ndarray] = None) -> np.ndarray:
        """
        计算灰色关联度（各方案与参考序列的综合关联程度）。

        Parameters
        ----------
        weights : 各指标权重，shape (n_ind,) 或 None（等权重）

        Returns
        -------
        grades : shape (n_alt,) 关联度，越大越优
        """
        if self.xi is None:
            self.calculate_coefficients()

        if weights is None:
            weights = np.ones(self.n_ind) / self.n_ind

        # TODO: 可替换为熵权法、AHP 等权重确定方法
        self.grades = self.xi @ weights
        return self.grades

    def ranking(self) -> np.ndarray:
        """
        获取排序结果。

        Returns
        -------
        ranks : shape (n_alt,) 基于关联度的排名（1=最优）
        """
        if self.grades is None:
            self.calculate_grades()
        return self.grades.argsort()[::-1].argsort() + 1

    def summary(self, alternative_names: Optional[List[str]] = None) -> pd.DataFrame:
        """输出汇总表"""
        if alternative_names is None:
            alternative_names = [f'方案 {i+1}' for i in range(self.n_alt)]

        if self.grades is None:
            self.calculate_grades()

        ranks = self.ranking()
        df = pd.DataFrame({
            '方案': alternative_names,
            '关联度': self.grades,
            '排名': ranks.astype(int),
        })
        df = df.sort_values('排名').reset_index(drop=True)
        return df

    def plot_heatmap(self, alternative_names: Optional[List[str]] = None,
                     indicator_names: Optional[List[str]] = None,
                     save_path: Optional[str] = None):
        """关联系数热力图"""
        if self.xi is None:
            self.calculate_coefficients()

        if alternative_names is None:
            alternative_names = [f'Scheme {i+1}' for i in range(self.n_alt)]
        if indicator_names is None:
            indicator_names = [f'Indicator {j+1}' for j in range(self.n_ind)]

        fig, ax = plt.subplots(figsize=(8, 5))
        im = ax.imshow(self.xi, cmap='YlOrRd', aspect='auto', vmin=0, vmax=1)

        for i in range(self.n_alt):
            for j in range(self.n_ind):
                ax.text(j, i, f'{self.xi[i, j]:.3f}', ha='center',
                        va='center', fontsize=9,
                        color='white' if self.xi[i, j] < 0.6 else 'black')

        ax.set_xticks(range(self.n_ind))
        ax.set_xticklabels(indicator_names, rotation=30, ha='right')
        ax.set_yticks(range(self.n_alt))
        ax.set_yticklabels(alternative_names)
        ax.set_title('灰色关联系数矩阵 (rho={})'.format(self.rho))
        plt.colorbar(im, ax=ax, shrink=0.8, label='关联系数')
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.show()

    def plot_grades(self, alternative_names: Optional[List[str]] = None,
                    save_path: Optional[str] = None):
        """关联度柱状图"""
        if self.grades is None:
            self.calculate_grades()

        if alternative_names is None:
            alternative_names = [f'方案 {i+1}' for i in range(self.n_alt)]

        sorted_idx = self.grades.argsort()
        grades_sorted = self.grades[sorted_idx]
        names_sorted = [alternative_names[i] for i in sorted_idx]

        fig, ax = plt.subplots(figsize=(8, 4))
        colors = plt.cm.RdYlGn(np.linspace(0.3, 1, len(grades_sorted)))
        ax.barh(range(len(names_sorted)), grades_sorted, color=colors, edgecolor='gray')
        ax.set_yticks(range(len(names_sorted)))
        ax.set_yticklabels(names_sorted)
        ax.set_xlabel('关联度')
        ax.set_title('灰色关联度对比')
        for i, v in enumerate(grades_sorted):
            ax.text(v + 0.01, i, f'{v:.4f}', va='center')
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.show()


# ===== 使用示例 =====
if __name__ == "__main__":
    print("=== 灰色关联分析示例 ===\n")

    # TODO: 替换为实际问题的评价数据
    # 5 个方案，4 个指标
    alt_names = ['方案 A', '方案 B', '方案 C', '方案 D', '方案 E']
    ind_names = ['生产效率', '成本', '可靠性', '环保指数']

    # 原始数据：每行一个方案，每列一个指标
    data_matrix = np.array([
        [85, 120, 0.92, 78],
        [72, 95,  0.85, 88],
        [90, 110, 0.95, 72],
        [68, 80,  0.78, 95],
        [78, 105, 0.88, 82],
    ])

    # 成本为 'neg'（越小越好），其余为 'pos'
    indicator_types = ['pos', 'neg', 'pos', 'pos']

    gra = GreyRelationalAnalysis(data_matrix, indicator_types, rho=0.5)

    # 归一化
    gra.normalize()
    print("归一化矩阵:\n", pd.DataFrame(gra.X_norm, columns=ind_names, index=alt_names).round(4), "\n")

    # 关联系数
    xi = gra.calculate_coefficients()
    print("关联系数矩阵:\n", pd.DataFrame(xi, columns=ind_names, index=alt_names).round(4), "\n")

    # 关联度 & 排名
    grades = gra.calculate_grades()  # 等权重
    ranks = gra.ranking()

    print("===== 灰色关联分析结果 =====")
    for i, name in enumerate(alt_names):
        print(f"  {name}: 关联度 = {grades[i]:.4f}, 排名 = {ranks[i]}")

    # 汇总表
    print("\n", gra.summary(alt_names).to_string(index=False))

    # 可视化
    gra.plot_heatmap(alt_names, ind_names)
    gra.plot_grades(alt_names)
