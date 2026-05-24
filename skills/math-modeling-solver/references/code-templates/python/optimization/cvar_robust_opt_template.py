"""
CVaR 稳健优化 (Conditional Value-at-Risk Robust Optimization) 模板
适用：投资组合优化、风险管理、不确定性下的鲁棒决策
参考：Rockafellar & Uryasev (2000, 2002) — CVaR 线性规划公式

问题适配点：
  1. 修改 _load_scenarios() —— 替换为实际场景数据（历史样本或自定义分布采样）
  2. 修改 _asset_returns() —— 如已有收益率场景则直接使用
  3. 调整 r_targets —— 目标收益范围，用于绘制有效前沿
  4. 如非投资组合问题，修改损失函数定义（loss = -return 适用于最大化收益）
  5. 调整约束条件（如权重上下界、行业集中度等）见 optimize_cvar() 内注释
"""

import numpy as np
from scipy.optimize import linprog
import matplotlib.pyplot as plt
from typing import Tuple, Optional

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class CVaRPortfolio:
    """CVaR 投资组合优化框架"""

    def __init__(self, n_assets: int = 5, n_scenarios: int = 1000,
                 random_seed: Optional[int] = 42):
        """
        Parameters
        ----------
        n_assets : 资产数量
        n_scenarios : 场景数量（历史样本数或蒙特卡洛抽样数）
        random_seed : 随机种子
        """
        self.n_assets = n_assets
        self.n_scenarios = n_scenarios
        self.rng = np.random.default_rng(random_seed)
        self.scenarios: Optional[np.ndarray] = None  # shape (n_scenarios, n_assets)
        self.weights: Optional[np.ndarray] = None
        self.var: Optional[float] = None
        self.cvar: Optional[float] = None

    def _load_scenarios(self) -> np.ndarray:
        """
        生成/加载收益率场景矩阵。

        实际应用中，可从历史数据、多元正态抽样、或 GARCH/COPULA 生成场景。
        返回 shape (n_scenarios, n_assets) 的收益率矩阵（每行一个场景）。

        Returns
        -------
        scenarios : np.ndarray, shape (n_scenarios, n_assets)
        """
        # TODO: 替换为实际问题的场景数据
        # 示例：多元正态分布，均值和协方差为随机生成
        means = self.rng.uniform(0.05, 0.20, self.n_assets)  # 年化收益率 5%-20%
        # 随机生成正定协方差矩阵
        A = self.rng.standard_normal((self.n_assets, self.n_assets))
        cov = A @ A.T + self.n_assets * np.eye(self.n_assets)
        vols = np.sqrt(np.diag(cov))
        # 调整波动率到合理范围
        cov = cov / np.outer(vols, vols) * np.outer(vols, vols)  # 保持相关性
        for i in range(self.n_assets):
            cov[i, i] = (self.rng.uniform(0.15, 0.40)) ** 2  # 波动率 15%-40%

        scenarios = self.rng.multivariate_normal(means, cov, self.n_scenarios)
        return scenarios

    def _compute_losses(self, scenarios: np.ndarray,
                         weights: np.ndarray) -> np.ndarray:
        """
        计算各场景下的损失（负收益）。

        Parameters
        ----------
        scenarios : shape (n_scenarios, n_assets) 收益率矩阵
        weights : shape (n_assets,) 资产权重

        Returns
        -------
        losses : shape (n_scenarios,) 各场景损失
        """
        portfolio_returns = scenarios @ weights
        losses = -portfolio_returns  # 损失 = 负收益
        return losses

    def optimize_cvar(self, scenarios: np.ndarray,
                      alpha: float = 0.05,
                      target_return: Optional[float] = None) -> Tuple[np.ndarray, float, float]:
        """
        CVaR 最小化线性规划（Rockafellar-Uryasev 公式）。

        约束：权重之和=1，允许卖空与否见 weight_bounds 参数。
        可选：加入目标收益约束（用于画有效前沿）。

        Parameters
        ----------
        scenarios : shape (n_scenarios, n_assets) 收益率矩阵
        alpha : CVaR 置信水平（如 0.05 表示 95% 置信度）
        target_return : 最低期望收益约束（None 表示无约束）

        Returns
        -------
        weights : shape (n_assets,) 最优权重
        var : 在险价值 VaR
        cvar : 条件在险价值 CVaR
        """
        n = self.n_scenarios
        m = self.n_assets

        # 辅助变量：w (weights m个), z (auxiliary n个), ζ (VaR, 1个)
        # 变量顺序：[w_0, ..., w_{m-1}, z_0, ..., z_{n-1}, zeta]
        n_vars = m + n + 1

        # 目标：CVaR = ζ + (1/(n*alpha)) * sum(z_k)
        c = np.zeros(n_vars)
        c[-1] = 1.0  # zeta 系数
        c[m:-1] = 1.0 / (n * alpha)  # z_k 系数

        # 约束1: z_k >= loss_k - ζ (线性化用 n 个不等式)
        # loss_k = -sum_j scenarios[k,j] * w_j
        # z_k + sum_j scenarios[k,j] * w_j + ζ >= 0
        # z_k >= -sum_j scenarios[k,j] * w_j - ζ
        A_ub = np.zeros((n, n_vars))
        for k in range(n):
            A_ub[k, :m] = -scenarios[k, :]  # -(-r_k) = +r_k，但这里 z_k >= loss_k - ζ
            A_ub[k, m + k] = 1.0  # z_k
            A_ub[k, -1] = 1.0  # ζ
        b_ub = np.zeros(n)

        # 约束2: z_k >= 0
        bounds = [(None, None)] * m + [(0, None)] * n + [(None, None)]  # zeta 自由

        # TODO: 修改权重上下界。
        # 例如 bounds[:m] = [(0, 1)] * m  代表不允许卖空
        # 或 bounds[:m] = [(0, 0.3)] * m  代表单一资产最多30%

        # 约束3: sum(w) = 1
        A_eq = np.zeros((1, n_vars))
        A_eq[0, :m] = 1.0
        b_eq = np.array([1.0])

        # 可选：期望收益约束
        if target_return is not None:
            mu = scenarios.mean(axis=0)
            extra_row = np.zeros((1, n_vars))
            extra_row[0, :m] = mu
            A_eq = np.vstack([A_eq, extra_row])
            b_eq = np.append(b_eq, target_return)

        # 求解线性规划
        result = linprog(c, A_ub=A_ub, b_ub=b_ub,
                         A_eq=A_eq, b_eq=b_eq,
                         bounds=bounds,
                         method='highs')

        if not result.success:
            raise RuntimeError(f"CVaR 优化失败: {result.message}")

        weights = result.x[:m]
        zeta = result.x[-1]  # VaR
        cvar_val = result.fun  # CVaR

        return weights, zeta, cvar_val

    def compute_var_cvar(self, losses: np.ndarray,
                         alpha: float = 0.05) -> Tuple[float, float]:
        """
        从损失分布直接计算 VaR 和 CVaR。

        Parameters
        ----------
        losses : shape (n_scenarios,) 损失序列
        alpha : 置信水平

        Returns
        -------
        var : VaR
        cvar : CVaR (超出 VaR 的期望损失)
        """
        sorted_losses = np.sort(losses)
        var_idx = int(np.ceil((1 - alpha) * len(sorted_losses))) - 1
        var_idx = max(0, min(var_idx, len(sorted_losses) - 1))
        var = sorted_losses[var_idx]
        cvar = sorted_losses[var_idx:].mean()
        return var, cvar

    def efficient_frontier(self, scenarios: np.ndarray,
                           alpha: float = 0.05,
                           n_points: int = 20,
                           r_min: Optional[float] = None,
                           r_max: Optional[float] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        计算均值-CVaR 有效前沿。

        Parameters
        ----------
        scenarios : shape (n_scenarios, n_assets) 收益率矩阵
        alpha : CVaR 置信水平
        n_points : 前沿上的点数
        r_min, r_max : 目标收益范围，不提供则自动计算

        Returns
        -------
        returns : shape (n_points,) 组合收益
        cvars : shape (n_points,) 对应的 CVaR
        """
        mu = scenarios.mean(axis=0)
        w_eq = np.ones(self.n_assets) / self.n_assets
        if r_min is None:
            r_min = mu.min()
        if r_max is None:
            r_max = mu.max() * 0.95

        targets = np.linspace(r_min, r_max, n_points)
        cvars_opt = np.zeros(n_points)
        returns_opt = np.zeros(n_points)

        for i, r_target in enumerate(targets):
            try:
                w_opt, var_opt, cvar_opt = self.optimize_cvar(
                    scenarios, alpha, target_return=r_target)
                cvars_opt[i] = cvar_opt
                returns_opt[i] = scenarios.mean(axis=0) @ w_opt
            except RuntimeError:
                cvars_opt[i] = np.nan
                returns_opt[i] = np.nan

        return returns_opt, cvars_opt

    def plot_loss_distribution(self, losses: np.ndarray,
                               var: float, cvar: float, alpha: float = 0.05,
                               save_path: Optional[str] = None):
        """绘制损失分布 + VaR/CVaR 标记"""
        fig, ax = plt.subplots(figsize=(9, 5))

        ax.hist(losses, bins=60, density=True, alpha=0.6,
                color='steelblue', edgecolor='white')
        kde_x = np.linspace(losses.min(), losses.max(), 300)
        from scipy import stats
        kde = stats.gaussian_kde(losses)
        ax.plot(kde_x, kde(kde_x), 'navy', lw=2, label='KDE 估计')

        ax.axvline(var, color='red', linestyle='--', lw=2,
                   label=f'VaR ({1-alpha:.0%}): {var:.4f}')
        ax.axvline(cvar, color='darkred', linestyle='-', lw=2,
                   label=f'CVaR ({1-alpha:.0%}): {cvar:.4f}')

        # 阴影超出 VaR 的尾部区域
        ax.fill_between(kde_x[kde_x >= var], 0,
                         kde(kde_x[kde_x >= var]),
                         color='red', alpha=0.15, label=f'超出 VaR ({alpha:.0%})')

        ax.set_xlabel('损失 (Loss = -Return)')
        ax.set_ylabel('概率密度')
        ax.set_title(f'投资组合损失分布与 VaR/CVaR (alpha={alpha})')
        ax.legend(loc='upper right')
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.show()

    def plot_efficient_frontier(self, returns: np.ndarray,
                                 cvars: np.ndarray,
                                 save_path: Optional[str] = None):
        """绘制均值-CVaR 有效前沿"""
        fig, ax = plt.subplots(figsize=(7, 5))

        valid = ~np.isnan(cvars) & ~np.isnan(returns)
        ax.plot(cvars[valid], returns[valid], 'b-o', markersize=5, lw=1.5)
        ax.set_xlabel('CVaR (条件在险价值)')
        ax.set_ylabel('期望收益')
        ax.set_title('均值-CVaR 有效前沿')
        ax.grid(True, alpha=0.3)

        # 标注最小 CVaR 点
        min_idx = np.nanargmin(cvars)
        ax.plot(cvars[min_idx], returns[min_idx], 'r*',
                markersize=14, label=f'最小 CVaR (收益={returns[min_idx]:.4f})')
        ax.legend()

        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.show()


# ===== 使用示例 =====
if __name__ == "__main__":
    print("=== CVaR 稳健优化示例 ===\n")

    # TODO: 修改参数为实际问题设定
    cvar_pf = CVaRPortfolio(n_assets=5, n_scenarios=1000, random_seed=42)
    scenarios = cvar_pf._load_scenarios()

    print(f"场景矩阵: {scenarios.shape}")
    print(f"各资产均值收益: {scenarios.mean(axis=0)}")
    print(f"各资产波动率: {scenarios.std(axis=0)}\n")

    # 1) CVaR 最优化
    w_opt, var_opt, cvar_opt = cvar_pf.optimize_cvar(scenarios, alpha=0.05)

    print("===== 最小 CVaR 组合 =====")
    for i, wi in enumerate(w_opt):
        print(f"  资产 {i+1}: 权重 = {wi:.4f}")
    print(f"  VaR (95%): {var_opt:.6f}")
    print(f"  CVaR (95%): {cvar_opt:.6f}")
    print(f"  期望收益: {scenarios.mean(axis=0) @ w_opt:.6f}\n")

    # 2) 损失分布可视化
    losses = cvar_pf._compute_losses(scenarios, w_opt)
    l_var, l_cvar = cvar_pf.compute_var_cvar(losses, alpha=0.05)
    cvar_pf.plot_loss_distribution(losses, l_var, l_cvar, alpha=0.05)

    # 3) 有效前沿
    returns_f, cvars_f = cvar_pf.efficient_frontier(scenarios, alpha=0.05, n_points=15)
    cvar_pf.plot_efficient_frontier(returns_f, cvars_f)
