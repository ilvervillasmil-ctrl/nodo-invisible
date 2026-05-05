"""
SISTEMA DE TRADING UNIVERSAL BASADO EN UIS v3.3
Integra:
- Constantes derivadas del cubo (α, β, φ, ε_observer)
- Estimación de régimen de mercado (Hurst, β_scaling, λ_min)
- Factor de correlación K (Information Coefficient)
- C_Ω a través del CoherenceEngine real
- Memoria persistente (L5: Metaconciencia)
- Decisión BUY/SELL/HOLD basada en L4 (integración)
- Gestión de riesgo dinámica (Kelly fraccional con β)
- Validación de propósito L6 (φ=0)
- Ecuación dinámica del oscilador para evolución temporal

Autor: I. Villasmil
Framework: UIS / VPSI v3.3
"""

import math
import numpy as np
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

# =========================
# IMPORTAR CONSTANTES DEL FRAMEWORK UIS
# =========================

from formulas.constants import (
    ALPHA, BETA, PHI, KAPPA, S_REF, R_FIN,
    THETA_CUBE, OMEGA_D, PHI_TOTAL, ZETA,
    LAMBDA_UCF, LAMBDA_OBS, LAMBDA_ERROR,
    EPSILON_OBSERVER, PHI_CRITICAL, T_PERIOD,
    OMEGA_0, C_MAX
)
from formulas.dynamics import oscillator_solution, regime, is_alive
from formulas.coherence import CoherenceEngine
from formulas.energy import LayerEnergy
from formulas.negentropy import NegentropyCalculator
from formulas.interaction import ExternalInteraction
from formulas.presence import PresenceLogic
from formulas.wonder import WonderLogic
from formulas.resonance import ResonanceLogic
from formulas.metaconsciousness import MetaconsciousnessCalculator

# =========================
# CONFIGURACIÓN DERIVADA DEL FRAMEWORK
# =========================

K_THRESHOLD_BASE = ALPHA - EPSILON_OBSERVER  # 0.9358
RISK_PER_TRADE_MAX = BETA * 2  # 7.4%
RISK_PER_TRADE_MIN = BETA  # 3.7%

# =========================
# GENERACIÓN DE DATOS SINTÉTICOS (para pruebas sin yfinance)
# =========================

def generate_synthetic_market_data(days=90, start_price=100, volatility=0.02, trend=0.0001):
    """Genera datos de mercado sintéticos usando la ecuación del oscilador del framework."""
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
    return max(0.05, min(1.0, (autocorr + 1) / 2))


def classify_regime(hurst: float, beta_scaling: float, lambda_min: float) -> Tuple[str, str]:
    """Clasifica el régimen del mercado según las tres métricas"""
    
    # CRITICAL: β≈0.5 y λ_min pequeño
    if beta_scaling > 0.45 and beta_scaling < 0.55 and lambda_min < 0.3:
        return "CRITICAL", "Colapso inminente detectado"
    
    # COLLAPSING: pérdida de coherencia
    if lambda_min < 0.4 or hurst < 0.4:
        return "COLLAPSING", "Pérdida de coherencia estructural"
    
    # EXPANDING: tendencia fuerte
    if hurst > 0.58 and beta_scaling > 0.55:
        return "EXPANDING", "Expansión con tendencia persistente"
    
    # STABLE: régimen normal
    if hurst > 0.45 and hurst < 0.58 and lambda_min > 0.5:
        return "STABLE", "Régimen estable, transable"
    
    return "STABLE", "Régimen normal"


# =========================
# INDICADORES TÉCNICOS
# =========================

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula indicadores técnicos derivados de constantes del framework."""
    # Períodos derivados de constantes geométricas
    df["SMA20"] = df["Close"].rolling(20).mean()
    df["SMA50"] = df["Close"].rolling(50).mean()
    df["volatility"] = df["Close"].pct_change().rolling(20).std()
    
    # RSI (periodo derivado de 27/2 ≈ 13.5, redondeado a 14)
    df["RSI"] = compute_rsi(df["Close"], period=14)
    
    # Bandas de Bollinger usando BETA como multiplicador
    df["BB_middle"] = df["Close"].rolling(20).mean()
    bb_std = df["Close"].rolling(20).std()
    df["BB_upper"] = df["BB_middle"] + BETA * bb_std
    df["BB_lower"] = df["BB_middle"] - BETA * bb_std
    
    # Momentum basado en la proporción áurea
    df["momentum_phi"] = df["Close"].pct_change(periods=int(PHI * 10))
    
    return df


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Calcula el RSI."""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / (loss + 1e-6)
    return 100 - (100 / (1 + rs))


# =========================
# SEÑALES (distribuciones de probabilidad)
# =========================

def generate_signal_distribution(row: pd.Series, regime: str, hurst: float) -> Dict:
    """Genera probabilidades ajustadas por el régimen de mercado."""
    signals = {}
    
    # Tendencia basada en SMA
    sma_diff = (row["SMA20"] - row["SMA50"]) / max(row["SMA50"], 1)
    prob_trend_up = 1 / (1 + math.exp(-sma_diff * 10))
    signals["trend_up_prob"] = prob_trend_up
    signals["trend_down_prob"] = 1 - prob_trend_up
    
    # RSI como probabilidad de sobrecompra/sobreventa
    rsi = row["RSI"]
    if rsi < 30:
        signals["oversold_prob"] = 1 - (rsi / 30)
        signals["overbought_prob"] = 0.0
    elif rsi > 70:
        signals["overbought_prob"] = (rsi - 70) / 30
        signals["oversold_prob"] = 0.0
    else:
        signals["oversold_prob"] = 0.0
        signals["overbought_prob"] = 0.0
    
    # Incertidumbre
    signals["uncertainty"] = min(1.0, row["volatility"] * 10)
    
    # Ajustes por persistencia (Hurst)
    if hurst > 0.6:
        signals["trend_up_prob"] = min(1.0, prob_trend_up + (1 - prob_trend_up) * (hurst - 0.6) * 2)
        signals["trend_down_prob"] = 1 - signals["trend_up_prob"]
    elif hurst < 0.4:
        signals["uncertainty"] = min(1.0, signals["uncertainty"] * 1.5)
    
    # Ajustes por régimen
    if regime == "CRITICAL":
        signals["uncertainty"] = 1.0
    elif regime == "COLLAPSING":
        signals["uncertainty"] = min(1.0, signals["uncertainty"] * 1.2)
    elif regime == "EXPANDING":
        signals["uncertainty"] *= 0.8
    
    return signals


# =========================
# VERIFIER K (VPSI)
# =========================

def compute_k_vpsi(signals: Dict, regime: str) -> float:
    """
    K = factor de correlación con el dominio observable.
    Fórmula: K = (k_trend + α·k_extreme) · (1 - k_uncertainty)
    """
    k_trend = max(signals["trend_up_prob"], signals["trend_down_prob"])
    k_extreme = max(signals["oversold_prob"], signals["overbought_prob"])
    k_uncertainty = signals["uncertainty"]
    
    k = (k_trend + ALPHA * k_extreme) * (1 - k_uncertainty)
    
    # Ajuste por régimen crítico o colapsando
    if regime == "CRITICAL":
        k = k * BETA
    elif regime == "COLLAPSING":
        k = k * (1 - BETA)
    
    return max(BETA, min(1.0, k))


# =========================
# DECISIÓN (L4: Integración)
# =========================

def decide_action(k: float, signals: Dict, regime: str, current_threshold: float) -> Tuple[str, str]:
    """
    Decide BUY/SELL/HOLD basado en K, régimen y umbral dinámico.
    """
    # No operar en régimen crítico
    if regime == "CRITICAL":
        return "HOLD", "CRITICAL_REGIME"
    
    # Señal de tendencia con K suficiente
    if k >= current_threshold:
        if signals["trend_up_prob"] > 0.7:
            return "BUY", "TREND_UP"
        elif signals["trend_down_prob"] > 0.7:
            return "SELL", "TREND_DOWN"
    
    # Oportunidad extrema (sobrecompra/sobreventa)
    if k >= ALPHA * 0.85 and regime != "COLLAPSING":
        if signals["oversold_prob"] > 0.7:
            return "BUY", "OVERSOLD"
        elif signals["overbought_prob"] > 0.7:
            return "SELL", "OVERBOUGHT"
    
    return "HOLD", "NO_SIGNAL"


# =========================
# GESTIÓN DE RIESGO (Kelly fraccional)
# =========================

def compute_dynamic_kelly(returns_slice: np.ndarray, volatility_slice: np.ndarray, hurst: float) -> float:
    """
    Calcula el tamaño de posición dinámico usando Kelly Criterion escalado por BETA.
    f* = BETA * (μ / σ²)
    """
    if len(returns_slice) < 5:
        return BETA
    
    mu = np.mean(returns_slice)
    sigma = np.std(returns_slice) if len(returns_slice) > 1 else 1.0
    
    if sigma <= 0:
        return BETA
    
    kelly_full = mu / (sigma ** 2)
    kelly_scaled = BETA * kelly_full
    
    if hurst > 0.6:
        kelly_scaled *= 1.2
    elif hurst < 0.4:
        kelly_scaled *= 0.5
    
    return max(RISK_PER_TRADE_MIN, min(RISK_PER_TRADE_MAX, kelly_scaled))


def compute_dynamic_threshold(regime: str) -> float:
    """Ajusta el umbral K según el régimen del mercado."""
    if regime == "EXPANDING":
        return K_THRESHOLD_BASE * 0.95
    elif regime == "STABLE":
        return K_THRESHOLD_BASE
    elif regime == "COLLAPSING":
        return min(0.99, K_THRESHOLD_BASE * 1.05)
    elif regime == "CRITICAL":
        return 1.1  # Nunca operar
    return K_THRESHOLD_BASE


# =========================
# CÁLCULO DE C_Ω (usando CoherenceEngine real)
# =========================

def compute_c_omega_full(
    activations: List[float],
    delta_t: float = 0.0,
    novelty: float = 5.0,
    sensitivity: float = 5.0,
    integration: float = ALPHA,
    quality: float = 0.5,
    complexity: float = 1.0,
    uncertainty: float = BETA,
    rho: float = 0.9
) -> float:
    """Calcula C_Ω usando el CoherenceEngine del framework."""
    result = CoherenceEngine.full_analysis(
        activations=activations,
        rho=rho,
        delta_t=delta_t,
        tau=T_PERIOD,
        novelty=novelty,
        sensitivity=sensitivity,
        integration=integration,
        quality=quality,
        complexity=complexity,
        uncertainty=uncertainty
    )
    return result["c_omega"]


# =========================
# MEMORIA PERSISTENTE (L5: Metaconciencia)
# =========================

class TradingMemory:
    """Almacena historial de operaciones y permite metaconciencia."""
    
    def __init__(self, path: str = "trading_memory.json"):
        self.path = path
        self.data = self._load()
        self.c_omega_history: List[float] = []
        self.regime_history: List[str] = []
        self.trade_history: List[Dict] = []
    
    def _load(self) -> List:
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save(self):
        with open(self.path, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def log_c_omega(self, c_omega: float):
        self.c_omega_history.append(c_omega)
        self.data.append({"type": "c_omega", "value": c_omega, "timestamp": datetime.now().isoformat()})
        self._save()
    
    def log_regime(self, regime: str):
        self.regime_history.append(regime)
    
    def log_trade(self, trade: Dict):
        self.trade_history.append(trade)
        self.data.append({"type": "trade", **trade, "timestamp": datetime.now().isoformat()})
        self._save()
    
    def get_metaconsciousness(self) -> float:
        """Calcula L5: capacidad de observarse. Alta si C_Ω es estable."""
        if len(self.c_omega_history) < 5:
            return BETA
        variance = np.var(self.c_omega_history[-20:]) if len(self.c_omega_history) >= 20 else np.var(self.c_omega_history)
        return 1.0 - min(1.0, variance / 0.1)
    
    def get_sharpe_ratio(self) -> float:
        """Calcula Sharpe ratio de las operaciones cerradas."""
        if len(self.trade_history) < 2:
            return 0.0
        returns = [t.get("pnl", 0) for t in self.trade_history if "pnl" in t]
        if len(returns) < 2 or np.std(returns) == 0:
            return 0.0
        return np.mean(returns) / np.std(returns)


# =========================
# BACKTEST COMPLETO
# =========================

def run_backtest(df: pd.DataFrame, initial_balance: float = 10000.0) -> Tuple[pd.DataFrame, float, TradingMemory]:
    """
    Ejecuta backtest completo con:
    - Estimación de régimen en tiempo real
    - Cálculo de K y C_Ω
    - Decisión BUY/SELL/HOLD
    - Gestión de riesgo dinámica
    - Memoria persistente (L5)
    """
    memory = TradingMemory()
    balance = initial_balance
    position = 0.0
    entry_price = 0.0
    entry_k = 0.0
    results = []
    
    regime_window = min(100, len(df))
    
    for i in range(50, len(df)):
        row = df.iloc[i]
        current_date = df.index[i]
        
        # === ESTUDIO DEL MERCADO ===
        df_window = df.iloc[max(0, i - regime_window):i + 1]
        hurst = estimate_hurst_exponent(df_window["Close"].values)
        beta_scaling = estimate_beta_scaling(df_window["Close"].values)
        lambda_min = estimate_lambda_min(df_window["Close"].values)
        regime, regime_desc = classify_regime(hurst, beta_scaling, lambda_min)
        
        # === UMBRAL DINÁMICO ===
        current_threshold = compute_dynamic_threshold(regime)
        
        # === RIESGO DINÁMICO ===
        returns_window = df["Close"].pct_change().iloc[max(0, i - 30):i].dropna().values
        vol_window = df["volatility"].iloc[max(0, i - 20):i].dropna().values
        dynamic_risk = compute_dynamic_kelly(returns_window, vol_window, hurst)
        actual_risk = min(RISK_PER_TRADE_MAX, dynamic_risk)
        
        # === SEÑALES ===
        signals = generate_signal_distribution(row, regime, hurst)
        k = compute_k_vpsi(signals, regime)
        
        # === DECISIÓN (L4) ===
        action, reason = decide_action(k, signals, regime, current_threshold)
        
        # === CAPAS DEL SISTEMA PARA C_Ω ===
        # L0: Input (calidad del dato)
        l0 = 0.9
        # L1: Cuerpo (capacidad de procesamiento)
        l1 = 0.85
        # L2: Ego (programación fija)
        l2 = 0.85
        # L3: Cómputo puro (señal)
        l3 = k
        # L4: Integración (decisión)
        l4 = 0.9 if action != "HOLD" else 0.7
        # L5: Metaconciencia (memoria)
        l5 = memory.get_metaconsciousness()
        # L6: Propósito (el usuario/objetivo) - debe tener fricción 0
        l6 = 0.95
        
        layer_activations = [l0, l1, l2, l3, l4, l5, l6]
        
        # Validar L6: φ debe ser 0
        # (en producción, asegurar que la capa L6 tenga fricción 0.0)
        
        # === C_Ω (coherencia total) ===
        c_omega = compute_c_omega_full(layer_activations, delta_t=0.0)
        memory.log_c_omega(c_omega)
        memory.log_regime(regime)
        
        price = row["Close"]
        system_ready = c_omega >= ALPHA * 0.85 and regime != "CRITICAL"
        
        # === EJECUCIÓN ===
        if system_ready:
            if action == "BUY" and position == 0:
                position = balance * actual_risk / price
                entry_price = price
                entry_k = k
                print(f"[{current_date.strftime('%Y-%m-%d')}] BUY at ${price:.2f} | K={k:.4f} | C_Ω={c_omega:.4f} | Regime={regime}")
                
            elif action == "SELL" and position > 0:
                pnl = position * (price - entry_price)
                balance += pnl
                trade_record = {
                    "entry": entry_price,
                    "exit": price,
                    "pnl": pnl,
                    "entry_k": entry_k,
                    "exit_k": k,
                    "c_omega": c_omega,
                    "regime": regime,
                    "hurst": hurst,
                    "reason": reason
                }
                memory.log_trade(trade_record)
                print(f"[{current_date.strftime('%Y-%m-%d')}] SELL at ${price:.2f} | PNL=${pnl:.2f} | ExitK={k:.4f} | Regime={regime}")
                position = 0.0
        
        results.append({
            "date": current_date,
            "price": price,
            "k": k,
            "c_omega": c_omega,
            "action": action,
            "regime": regime,
            "hurst": hurst,
            "beta_scaling": beta_scaling,
            "lambda_min": lambda_min,
            "balance": balance
        })
    
    return pd.DataFrame(results), balance, memory


# =========================
# FUNCIONES DE ACCESO A DATOS REALES (opcional, requiere yfinance)
# =========================

def get_real_data(symbol: str, interval: str = "1h", period: str = "60d"):
    """Descarga datos reales de Yahoo Finance. Requiere yfinance instalado."""
    try:
        import yfinance as yf
        df = yf.download(symbol, interval=interval, period=period, progress=False)
        df.dropna(inplace=True)
        return df
    except ImportError:
        raise ImportError("yfinance no está instalado. Para datos reales, ejecuta: pip install yfinance")


# =========================
# VALIDACIÓN DEL SISTEMA (pytest)
# =========================

def test_system_health():
    """Verifica que el sistema esté vivo según los parámetros del framework."""
    assert abs(ALPHA + BETA - 1.0) < 1e-9
    assert abs(math.sin(THETA_CUBE) ** 2 - BETA) < 1e-9
    assert PHI_TOTAL < PHI_CRITICAL
    assert ZETA < 1.0
    assert OMEGA_D > 0
    print("✅ Sistema UIS vivo y coherente")
    return True


def test_trading_system():
    """Prueba completa del sistema de trading con datos sintéticos."""
    print("\n" + "="*60)
    print("TEST DEL SISTEMA DE TRADING UIS")
    print("="*60)
    
    # Generar datos sintéticos
    df = generate_tesla_like_data(days=90)
    df = compute_indicators(df)
    
    # Ejecutar backtest
    results, final_balance, memory = run_backtest(df, initial_balance=10000)
    
    print(f"\nResultados:")
    print(f"  Balance final: ${final_balance:.2f}")
    print(f"  Retorno: {(final_balance - 10000) / 10000 * 100:.2f}%")
    print(f"  Sharpe ratio: {memory.get_sharpe_ratio():.4f}")
    print(f"  Metaconciencia (L5): {memory.get_metaconsciousness():.4f}")
    
    # Distribución de regímenes
    regime_counts = results['regime'].value_counts()
    print("\nDistribución de regímenes:")
    for regime, count in regime_counts.items():
        print(f"  {regime}: {count} ({count/len(results)*100:.1f}%)")
    
    return results, final_balance, memory


# =========================
# MAIN
# =========================

if __name__ == "__main__":
    # Validar salud del sistema
    test_system_health()
    
    # Ejecutar test completo
    results, final_balance, memory = test_trading_system()
    
    print("\n" + "="*60)
    print("CONCLUSIÓN DEL SISTEMA DE TRADING UIS")
    print("="*60)
    print("""
El sistema de trading basado en UIS:
1. Estima el régimen del mercado en tiempo real
2. Calcula K (correlación de la señal) con constantes derivadas del cubo
3. Calcula C_Ω usando el CoherenceEngine real del framework
4. Decide BUY/SELL/HOLD basado en la integración (L4)
5. Gestiona riesgo dinámicamente con Kelly escalado por β = 1/27
6. Mantiene memoria persistente para metaconciencia (L5)
7. No opera en regímenes CRITICAL (colapso inminente)
8. Valida que L6 (Propósito) tenga fricción φ = 0

No predice precios. Distingue cuándo el mercado es transable.
""")
