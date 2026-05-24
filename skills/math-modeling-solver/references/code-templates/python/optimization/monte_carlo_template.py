"""
蒙特卡洛模拟 (Monte Carlo Simulation) 模板
适用：不确定性分析、风险量化、随机系统模拟
问题适配点：
  1. 修改 run_single_trial() —— 定义单次试验的输入-输出逻辑
  2. 修改 _define_input_distributions() —— 定义各输入参数的分布
  3. 调整 n_trials（试验次数）和置信水平 alpha
  4. 如有确定性参数，直接替换对应分布为常数
"""

import numpy as np
from scipy import stats
from typing import Dict, Callable, Any, Tuple, Optional

# tqdm 可选依赖，未安装时自动降级
try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs):
        return iterable


class MonteCarloSimulation:
    """蒙特卡洛模拟框架"""

    def __init__(self, n_trials: int = 10000, alpha: float = 0.05,
                 use_lhs: bool = False, random_seed: Optional[int] = 42):
        """
        Parameters
        ----------
        n_trials : 模拟次数
        alpha : 显著性水平 (1-alpha 为置信水平)
        use_lhs : 是否使用拉丁超立方采样 (需要 scipy >= 1.7)
        random_seed : 随机种子，保证可复现
        """
        self.n_trials = n_trials
        self.alpha = alpha
        self.use_lhs = use_lhs
        self.rng = np.random.default_rng(random_seed)
        self.results: Optional[np.ndarray] = None

    def _define_input_distributions(self) -> Dict[str, Callable[[int], np.ndarray]]:
        """定义输入参数的概率分布，返回 {参数名: 采样函数}

        支持的分布（采样函数接收样本数 n，返回 shape=(n,) 的数组）：
        - 正态: lambda n: self.rng.normal(mu, sigma, n)
        - 均匀: lambda n: self.rng.uniform(low, high, n)
        - 三角: lambda n: self.rng.triangular(left, mode, right, n)
        - 对数正态: lambda n: self.rng.lognormal(mean, sigma, n)
        - 常数: lambda n: np.full(n, value)
        """
        # TODO: 替换为实际问题中的参数分布
        return {
            'demand': lambda n: self.rng.normal(100, 15, n),
            'unit_cost': lambda n: self.rng.uniform(8.0, 12.0, n),
            'lead_time': lambda n: self.rng.triangular(2, 5, 10, n).astype(int),
        }

    def run_single_trial(self, params: Dict[str, float]) -> float:
        """
        单次试验逻辑 —— 竞赛中需替换此方法。

        Parameters
        ----------
        params : 单组抽样结果，key 为参数名，value 为标量值

        Returns
        -------
        输出指标（利润、成本、完成时间等）
        """
        # TODO: 替换为实际问题的单次模拟逻辑
        revenue = 50 * min(params['demand'], 120)
        cost = params['unit_cost'] * 120
        return revenue - cost

    def _sample_parameters(self, n: int) -> Dict[str, np.ndarray]:
        """生成 n 组参数样本"""
        dists = self._define_input_distributions()
        if self.use_lhs:
            return self._sample_via_lhs(n, dists)
        else:
            return {name: fn(n) for name, fn in dists.items()}

    def _sample_via_lhs(self, n: int, dists: Dict) -> Dict[str, np.ndarray]:
        """拉丁超立方采样 (LHS)，starts 均匀分布于 [0,1] 超立方，
        再通过 PPF / 逆变换映射到各分布"""
        from scipy.stats.qmc import LatinHypercube
        sampler = LatinHypercube(d=len(dists), seed=self.rng.integers(0, 2**31))
        lhs_samples = sampler.random(n)  # shape (n, d), 每列 U(0,1)

        result = {}
        for idx, (name, fn) in enumerate(dists.items()):
            # 取该维度的 LHS 均匀样本，通过排序 + 经验 CDF 逆变换重排原样本
            # 方法：生成大样本 -> 按 LHS 百分位数重排
            large_n = max(n * 10, 10000)
            base = fn(large_n)
            base_sorted = np.sort(base)
            percentiles = lhs_samples[:, idx]
            indices = np.floor(percentiles * large_n).astype(int)
            indices = np.clip(indices, 0, large_n - 1)
            result[name] = base_sorted[indices]
        return result

    def run(self, verbose: bool = True) -> np.ndarray:
        """运行全部模拟试验"""
        params = self._sample_parameters(self.n_trials)

        if verbose:
            print(f"运行 {self.n_trials} 次模拟" + (" (LHS)" if self.use_lhs else "") + "...")

        results = np.zeros(self.n_trials)
        param_names = list(params.keys())

        for i in tqdm(range(self.n_trials), desc="模拟进度"):
            trial_params = {k: params[k][i] for k in param_names}
            results[i] = self.run_single_trial(trial_params)

        self.results = results
        return results

    def summarize(self) -> Dict[str, Any]:
        """结果汇总：均值、标准差、置信区间"""
        if self.results is None:
            raise RuntimeError("请先调用 run()")
        r = self.results
        mean, std = np.mean(r), np.std(r, ddof=1)
        se = std / np.sqrt(self.n_trials)
        z = stats.norm.ppf(1 - self.alpha / 2)
        ci_low, ci_high = mean - z * se, mean + z * se
        return {
            'mean': mean, 'std': std,
            'median': np.median(r),
            'p5': np.percentile(r, 5), 'p95': np.percentile(r, 95),
            'ci_95': (ci_low, ci_high),
            'ci_width': ci_high - ci_low,
            'skewness': stats.skew(r),
            'min': np.min(r), 'max': np.max(r),
        }

    def check_convergence(self, n_points: int = 20, verbose: bool = True) -> Tuple[np.ndarray, np.ndarray]:
        """收敛检查：CI 宽度随样本量变化"""
        if self.results is None:
            raise RuntimeError("请先调用 run()")
        sizes = np.linspace(100, self.n_trials, n_points, dtype=int)
        widths = np.zeros_like(sizes, dtype=float)
        z = stats.norm.ppf(1 - self.alpha / 2)
        for i, s in enumerate(sizes):
            sample = self.results[:s]
            se = np.std(sample, ddof=1) / np.sqrt(s)
            widths[i] = 2 * z * se
        if verbose:
            print(f"CI 宽度: {widths[0]:.4f} (n={sizes[0]}) -> {widths[-1]:.4f} (n={sizes[-1]})")
        return sizes, widths

    def plot(self, save_path: Optional[str] = None):
        """直方图 + KDE + CI 标记可视化"""
        import matplotlib.pyplot as plt
        if self.results is None:
            raise RuntimeError("请先调用 run()")

        fig, axes = plt.subplots(1, 2, figsize=(12, 4))

        # 左：直方图 + KDE
        ax = axes[0]
        ax.hist(self.results, bins=50, density=True, alpha=0.6, color='steelblue', edgecolor='white')
        kde_x = np.linspace(self.results.min(), self.results.max(), 300)
        kde = stats.gaussian_kde(self.results)
        ax.plot(kde_x, kde(kde_x), 'r-', lw=2, label='KDE')
        s = self.summarize()
        for val, color, label in [(s['mean'], 'red', 'Mean'), (s['ci_95'][0], 'orange', '95% CI'),
                                   (s['ci_95'][1], 'orange', None)]:
            ax.axvline(val, color=color, linestyle='--', alpha=0.8)
        ax.set_xlabel('Output'), ax.set_ylabel('Density'), ax.set_title('Output Distribution')
        ax.legend()

        # 右：收敛图
        ax = axes[1]
        sizes, widths = self.check_convergence(verbose=False)
        ax.plot(sizes, widths, 'b-o', markersize=3)
        ax.set_xlabel('Sample Size'), ax.set_ylabel('CI Width')
        ax.set_title('Convergence Check'), ax.grid(True, alpha=0.3)

        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.show()


# ===== 使用示例 =====
if __name__ == "__main__":
    mc = MonteCarloSimulation(n_trials=5000, use_lhs=False, random_seed=42)
    mc.run()
    summary = mc.summarize()
    print("\n=== 模拟结果汇总 ===")
    for k, v in summary.items():
        if isinstance(v, tuple):
            print(f"{k}: ({v[0]:.4f}, {v[1]:.4f})")
        else:
            print(f"{k}: {v:.4f}" if isinstance(v, float) else f"{k}: {v}")
    mc.plot()
