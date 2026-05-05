"""
TEST DE VALIDACIÓN DEL MODELO VPSI - VERSIÓN SIN DEPENDENCIAS EXTERNAS
Utiliza la oscillator_solution del framework UIS para generar datos sintéticos.
No requiere yfinance. Puede ejecutarse en el CI sin dependencias externas.
"""

import math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# =========================
# IMPORTAR CONSTANTES DEL FRAMEWORK UIS
# =========================

from formulas.constants import (
    ALPHA, BETA, PHI, EPSILON_OBSERVER,
    THETA_CUBE, OMEGA_D, PHI_TOTAL, ZETA,
    LAMBDA_UCF, LAMBDA_OBS, LAMBDA_ERROR,
    PHI_CRITICAL
)
from formulas.dynamics import oscillator_solution, regime, is_alive

# =========================
# CONSTANTES DERIVADAS PARA EL TEST
# =========================

K_THRESHOLD_BASE = ALPHA - EPSILON_OBSERVER  # 0.9358


# =========================
# GENERACIÓN DE DATOS SINTÉTICOS
# =========================

def generate_synthetic_market_data(days=90, start_price=100, volatility=0.02, trend=0.0001):
    t = np.linspace(0, days, days)
    oscillator_component = np.array([oscillator_solution(ti, A=volatility * 10, delta=0.0) for ti in t])
    trend_component = trend * t
    noise = np.random.normal(0, volatility, days)
    prices = start_price * (1 + trend_component + oscillator_component / 100 + noise)
    prices = np.maximum(prices, start_price * 0.5)
    
    start_date = datetime.now() - timedelta(days=days)
    dates = [start_date + timedelta(days=i) for i in range(days)]
    
    return pd.DataFrame({'Close': prices, 'Volume': np.random.randint(1000000, 10000000, days)}, index=dates)


def generate_tesla_like_data(days=90):
    return generate_synthetic_market_data(days=days, start_price=450, volatility=0.035, trend=-0.002)


def generate_stable_market_data(days=90):
    return generate_synthetic_market_data(days=days, start_price=100, volatility=0.008, trend=0.0005)


# =========================
# ESTIMACIÓN DEL RÉGIMEN DE MERCADO
# =========================

def estimate_hurst_exponent(price_series, max_lag=20):
    if len(price_series) < 10:
        return 0.5
    
    returns = np.diff(np.log(price_series))
    if len(returns) < max_lag:
        max_lag = len(returns) // 2
    if max_lag < 2:
        return 0.5
    
    lags = range(2, max_lag)
    rs_values = []
    
    for lag in lags:
        if len(returns) - lag < 1:
            continue
        n_sub = len(returns) // lag
        if n_sub < 1:
            continue
        
        rs = []
        for i in range(n_sub):
            segment = returns[i*lag:(i+1)*lag]
            if len(segment) < 2:
                continue
            mean_seg = np.mean(segment)
            deviation = np.cumsum(segment - mean_seg)
            r = max(deviation) - min(deviation)
            s = np.std(segment)
            if s > 0:
                rs.append(r / s)
        
        if rs:
            rs_values.append(np.mean(rs))
        else:
            rs_values.append(0)
    
    if len(rs_values) > 2 and len(lags) == len(rs_values):
        log_lags = np.log(list(lags)[:len(rs_values)])
        log_rs = np.log([max(x, 1e-10) for x in rs_values])
        n_points = len(log_lags)
        if n_points > 1:
            x_mean = np.mean(log_lags)
            y_mean = np.mean(log_rs)
            numerator = np.sum((log_lags - x_mean) * (log_rs - y_mean))
            denominator = np.sum((log_lags - x_mean) ** 2)
            if denominator > 0:
                hurst = numerator / denominator
                return max(0.1, min(0.9, hurst))
    
    return 0.5


def estimate_beta_scaling(price_series):
    if len(price_series) < 20:
        return 0.5
    
    returns = np.diff(np.log(price_series))
    n = len(returns)
    scales = np.unique(np.logspace(0, np.log10(n//4), 8).astype(int))
    scales = [s for s in scales if s >= 3 and s <= n//2]
    
    if len(scales) < 2:
        return 0.5
    
    fluct = []
    for scale in scales:
        n_seg = n // scale
        if n_seg < 1:
            continue
        rms_total = 0
        for i in range(n_seg):
            seg = returns[i*scale:(i+1)*scale]
            if len(seg) < 2:
                continue
            x = np.arange(len(seg))
            coeffs = np.polyfit(x, seg, 1)
            trend = np.polyval(coeffs, x)
            detrended = seg - trend
            rms_total += np.sqrt(np.mean(detrended**2))
        fluct.append(rms_total / max(1, n_seg))
    
    if len(fluct) > 1 and len(scales) == len(fluct):
        log_scales = np.log(scales[:len(fluct)])
        log_fluct = np.log([max(x, 1e-10) for x in fluct])
        x_mean = np.mean(log_scales)
        y_mean = np.mean(log_fluct)
        numerator = np.sum((log_scales - x_mean) * (log_fluct - y_mean))
        denominator = np.sum((log_scales - x_mean) ** 2)
        if denominator > 0:
            beta_val = numerator / denominator
            return max(0.2, min(0.8, beta_val))
    
    return 0.5


def estimate_lambda_min(price_series, window=20):
    if len(price_series) < window + 5:
        return 1.0
    
    returns = np.diff(np.log(price_series))
    if len(returns) < window:
        return 1.0
    
    recent_returns = returns[-window:]
    if len(recent_returns) < 2:
        return 1.0
    
    autocorr = np.corrcoef(recent_returns[:-1], recent_returns[1:])[0, 1]
    return max(0.05, min(1.0, (autocorr + 1) / 2))


def classify_regime(hurst, beta_scaling, lambda_min):
    if beta_scaling > 0.45 and beta_scaling < 0.55 and lambda_min < 0.3:
        return "CRITICAL"
    if lambda_min < 0.4 or hurst < 0.4:
        return "COLLAPSING"
    if hurst > 0.58 and beta_scaling > 0.55:
        return "EXPANDING"
    if hurst > 0.45 and hurst < 0.58 and lambda_min > 0.5:
        return "STABLE"
    return "STABLE"


# =========================
# CÁLCULO DE K Y C_Ω
# =========================

def compute_k_from_price(price_series, window=20):
    if len(price_series) < window + 10:
        return BETA
    
    series = pd.Series(price_series) if not isinstance(price_series, pd.Series) else price_series
    mom = series.pct_change(periods=5).iloc[-window:]
    future_ret = series.pct_change(periods=1).shift(-1).iloc[-window:]
    
    if len(mom) > 3 and len(future_ret) > 3:
        valid_mask = ~(mom.isna() | future_ret.isna())
        if valid_mask.sum() > 3:
            mom_vals = mom[valid_mask].values
            ret_vals = future_ret[valid_mask].values
            if np.std(mom_vals) > 0 and np.std(ret_vals) > 0:
                ic = np.corrcoef(mom_vals, ret_vals)[0, 1]
                return max(BETA, min(ALPHA, (ic + 1) / 2))
    
    return ALPHA * 0.3


def compute_c_omega(k, hurst, regime):
    c_base = k
    if regime == "CRITICAL":
        c_regime_penalty = 0.3
    elif regime == "COLLAPSING":
        c_regime_penalty = 0.5
    else:
        c_regime_penalty = 0.9
    
    hurst_factor = min(1.0, hurst / 0.5)
    c_omega = c_base * c_regime_penalty * hurst_factor
    return min(ALPHA, max(BETA * 2, c_omega))


def decide_investment(c_omega, k, hurst, lambda_min, regime):
    conditions = {
        "c_omega_sufficient": c_omega >= ALPHA * 0.7,
        "k_sufficient": k >= K_THRESHOLD_BASE * 0.8,
        "hurst_favorable": hurst > 0.48,
        "lambda_min_safe": lambda_min > 0.3,
        "regime_not_critical": regime not in ["CRITICAL"]
    }
    
    if all(conditions.values()):
        return "INVEST"
    return "HOLD"


# =========================
# TEST PRINCIPAL
# =========================

def run_synthetic_test():
    print("=" * 80)
    print("VPSI MARKET REGIME DETECTION - SYNTHETIC DATA TEST")
    print("=" * 80)
    
    df = generate_tesla_like_data(days=90)
    print(f"\nDatos generados: {len(df)} días")
    print(f"Precio inicial: ${df['Close'].iloc[0]:.2f}")
    print(f"Precio final: ${df['Close'].iloc[-1]:.2f}")
    
    results = []
    window_size = 30
    
    for i in range(window_size, len(df)):
        price_window = df["Close"].iloc[max(0, i-window_size):i+1]
        
        hurst = estimate_hurst_exponent(price_window.values)
        beta_scaling = estimate_beta_scaling(price_window.values)
        lambda_min = estimate_lambda_min(price_window.values)
        regime = classify_regime(hurst, beta_scaling, lambda_min)
        
        k = compute_k_from_price(price_window.values)
        c_omega = compute_c_omega(k, hurst, regime)
        decision = decide_investment(c_omega, k, hurst, lambda_min, regime)
        
        results.append({"regime": regime, "k": k, "c_omega": c_omega, "decision": decision})
    
    df_results = pd.DataFrame(results)
    print(f"\nRégimen más frecuente: {df_results['regime'].mode()[0]}")
    print(f"Decisión más frecuente: {df_results['decision'].mode()[0]}")
    print(f"K promedio: {df_results['k'].mean():.4f}")
    print(f"C_Ω promedio: {df_results['c_omega'].mean():.4f}")
    
    return df_results


def test_system_health():
    print("\nVERIFICACIÓN DEL SISTEMA (UCF v3.3)")
    print(f"PHI_TOTAL = {PHI_TOTAL:.6f}")
    print(f"PHI_CRITICAL = {PHI_CRITICAL:.6f}")
    print(f"ZETA = {ZETA:.6f}")
    print(f"Sistema vivo: {is_alive(PHI_TOTAL)}")
    
    assert abs(ALPHA + BETA - 1.0) < 1e-9
    assert abs(math.sin(THETA_CUBE) ** 2 - BETA) < 1e-9
    assert PHI_TOTAL < PHI_CRITICAL
    assert ZETA < 1.0
    assert OMEGA_D > 0
    print("✅ Verificaciones estructurales pasaron.")
    return True


# =========================
# MAIN
# =========================

if __name__ == "__main__":
    test_system_health()
    run_synthetic_test()
