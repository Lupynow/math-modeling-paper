"""
方差分析 (ANOVA) 模板
适用：多组均值差异检验、因素显著性分析、实验设计分析

问题适配点：
  1. 修改 _load_data() —— 替换为实际分组数据（CSV/实验数据）
  2. 修改 one_way 的 groups —— 替换为实际分组列表
  3. 修改 two_way 的 data —— 替换为实际两因素数据（带分组标签）
  4. 如不满足正态性/方差齐性，结果会自动提示使用 Kruskal-Wallis
  5. 如有多个因变量，考虑 MANOVA 或多重比较校正（Bonferroni）
"""

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import matplotlib.pyplot as plt
from typing import List, Optional, Tuple, Dict

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class ANOVAAnalyzer:
    """方差分析框架"""

    def __init__(self):
        self.oneway_result: Optional[dict] = None
        self.twoway_result: Optional[dict] = None
        self.posthoc_result: Optional[pd.DataFrame] = None

    @staticmethod
    def _load_data() -> Dict[str, np.ndarray]:
        """加载/生成分组数据"""
        # TODO: 替换为实际数据加载
        rng = np.random.default_rng(42)
        return {
            '对照组': rng.normal(loc=50, scale=5, size=30),
            '处理组A': rng.normal(loc=55, scale=5, size=30),
            '处理组B': rng.normal(loc=62, scale=6, size=30),
        }

    def shapiro_wilk(self, groups: Dict[str, np.ndarray],
                     verbose: bool = True) -> Dict[str, Tuple[float, float]]:
        """
        正态性检验（Shapiro-Wilk）。p > 0.05 表示不能拒绝正态分布原假设。

        Returns
        -------
        {组名: (W统计量, p值)}
        """
        results = {}
        for name, data in groups.items():
            w, p = stats.shapiro(data)
            results[name] = (w, p)
            if verbose:
                status = '正态 ✓' if p > 0.05 else '非正态 ✗'
                print(f"  {name}: W={w:.4f}, p={p:.4f}  ({status})")
        return results

    def levene(self, groups: Dict[str, np.ndarray],
               center: str = 'median',
               verbose: bool = True) -> Tuple[float, float]:
        """
        方差齐性检验（Levene）。p > 0.05 表示不能拒绝方差齐性原假设。

        Parameters
        ----------
        center : 'median'（推荐, 更稳健）或 'mean'
        """
        data_list = list(groups.values())
        stat, p = stats.levene(*data_list, center=center)
        if verbose:
            status = '方差齐性 ✓' if p > 0.05 else '方差不齐 ✗'
            print(f"Levene 检验: stat={stat:.4f}, p={p:.4f}  ({status})")
        return stat, p

    def one_way(self, groups: Dict[str, np.ndarray],
                verbose: bool = True) -> Dict:
        """
        单因素方差分析。

        同时计算 eta-squared 效应量：
        - eta^2 = SS_between / SS_total
        - 小效应 0.01, 中效应 0.06, 大效应 0.14 (Cohen)

        Returns
        -------
        result : dict，含 'F', 'p_value', 'eta_squared', 'significant'
        """
        # TODO: 替换 groups 为实际问题分组
        data_list = list(groups.values())
        F_stat, p_value = stats.f_oneway(*data_list)

        # 计算 eta-squared
        all_data = np.concatenate(data_list)
        grand_mean = all_data.mean()
        ss_total = np.sum((all_data - grand_mean) ** 2)
        ss_between = sum(len(g) * (g.mean() - grand_mean) ** 2
                         for g in data_list)
        eta_sq = ss_between / ss_total if ss_total > 0 else 0

        self.oneway_result = {
            'F': F_stat,
            'p_value': p_value,
            'eta_squared': eta_sq,
            'significant': p_value < 0.05,
            'df_between': len(data_list) - 1,
            'df_within': len(all_data) - len(data_list),
            'ss_between': ss_between,
            'ss_total': ss_total,
        }

        if verbose:
            print(f"\n===== 单因素方差分析 =====")
            print(f"  F({self.oneway_result['df_between']}, "
                  f"{self.oneway_result['df_within']}) = {F_stat:.4f}")
            print(f"  p-value = {p_value:.4f}"
                  f"{' ***' if p_value < 0.001 else ' **' if p_value < 0.01 else ' *' if p_value < 0.05 else ''}")
            print(f"  eta-squared = {eta_sq:.4f} (效应量)")

        return self.oneway_result

    def two_way(self, data: pd.DataFrame,
                formula: str = 'value ~ C(factor_A) + C(factor_B) + C(factor_A):C(factor_B)',
                verbose: bool = True) -> Dict:
        """
        两因素方差分析（含交互作用）。

        Parameters
        ----------
        data : DataFrame，包含 'value', 'factor_A', 'factor_B' 列
        formula : statsmodels 公式
        """
        # TODO: 替换 data 为实际数据，调整 formula
        model = ols(formula, data=data).fit()
        anova_table = sm.stats.anova_lm(model, typ=2)

        self.twoway_result = {
            'anova_table': anova_table,
            'model': model,
        }

        if verbose:
            print(f"\n===== 两因素方差分析 =====")
            print(anova_table.round(4).to_string())

        return self.twoway_result

    def post_hoc_tukey(self, data: np.ndarray, groups: np.ndarray,
                       alpha: float = 0.05,
                       verbose: bool = True) -> pd.DataFrame:
        """
        Tukey HSD 事后多重比较。

        Parameters
        ----------
        data : 所有观测值（拼接为一维数组）
        groups : 对应的分组标签（与 data 等长）
        alpha : 显著性水平
        """
        tukey = pairwise_tukeyhsd(data, groups, alpha=alpha)
        self.posthoc_result = pd.DataFrame(data=tukey.summary().data[1:],
                                           columns=tukey.summary().data[0])

        if verbose:
            print(f"\n===== Tukey HSD 事后检验 (alpha={alpha}) =====")
            print(self.posthoc_result.to_string(index=False))

        return self.posthoc_result

    def kruskal_wallis(self, groups: Dict[str, np.ndarray],
                       verbose: bool = True) -> Dict:
        """
        非参数替代：Kruskal-Wallis H 检验（不要求正态性和方差齐性）。

        Returns
        -------
        result : dict，含 'H', 'p_value', 'significant'
        """
        # TODO: 当正态性或方差齐性不满足时，使用此方法替代单因素 ANOVA
        data_list = list(groups.values())
        H_stat, p_value = stats.kruskal(*data_list)

        result = {'H': H_stat, 'p_value': p_value,
                  'significant': p_value < 0.05}

        if verbose:
            print(f"\n===== Kruskal-Wallis 检验 =====")
            print(f"  H = {H_stat:.4f}, p = {p_value:.4f}"
                  f"{' ***' if p_value < 0.001 else ' **' if p_value < 0.01 else ' *' if p_value < 0.05 else ''}")

        return result

    def plot_boxplot(self, groups: Dict[str, np.ndarray],
                     title: str = '分组箱线图',
                     save_path: Optional[str] = None):
        """各组箱线图可视化"""
        names = list(groups.keys())
        data_list = [groups[name] for name in names]

        fig, ax = plt.subplots(figsize=(8, 5))
        bp = ax.boxplot(data_list, labels=names, patch_artist=True,
                         showmeans=True, meanprops=dict(marker='D',
                                                        markerfacecolor='red',
                                                        markersize=6))

        colors = plt.cm.Set2(np.linspace(0, 1, len(names)))
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)

        # 叠加原始数据点
        for i, (name, d) in enumerate(groups.items()):
            jitter = np.random.default_rng(0).uniform(-0.15, 0.15, len(d))
            ax.scatter(np.full_like(d, i + 1) + jitter, d, alpha=0.4,
                       s=20, edgecolors='gray', linewidth=0.5)

        ax.set_xlabel('组别')
        ax.set_ylabel('观测值')
        ax.set_title(title)
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.show()

    def plot_qq(self, data: np.ndarray,
                title: str = 'Q-Q 图 (正态性检验)',
                save_path: Optional[str] = None):
        """Q-Q 图辅助判断正态性"""
        fig, ax = plt.subplots(figsize=(5, 5))
        stats.probplot(data, dist='norm', plot=ax)
        ax.get_lines()[0].set_markerfacecolor('steelblue')
        ax.get_lines()[0].set_markeredgecolor('steelblue')
        ax.get_lines()[1].set_color('red')
        ax.set_title(title)
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.show()

    def plot_residual_diagnostics(self, model_fit):
        """回归诊断图（适用于 two-way ANOVA 模型）"""
        fig, axes = plt.subplots(2, 2, figsize=(10, 8))

        # 残差 vs 拟合值
        fitted = model_fit.fittedvalues
        resid = model_fit.resid
        axes[0, 0].scatter(fitted, resid, alpha=0.6, color='steelblue')
        axes[0, 0].axhline(0, color='red', linestyle='--')
        axes[0, 0].set_xlabel('拟合值'), axes[0, 0].set_ylabel('残差')
        axes[0, 0].set_title('残差 vs 拟合值')

        # Q-Q 图
        stats.probplot(resid, dist='norm', plot=axes[0, 1])
        axes[0, 1].get_lines()[1].set_color('red')
        axes[0, 1].set_title('Q-Q 图')

        # 标准化残差直方图
        axes[1, 0].hist(resid / resid.std(), bins=20, density=True,
                         color='steelblue', alpha=0.7, edgecolor='white')
        x = np.linspace(-3, 3, 100)
        axes[1, 0].plot(x, stats.norm.pdf(x), 'r-', lw=1.5)
        axes[1, 0].set_title('标准化残差')

        # 残差 vs 顺序
        axes[1, 1].plot(resid, 'o-', color='steelblue', markersize=4)
        axes[1, 1].axhline(0, color='red', linestyle='--')
        axes[1, 1].set_xlabel('观测序号'), axes[1, 1].set_ylabel('残差')
        axes[1, 1].set_title('残差时序')

        plt.tight_layout()
        plt.show()


# ===== 使用示例 =====
if __name__ == "__main__":
    print("=== 方差分析示例 ===\n")

    analyzer = ANOVAAnalyzer()

    # ---- 单因素 ANOVA ----
    # TODO: 替换为实际分组数据
    groups = analyzer._load_data()
    print("各组描述统计:")
    for name, d in groups.items():
        print(f"  {name}: n={len(d)}, mean={np.mean(d):.2f}, std={np.std(d, ddof=1):.2f}")

    # 假设检验
    print("\n--- 正态性检验 (Shapiro-Wilk) ---")
    analyzer.shapiro_wilk(groups)

    print("\n--- 方差齐性检验 (Levene) ---")
    analyzer.levene(groups)

    # 单因素 ANOVA
    result = analyzer.one_way(groups)

    # 事后检验
    all_data = np.concatenate(list(groups.values()))
    all_labels = np.concatenate([[name] * len(d) for name, d in groups.items()])
    analyzer.post_hoc_tukey(all_data, all_labels)

    # 非参数备选（若假设不满足）
    kw = analyzer.kruskal_wallis(groups)

    # 可视化
    analyzer.plot_boxplot(groups, title='单因素 ANOVA — 各组对比')

    # ---- 两因素 ANOVA 示例 ----
    print("\n" + "=" * 50)
    print("===== 两因素 ANOVA 示例 =====\n")

    # TODO: 替换为实际问题数据
    rng = np.random.default_rng(123)
    factor_A = np.repeat(['A1', 'A2', 'A3'], 20)
    factor_B = np.tile(np.repeat(['B1', 'B2'], 10), 3)
    values = (5 * (factor_A == 'A1').astype(float) +
              8 * (factor_A == 'A2').astype(float) +
              7 * (factor_A == 'A3').astype(float) +
              3 * (factor_B == 'B2').astype(float) +
              rng.normal(0, 2, 60))

    df_two = pd.DataFrame({
        'value': values,
        'factor_A': factor_A,
        'factor_B': factor_B,
    })

    result2 = analyzer.two_way(df_two)

    # 残差诊断
    analyzer.plot_residual_diagnostics(result2['model'])
