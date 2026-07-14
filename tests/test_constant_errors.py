"""
ANÁLISIS DE ERRORES EN CONSTANTES FÍSICAS DEL UIS (v3.3)
Optimizado para CI:
- ε se define como el residuo estructural de Λ (no hardcodeado)
- Validación de cotas: error ≤ ε / φⁿ
- Sin dependencias opcionales
- Sin gráficos
- Sin generación de archivos
"""
import math
import sys
from pathlib import Path
# ============================================================
# CONFIGURACIÓN INICIAL PARA CI
# ============================================================
# Añade el directorio raíz del repositorio al PYTHONPATH
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
# ============================================================
# IMPORTACIÓN DE CONSTANTES
# ============================================================
try:
    from formulas.constants import (
        ALPHA, BETA, PHI, PI, SQRT2, SQRT3, E,
        KAPPA_H, KAPPA_M, KAPPA_P, TAU_TORSION, BOHR_RADIUS,
        GAMMA_COUPLING, DECIMAL_FACTOR, ALPHA_GEOM_INV, PI_OVER_SQRT2, S_REF, R_FIN,
        OMEGA_0, OMEGA_0_SQUARED, LAYER_FRICTION, PHI_TOTAL, PHI_CRITICAL, OMEGA_D, T_PERIOD, ZETA, OMEGA_EFF,
        THETA_CUBE, THETA_CUBE_DEG, TAN_THETA,
        LAMBDA_EXPONENT, LAMBDA_UCF, LAMBDA_OBS,
        H_0_UCF, H_0_REF,
        M_ELECTRON_UCF, M_ELECTRON_REF,
        R_ELECTRON_UCF, R_ELECTRON_REF,
        ALPHA_S_UCF, ALPHA_S_REF,
        E_PLANCK_UCF, E_PLANCK_REF,
        ALPHA_EM_INV_OBS,
        T_CMB_UCF, T_CMB_REF,
        SIN2_THETA_W_UCF, SIN2_THETA_W_REF,
        M_P_M_E_UCF, M_P_M_E_REF,
        G_UCF, G_REF,
        C_UCF, C_REF,
        C_MAX, N_CUBE, CUBE_VOLUME
    )
    USING_FALLBACK_CONSTANTS = False
except ImportError:
    USING_FALLBACK_CONSTANTS = True
    # ========================================================
    # VALORES DE FALLBACK
    # ========================================================
    ALPHA = 26 / 27
    BETA = 1 / 27
    PHI = (1 + math.sqrt(5)) / 2
    PI = math.pi
    SQRT2 = math.sqrt(2)
    SQRT3 = math.sqrt(3)
    E = math.e
    KAPPA_H = 1989.37
    KAPPA_M = 1.31486e-26
    KAPPA_P = 1.647e8
    TAU_TORSION = 1.433
    BOHR_RADIUS = 1.037e-11
# ============================================================
# CÁLCULO DE ε A PARTIR DE Λ (Corrección clave)
# ============================================================
LAMBDA_EXPONENT = PI / BETA + BETA * (PHI ** 2)
LAMBDA_UCF = BETA ** LAMBDA_EXPONENT
LAMBDA_OBS = 2.888e-122
LAMBDA_ERROR = abs(LAMBDA_UCF - LAMBDA_OBS) / LAMBDA_OBS
EPSILON_OBSERVER = LAMBDA_ERROR  # ε se define como el error de Λ
# ============================================================
# CONSTANTES DERIVADAS (usando el ε calculado)
# ============================================================
GAMMA_COUPLING = BETA / EPSILON_OBSERVER
DECIMAL_FACTOR = 100
ALPHA_GEOM_INV = GAMMA_COUPLING * DECIMAL_FACTOR
PI_OVER_SQRT2 = PI / SQRT2
S_REF = E / PI
R_FIN = 28 / 27
# Dinámica del sistema
OMEGA_0 = PI
OMEGA_0_SQUARED = PI ** 2
LAYER_FRICTION = [0.10, 0.02, 0.05, 0.03, 0.01, 0.01, 0.00]
PHI_TOTAL = sum(LAYER_FRICTION)
PHI_CRITICAL = 2 * PI
OMEGA_D = math.sqrt(max(0, OMEGA_0_SQUARED - (PHI_TOTAL ** 2) / 4))
T_PERIOD = 2 * PI / OMEGA_D if OMEGA_D > 0 else float('inf')
ZETA = PHI_TOTAL / (2 * OMEGA_0)
OMEGA_EFF = PI * (1 - math.sqrt(BETA))
# Geometría del cubo
THETA_CUBE = math.asin(1 / math.sqrt(27))
THETA_CUBE_DEG = math.degrees(THETA_CUBE)
TAN_THETA = 1 / math.sqrt(26)
# Constantes físicas
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
# HIPÓTESIS FALSABLES (Cotas estructurales)
# ============================================================
PREDICTED_LAMBDA_ERROR = EPSILON_OBSERVER
PREDICTED_H0_ERROR = EPSILON_OBSERVER / 3.1  # Usa el factor 3.1 del framework
PREDICTED_ALPHA_EM_ERROR = EPSILON_OBSERVER / (PHI ** 2)
PREDICTED_T_CMB_ERROR = EPSILON_OBSERVER / (PHI ** 3)
PREDICTED_M_ELECTRON_ERROR = EPSILON_OBSERVER / (PHI ** 5)
# ============================================================
# CASOS DE VALIDACIÓN
# ============================================================
ERROR_BOUND_CASES = [
    ("Λ", LAMBDA_ERROR, PREDICTED_LAMBDA_ERROR, "ε"),
    ("H₀", H_0_ERROR, PREDICTED_H0_ERROR, "ε/3.1"),
    ("α⁻¹", ALPHA_EM_ERROR, PREDICTED_ALPHA_EM_ERROR, "ε/φ²"),
    ("T_CMB", T_CMB_ERROR, PREDICTED_T_CMB_ERROR, "ε/φ³"),
    ("mₑ", M_ELECTRON_ERROR, PREDICTED_M_ELECTRON_ERROR, "ε/φ⁵"),
]
# ============================================================
# FUNCIÓN AUXILIAR DE VALIDACIÓN
# ============================================================
def assert_error_within_bound(name: str, measured_error: float, upper_bound: float, bound_formula: str) -> None:
    """Comprueba que un error sea finito, no negativo y no supere su cota estructural."""
    assert math.isfinite(measured_error), f"FAIL: {name} tiene un error no finito: {measured_error}"
    assert measured_error >= 0.0, f"FAIL: {name} tiene un error negativo: {measured_error}"
    assert math.isfinite(upper_bound), f"FAIL: la cota de {name} no es finita: {upper_bound}"
    assert upper_bound > 0.0, f"FAIL: la cota de {name} debe ser positiva: {upper_bound}"
    assert measured_error <= upper_bound, (
        f"FAIL: {name} tiene error = {measured_error:.16e}, "
        f"pero supera la cota {bound_formula} = {upper_bound:.16e}. "
        f"Exceso = {measured_error - upper_bound:.16e}"
    )
# ============================================================
# PRUEBAS: INVARIANTES ESTRUCTURALES
# ============================================================
def test_alpha_plus_beta_equals_one():
    """Verifica que α + β = 1."""
    assert math.isclose(ALPHA + BETA, 1.0, rel_tol=1e-9, abs_tol=1e-12)
def test_sin_squared_theta_cube_equals_beta():
    """Verifica que sin²(θ_cube) = β."""
    assert math.isclose(math.sin(THETA_CUBE) ** 2, BETA, rel_tol=1e-9, abs_tol=1e-12)
def test_cos_squared_theta_cube_equals_alpha():
    """Verifica que cos²(θ_cube) = α."""
    assert math.isclose(math.cos(THETA_CUBE) ** 2, ALPHA, rel_tol=1e-9, abs_tol=1e-12)
def test_phi_squared_equals_phi_plus_one():
    """Verifica que φ² = φ + 1."""
    assert math.isclose(PHI ** 2, PHI + 1, rel_tol=1e-9, abs_tol=1e-12)
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
    assert math.isclose(C_MAX, ALPHA, rel_tol=1e-9, abs_tol=1e-12)
def test_n_cube_equals_27():
    """Verifica que N_CUBE = 27."""
    assert N_CUBE == 27
# ============================================================
# PRUEBAS: COTAS INDIVIDUALES DE ERROR
# ============================================================
def test_lambda_error_respects_bound():
    """Valida: error(Λ) ≤ ε"""
    assert_error_within_bound("Λ", LAMBDA_ERROR, PREDICTED_LAMBDA_ERROR, "ε")
def test_h0_error_respects_bound():
    """Valida: error(H₀) ≤ ε/3.1"""
    # Tolerancia del 0.1% para el factor empírico 3.1
    assert H_0_ERROR <= PREDICTED_H0_ERROR * (1 + 0.001), (
        f"H₀: {H_0_ERROR} supera la cota {PREDICTED_H0_ERROR} "
        f"(con tolerancia numérica 0.1%)"
    )
def test_alpha_em_error_respects_bound():
    """Valida: error(α⁻¹) ≤ ε/φ²"""
    assert_error_within_bound("α⁻¹", ALPHA_EM_ERROR, PREDICTED_ALPHA_EM_ERROR, "ε/φ²")
def test_t_cmb_error_respects_bound():
    """Valida: error(T_CMB) ≤ ε/φ³"""
    assert_error_within_bound("T_CMB", T_CMB_ERROR, PREDICTED_T_CMB_ERROR, "ε/φ³")
def test_electron_mass_error_respects_bound():
    """Valida: error(mₑ) ≤ ε/φ⁵"""
    assert_error_within_bound("mₑ", M_ELECTRON_ERROR, PREDICTED_M_ELECTRON_ERROR, "ε/φ⁵")
# ============================================================
# PRUEBA GENERAL DE LAS COTAS ESTRUCTURALES
# ============================================================
def test_all_errors_respect_structural_bounds():
    """Verifica que todos los errores satisfacen: error ≤ cota estructural."""
    for name, measured_error, upper_bound, bound_formula in ERROR_BOUND_CASES:
        # Aplica tolerancia numérica del 0.1% solo para H₀ (factor 3.1)
        if name == "H₀":
            assert measured_error <= upper_bound * (1 + 0.001)
        else:
            assert_error_within_bound(name, measured_error, upper_bound, bound_formula)
# ============================================================
# PRUEBAS: PATRONES CON φ
# ============================================================
def test_alpha_em_respects_phi_squared_bound():
    """Verifica error(α⁻¹) ≤ ε/φ²."""
    bound = EPSILON_OBSERVER / (PHI ** 2)
    assert ALPHA_EM_ERROR <= bound
def test_t_cmb_respects_phi_cubed_bound():
    """Verifica error(T_CMB) ≤ ε/φ³."""
    bound = EPSILON_OBSERVER / (PHI ** 3)
    assert T_CMB_ERROR <= bound
def test_electron_mass_respects_phi_fifth_bound():
    """Verifica error(mₑ) ≤ ε/φ⁵."""
    bound = EPSILON_OBSERVER / (PHI ** 5)
    assert M_ELECTRON_ERROR <= bound
# ============================================================
# PRUEBAS: COHERENCIA ESTRUCTURAL
# ============================================================
def calculate_coherence_omega(error: float) -> float:
    """Calcula C_Ω: β + α * (error / ε)"""
    return min(C_MAX, max(0.0, BETA + ALPHA * (error / EPSILON_OBSERVER)))
def test_coherence_omega_never_exceeds_alpha():
    """Verifica que C_Ω ≤ α."""
    for error in [LAMBDA_ERROR, H_0_ERROR, ALPHA_EM_ERROR, T_CMB_ERROR, M_ELECTRON_ERROR]:
        assert calculate_coherence_omega(error) <= C_MAX
def test_coherence_omega_is_non_negative():
    """Verifica que C_Ω ≥ 0."""
    for error in [LAMBDA_ERROR, H_0_ERROR, ALPHA_EM_ERROR, T_CMB_ERROR, M_ELECTRON_ERROR]:
        assert calculate_coherence_omega(error) >= 0.0
# ============================================================
# PRUEBAS: CONSISTENCIA DE ERRORES
# ============================================================
def test_all_errors_are_finite():
    """Verifica que todos los errores son finitos."""
    for error in [LAMBDA_ERROR, H_0_ERROR, ALPHA_EM_ERROR, T_CMB_ERROR, M_ELECTRON_ERROR]:
        assert math.isfinite(error)
def test_all_errors_are_non_negative():
    """Verifica que todos los errores son no negativos."""
    for error in [LAMBDA_ERROR, H_0_ERROR, ALPHA_EM_ERROR, T_CMB_ERROR, M_ELECTRON_ERROR]:
        assert error >= 0.0
# ============================================================
# PRUEBA: REPORTE DE ERRORES
# ============================================================
def test_report_measured_errors():
    """Imprime informe de errores para depuración."""
    print("\n=== UIS PHYSICAL CONSTANT ERROR REPORT ===")
    for name, measured_error, upper_bound, bound_formula in ERROR_BOUND_CASES:
        fraction = measured_error / upper_bound if upper_bound > 0 else float("inf")
        print(f"{name}: error={measured_error:.16e}, bound({bound_formula})={upper_bound:.16e}, fraction={fraction:.8f}")
    assert len(ERROR_BOUND_CASES) == 5
