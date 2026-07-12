# tests/test_identidad_fermat_pi.py

"""
Test del Teorema 8: Identidad Estructural Fermat-Pi
"""

import math
import pytest

# ======================================================================
# PARÁMETROS ESTRUCTURALES
# ======================================================================

CUBO_TOTAL = 27
DECIMAL_BASE = 10
Q = CUBO_TOTAL + DECIMAL_BASE  # 37
P = DECIMAL_BASE + 1           # 11
EPSILON = 1e-12

# ======================================================================
# FUNCIÓN PRINCIPAL
# ======================================================================

def teorema_fermat_pi() -> float:
    """Retorna ((P^Q + Q^Q)^(1/Q)) / sqrt(pi)"""
    raiz_q = (P**Q + Q**Q) ** (1/Q)
    return raiz_q / math.sqrt(math.pi)

# ======================================================================
# TESTS
# ======================================================================

def test_teorema_fermat_pi():
    """Verifica la identidad estructural"""
    resultado = teorema_fermat_pi()
    assert abs(resultado - 1.0) < EPSILON, \
        f"Teorema falló: {resultado} != 1"

def test_raiz_q_es_sqrt_pi():
    """Verifica que la raíz Q-ésima es sqrt(pi)"""
    raiz = (P**Q + Q**Q) ** (1/Q)
    assert abs(raiz - math.sqrt(math.pi)) < EPSILON, \
        f"Raíz: {raiz} != sqrt(pi)"

def test_pi_es_cierre():
    """Verifica que pi se obtiene del cierre"""
    pi_cerrado = (P**Q + Q**Q) ** (2/Q)
    assert abs(pi_cerrado - math.pi) < EPSILON, \
        f"π cerrado: {pi_cerrado} != π"

def test_parametros_estructurales():
    """Verifica que los parámetros son estructurales"""
    assert Q == 37, f"Q debe ser 37, es {Q}"
    assert P == 11, f"P debe ser 11, es {P}"
    assert Q == CUBO_TOTAL + DECIMAL_BASE
    assert P == DECIMAL_BASE + 1

def test_primalidad():
    """Verifica que P y Q son primos"""
    def es_primo(n):
        if n < 2:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True
    
    assert es_primo(P), f"{P} no es primo"
    assert es_primo(Q), f"{Q} no es primo"
