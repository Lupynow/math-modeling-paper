"""
粒子群优化 (PSO) 模板
适用：连续变量非线性优化
问题适配点：
  1. 修改 objective() 和 constraint_penalty() 方法
  2. 修改 bounds
  3. 调整 PSO 参数
"""

import numpy as np


class PSO:
    def __init__(self, obj_func, n_particles=30, max_iter=200,
                 w_start=0.9, w_end=0.4, c1=2.0, c2=2.0,
                 tol=1e-6, patience=50):
        self.obj = obj_func
        self.n_particles = n_particles
        self.max_iter = max_iter
        self.w_start = w_start
        self.w_end = w_end
        self.c1 = c1
        self.c2 = c2
        self.tol = tol
        self.patience = patience
        self.n_var = obj_func.n_var
        self.bounds = obj_func.bounds
        self.history = {'best_fitness': [], 'avg_fitness': []}

    def _init_swarm(self):
        positions = np.zeros((self.n_particles, self.n_var))
        velocities = np.zeros((self.n_particles, self.n_var))
        for i in range(self.n_var):
            low, high = self.bounds[i]
            positions[:, i] = np.random.uniform(low, high, self.n_particles)
            velocities[:, i] = np.random.uniform(-abs(high - low) * 0.1,
                                                  abs(high - low) * 0.1,
                                                  self.n_particles)
        return positions, velocities

    def _evaluate(self, positions):
        return np.array([self.obj.fitness(p) for p in positions])

    def run(self, verbose=True):
        positions, velocities = self._init_swarm()
        fitness = self._evaluate(positions)

        pbest_positions = positions.copy()
        pbest_fitness = fitness.copy()

        gbest_idx = np.argmax(fitness)
        gbest_position = positions[gbest_idx].copy()
        gbest_fitness = fitness[gbest_idx]

        no_improve = 0

        for it in range(self.max_iter):
            w = self.w_start - (self.w_start - self.w_end) * it / self.max_iter

            r1 = np.random.random((self.n_particles, self.n_var))
            r2 = np.random.random((self.n_particles, self.n_var))

            velocities = (w * velocities +
                          self.c1 * r1 * (pbest_positions - positions) +
                          self.c2 * r2 * (gbest_position - positions))

            # 速度限制
            for i in range(self.n_var):
                v_max = abs(self.bounds[i][1] - self.bounds[i][0]) * 0.2
                velocities[:, i] = np.clip(velocities[:, i], -v_max, v_max)

            positions = positions + velocities

            # 位置边界处理
            for i in range(self.n_var):
                low, high = self.bounds[i]
                positions[:, i] = np.clip(positions[:, i], low, high)

            fitness = self._evaluate(positions)

            # 更新个体最优
            improved = fitness > pbest_fitness
            pbest_positions[improved] = positions[improved]
            pbest_fitness[improved] = fitness[improved]

            # 更新全局最优
            if np.max(fitness) > gbest_fitness + self.tol:
                gbest_idx = np.argmax(fitness)
                gbest_position = positions[gbest_idx].copy()
                gbest_fitness = fitness[gbest_idx]
                no_improve = 0
            else:
                no_improve += 1

            self.history['best_fitness'].append(gbest_fitness)
            self.history['avg_fitness'].append(np.mean(fitness))

            if verbose and it % 20 == 0:
                print(f"Iter {it:4d} | Best: {gbest_fitness:.6f}")

            if no_improve >= self.patience:
                if verbose:
                    print(f"收敛于第 {it} 次迭代")
                break

        return gbest_position, gbest_fitness, self.history


if __name__ == "__main__":
    from ga_template import ObjectiveFunction
    obj = ObjectiveFunction()
    pso = PSO(obj, n_particles=30, max_iter=200)
    solution, fitness, history = pso.run()
    print(f"\n最优解: {solution}")
    print(f"最优适应度: {fitness:.6f}")
