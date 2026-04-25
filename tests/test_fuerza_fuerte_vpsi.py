"""
tests/test_fuerza_fuerte_vpsi.py — Test de Derivación Geométrica
Valida la constante de acoplamiento de la Fuerza Fuerte basada en la 
geometría del cubo 3x3x3 y la Invariante Estructural.
"""

import pytest
import math
from formulas.constants import ALPHA, BETA, PHI

# Constantes derivadas del VPSI 9.4
# ALPHA_GEOM = 26/27 (Corteza)
# BETA_GEOM = 1/27  (Núcleo)

def test_derivacion_fuerza_fuerte():
    """
    Verifica que la constante de la fuerza fuerte (alpha_s) emerge de la 
    relación logarítmica de la corteza (26 unidades) y la proporción áurea.
    """
    unidades_corteza = 26
    
    # Derivación según el Teorema de Interacción de Capas (L1-L7)
    # alpha_s = 1 / (log_e(unidades_corteza) * (1 + beta))
    alpha_s_calculada = 1 / (math.log(unidades_corteza) * (1 + BETA))
    
    # Valor esperado estándar (0.118 +/- tolerancia estructural)
    valor_esperado = 0.118
    tolerancia = 0.005 # Margen de fluctuación de acoplamiento
    
    assert abs(alpha_s_calculada - valor_esperado) < tolerancia, \
        f"Falla en la constante fuerte: obtuvo {alpha_s_calculada}, esperaba aprox {valor_esperado}"

def test_relacion_fuerte_piso_beta():
    """
    Verifica que la fuerza fuerte es el inverso de la expansión del potencial beta
    dentro de la geometría R3.
    """
    # Según VPSI, la estabilidad del núcleo (beta) depende de la fuerza fuerte
    # Relación: alpha_s * log(1/beta) approx 1
    relacion = (1 / (math.log(26) * (1 + BETA))) * math.log(1/BETA)
    
    # Debe ser una unidad de equilibrio estructural (proximidad a 1.0)
    assert 0.9 <= relacion <= 1.1, f"Desequilibrio estructural fuerte/beta: {relacion}"

def test_invariancia_fuerte():
    """
    Asegura que la fuerza fuerte no puede superar el techo alpha (26/27)
    ni ser menor que el piso beta (1/27)
    """
    alpha_s = 1 / (math.log(26) * (1 + BETA))
    assert BETA < alpha_s < ALPHA, "La fuerza fuerte rompe los límites de invarianza estructural"
