"""
NSGA-II (Non-dominated Sorting Genetic Algorithm II) 多目标优化模板
适用：多目标函数存在冲突、需要帕累托前沿的问题
     如成本-质量权衡、风险-收益优化、多指标评价
问题适配点：
  1. 修改 Individual.evaluate() —— 定义多个目标函数
  2. 修改 Individual.make_random() —— 修改变量范围和维度
  3. 修改 constraint_violation() —— 添加问题约束
  4. 调整 GA 参数 (pop_size, pc, pm, max_gen)
参考：Deb et al., IEEE TEC 2002
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Optional


class Individual:
    """个体：决策变量 + 目标值"""
    __slots__ = ('x', 'objectives', 'rank', 'crowding_dist', 'constraint_viol')

    def __init__(self, x: np.ndarray):
        self.x = x
        self.objectives: np.ndarray = np.array([])
        self.rank = np.inf
        self.crowding_dist = 0.0
        self.constraint_viol = 0.0

    @classmethod
    def make_random(cls, n_var: int = 10, bounds: tuple = (0.0, 1.0)):
        """随机生成个体 —— 比赛中需调整变量维度和范围"""
        # TODO: 替换 bounds 为实际问题范围, n_var 为变量个数
        x = np.random.uniform(bounds[0], bounds[1], n_var)
        return cls(x)

    def evaluate(self):
        """多目标函数计算 —— 比赛中需替换"""
        # TODO: 替换为实际的多目标函数
        # 示例：ZDT1 测试问题 (minimize f1, f2)
        n = len(self.x)
        f1 = self.x[0]
        g = 1.0 + 9.0 * np.sum(self.x[1:]) / (n - 1)
        f2 = g * (1.0 - np.sqrt(f1 / g))
        self.objectives = np.array([f1, f2])

    def constraint_violation(self) -> float:
        """约束违反度 —— 比赛中根据实际问题添加"""
        # TODO: 添加实际约束，返回 >0 表示违反
        return 0.0

    def dominates(self, other: 'Individual') -> bool:
        """Pareto 支配关系 (最小化问题)"""
        if self.constraint_viol < other.constraint_viol:
            return True
        if self.constraint_viol > other.constraint_viol:
            return False
        return np.all(self.objectives <= other.objectives) and \
               np.any(self.objectives < other.objectives)


class NSGA2:
    """NSGA-II 求解器"""

    def __init__(self, pop_size: int = 100, max_gen: int = 200,
                 pc: float = 0.9, pm: float = 0.1,
                 n_var: int = 10, bounds: tuple = (0.0, 1.0)):
        self.pop_size = pop_size
        self.max_gen = max_gen
        self.pc = pc
        self.pm = pm
        self.n_var = n_var
        self.bounds = bounds
        self.population: List[Individual] = []
        self.front_history: List[np.ndarray] = []  # 跟踪每代前沿目标值

    def _init_population(self):
        self.population = [Individual.make_random(self.n_var, self.bounds)
                           for _ in range(self.pop_size)]
        for ind in self.population:
            ind.evaluate()

    def _non_dominated_sort(self, pop: List[Individual]):
        """快速非支配排序 (Deb 2002)"""
        fronts = [[]]
        for p in pop:
            p.n_dominated = 0  # type: ignore
            p.dominates_list = []  # type: ignore
            for q in pop:
                if p is q:
                    continue
                if p.dominates(q):
                    p.dominates_list.append(q)  # type: ignore
                elif q.dominates(p):
                    p.n_dominated += 1  # type: ignore
            if p.n_dominated == 0:  # type: ignore
                p.rank = 0
                fronts[0].append(p)

        i = 0
        while fronts[i]:
            next_front = []
            for p in fronts[i]:
                for q in p.dominates_list:  # type: ignore
                    q.n_dominated -= 1  # type: ignore
                    if q.n_dominated == 0:  # type: ignore
                        q.rank = i + 1
                        next_front.append(q)
            i += 1
            if next_front:
                fronts.append(next_front)
            else:
                break
        return fronts

    def _crowding_distance(self, front: List[Individual]):
        """拥挤度距离计算"""
        if not front:
            return
        for ind in front:
            ind.crowding_dist = 0.0
        n_obj = len(front[0].objectives)
        for m in range(n_obj):
            front.sort(key=lambda ind: ind.objectives[m])
            front[0].crowding_dist = front[-1].crowding_dist = np.inf
            f_min, f_max = front[0].objectives[m], front[-1].objectives[m]
            if f_max == f_min:
                continue
            for i in range(1, len(front) - 1):
                front[i].crowding_dist += \
                    (front[i + 1].objectives[m] - front[i - 1].objectives[m]) / (f_max - f_min)

    def _tournament_select(self) -> Individual:
        """锦标赛选择 (rank 优先, 拥挤度 tie-break)"""
        a, b = np.random.choice(len(self.population), 2, replace=False)
        p1, p2 = self.population[a], self.population[b]
        if p1.rank < p2.rank:
            return p1
        if p1.rank > p2.rank:
            return p2
        return p1 if p1.crowding_dist > p2.crowding_dist else p2

    def _crossover_sbx(self, p1: np.ndarray, p2: np.ndarray, eta: float = 20) -> tuple:
        """SBX 交叉 (复用 ga_template.py 实现)"""
        c1, c2 = p1.copy(), p2.copy()
        for i in range(self.n_var):
            if np.random.random() < self.pc:
                if abs(p1[i] - p2[i]) > 1e-10:
                    u = np.random.random()
                    beta = (2 * u) ** (1 / (eta + 1)) if u <= 0.5 \
                        else (1 / (2 * (1 - u))) ** (1 / (eta + 1))
                    c1[i] = 0.5 * ((1 + beta) * p1[i] + (1 - beta) * p2[i])
                    c2[i] = 0.5 * ((1 - beta) * p1[i] + (1 + beta) * p2[i])
            lo, hi = self.bounds[0], self.bounds[1]
            c1[i] = np.clip(c1[i], lo, hi)
            c2[i] = np.clip(c2[i], lo, hi)
        return c1, c2

    def _mutate_polynomial(self, x: np.ndarray, eta: float = 20) -> np.ndarray:
        """多项式变异 (复用 ga_template.py 实现)"""
        mutant = x.copy()
        lo, hi = self.bounds[0], self.bounds[1]
        for i in range(self.n_var):
            if np.random.random() < self.pm:
                u = np.random.random()
                delta = min(mutant[i] - lo, hi - mutant[i]) / (hi - lo + 1e-10)
                if u <= 0.5:
                    dq = (2 * u + (1 - 2 * u) * (1 - delta) ** (eta + 1)) ** (1 / (eta + 1)) - 1
                else:
                    dq = 1 - (2 * (1 - u) + 2 * (u - 0.5) * (1 - delta) ** (eta + 1)) ** (1 / (eta + 1))
                mutant[i] += dq * (hi - lo)
                mutant[i] = np.clip(mutant[i], lo, hi)
        return mutant

    def run(self, verbose: bool = True) -> List[Individual]:
        """运行 NSGA-II，返回最终种群"""
        self._init_population()
        for gen in range(self.max_gen):
            # 生成子代
            offspring = []
            while len(offspring) < self.pop_size:
                p1 = self._tournament_select()
                p2 = self._tournament_select()
                c1_x, c2_x = self._crossover_sbx(p1.x, p2.x)
                c1_x = self._mutate_polynomial(c1_x)
                c2_x = self._mutate_polynomial(c2_x)
                c1, c2 = Individual(c1_x), Individual(c2_x)
                c1.evaluate(), c2.evaluate()
                offspring.extend([c1, c2])
            offspring = offspring[:self.pop_size]

            # 合并 + 非支配排序 + 拥挤度选择
            combined = self.population + offspring
            fronts = self._non_dominated_sort(combined)
            self.population = []
            for front in fronts:
                if len(self.population) + len(front) <= self.pop_size:
                    self.population.extend(front)
                else:
                    self._crowding_distance(front)
                    front.sort(key=lambda ind: ind.crowding_dist, reverse=True)
                    needed = self.pop_size - len(self.population)
                    self.population.extend(front[:needed])
                    break

            # 记录前沿
            pf = np.array([ind.objectives for ind in self.population if ind.rank == 0])
            self.front_history.append(pf)

            if verbose and gen % 50 == 0:
                print(f"Gen {gen:4d} | Pareto front size: {len(pf)}")

        return self.population

    def get_pareto_front(self) -> List[Individual]:
        """返回 rank==0 的帕累托前沿"""
        return [ind for ind in self.population if ind.rank == 0]

    def hypervolume(self, ref_point: Optional[np.ndarray] = None) -> float:
        """超体积指标 (Hypervolume Indicator) —— 越大越好

        需要 pygmo 或自行实现 LebMeasure 算法。
        此处提供简化的 Monte Carlo 近似（高维时精度有限）。
        """
        pareto = self.get_pareto_front()
        if not pareto:
            return 0.0
        pts = np.array([ind.objectives for ind in pareto])
        if ref_point is None:
            ref_point = np.max(pts, axis=0) + 1.0
        # Monte Carlo 近似
        n_samples = 100000
        lo = np.min(pts, axis=0)
        hi = ref_point
        samples = np.random.uniform(lo, hi, (n_samples, len(lo)))
        dominated = 0
        for s in samples:
            if np.any(np.all(pts <= s, axis=1)):
                dominated += 1
        return dominated / n_samples * np.prod(hi - lo)

    def plot_pareto(self, save_path: Optional[str] = None):
        """可视化帕累托前沿"""
        pareto = self.get_pareto_front()
        if not pareto:
            print("无帕累托前沿")
            return
        pts = np.array([ind.objectives for ind in pareto])
        # 按第一目标排序画线
        order = np.argsort(pts[:, 0])
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.scatter(pts[:, 0], pts[:, 1], c='steelblue', s=20, label='Pareto Front')
        ax.plot(pts[order, 0], pts[order, 1], 'r--', alpha=0.4)
        ax.set_xlabel('f1 (to minimize)'), ax.set_ylabel('f2 (to minimize)')
        ax.set_title('NSGA-II Pareto Front'), ax.legend(), ax.grid(True, alpha=0.3)
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.show()


# ===== 使用示例：ZDT1 测试问题 =====
if __name__ == "__main__":
    nsga2 = NSGA2(pop_size=100, max_gen=100, pc=0.9, pm=0.1,
                  n_var=10, bounds=(0.0, 1.0))
    nsga2.run()
    pareto = nsga2.get_pareto_front()
    print(f"\n帕累托前沿解个数: {len(pareto)}")
    if pareto:
        print(f"HV (Monte Carlo approx): {nsga2.hypervolume():.4f}")
    nsga2.plot_pareto()
