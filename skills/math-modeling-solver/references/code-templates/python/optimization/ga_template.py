"""
遗传算法 (Genetic Algorithm) 模板
适用：单目标/多变量非线性优化
问题适配点：
  1. 修改 ObjectiveFunction 类中的 fitness() 方法
  2. 修改变量范围 bounds
  3. 如含约束，修改 constraint_penalty() 方法
  4. 调整 GA 参数（pop_size, pc, pm, max_gen）
"""

import numpy as np


class ObjectiveFunction:
    """目标函数 + 约束处理"""

    def __init__(self):
        # 变量范围：[(min1, max1), (min2, max2), ...]
        self.bounds = [(0, 10), (0, 10)]  # TODO: 替换为实际问题范围
        self.n_var = len(self.bounds)

    def objective(self, x):
        """
        目标函数
        x: numpy array, 决策变量向量
        返回: 目标函数值（GA 默认最大化，最小化问题请取负）
        """
        # TODO: 替换为实际目标函数
        return -np.sum(x ** 2)  # 示例：最大化 -sum(x^2)

    def constraint_penalty(self, x):
        """
        约束惩罚项
        返回: 0 如果所有约束满足，>0 表示约束违反程度
        """
        penalty = 0.0
        # TODO: 添加实际约束
        # 示例：约束 x[0] + x[1] <= 15
        # if x[0] + x[1] > 15:
        #     penalty += 1e6 * (x[0] + x[1] - 15) ** 2
        return penalty

    def fitness(self, x):
        """适应度 = 目标函数 - 惩罚项"""
        return self.objective(x) - self.constraint_penalty(x)


class GA:
    """遗传算法求解器"""

    def __init__(self, obj_func, pop_size=50, pc=0.8, pm=0.05, max_gen=200,
                 elite_rate=0.05, tol=1e-6, patience=50):
        self.obj = obj_func
        self.pop_size = pop_size
        self.pc = pc
        self.pm = pm
        self.max_gen = max_gen
        self.elite_size = max(1, int(pop_size * elite_rate))
        self.tol = tol
        self.patience = patience
        self.n_var = obj_func.n_var
        self.bounds = obj_func.bounds
        self.history = {'best_fitness': [], 'avg_fitness': []}

    def _init_population(self):
        """初始化种群（实数编码，均匀分布）"""
        pop = np.zeros((self.pop_size, self.n_var))
        for i in range(self.n_var):
            low, high = self.bounds[i]
            pop[:, i] = np.random.uniform(low, high, self.pop_size)
        return pop

    def _evaluate(self, pop):
        """计算种群适应度"""
        return np.array([self.obj.fitness(ind) for ind in pop])

    def _select_tournament(self, pop, fitness, k=3):
        """锦标赛选择"""
        selected = np.zeros_like(pop)
        for i in range(self.pop_size):
            candidates = np.random.choice(self.pop_size, k, replace=False)
            winner = candidates[np.argmax(fitness[candidates])]
            selected[i] = pop[winner]
        return selected

    def _crossover_sbx(self, parent1, parent2, eta=20):
        """模拟二进制交叉 (SBX)"""
        child1, child2 = parent1.copy(), parent2.copy()
        for i in range(self.n_var):
            if np.random.random() < self.pc:
                if abs(parent1[i] - parent2[i]) > 1e-10:
                    u = np.random.random()
                    if u <= 0.5:
                        beta = (2 * u) ** (1 / (eta + 1))
                    else:
                        beta = (1 / (2 * (1 - u))) ** (1 / (eta + 1))
                    child1[i] = 0.5 * ((1 + beta) * parent1[i] + (1 - beta) * parent2[i])
                    child2[i] = 0.5 * ((1 - beta) * parent1[i] + (1 + beta) * parent2[i])
            # 边界修正
            low, high = self.bounds[i]
            child1[i] = np.clip(child1[i], low, high)
            child2[i] = np.clip(child2[i], low, high)
        return child1, child2

    def _mutate_polynomial(self, individual, eta=20):
        """多项式变异"""
        mutant = individual.copy()
        for i in range(self.n_var):
            if np.random.random() < self.pm:
                u = np.random.random()
                low, high = self.bounds[i]
                delta = min(mutant[i] - low, high - mutant[i]) / (high - low + 1e-10)
                if u <= 0.5:
                    delta_q = (2 * u + (1 - 2 * u) * (1 - delta) ** (eta + 1)) ** (1 / (eta + 1)) - 1
                else:
                    delta_q = 1 - (2 * (1 - u) + 2 * (u - 0.5) * (1 - delta) ** (eta + 1)) ** (1 / (eta + 1))
                mutant[i] += delta_q * (high - low)
                mutant[i] = np.clip(mutant[i], low, high)
        return mutant

    def run(self, verbose=True):
        """运行 GA，返回最优解和最优适应度"""
        pop = self._init_population()
        fitness = self._evaluate(pop)

        best_fitness = np.max(fitness)
        best_idx = np.argmax(fitness)
        best_solution = pop[best_idx].copy()
        no_improve = 0

        for gen in range(self.max_gen):
            # 精英保留
            elite_indices = np.argsort(fitness)[-self.elite_size:]
            elites = pop[elite_indices].copy()

            # 选择
            selected = self._select_tournament(pop, fitness)

            # 交叉
            offspring = np.zeros_like(pop)
            for i in range(0, self.pop_size, 2):
                if i + 1 < self.pop_size:
                    c1, c2 = self._crossover_sbx(selected[i], selected[i + 1])
                    offspring[i], offspring[i + 1] = c1, c2
                else:
                    offspring[i] = selected[i]

            # 变异
            for i in range(self.pop_size):
                offspring[i] = self._mutate_polynomial(offspring[i])

            # 精英替换
            offspring[:self.elite_size] = elites

            pop = offspring
            fitness = self._evaluate(pop)

            gen_best = np.max(fitness)
            avg_fit = np.mean(fitness)
            self.history['best_fitness'].append(gen_best)
            self.history['avg_fitness'].append(avg_fit)

            if gen_best > best_fitness + self.tol:
                best_fitness = gen_best
                best_solution = pop[np.argmax(fitness)].copy()
                no_improve = 0
            else:
                no_improve += 1

            if verbose and gen % 20 == 0:
                print(f"Gen {gen:4d} | Best: {best_fitness:.6f} | Avg: {avg_fit:.6f}")

            if no_improve >= self.patience:
                if verbose:
                    print(f"收敛于第 {gen} 代")
                break

        return best_solution, best_fitness, self.history


# ===== 使用示例 =====
if __name__ == "__main__":
    obj = ObjectiveFunction()
    ga = GA(obj, pop_size=50, pc=0.8, pm=0.05, max_gen=200)
    solution, fitness, history = ga.run()

    print(f"\n最优解: {solution}")
    print(f"最优适应度: {fitness:.6f}")

    # 收敛曲线（可选）
    import matplotlib.pyplot as plt
    plt.plot(history['best_fitness'], label='Best')
    plt.plot(history['avg_fitness'], label='Avg', alpha=0.6)
    plt.xlabel('Generation')
    plt.ylabel('Fitness')
    plt.legend()
    plt.title('GA Convergence')
    plt.show()
