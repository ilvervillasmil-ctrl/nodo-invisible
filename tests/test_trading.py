# tests/test_trading.py
import pytest
import numpy as np
import pandas as pd
import math
from datetime import datetime, timedelta

# Esto ahora funciona porque trading.py ya no importa yfinance al inicio
import formulas.trading as trading

from formulas.constants import ALPHA, BETA, PHI, EPSILON_OBSERVER, OMEGA_D, PHI_TOTAL
from formulas.dynamics import oscillator_solution, regime, is_alive


def generate_synthetic_price_data(days=100, start_price=100, volatility=0.02, trend=0.0001):
    """Genera datos de precios sintéticos usando oscillator_solution."""
    t = np.linspace(0, days, days)
    oscillator_component = np.array([oscillator_solution(ti, A=volatility * 10, delta=0.0) for ti in t])
    trend_component = trend * t
    noise = np.random.normal(0, volatility, days)
    prices = start_price * (1 + trend_component + oscillator_component / 100 + noise)
    prices = np.maximum(prices, start_price * 0.5)
    
    start_date = datetime.now() - timedelta(days=days)
    dates = [start_date + timedelta(days=i) for i in range(days)]
    
    df = pd.DataFrame({
        'Open': prices * 0.999,
        'High': prices * 1.002,
        'Low': prices * 0.998,
        'Close': prices,
        'Volume': np.random.randint(1000000, 10000000, days)
    }, index=dates)
    return df


def test_trading_module_import():
    """Verifica que el módulo de trading se puede importar"""
    assert hasattr(trading, 'estimate_market_regime')
    assert hasattr(trading, 'compute_k_vpsi')
    assert hasattr(trading, 'decide_action')
    assert hasattr(trading, 'run_backtest')


def test_estimate_market_regime():
    """Verifica la estimación del régimen de mercado"""
    df = generate_synthetic_price_data(days=100)
    regime, beta_scaling, lambda_min, hurst = trading.estimate_market_regime(df, window=50)
    
    assert regime in ["EXPANDING", "STABLE", "COLLAPSING", "CRITICAL"]
    assert 0.0 <= beta_scaling <= 1.0
    assert 0.0 <= lambda_min <= 1.0
    assert 0.0 <= hurst <= 1.0


def test_compute_k_vpsi():
    """Verifica el cálculo de K"""
    df = generate_synthetic_price_data(days=50)
    df = trading.compute_indicators(df)
    
    row = df.iloc[-1]
    regime = "EXPANDING"
    hurst = 0.65
    
    signals = trading.generate_signal_distribution(row, regime, hurst)
    k = trading.compute_k_vpsi(signals, regime)
    
    assert trading.BETA <= k <= 1.0


def test_decide_action():
    """Verifica la decisión de trading"""
    k = trading.K_THRESHOLD + 0.05
    signals = {"trend_up_prob": 0.85, "trend_down_prob": 0.15, 
               "oversold_prob": 0.0, "overbought_prob": 0.0, "uncertainty": 0.2}
    current_threshold = trading.K_THRESHOLD
    
    action, reason = trading.decide_action(k, signals, "EXPANDING", current_threshold)
    assert action == "BUY"
    
    action, reason = trading.decide_action(k, signals, "CRITICAL", current_threshold)
    assert action == "HOLD"
    
    action, reason = trading.decide_action(0.5, signals, "STABLE", current_threshold)
    assert action == "HOLD"


def test_system_health():
    """Verifica que el sistema esté vivo según los parámetros del framework"""
    from formulas.constants import ALPHA, BETA, THETA_CUBE, ZETA, OMEGA_D, PHI_CRITICAL
    
    assert abs(ALPHA + BETA - 1.0) < 1e-9
    assert abs(math.sin(THETA_CUBE) ** 2 - BETA) < 1e-9
    assert PHI_TOTAL < PHI_CRITICAL
    assert ZETA < 1.0
    assert OMEGA_D > 0


def test_compute_indicators_synthetic():
    """Verifica el cálculo de indicadores con datos sintéticos"""
    df = generate_synthetic_price_data(days=50)
    df = trading.compute_indicators(df)
    
    assert 'SMA20' in df.columns
    assert 'SMA50' in df.columns
    assert 'RSI' in df.columns
    assert 'volatility' in df.columns
    assert not df['SMA20'].isna().all()
    assert not df['RSI'].isna().all()


def test_run_backtest_synthetic():
    """Ejecuta un backtest completo con datos sintéticos"""
    df = generate_synthetic_price_data(days=100)
    df = trading.compute_indicators(df)
    
    results, final_balance = trading.run_backtest(df)
    
    assert isinstance(results, pd.DataFrame)
    assert len(results) > 0
    assert final_balance > 0
    assert 'regime' in results.columns
    assert 'k' in results.columns
