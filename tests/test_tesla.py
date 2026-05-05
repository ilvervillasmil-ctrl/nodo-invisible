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
# IMPORTAR CONSTANTES DEL FRAMEWORK UIS (CORRECTAMENTE)
# =========================

from formulas.constants import (
    ALPHA, BETA, PHI, EPSILON_OBSERVER,
    THETA_CUBE, OMEGA_D, PHI_TOTAL, ZETA,
    LAMBDA_UCF, LAMBDA_OBS, LAMBDA_ERROR,
    PHI_CRITICAL, OMEGA_0
)
from formulas.dynamics import oscillator_solution, regime, is_alive

# =========================
# CONSTANTES DERIVADAS PARA EL TEST
# =========================

K_THRESHOLD_BASE = ALPHA - EPSILON_OBSERVER  # 0.9358


# =========================
# GENERACIÓN DE DATOS SINTÉTICOS (reemplaza a yfinance)
# =========================

def generate_synthetic_market_data(days=90, start_price=100, volatility=0.02, trend=0.0001):
    """Genera datos de mercado sintéticos usando la ecuación del oscilador del framework."""
    t = np.linspace(0, days, days)
    oscillator_component = oscillator_solution(t, A=volatility * 10, delta=0.0)
    trend_component = trend * t
    noise = np.random.normal(0, volatility, days)
    prices = start_price * (1 + trend_component + oscillator_component / 100 + noise)
    prices = np.maximum(prices, start_price * 0.5)
    
    start_date = datetime.now() - timedelta(days=days)
    dates = [start_date + timedelta(days=i) for i in range(days)]
    
    df = pd.DataFrame({'Close': prices, 'Volume': np.random.randint(1000000, 10000000, days)}, index=dates)
    return df


def generate_tesla_like_data(days=90):
    """Genera datos que imitan el comportamiento de Tesla en 2026."""
    return generate_synthetic_market_data(
        days=days,
        start_price=450,
        volatility=0.035,
        trend=-0.002
    )


def generate_stable_market_data(days=90):
    """Genera datos de mercado estable (para comparación)."""
    return generate_synthetic_market_data(
        days=days,
        start_price=100,
        volatility=0.008,
        trend=0.0005
    )


# =========================
# ESTIMACIÓN DEL RÉGIMEN DE MERCADO
# =========================

def estimate_hurst_exponent(price_series, max_lag=20):
    """Estima el exponente de Hurst (persistencia) usando R/S analysis"""
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
    """Estima el exponente de escalamiento β (cercano a 0.5 en colapsos)"""
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
    """Estima el valor propio mínimo del Hessiano de coherencia"""
    if len(price_series) < window + 5:
        return 1.0
    
    returns = np.diff(np.log(price_series))
    if len(returns) < window:
        return 1.0
    
    recent_returns = returns[-window:]
    if len(recent_returns) < 2:
        return 1.0
    
    autocorr = np.corrcoef(recent_returns[:-1], recent_returns[1:])[0, 1]
    lambda_min = max(0.05, min(1.0, (autocorr + 1) / 2))
    
    return lambda_min


def classify_regime(hurst, beta_scaling, lambda_min):
    """Clasifica el régimen del mercado según las tres métricas"""
    
    if beta_scaling > 0.45 and beta_scaling < 0.55 and lambda_min < 0.3:
        return "CRITICAL", "Colapso inminente detectado (β≈0.5, λ_min pequeño)"
    
    if lambda_min < 0.4 or hurst < 0.4:
        return "COLLAPSING", "Pérdida de coherencia estructural"
    
    if hurst > 0.58 and beta_scaling > 0.55:
        return "EXPANDING", "Expansión con tendencia persistente"
    
    if hurst > 0.45 and hurst < 0.58 and lambda_min > 0.5:
        return "STABLE", "Régimen estable, transable"
    
    return "STABLE", "Régimen normal"


def compute_k_from_price(price_series, window=20):
    """Calcula K como Information Coefficient simple"""
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
                k = max(BETA, min(ALPHA, (ic + 1) / 2))
                return k
    
    return ALPHA * 0.3


def compute_c_omega(k, hurst, regime):
    """C_Ω simplificado para la prueba"""
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
    """Decisión final basada en todas las métricas"""
    
    conditions = {
        "c_omega_sufficient": c_omega >= ALPHA * 0.7,
        "k_sufficient": k >= K_THRESHOLD_BASE * 0.8,
        "hurst_favorable": hurst > 0.48,
        "lambda_min_safe": lambda_min > 0.3,
        "regime_not_critical": regime not in ["CRITICAL"]
    }
    
    all_met = all(conditions.values())
    
    if all_met:
        confidence = (c_omega + k) / 2
        if confidence > 0.8:
            return "INVEST", "Alta confianza", conditions
        else:
            return "INVEST", "Confianza moderada", conditions
    else:
        if not conditions["regime_not_critical"]:
            reason = "Régimen CRITICAL detectado"
        elif not conditions["c_omega_sufficient"]:
            reason = f"C_Ω bajo ({c_omega:.3f} < {ALPHA*0.7:.3f})"
        elif not conditions["k_sufficient"]:
            reason = f"K bajo ({k:.3f} < {K_THRESHOLD_BASE*0.8:.3f})"
        elif not conditions["hurst_favorable"]:
            reason = f"Baja persistencia (H={hurst:.3f} < 0.48)"
        elif not conditions["lambda_min_safe"]:
            reason = f"Pérdida coherencia (λ_min={lambda_min:.3f} < 0.3)"
        else:
            reason = "Múltiples condiciones no cumplidas"
        
        return "HOLD", reason, conditions


# =========================
# FUNCIÓN PRINCIPAL DE TEST
# =========================

def run_synthetic_test():
    """Ejecuta el test con datos sintéticos"""
    print("=" * 80)
    print("VPSI MARKET REGIME DETECTION - SYNTHETIC DATA TEST")
    print("(No external dependencies - can run in CI)")
    print("=" * 80)
    
    # Generar datos sintéticos que imitan a Tesla
    print("\n[1] Generando datos sintéticos (Tesla-like)...")
    df = generate_tesla_like_data(days=90)
    print(f"    Datos generados: {len(df)} días ({df.index[0].date()} a {df.index[-1].date()})")
    print(f"    Precio inicial: ${df['Close'].iloc[0]:.2f}")
    print(f"    Precio final: ${df['Close'].iloc[-1]:.2f}")
    
    # Análisis día por día
    print("\n[2] Analizando régimen día por día...")
    print("-" * 85)
    
    results = []
    window_size = 30
    
    for i in range(window_size, len(df)):
        current_date = df.index[i]
        price_window = df["Close"].iloc[max(0, i-window_size):i+1]
        current_price = df["Close"].iloc[i]
        
        hurst = estimate_hurst_exponent(price_window.values)
        beta_scaling = estimate_beta_scaling(price_window.values)
        lambda_min = estimate_lambda_min(price_window.values)
        regime, regime_desc = classify_regime(hurst, beta_scaling, lambda_min)
        
        k = compute_k_from_price(price_window.values)
        c_omega = compute_c_omega(k, hurst, regime)
        decision, reason, conditions = decide_investment(c_omega, k, hurst, lambda_min, regime)
        
        results.append({
            "date": current_date,
            "price": current_price,
            "hurst": hurst,
            "beta_scaling": beta_scaling,
            "lambda_min": lambda_min,
            "regime": regime,
            "k": k,
            "c_omega": c_omega,
            "decision": decision,
            "reason": reason
        })
    
    # Mostrar resultados
    print(f"\n{'Date':<12} {'Price':<10} {'Regime':<12} {'Hurst':<7} {'β_scal':<7} {'K':<7} {'C_Ω':<7} {'Decision':<8}")
    print("-" * 85)
    
    for r in results[-20:]:
        print(f"{r['date'].strftime('%Y-%m-%d'):<12} "
              f"${r['price']:<9.2f} "
              f"{r['regime']:<12} "
              f"{r['hurst']:.3f}   "
              f"{r['beta_scaling']:.3f}   "
              f"{r['k']:.3f}   "
              f"{r['c_omega']:.3f}   "
              f"{r['decision']:<8}")
    
    # Estadísticas
    print("\n" + "=" * 80)
    print("[3] ESTADÍSTICAS DEL PERIODO")
    print("=" * 80)
    
    decisions_df = pd.DataFrame(results)
    regime_counts = decisions_df["regime"].value_counts()
    decision_counts = decisions_df["decision"].value_counts()
    
    print(f"\nPeríodo analizado: {len(results)} días")
    print(f"\nDistribución de Regímenes:")
    for regime, count in regime_counts.items():
        pct = count / len(results) * 100
        print(f"  {regime}: {count} días ({pct:.1f}%)")
    
    print(f"\nDecisiones del modelo:")
    for decision, count in decision_counts.items():
        pct = count / len(results) * 100
        print(f"  {decision}: {count} días ({pct:.1f}%)")
    
    # Retorno y resultados finales
    initial_price = results[0]["price"] if results else 1
    final_price = results[-1]["price"] if results else 1
    market_return = (final_price - initial_price) / initial_price * 100
    
    print(f"\nRendimiento del mercado sintético:")
    print(f"  Precio inicial: ${initial_price:.2f}")
    print(f"  Precio final: ${final_price:.2f}")
    print(f"  Retorno: {market_return:.2f}%")
    
    print(f"\nRecomendación final según el modelo VPSI:")
    last_regime = results[-1]["regime"] if results else "UNKNOWN"
    last_decision = results[-1]["decision"] if results else "UNKNOWN"
    
    print(f"  Régimen actual: {last_regime}")
    print(f"  Decisión actual: {last_decision}")
    
    if last_regime == "CRITICAL":
        print("\n⚠️  El modelo recomienda NO INVERTIR (régimen CRITICAL).")
    elif last_regime == "COLLAPSING":
        print("\n⚠️  El modelo recomienda posiciones reducidas o nulas (régimen COLLAPSING).")
    else:
        print(f"\n✅ El mercado está en régimen {last_regime}.")
        if last_decision == "INVEST":
            print("   El modelo permite inversión con gestión de riesgo adecuada.")
    
    return results


def test_system_health():
    """Verifica que el sistema esté vivo según los parámetros del framework"""
    print("\n" + "=" * 80)
    print("VERIFICACIÓN DEL SISTEMA (UCF v3.3)")
    print("=" * 80)
    
    # Usar las constantes importadas correctamente (PHI_TOTAL, etc. ya están importadas)
    print(f"\nParámetros del oscilador:")
    print(f"  PHI_TOTAL = {PHI_TOTAL:.6f}")
    print(f"  PHI_CRITICAL = {PHI_CRITICAL:.6f}")
    print(f"  ZETA = {ZETA:.6f}")
    print(f"  OMEGA_D = {OMEGA_D:.6f}")
    print(f"  OMEGA_0 = {OMEGA_0:.6f}")
    print(f"  Régimen: {regime(PHI_TOTAL)}")
    print(f"  Sistema vivo: {is_alive(PHI_TOTAL)}")
    
    print(f"\nConstantes fundamentales:")
    print(f"  ALPHA = {ALPHA:.10f} (26/27)")
    print(f"  BETA = {BETA:.10f} (1/27)")
    print(f"  PHI = {PHI:.10f}")
    print(f"  EPSILON_OBSERVER = {EPSILON_OBSERVER:.10f}")
    
    print(f"\nCosmología:")
    print(f"  LAMBDA_UCF = {LAMBDA_UCF:.6e}")
    print(f"  LAMBDA_OBS = {LAMBDA_OBS:.6e}")
    print(f"  Error = {LAMBDA_ERROR:.4%}")
    
    # Verificaciones estructurales
    assertions_passed = True
    try:
        assert abs(ALPHA + BETA - 1.0) < 1e-9, "alpha + beta != 1"
        assert abs(math.sin(THETA_CUBE) ** 2 - BETA) < 1e-9, "sin^2(theta_cube) != beta"
        assert PHI_TOTAL < PHI_CRITICAL, "System not underdamped: phi_total >= 2*pi"
        assert ZETA < 1.0, "System not underdamped: zeta >= 1"
        assert OMEGA_D > 0, "System not oscillating: omega_d <= 0"
        print("\n✅ Todas las verificaciones estructurales pasaron.")
    except AssertionError as e:
        assertions_passed = False
        print(f"\n❌ Falló verificación estructural: {e}")
    
    return assertions_passed


# =========================
# TEST DE PYTEST
# =========================

def test_synthetic_market_regime():
    """Test principal para pytest - verifica que el modelo funciona sin errores"""
    results = run_synthetic_test()
    assert len(results) > 0
    assert all(r["decision"] in ["INVEST", "HOLD"] for r in results)
    assert all(r["regime"] in ["CRITICAL", "COLLAPSING", "EXPANDING", "STABLE"] for r in results)


def test_system_health_pytest():
    """Test de salud del sistema para pytest"""
    assert test_system_health() is True


def test_constants_consistency():
    """Verifica que las constantes del framework sean consistentes"""
    from formulas.constants import ALPHA, BETA, THETA_CUBE, PHI_TOTAL, PHI_CRITICAL, ZETA, OMEGA_D
    
    assert abs(ALPHA + BETA - 1.0) < 1e-9
    assert abs(math.sin(THETA_CUBE) ** 2 - BETA) < 1e-9
    assert PHI_TOTAL < PHI_CRITICAL
    assert ZETA < 1.0
    assert OMEGA_D > 0


# =========================
# MAIN
# =========================

if __name__ == "__main__":
    # Primero verificar la salud del sistema
    test_system_health()
    
    # Ejecutar el test con datos sintéticos
    results = run_synthetic_test()
    
    print("\n" + "=" * 80)
    print("CONCLUSIÓN")
    print("=" * 80)
    print("""
El modelo VPSI no predice si un activo subirá o bajará.
Predice si el MERCADO está en un régimen transable o no.

Si el régimen es CRITICAL o COLLAPSING → NO INVERTIR.
Si el régimen es EXPANDING o STABLE → INVERSIÓN POSIBLE con riesgo β = 1/27.

Este test utiliza datos sintéticos generados por la oscillator_solution del
propio framework UIS, por lo que NO requiere yfinance ni dependencias externas.
Puede ejecutarse en el CI sin problemas.
""")
