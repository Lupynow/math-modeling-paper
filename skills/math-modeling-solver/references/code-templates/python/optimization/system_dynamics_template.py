"""
系统动力学仿真模板 (System Dynamics / Coupled ODE Simulation)
===============================================================
适用场景：
  - 人口-资源-环境耦合系统（如 MCM F/E 类环境问题）
  - 传染病传播 (SIR/SEIR/SEIRD)
  - 经济增长-污染排放反馈系统
  - 捕食者-猎物 / 竞争 / 共生生态系统
  - 任何多变量相互影响的时序演化问题

系统动力学 vs 纯 ODE（常微分方程）：
  - 系统动力学：关注反馈回路定性与结构，适合"如果...那么..."情景推演
  - 纯 ODE：数学精确解/数值分析，适合参数估计和理论分析
  - 建模时两者互补：ODEs 提供方程骨架，系统动力学提供解释框架

核心概念：
  - Stock（存量）：系统状态变量（如人口、CO2浓度）
  - Flow（流速）：存量变化的速率（如出生率、排放率）
  - 反馈回路：存量→速率→存量的闭链
    - 正反馈（+）：放大效应（如人口越多→出生越多→人口更多）
    - 负反馈（-）：稳定效应（如人口越多→资源越少→死亡率上升）

问题适配点（需替换的 TODO 标记）：
  1. 修改 system_ode() 为实际耦合 ODE 系统
  2. 修改 state_names 和参数名称为实际变量
  3. 替换 param_sweep_points 为实际参数范围
  4. 根据问题选择合适的时间跨度 t_span
  5. 如需更复杂流图，可使用 Vensim/InsightMaker 辅助
"""
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt


# ======================== 系统定义 ========================

def system_ode(t: float, y: np.ndarray, params: dict) -> np.ndarray:
    """
    耦合 ODE 系统定义
    y = [stock1, stock2, ...]  — 系统存量
    params: 参数字典

    TODO: 替换为实际系统方程
    当前示例：Logistic增长 + 比例收获（捕食者-猎物简化版）
      dy[0]/dt = r*y[0]*(1 - y[0]/K) - harvest_rate*y[0]  (资源/猎物)
      dy[1]/dt = e*harvest_rate*y[0] - m*y[1]              (收获者/捕食者)
    """
    r = params.get('r', 0.8)           # 内禀增长率
    K = params.get('K', 100)           # 环境容量
    harvest = params.get('harvest', 0.15)  # 收获/捕食率
    e = params.get('e', 0.1)           # 转化效率
    m = params.get('m', 0.4)           # 收获者死亡率

    prey = np.maximum(y[0], 0)         # 非负约束（ODE积分可能越界）
    predator = np.maximum(y[1], 0)

    d_prey = r * prey * (1 - prey / K) - harvest * prey * predator
    d_predator = e * harvest * prey * predator - m * predator

    return np.array([d_prey, d_predator])


# ======================== 反馈回路分析 ========================

def analyze_feedback(y_eq: np.ndarray, ode_func, params: dict,
                     delta: float = 1e-4) -> dict:
    """
    在平衡点 y_eq 附近通过 Jacobian 分析反馈回路
    Jacobian: J[i,j] = d(dy_i/dt)/dy_j
    正特征值实部 → 正反馈主导（发散）
    负特征值实部 → 负反馈主导（稳定）
    """
    n = len(y_eq)
    J = np.zeros((n, n))
    f0 = ode_func(0, y_eq, params)
    for j in range(n):
        y_pert = y_eq.copy()
        y_pert[j] += delta
        f_pert = ode_func(0, y_pert, params)
        J[:, j] = (f_pert - f0) / delta

    eigvals = np.linalg.eigvals(J)
    eig_real = np.real(eigvals)

    feedback_type = "稳定（负反馈主导）" if np.all(eig_real < 0) else \
                    "可能不稳定（存在正反馈或中性）"

    return {
        'jacobian': J,
        'eigenvalues': eigvals,
        'dominant_sign': "负反馈" if np.all(eig_real < 0) else "正反馈/混合",
        'stability': feedback_type
    }


# ======================== 参数灵敏度扫描 ========================

def parameter_sweep(ode_func, base_params: dict, sweep_key: str,
                    sweep_values: list, y0: list, t_span: tuple,
                    t_eval: np.ndarray = None) -> dict:
    """
    对指定参数做灵敏度扫描，返回每次运行的时间序列
    """
    results = {}
    print(f"\n[参数扫描] {sweep_key}:")
    for val in sweep_values:
        p = base_params.copy()
        p[sweep_key] = val
        sol = solve_ivp(ode_func, t_span, y0, args=(p,),
                        t_eval=t_eval, method='RK45', rtol=1e-6, atol=1e-9)
        results[val] = sol
        final = [f"{sol.y[i,-1]:.1f}" for i in range(len(y0))]
        print(f"  {sweep_key}={val:<6.3f} → 终态 y={final}")
    return results


# ======================== 可视化 ========================

def plot_trajectories(sol, state_names: list, title: str = "System Dynamics"):
    """绘制存量时间轨迹"""
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    t = sol.t
    y = sol.y
    colors = ['#2196F3', '#FF5722', '#4CAF50', '#9C27B0']
    for i in range(y.shape[0]):
        axes[0].plot(t, y[i], color=colors[i % len(colors)],
                     linewidth=2, label=state_names[i])
    axes[0].set_xlabel('Time'), axes[0].set_ylabel('Stock Level')
    axes[0].set_title('Stock Trajectories')
    axes[0].legend(), axes[0].grid(alpha=0.3)

    # 相图 (如果为2维)
    if y.shape[0] >= 2:
        axes[1].plot(y[0], y[1], 'k-', linewidth=1.5, alpha=0.7)
        axes[1].scatter(y[0, 0], y[1, 0], c='green', s=80, zorder=5,
                        label='Start')
        axes[1].scatter(y[0, -1], y[1, -1], c='red', s=80, zorder=5,
                        label='End')
        axes[1].set_xlabel(state_names[0]), axes[1].set_ylabel(state_names[1])
        axes[1].set_title('Phase Portrait')
        axes[1].legend(), axes[1].grid(alpha=0.3)

    fig.suptitle(title)
    plt.tight_layout()
    plt.savefig('system_dynamics.png', dpi=150)
    plt.close()
    print("[可视化] 已保存 system_dynamics.png")


# ======================== 运行示例 ========================

if __name__ == "__main__":
    print("=" * 55)
    print("系统动力学仿真模板 — Logistic增长+收获演示")
    print("=" * 55)

    # TODO: 替换为实际初始条件和时间范围
    state_names = ["资源(猎物)", "收获者(捕食者)"]
    y0 = [50.0, 5.0]         # 初始存量
    t_span = (0, 60)         # 时间跨度
    t_eval = np.linspace(*t_span, 300)

    base_params = {
        'r': 0.8, 'K': 100, 'harvest': 0.15, 'e': 0.1, 'm': 0.4
    }

    # ---- 基准仿真 ----
    print("\n[1] 基准仿真")
    sol = solve_ivp(system_ode, t_span, y0, args=(base_params,),
                    t_eval=t_eval, method='RK45', rtol=1e-6, atol=1e-9)
    print(f"  求解状态: {'成功' if sol.success else '失败'}")
    print(f"  终态: {np.round(sol.y[:, -1], 2)}")

    # ---- 反馈回路分析 ----
    print("\n[2] 反馈回路分析（终态附近 Jacobian）")
    fb = analyze_feedback(sol.y[:, -1], system_ode, base_params)
    print(f"  特征值: {np.round(fb['eigenvalues'], 4)}")
    print(f"  反馈类型: {fb['dominant_sign']}")
    print(f"  稳定性: {fb['stability']}")

    # ---- 参数灵敏度扫描 ----
    print("\n[3] 参数灵敏度扫描")
    # TODO: 根据实际问题选择要扫描的参数和范围
    sweep_vals = [0.05, 0.10, 0.15, 0.20, 0.25]
    sweep_results = parameter_sweep(
        system_ode, base_params, 'harvest', sweep_vals,
        y0, t_span, t_eval)

    # ---- 可视化 ----
    print("\n[4] 可视化")
    plot_trajectories(sol, state_names,
                      "Logistic Growth with Harvesting (System Dynamics Demo)")

    # 灵敏度对比图
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    colors = plt.cm.viridis(np.linspace(0, 1, len(sweep_vals)))
    for val, color in zip(sweep_vals, colors):
        sr = sweep_results[val]
        axes[0].plot(sr.t, sr.y[0], color=color, linewidth=1.5,
                     label=f'h={val:.2f}')
        axes[1].plot(sr.t, sr.y[1], color=color, linewidth=1.5,
                     label=f'h={val:.2f}')
    axes[0].set_title(state_names[0]), axes[1].set_title(state_names[1])
    for ax in axes:
        ax.set_xlabel('Time'), ax.set_ylabel('Stock')
        ax.legend(fontsize=7), ax.grid(alpha=0.3)
    plt.suptitle("Parameter Sensitivity: harvest rate")
    plt.tight_layout()
    plt.savefig('system_dynamics_sensitivity.png', dpi=150)
    plt.close()
    print("[可视化] 已保存 system_dynamics_sensitivity.png")
    print("\n完成。")
