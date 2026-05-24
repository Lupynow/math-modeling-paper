"""
食物网 / 生态ODE模板 (Food Web & Ecological ODEs)
=====================================================
适用场景（MCM E 类环境/生态问题）：
  - 物种共存、竞争排斥、入侵物种影响评估
  - 渔业/林业可持续收获策略
  - 生态系统稳定性与恢复力分析
  - 气候变化对食物链的级联效应

核心模型层次：
  1. Lotka-Volterra (2-species)：经典捕食者-猎物模型
     dx/dt = αx - βxy,  dy/dt = δxy - γy
  2. 多物种交互矩阵：dN_i/dt = N_i * (r_i + Σ a_ij * N_j)
  3. 功能响应提升现实性：
     - Holling I: linear up to saturation (如滤食性动物)
     - Holling II: f(N) = aN / (1 + ahN)  (处理时间限制)
     - Holling III: f(N) = aN^2 / (1 + ahN^2) (学习/转换行为）

生态学指标：
  - Shannon多样性: H = -Σ p_i * ln(p_i)
  - Simpson 多样性: D = 1 - Σ p_i^2
  - 生物量稳定性：总生物量的变异系数 CV

问题适配点（需替换的 TODO 标记）：
  1. 修改 food_chain_ode() 为实际食物网 ODE 系统
  2. 修改 species_names, interaction_matrix 为实际物种和参数
  3. 根据实际功能响应选择 Holling Type I/II/III
  4. 调整 t_span 为实际时间尺度（年/月/日）
  5. 如系统 > 5维，建议降维或用矩阵分块求解
"""
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt


# ======================== 功能响应函数 ========================

def holling_type1(N_prey: np.ndarray, a: float, sat: float) -> np.ndarray:
    """Holling I: 线性增长到饱和值 sat"""
    return np.minimum(a * N_prey, sat)


def holling_type2(N_prey: np.ndarray, a: float, h: float) -> np.ndarray:
    """Holling II: f(N) = aN / (1 + ahN) — 渐近饱和"""
    denom = 1.0 + a * h * np.maximum(N_prey, 0)
    return a * np.maximum(N_prey, 0) / np.maximum(denom, 1e-12)


def holling_type3(N_prey: np.ndarray, a: float, h: float) -> np.ndarray:
    """Holling III: f(N) = aN^2 / (1 + ahN^2) — S型"""
    N2 = np.maximum(N_prey, 0) ** 2
    denom = 1.0 + a * h * N2
    return a * N2 / np.maximum(denom, 1e-12)


# ======================== 食物网 ODE 系统 ========================

def food_chain_ode(t: float, y: np.ndarray, params: dict) -> np.ndarray:
    """
    3-物种食物链 ODE（草 → 兔 → 狐）
    y = [grass, rabbit, fox]

    TODO: 替换为实际食物网结构和参数
    更多物种时使用矩阵形式：
      dN_i/dt = N_i * (r_i + sum_j(A[i,j] * N_j))
      其中 A 为交互矩阵（正=受益，负=受害）
    """
    y = np.maximum(y, 0)      # 非负约束

    G, R, F = y[0], y[1], y[2]
    # ---- 草(grass) ----
    rG, KG = params.get('rG', 0.8), params.get('KG', 100)
    grazing_rate = params.get('grazing', 0.15)
    dG = rG * G * (1 - G / KG) - grazing_rate * G * R

    # ---- 兔子(rabbit) ----
    eR = params.get('eR', 0.2)          # 食草转化效率
    mR = params.get('mR', 0.3)          # 自然死亡率
    pred_rate = params.get('pred_rate', 0.1)  # 狐狸捕食率
    dR = eR * grazing_rate * G * R - mR * R - pred_rate * R * F

    # ---- 狐狸(fox) ----
    eF = params.get('eF', 0.08)         # 捕食转化效率
    mF = params.get('mF', 0.35)         # 狐狸死亡率
    dF = eF * pred_rate * R * F - mF * F

    return np.array([dG, dR, dF])


def multi_species_lv_ode(t: float, N: np.ndarray,
                          r: np.ndarray, A: np.ndarray) -> np.ndarray:
    """
    广义多物种 Lotka-Volterra 模型
    dN_i/dt = N_i * (r_i + sum_j(A[i,j] * N_j))
    r: 内禀增长率 (n,)
    A: 交互矩阵 (n, n), A[i,j] = 物种j对物种i的影响
       A[i,i] < 0 为种内竞争，A[i,j] < 0 为种间竞争/捕食
    """
    N = np.maximum(N, 0)
    dN = N * (r + A @ N)
    return dN


# ======================== 生态学指标 ========================

def shannon_diversity(populations: np.ndarray, axis: int = -1) -> float:
    """
    Shannon 多样性指数: H = -Σ p_i * ln(p_i)
    populations: 各物种个体数/生物量
    """
    total = np.sum(populations, axis=axis, keepdims=True)
    total = np.where(total < 1e-12, 1e-12, total)
    p = populations / total
    p = np.where(p < 1e-12, 1e-12, p)
    H = -np.sum(p * np.log(p), axis=axis)
    return float(H)


def simpson_index(populations: np.ndarray, axis: int = -1) -> float:
    """
    Simpson 多样性指数: D = 1 - Σ p_i^2
    值越大多样性越高
    """
    total = np.sum(populations, axis=axis, keepdims=True)
    total = np.where(total < 1e-12, 1e-12, total)
    p = populations / total
    D = 1 - np.sum(p ** 2, axis=axis)
    return float(D)


def biomass_stability(sol_y: np.ndarray) -> dict:
    """
    生物量稳定性分析
    sol_y: (n_species, n_timepoints)
    返回每物种的均值、标准差、变异系数(CV)
    """
    means = np.mean(sol_y, axis=1)
    stds = np.std(sol_y, axis=1)
    cvs = stds / (means + 1e-12)
    total_biomass = np.sum(sol_y, axis=0)
    return {
        'mean': means, 'std': stds, 'cv': cvs,
        'total_cv': np.std(total_biomass) / (np.mean(total_biomass) + 1e-12),
        'total_range': (np.min(total_biomass), np.max(total_biomass))
    }


# ======================== 可视化 ========================

def plot_food_chain_results(sol, species_names: list):
    """绘制食物链时间序列 + 相图 + 多样性时间序列"""
    t = sol.t
    y = sol.y
    n_species = y.shape[0]

    fig, axes = plt.subplots(2, 2, figsize=(11, 8))

    # (a) 种群时间序列
    colors = ['#4CAF50', '#2196F3', '#FF5722', '#9C27B0', '#FF9800']
    for i in range(n_species):
        axes[0, 0].plot(t, y[i], color=colors[i % len(colors)],
                        linewidth=2, label=species_names[i])
    axes[0, 0].set_xlabel('Time'), axes[0, 0].set_ylabel('Population')
    axes[0, 0].set_title('Population Time Series')
    axes[0, 0].legend(), axes[0, 0].grid(alpha=0.3)

    # (b) 相图 (前两个物种)
    if n_species >= 2:
        axes[0, 1].plot(y[0], y[1], 'k-', linewidth=1.2, alpha=0.7)
        axes[0, 1].scatter(y[0, 0], y[1, 0], c='green', s=60, zorder=5,
                           label='Start')
        axes[0, 1].scatter(y[0, -1], y[1, -1], c='red', s=60, zorder=5,
                           label='End')
        axes[0, 1].set_xlabel(species_names[0])
        axes[0, 1].set_ylabel(species_names[1])
        axes[0, 1].set_title('Phase Portrait')
        axes[0, 1].legend(), axes[0, 1].grid(alpha=0.3)

    # (c) 多样性指标随时间变化
    div_samples = np.arange(0, len(t), max(1, len(t) // 50))
    t_div = t[div_samples]
    y_div = y[:, div_samples]
    H_vals = np.array([shannon_diversity(y_div[:, i]) for i in range(len(t_div))])
    D_vals = np.array([simpson_index(y_div[:, i]) for i in range(len(t_div))])
    axes[1, 0].plot(t_div, H_vals, 'b-', linewidth=2, label='Shannon H')
    axes[1, 0].plot(t_div, D_vals, 'r--', linewidth=2, label='Simpson D')
    axes[1, 0].set_xlabel('Time'), axes[1, 0].set_ylabel('Diversity Index')
    axes[1, 0].set_title('Diversity Over Time')
    axes[1, 0].legend(), axes[1, 0].grid(alpha=0.3)

    # (d) 总生物量
    total = np.sum(y, axis=0)
    axes[1, 1].plot(t, total, 'k-', linewidth=2)
    axes[1, 1].axhline(np.mean(total), color='r', linestyle='--',
                       label=f'Mean={np.mean(total):.1f}')
    axes[1, 1].set_xlabel('Time'), axes[1, 1].set_ylabel('Total Biomass')
    axes[1, 1].set_title('Total Biomass')
    axes[1, 1].legend(), axes[1, 1].grid(alpha=0.3)

    fig.suptitle('3-Species Food Chain Dynamics')
    plt.tight_layout()
    plt.savefig('food_web_simulation.png', dpi=150)
    plt.close()
    print("[可视化] 已保存 food_web_simulation.png")


# ======================== 运行示例 ========================

if __name__ == "__main__":
    print("=" * 55)
    print("食物网ODE模板 — 3物种食物链 (草→兔→狐)")
    print("=" * 55)

    # ---- 食物链仿真 ----
    # TODO: 根据实际生态学情境修改参数
    species_names = ["草 (Grass)", "兔 (Rabbit)", "狐 (Fox)"]
    y0 = [80.0, 20.0, 8.0]       # 初始种群
    t_span = (0, 100)
    t_eval = np.linspace(*t_span, 500)

    params = {
        'rG': 0.8, 'KG': 100.0, 'grazing': 0.15,
        'eR': 0.2, 'mR': 0.3, 'pred_rate': 0.1,
        'eF': 0.08, 'mF': 0.35,
    }

    print("\n[1] 食物链仿真")
    sol = solve_ivp(food_chain_ode, t_span, y0, args=(params,),
                    t_eval=t_eval, method='RK45', rtol=1e-7, atol=1e-10)
    print(f"  求解状态: {'成功' if sol.success else '失败'}")
    print(f"  终态种群: {np.round(sol.y[:, -1], 2)}")

    # ---- 生态学指标 ----
    print("\n[2] 生态学指标")
    H_final = shannon_diversity(sol.y[:, -1])
    D_final = simpson_index(sol.y[:, -1])
    print(f"  Shannon 多样性 H = {H_final:.4f}")
    print(f"  Simpson 多样性 D = {D_final:.4f}")

    stability = biomass_stability(sol.y)
    print(f"  各物种 CV = {np.round(stability['cv'], 4)}")
    print(f"  总生物量 CV = {stability['total_cv']:.4f}")

    # ---- 参数灵敏度：改变捕食强度 ----
    # TODO: 根据实际问题选择扫描参数
    print("\n[3] 参数灵敏度（改变捕食率 pred_rate）")
    for pr in [0.05, 0.10, 0.15, 0.20]:
        p2 = params.copy()
        p2['pred_rate'] = pr
        s2 = solve_ivp(food_chain_ode, t_span, y0, args=(p2,),
                       t_eval=t_eval, method='RK45', rtol=1e-7, atol=1e-10)
        H2 = shannon_diversity(s2.y[:, -1])
        print(f"  pred_rate={pr:.2f}: 终态={np.round(s2.y[:,-1],1)}, "
              f"Shannon H={H2:.4f}")

    # ---- 可视化 ----
    print("\n[4] 可视化")
    plot_food_chain_results(sol, species_names)

    print("\n食物网结构描述：")
    print("  ┌─────────┐")
    print("  │  Grass  │ ← 自养/光合（Logistic增长）")
    print("  └────┬────┘")
    print("       │ grazing (Holling I 线性捕食)")
    print("  ┌────v────┐")
    print("  │ Rabbit  │ ← 初级消费者")
    print("  └────┬────┘")
    print("       │ predation (质量作用律)")
    print("  ┌────v────┐")
    print("  │   Fox   │ ← 次级消费者")
    print("  └─────────┘")
    print("\n完成。")
