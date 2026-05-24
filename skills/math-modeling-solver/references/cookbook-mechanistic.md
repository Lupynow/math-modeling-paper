# 机理/物理建模手册

覆盖：热传导与扩散、ODE 建模与求解、几何/运动学建模、光学/辐射建模、流体/压力系统、振动/波动系统

---

## 机理建模方法选择速查

| 问题特征 | 推荐方法 | 典型赛题 |
|---------|---------|---------|
| 温度随时间/空间变化 | 热传导 PDE + FDM | 2018A 高温作业服、2020A 回焊炉 |
| 系统状态随时间演化 | ODE 方程组 + solve_ivp | 2019A 高压油管、2022A 波浪能 |
| 运动轨迹/空间布局（无 PDE） | 几何/运动学模型 | 2024A 板凳龙、2021A FAST、2023B 测线 |
| 光能传输/反射/聚焦 | 光学模型 + 光线追迹 | 2023A 定日镜、2021A FAST |
| 流体压力/流量/密度关系 | Bernoulli + PVT + 管道流 | 2019A 高压油管 |
| 振动/波动/能量转换 | 质量-弹簧-阻尼 ODE | 2022A 波浪能 |

---

## 1. 热传导/扩散建模

### 物理背景

热传导问题在数学建模 A 题中反复出现，核心是求解温度场在时间和空间上的分布。2018A 高温作业服要求在高温环境下设计隔热层，2020A 回焊炉要求控制焊接温度曲线。两个问题的本质都是求解热传导偏微分方程。

### 控制方程

**一维 Fourier 热传导方程**：

$$\frac{\partial T}{\partial t} = \alpha \frac{\partial^2 T}{\partial x^2}$$

其中 $\alpha = \frac{k}{\rho c_p}$ 为热扩散系数（m^2/s），$k$ 为导热系数（W/(m·K)），$\rho$ 为密度，$c_p$ 为比热容。

当存在内热源时，方程为：

$$\frac{\partial T}{\partial t} = \alpha \frac{\partial^2 T}{\partial x^2} + \frac{q(x,t)}{\rho c_p}$$

**稳态情况**（$\partial T/\partial t = 0$）退化为：

$$\frac{d^2 T}{dx^2} = 0 \quad \Rightarrow \quad T(x) = C_1 x + C_2$$

### 边界条件

| 类型 | 数学表达 | 物理意义 |
|------|---------|---------|
| Dirichlet（第一类） | $T(0, t) = T_0$ | 边界温度固定，如接触恒温热源 |
| Neumann（第二类） | $-k\frac{\partial T}{\partial x}\big|_{x=0} = q_0$ | 边界热流密度固定，如绝热边界 $q_0=0$ |
| Robin（第三类） | $-k\frac{\partial T}{\partial x}\big|_{x=0} = h(T - T_\infty)$ | 对流换热边界，$h$ 为对流换热系数 |

**多层介质界面条件**：在两种材料的界面处，温度和热流连续：

$$T_1\big|_{x=L} = T_2\big|_{x=L}, \quad k_1\frac{\partial T_1}{\partial x}\bigg|_{x=L} = k_2\frac{\partial T_2}{\partial x}\bigg|_{x=L}$$

### 有限差分法 (FDM) 离散

将空间域 $[0, L]$ 划分为 $N$ 个等距节点，步长 $\Delta x = L/N$。时间步长 $\Delta t$。

记 $T_i^n = T(x_i, t_n)$，其中 $x_i = i\Delta x$，$t_n = n\Delta t$。

**显式格式 (Forward Euler)**：

$$\frac{T_i^{n+1} - T_i^n}{\Delta t} = \alpha \frac{T_{i+1}^n - 2T_i^n + T_{i-1}^n}{(\Delta x)^2}$$

直接递推：

$$T_i^{n+1} = T_i^n + \frac{\alpha \Delta t}{(\Delta x)^2}(T_{i+1}^n - 2T_i^n + T_{i-1}^n)$$

**CFL 稳定性条件**：显式格式稳定的充要条件是

$$r = \frac{\alpha \Delta t}{(\Delta x)^2} \leq \frac{1}{2}$$

不满足 CFL 条件时数值解会指数发散。这是显式格式最大的限制——空间网格细一倍，时间步长必须缩小四倍。

**隐式格式 (Backward Euler)**：

$$\frac{T_i^{n+1} - T_i^n}{\Delta t} = \alpha \frac{T_{i+1}^{n+1} - 2T_i^{n+1} + T_{i-1}^{n+1}}{(\Delta x)^2}$$

每步需解三对角线性方程组：$A T^{n+1} = T^n$，其中

$$A = \begin{bmatrix}
1+2r & -r & & \\
-r & 1+2r & -r & \\
& \ddots & \ddots & \ddots \\
& & -r & 1+2r
\end{bmatrix}$$

隐式格式**无条件稳定**，但每步需要解方程，计算量大于显式。

**Crank-Nicolson 格式**（推荐）：

$$\frac{T_i^{n+1} - T_i^n}{\Delta t} = \frac{\alpha}{2}\left(\frac{T_{i+1}^{n+1} - 2T_i^{n+1} + T_{i-1}^{n+1}}{(\Delta x)^2} + \frac{T_{i+1}^n - 2T_i^n + T_{i-1}^n}{(\Delta x)^2}\right)$$

Crank-Nicolson 是**无条件稳定**且**二阶精度**的格式（显式和隐式均为一阶），是建模竞赛中的首选方案。

### Python 实现模板

```python
import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import spsolve

def solve_heat_1d_cn(L, T_total, Nx, Nt, alpha, T_left, T_right, T_init):
    """Crank-Nicolson 求解 1D 热传导方程
    
    Args:
        L: 空间域长度 (m)
        T_total: 总时间 (s)
        Nx: 空间节点数
        Nt: 时间步数
        alpha: 热扩散系数 (m^2/s)
        T_left, T_right: 左右边界温度 (Dirichlet)
        T_init: 初始温度分布 (array of length Nx+1)
    """
    dx = L / Nx
    dt = T_total / Nt
    r = alpha * dt / (dx * dx)
    
    x = np.linspace(0, L, Nx + 1)
    T = T_init.copy()
    
    # 构造三对角矩阵 A (LHS of C-N)
    main_diag = (1 + r) * np.ones(Nx - 1)
    off_diag = (-r / 2) * np.ones(Nx - 2)
    A = diags([off_diag, main_diag, off_diag], [-1, 0, 1], format='csr')
    
    for n in range(Nt):
        # 右端项 b = (I - (r/2)*D2) * T_interior
        b = np.zeros(Nx - 1)
        for i in range(1, Nx):
            idx = i - 1
            b[idx] = T[i] + (r / 2) * (T[i+1] - 2*T[i] + T[i-1])
        # Dirichlet 边界贡献
        b[0] += (r / 2) * T_left
        b[-1] += (r / 2) * T_right
        
        T_interior = spsolve(A, b)
        T[1:Nx] = T_interior
        T[0], T[-1] = T_left, T_right
    
    return x, T
```

### 参数估计：最小二乘拟合

已知实验温度曲线，需要反推材料的热扩散系数 $\alpha$。建立优化问题：

$$\min_{\alpha} \sum_{j=1}^{M} \left(T_{\text{sim}}(x_{\text{obs}}, t_j; \alpha) - T_{\text{obs}}(t_j)\right)^2$$

其中 $T_{\text{sim}}$ 是数值解 PDE 得到的温度。

```python
from scipy.optimize import minimize

def fit_alpha(observed_temp, times):
    """最小二乘拟合热扩散系数 alpha"""
    def objective(alpha):
        x, T_sim = solve_heat_1d_cn(L, T_total, Nx, Nt, alpha[0], ...)
        T_at_obs = np.interp(times, np.linspace(0, T_total, Nt+1), T_sim[obs_idx])
        return np.sum((T_at_obs - observed_temp) ** 2)
    
    res = minimize(objective, x0=[1e-5], bounds=[(1e-9, 1e-2)])
    return res.x[0]
```

**MATLAB 对照**：用 `pdepe` 求解一维热传导 PDE，用 `lsqcurvefit` 做参数拟合。

```matlab
% PDE 求解
m = 0;  % 对称性参数 (0=平板, 1=圆柱, 2=球)
sol = pdepe(m, @heatpde, @heatic, @heatbc, x, t);

% 参数拟合
alpha_fit = lsqcurvefit(@(alpha, t) forward_model(alpha, t), alpha0, t_obs, T_obs, lb, ub);
```

### 典型赛题

- **2018A 高温作业服**：三层介质（外层织物 + 隔热层 + 内层织物）的 1D 热传导，Robin 边界条件（对流换热）。核心是求解稳态温度分布，验证隔热层厚度是否满足安全要求（假人皮肤温度 < 47°C）。参数求解：反推隔热层的热传导系数。
- **2020A 回焊炉**：焊接区域经过多个温区（预热→恒温→回流→冷却），本质是移动边界条件下的瞬态热传导。需要根据给定的炉温曲线反推传送带速度和各温区设定温度。关键技巧：将传送带运动转化为对流换热系数的空间变化。

---

## 2. ODE 建模与求解

### 问题识别

当题目涉及「系统状态随时间的演化速率」时，应当建立 ODE 模型。典型的 ODE 赛题特征：
- 问题描述中出现「速率」「变化率」「随时间变化」「动态过程」
- 存在质量/能量/动量的守恒关系
- 系统的未来状态仅依赖于当前状态（Markov 性）

### 标准建模流程

1. **识别状态变量**：哪些量随时间变化（如压力、温度、位移、浓度）
2. **建立守恒方程**：基于物理定律写出状态变量的变化率表达式
3. **确定参数**：哪些参数已知（几何尺寸、物性常数），哪些需要拟合
4. **选择求解方法**：非刚性用 RK4/solve_ivp('RK45')，刚性用 solve_ivp('BDF') 或 ode15s
5. **参数拟合**：用 curve_fit 反推未知参数

### 高阶 ODE 转化

建模中常见的二阶 ODE（如振动方程 $m\ddot{x} + c\dot{x} + kx = F(t)$）需转化为一阶方程组：

令 $y_1 = x, \ y_2 = \dot{x}$，则：

$$\begin{cases}
\dot{y}_1 = y_2 \\
\dot{y}_2 = \frac{1}{m}(F(t) - c y_2 - k y_1)
\end{cases}$$

一般形式：将 $n$ 阶 ODE $y^{(n)} = f(t, y, y', ..., y^{(n-1)})$ 转化为：

$$\frac{d}{dt}\begin{bmatrix} y_1 \\ y_2 \\ \vdots \\ y_n \end{bmatrix} = \begin{bmatrix} y_2 \\ y_3 \\ \vdots \\ f(t, y_1, y_2, ..., y_n) \end{bmatrix}$$

### 求解器选择

| 方法 | 精度 | 稳定性 | 适用场景 | Python |
|------|------|--------|---------|--------|
| Euler 显式 | 一阶 | 条件稳定 | 教学演示，不推荐实赛使用 | 手动实现 |
| RK4（经典四阶 Runge-Kutta） | 四阶 | 条件稳定 | 非刚性 ODE，精度要求高 | 手动实现 / `solve_ivp(method='RK45')` |
| RK45（Dormand-Prince） | 五阶 (4) | 自适应步长 | **默认首选**，非刚性通用 | `solve_ivp(method='RK45')` |
| BDF（后向差分） | 变阶 | 刚性稳定 | **刚性 ODE 首选** | `solve_ivp(method='BDF')` |
| Radau | 五阶 | 刚性稳定 | 刚性 + 高精度 | `solve_ivp(method='Radau')` |

MATLAB 对照：`ode45`（非刚性，等价 RK45）、`ode15s`（刚性，等价 BDF）、`ode23s`（轻度刚性）。

### 刚性问题检测与处理

**刚性 (Stiffness) 判断标准**：
- 系统中存在时间尺度差异极大的过程（快慢变量耦合）
- 显式方法需要极小步长才能稳定
- 求解时间异常长

**信号**：`solve_ivp` 用 RK45 时步长极小（`t` 数组非常密集），或者求解时间远超预期。

**对策**：改用隐式方法（BDF/Radau/ode15s）。

```python
from scipy.integrate import solve_ivp
import numpy as np

def ode_system(t, y, params):
    """ODE 右端函数：y 为状态向量，返回 dy/dt"""
    # 解包参数和状态
    a, b, c = params
    y1, y2, y3 = y
    dy1 = a * y1 - b * y2 * y3
    dy2 = -c * y2 + y1 * y3
    dy3 = b * y2 * y1 - y3
    return [dy1, dy2, dy3]

# 非刚性 → RK45
sol = solve_ivp(ode_system, [t0, tf], y0, args=(params,),
                method='RK45', rtol=1e-6, atol=1e-9)

# 刚性 → BDF
sol = solve_ivp(ode_system, [t0, tf], y0, args=(params,),
                method='BDF', rtol=1e-6, atol=1e-9)

# 访问结果
t, y = sol.t, sol.y  # y.shape = (n_vars, n_steps)
```

### RK4 手动实现

当需要完全控制求解过程（如每一步输出额外信息），手动实现 RK4：

```python
def rk4_step(f, t, y, h, *args):
    """单步 RK4"""
    k1 = f(t, y, *args)
    k2 = f(t + h/2, y + h/2 * k1, *args)
    k3 = f(t + h/2, y + h/2 * k2, *args)
    k4 = f(t + h, y + h * k3, *args)
    return y + (h / 6) * (k1 + 2*k2 + 2*k3 + k4)

def rk4_solve(f, t_span, y0, h, *args):
    """定步长 RK4 求解"""
    t0, tf = t_span
    n_steps = int((tf - t0) / h)
    t = np.linspace(t0, tf, n_steps + 1)
    y = np.zeros((n_steps + 1, len(y0)))
    y[0] = y0
    for i in range(n_steps):
        y[i+1] = rk4_step(f, t[i], y[i], h, *args)
    return t, y
```

### 参数拟合

已知观测数据 $(t_k, y_{\text{obs},k})$，ODE 中有未知参数 $\theta$ 需要反推：

```python
from scipy.optimize import curve_fit
from scipy.integrate import solve_ivp

def ode_forward(t_eval, *theta):
    """将 ODE 求解包装为 curve_fit 兼容的函数"""
    sol = solve_ivp(ode_system, [t_eval[0], t_eval[-1]], y0,
                    args=(theta,), t_eval=t_eval, method='RK45',
                    rtol=1e-6, atol=1e-9)
    return sol.y[0]  # 返回第一个状态变量

# 拟合
popt, pcov = curve_fit(ode_forward, t_obs, y_obs, p0=theta0,
                       bounds=(lb, ub))

# 参数不确定度
perr = np.sqrt(np.diag(pcov))
```

MATLAB 对应：

```matlab
function y_pred = ode_forward(theta, t_eval)
    [~, y] = ode45(@(t,y) ode_system(t,y,theta), t_eval, y0);
    y_pred = y(:,1);
end

theta_fit = lsqcurvefit(@ode_forward, theta0, t_obs, y_obs, lb, ub);
```

### 典型赛题

- **2019A 高压油管**：燃油在高压油管中的压力变化由 ODE 描述（质量守恒：进油量 - 出油量 = 密度变化 × 体积）。单向阀的开启/关闭产生分段 ODE 系统，需要结合事件检测（`solve_ivp` 的 `events` 参数）处理状态切换。核心是确定凸轮角速度使油管压力稳定在目标值附近。
- **2022A 波浪能**：浮子在波浪作用下的垂荡运动由二阶振动 ODE 描述，包含波浪激励力、辐射力（附加质量 + 阻尼）、静水恢复力。利用 Cummins 方程将时域水动力学问题转化为 ODE 求解，进而计算功率输出。

---

## 3. 几何/运动学建模

### 适用场景

这类问题不需要求解 PDE/ODE，核心是对几何关系和运动规律的分析。在建模竞赛 A/B 题中频繁出现，关键在于**将物理世界的空间关系转化为精确的数学不等式/方程**。

### 曲线运动学

**阿基米德螺线（Archimedean Spiral）**：

$$r = a + b\theta$$

参数形式：
$$x(\theta) = (a + b\theta)\cos\theta, \quad y(\theta) = (a + b\theta)\sin\theta$$

螺线的关键在于：当 $\theta$ 均匀增加时，相邻圈的径向间距恒为 $2\pi b$。

弧长公式：
$$s(\theta) = \int_0^\theta \sqrt{r^2 + (dr/d\theta)^2} \, d\theta = \int_0^\theta \sqrt{(a+bt)^2 + b^2} \, dt$$

此积分没有初等表达式，可用 `scipy.integrate.quad` 或梯形法则数值计算。

**一般参数曲线**：对于 $\mathbf{r}(t) = (x(t), y(t))$：

- 切向量：$\mathbf{r}'(t) = (x'(t), y'(t))$
- 法向量：$\mathbf{n}(t) = (-y'(t), x'(t)) / |\mathbf{r}'(t)|$（单位法向量）
- 曲率：$\kappa(t) = \frac{|x'y'' - y'x''|}{(x'^2 + y'^2)^{3/2}}$
- 曲率半径：$R(t) = 1/\kappa(t)$

### 坐标变换：齐次变换矩阵

在空间运动分析（如2024A板凳龙、2021A FAST）中，刚体的位置和姿态统一用 $4 \times 4$ 齐次变换矩阵描述：

$$T = \begin{bmatrix} R_{3\times3} & \mathbf{p}_{3\times1} \\ \mathbf{0}_{1\times3} & 1 \end{bmatrix}$$

其中 $R$ 为旋转矩阵，$\mathbf{p}$ 为平移向量。

**二维旋转矩阵**：

$$R(\theta) = \begin{bmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{bmatrix}$$

**三维旋转矩阵（绕坐标轴）**：

$$R_x(\alpha) = \begin{bmatrix} 1 & 0 & 0 \\ 0 & \cos\alpha & -\sin\alpha \\ 0 & \sin\alpha & \cos\alpha \end{bmatrix}, \quad
R_y(\beta) = \begin{bmatrix} \cos\beta & 0 & \sin\beta \\ 0 & 1 & 0 \\ -\sin\beta & 0 & \cos\beta \end{bmatrix}, \quad
R_z(\gamma) = \begin{bmatrix} \cos\gamma & -\sin\gamma & 0 \\ \sin\gamma & \cos\gamma & 0 \\ 0 & 0 & 1 \end{bmatrix}$$

**链式变换**：若 A 相对于世界的位置为 $T_A$，B 相对于 A 的位置为 $T_B^A$，则 B 在世界系下的位置为：

$$T_B = T_A \cdot T_B^A$$

### 碰撞/干涉检测

多体运动问题中的核心约束：各物体之间不能交叉重叠。数学上表达为几何不等式约束。

**二维圆形物体**：物体 $i$ 和 $j$ 的圆心距 $\geq r_i + r_j$：

$$(x_i - x_j)^2 + (y_i - y_j)^2 \geq (r_i + r_j)^2$$

**多边形物体**：用分离轴定理 (SAT)。若存在一个方向，两个多边形在该方向上的投影不重叠，则不相交。

**矩形物体**：可以用四个角点的坐标范围判断，或者将问题简化为两个矩形的 AABB 检测。

在竞赛中，通常可以将约束简化为离散的关键碰撞对，用一组不等式表达：

$$g_k(\mathbf{x}) \leq 0, \quad k = 1, 2, ..., K$$

### 空间覆盖模型

**正弦定理与重叠率**：在测线覆盖问题（如2023B 多波束测深）中，相邻测线的覆盖区域存在重叠。利用正弦定理建立重叠率与测线间距的关系：

$$\frac{a}{\sin A} = \frac{b}{\sin B} = \frac{c}{\sin C}$$

**扇形覆盖面积**：对于扇形扫描的覆盖面积计算：

$$A = \frac{1}{2}\theta R^2$$

考虑地形坡度 $\alpha$ 时，有效覆盖宽度需用三角函数修正。

```python
import numpy as np

def coverage_width(depth, beam_angle, slope_angle=0):
    """计算多波束测深的覆盖宽度
    
    Args:
        depth: 水深 (m)
        beam_angle: 波束开角 (rad)，半角
        slope_angle: 海底坡度 (rad)，水平为 0
    """
    # 利用正弦定理计算修正后的左右覆盖
    left_angle = beam_angle - slope_angle
    right_angle = beam_angle + slope_angle
    left_width = depth * np.sin(left_angle) / np.sin(np.pi/2 - left_angle)
    right_width = depth * np.sin(right_angle) / np.sin(np.pi/2 - right_angle)
    return left_width, right_width, left_width + right_width
```

### 典型赛题

- **2024A 板凳龙**（CUMCM）：龙头沿阿基米德螺线运动，后方各条板凳跟随运动（铰接约束）。核心挑战：在 $r(\theta) = a + b\theta$ 曲线上，已知龙头位置，递推计算后方所有板凳的坐标，确保相邻板凳间距离等于固定值（连杆长度约束）。这是一个典型的**几何递推问题**——每步需解一个非线性方程确定下一个铰接点的位置。

- **2021A FAST 主动反射面**（CUMCM）：半球面反射面由数千块可调三角面板组成。工作抛物面（300m 口径）需要在基准球面（半径 300m）内通过调节促动器伸缩来实现。核心是：(1) 球面到抛物面的几何映射；(2) 各促动器的伸缩量计算；(3) 三角面板顶点坐标和法向量计算。

- **2023B 测线设计**（CUMCM）：多波束测深系统在海底地形测量中的测线布局优化。核心是：给定波束开角和海底坡度，计算不同航向下的覆盖宽度和重叠率，优化测线间距使得既无遗漏又不过度重叠。

---

## 4. 光学/辐射建模

### 太阳位置计算

太阳位置是太阳能利用问题的基础输入。使用 NOAA 太阳位置算法。

**太阳赤纬角 (Declination)**：

$$\delta = 23.45^\circ \times \sin\left(\frac{360^\circ}{365} \times (284 + n)\right)$$

其中 $n$ 为年积日（1月1日为 $n=1$）。

**太阳时角 (Hour Angle)**：

$$\omega = 15^\circ \times (t_{\text{solar}} - 12)$$

其中 $t_{\text{solar}}$ 为当地太阳时。

**太阳高度角 (Altitude)**：

$$\sin \alpha_s = \sin \phi \sin \delta + \cos \phi \cos \delta \cos \omega$$

**太阳方位角 (Azimuth)**：

$$\sin \gamma_s = \frac{-\cos \delta \sin \omega}{\cos \alpha_s}$$

其中 $\phi$ 为当地纬度，$\alpha_s$ 为高度角。

**Python 快速计算（推荐用 pvlib）**：

```python
import pvlib
import pandas as pd

# 定日镜场某天的太阳位置
times = pd.date_range('2023-06-21', '2023-06-22', freq='1min', tz='Asia/Shanghai')
solar_pos = pvlib.solarposition.get_solarposition(
    times, latitude=37.4, longitude=97.4, altitude=3000
)
# solar_pos['apparent_elevation'] - 高度角 (deg)
# solar_pos['azimuth'] - 方位角 (deg)
```

### DNI 模型与光学效率链

**直接法向辐照度 (DNI)** 是定日镜场接收的太阳辐射功率密度。常用 Haurwitz 晴空模型：

$$DNI = I_0 \times \cos\theta_z \times \exp\left(-\frac{AM}{B}\right)$$

其中 $I_0$ 为太阳常数（1367 W/m^2），$\theta_z$ 为天顶角（$\theta_z = 90^\circ - \alpha_s$），$AM = 1/\cos\theta_z$ 为大气质量，$B$ 为大气透明度系数。

**光学效率链**：从太阳辐射到接收器热能，经过多级光学损失：

$$\eta_{\text{opt}} = \eta_{\text{shadow}} \times \eta_{\text{cos}} \times \eta_{\text{ref}} \times \eta_{\text{atten}} \times \eta_{\text{spill}}$$

| 效率项 | 含义 | 影响因素 |
|--------|------|---------|
| $\eta_{\text{shadow}}$ | 阴影遮挡效率 | 镜面间相互遮挡（早晚低，正午高）|
| $\eta_{\text{cos}}$ | 余弦效率 | 镜面法向与入射光线夹角（核心损失源）|
| $\eta_{\text{ref}}$ | 镜面反射率 | 镜面材料（通常 0.90-0.95）|
| $\eta_{\text{atten}}$ | 大气衰减效率 | 光线在大气中传播的衰减（距离相关）|
| $\eta_{\text{spill}}$ | 溢出效率 | 光斑超出接收器口径的比例 |

### 反射定律

定日镜将太阳光反射到接收塔顶的接收器，反射方向由镜面法向量决定。

**镜面法向量**：入射方向 $\mathbf{s}$（指向太阳），期望反射方向 $\mathbf{t}$（指向接收器），则镜面法向量必须为：

$$\mathbf{n} = \frac{\mathbf{s} + \mathbf{t}}{|\mathbf{s} + \mathbf{t}|}$$

**反射验证**：反射方向 $\mathbf{r} = \mathbf{s} - 2(\mathbf{s} \cdot \mathbf{n})\mathbf{n}$ 应与 $\mathbf{t}$ 一致。

**余弦效率**：入射辐射在镜面法向的分量比例：

$$\eta_{\text{cos}} = \mathbf{s} \cdot \mathbf{n}$$

### 光线追迹基础

```python
import numpy as np

def reflect_ray(incident, normal):
    """计算反射光线方向
    
    Args:
        incident: 入射方向单位向量 (3,)
        normal: 表面法向量单位向量 (3,)
    Returns:
        反射方向单位向量
    """
    # 确保法向量指向入射侧
    if np.dot(incident, normal) > 0:
        normal = -normal
    return incident - 2 * np.dot(incident, normal) * normal

def mirror_normal(sun_dir, target_dir):
    """计算定日镜所需的法向量
    
    Args:
        sun_dir: 太阳方向单位向量 (3,)——指向太阳
        target_dir: 目标方向单位向量 (3,)——指向接收器
    Returns:
        镜面法向量单位向量
    """
    n = sun_dir + target_dir
    return n / np.linalg.norm(n)

# 示例：太阳从东方入射，接收器在北方塔顶
sun_vec = np.array([1.0, 0.0, 0.0])   # 水平入射
sun_vec = sun_vec / np.linalg.norm(sun_vec)
target = np.array([0.0, 30.0, 100.0])  # 塔顶坐标
target_vec = target / np.linalg.norm(target)

n = mirror_normal(sun_vec, target_vec)
print(f"镜面法向量: {n}")
print(f"余弦效率: {np.dot(sun_vec, n):.4f}")
```

### 典型赛题

- **2023A 定日镜场优化设计**（CUMCM）：在给定的圆形场地内布置数千面定日镜，使接收器输出功率最大化。核心挑战是：(1) 阴影遮挡效率的计算（两镜之间的几何遮挡关系）；(2) 余弦效率与镜面位置的关系（边缘镜余弦效率低但遮挡少，中心镜相反）；(3) 全年加权优化（春分/夏至/秋分/冬至的典型日代表全年）。关键是建立完整的光学效率计算模型，然后用优化算法确定镜面布局。

- **2021A FAST 主动反射面**：虽然 FAST 是射电望远镜（接收天体辐射），但其信号接收效率受面板指向精度和反射面形状决定。光（电磁波）平行入射后需汇聚到馈源舱，面板的法向量决定了反射方向。几何上等价于光线追迹问题。

---

## 5. 流体/压力系统

### 应用场景

流体/压力系统在 2019A 高压油管问题中集中体现。核心物理定律只有三条，但组合起来能描述复杂的工程系统。

### Bernoulli 方程

适合不可压缩、无黏流体的稳态流动（沿流线）：

$$P + \frac{1}{2}\rho v^2 + \rho g h = \text{const}$$

其中 $P$ 为静压，$\rho v^2/2$ 为动压，$\rho g h$ 为位能。

**工程形式（含损失）**：

$$P_1 + \frac{1}{2}\rho v_1^2 + \rho g h_1 = P_2 + \frac{1}{2}\rho v_2^2 + \rho g h_2 + \Delta P_{\text{loss}}$$

### 流量方程

通过小孔的流量（孔口出流）：

$$Q = C_d A \sqrt{\frac{2\Delta P}{\rho}}$$

其中 $C_d$ 为流量系数（0.6-0.8），$A$ 为孔口面积，$\Delta P$ 为孔口前后压差。

通过管道的流量（Poiseuille 流）：

$$Q = \frac{\pi d^4}{128 \mu L} \Delta P$$

其中 $\mu$ 为动力黏度，$L$ 为管长，$d$ 为管径。

### PVT（压力-体积-温度）关系

**理想气体**：

$$PV = nRT$$

其中 $R = 8.314$ J/(mol·K)，$n$ 为摩尔数。适用于低压高温条件。

**实际气体（范德瓦尔斯方程）**：

$$\left(P + \frac{a}{V_m^2}\right)(V_m - b) = RT$$

其中 $a, b$ 为气体相关常数，$V_m$ 为摩尔体积。

**液体压缩性**：考虑液体的体积模量 $K$：

$$\Delta P = -K \frac{\Delta V}{V}$$

燃油在高压下的弹性效应影响不可忽略，体积模量通常在 $1.2 \times 10^9$ Pa 量级。

### 一维管道流模型

质量守恒（连续性方程）：

$$\frac{d(\rho V)}{dt} = \dot{m}_{\text{in}} - \dot{m}_{\text{out}}$$

考虑密度变化：

$$\frac{dP}{dt} = \frac{K}{\rho V} (\dot{m}_{\text{in}} - \dot{m}_{\text{out}})$$

其中 $K$ 为体积模量（或气体时为 $\gamma P$，$\gamma$ 为绝热指数）。

### 单向阀模型

单向阀是 2019A 的核心元件，开启/关闭逻辑为：

$$\text{状态} = \begin{cases}
\text{open} & \text{if } P_{\text{in}} > P_{\text{out}} + P_{\text{crack}} \\
\text{closed} & \text{otherwise}
\end{cases}$$

其中 $P_{\text{crack}}$ 为开启压力。

```python
def check_valve_flow(P_in, P_out, P_crack, C_d, A, rho):
    """单向阀流量模型"""
    if P_in > P_out + P_crack:
        # 阀门开启
        Q = C_d * A * np.sqrt(2 * abs(P_in - P_out) / rho)
        return Q
    else:
        return 0.0
```

### Python 管道压力瞬态求解示例

```python
from scipy.integrate import solve_ivp
import numpy as np

def fuel_pipe_ode(t, P, params):
    """燃油管道压力 ODE"""
    V, K, rho, Cd_in, A_in, Cd_out, A_out, P_pump, P_atm = params
    
    # 进油流量（高压泵 → 油管）
    if P_pump > P[0]:
        Q_in = Cd_in * A_in * np.sqrt(2 * abs(P_pump - P[0]) / rho)
    else:
        Q_in = 0.0
    
    # 出油流量（油管 → 喷油器）
    if P[0] > P_atm:
        Q_out = Cd_out * A_out * np.sqrt(2 * abs(P[0] - P_atm) / rho)
    else:
        Q_out = 0.0
    
    # 质量守恒 → 压力变化率
    dP = (K / (rho * V)) * (rho * Q_in - rho * Q_out)
    return [dP]

# 求解
params = (V, K, rho, Cd_in, A_in, Cd_out, A_out, P_pump, P_atm)
sol = solve_ivp(fuel_pipe_ode, [0, 10], [P0], args=(params,),
                method='BDF', rtol=1e-6, atol=1e-6)
```

### 典型赛题

- **2019A 高压油管**（CUMCM）：燃油在高压油管中的压力波动由喷油器周期性开启/关闭引起。单向阀控制进油，喷油嘴控制出油。系统是分段 ODE（阀门开/闭状态切换）。核心任务：(1) 调节凸轮角速度使压力波动幅度最小；(2) 优化单向阀开启持续时间和凸轮型线使系统工作稳定；(3) 加入高压油泵的柱塞运动后，系统变为耦合 ODE。

---

## 6. 振动/波动系统

### 质量-弹簧-阻尼系统

最基本的振动模型，二阶线性 ODE：

$$m\ddot{x} + c\dot{x} + kx = F(t)$$

其中 $m$ 为质量，$c$ 为阻尼系数，$k$ 为弹簧刚度，$F(t)$ 为外激励力。

**无阻尼自振频率**：

$$\omega_n = \sqrt{\frac{k}{m}} \quad (\text{rad/s}), \quad f_n = \frac{\omega_n}{2\pi} \quad (\text{Hz})$$

**阻尼比**：

$$\zeta = \frac{c}{2\sqrt{mk}} = \frac{c}{2m\omega_n}$$

- $\zeta < 1$：欠阻尼（振荡衰减）
- $\zeta = 1$：临界阻尼（最快回到平衡，无振荡）
- $\zeta > 1$：过阻尼（缓慢回到平衡，无振荡）

**有阻尼自振频率**：

$$\omega_d = \omega_n \sqrt{1 - \zeta^2}$$

### 受迫振动与共振

简谐激励 $F(t) = F_0 \sin(\omega t)$ 下的稳态响应：

$$x(t) = X \sin(\omega t - \phi)$$

振幅放大因子：

$$\frac{X}{F_0/k} = \frac{1}{\sqrt{(1 - r^2)^2 + (2\zeta r)^2}}$$

其中 $r = \omega / \omega_n$ 为频率比。

**共振条件**：当 $\omega = \omega_n \sqrt{1 - 2\zeta^2}$ 时振幅最大（对 $\zeta < 1/\sqrt{2}$）。对于小阻尼系统，共振近似发生在 $\omega \approx \omega_n$。

共振时振幅放大因子 $\approx 1/(2\zeta)$，阻尼越小共振越剧烈。

### 多自由度振动

$n$ 自由度系统的运动方程：

$$M \ddot{\mathbf{x}} + C \dot{\mathbf{x}} + K \mathbf{x} = \mathbf{F}(t)$$

模态分析：求解广义特征值问题 $K \Phi = M \Phi \Lambda$，得到固有频率和振型。

### 波浪能转换基础

波浪能装置（如2022A）的动力学基于**Cummins 方程**，在时域中描述浮体运动：

$$(m + A_\infty)\ddot{x} + \int_0^t K(t - \tau)\dot{x}(\tau) d\tau + C x = F_{\text{exc}}(t) + F_{\text{PTO}}(t)$$

其中：
- $m$：浮体质量
- $A_\infty$：无限频率附加质量（与加速度同相位的流体反作用力）
- $K(t)$：迟滞函数（辐射力的记忆效应——卷积项）
- $C$：静水恢复力系数（$C = \rho g A_w$，$A_w$ 为水线面面积）
- $F_{\text{exc}}(t)$：波浪激励力
- $F_{\text{PTO}}(t)$：能量提取系统 (Power Take-Off) 施加的力

**平均功率输出**：

$$P_{\text{avg}} = \frac{1}{T} \int_0^T F_{\text{PTO}}(t) \cdot \dot{x}(t) \, dt$$

当 PTO 简化为线性阻尼器 $F_{\text{PTO}} = -c_{\text{PTO}} \dot{x}$ 时：

$$P_{\text{avg}} = \frac{1}{T} \int_0^T c_{\text{PTO}} \dot{x}^2(t) \, dt$$

**最优 PTO 阻尼**：在规则波（单频）激励下，忽略卷积项和 $A_\infty$ 时，最优 PTO 阻尼系数近似为：

$$c_{\text{PTO}}^{\text{opt}} \approx \sqrt{\frac{k^2}{\omega^2} + c^2}$$

### Python 振动 ODE 求解

```python
from scipy.integrate import solve_ivp
import numpy as np

def vibration_ode(t, y, m, c, k, F_func):
    """二阶振动系统的一阶形式
    y = [x, v]  where v = dx/dt
    """
    x, v = y
    F = F_func(t)
    dxdt = v
    dvdt = (F - c * v - k * x) / m
    return [dxdt, dvdt]

# 参数
m, c, k = 100.0, 50.0, 1000.0  # 质量, 阻尼, 刚度
omega_n = np.sqrt(k / m)        # 固有频率
zeta = c / (2 * np.sqrt(m * k)) # 阻尼比

# 激励力
def excitation(t, omega=1.2, F0=100):
    return F0 * np.sin(omega * t)

# 求解
sol = solve_ivp(vibration_ode, [0, 50], [0, 0],
                args=(m, c, k, excitation),
                method='RK45', rtol=1e-6, atol=1e-9,
                max_step=0.01)

# 计算稳态平均功率（PTO 功率提取）
t_eval = np.linspace(10, 50, 10000)  # 稳态段
sol_eval = solve_ivp(vibration_ode, [10, 50], [sol.y[0,-1], sol.y[1,-1]],
                     args=(m, c, k, excitation),
                     t_eval=t_eval, method='RK45', rtol=1e-6, atol=1e-9)
x, v = sol_eval.y[0], sol_eval.y[1]
c_pto = 200.0  # PTO 阻尼系数
P_avg = c_pto * np.mean(v**2)
print(f"平均功率输出: {P_avg:.1f} W")
```

### 典型赛题

- **2022A 波浪能装置**（CUMCM）：振荡浮子式波浪能转换装置的动力学建模与功率优化。浮子在波浪作用下做垂荡运动，通过 PTO 系统将动能转换为电能。核心：(1) 基于 Cummins 方程建立时域运动方程；(2) 处理迟滞函数的卷积项；(3) 优化 PTO 阻尼系数使平均输出功率最大。还需考虑实际约束（浮子位移不能超出物理限位）。

---

## 7. 求解工具速查表

### 核心工具对照

| 问题类型 | Python | MATLAB |
|---------|--------|--------|
| ODE 求解（非刚性） | `scipy.integrate.solve_ivp(method='RK45')` | `ode45` |
| ODE 求解（刚性） | `scipy.integrate.solve_ivp(method='BDF')` | `ode15s` |
| ODE 事件检测 | `solve_ivp(..., events=...)` | `odeset('Events', ...)` |
| 1D 热传导 PDE | 自定义 FDM / FiPy 库 | `pdepe` |
| 2D/3D PDE | FiPy / FEniCS | `pdepe` (1D) / PDE Toolbox |
| 非线性参数拟合 | `scipy.optimize.curve_fit` | `lsqcurvefit` |
| 非线性优化 | `scipy.optimize.minimize` | `fmincon` |
| 全局优化 | `scipy.optimize.differential_evolution` | `ga` / `particleswarm` |
| 数值积分 | `scipy.integrate.quad` / `simpson` | `integral` / `trapz` |
| 数值微分 | `numpy.gradient` | `gradient` / `diff` |
| 方程求根 | `scipy.optimize.fsolve` / `root` | `fsolve` / `fzero` |
| 太阳位置 | `pvlib.solarposition.get_solarposition` | 自定义 NOAA 公式 |
| 插值 | `scipy.interpolate.interp1d` / `CubicSpline` | `interp1` / `spline` |
| 样条平滑 | `scipy.interpolate.UnivariateSpline` | `csaps` / `spaps` |
| 稀疏矩阵 | `scipy.sparse` | `sparse` |
| 特征值求解 | `scipy.linalg.eig` / `eigh` | `eig` / `eigs` |

### 偏微分方程工具对比

| 工具 | 语言 | 方法 | 适用维度 | 难度 |
|------|------|------|---------|------|
| 自编 FDM | Python/MATLAB | 有限差分 | 1D, 2D 规则域 | 中等 |
| FiPy | Python | 有限体积 | 1D-3D 非结构网格 | 中等 |
| FEniCS | Python/C++ | 有限元 | 1D-3D 非结构网格 | 较高（竞赛不常需要）|
| `pdepe` | MATLAB | 有限差分 | 1D | 简单 |
| PDE Toolbox | MATLAB | 有限元 | 2D-3D | 中等 |

**竞赛建议**：绝大部分 A 题 PDE 无需 FEniCS 等重型工具。一维问题用自编 FDM（几行代码），或 MATLAB 的 `pdepe`。二维简单域可扩展 FDM。只在几何极其复杂时才考虑有限元工具。

---

## 常见陷阱与对策

| 陷阱 | 对策 |
|------|------|
| 显式 FDM 不检查 CFL 条件，结果发散 | 显式方案先算 $r = \alpha \Delta t / (\Delta x)^2$，确保 $r \leq 0.5$ |
| ODE 求解用错方法（刚性用 RK45，求解极慢） | 先试 RK45，步数异常大则切 BDF/Radau |
| 参数拟合陷入局部最优 | 多次从不同初值启动，或先用网格搜索粗找，再用 curve_fit 精化 |
| 高阶 ODE 忘记降阶转化 | $n$ 阶 ODE 转化为 $n$ 个一阶 ODE 再送 solve_ivp |
| 几何模型中角度单位混淆 | 始终统一使用弧度（rad），sin/cos 函数均以 rad 为单位 |
| 太阳位置计算忽略大气折射修正 | 低高度角时（$\alpha_s < 10^\circ$）大气折射不可忽略，pvlib 自动修正 |
| Bernoulli 方程滥用（忽略了可压缩性） | 先判断是否满足不可压缩假设（Ma < 0.3），高压气体需改用可压缩流公式 |
| 忘记方向向量归一化 | 光线追迹中所有方向向量使用前必须归一化 |
| 几何约束遗漏 | 多体系统中检查所有可能碰撞对，用穷举或空间哈希加速 |
| 忽略了多层介质的界面连续性条件 | 多层热传导问题中界面的温度和热流必须连续 |
