"""
高斯混合模型 (Gaussian Mixture Model) — EM算法实现
======================================================
适用场景：
  - 数据聚类，尤其是簇呈椭圆形状、重叠、或大小不一时
  - 密度估计（生成式模型）：估计数据的概率密度分布
  - 异常检测：低概率区域数据点视为异常
  - 软聚类：每个点给出属于各簇的概率（soft assignment）

何时优于 K-Means：
  - 簇呈拉长形状（非圆形）→ GMM 通过协方差矩阵捕获方向性
  - 需要软分配（概率）而非硬分配 → 下游不确定性传递
  - 需要概率密度 → 生成新样本、评估新点似然
  - 簇大小/密度不均 → K-Means 偏向均匀大小

何时回到 K-Means / DBSCAN：
  - 计算资源极度受限（EM每轮 O(n*k*d^2) vs K-Means O(n*k*d)）
  - 簇形状不规则（非椭圆）→ DBSCAN
  - 样本量 < 维度的 10 倍 → 协方差估计不稳定

模型选择（选几个分量 K）：
  - BIC：对参数数量惩罚更重，偏好简洁模型（建模竞赛推荐）
  - AIC：可能选偏多分量，适用于预测而非解释场景

问题适配点（需替换的 TODO 标记）：
  1. 修改 _demo_data() 为实际数据加载
  2. 修改 K_range 分量数搜索范围
  3. 如需要，调整 max_iter 和 tol 收敛参数
  4. 对于文本/图像等非表格数据，先将特征转换为数值向量
"""
import numpy as np
from scipy.stats import multivariate_normal
from sklearn.mixture import GaussianMixture as SklearnGMM
import matplotlib.pyplot as plt


class GMM:
    """高斯混合模型 — 从零实现 EM 算法"""

    def __init__(self, n_components: int = 3, max_iter: int = 100,
                 tol: float = 1e-4, random_state: int = 42):
        self.K = n_components
        self.max_iter = max_iter
        self.tol = tol
        self.rng = np.random.RandomState(random_state)
        self.weights_ = None          # 混合系数 (K,)
        self.means_ = None            # 均值 (K, d)
        self.covariances_ = None      # 协方差 (K, d, d)
        self.log_likelihood_ = []

    def _initialize(self, X: np.ndarray):
        """K-Means++风格的初始化"""
        n, d = X.shape
        # 随机选第一个中心
        idx = self.rng.choice(n, 1)
        self.means_ = X[idx].copy()
        for _ in range(1, self.K):
            # D^2 weighting
            dist_sq = np.array([np.min(np.sum((X - m) ** 2, axis=1))
                                for m in self.means_])
            dist_sq = np.min(
                np.array([np.sum((X[:, None] - self.means_) ** 2, axis=2)]), axis=1)
            probs = dist_sq / dist_sq.sum()
            new_idx = self.rng.choice(n, 1, p=probs)
            self.means_ = np.vstack([self.means_, X[new_idx]])
        self.covariances_ = np.array([np.cov(X.T) + 1e-3 * np.eye(d)
                                      for _ in range(self.K)])
        self.weights_ = np.ones(self.K) / self.K

    def _e_step(self, X: np.ndarray) -> np.ndarray:
        """E-step: 计算后验概率（责任矩阵）"""
        n = X.shape[0]
        resp = np.zeros((n, self.K))
        for k in range(self.K):
            resp[:, k] = self.weights_[k] * multivariate_normal.pdf(
                X, mean=self.means_[k], cov=self.covariances_[k],
                allow_singular=True)
        resp_sum = resp.sum(axis=1, keepdims=True)
        resp_sum = np.where(resp_sum < 1e-300, 1e-300, resp_sum)
        return resp / resp_sum

    def _m_step(self, X: np.ndarray, resp: np.ndarray):
        """M-step: 更新参数"""
        n, d = X.shape
        nk = resp.sum(axis=0) + 1e-12
        self.weights_ = nk / n
        # 更新均值
        self.means_ = (resp.T @ X) / nk[:, np.newaxis]
        # 更新协方差
        for k in range(self.K):
            diff = X - self.means_[k]
            self.covariances_[k] = ((resp[:, k][:, np.newaxis] * diff).T @ diff
                                    / nk[k])
            # 正则化防奇异
            self.covariances_[k] += 1e-6 * np.eye(d)

    def fit(self, X: np.ndarray):
        """训练 GMM"""
        self._initialize(X)
        prev_ll = -np.inf
        for it in range(self.max_iter):
            resp = self._e_step(X)
            self._m_step(X, resp)
            # 对数似然
            ll = 0.0
            for k in range(self.K):
                ll += self.weights_[k] * multivariate_normal.pdf(
                    X, mean=self.means_[k], cov=self.covariances_[k],
                    allow_singular=True)
            ll = np.sum(np.log(np.maximum(ll, 1e-300)))
            self.log_likelihood_.append(ll)
            if abs(ll - prev_ll) < self.tol:
                break
            prev_ll = ll
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """返回硬聚类标签"""
        resp = self._e_step(X)
        return np.argmax(resp, axis=1)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """返回软分配概率"""
        return self._e_step(X)

    def bic(self, X: np.ndarray) -> float:
        """BIC (Bayesian Information Criterion)"""
        n, d = X.shape
        # 参数个数：K-1 (weights) + K*d (means) + K*d*(d+1)/2 (covariances)
        n_params = (self.K - 1) + self.K * d + self.K * d * (d + 1) // 2
        ll = self.log_likelihood_[-1]
        return n_params * np.log(n) - 2 * ll

    def aic(self, X: np.ndarray) -> float:
        """AIC (Akaike Information Criterion)"""
        n, d = X.shape
        n_params = (self.K - 1) + self.K * d + self.K * d * (d + 1) // 2
        ll = self.log_likelihood_[-1]
        return 2 * n_params - 2 * ll


# ======================== 可视化 ========================

def plot_gmm_ellipses(X: np.ndarray, gmm: GMM, title: str = "GMM Result"):
    """绘制数据散点 + 各高斯分量的椭圆等高线"""
    from matplotlib.patches import Ellipse

    fig, ax = plt.subplots(figsize=(6, 5))
    labels = gmm.predict(X)
    sc = ax.scatter(X[:, 0], X[:, 1], c=labels, cmap='viridis',
                    s=15, alpha=0.6, edgecolors='none')
    ax.set_xlabel('x1'), ax.set_ylabel('x2')

    colors = plt.cm.viridis(np.linspace(0, 1, gmm.K))
    for k in range(gmm.K):
        mean = gmm.means_[k]
        cov = gmm.covariances_[k]
        # 特征分解获取椭圆参数
        vals, vecs = np.linalg.eigh(cov)
        angle = np.degrees(np.arctan2(vecs[1, 0], vecs[0, 0]))
        width, height = 2 * np.sqrt(vals)
        for std in [1, 2]:
            ell = Ellipse(xy=mean, width=std * width, height=std * height,
                          angle=angle, edgecolor=colors[k], facecolor='none',
                          linewidth=1.2 - 0.2 * (std - 1), alpha=0.6)
            ax.add_patch(ell)
        ax.scatter(*mean, c=[colors[k]], marker='x', s=80, linewidths=2)
    ax.set_title(title)
    plt.tight_layout()
    plt.savefig('gmm_result.png', dpi=150)
    plt.close()
    print("[可视化] 已保存 gmm_result.png")


# ======================== 辅助函数 ========================

def _generate_demo_data():
    """生成 3 分量 2D 混合高斯数据"""
    # TODO: 替换为实际数据加载（pd.read_csv 等）
    rng = np.random.RandomState(42)
    n = 300
    X = np.vstack([
        rng.multivariate_normal([0, 0], [[2, 1.2], [1.2, 0.8]], n),
        rng.multivariate_normal([5, 3], [[1.5, -0.5], [-0.5, 2.5]], n),
        rng.multivariate_normal([-2, 5], [[1.2, 0], [0, 0.3]], n // 2),
    ])
    return X


# ======================== 运行示例 ========================

if __name__ == "__main__":
    print("=" * 55)
    print("高斯混合模型 (GMM) — EM算法模板 — 3分量2D演示")
    print("=" * 55)

    X = _generate_demo_data()

    # ---- 模型选择：BIC/AIC 搜索最优 K ----
    # TODO: 根据实际数据复杂度调整 K_range
    print("\n[1] 模型选择 (BIC / AIC)")
    K_range = range(1, 8)
    bics, aics = [], []
    models = {}
    for k in K_range:
        gmm = GMM(n_components=k).fit(X)
        models[k] = gmm
        bics.append(gmm.bic(X))
        aics.append(gmm.aic(X))
        print(f"  K={k}: BIC={bics[-1]:.1f}, AIC={aics[-1]:.1f}")

    best_k = K_range[np.argmin(bics)]
    print(f"  BIC最优K = {best_k}")

    # ---- 从零实现的 GMM ----
    print(f"\n[2] 最终模型 (K={best_k})")
    gmm_own = GMM(n_components=best_k).fit(X)
    print(f"  对数似然: {gmm_own.log_likelihood_[-1]:.2f}")
    print(f"  混合权重: {np.round(gmm_own.weights_, 3)}")

    # ---- sklearn 验证 ----
    print(f"\n[3] sklearn 基准对比 (K={best_k})")
    gmm_sk = SklearnGMM(n_components=best_k, covariance_type='full',
                        random_state=42).fit(X)
    print(f"  sklearn 对数似然: {gmm_sk.lower_bound_:.2f}")
    print(f"  sklearn 混合权重: {np.round(gmm_sk.weights_, 3)}")
    print(f"  (注意: sklearn使用不同的初始化，似然值有差异属正常)")

    # ---- 可视化 ----
    print("\n[4] 可视化")
    plot_gmm_ellipses(X, gmm_own, f"GMM (K={best_k}) — Own Implementation")
    # 对比 sklearn
    gmm_sk_wrap = type('obj', (object,), {
        'K': best_k,
        'means_': gmm_sk.means_,
        'covariances_': gmm_sk.covariances_,
        'predict': lambda self, X: gmm_sk.predict(X),
    })()
    # plot_gmm_ellipses 需要 predict 方法，用 sklearn 结果
    labels_sk = gmm_sk.predict(X)

    from matplotlib.patches import Ellipse
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(X[:, 0], X[:, 1], c=labels_sk, cmap='plasma', s=15, alpha=0.6)
    colors = plt.cm.plasma(np.linspace(0, 1, best_k))
    for k in range(best_k):
        mean = gmm_sk.means_[k]
        cov = gmm_sk.covariances_[k]
        vals, vecs = np.linalg.eigh(cov)
        angle = np.degrees(np.arctan2(vecs[1, 0], vecs[0, 0]))
        width, height = 2 * np.sqrt(vals)
        for std in [1, 2]:
            ell = Ellipse(xy=mean, width=std * width, height=std * height,
                          angle=angle, edgecolor=colors[k], facecolor='none',
                          linewidth=1.2, alpha=0.6)
            ax.add_patch(ell)
        ax.scatter(*mean, c=[colors[k]], marker='x', s=80, linewidths=2)
    ax.set_title(f"GMM (K={best_k}) — sklearn Benchmark")
    plt.tight_layout()
    plt.savefig('gmm_sklearn.png', dpi=150)
    plt.close()
    print("[可视化] 已保存 gmm_sklearn.png")
    print("\n完成。")
