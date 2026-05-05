"""
Test de verificación de importación del módulo de trading.
Este test NO ejecuta el trading, solo verifica que el código
se puede importar sin errores de sintaxis.
"""

def test_trading_module_import():
    """Verifica que el módulo de trading se puede importar"""
    try:
        # Intentar importar el módulo de trading
        import formulas.trading_backtest
        assert True
    except ImportError as e:
        # Si falla la importación, el test falla
        assert False, f"No se pudo importar el módulo de trading: {e}"
