"""
tests/test_fuerza_debil_vpsi.py — VPSI 9.4
Valida el ángulo de mezcla débil (Weinberg) derivado de la geometría R3.
"""

import pytest
import math
from formulas.constants import ALPHA, BETA

def test_angulo_weinberg_geometrico():
    """
    Verifica la derivación G.4.3: sin^2(theta_W) = F / Ext
    Donde F=6 (caras) y Ext=26 (unidades externas).
    """
    unidades_externas = 26
    caras_cubo = 6
    
    # Derivación directa del VPSI
    sin2_theta_w_calc = caras_cubo / unidades_externas
    
    # Valor físico de referencia (Escala Z)
    valor_referencia = 0.23122
    # Tolerancia según el manuscrito (0.20%)
    tolerancia = valor_referencia * 0.0020
    
    print(f"\n[VPSI] Calculado: {sin2_theta_w_calc} | Esperado: {valor_referencia}")
    
    assert abs(sin2_theta_w_calc - valor_referencia) < tolerancia, \
        f"La asimetría débil {sin2_theta_w_calc} se desvía de la constante física"

def test_proyeccion_beta_debil():
    """
    Valida que la interacción débil es una proyección de la 
    Invariante de Correlación (K) sobre el plano de las caras.
    """
    # Relación entre el núcleo beta y el ángulo débil
    # Según VPSI: sin2_theta_w debe ser aprox 6 * beta
    valor_vpsi = 6 * BETA
    referencia = 6 / 26
    
    assert abs(valor_vpsi - referencia) < 0.01, "Falla en la escala de proyección beta-cara"
