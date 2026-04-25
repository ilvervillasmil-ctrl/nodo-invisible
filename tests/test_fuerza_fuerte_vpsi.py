"""
tests/test_fuerza_fuerte_vpsi.py
Test de precisión para la primera de las 21 constantes del Apéndice G.
"""

import pytest
import math
from formulas.constants import ALPHA, BETA # ALPHA=26/27, BETA=1/27

def test_derivacion_g4_3_fuerza_z_scale():
    """
    Valida la derivación G.4.3: El ángulo de mezcla débil (escala Z) 
    como relación geométrica Caras/Corteza.
    """
    # Cantidades del cubo 3x3x3 según VPSI 9.4
    caras = 6
    corteza = 26 # Ext
    
    # La teoría dicta que sin^2(theta_W) = F / Ext
    valor_calculado = caras / corteza
    
    # Referencia física estándar: 0.23122
    valor_referencia = 0.23122
    error_vpsi = 0.0020 # 0.20% de error reportado en el doc
    
    print(f"\n[VPSI G.4.3] Geométrico: {valor_calculado} | Referencia: {valor_referencia}")
    
    assert abs(valor_calculado - valor_referencia) / valor_referencia < error_vpsi, \
        f"La derivación geométrica {valor_calculado} excede el margen de error del 0.20%"

def test_identidad_dualidad_vpsi():
    """
    Valida la Identidad Geométrica Central H.2: sin^2(theta_cube) = beta
    """
    n_total = 27
    theta_cube = math.asin(1 / math.sqrt(n_total))
    
    res_sin2 = math.sin(theta_cube)**2
    
    # Debe ser exactamente igual a BETA (1/27)
    assert abs(res_sin2 - BETA) < 1e-15, f"Falla en Identidad Central: {res_sin2} != {BETA}"
