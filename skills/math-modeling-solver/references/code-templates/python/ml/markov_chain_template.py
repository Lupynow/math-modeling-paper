"""
马尔可夫链仿真模板 (Markov Chain Simulation)
==============================================
适用场景：
  - 体育赛事：网球/乒乓球逐球/逐局得分概率、胜率预测
  - 队列系统：服务台状态转移、排队长度稳态分布
  - 时间序列状态建模：天气状态（晴/阴/雨）、信用评级迁移
  - 客户行为预测：购买/流失/活跃三态转移
  - 博弈策略：马尔可夫决策过程 (MDP) 前身

核心概念：
  - 转移概率矩阵 P[i,j] = P(state_j | state_i)，每行和为 1
  - 稳态分布 π：πP = π（求解特征值 λ=1 的左特征向量）
  - 吸收态：一旦进入就无法离开的状态（如网球一分结束）

与其他模型对比：
  - vs 回归/时序：Markov 不需要连续值，适合离散状态序列
  - vs RNN/LSTM：可解释性强，小样本即可建立，但无长期记忆
  - vs MDP：不含行动决策，仅描述自发状态转移

问题适配点（需替换的 TODO 标记）：
  1. 修改 _build_tennis_transition_matrix() 为实际转移概率
  2. 修改 STATE_NAMES 为实际状态名称
  3. 如为吸收链，修改 is_absorbing 逻辑
  4. 可替换仿真步数 n_sim_steps
  5. 如需文本/评分建模为状态，先做离散化
"""
import numpy as np
import matplotlib.pyplot as plt


# ======================== 马尔可夫链核心类 ========================

class MarkovChain:
    """离散时间马尔可夫链"""

    def __init__(self, P: np.ndarray, state_names: list = None):
        """
        P: (n, n) 转移概率矩阵，每行和为1
        state_names: 状态名称列表
        """
        self.P = np.asarray(P, dtype=float)
        self.n = len(P)
        # 确保每行归一化
        row_sums = self.P.sum(axis=1, keepdims=True)
        self.P = self.P / row_sums
        self.state_names = state_names or [f"S{i}" for i in range(self.n)]
        self._steady_state = None

    @property
    def steady_state(self) -> np.ndarray:
        """稳态分布 π：求解 πP = π 即 P^T π^T = π^T"""
        if self._steady_state is None:
            vals, vecs = np.linalg.eig(self.P.T)
            idx = np.argmin(np.abs(vals - 1.0))
            pi = np.real(vecs[:, idx])
            pi = pi / pi.sum()
            self._steady_state = pi
        return self._steady_state

    def is_absorbing(self, state_idx: int) -> bool:
        """判断是否为吸收态（P[i,i]=1）"""
        return abs(self.P[state_idx, state_idx] - 1.0) < 1e-10

    def step(self, current_state: int, rng: np.random.RandomState = None) -> int:
        """单步转移"""
        rng = rng or np.random.RandomState()
        return rng.choice(self.n, p=self.P[current_state])

    def simulate(self, start_state: int, n_steps: int,
                 rng: np.random.RandomState = None) -> np.ndarray:
        """仿真一条轨迹，返回状态序列"""
        rng = rng or np.random.RandomState()
        states = [start_state]
        for _ in range(n_steps):
            states.append(self.step(states[-1], rng))
        return np.array(states)

    def simulate_many(self, start_state: int, n_steps: int, n_chains: int = 1000,
                      verbose: bool = True) -> np.ndarray:
        """多条仿真链，返回 (n_chains, n_steps+1) 状态矩阵"""
        rng = np.random.RandomState(42)
        chains = np.zeros((n_chains, n_steps + 1), dtype=int)
        chains[:, 0] = start_state
        for t in range(n_steps):
            for c in range(n_chains):
                chains[c, t + 1] = self.step(chains[c, t], rng)
        return chains

    def occupancy_over_time(self, chains: np.ndarray) -> np.ndarray:
        """计算各时刻状态占有率 (n_steps+1, n)"""
        n_steps_plus1 = chains.shape[1]
        occ = np.zeros((n_steps_plus1, self.n))
        for t in range(n_steps_plus1):
            vals, cnts = np.unique(chains[:, t], return_counts=True)
            occ[t, vals] = cnts / chains.shape[0]
        return occ

    def convergence_check(self, tol: float = 1e-4) -> int:
        """检测 P^k 是否收敛到稳态（返回近似收敛所需的步数）"""
        Pk = np.eye(self.n)
        for k in range(1, 200):
            Pk = Pk @ self.P
            if np.allclose(Pk, np.outer(np.ones(self.n), self.steady_state),
                           atol=tol):
                return k
        return -1  # 未收敛


# ======================== 可视化 ========================

def plot_transition_heatmap(mc: MarkovChain):
    """绘制转移矩阵热力图"""
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    im = ax.imshow(mc.P, cmap='YlOrRd', vmin=0, vmax=1)
    for i in range(mc.n):
        for j in range(mc.n):
            ax.text(j, i, f"{mc.P[i, j]:.2f}", ha='center', va='center',
                    fontsize=9, color='black' if mc.P[i, j] < 0.5 else 'white')
    ax.set_xticks(range(mc.n)), ax.set_yticks(range(mc.n))
    ax.set_xticklabels(mc.state_names)
    ax.set_yticklabels(mc.state_names)
    ax.set_title("Transition Probability Matrix")
    ax.set_xlabel("To State"), ax.set_ylabel("From State")
    plt.colorbar(im, ax=ax, shrink=0.8)
    plt.tight_layout()
    plt.savefig('markov_heatmap.png', dpi=150)
    plt.close()
    print("[可视化] 已保存 markov_heatmap.png")


def plot_state_distribution_over_time(occupancy: np.ndarray,
                                      state_names: list):
    """绘制状态占有率随时间变化"""
    t_vals = np.arange(occupancy.shape[0])
    plt.figure(figsize=(7, 4))
    for s in range(occupancy.shape[1]):
        plt.plot(t_vals, occupancy[:, s], label=state_names[s], linewidth=1.8)
    plt.xlabel("Step"), plt.ylabel("Proportion")
    plt.title("State Distribution Over Time")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('markov_distribution.png', dpi=150)
    plt.close()
    print("[可视化] 已保存 markov_distribution.png")


# ======================== 运行示例 ========================

def _build_tennis_chain() -> MarkovChain:
    """
    网球一分内的状态转移模型
    状态: [A发球优势, B发球优势, 相持A略优, 相持B略优, A得分, B得分]
    最后两个为吸收态
    """
    # TODO: 替换为实际问题的转移概率（可用数据统计或文献值）
    P = np.array([
        [0.20, 0.05, 0.35, 0.15, 0.20, 0.05],   # A发球优势
        [0.05, 0.25, 0.10, 0.35, 0.05, 0.20],   # B发球优势
        [0.05, 0.02, 0.38, 0.20, 0.30, 0.05],   # 相持A略优
        [0.02, 0.08, 0.18, 0.37, 0.05, 0.30],   # 相持B略优
        [0.00, 0.00, 0.00, 0.00, 1.00, 0.00],   # A得分（吸收）
        [0.00, 0.00, 0.00, 0.00, 0.00, 1.00],   # B得分（吸收）
    ])
    names = ["A-serve-adv", "B-serve-adv", "rally-A", "rally-B",
             "A-POINT", "B-POINT"]
    return MarkovChain(P, names)


if __name__ == "__main__":
    print("=" * 55)
    print("马尔可夫链仿真模板 — 网球逐球仿真演示")
    print("=" * 55)

    mc = _build_tennis_chain()

    # ---- 稳态分布 ----
    print("\n[1] 稳态分布 π")
    pi = mc.steady_state
    for name, p in zip(mc.state_names, pi):
        print(f"  {name:15s}: {p:.4f}")
    # TODO: 如果包含吸收态，稳态分布将全部集中在吸收态

    # ---- 收敛检测 ----
    print("\n[2] 收敛速度")
    conv_k = mc.convergence_check()
    print(f"  P^k 收敛到稳态所需步数: {conv_k if conv_k > 0 else '>200 (未收敛)'}")

    # ---- 单链仿真 ----
    print("\n[3] 单条链仿真")
    n_sim_steps = 30  # TODO: 根据实际需求调整仿真步数
    chain = mc.simulate(start_state=0, n_steps=n_sim_steps)
    state_seq_str = " → ".join([mc.state_names[s] for s in chain[:8]])
    print(f"  前8步轨迹: {state_seq_str} ...")

    # ---- 多条链统计 ----
    print("\n[4] 多条链占用率 (n_chains=1000)")
    chains = mc.simulate_many(start_state=0, n_steps=20, n_chains=1000)
    occ = mc.occupancy_over_time(chains)
    print(f"  最后时刻状态分布: {np.round(occ[-1], 4)}")
    # 吸收概率
    print(f"  A得分概率={occ[-1, 4]:.4f}, B得分概率={occ[-1, 5]:.4f}")

    # ---- 可视化 ----
    print("\n[5] 可视化")
    plot_transition_heatmap(mc)
    plot_state_distribution_over_time(occ[:, :4], mc.state_names[:4])
    print("\n完成。")
