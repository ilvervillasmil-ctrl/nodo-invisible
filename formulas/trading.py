# formulas/trading.py

import pandas as pd
import numpy as np
from dataclasses import dataclass
import json
import os
import math
from scipy import stats
from scipy.signal import welch

# =========================
# IMPORT FRAMEWORK UIS
# =========================

from formulas.constants import (
    ALPHA, BETA, PHI, KAPPA, S_REF, R_FIN,
    THETA_CUBE, GOLDEN_ANG, EPSILON_OBSERVER,
    OMEGA_D, ZETA, PHI_TOTAL, LAMBDA_UCF
)
from formulas.neghentropy import NegentropyCalculator
from formulas.interaction import ExternalInteraction
from formulas.coherence import CoherenceEngine
from formulas.dynamics import regime, is_alive, oscillator_solution

# =========================
# CONFIG (derivada del framework)
# =========================

SYMBOL = "AAPL"
INTERVAL = "1h"
PERIOD = "60d"

# K_THRESHOLD derivado del teorema de coherencia:
K_THRESHOLD = ALPHA - EPSILON_OBSERVER  # 0.96296 - 0.02716 = 0.9358

# Riesgo por trade: Fracción de Kelly usando BETA como factor de escala
RISK_PER_TRADE = BETA  # 1/27 = 3.7%

MEMORY_FILE = "trading_memory.json"


# =========================
# ESTUDIO DEL MERCADO (Régimen de Coherencia)
# =========================

def estimate_market_regime(df, window=100):
    """Estima el régimen actual del mercado usando las métricas del UCF."""
    closes = df["Close"].values[-window:]
    returns = np.diff(np.log(closes))
    
    n = len(returns)
    if n > 10:
        scales = np.unique(np.logspace(0, np.log10(n//4), 10).astype(int))
        scales = scales[scales >= 4]
        fluct = []
        for scale in scales:
            n_seg = n // scale
            rms = 0
            for i in range(n_seg):
                seg = returns[i*scale:(i+1)*scale]
                if len(seg) > 1:
                    seg_detrend = seg - np.polyval(np.polyfit(range(len(seg)), seg, 1), range(len(seg)))
                    rms += np.sqrt(np.mean(seg_detrend**2))
            fluct.append(rms / max(1, n_seg))
        
        if len(fluct) > 1 and len(scales) == len(fluct):
            log_scales = np.log(scales)
            log_fluct = np.log(fluct)
            slope, _, _, _, _ = stats.linregress(log_scales, log_fluct)
            hurst = slope
        else:
            hurst = 0.5
    else:
        hurst = 0.5
    
    if len(returns) > 10:
        corr_matrix = np.corrcoef(returns[-min(20, len(returns)):])
        if corr_matrix.shape[0] > 1:
            eigenvals = np.linalg.eigvalsh(corr_matrix)
            lambda_min = min(eigenvals)
        else:
            lambda_min = 1.0
    else:
        lambda_min = 1.0
    
    if len(returns) > 20:
        cum_returns = np.cumsum(returns - np.mean(returns))
        scales_test = np.arange(5, min(30, len(cum_returns)//4))
        if len(scales_test) > 2:
            fluct_scale = []
            for s in scales_test:
                fluct_scale.append(np.std(cum_returns[::s]) if len(cum_returns[::s]) > 1 else 0)
            fluct_scale = [f for f in fluct_scale if f > 0]
            if len(fluct_scale) > 1 and len(scales_test) == len(fluct_scale):
                log_s = np.log(scales_test[:len(fluct_scale)])
                log_f = np.log(fluct_scale)
                beta_scaling, _, _, _, _ = stats.linregress(log_s, log_f)
            else:
                beta_scaling = 0.5
        else:
            beta_scaling = 0.5
    else:
        beta_scaling = 0.5
    
    if beta_scaling > 0.4 and lambda_min < 0.1:
        regime = "CRITICAL"
    elif lambda_min < 0.2:
        regime = "COLLAPSING"
    elif hurst > 0.55:
        regime = "EXPANDING"
    else:
        regime = "STABLE"
    
    return regime, beta_scaling, lambda_min, hurst


def compute_dynamic_threshold(regime, base_threshold=K_THRESHOLD):
    """Ajusta el umbral K según el régimen del mercado."""
    if regime == "EXPANDING":
        return base_threshold * 0.95
    elif regime == "STABLE":
        return base_threshold
    elif regime == "COLLAPSING":
        return min(0.99, base_threshold * 1.05)
    elif regime == "CRITICAL":
        return 1.1
    else:
        return base_threshold


def compute_dynamic_kelly(returns_slice, volatility_slice, hurst):
    """Calcula el tamaño de posición dinámico usando Kelly Criterion escalado por BETA."""
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
    
    return max(0.01, min(BETA * 2, kelly_scaled))


# =========================
# INDICATORS (evidence)
# =========================

def compute_indicators(df):
    """Calcula indicadores técnicos derivados de constantes del framework."""
    df["SMA20"] = df["Close"].rolling(20).mean()
    df["SMA50"] = df["Close"].rolling(50).mean()
    df["RSI"] = compute_rsi(df["Close"], period=14)
    df["volatility"] = df["Close"].pct_change().rolling(20).std()
    
    df["BB_middle"] = df["Close"].rolling(20).mean()
    bb_std = df["Close"].rolling(20).std()
    df["BB_upper"] = df["BB_middle"] + BETA * bb_std
    df["BB_lower"] = df["BB_middle"] - BETA * bb_std
    
    df["momentum_phi"] = df["Close"].pct_change(periods=int(PHI * 10))
    
    return df


def compute_rsi(series, period=14):
    """Calcula el RSI."""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / (loss + 1e-6)
    return 100 - (100 / (1 + rs))


# =========================
# SEÑALES
# =========================

def generate_signal_distribution(row, regime, hurst):
    """Genera probabilidades ajustadas por el régimen de mercado."""
    signals = {}
    
    sma_diff = (row["SMA20"] - row["SMA50"]) / max(row["SMA50"], 1)
    prob_trend_up = 1 / (1 + math.exp(-sma_diff * 10))
    signals["trend_up_prob"] = prob_trend_up
    signals["trend_down_prob"] = 1 - prob_trend_up
    
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
    
    signals["uncertainty"] = min(1.0, row["volatility"] * 10)
    
    if hurst > 0.6:
        signals["trend_up_prob"] = prob_trend_up + (1 - prob_trend_up) * (hurst - 0.6) * 2
        signals["trend_up_prob"] = min(1.0, signals["trend_up_prob"])
        signals["trend_down_prob"] = 1 - signals["trend_up_prob"]
    elif hurst < 0.4:
        signals["uncertainty"] = min(1.0, signals["uncertainty"] * 1.5)
    
    if regime == "CRITICAL":
        signals["uncertainty"] = 1.0
    elif regime == "COLLAPSING":
        signals["uncertainty"] = min(1.0, signals["uncertainty"] * 1.2)
    elif regime == "EXPANDING":
        signals["uncertainty"] *= 0.8
    
    return signals


def compute_k_vpsi(signals, regime):
    """K = factor de correlación con el dominio observable."""
    k_trend = max(signals["trend_up_prob"], signals["trend_down_prob"])
    k_extreme = max(signals["oversold_prob"], signals["overbought_prob"])
    k_uncertainty = signals["uncertainty"]
    
    k = (k_trend + ALPHA * k_extreme) * (1 - k_uncertainty)
    
    if regime == "CRITICAL":
        k = k * BETA
    elif regime == "COLLAPSING":
        k = k * (1 - BETA)
    
    return max(BETA, min(1.0, k))


def decide_action(k, signals, regime, current_threshold):
    """Decisión basada en K, régimen y umbral dinámico."""
    if regime == "CRITICAL":
        return "HOLD", "CRITICAL_REGIME"
    
    if k >= current_threshold:
        if signals["trend_up_prob"] > 0.7:
            return "BUY", "TREND_UP"
        elif signals["trend_down_prob"] > 0.7:
            return "SELL", "TREND_DOWN"
    
    if k >= ALPHA * 0.85 and regime != "COLLAPSING":
        if signals["oversold_prob"] > 0.7:
            return "BUY", "OVERSOLD"
        elif signals["overbought_prob"] > 0.7:
            return "SELL", "OVERBOUGHT"
    
    return "HOLD", "NO_SIGNAL"


def compute_c_omega_for_row(layer_activations, delta_t=0.0):
    """Calcula C_Ω usando el CoherenceEngine del framework."""
    result = CoherenceEngine.full_analysis(
        activations=layer_activations,
        rho=0.9,
        delta_t=delta_t,
        tau=60.0,
        novelty=5.0,
        sensitivity=5.0,
        integration=ALPHA,
        quality=0.5,
        complexity=1.0,
        uncertainty=BETA
    )
    return result["c_omega"]


# =========================
# MEMORY
# =========================

class Memory:
    def __init__(self, path=MEMORY_FILE):
        self.path = path
        self.data = self.load()
        self.c_omega_history = []
        self.regime_history = []

    def load(self):
        if os.path.exists(self.path):
            return json.load(open(self.path))
        return []

    def save(self):
        json.dump(self.data, open(self.path, "w"), indent=2)

    def log(self, item):
        self.data.append(item)
        self.save()

    def log_c_omega(self, c_omega):
        self.c_omega_history.append(c_omega)

    def log_regime(self, regime):
        self.regime_history.append(regime)

    def get_metaconsciousness(self):
        if len(self.c_omega_history) < 5:
            return BETA
        variance = np.var(self.c_omega_history[-20:]) if len(self.c_omega_history) >= 20 else np.var(self.c_omega_history)
        return 1.0 - min(1.0, variance / (ALPHA * 0.1))


# =========================
# BACKTEST (sin yfinance aquí)
# =========================

def run_backtest(df):
    """Ejecuta backtest con un DataFrame que ya contiene los datos."""
    memory = Memory()
    
    balance = 10000
    position = 0
    entry_price = 0
    entry_k = 0
    
    results = []
    regime_window = min(100, len(df))
    
    for i in range(50, len(df)):
        row = df.iloc[i]
        
        df_window = df.iloc[max(0, i-regime_window):i+1]
        regime, beta_scaling, lambda_min, hurst = estimate_market_regime(df_window)
        
        current_threshold = compute_dynamic_threshold(regime)
        
        returns_window = df["Close"].pct_change().iloc[max(0, i-30):i].dropna()
        vol_window = df["volatility"].iloc[max(0, i-20):i].dropna()
        dynamic_risk = compute_dynamic_kelly(returns_window.values, vol_window.values, hurst)
        actual_risk = min(RISK_PER_TRADE, dynamic_risk)
        
        signals = generate_signal_distribution(row, regime, hurst)
        k = compute_k_vpsi(signals, regime)
        action, reason = decide_action(k, signals, regime, current_threshold)
        
        layer_activations = [0.9, 0.85, 0.85, k, 0.9 if action != "HOLD" else 0.7, 
                             memory.get_metaconsciousness(), 0.95]
        
        c_omega = compute_c_omega_for_row(layer_activations)
        memory.log_c_omega(c_omega)
        memory.log_regime(regime)
        
        price = row["Close"]
        system_ready = c_omega >= ALPHA * 0.85 and regime != "CRITICAL"
        
        if system_ready:
            if action == "BUY" and position == 0:
                position = balance * actual_risk / price
                entry_price = price
                entry_k = k
            elif action == "SELL" and position > 0:
                pnl = position * (price - entry_price)
                balance += pnl
                memory.log({"entry": entry_price, "exit": price, "pnl": pnl, "entry_k": entry_k, "exit_k": k})
                position = 0
        
        results.append({"price": price, "k": k, "c_omega": c_omega, "action": action, 
                        "regime": regime, "hurst": hurst, "balance": balance})
    
    return pd.DataFrame(results), balance


# =========================
# DATA LAYER (solo se importa yfinance si se ejecuta como script)
# =========================

def get_data(symbol, interval=INTERVAL, period=PERIOD):
    """Descarga datos de Yahoo Finance. Esta función solo funciona con yfinance instalado."""
    import yfinance as yf
    df = yf.download(symbol, interval=interval, period=period, progress=False)
    df.dropna(inplace=True)
    return df


# =========================
# MAIN (solo se ejecuta si es script principal)
# =========================

if __name__ == "__main__":
    print("=" * 70)
    print("TRADING SYSTEM WITH UIS FRAMEWORK - FULLY INTEGRATED")
    print("=" * 70)
    print(f"Constants from UIS (v3.3):")
    print(f"  ALPHA = {ALPHA:.10f} (26/27)")
    print(f"  BETA  = {BETA:.10f}  (1/27)")
    print(f"  PHI   = {PHI:.10f}")
    print(f"  EPSILON_OBSERVER = {EPSILON_OBSERVER:.10f}")
    
    print("\nDownloading data...")
    df = get_data(SYMBOL)
    print(f"Data shape: {df.shape}")
    
    print("Computing indicators...")
    df = compute_indicators(df)
    
    print("Running backtest...")
    results, final_balance = run_backtest(df)
    
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Symbol: {SYMBOL}")
    print(f"Initial Balance: $10,000.00")
    print(f"Final Balance: ${final_balance:.2f}")
    print(f"Total Return: {((final_balance - 10000) / 10000 * 100):.2f}%")
