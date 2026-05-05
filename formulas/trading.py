import yfinance as yf
import pandas as pd
import numpy as np
from dataclasses import dataclass
import json
import os

# =========================
# CONFIG
# =========================

SYMBOL = "AAPL"
INTERVAL = "1h"
PERIOD = "60d"

K_THRESHOLD = 0.75   # threshold para operar
RISK_PER_TRADE = 0.01

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
    df["SMA20"] = df["Close"].rolling(20).mean()
    df["SMA50"] = df["Close"].rolling(50).mean()

    df["RSI"] = compute_rsi(df["Close"], 14)

    return df

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()

    rs = gain / (loss + 1e-6)
    return 100 - (100 / (1 + rs))

# =========================
# SIGNAL GENERATION (LLM analog)
# =========================

def generate_signal(row):
    signals = []

    if row["SMA20"] > row["SMA50"]:
        signals.append("trend_up")
    else:
        signals.append("trend_down")

    if row["RSI"] < 30:
        signals.append("oversold")
    elif row["RSI"] > 70:
        signals.append("overbought")

    return signals

# =========================
# VERIFIER (K estimator)
# =========================

def compute_k(signals):
    score = 0

    if "trend_up" in signals:
        score += 0.4
    if "oversold" in signals:
        score += 0.4
    if "trend_down" in signals and "overbought" in signals:
        score -= 0.5

    return max(min(score, 1.0), 0.0)

# =========================
# POLICY ENGINE
# =========================

def decide_action(k, signals):
    if k >= K_THRESHOLD and "trend_up" in signals:
        return "BUY"
    elif k >= K_THRESHOLD and "trend_down" in signals:
        return "SELL"
    else:
        return "HOLD"

# =========================
# MEMORY (feedback loop)
# =========================

class Memory:
    def __init__(self, path=MEMORY_FILE):
        self.path = path
        self.data = self.load()

    def load(self):
        if os.path.exists(self.path):
            return json.load(open(self.path))
        return []

    def save(self):
        json.dump(self.data, open(self.path, "w"), indent=2)

    def log(self, item):
        self.data.append(item)
        self.save()

# =========================
# BACKTEST / EXECUTION LOOP
# =========================

def run_backtest(df):

    memory = Memory()

    balance = 10000
    position = 0
    entry_price = 0

    results = []

    for i in range(50, len(df)):
        row = df.iloc[i]

        signals = generate_signal(row)
        k = compute_k(signals)
        action = decide_action(k, signals)

        price = row["Close"]

        # ===== EXECUTION =====
        if action == "BUY" and position == 0:
            position = balance * RISK_PER_TRADE / price
            entry_price = price

        elif action == "SELL" and position > 0:
            pnl = position * (price - entry_price)
            balance += pnl

            memory.log({
                "entry": entry_price,
                "exit": price,
                "pnl": pnl,
                "k": k,
                "signals": signals
            })

            position = 0

        results.append({
            "price": price,
            "k": k,
            "action": action,
            "balance": balance
        })

    return pd.DataFrame(results), balance

# =========================
# MAIN
# =========================

if __name__ == "__main__":

    df = get_data(SYMBOL)
    df = compute_indicators(df)

    results, final_balance = run_backtest(df)

    print("\nFinal Balance:", final_balance)
    print(results.tail())
