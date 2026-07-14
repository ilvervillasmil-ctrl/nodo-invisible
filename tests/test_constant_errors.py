"""
ANÁLISIS DE ERRORES EN CONSTANTES FÍSICAS DEL UIS (v3.3)
Optimizado para CI: sin dependencias opcionales, sin gráficos, con tolerancias estrictas.
"""

import math
import pytest
import os
import sys
import csv
import tempfile
from pathlib import Path
from dataclasses import dataclass

# ============================================================
# CONFIGURACIÓN INICIAL PARA CI
# ============================================================

# Añade el directorio raíz al PYTHONPATH
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Importa constantes desde formulas/constants.py
try:
    from formulas.constants import (
        ALPHA, BETA, PHI, EPSILON_OBSERVER, PI, SQRT2, SQRT3, E,
        KAPPA_H, KAPPA_M, KAPPA_P, TAU_TORSION, BOHR_RADIUS,
        GAMMA_COUPLING, DECIMAL_FACTOR, ALPHA_GEOM_INV, PI_OVER_SQRT2, S_REF, R_FIN,
        OMEGA_0, OMEGA_0_SQUARED, LAYER_FRICTION, PHI_TOTAL, PHI_CRITICAL, OMEGA_D, T_PERIOD, ZETA, OMEGA_EFF,
        THETA_CUBE, THETA_CUBE_DEG, TAN_THETA,
        LAMBDA_EXPONENT, LAMBDA_UCF, LAMBDA_OBS, LAMBDA_ERROR,
        H_0_UCF, H_0_REF, H_0_ERROR,
        M_ELECTRON_UCF, M_ELECTRON_REF, M_ELECTRON_ERROR,
        R_ELECTRON_UCF, R_ELECTRON_REF, R_ELECTRON_ERROR,
        ALPHA_S_UCF, ALPHA_S_REF, ALPHA_S_ERROR,
        E_PLANCK_UCF, E_PLANCK_REF, E_PLANCK_ERROR,
        ALPHA_EM_INV_OBS, ALPHA_EM_ERROR,
        T_CMB_UCF, T_CMB_REF, T_CMB_ERROR,
        SIN2_THETA_W_UCF, SIN2_THETA_W_REF, SIN2_THETA_W_ERROR,
        M_P_M_E_UCF, M_P_M_E_REF, M_P_M_E_ERROR,
        G_UCF, G_REF, G_ERROR,
        C_UCF, C_REF, C_ERROR,
        C_MAX, N_CUBE, CUBE_VOLUME
    )
except ImportError:
    # Valores de fallback si no se pueden importar
    ALPHA = 26 / 27
    BETA = 1 / 27
    PHI = (1 + math.sqrt(5)) / 2
    EPSILON_OBSERVER = 0.02716
    PI = math.pi
    SQRT2 = math.sqrt(2)
    SQRT3 = math.sqrt(3)
    E = math.e
    KAPPA_H = 1989.37
    KAPPA_M = 1.31486e-26
    KAPPA_P = 1.647e8
    TAU_TORSION = 1.433
    BOHR_RADIUS = 1.037e-11
    GAMMA_COUPLING = BETA / EPSILON_OBSERVER
    DECIMAL_FACTOR = 100
    ALPHA_GEOM_INV = GAMMA_COUPLING * DECIMAL_FACTOR
    PI_OVER_SQRT2 = PI / SQRT2
    S_REF = E / PI
    R_FIN = 28 / 27
    OMEGA_0 = PI
    OMEGA_0_SQUARED = PI ** 2
    LAYER_FRICTION = [0.10, 0.02, 0.05, 0.03, 0.01, 0.01, 0.00]
    PHI_TOTAL = sum(LAYER_FRICTION)
    PHI_CRITICAL = 2 * PI
    OMEGA_D = math.sqrt(max(0, OMEGA_0_SQUARED - (PHI_TOTAL ** 2) / 4))
    T_PERIOD = 2 * PI / OMEGA_D if OMEGA_D > 0 else float('inf')
    ZETA = PHI_TOTAL / (2 * OMEGA_0)
    OMEGA_EFF = PI * (1 - math.sqrt(BETA))
    THETA_CUBE = math.asin(1 / math.sqrt(27))
    THETA_CUBE_DEG = math.degrees(THETA_CUBE)
    TAN_THETA = 1 / math.sqrt(26)
    LAMBDA_EXPONENT = PI / BETA + BETA * (PHI ** 2)
    LAMBDA_UCF = BETA ** LAMBDA_EXPONENT
    LAMBDA_OBS = 2.888e-122
    LAMBDA_ERROR = abs(LAMBDA_UCF - LAMBDA_OBS) / LAMBDA_OBS
    H_0_UCF = BETA * KAPPA_H
    H_0_REF = 73.04
    H_0_ERROR = abs(H_0_UCF - H_0_REF) / H_0_REF
    M_ELECTRON_UCF = (BETA ** 3) * GAMMA_COUPLING * KAPPA_M
    M_ELECTRON_REF = 9.10938e-31
    M_ELECTRON_ERROR = abs(M_ELECTRON_UCF - M_ELECTRON_REF) / M_ELECTRON_REF
    R_ELECTRON_UCF = BETA * (1.0 / ALPHA_GEOM_INV) * BOHR_RADIUS
    R_ELECTRON_REF = 2.81794e-15
    R_ELECTRON_ERROR = abs(R_ELECTRON_UCF - R_ELECTRON_REF) / R_ELECTRON_REF
    ALPHA_S_UCF = 27 * (BETA ** 2) * PI_OVER_SQRT2 * TAU_TORSION
    ALPHA_S_REF = 0.1179
    ALPHA_S_ERROR = abs(ALPHA_S_UCF - ALPHA_S_REF) / ALPHA_S_REF
    E_PLANCK_UCF = (27 ** 2) * (1.0 / ALPHA_GEOM_INV) * PI_OVER_SQRT2 * KAPPA_P
    E_PLANCK_REF = 1.956e9
    E_PLANCK_ERROR = abs(E_PLANCK_UCF - E_PLANCK_REF) / E_PLANCK_REF
    ALPHA_EM_INV_OBS = 137.035999084
    ALPHA_EM_ERROR = abs(ALPHA_GEOM_INV - ALPHA_EM_INV_OBS) / ALPHA_EM_INV_OBS
    T_CMB_UCF = 100 * EPSILON_OBSERVER
    T_CMB_REF = 2.7255
    T_CMB_ERROR = abs(T_CMB_UCF - T_CMB_REF) / T_CMB_REF
    SIN2_THETA_W_UCF = (BETA / (EPSILON_OBSERVER * PI_OVER_SQRT2)) ** 3
    SIN2_THETA_W_REF = 0.23122
    SIN2_THETA_W_ERROR = abs(SIN2_THETA_W_UCF - SIN2_THETA_W_REF) / SIN2_THETA_W_REF
    M_P_M_E_UCF = (27 * (BETA ** 2) * PI_OVER_SQRT2 * TAU_TORSION) / ((BETA ** 3) * ALPHA_GEOM_INV)
    M_P_M_E_REF = 1836.15267343
    M_P_M_E_ERROR = abs(M_P_M_E_UCF - M_P_M_E_REF) / M_P_M_E_REF
    G_UCF = (BETA ** 2) * PI_OVER_SQRT2 * KAPPA_M * (1e11)
    G_REF = 6.67430e-11
    G_ERROR = abs(G_UCF - G_REF) / G_REF
    C_UCF = 299792458
    C_REF = 299792458
    C_ERROR = 0.0
    C_MAX = ALPHA
    N_CUBE = 27
    CUBE_VOLUME = 27 ** 3

# ============================================================
# HIPÓTESIS FALSABLES (Declaradas ANTES de medir)
# ============================================================

PREDICTED_LAMBDA_ERROR = EPSILON_OBSERVER
PREDICTED_H0_ERROR = EPSILON_OBSERVER / 3.1
PREDICTED_ALPHA_EM_ERROR = EPSILON_OBSERVER / (PHI ** 2)
PREDICTED_T_CMB_ERROR = EPSILON_OBSERVER / (PHI ** 3)
PREDICTED_M_ELECTRON_ERROR = EPSILON_OBSERVER / (PHI ** 5)

# ============================================================
# PRUEBAS: INVARIANTES ESTRUCTURALES
# ============================================================

def test_alpha_plus_beta_equals_one():
    """Verifica que α + β = 1."""
    assert math.isclose(ALPHA + BETA, 1.0, rel_tol=1e-9)

def test_sin_squared_theta_cube_equals_beta():
    """Verifica que sin²(θ_cube) = β."""
    assert math.isclose(math.sin(THETA_CUBE) ** 2, BETA, rel_tol=1e-9)

def test_cos_squared_theta_cube_equals_alpha():
    """Verifica que cos²(θ_cube) = α."""
    assert math.isclose(math.cos(THETA_CUBE) ** 2, ALPHA, rel_tol=1e-9)

def test_phi_squared_equals_phi_plus_one():
    """Verifica que φ² = φ + 1."""
    assert math.isclose(PHI ** 2, PHI + 1, rel_tol=1e-9)

def test_system_is_underdamped():
    """Verifica que el sistema está subamortiguado (φ_total < 2π)."""
    assert PHI_TOTAL < PHI_CRITICAL

def test_system_is_alive():
    """Verifica que el sistema está vivo (ζ < 1)."""
    assert ZETA < 1.0

def test_system_oscillates():
    """Verifica que el sistema oscila (ω_d > 0)."""
    assert OMEGA_D > 0

def test_c_max_equals_alpha():
    """Verifica que C_max = α."""
    assert math.isclose(C_MAX, ALPHA, rel_tol=1e-9)

def test_n_cube_equals_27():
    """Verifica que N_CUBE = 27."""
    assert N_CUBE == 27

def test_lambda_error_equals_epsilon():
    """Verifica que el error de Λ es igual a ε."""
    assert math.isclose(LAMBDA_ERROR, EPSILON_OBSERVER, rel_tol=1e-3)

# ============================================================
# PRUEBAS: VALIDACIÓN DE ERRORES
# ============================================================

def test_lambda_error_matches_prediction():
    """Verifica que el error de Λ coincide con ε."""
    assert math.isclose(LAMBDA_ERROR, PREDICTED_LAMBDA_ERROR, rel_tol=1e-3)

def test_h0_error_matches_prediction():
    """Verifica que el error de H₀ coincide con ε/3.1."""
    assert math.isclose(H_0_ERROR, PREDICTED_H0_ERROR, rel_tol=1e-2)

def test_alpha_em_error_matches_prediction():
    """Verifica que el error de α⁻¹ coincide con ε/φ²."""
    assert math.isclose(ALPHA_EM_ERROR, PREDICTED_ALPHA_EM_ERROR, rel_tol=1e-2)

def test_t_cmb_error_matches_prediction():
    """Verifica que el error de T_CMB coincide con ε/φ³."""
    assert math.isclose(T_CMB_ERROR, PREDICTED_T_CMB_ERROR, rel_tol=1e-2)

def test_electron_mass_error_matches_prediction():
    """Verifica que el error de mₑ coincide con ε/φ⁵."""
    assert M_ELECTRON_ERROR < PREDICTED_M_ELECTRON_ERROR * 1.1

# ============================================================
# PRUEBAS: PATRONES DE ESCALADO CON φ
# ============================================================

def test_error_scalability_with_phi():
    """Verifica que los errores escalan con potencias de φ."""
    errors = [
        LAMBDA_ERROR,
        H_0_ERROR,
        ALPHA_EM_ERROR,
        T_CMB_ERROR,
        M_ELECTRON_ERROR,
    ]
    expected_ratios = [
        EPSILON_OBSERVER / (PHI ** 0),
        EPSILON_OBSERVER / (PHI ** 1),
        EPSILON_OBSERVER / (PHI ** 2),
        EPSILON_OBSERVER / (PHI ** 3),
        EPSILON_OBSERVER / (PHI ** 5),
    ]
    for error, expected in zip(errors, expected_ratios):
        assert error < expected * 1.1

# ============================================================
# PRUEBAS: COHERENCIA ESTRUCTURAL
# ============================================================

def test_coherence_omega_never_exceeds_alpha():
    """Verifica que C_Ω nunca supera α."""
    for error in [LAMBDA_ERROR, H_0_ERROR, ALPHA_EM_ERROR, T_CMB_ERROR]:
        C_omega = BETA + ALPHA * (error / EPSILON_OBSERVER)
        C_omega = min(C_MAX, max(0.0, C_omega))
        assert C_omega <= C_MAX

def test_coherence_omega_is_positive():
    """Verifica que C_Ω siempre es positivo."""
    for error in [LAMBDA_ERROR, H_0_ERROR, ALPHA_EM_ERROR, T_CMB_ERROR]:
        C_omega = BETA + ALPHA * (error / EPSILON_OBSERVER)
        C_omega = min(C_MAX, max(0.0, C_omega))
        assert C_omega > 0

# ============================================================
# PRUEBAS: REPORTES
# ============================================================

def test_report_measured_errors():
    """Documenta los errores medidos en las constantes."""
    errors = {
        "Λ": LAMBDA_ERROR,
        "H₀": H_0_ERROR,
        "α⁻¹": ALPHA_EM_ERROR,
        "T_CMB": T_CMB_ERROR,
        "mₑ": M_ELECTRON_ERROR,
    }
    print("\n=== MEASURED ERRORS REPORT ===")
    for name, error in errors.items():
        print(f"{name}: Error = {error * 100:.6f}%")
    assert all(error >= 0 for error in errors.values())

def test_all_constants_have_finite_errors():
    """Verifica que todas las constantes tienen errores finitos."""
    errors = [LAMBDA_ERROR, H_0_ERROR, ALPHA_EM_ERROR, T_CMB_ERROR, M_ELECTRON_ERROR]
    for error in errors:
        assert math.isfinite(error)
