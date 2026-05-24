"""
常微分方程求解 (ODE Solver) 模板
适用：动力学系统建模、传染病模型、种群动力学、物理过程模拟

问题适配点：
  1. 修改 ode_system() —— 定义实际 ODE 系统的右端函数 f(t, y)
  2. 修改高阶 ODE 转一阶的方程（见 higher_order_to_first_order() 注释）
  3. 修改 true_params —— 参数拟合中"真值"替换为实际观测数据
  4. 调整 t_span / t_eval —— 时间范围和输出点
  5. 调整初始条件 y0 和参数范围
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from typing import Tuple, Callable, List, Optional

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def higher_order_to_first_order(coeffs: List[float]) -> Callable:
    """
    将 n 阶齐次线性 ODE 转化为一阶系统。

    示例：y'' + a*y' + b*y = 0
    coeffs = [b, a]  # 从最低阶开始
    返回 function f(t, y) 适用于 solve_ivp。

    Parameters
    ----------
    coeffs : 系数列表 [c0, c1, ..., c_{n-1}]，
             其中 c0*y + c1*y' + ... + c_{n-1}*y^{(n-1)} + y^{(n)} = 0

    Returns
    -------
    f(t, y) : 一阶系统右端函数
    """
    n = len(coeffs)

    def system(t, y):
        dy = np.zeros(n)
        for i in range(n - 1):
            dy[i] = y[i + 1]
        # y_n' = -sum(c_i * y_i)
        dy[n - 1] = -sum(coeffs[i] * y[i] for i in range(n))
        return dy

    return system


def ode_system(t: float, y: np.ndarray,
               k: float, c: float, m: float, F0: float, omega: float) -> np.ndarray:
    """
    示例：阻尼受迫谐振子。

    m * y'' + c * y' + k * y = F0 * cos(omega * t)

    转化：y0 = y (位移), y1 = y' (速度)
    y0' = y1
    y1' = (F0*cos(omega*t) - c*y1 - k*y0) / m

    Parameters
    ----------
    t : 时间
    y : 状态向量 [位移, 速度]
    其余 : 物理参数

    Returns
    -------
    dy : [dy0/dt, dy1/dt]
    """
    # TODO: 替换为实际问题的 ODE 系统
    y0, y1 = y
    dy0 = y1
    dy1 = (F0 * np.cos(omega * t) - c * y1 - k * y0) / m
    return np.array([dy0, dy1])


class ODESolver:
    """ODE 求解与后处理框架"""

    def __init__(self, ode_func: Callable, y0: np.ndarray,
                 t_span: Tuple[float, float],
                 t_eval: Optional[np.ndarray] = None,
                 n_points: int = 500):
        """
        Parameters
        ----------
        ode_func : f(t, y, *params) — 一阶 ODE 系统右端函数
        y0 : 初始条件
        t_span : (t_start, t_end)
        t_eval : 输出时间点（None 则等距生成 n_points 个点）
        n_points : t_eval 点数
        """
        self.ode_func = ode_func
        self.y0 = np.array(y0)
        self.t_span = t_span
        self.t_eval = t_eval if t_eval is not None else np.linspace(*t_span, n_points)
        self.solution = None

    def solve_euler(self, params: tuple = ()) -> Tuple[np.ndarray, np.ndarray]:
        """
        显式欧拉法（主要用于教学对比，实际项目用 solve_ivp）。

        Returns
        -------
        t : 时间点
        y : shape (n_points, n_states) 解矩阵
        """
        n = len(self.t_eval)
        dt = self.t_eval[1] - self.t_eval[0]
        y = np.zeros((n, len(self.y0)))
        y[0] = self.y0

        for i in range(n - 1):
            t_i = self.t_eval[i]
            y[i + 1] = y[i] + dt * self.ode_func(t_i, y[i], *params)

        return self.t_eval, y

    def solve_rk4(self, params: tuple = ()) -> Tuple[np.ndarray, np.ndarray]:
        """
        经典四阶 Runge-Kutta 法。

        Returns
        -------
        t : 时间点
        y : shape (n_points, n_states) 解矩阵
        """
        n = len(self.t_eval)
        dt = self.t_eval[1] - self.t_eval[0]
        y = np.zeros((n, len(self.y0)))
        y[0] = self.y0

        for i in range(n - 1):
            t_i = self.t_eval[i]
            yi = y[i]
            k1 = self.ode_func(t_i, yi, *params)
            k2 = self.ode_func(t_i + dt / 2, yi + dt * k1 / 2, *params)
            k3 = self.ode_func(t_i + dt / 2, yi + dt * k2 / 2, *params)
            k4 = self.ode_func(t_i + dt, yi + dt * k3, *params)
            y[i + 1] = yi + (dt / 6) * (k1 + 2 * k2 + 2 * k3 + k4)

        return self.t_eval, y

    def solve_scipy(self, params: tuple = (),
                    method: str = 'RK45',
                    rtol: float = 1e-6) -> object:
        """
        使用 scipy.integrate.solve_ivp（生产级求解器）。

        Parameters
        ----------
        params : ODE 函数参数
        method : 'RK45', 'DOP853', 'Radau', 'BDF', 'LSODA'
        rtol : 相对误差容限

        Returns
        -------
        scipy OdeResult 对象
        """
        self.solution = solve_ivp(
            self.ode_func, self.t_span, self.y0,
            args=params,
            method=method,
            t_eval=self.t_eval,
            rtol=rtol
        )
        return self.solution

    def fit_parameters(self, t_obs: np.ndarray, y_obs: np.ndarray,
                       param_guess: tuple,
                       param_bounds: Optional[tuple] = None,
                       state_idx: int = 0) -> Tuple[np.ndarray, np.ndarray]:
        """
        用观测数据拟合 ODE 参数（curve_fit 方法）。

        Parameters
        ----------
        t_obs : 观测时间点
        y_obs : 观测值（单变量，如仅观测位移）
        param_guess : 参数初始猜测
        param_bounds : 参数上下界，如 ( [lb], [ub] )
        state_idx : 观测对应 y 的第几个分量（默认 0）

        Returns
        -------
        popt : 最优参数
        pcov : 参数协方差矩阵
        """
        # TODO: 替换 y_obs 为实际观测数据
        def model(t, *params):
            """给定时间点和参数，返回指定状态的模拟值"""
            n = len(t)
            y_sim = np.zeros(n)
            sol = solve_ivp(self.ode_func, [t[0], t[-1]], self.y0,
                            args=params, t_eval=t, method='RK45', rtol=1e-6)
            if sol.success:
                return sol.y[state_idx]
            else:
                return np.full(n, np.nan)

        popt, pcov = curve_fit(model, t_obs, y_obs,
                               p0=param_guess,
                               bounds=param_bounds if param_bounds else (-np.inf, np.inf),
                               maxfev=10000)
        return popt, pcov

    def sensitivity_analysis(self, base_params: dict,
                             perturbation: float = 0.1,
                             metric: str = 'max') -> dict:
        """
        单因素灵敏度分析：逐个参数 ±perturbation，记录输出变化。

        Parameters
        ----------
        base_params : 基准参数字典 {name: value}
        perturbation : 扰动比例（0.1 = 10%）
        metric : 输出变化指标 'max' 或 'final'

        Returns
        -------
        sensitivity : {param_name: delta_metric}
        """
        # TODO: 修改 metric 定义，匹配实际问题的关注指标
        params_tuple = tuple(base_params.values())
        sol_base = solve_ivp(self.ode_func, self.t_span, self.y0,
                             args=params_tuple, t_eval=self.t_eval,
                             method='RK45', rtol=1e-6)

        if metric == 'max':
            base_val = np.max(np.abs(sol_base.y[0]))
        else:
            base_val = np.abs(sol_base.y[0, -1])

        sensitivity = {}
        keys = list(base_params.keys())
        vals = list(base_params.values())

        for i, key in enumerate(keys):
            delta = vals[i] * perturbation
            for factor in [+1, -1]:
                perturbed = list(vals)
                perturbed[i] += factor * delta
                sol_pert = solve_ivp(self.ode_func, self.t_span, self.y0,
                                     args=tuple(perturbed), t_eval=self.t_eval,
                                     method='RK45', rtol=1e-6)
                if metric == 'max':
                    val = np.max(np.abs(sol_pert.y[0]))
                else:
                    val = np.abs(sol_pert.y[0, -1])
                sensitivity[f"{key}_{'+' if factor > 0 else '-'}{perturbation*100:.0f}%"] = val - base_val

        return sensitivity

    def plot_state(self, solution=None, labels: Optional[List[str]] = None,
                   save_path: Optional[str] = None):
        """绘制状态变量 vs 时间"""
        if solution is None:
            if hasattr(self.solution, 't'):
                solution = self.solution
            else:
                raise RuntimeError("请先调用 solve_* 方法")

        t, y = solution.t, solution.y
        n_states = y.shape[0]

        if labels is None:
            labels = [f'State {i+1}' for i in range(n_states)]

        fig, ax = plt.subplots(figsize=(10, 4))
        colors = plt.cm.tab10(np.linspace(0, 1, n_states))
        for i in range(n_states):
            ax.plot(t, y[i], color=colors[i], lw=1.5, label=labels[i])
        ax.set_xlabel('时间 t')
        ax.set_ylabel('状态值')
        ax.set_title('ODE 状态变量时间演化')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.show()

    def plot_phase_portrait(self, solution=None, x_idx: int = 0,
                             y_idx: int = 1,
                             labels: Optional[Tuple[str, str]] = None,
                             save_path: Optional[str] = None):
        """绘制相图（状态空间轨迹）"""
        if solution is None:
            if hasattr(self.solution, 't'):
                solution = self.solution
            else:
                raise RuntimeError("请先调用 solve_* 方法")

        y = solution.y
        if labels is None:
            labels = (f'State {x_idx+1}', f'State {y_idx+1}')

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.plot(y[x_idx], y[y_idx], 'steelblue', lw=1.5)
        ax.plot(y[x_idx, 0], y[y_idx, 0], 'go', markersize=8, label='起点')
        ax.plot(y[x_idx, -1], y[y_idx, -1], 'ro', markersize=8, label='终点')
        ax.set_xlabel(labels[0])
        ax.set_ylabel(labels[1])
        ax.set_title('相图（Phase Portrait）')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_aspect('auto')
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.show()

    def plot_tornado(self, sensitivity: dict,
                     save_path: Optional[str] = None):
        """绘制灵敏度分析的龙卷风图"""
        labels = list(sensitivity.keys())
        values = list(sensitivity.values())

        sorted_idx = np.argsort(np.abs(values))
        labels = [labels[i] for i in sorted_idx]
        values = [values[i] for i in sorted_idx]

        colors = ['#d62728' if v > 0 else '#1f77b4' for v in values]

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.barh(labels, values, color=colors, edgecolor='gray')
        ax.axvline(0, color='black', lw=1)
        ax.set_xlabel('输出指标变化量')
        ax.set_title('单因素灵敏度分析 — 龙卷风图')
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.show()


# ===== 使用示例 =====
if __name__ == "__main__":
    print("=== ODE 求解示例：阻尼受迫谐振子 ===\n")

    # TODO: 修改参数为实际物理/系统问题
    # 参数：k(刚度), c(阻尼), m(质量), F0(驱动力幅值), omega(驱动频率)
    params = (40.0, 0.5, 1.0, 1.5, 2.0)  # k, c, m, F0, omega
    y0 = [1.0, 0.0]  # 初始位移=1, 初始速度=0
    t_span = (0, 20)

    solver = ODESolver(ode_system, y0, t_span, n_points=800)

    # 1) 多种方法对比
    _, y_euler = solver.solve_euler(params)
    _, y_rk4 = solver.solve_rk4(params)
    sol_scipy = solver.solve_scipy(params, method='DOP853')

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(solver.t_eval, y_euler[:, 0], 'gray', lw=0.8, alpha=0.6, label='Euler')
    ax.plot(solver.t_eval, y_rk4[:, 0], 'orange', lw=1, alpha=0.7, label='RK4')
    ax.plot(sol_scipy.t, sol_scipy.y[0], 'steelblue', lw=2, label='scipy DOP853')
    ax.set_xlabel('时间 t'), ax.set_ylabel('位移 y')
    ax.set_title('不同数值方法对比')
    ax.legend(), ax.grid(True, alpha=0.3)
    plt.tight_layout(), plt.show()

    # 2) 状态演化 + 相图
    solver.solution = sol_scipy
    solver.plot_state(labels=['位移', '速度'])
    solver.plot_phase_portrait(labels=('位移', '速度'))

    # 3) 灵敏度分析
    base_params = {'k': 40.0, 'c': 0.5, 'm': 1.0, 'F0': 1.5, 'omega': 2.0}
    sens = solver.sensitivity_analysis(base_params, perturbation=0.2, metric='max')
    print("\n===== 灵敏度分析结果 =====")
    for k, v in sens.items():
        print(f"  {k}: {v:+.6f}")
    solver.plot_tornado(sens)
