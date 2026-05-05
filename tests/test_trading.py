"""
Test del módulo de trading usando datos sintéticos generados por el framework.
No requiere yfinance. Valida la lógica del sistema de trading.
"""

import pytest
import numpy as np
import pandas as pd
import math
from datetime import datetime, timedelta

# Importar el módulo de trading
import formulas.trading as trading

# Importar constantes y funciones del framework
from formulas.constants import ALPHA, BETA, PHI, EPSILON_OBSERVER, OMEGA_D, PHI_TOTAL
from formulas.dynamics import oscillator_solution, regime, is_alive


# =========================
# GENERACIÓN DE DATOS SINTÉTICOS (reemplaza a yfinance)
# =========================

def generate_synthetic_price_data(days=100, start_price=100, volatility=0.02, trend=0.0001):
    """
    Genera datos de precios sintéticos usando la ecuación del oscilador del framework.
    Esto permite testear la lógica sin depender de yfinance.
    """
    t = np.linspace(0, days, days)
    
    # Usar oscillator_solution para generar movimiento realista
    oscillator_component = np.array([oscillator_solution(ti, A=volatility * 10, delta=0.0) for ti in t])
    
    trend_component = trend * t
    noise = np.random.normal(0, volatility, days)
    prices = start_price * (1 + trend_component + oscillator_component / 100 + noise)
    prices = np.maximum(prices, start_price * 0.5)  # Evitar precios negativos
    
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


def generate_trending_market(days=100):
    """Genera un mercado con tendencia alcista fuerte"""
    return generate_synthetic_price_data(days=days, start_price=100, volatility=0.01, trend=0.002)


def generate_critical_market(days=100):
    """Genera un mercado en régimen crítico (alta volatilidad, sin tendencia)"""
    return generate_synthetic_price_data(days=days, start_price=100, volatility=0.05, trend=0.0)


# =========================
# TESTS
# =========================

def test_trading_module_import():
    """Verifica que el módulo de trading se puede importar"""
    assert hasattr(trading, 'estimate_market_regime')
    assert hasattr(trading, 'compute_k_vpsi')
    assert hasattr(trading, 'decide_action')
    assert hasattr(trading, 'run_backtest')


def test_estimate_market_regime():
    """Verifica la estimación del régimen de mercado"""
    # Generar datos sintéticos de mercado alcista
    df = generate_trending_market(days=100)
    
    regime, beta_scaling, lambda_min, hurst = trading.estimate_market_regime(df, window=50)
    
    # Verificar que el régimen es válido
    assert regime in ["EXPANDING", "STABLE", "COLLAPSING", "CRITICAL"]
    assert 0.0 <= beta_scaling <= 1.0
    assert 0.0 <= lambda_min <= 1.0
    assert 0.0 <= hurst <= 1.0


def test_compute_k_vpsi():
    """Verifica el cálculo de K (factor de correlación)"""
    # Crear un mercado sintético con tendencia clara
    df = generate_trending_market(days=50)
    
    # Usar los datos de la última fila
    row = df.iloc[-1]
    regime = "EXPANDING"
    hurst = 0.65
    
    signals = trading.generate_signal_distribution(row, regime, hurst)
    k = trading.compute_k_vpsi(signals, regime)
    
    # K debe estar entre BETA y 1.0
    assert BETA <= k <= 1.0
    
    # En mercado expansivo, K debería ser relativamente alto
    # (pero no podemos asumir >0.5 porque depende de los datos)


def test_decide_action():
    """Verifica la decisión de trading"""
    # Caso 1: K alto, tendencia alcista, régimen expansivo → BUY
    k = trading.K_THRESHOLD + 0.05
    signals = {"trend_up_prob": 0.85, "trend_down_prob": 0.15, 
               "oversold_prob": 0.0, "overbought_prob": 0.0, "uncertainty": 0.2}
    regime = "EXPANDING"
    current_threshold = trading.K_THRESHOLD
    
    action, reason = trading.decide_action(k, signals, regime, current_threshold)
    assert action == "BUY"
    
    # Caso 2: Régimen crítico → HOLD
    regime = "CRITICAL"
    action, reason = trading.decide_action(k, signals, regime, current_threshold)
    assert action == "HOLD"
    
    # Caso 3: K bajo → HOLD
    k = 0.5
    regime = "STABLE"
    action, reason = trading.decide_action(k, signals, regime, current_threshold)
    assert action == "HOLD"


def test_compute_dynamic_kelly():
    """Verifica el cálculo del tamaño de posición dinámico"""
    returns = np.array([0.01, -0.005, 0.02, -0.01, 0.015])
    volatility = np.array([0.02, 0.018, 0.022, 0.019, 0.021])
    hurst = 0.55
    
    kelly = trading.compute_dynamic_kelly(returns, volatility, hurst)
    
    # Kelly debe ser un número positivo y razonable
    assert kelly > 0.0
    assert kelly <= trading.BETA * 2  # Máximo BETA*2
    
    # Kelly por defecto debería ser BETA
    kelly_default = trading.compute_dynamic_kelly(np.array([1]), np.array([1]), 0.5)
    assert kelly_default == trading.BETA


def test_run_backtest_synthetic():
    """Ejecuta un backtest completo con datos sintéticos"""
    # Generar datos sintéticos
    df = generate_trending_market(days=100)
    df = trading.compute_indicators(df)
    
    # Ejecutar backtest
    results, final_balance = trading.run_backtest(df)
    
    # Verificar resultados
    assert isinstance(results, pd.DataFrame)
    assert len(results) > 0
    assert final_balance > 0
    assert 'regime' in results.columns
    assert 'k' in results.columns
    assert 'c_omega' in results.columns
    assert 'action' in results.columns


def test_system_health():
    """Verifica que el sistema esté vivo según los parámetros del framework"""
    # Verificaciones estructurales del UCF
    from formulas.constants import ALPHA, BETA, THETA_CUBE, ZETA, OMEGA_D, PHI_CRITICAL
    
    assert abs(ALPHA + BETA - 1.0) < 1e-9
    assert abs(math.sin(THETA_CUBE) ** 2 - BETA) < 1e-9
    assert PHI_TOTAL < PHI_CRITICAL
    assert ZETA < 1.0
    assert OMEGA_D > 0


def test_compute_indicators_synthetic():
    """Verifica el cálculo de indicadores con datos sintéticos"""
    df = generate_trending_market(days=50)
    df = trading.compute_indicators(df)
    
    # Verificar que se crearon las columnas esperadas
    assert 'SMA20' in df.columns
    assert 'SMA50' in df.columns
    assert 'RSI' in df.columns
    assert 'volatility' in df.columns
    assert 'BB_middle' in df.columns
    assert 'BB_upper' in df.columns
    assert 'BB_lower' in df.columns
    assert 'momentum_phi' in df.columns
    
    # Verificar que los valores son razonables
    assert not df['SMA20'].isna().all()
    assert not df['RSI'].isna().all()
    assert (df['RSI'] >= 0).all() and (df['RSI'] <= 100).all()


def test_generate_signal_distribution():
    """Verifica la generación de distribuciones de señal"""
    df = generate_trending_market(days=50)
    df = trading.compute_indicators(df)
    
    row = df.iloc[-1]
    regime = "STABLE"
    hurst = 0.55
    
    signals = trading.generate_signal_distribution(row, regime, hurst)
    
    assert "trend_up_prob" in signals
    assert "trend_down_prob" in signals
    assert "oversold_prob" in signals
    assert "overbought_prob" in signals
    assert "uncertainty" in signals
    
    # Las probabilidades deben estar entre 0 y 1
    assert 0.0 <= signals["trend_up_prob"] <= 1.0
    assert 0.0 <= signals["trend_down_prob"] <= 1.0
    assert 0.0 <= signals["oversold_prob"] <= 1.0
    assert 0.0 <= signals["overbought_prob"] <= 1.0
    assert 0.0 <= signals["uncertainty"] <= 1.0


def test_dynamic_threshold():
    """Verifica el ajuste dinámico del umbral según el régimen"""
    base = trading.K_THRESHOLD
    
    assert trading.compute_dynamic_threshold("EXPANDING", base) < base
    assert trading.compute_dynamic_threshold("STABLE", base) == base
    assert trading.compute_dynamic_threshold("COLLAPSING", base) > base
    assert trading.compute_dynamic_threshold("CRITICAL", base) > 1.0


# =========================
# EJECUTAR TESTS
# =========================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
