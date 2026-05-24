"""
整数规划 / 混合整数规划 (Integer / Mixed-Integer Programming) 模板
适用：选址问题、排产调度、任务指派、设施布局等离散决策问题
问题适配点：
  1. 修改 _define_variables() —— 定义决策变量及类型
  2. 修改 _define_constraints() —— 添加约束条件
  3. 修改 _define_objective() —— 设置优化目标
  4. 选择求解器：PuLP（免费）、Gurobi（需 license）、SCIP（开源）
"""

import numpy as np
from scipy.optimize import linprog
from typing import List, Tuple, Dict, Optional


class IntegerProgram:
    """整数规划问题框架（PuLP 为主，Gurobi 为备用）"""

    def __init__(self):
        self.solution = None
        self.objective_value = None
        self.status = None

    def lp_relaxation_bound(self) -> float:
        """LP 松弛下界：将所有整数变量松弛为连续，用 scipy 求解

        Returns
        -------
        LP 松弛的最优目标值（最小化问题提供下界，最大化问题提供上界）
        """
        # TODO: 替换为目标函数的系数和约束矩阵
        # 示例：min c^T x, s.t. A x <= b, x >= 0
        c = np.array([1.0, 2.0])  # 目标系数
        A = np.array([[1.0, 1.0], [2.0, 1.0]])  # 约束矩阵
        b = np.array([4.0, 5.0])  # 右端项
        bounds = [(0, None), (0, None)]

        res = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method='highs')
        if res.success:
            return res.fun
        return np.nan

    def solve_pulp(self, minimize: bool = True) -> Dict:
        """
        使用 PuLP 求解整数规划（推荐首选，开源免费）

        Returns
        -------
        {'status': ..., 'objective': ..., 'variables': {...}}
        """
        try:
            import pulp
        except ImportError:
            raise ImportError("请安装 pulp: pip install pulp")

        # ---- 定义变量 ----
        # TODO: 替换为实际决策变量
        x1 = pulp.LpVariable('x1', lowBound=0, cat='Integer')
        x2 = pulp.LpVariable('x2', lowBound=0, cat='Integer')

        # ---- 定义问题 ----
        sense = pulp.LpMinimize if minimize else pulp.LpMaximize
        prob = pulp.LpProblem("IP_Problem", sense)

        # ---- 目标函数 ----
        # TODO: 替换为实际目标
        prob += 2 * x1 + 3 * x2, "Objective"

        # ---- 约束条件 ----
        # TODO: 替换为实际约束
        prob += x1 + x2 <= 10, "Constraint_1"
        prob += 2 * x1 + x2 >= 5, "Constraint_2"

        # ---- 求解 ----
        prob.solve(pulp.PULP_CBC_CMD(msg=False))

        self.status = pulp.LpStatus[prob.status]
        solution = {
            'status': self.status,
            'objective': pulp.value(prob.objective) if prob.status == pulp.LpStatusOptimal else None,
            'variables': {v.name: v.varValue for v in prob.variables()},
        }
        return solution

    # ===== Gurobi 备用接口 (需 license) =====
    # def solve_gurobi(self, minimize: bool = True) -> Dict:
    #     """使用 Gurobi 求解（需安装 gurobipy 并有有效 license）"""
    #     try:
    #         import gurobipy as gp
    #     except ImportError:
    #         raise ImportError("请安装 gurobipy: pip install gurobipy")
    #
    #     env = gp.Env(empty=True)
    #     env.setParam('OutputFlag', 0)
    #     env.start()
    #     model = gp.Model("MIP", env=env)
    #
    #     # TODO: 替换为实际变量定义
    #     x1 = model.addVar(vtype=gp.GRB.INTEGER, name='x1', lb=0)
    #     x2 = model.addVar(vtype=gp.GRB.INTEGER, name='x2', lb=0)
    #
    #     model.setObjective(2*x1 + 3*x2, gp.GRB.MINIMIZE if minimize else gp.GRB.MAXIMIZE)
    #
    #     # TODO: 替换为实际约束
    #     model.addConstr(x1 + x2 <= 10)
    #     model.addConstr(2*x1 + x2 >= 5)
    #
    #     model.optimize()
    #     status = model.Status
    #     result = {
    #         'status': status,
    #         'objective': model.ObjVal if status == gp.GRB.OPTIMAL else None,
    #         'variables': {v.VarName: v.X for v in model.getVars()},
    #     }
    #     model.dispose()
    #     env.dispose()
    #     return result


# ===== 常用二进制变量建模模式 =====
def binary_patterns_demo():
    """演示常见的 0-1 变量建模技巧 —— 适配竞赛问题时可参考"""
    import pulp

    # 互斥约束：最多选 1 个
    # y1 + y2 + y3 <= 1  (y_i in {0,1})

    # 固定成本/启动约束：x <= M * y
    # 当 y=1 时 x 可 >0, y=0 时 x=0

    # 逻辑条件：若 y1=1 则 y2=1 (y1 => y2)
    # y1 <= y2

    # 半连续变量：x = 0 或 x >= L
    # L * y <= x <= M * y

    # 或者 (either-or) 约束：
    # a1^T x <= b1 + M*(1-y), a2^T x <= b2 + M*y, y in {0,1}

    # SOS1 (Special Ordered Set of type 1)：一组中最多一个非零
    # pulp 中: 对连续变量用分支定界或添加互斥二元变量

    pass  # 仅文档用途


def interpret_solution(solution: Dict):
    """结果解读与格式化输出"""
    if solution['status'] != 'Optimal':
        print(f"求解状态: {solution['status']} — 请检查模型是否可行")
        return
    print(f"最优目标值: {solution['objective']:.4f}")
    print("最优解:")
    for name, val in solution['variables'].items():
        print(f"  {name} = {val}")


# ===== 运行示例：简单设施选址问题 =====
if __name__ == "__main__":
    """
    设施选址问题：从 5 个候选地点中选择若干建仓库，服务 6 个需求点
    目标：总成本（固定成本 + 运输成本）最小
    """
    import pulp

    # 数据
    candidates = [0, 1, 2, 3, 4]          # 候选仓库
    demand_pts = [0, 1, 2, 3, 4, 5]       # 需求点
    fixed_cost = [100, 80, 120, 90, 110]  # 各仓库固定成本
    demand = [30, 25, 35, 20, 40, 15]     # 各需求点需求量
    # 运输成本矩阵 (从仓库 i 到需求点 j)
    transport = np.array([
        [2, 4, 5, 3, 6, 7],
        [5, 3, 2, 6, 4, 8],
        [4, 5, 3, 2, 7, 5],
        [6, 3, 4, 5, 2, 4],
        [3, 6, 7, 4, 3, 2],
    ])

    # 建模
    prob = pulp.LpProblem("Facility_Location", pulp.LpMinimize)

    # 变量：y_i = 1 如果在 i 建仓；x_ij = 从 i 到 j 的运输量
    y = {i: pulp.LpVariable(f'y_{i}', cat='Binary') for i in candidates}
    x = {(i, j): pulp.LpVariable(f'x_{i}_{j}', lowBound=0, cat='Continuous')
         for i in candidates for j in demand_pts}

    # 目标：固定成本 + 运输成本
    prob += (pulp.lpSum(fixed_cost[i] * y[i] for i in candidates) +
             pulp.lpSum(transport[i][j] * x[i, j] for i in candidates for j in demand_pts))

    # 约束 1：每个需求点需求被满足
    for j in demand_pts:
        prob += pulp.lpSum(x[i, j] for i in candidates) == demand[j], f"demand_{j}"

    # 约束 2：只能从已建仓库运输
    M = sum(demand)
    for i in candidates:
        prob += pulp.lpSum(x[i, j] for j in demand_pts) <= M * y[i], f"open_{i}"

    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    print(f"求解状态: {pulp.LpStatus[prob.status]}")
    print(f"最优总成本: {pulp.value(prob.objective):.2f}")
    print("选址决策:", {i: int(y[i].varValue) for i in candidates})
    print("运输方案:")
    for i in candidates:
        for j in demand_pts:
            if x[i, j].varValue > 0.01:
                print(f"  仓库{i} -> 需求点{j}: {x[i, j].varValue:.0f}")

    # 对比 LP 松弛下界
    ip = IntegerProgram()
    lb = ip.lp_relaxation_bound()
    print(f"LP 松弛下界: {lb:.4f}")
