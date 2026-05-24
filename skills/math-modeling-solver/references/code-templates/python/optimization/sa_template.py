"""
模拟退火 (SA) 模板
适用：组合优化/单目标优化
"""

import numpy as np
import math


class SA:
    def __init__(self, obj_func, T0=1000, alpha=0.95, L=100, T_min=0.01, max_iter=5000):
        self.obj = obj_func
        self.T0 = T0
        self.alpha = alpha
        self.L = L
        self.T_min = T_min
        self.max_iter = max_iter
        self.n_var = obj_func.n_var
        self.bounds = obj_func.bounds
        self.history = {'best_fitness': [], 'temperature': []}

    def _random_solution(self):
        x = np.zeros(self.n_var)
        for i in range(self.n_var):
            low, high = self.bounds[i]
            x[i] = np.random.uniform(low, high)
        return x

    def _neighbor(self, x, T):
        """生成邻域解（高斯扰动，幅度随温度减小）"""
        neighbor = x.copy()
        for i in range(self.n_var):
            low, high = self.bounds[i]
            scale = (high - low) * 0.1 * (T / self.T0 + 0.01)
            neighbor[i] += np.random.normal(0, scale)
            neighbor[i] = np.clip(neighbor[i], low, high)
        return neighbor

    def run(self, verbose=True):
        current = self._random_solution()
        current_fit = self.obj.fitness(current)
        best_solution = current.copy()
        best_fitness = current_fit
        T = self.T0

        for it in range(self.max_iter):
            for _ in range(self.L):
                neighbor = self._neighbor(current, T)
                neighbor_fit = self.obj.fitness(neighbor)
                delta = current_fit - neighbor_fit  # 负值=neighbor更好(最小化视角)

                if delta < 0:  # neighbor 更好
                    current = neighbor
                    current_fit = neighbor_fit
                else:
                    p = math.exp(-delta / T)
                    if np.random.random() < p:
                        current = neighbor
                        current_fit = neighbor_fit

                if current_fit > best_fitness:
                    best_solution = current.copy()
                    best_fitness = current_fit

            T *= self.alpha
            self.history['best_fitness'].append(best_fitness)
            self.history['temperature'].append(T)

            if verbose and it % 50 == 0:
                print(f"Iter {it:5d} | T: {T:.3f} | Best: {best_fitness:.6f}")

            if T < self.T_min:
                break

        return best_solution, best_fitness, self.history


if __name__ == "__main__":
    from ga_template import ObjectiveFunction
    obj = ObjectiveFunction()
    sa = SA(obj, T0=1000, alpha=0.95, max_iter=5000)
    solution, fitness, history = sa.run()
    print(f"\n最优解: {solution}")
    print(f"最优适应度: {fitness:.6f}")
