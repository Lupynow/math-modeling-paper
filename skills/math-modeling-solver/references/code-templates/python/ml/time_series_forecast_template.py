"""
时间序列预测 (Time Series Forecasting) 模板
适用：销售量预测、经济指标预测、时序数据分析
问题适配点：
  1. 修改 _load_data() —— 加载实际时间序列数据（CSV/Excel/数据库）
  2. 修改 data_freq —— 数据频率：'D'每日, 'W'每周, 'M'每月, 'Q'季度, 'Y'年度
  3. 调整 ARIMA/SARIMA 阶数 —— 根据 ACF/PACF 图手动选择或启用 auto_arima
  4. 如需预测外生变量，使用 SARIMAX 并传 exog 参数
  5. 多序列 → 对每个序列分别建模，或使用 VAR/VARMAX
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.stats.diagnostic import acorr_ljungbox
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class TimeSeriesForecaster:
    """时间序列预测框架（基于 ARIMA/SARIMA）"""

    def __init__(self, data: Optional[pd.Series] = None,
                 freq: str = 'M'):
        """
        Parameters
        ----------
        data : 时间序列数据（pandas Series，带 DatetimeIndex）
        freq : 数据频率，用于生成日期范围
        """
        self.data = data
        self.freq = freq
        self.model = None
        self.model_fit = None
        self.forecast_result = None

    @staticmethod
    def _load_data() -> pd.Series:
        """
        加载或生成时间序列数据。

        Returns
        -------
        pandas Series，索引为时间戳
        """
        # TODO: 替换为实际数据加载逻辑
        # 示例：生成带季节性的合成数据
        n = 120  # 10年 × 12月
        t = np.arange(n)
        trend = 0.15 * t
        seasonal = 5 * np.sin(2 * np.pi * t / 12)  # 年度周期
        noise = np.random.default_rng(42).normal(0, 1.5, n)
        y = 100 + trend + seasonal + noise

        idx = pd.date_range(start='2015-01-01', periods=n, freq='M')
        return pd.Series(y, index=idx, name='value')

    def check_stationarity(self, series: Optional[pd.Series] = None,
                           verbose: bool = True) -> dict:
        """
        ADF 平稳性检验。p < 0.05 表示拒绝"存在单位根"的原假设，即序列平稳。

        Returns
        -------
        result : dict，含 'adf_stat', 'p_value', 'used_lag', 'is_stationary'
        """
        if series is None:
            series = self.data
        s = series.dropna()
        adf_result = adfuller(s, autolag='AIC')
        is_stationary = adf_result[1] < 0.05

        if verbose:
            print(f"ADF 统计量: {adf_result[0]:.4f}")
            print(f"p-value:     {adf_result[1]:.4f}")
            print(f"使用滞后阶数: {adf_result[2]}")
            print(f"结论: {'平稳' if is_stationary else '非平稳，需要差分'}\n")

        return {'adf_stat': adf_result[0], 'p_value': adf_result[1],
                'used_lag': adf_result[2], 'is_stationary': is_stationary}

    def decompose(self, series: Optional[pd.Series] = None,
                  period: int = 12, model: str = 'additive'):
        """
        季节分解（趋势 + 季节 + 残差）。

        Parameters
        ----------
        period : 季节周期（月数据=12，季度=4，周数据=52）
        model : 'additive' 加法模型 或 'multiplicative' 乘法模型
        """
        if series is None:
            series = self.data
        result = seasonal_decompose(series.dropna(), model=model, period=period)

        fig, axes = plt.subplots(4, 1, figsize=(12, 8), sharex=True)
        axes[0].plot(result.observed, color='black', lw=1)
        axes[0].set_ylabel('Observed')
        axes[1].plot(result.trend, color='steelblue', lw=1.5)
        axes[1].set_ylabel('Trend')
        axes[2].plot(result.seasonal, color='darkorange', lw=1)
        axes[2].set_ylabel('Seasonal')
        axes[3].plot(result.resid, color='gray', lw=0.8)
        axes[3].set_ylabel('Residual')
        axes[3].set_xlabel('Time')
        fig.suptitle('时间序列季节分解', fontsize=14)
        plt.tight_layout()
        plt.show()
        return result

    def plot_acf_pacf(self, series: Optional[pd.Series] = None,
                      lags: int = 40):
        """绘制 ACF / PACF 图，辅助定阶 (p, q) 选择"""
        if series is None:
            series = self.data
        s = series.dropna()

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 4))
        plot_acf(s, lags=lags, ax=ax1)
        ax1.set_title('自相关函数 (ACF)')
        plot_pacf(s, lags=lags, ax=ax2, method='ywm')
        ax2.set_title('偏自相关函数 (PACF)')
        plt.tight_layout()
        plt.show()

    def fit_arima(self, order: Tuple[int, int, int] = (1, 1, 1),
                  series: Optional[pd.Series] = None,
                  verbose: bool = True):
        """
        拟合 ARIMA 模型。

        Parameters
        ----------
        order : (p, d, q) 阶数
            p — 自回归阶数（PACF 截尾点）
            d — 差分阶数（使序列平稳的最小差分次数）
            q — 移动平均阶数（ACF 截尾点）
        """
        # TODO: 根据 ACF/PACF 图调整阶数
        if series is None:
            series = self.data
        s = series.dropna()
        self.model = ARIMA(s, order=order)
        self.model_fit = self.model.fit()

        if verbose:
            print(self.model_fit.summary())
        return self.model_fit

    def fit_sarima(self, order: Tuple[int, int, int] = (1, 1, 1),
                   seasonal_order: Tuple[int, int, int, int] = (1, 1, 1, 12),
                   series: Optional[pd.Series] = None,
                   verbose: bool = True):
        """
        拟合 SARIMA 模型（含季节成分）。

        Parameters
        ----------
        order : (p, d, q)
        seasonal_order : (P, D, Q, s)
            P — 季节自回归阶数, D — 季节差分阶数
            Q — 季节移动平均阶数, s — 季节周期长度
        """
        # TODO: 根据季节性 ACF/PACF 调整季节阶数
        if series is None:
            series = self.data
        s = series.dropna()
        self.model = SARIMAX(s, order=order,
                             seasonal_order=seasonal_order,
                             enforce_stationarity=False,
                             enforce_invertibility=False)
        self.model_fit = self.model.fit(disp=False)

        if verbose:
            print(self.model_fit.summary())
        return self.model_fit

    def forecast(self, steps: int = 12,
                 series: Optional[pd.Series] = None,
                 alpha: float = 0.05) -> pd.DataFrame:
        """
        预测未来 steps 步，含 95% 置信区间。

        Returns
        -------
        DataFrame，列：['forecast', 'lower_ci', 'upper_ci']
        """
        if self.model_fit is None:
            raise RuntimeError("请先调用 fit_arima() 或 fit_sarima() 拟合模型")
        if series is None:
            series = self.data

        fc = self.model_fit.get_forecast(steps=steps)
        fc_mean = fc.predicted_mean
        fc_ci = fc.conf_int(alpha=alpha)

        last_date = series.index[-1]
        new_index = pd.date_range(start=last_date, periods=steps + 1,
                                  freq=self.freq)[1:]

        self.forecast_result = pd.DataFrame({
            'forecast': fc_mean.values,
            'lower_ci': fc_ci.iloc[:, 0].values,
            'upper_ci': fc_ci.iloc[:, 1].values,
        }, index=new_index)
        return self.forecast_result

    def evaluate(self, true_values: pd.Series,
                 pred_values: pd.Series) -> dict:
        """
        评价指标：MAE, RMSE, MAPE。

        Parameters
        ----------
        true_values : 真实值
        pred_values : 预测值
        """
        # 对齐索引
        common_idx = true_values.index.intersection(pred_values.index)
        y_true = true_values.loc[common_idx].values
        y_pred = pred_values.loc[common_idx].values

        mae = np.mean(np.abs(y_true - y_pred))
        rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
        mape = np.mean(np.abs((y_true - y_pred) / (y_true + 1e-10))) * 100

        return {'MAE': mae, 'RMSE': rmse, 'MAPE': mape}

    def residual_diagnostics(self, lags: Optional[int] = None,
                             verbose: bool = True) -> dict:
        """
        残差诊断：Ljung-Box 白噪声检验。
        p > 0.05 表示残差为白噪声（模型充分提取信息）。

        Returns
        -------
        dict : {'ljung_box_stat', 'ljung_box_pvalue', 'is_white_noise'}
        """
        if self.model_fit is None:
            raise RuntimeError("请先拟合模型")
        resid = self.model_fit.resid

        lags_use = min(10, len(resid) // 5) if lags is None else lags
        lb_result = acorr_ljungbox(resid.dropna(), lags=[lags_use],
                                   return_df=True)
        p_value = lb_result['lb_pvalue'].values[0]
        is_white = p_value > 0.05

        if verbose:
            print(f"Ljung-Box 检验 (lag={lags_use}):")
            print(f"  p-value = {p_value:.4f}")
            print(f"  结论: {'残差为白噪声 ✓' if is_white else '残差存在自相关 ✗'}\n")

        return {'ljung_box_stat': lb_result['lb_stat'].values[0],
                'ljung_box_pvalue': p_value, 'is_white_noise': is_white}

    def plot_forecast(self, series: Optional[pd.Series] = None,
                      train_ratio: float = 0.8,
                      save_path: Optional[str] = None):
        """绘制历史数据 + 预测 ± 置信区间"""
        if self.forecast_result is None:
            raise RuntimeError("请先调用 forecast()")
        if series is None:
            series = self.data

        fig, ax = plt.subplots(figsize=(12, 5))

        # 用最近一部分训练数据（避免图太密）
        n_show = int(len(series) * (1 - train_ratio)) + len(self.forecast_result)
        n_show = max(n_show, len(self.forecast_result) * 2)
        show_start = max(0, len(series) - n_show)

        ax.plot(series.index[show_start:], series.values[show_start:],
                'navy', lw=1.5, label='历史数据')
        ax.plot(self.forecast_result.index, self.forecast_result['forecast'],
                'red', lw=2, label='预测值')
        ax.fill_between(self.forecast_result.index,
                         self.forecast_result['lower_ci'],
                         self.forecast_result['upper_ci'],
                         color='red', alpha=0.15, label='95% 置信区间')
        ax.axvline(x=series.index[-1], color='gray', linestyle='--', lw=1)
        ax.set_xlabel('时间')
        ax.set_ylabel('数值')
        ax.set_title('时间序列预测结果')
        ax.legend()
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.show()

    def plot_residuals(self, save_path: Optional[str] = None):
        """残差诊断图：残差时序 + 直方图 + Q-Q 图"""
        if self.model_fit is None:
            raise RuntimeError("请先拟合模型")
        resid = self.model_fit.resid.dropna()

        fig, axes = plt.subplots(1, 3, figsize=(14, 4))

        axes[0].plot(resid, color='steelblue', lw=0.8)
        axes[0].axhline(0, color='red', linestyle='--')
        axes[0].set_title('残差序列')

        axes[1].hist(resid, bins=30, density=True, color='steelblue',
                     alpha=0.7, edgecolor='white')
        x = np.linspace(resid.min(), resid.max(), 200)
        axes[1].plot(x, stats.norm.pdf(x, resid.mean(), resid.std()),
                     'r-', lw=1.5)
        axes[1].set_title('残差分布')

        stats.probplot(resid, dist='norm', plot=axes[2])
        axes[2].get_lines()[1].set_color('steelblue')
        axes[2].set_title('Q-Q 图')

        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.show()


# ===== 使用示例 =====
if __name__ == "__main__":
    print("=== 时间序列预测示例 ===\n")

    # 1) 加载数据
    forecaster = TimeSeriesForecaster(freq='M')
    data = forecaster._load_data()
    print(f"数据范围: {data.index[0].date()} ~ {data.index[-1].date()}")
    print(f"数据点数: {len(data)}\n")

    # 2) 平稳性检验
    forecaster.check_stationarity(data)

    # 3) 季节分解
    forecaster.decompose(data, period=12, model='additive')

    # 4) ACF/PACF 图
    forecaster.plot_acf_pacf(data.diff().dropna(), lags=30)

    # 5) 拟合 SARIMA
    # TODO: 根据 ACF/PACF 图调整 order 和 seasonal_order
    forecaster.fit_sarima(
        order=(1, 1, 1),
        seasonal_order=(1, 1, 1, 12),
        series=data
    )

    # 6) 残差诊断
    forecaster.residual_diagnostics()

    # 7) 预测
    forecast_result = forecaster.forecast(steps=12, series=data, alpha=0.05)
    print("未来 12 期预测:\n", forecast_result[['forecast', 'lower_ci', 'upper_ci']])

    # 8) 画图
    forecaster.plot_forecast(data, train_ratio=0.7)
    forecaster.plot_residuals()

    # ===== Prophet 备选方案（注释，需 pip install prophet） =====
    # from prophet import Prophet
    # df = data.reset_index()
    # df.columns = ['ds', 'y']
    # model = Prophet(yearly_seasonality=True, weekly_seasonality=False)
    # model.fit(df)
    # future = model.make_future_dataframe(periods=12, freq='M')
    # forecast = model.predict(future)
    # model.plot(forecast)
    # model.plot_components(forecast)
    # plt.show()
