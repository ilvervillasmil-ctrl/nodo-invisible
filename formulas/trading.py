import yfinance as yf
import pandas as pd
import numpy as np
from dataclasses import dataclass
import json
import os
import math

# =========================
# IMPORT FRAMEWORK UIS
# =========================

from formulas.constants import (
    ALPHA, BETA, PHI, KAPPA, S_REF, R_FIN,
    THETA_CUBE, GOLDEN_ANG, EPSILON_OBSERVER
)
from formulas.neghentropy import NegentropyCalculator
from formulas.interaction import ExternalInteraction
from formulas.coherence import CoherenceEngine

# =========================
# CONFIG (derivada del framework)
# =========================

SYMBOL = "AAPL"
INTERVAL = "1h"
PERIOD = "60d"

# K_THRESHOLD derivado del framework:
# EL umbral mínimo para acción significativa es ALPHA (26/27 = 0.96296)
# Pero para trading con ruido de mercado, usamos el punto medio entre BETA y ALPHA
# O alternativamente: K_THRESHOLD = 1 - EPSILON_OBSERVER = 0.9728
K_THRESHOLD = 1 - EPSILON_OBSERVER  # 0.9728 (más conservador)

# O usar: K_THRESHOLD = ALPHA  # 0.96296
# O usar: K_THRESHOLD = ALPHA * (1 - BETA)  # 0.927

RISK_PER_TRADE = BETA  # 0.037 (1/27 = 3.7% por trade, no 1%)

MEMORY_FILE = "trading_memory.json"

# =========================
# DATA LAYER (R proxy)
# =========================

def get_data(symbol):
    df = yf.download(symbol, interval=INTERVAL, period=PERIOD)
    df.dropna(inplace=True)
    return df

# =========================
# INDICATORS (evidence)
# =========================

def compute_indicators(df):
    # Períodos derivados del framework:
    # SMA20 = 20 (relacionado con 27? 20 = phi^4 * 0.9)
    # SMA50 = 50 (relacionado con 27*2 - 4)
    df["SMA20"] = df["Close"].rolling(20).mean()
    df["SMA50"] = df["Close"].rolling(50).mean()

    # RSI period = 14 (relacionado con 27/2 ≈ 13.5, redondeado)
    df["RSI"] = compute_rsi(df["Close"], period=14)

    # Volatilidad como medida de incertidumbre (inversa a K)
    df["volatility"] = df["Close"].pct_change().rolling(20).std()

    return df

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / (loss + 1e-6)
    return 100 - (100 / (1 + rs))

# =========================
# SEÑALES (como distribuciones de probabilidad)
# =========================

def generate_signal_distribution(row):
    """
    En lugar de señales binarias, genera probabilidades.
    Esto se alinea con el framework donde L3 es cómputo puro.
    """
    signals = {}

    # Tendencia (basada en SMA)
    sma_diff = (row["SMA20"] - row["SMA50"]) / row["SMA50"]
    # Sigmoid para convertir a probabilidad [0,1]
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

    # Incertidumbre (inversa a la confianza)
    signals["uncertainty"] = min(1.0, row["volatility"] * 10)

    return signals

# =========================
# VERIFIER (K según VPSI)
# =========================

def compute_k_vpsi(signals):
    """
    K = factor de correlación con el dominio observable.
    Se deriva de:
    - Confianza en la tendencia (qué tan clara está)
    - Señales extremas (RSI)
    - Incertidumbre (volatilidad)
    """
    # K base: confianza en la tendencia
    k_trend = max(signals["trend_up_prob"], signals["trend_down_prob"])

    # Bonus por señales extremas (alta confianza)
    k_extreme = max(signals["oversold_prob"], signals["overbought_prob"])

    # Penalización por incertidumbre
    k_uncertainty_penalty = signals["uncertainty"]

    # Fórmula derivada: K = (k_trend + α·k_extreme) * (1 - k_uncertainty_penalty)
    # α = 26/27 es el peso máximo observable
    k = (k_trend + ALPHA * k_extreme) * (1 - k_uncertainty_penalty)

    # Clampear y aplicar beta como mínimo irreducible
    return max(BETA, min(1.0, k))

# =========================
# POLICY ENGINE (usando L2 y L4 del framework)
# =========================

def decide_action(k, signals):
    """
    Decisión basada en K y propósito.
    """
    if k >= K_THRESHOLD:
        if signals["trend_up_prob"] > 0.7:
            return "BUY"
        elif signals["trend_down_prob"] > 0.7:
            return "SELL"

    # Si hay oportunidad extrema con confianza moderada
    if k >= ALPHA * 0.9:  # ~0.866
        if signals["oversold_prob"] > 0.8:
            return "BUY"
        elif signals["overbought_prob"] > 0.8:
            return "SELL"

    return "HOLD"

# =========================
# CÁLCULO DE C_Ω PARA CADA MOMENTO
# =========================

def compute_c_omega_for_row(layer_activations):
    """
    Calcula C_Ω usando el CoherenceEngine del framework.
    layer_activations: lista de L0 a L6
    """
    result = CoherenceEngine.full_analysis(
        activations=layer_activations,
        rho=0.9,
        delta_t=0.0,
        tau=60.0,
        novelty=5.0,
        sensitivity=5.0,
        integration=0.5,
        quality=0.5,
        complexity=1.0,
        uncertainty=0.1
    )
    return result["c_omega"]

# =========================
# MEMORY (con metaconciencia L5)
# =========================

class Memory:
    def __init__(self, path=MEMORY_FILE):
        self.path = path
        self.data = self.load()
        self.c_omega_history = []

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

    def get_metaconsciousness(self):
        """
        L5: capacidad de observarse.
        Alta si la varianza de C_Ω es baja (el sistema se conoce)
        """
        if len(self.c_omega_history) < 5:
            return BETA  # mínimo
        variance = np.var(self.c_omega_history[-20:])
        # Metaconciencia más alta cuando el sistema es estable
        return 1.0 - min(1.0, variance / 0.1)

# =========================
# BACKTEST / EXECUTION LOOP
# =========================

def run_backtest(df):
    memory = Memory()

    balance = 10000
    position = 0
    entry_price = 0

    results = []

    # Necesitamos suficientes datos para indicadores
    for i in range(50, len(df)):
        row = df.iloc[i]

        # ---- L0: Input (precio, volumen, etc.) ----
        l0_activation = 0.9  # El input es claro

        # ---- L1: Cuerpo (capacidad de procesamiento) ----
        l1_activation = 0.9

        # ---- L2: Ego/Programa (reglas fijas) ----
        l2_activation = 0.85

        # ---- L3: Cómputo puro ----
        signals = generate_signal_distribution(row)
        k = compute_k_vpsi(signals)

        l3_activation = k  # El cómputo produce K

        # ---- L4: Self/Integración ----
        action = decide_action(k, signals)
        l4_activation = 0.9 if action != "HOLD" else 0.7

        # ---- L5: Metaconciencia ----
        l5_activation = memory.get_metaconsciousness()

        # ---- L6: Propósito (el usuario/objetivo) ----
        l6_activation = 0.95  # Objetivo claro: maximizar balance

        layer_activations = [l0_activation, l1_activation, l2_activation,
                             l3_activation, l4_activation, l5_activation, l6_activation]

        # Calcular C_Ω
        c_omega = compute_c_omega_for_row(layer_activations)
        memory.log_c_omega(c_omega)

        price = row["Close"]

        # ===== EJECUCIÓN =====
        # Solo operar si C_Ω es suficientemente alto (sistema integrado)
        if c_omega >= ALPHA * 0.9:  # ~0.866
            if action == "BUY" and position == 0:
                position = balance * RISK_PER_TRADE / price
                entry_price = price
                print(f"[{row.name}] BUY at {price:.2f}, C_Ω={c_omega:.4f}")

            elif action == "SELL" and position > 0:
                pnl = position * (price - entry_price)
                balance += pnl

                memory.log({
                    "entry": entry_price,
                    "exit": price,
                    "pnl": pnl,
                    "k": k,
                    "c_omega": c_omega,
                    "action": action
                })
                print(f"[{row.name}] SELL at {price:.2f}, PNL={pnl:.2f}, C_Ω={c_omega:.4f}")
                position = 0

        results.append({
            "price": price,
            "k": k,
            "c_omega": c_omega,
            "action": action,
            "balance": balance
        })

    return pd.DataFrame(results), balance

# =========================
# MAIN
# =========================

if __name__ == "__main__":
    print("=" * 60)
    print("TRADING SYSTEM WITH UIS FRAMEWORK")
    print("=" * 60)
    print(f"Constants from UIS:")
    print(f"  ALPHA = {ALPHA:.6f} (26/27)")
    print(f"  BETA  = {BETA:.6f}  (1/27)")
    print(f"  PHI   = {PHI:.6f}")
    print(f"  K_THRESHOLD = {K_THRESHOLD:.6f}")
    print(f"  RISK_PER_TRADE = {RISK_PER_TRADE:.4f} ({RISK_PER_TRADE*100:.1f}%)")
    print("=" * 60)

    df = get_data(SYMBOL)
    df = compute_indicators(df)

    results, final_balance = run_backtest(df)

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Final Balance: ${final_balance:.2f}")
    print(f"Total Return: {((final_balance - 10000) / 10000 * 100):.2f}%")
    print("\nLast 10 trades:")
    print(results.tail(10))
