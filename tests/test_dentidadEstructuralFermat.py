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
# FUNCIÓN PRINCIPAL (¡CORREGIDA!)
# ======================================================================

def teorema_fermat_pi() -> float:
    """Retorna ((P^Q + Q^Q)^(1/Q)) / sqrt(pi)"""
    # ¡IMPORTANTE! ** (1/Q) es la raíz Q-ésima
    raiz_q = (P ** Q + Q ** Q) ** (1 / Q)  # ← ¡LA CLAVE!
    return raiz_q / math.sqrt(math.pi)

# ======================================================================
# TESTS
# ======================================================================

def test_teorema_fermat_pi():
    """Verifica la identidad estructural"""
    resultado = teorema_fermat_pi()
    print(f"\nResultado: {resultado}")
    print(f"√π: {math.sqrt(math.pi)}")
    print(f"Raíz Q-ésima: {(P ** Q + Q ** Q) ** (1 / Q)}")
    assert abs(resultado - 1.0) < EPSILON, \
        f"Teorema falló: {resultado} != 1"

def test_raiz_q_es_sqrt_pi():
    """Verifica que la raíz Q-ésima es sqrt(pi)"""
    raiz = (P ** Q + Q ** Q) ** (1 / Q)
    print(f"\nRaíz Q-ésima: {raiz}")
    print(f"√π: {math.sqrt(math.pi)}")
    print(f"Diferencia: {abs(raiz - math.sqrt(math.pi))}")
    assert abs(raiz - math.sqrt(math.pi)) < EPSILON, \
        f"Raíz: {raiz} != sqrt(pi)"

def test_pi_es_cierre():
    """Verifica que pi se obtiene del cierre"""
    pi_cerrado = (P ** Q + Q ** Q) ** (2 / Q)
    print(f"\nπ cerrado: {pi_cerrado}")
    print(f"π: {math.pi}")
    print(f"Diferencia: {abs(pi_cerrado - math.pi)}")
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
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True
    
    assert es_primo(P), f"{P} no es primo"
    assert es_primo(Q), f"{Q} no es primo"

def test_relacion_estructural():
    """Verifica la relación Q - P = 26 (cubo exterior)"""
    assert Q - P == 26, f"{Q} - {P} = {Q-P} != 26"
    assert Q + P == 48, f"{Q} + {P} = {Q+P} != 48"
    assert Q * P == 407, f"{Q} * {P} = {Q*P} != 407"
