"""
网络流优化模板 (Network Flow Optimization)
============================================
适用场景：
  - 供水/供气/交通/物流网络的流量分配与调度
  - 通信网络路由、电力潮流调度
  - 资源分配问题（可建模为最大流或最小费用流）

模型选择指南：
  - 最大流：给定网络容量，求源到汇的最大可能流量
    适用：瓶颈分析、管网极限能力评估、运输容量规划
  - 最小费用流：在满足流量需求下最小化成本
    适用：调度优化、经济决策、多源多汇分配
  - 动态流（时间扩展图）：随时间变化的流量需求
    适用：时序调度、48h供水规划、高峰期资源调配

与一般线性规划的对比：
  - 网络流具有特殊结构（全单模矩阵），整数约束下仍有整数最优解
  - 使用专用算法（EK, Dinic）比通用LP快1-2个数量级
  - 但如果约束复杂（非网络约束），建议回到LP/MIP

问题适配点（需替换的 TODO 标记）：
  1. 修改 _build_demo_graph() 为实际网络拓扑
  2. 修改源/汇/需求量为实际值
  3. 如需时间维度，修改时间扩展图的参数
  4. 如需整数约束且线性规划不适用，使用 pulp 分支定界
"""
import numpy as np
from collections import deque
from scipy.sparse import csr_matrix
from scipy.optimize import linprog
from scipy.sparse.csgraph import maximum_flow
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)


# ======================== 图结构定义 ========================

class FlowGraph:
    """有向流网络（邻接表）"""

    def __init__(self, n_nodes: int):
        self.n = n_nodes
        self.adj = [[] for _ in range(n_nodes)]       # 邻接表：[(to, edge_index)]
        self.edges = []                                # (u, v, cap, flow, cost)

    def add_edge(self, u: int, v: int, cap: float, cost: float = 0.0) -> int:
        """添加有向边，自动创建反向边（残留网络）"""
        # 正向边
        self.adj[u].append(len(self.edges))
        self.edges.append([u, v, cap, 0.0, cost])
        # 反向边（cap=0，cost = -cost）
        self.adj[v].append(len(self.edges))
        self.edges.append([v, u, 0.0, 0.0, -cost])
        return len(self.edges) - 2

    def get_edge_flow(self, edge_idx: int) -> float:
        """获取正向边的实际流量"""
        return self.edges[edge_idx][3]


# ======================== 最大流 (Edmonds-Karp) ========================

def edmonds_karp(graph: FlowGraph, source: int, sink: int) -> tuple:
    """
    Edmonds-Karp 最大流算法
    返回: (最大流量, 每条正向边的最终流量)
    复杂度: O(V*E^2)
    """
    n, edges, adj = graph.n, graph.edges, graph.adj
    total_flow = 0.0

    while True:
        # BFS 找增广路径
        parent = [-1] * n
        parent_edge = [-1] * n
        parent[source] = source
        q = deque([source])
        while q and parent[sink] == -1:
            u = q.popleft()
            for ei in adj[u]:
                _, v, cap, flow, _ = edges[ei]
                if cap - flow > 1e-9 and parent[v] == -1:
                    parent[v] = u
                    parent_edge[v] = ei
                    q.append(v)

        if parent[sink] == -1:
            break  # 无增广路径

        # 计算瓶颈容量
        push = float('inf')
        v = sink
        while v != source:
            ei = parent_edge[v]
            cap, flow = edges[ei][2], edges[ei][3]
            push = min(push, cap - flow)
            v = parent[v]

        # 推送流量
        v = sink
        while v != source:
            ei = parent_edge[v]
            edges[ei][3] += push
            edges[ei ^ 1][3] -= push          # 反向边
            v = parent[v]
        total_flow += push

    return total_flow, [edges[i][3] for i in range(0, len(edges), 2)]


# ======================== 最小费用流 (LP方法) ========================

def min_cost_flow_lp(graph: FlowGraph, source: int, sink: int,
                     required_flow: float) -> dict:
    """
    最小费用流 — scipy.optimize.linprog 求解
    适用于中小规模（V < 1000），大规模请用 network_simplex
    返回: {'flow': [每条正向边流量], 'total_cost': float, 'success': bool}
    """
    edges = graph.edges
    m_fwd = len(edges) // 2                         # 正向边数
    n_var = m_fwd

    # 费用系数
    c = [edges[i][4] for i in range(0, len(edges), 2)]

    # 容量约束：0 <= flow[i] <= cap[i]
    bounds = [(0, max(0, edges[i][2])) for i in range(0, len(edges), 2)]

    # 流量守恒约束：A_eq @ x = b_eq
    # 每个节点流出 - 流入 = 净流量
    n_nodes = graph.n
    A_eq = np.zeros((n_nodes, n_var))
    b_eq = np.zeros(n_nodes)

    for i in range(n_var):
        u, v = edges[2 * i][0], edges[2 * i][1]
        A_eq[u, i] = -1
        A_eq[v, i] = 1

    b_eq[source] = -required_flow
    b_eq[sink] = required_flow
    # TODO: 如果还有中间需求节点，相应设置 b_eq[node] = net_out

    # 去掉源节点或汇节点的一行（避免行满秩问题）
    keep_rows = [r for r in range(n_nodes) if r != source]
    A_eq = A_eq[keep_rows]
    b_eq = b_eq[keep_rows]

    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')

    flow = res.x if res.success else np.zeros(n_var)
    total_cost = np.dot(flow, c)
    return {'flow': flow, 'total_cost': total_cost, 'success': res.success}


# ======================== 时间扩展图 (Dynamic Flow) ========================

def build_time_expanded_graph(base_n_nodes: int, edge_list: list,
                               T: int) -> FlowGraph:
    """
    构建 T 个时间层的时间扩展图
    edge_list: [(u, v, capacity, transit_time, cost), ...]
    每个节点 v 在时刻 t 对应 v*T + t

    TODO: 根据实际问题调整边的传播方式和时间步长
    """
    total_nodes = base_n_nodes * T
    g = FlowGraph(total_nodes)
    for u, v, cap, transit_time, cost in edge_list:
        for t in range(T):
            if t + transit_time < T:
                ut = u * T + t
                vt = v * T + (t + transit_time)
                g.add_edge(ut, vt, cap, cost)
    # 节点"滞留边"：容量无限，允许流量在时间上停留
    # TODO: 如有储存/蓄水能力上限，修改滞留边容量
    for i in range(base_n_nodes):
        for t in range(T - 1):
            g.add_edge(i * T + t, i * T + t + 1, float('inf'), 0.0)
    return g


# ======================== 可视化 ========================

def plot_flow_network(graph: FlowGraph, flows: list, title: str = "Network Flow"):
    """绘制带流量标注的流网络"""
    edges = graph.edges
    import networkx as nx

    G = nx.DiGraph()
    for i in range(0, len(edges), 2):
        u, v, cap, _, _ = edges[i]
        f = flows[i // 2] if i // 2 < len(flows) else 0
        G.add_edge(u, v, capacity=cap, flow=f)

    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(7, 5))
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=600)
    nx.draw_networkx_labels(G, pos, font_size=10)

    # 边：宽度与流量成正比
    edge_widths = [1.5 + 3 * G[u][v]['flow'] / max(0.01, G[u][v]['capacity'])
                   for u, v in G.edges()]
    nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=15,
                           width=edge_widths, edge_color='gray')
    # 标注 流量/容量
    edge_labels = {(u, v): f"{G[u][v]['flow']:.1f}/{G[u][v]['capacity']:.1f}"
                   for u, v in G.edges()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    plt.title(title)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('network_flow.png', dpi=150)
    plt.close()
    print("[可视化] 已保存 network_flow.png")


# ======================== 运行示例 ========================

def _build_demo_graph() -> FlowGraph:
    """5节点供水网络：节点0=水库, 节点4=城市"""
    # TODO: 替换为实际管网拓扑
    g = FlowGraph(5)
    # (u, v, capacity, cost)
    # 水库→A
    g.add_edge(0, 1, cap=20, cost=2)
    # 水库→B
    g.add_edge(0, 2, cap=15, cost=3)
    # A→B（互联）
    g.add_edge(1, 2, cap=10, cost=1)
    # A→中转站
    g.add_edge(1, 3, cap=12, cost=2)
    # B→中转站
    g.add_edge(2, 3, cap=10, cost=2)
    # 中转站→城市
    g.add_edge(3, 4, cap=25, cost=1)
    # B→城市（直连）
    g.add_edge(2, 4, cap=8, cost=4)
    return g


if __name__ == "__main__":
    print("=" * 55)
    print("网络流优化模板 — 5节点供水网络演示")
    print("=" * 55)

    # ---- 最大流 ----
    print("\n[1] 最大流 (Edmonds-Karp)")
    g = _build_demo_graph()
    source, sink = 0, 4
    max_flow_val, flows = edmonds_karp(g, source, sink)
    print(f"  从节点{source}到节点{sink}的最大流量: {max_flow_val:.1f}")

    # ---- 最小费用流 ----
    print("\n[2] 最小费用流 (线性规划)")
    g2 = _build_demo_graph()
    # TODO: 替换 required_flow 为实际需水量
    demand = 18.0
    result = min_cost_flow_lp(g2, source, sink, required_flow=demand)
    print(f"  需水量={demand:.0f}, 总费用={result['total_cost']:.1f}, "
          f"求解成功={result['success']}")

    # ---- 时间扩展图 ----
    print("\n[3] 时间扩展图动态流（简单示例）")
    # TODO: 根据实际时段数替换 T
    base_edges = [(0, 1, 20, 1, 2), (0, 2, 15, 1, 3),
                  (1, 3, 12, 2, 2), (2, 3, 10, 1, 2),
                  (3, 4, 25, 1, 1)]
    T = 5
    g_dyn = build_time_expanded_graph(5, base_edges, T)
    print(f"  基础节点数=5, 时间层数={T}, 扩展后总节点数={g_dyn.n}")

    # ---- 可视化 ----
    print("\n[4] 可视化")
    g_vis = _build_demo_graph()
    _, flows_vis = edmonds_karp(g_vis, source, sink)
    plot_flow_network(g_vis, flows_vis, "Water Distribution Network")
    print("  完成。")
