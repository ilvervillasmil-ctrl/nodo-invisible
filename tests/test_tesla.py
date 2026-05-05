"""
TEST DE VALIDACIÓN DEL MODELO VPSI EN TESLA (TSLA)
Datos reales desde yfinance
Ejecuta este script para ver el régimen del mercado y las decisiones del modelo
"""

import yfinance as yf
import pandas as pd
import numpy as np
import math
from datetime import datetime, timedelta

# =========================
# CONSTANTES DEL FRAMEWORK UIS (derivadas de 27)
# =========================

ALPHA = 26/27          # 0.962962962962963
BETA = 1/27            # 0.037037037037037
PHI = (1 + math.sqrt(5)) / 2  # 1.618033988749895
EPSILON_OBSERVER = 0.02716    # Residuo irreducible del observador

K_THRESHOLD_BASE = ALPHA - EPSILON_OBSERVER  # 0.9358

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
        # Dividir en subperíodos
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
        log_rs = np.log(rs_values)
        # Regresión simple
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
    
    # DFA simplificado
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
            # Detrend (quitar tendencia lineal)
            coeffs = np.polyfit(x, seg, 1)
            trend = np.polyval(coeffs, x)
            detrended = seg - trend
            rms_total += np.sqrt(np.mean(detrended**2))
        fluct.append(rms_total / max(1, n_seg))
    
    if len(fluct) > 1 and len(scales) == len(fluct):
        log_scales = np.log(scales[:len(fluct)])
        log_fluct = np.log(fluct)
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
    
    # Calcular matriz de correlación móvil
    recent_returns = returns[-window:]
    if len(recent_returns) < 2:
        return 1.0
    
    # Construir matriz de correlación simplificada
    # (en un caso real, usarías múltiples sectores)
    # Aquí usamos autocorrelación como proxy
    autocorr = np.corrcoef(recent_returns[:-1], recent_returns[1:])[0, 1]
    
    # λ_min pequeño indica pérdida de coherencia
    # Si autocorr es negativa o cercana a cero, λ_min tiende a 0
    lambda_min = max(0.05, min(1.0, (autocorr + 1) / 2))
    
    return lambda_min


def classify_regime(hurst, beta_scaling, lambda_min):
    """Clasifica el régimen del mercado según las tres métricas"""
    
    # CRITICAL: β ≈ 0.5 y λ_min pequeño (colapso inminente)
    if beta_scaling > 0.45 and beta_scaling < 0.55 and lambda_min < 0.3:
        return "CRITICAL", "Colapso inminente detectado (β≈0.5, λ_min pequeño)"
    
    # COLLAPSING: pérdida de coherencia
    if lambda_min < 0.4 or hurst < 0.4:
        return "COLLAPSING", "Pérdida de coherencia estructural"
    
    # EXPANDING: tendencia fuerte
    if hurst > 0.58 and beta_scaling > 0.55:
        return "EXPANDING", "Expansión con tendencia persistente"
    
    # STABLE: régimen normal
    if hurst > 0.45 and hurst < 0.58 and lambda_min > 0.5:
        return "STABLE", "Régimen estable, transable"
    
    # DEFAULT
    return "STABLE", "Régimen normal"


# =========================
# CÁLCULO DE K (CORRELACIÓN)
# =========================

def compute_k_from_price(price_series, window=20):
    """Calcula K como Information Coefficient simple"""
    if len(price_series) < window + 10:
        return BETA
    
    # Señal de momentum (predicción simple)
    mom = price_series.pct_change(periods=5).iloc[-window:]
    
    # Retorno futuro (outcome)
    future_ret = price_series.pct_change(periods=1).shift(-1).iloc[-window:]
    
    # Correlación entre señal y resultado → Information Coefficient
    if len(mom) > 3 and len(future_ret) > 3:
        valid_mask = ~(mom.isna() | future_ret.isna())
        if valid_mask.sum() > 3:
            mom_vals = mom[valid_mask].values
            ret_vals = future_ret[valid_mask].values
            if np.std(mom_vals) > 0 and np.std(ret_vals) > 0:
                ic = np.corrcoef(mom_vals, ret_vals)[0, 1]
                # Clampear y asegurar β mínimo
                k = max(BETA, min(ALPHA, (ic + 1) / 2))
                return k
    
    return ALPHA * 0.3  # Default moderado


# =========================
# CÁLCULO DE C_Ω (COHERENCIA)
# =========================

def compute_c_omega(k, hurst, regime):
    """C_Ω simplificado para la prueba"""
    # Base: K
    c_base = k
    
    # Penalización por baja coherencia estructural
    if regime == "CRITICAL":
        c_regime_penalty = 0.3
    elif regime == "COLLAPSING":
        c_regime_penalty = 0.5
    else:
        c_regime_penalty = 0.9
    
    # Penalización por baja persistencia (hurst < 0.5)
    hurst_factor = min(1.0, hurst / 0.5)
    
    c_omega = c_base * c_regime_penalty * hurst_factor
    
    return min(ALPHA, max(BETA * 2, c_omega))


# =========================
# DECISIÓN DE INVERSIÓN
# =========================

def decide_investment(c_omega, k, hurst, lambda_min, regime):
    """Decisión final basada en todas las métricas"""
    
    # Condiciones para INVERTIR
    conditions = {
        "c_omega_sufficient": c_omega >= ALPHA * 0.7,  # 0.674
        "k_sufficient": k >= K_THRESHOLD_BASE * 0.8,   # ~0.748
        "hurst_favorable": hurst > 0.48,
        "lambda_min_safe": lambda_min > 0.3,
        "regime_not_critical": regime not in ["CRITICAL"]
    }
    
    all_met = all(conditions.values())
    
    if all_met:
        # Calcular confianza adicional
        confidence = (c_omega + k) / 2
        if confidence > 0.8:
            return "INVEST", "Alta confianza", conditions
        else:
            return "INVEST", "Confianza moderada", conditions
    else:
        # Identificar la principal razón para no invertir
        if not conditions["regime_not_critical"]:
            reason = f"Régimen CRITICAL detectado (β escalado cerca de 0.5)"
        elif not conditions["c_omega_sufficient"]:
            reason = f"C_Ω demasiado bajo ({c_omega:.3f} < {ALPHA*0.7:.3f})"
        elif not conditions["k_sufficient"]:
            reason = f"K demasiado bajo ({k:.3f} < {K_THRESHOLD_BASE*0.8:.3f})"
        elif not conditions["hurst_favorable"]:
            reason = f"Baja persistencia (H={hurst:.3f} < 0.48)"
        elif not conditions["lambda_min_safe"]:
            reason = f"Pérdida de coherencia (λ_min={lambda_min:.3f} < 0.3)"
        else:
            reason = "Múltiples condiciones no cumplidas"
        
        return "HOLD", reason, conditions


# =========================
# MAIN - TEST CON TESLA
# =========================

def run_tesla_test():
    print("=" * 80)
    print("VPSI MARKET REGIME DETECTION - REAL DATA TEST")
    print("Tesla (TSLA) - Últimos 60 días")
    print("=" * 80)
    
    # === 1. DESCARGAR DATOS REALES ===
    print("\n[1] Descargando datos de Tesla (TSLA)...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)  # 90 días para tener 60 de análisis
    
    ticker = yf.Ticker("TSLA")
    df = ticker.history(start=start_date, end=end_date, interval="1d")
    
    if df.empty:
        print("ERROR: No se pudieron descargar los datos de Tesla")
        return None
    
    print(f"    Datos descargados: {len(df)} días ({df.index[0].date()} a {df.index[-1].date()})")
    
    # === 2. ANÁLISIS DÍA POR DÍA ===
    print("\n[2] Analizando régimen día por día...")
    print("-" * 80)
    
    results = []
    window_size = 30  # Días para análisis de régimen
    
    # También descargar SPY para comparación de mercado
    spy = yf.Ticker("SPY")
    df_spy = spy.history(start=start_date, end=end_date, interval="1d")
    
    for i in range(window_size, len(df)):
        current_date = df.index[i]
        price_window = df["Close"].iloc[max(0, i-window_size):i+1]
        current_price = df["Close"].iloc[i]
        
        # Métricas de régimen
        hurst = estimate_hurst_exponent(price_window.values)
        beta_scaling = estimate_beta_scaling(price_window.values)
        lambda_min = estimate_lambda_min(price_window.values)
        regime, regime_desc = classify_regime(hurst, beta_scaling, lambda_min)
        
        # K y C_Ω
        k = compute_k_from_price(price_window.values)
        c_omega = compute_c_omega(k, hurst, regime)
        
        # Decisión final
        decision, reason, conditions = decide_investment(c_omega, k, hurst, lambda_min, regime)
        
        # Precio de SPY para contexto
        spy_price = None
        if len(df_spy) > i:
            spy_price = df_spy["Close"].iloc[i] if i < len(df_spy) else None
        
        results.append({
            "date": current_date,
            "price": current_price,
            "spy_price": spy_price,
            "hurst": hurst,
            "beta_scaling": beta_scaling,
            "lambda_min": lambda_min,
            "regime": regime,
            "k": k,
            "c_omega": c_omega,
            "decision": decision,
            "reason": reason
        })
    
    # === 3. MOSTRAR RESULTADOS ===
    print(f"\n{'Date':<12} {'Price':<10} {'Regime':<12} {'Hurst':<7} {'β_scal':<7} {'K':<7} {'C_Ω':<7} {'Decision':<8}")
    print("-" * 85)
    
    for r in results[-30:]:  # Últimos 30 días
        print(f"{r['date'].strftime('%Y-%m-%d'):<12} "
              f"${r['price']:<9.2f} "
              f"{r['regime']:<12} "
              f"{r['hurst']:.3f}   "
              f"{r['beta_scaling']:.3f}   "
              f"{r['k']:.3f}   "
              f"{r['c_omega']:.3f}   "
              f"{r['decision']:<8}")
    
    # === 4. ESTADÍSTICAS ===
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
    
    # Calcular retorno del mercado y retorno teórico del modelo
    initial_price = results[0]["price"] if results else 1
    final_price = results[-1]["price"] if results else 1
    market_return = (final_price - initial_price) / initial_price * 100
    
    # Retorno teórico si solo se invierte en días de INVEST
    portfolio_value = 10000
    invested_days = 0
    for r in results:
        if r["decision"] == "INVEST":
            invested_days += 1
            # Simulación simple: seguir el mercado
            daily_return = (r["price"] / results[0]["price"] - 1) if r == results[0] else 0
    
    # Retorno final simplificado
    theoretical_return = market_return * (decision_counts.get("INVEST", 0) / len(results))
    
    print(f"\nRendimiento del mercado ({results[0]['date'].date()} a {results[-1]['date'].date()}):")
    print(f"  Precio inicial: ${initial_price:.2f}")
    print(f"  Precio final: ${final_price:.2f}")
    print(f"  Retorno: {market_return:.2f}%")
    
    if "INVEST" in decision_counts:
        print(f"\nRendimiento teórico del modelo (solo días INVEST):")
        print(f"  Días invertidos: {decision_counts['INVEST']} de {len(results)} ({decision_counts['INVEST']/len(results)*100:.1f}%)")
    
    print(f"\nRecomendación final según el modelo VPSI:")
    last_regime = results[-1]["regime"] if results else "UNKNOWN"
    last_decision = results[-1]["decision"] if results else "UNKNOWN"
    last_reason = results[-1]["reason"] if results else ""
    
    print(f"  Régimen actual: {last_regime}")
    print(f"  Decisión actual: {last_decision}")
    if last_decision == "HOLD":
        print(f"  Razón: {last_reason}")
    
    if last_regime == "CRITICAL":
        print("\n⚠️  ADVERTENCIA: El mercado está en régimen CRITICAL.")
        print("   El modelo recomienda NO INVERTIR hasta que se recupere la coherencia estructural.")
    elif last_regime == "COLLAPSING":
        print("\n⚠️  PRECAUCIÓN: El mercado está perdiendo coherencia.")
        print("   Se recomienda posiciones muy pequeñas o nulas.")
    else:
        print(f"\n✅ El mercado está en régimen {last_regime}.")
        if last_decision == "INVEST":
            print("   El modelo permite inversión con gestión de riesgo adecuada (β = 3.7% por operación).")
    
    return results


# =========================
# EJECUTAR TEST
# =========================

if __name__ == "__main__":
    results = run_tesla_test()
    
    print("\n" + "=" * 80)
    print("CONCLUSIÓN")
    print("=" * 80)
    print("""
El modelo VPSI no predice si Tesla subirá o bajará.
Predice si el MERCADO está en un régimen transable o no.

Si el régimen es CRITICAL o COLLAPSING → NO INVERTIR.
Si el régimen es EXPANDING o STABLE → INVERSIÓN POSIBLE con riesgo β = 1/27.

Esto es conocimiento útil porque evita operar en condiciones donde la señal
es ruido y el sistema de decisión no está integrado.
""")
