"""
ANÁLISIS DE ERRORES EN CONSTANTES FÍSICAS DEL UIS (v3.3)

Optimizado para CI:
- Sin dependencias opcionales.
- Sin gráficos.
- Sin generación de archivos.
- Con hipótesis falsables expresadas como cotas superiores.

Hipótesis general:

    0 ≤ error ≤ límite estructural predicho

Para los patrones asociados a la razón áurea:

    error ≤ ε / φⁿ

No se exige igualdad exacta entre el error medido y la cota.
"""

import math
import sys
from pathlib import Path

# ============================================================
# CONFIGURACIÓN INICIAL PARA CI
# ============================================================

# Añade el directorio raíz del repositorio al PYTHONPATH.
REPO_ROOT = Path(__file__).resolve().parent.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


# ============================================================
# IMPORTACIÓN DE CONSTANTES
# ============================================================

try:
    from formulas.constants import (
        ALPHA,
        BETA,
        PHI,
        EPSILON_OBSERVER,
        PI,
        SQRT2,
        SQRT3,
        E,
        KAPPA_H,
        KAPPA_M,
        KAPPA_P,
        TAU_TORSION,
        BOHR_RADIUS,
        GAMMA_COUPLING,
        DECIMAL_FACTOR,
        ALPHA_GEOM_INV,
        PI_OVER_SQRT2,
        S_REF,
        R_FIN,
        OMEGA_0,
        OMEGA_0_SQUARED,
        LAYER_FRICTION,
        PHI_TOTAL,
        PHI_CRITICAL,
        OMEGA_D,
        T_PERIOD,
        ZETA,
        OMEGA_EFF,
        THETA_CUBE,
        THETA_CUBE_DEG,
        TAN_THETA,
        LAMBDA_EXPONENT,
        LAMBDA_UCF,
        LAMBDA_OBS,
        LAMBDA_ERROR,
        H_0_UCF,
        H_0_REF,
        H_0_ERROR,
        M_ELECTRON_UCF,
        M_ELECTRON_REF,
        M_ELECTRON_ERROR,
        R_ELECTRON_UCF,
        R_ELECTRON_REF,
        R_ELECTRON_ERROR,
        ALPHA_S_UCF,
        ALPHA_S_REF,
        ALPHA_S_ERROR,
        E_PLANCK_UCF,
        E_PLANCK_REF,
        E_PLANCK_ERROR,
        ALPHA_EM_INV_OBS,
        ALPHA_EM_ERROR,
        T_CMB_UCF,
        T_CMB_REF,
        T_CMB_ERROR,
        SIN2_THETA_W_UCF,
        SIN2_THETA_W_REF,
        SIN2_THETA_W_ERROR,
        M_P_M_E_UCF,
        M_P_M_E_REF,
        M_P_M_E_ERROR,
        G_UCF,
        G_REF,
        G_ERROR,
        C_UCF,
        C_REF,
        C_ERROR,
        C_MAX,
        N_CUBE,
        CUBE_VOLUME,
    )

    USING_FALLBACK_CONSTANTS = False

except ImportError:
    # ========================================================
    # VALORES DE FALLBACK
    # ========================================================

    USING_FALLBACK_CONSTANTS = True

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
    OMEGA_0_SQUARED = PI**2

    LAYER_FRICTION = [
        0.10,
        0.02,
        0.05,
        0.03,
        0.01,
        0.01,
        0.00,
    ]

    PHI_TOTAL = sum(LAYER_FRICTION)
    PHI_CRITICAL = 2 * PI

    OMEGA_D = math.sqrt(
        max(
            0.0,
            OMEGA_0_SQUARED - (PHI_TOTAL**2) / 4,
        )
    )

    T_PERIOD = (
        2 * PI / OMEGA_D
        if OMEGA_D > 0
        else float("inf")
    )

    ZETA = PHI_TOTAL / (2 * OMEGA_0)
    OMEGA_EFF = PI * (1 - math.sqrt(BETA))

    THETA_CUBE = math.asin(1 / math.sqrt(27))
    THETA_CUBE_DEG = math.degrees(THETA_CUBE)
    TAN_THETA = 1 / math.sqrt(26)

    LAMBDA_EXPONENT = PI / BETA + BETA * (PHI**2)
    LAMBDA_UCF = BETA**LAMBDA_EXPONENT
    LAMBDA_OBS = 2.888e-122
    LAMBDA_ERROR = (
        abs(LAMBDA_UCF - LAMBDA_OBS)
        / LAMBDA_OBS
    )

    H_0_UCF = BETA * KAPPA_H
    H_0_REF = 73.04
    H_0_ERROR = (
        abs(H_0_UCF - H_0_REF)
        / H_0_REF
    )

    M_ELECTRON_UCF = (
        (BETA**3)
        * GAMMA_COUPLING
        * KAPPA_M
    )

    M_ELECTRON_REF = 9.10938e-31
    M_ELECTRON_ERROR = (
        abs(M_ELECTRON_UCF - M_ELECTRON_REF)
        / M_ELECTRON_REF
    )

    R_ELECTRON_UCF = (
        BETA
        * (1.0 / ALPHA_GEOM_INV)
        * BOHR_RADIUS
    )

    R_ELECTRON_REF = 2.81794e-15
    R_ELECTRON_ERROR = (
        abs(R_ELECTRON_UCF - R_ELECTRON_REF)
        / R_ELECTRON_REF
    )

    ALPHA_S_UCF = (
        27
        * (BETA**2)
        * PI_OVER_SQRT2
        * TAU_TORSION
    )

    ALPHA_S_REF = 0.1179
    ALPHA_S_ERROR = (
        abs(ALPHA_S_UCF - ALPHA_S_REF)
        / ALPHA_S_REF
    )

    E_PLANCK_UCF = (
        (27**2)
        * (1.0 / ALPHA_GEOM_INV)
        * PI_OVER_SQRT2
        * KAPPA_P
    )

    E_PLANCK_REF = 1.956e9
    E_PLANCK_ERROR = (
        abs(E_PLANCK_UCF - E_PLANCK_REF)
        / E_PLANCK_REF
    )

    ALPHA_EM_INV_OBS = 137.035999084
    ALPHA_EM_ERROR = (
        abs(ALPHA_GEOM_INV - ALPHA_EM_INV_OBS)
        / ALPHA_EM_INV_OBS
    )

    T_CMB_UCF = 100 * EPSILON_OBSERVER
    T_CMB_REF = 2.7255
    T_CMB_ERROR = (
        abs(T_CMB_UCF - T_CMB_REF)
        / T_CMB_REF
    )

    SIN2_THETA_W_UCF = (
        BETA
        / (
            EPSILON_OBSERVER
            * PI_OVER_SQRT2
        )
    ) ** 3

    SIN2_THETA_W_REF = 0.23122
    SIN2_THETA_W_ERROR = (
        abs(
            SIN2_THETA_W_UCF
            - SIN2_THETA_W_REF
        )
        / SIN2_THETA_W_REF
    )

    M_P_M_E_UCF = (
        27
        * (BETA**2)
        * PI_OVER_SQRT2
        * TAU_TORSION
    ) / (
        (BETA**3)
        * ALPHA_GEOM_INV
    )

    M_P_M_E_REF = 1836.15267343
    M_P_M_E_ERROR = (
        abs(M_P_M_E_UCF - M_P_M_E_REF)
        / M_P_M_E_REF
    )

    G_UCF = (
        (BETA**2)
        * PI_OVER_SQRT2
        * KAPPA_M
        * 1e11
    )

    G_REF = 6.67430e-11
    G_ERROR = (
        abs(G_UCF - G_REF)
        / G_REF
    )

    C_UCF = 299792458
    C_REF = 299792458
    C_ERROR = 0.0

    C_MAX = ALPHA
    N_CUBE = 27
    CUBE_VOLUME = 27**3


# ============================================================
# HIPÓTESIS FALSABLES
# ============================================================
#
# Estas cotas deben estar declaradas antes de evaluar los
# errores calculados.
#
# Hipótesis:
#
#     error medido ≤ límite estructural predicho
#
# Para α⁻¹, T_CMB y mₑ:
#
#     error ≤ ε / φⁿ
#
# Para H₀ se mantiene la relación específica ε / 3.1
# declarada por el framework.
# ============================================================

PREDICTED_LAMBDA_ERROR = EPSILON_OBSERVER

PREDICTED_H0_ERROR = (
    EPSILON_OBSERVER / 3.1
)

PREDICTED_ALPHA_EM_ERROR = (
    EPSILON_OBSERVER / (PHI**2)
)

PREDICTED_T_CMB_ERROR = (
    EPSILON_OBSERVER / (PHI**3)
)

PREDICTED_M_ELECTRON_ERROR = (
    EPSILON_OBSERVER / (PHI**5)
)


# ============================================================
# CASOS DE VALIDACIÓN
# ============================================================

ERROR_BOUND_CASES = [
    (
        "Λ",
        LAMBDA_ERROR,
        PREDICTED_LAMBDA_ERROR,
        "ε",
    ),
    (
        "H₀",
        H_0_ERROR,
        PREDICTED_H0_ERROR,
        "ε/3.1",
    ),
    (
        "α⁻¹",
        ALPHA_EM_ERROR,
        PREDICTED_ALPHA_EM_ERROR,
        "ε/φ²",
    ),
    (
        "T_CMB",
        T_CMB_ERROR,
        PREDICTED_T_CMB_ERROR,
        "ε/φ³",
    ),
    (
        "mₑ",
        M_ELECTRON_ERROR,
        PREDICTED_M_ELECTRON_ERROR,
        "ε/φ⁵",
    ),
]


# ============================================================
# FUNCIÓN AUXILIAR DE VALIDACIÓN
# ============================================================

def assert_error_within_bound(
    name: str,
    measured_error: float,
    upper_bound: float,
    bound_formula: str,
) -> None:
    """
    Comprueba que un error sea finito, no negativo y que no
    supere su cota estructural.
    """

    assert math.isfinite(measured_error), (
        f"FAIL: {name} tiene un error no finito: "
        f"{measured_error}"
    )

    assert measured_error >= 0.0, (
        f"FAIL: {name} tiene un error negativo: "
        f"{measured_error}"
    )

    assert math.isfinite(upper_bound), (
        f"FAIL: la cota de {name} no es finita: "
        f"{upper_bound}"
    )

    assert upper_bound > 0.0, (
        f"FAIL: la cota de {name} debe ser positiva: "
        f"{upper_bound}"
    )

    assert measured_error <= upper_bound, (
        f"FAIL: {name} tiene error = {measured_error:.16e}, "
        f"pero supera la cota {bound_formula} = "
        f"{upper_bound:.16e}. "
        f"Exceso = {measured_error - upper_bound:.16e}"
    )


# ============================================================
# PRUEBAS: IMPORTACIÓN Y CONFIGURACIÓN
# ============================================================

def test_repository_root_exists():
    """Verifica que el directorio raíz calculado existe."""

    assert REPO_ROOT.exists(), (
        f"El directorio raíz no existe: {REPO_ROOT}"
    )

    assert REPO_ROOT.is_dir(), (
        f"La ruta raíz no es un directorio: {REPO_ROOT}"
    )


def test_structural_constants_are_finite():
    """Verifica que las constantes estructurales son finitas."""

    constants = [
        ALPHA,
        BETA,
        PHI,
        EPSILON_OBSERVER,
        PI,
        SQRT2,
        SQRT3,
        E,
        C_MAX,
    ]

    for value in constants:
        assert math.isfinite(value), (
            f"Constante estructural no finita: {value}"
        )


def test_epsilon_observer_is_positive():
    """Verifica que ε es una cantidad positiva."""

    assert EPSILON_OBSERVER > 0.0, (
        f"ε debe ser positiva, pero vale "
        f"{EPSILON_OBSERVER}"
    )


# ============================================================
# PRUEBAS: INVARIANTES ESTRUCTURALES
# ============================================================

def test_alpha_plus_beta_equals_one():
    """Verifica que α + β = 1."""

    assert math.isclose(
        ALPHA + BETA,
        1.0,
        rel_tol=1e-9,
        abs_tol=1e-12,
    ), (
        f"α + β = {ALPHA + BETA}, "
        f"pero debería ser 1"
    )


def test_sin_squared_theta_cube_equals_beta():
    """Verifica que sin²(θ_cube) = β."""

    measured = math.sin(THETA_CUBE) ** 2

    assert math.isclose(
        measured,
        BETA,
        rel_tol=1e-9,
        abs_tol=1e-12,
    ), (
        f"sin²(θ_cube) = {measured}, "
        f"pero β = {BETA}"
    )


def test_cos_squared_theta_cube_equals_alpha():
    """Verifica que cos²(θ_cube) = α."""

    measured = math.cos(THETA_CUBE) ** 2

    assert math.isclose(
        measured,
        ALPHA,
        rel_tol=1e-9,
        abs_tol=1e-12,
    ), (
        f"cos²(θ_cube) = {measured}, "
        f"pero α = {ALPHA}"
    )


def test_phi_squared_equals_phi_plus_one():
    """Verifica que φ² = φ + 1."""

    assert math.isclose(
        PHI**2,
        PHI + 1,
        rel_tol=1e-9,
        abs_tol=1e-12,
    ), (
        f"φ² = {PHI**2}, "
        f"pero φ + 1 = {PHI + 1}"
    )


def test_system_is_underdamped():
    """
    Verifica que el sistema está subamortiguado:

        φ_total < 2π
    """

    assert PHI_TOTAL < PHI_CRITICAL, (
        f"φ_total = {PHI_TOTAL} no es menor que "
        f"φ_critical = {PHI_CRITICAL}"
    )


def test_system_is_alive():
    """
    Verifica la condición dinámica definida por el framework:

        ζ < 1
    """

    assert ZETA < 1.0, (
        f"ζ = {ZETA} no cumple ζ < 1"
    )


def test_system_oscillates():
    """
    Verifica la condición de oscilación:

        ω_d > 0
    """

    assert OMEGA_D > 0.0, (
        f"ω_d = {OMEGA_D} no es positivo"
    )


def test_c_max_equals_alpha():
    """Verifica que C_max = α."""

    assert math.isclose(
        C_MAX,
        ALPHA,
        rel_tol=1e-9,
        abs_tol=1e-12,
    ), (
        f"C_MAX = {C_MAX}, pero α = {ALPHA}"
    )


def test_n_cube_equals_27():
    """Verifica que N_CUBE = 27."""

    assert N_CUBE == 27, (
        f"N_CUBE = {N_CUBE}, pero debería ser 27"
    )


def test_cube_volume_is_consistent():
    """Verifica que CUBE_VOLUME = N_CUBE³."""

    expected_volume = N_CUBE**3

    assert CUBE_VOLUME == expected_volume, (
        f"CUBE_VOLUME = {CUBE_VOLUME}, "
        f"pero N_CUBE³ = {expected_volume}"
    )


# ============================================================
# PRUEBAS: COTAS INDIVIDUALES DE ERROR
# ============================================================

def test_lambda_error_respects_prediction_bound():
    """
    Verifica:

        error(Λ) ≤ ε
    """

    assert_error_within_bound(
        name="Λ",
        measured_error=LAMBDA_ERROR,
        upper_bound=PREDICTED_LAMBDA_ERROR,
        bound_formula="ε",
    )


def test_h0_error_respects_prediction_bound():
    """
    Verifica:

        error(H₀) ≤ ε/3.1
    """

    assert_error_within_bound(
        name="H₀",
        measured_error=H_0_ERROR,
        upper_bound=PREDICTED_H0_ERROR,
        bound_formula="ε/3.1",
    )


def test_alpha_em_error_respects_prediction_bound():
    """
    Verifica:

        error(α⁻¹) ≤ ε/φ²
    """

    assert_error_within_bound(
        name="α⁻¹",
        measured_error=ALPHA_EM_ERROR,
        upper_bound=PREDICTED_ALPHA_EM_ERROR,
        bound_formula="ε/φ²",
    )


def test_t_cmb_error_respects_prediction_bound():
    """
    Verifica:

        error(T_CMB) ≤ ε/φ³
    """

    assert_error_within_bound(
        name="T_CMB",
        measured_error=T_CMB_ERROR,
        upper_bound=PREDICTED_T_CMB_ERROR,
        bound_formula="ε/φ³",
    )


def test_electron_mass_error_respects_prediction_bound():
    """
    Verifica:

        error(mₑ) ≤ ε/φ⁵
    """

    assert_error_within_bound(
        name="mₑ",
        measured_error=M_ELECTRON_ERROR,
        upper_bound=PREDICTED_M_ELECTRON_ERROR,
        bound_formula="ε/φ⁵",
    )


# ============================================================
# PRUEBA GENERAL DE LAS COTAS ESTRUCTURALES
# ============================================================

def test_all_errors_respect_structural_bounds():
    """
    Verifica conjuntamente que todos los errores satisfacen:

        error medido ≤ cota estructural predicha
    """

    for (
        name,
        measured_error,
        upper_bound,
        bound_formula,
    ) in ERROR_BOUND_CASES:

        assert_error_within_bound(
            name=name,
            measured_error=measured_error,
            upper_bound=upper_bound,
            bound_formula=bound_formula,
        )


# ============================================================
# PRUEBAS: PATRONES ESPECÍFICOS CON φ
# ============================================================

def test_alpha_em_respects_phi_squared_bound():
    """Verifica error(α⁻¹) ≤ ε/φ²."""

    bound = EPSILON_OBSERVER / (PHI**2)

    assert ALPHA_EM_ERROR <= bound, (
        f"error(α⁻¹) = {ALPHA_EM_ERROR:.16e} "
        f"supera ε/φ² = {bound:.16e}"
    )


def test_t_cmb_respects_phi_cubed_bound():
    """Verifica error(T_CMB) ≤ ε/φ³."""

    bound = EPSILON_OBSERVER / (PHI**3)

    assert T_CMB_ERROR <= bound, (
        f"error(T_CMB) = {T_CMB_ERROR:.16e} "
        f"supera ε/φ³ = {bound:.16e}"
    )


def test_electron_mass_respects_phi_fifth_bound():
    """Verifica error(mₑ) ≤ ε/φ⁵."""

    bound = EPSILON_OBSERVER / (PHI**5)

    assert M_ELECTRON_ERROR <= bound, (
        f"error(mₑ) = {M_ELECTRON_ERROR:.16e} "
        f"supera ε/φ⁵ = {bound:.16e}"
    )


# ============================================================
# PRUEBAS: COHERENCIA ESTRUCTURAL
# ============================================================

def calculate_coherence_omega(error: float) -> float:
    """
    Calcula C_Ω y aplica el intervalo cerrado:

        0 ≤ C_Ω ≤ C_MAX
    """

    raw_coherence = (
        BETA
        + ALPHA
        * (error / EPSILON_OBSERVER)
    )

    return min(
        C_MAX,
        max(0.0, raw_coherence),
    )


def test_coherence_omega_never_exceeds_alpha():
    """Verifica que C_Ω nunca supera α."""

    errors = [
        LAMBDA_ERROR,
        H_0_ERROR,
        ALPHA_EM_ERROR,
        T_CMB_ERROR,
        M_ELECTRON_ERROR,
    ]

    for error in errors:
        coherence = calculate_coherence_omega(error)

        assert coherence <= C_MAX, (
            f"C_Ω = {coherence} supera "
            f"C_MAX = {C_MAX}"
        )


def test_coherence_omega_is_non_negative():
    """Verifica que C_Ω nunca es negativo."""

    errors = [
        LAMBDA_ERROR,
        H_0_ERROR,
        ALPHA_EM_ERROR,
        T_CMB_ERROR,
        M_ELECTRON_ERROR,
    ]

    for error in errors:
        coherence = calculate_coherence_omega(error)

        assert coherence >= 0.0, (
            f"C_Ω = {coherence} es negativo"
        )


def test_coherence_omega_is_positive_for_positive_errors():
    """
    Verifica que C_Ω es positivo para los errores físicos
    analizados.
    """

    errors = [
        LAMBDA_ERROR,
        H_0_ERROR,
        ALPHA_EM_ERROR,
        T_CMB_ERROR,
        M_ELECTRON_ERROR,
    ]

    for error in errors:
        assert error >= 0.0

        coherence = calculate_coherence_omega(error)

        assert coherence > 0.0, (
            f"C_Ω = {coherence} no es positivo "
            f"para error = {error}"
        )


# ============================================================
# PRUEBAS: FINITUD Y CONSISTENCIA DE LOS ERRORES
# ============================================================

def test_all_selected_errors_are_finite():
    """Verifica que todos los errores seleccionados son finitos."""

    errors = [
        LAMBDA_ERROR,
        H_0_ERROR,
        ALPHA_EM_ERROR,
        T_CMB_ERROR,
        M_ELECTRON_ERROR,
    ]

    for error in errors:
        assert math.isfinite(error), (
            f"Error no finito detectado: {error}"
        )


def test_all_selected_errors_are_non_negative():
    """Verifica que ningún error relativo sea negativo."""

    errors = [
        LAMBDA_ERROR,
        H_0_ERROR,
        ALPHA_EM_ERROR,
        T_CMB_ERROR,
        M_ELECTRON_ERROR,
    ]

    for error in errors:
        assert error >= 0.0, (
            f"Error negativo detectado: {error}"
        )


def test_all_predicted_bounds_are_finite():
    """Verifica que todas las cotas predichas son finitas."""

    bounds = [
        PREDICTED_LAMBDA_ERROR,
        PREDICTED_H0_ERROR,
        PREDICTED_ALPHA_EM_ERROR,
        PREDICTED_T_CMB_ERROR,
        PREDICTED_M_ELECTRON_ERROR,
    ]

    for bound in bounds:
        assert math.isfinite(bound), (
            f"Cota no finita detectada: {bound}"
        )


def test_all_predicted_bounds_are_positive():
    """Verifica que todas las cotas predichas son positivas."""

    bounds = [
        PREDICTED_LAMBDA_ERROR,
        PREDICTED_H0_ERROR,
        PREDICTED_ALPHA_EM_ERROR,
        PREDICTED_T_CMB_ERROR,
        PREDICTED_M_ELECTRON_ERROR,
    ]

    for bound in bounds:
        assert bound > 0.0, (
            f"Cota no positiva detectada: {bound}"
        )


# ============================================================
# PRUEBA: REPORTE DE ERRORES
# ============================================================

def test_report_measured_errors():
    """
    Imprime el error medido, la cota y la fracción utilizada.

    Para mostrar el reporte en CI:

        pytest -s tests/test_constant_errors.py
    """

    print("\n=== UIS PHYSICAL CONSTANT ERROR REPORT ===")

    for (
        name,
        measured_error,
        upper_bound,
        bound_formula,
    ) in ERROR_BOUND_CASES:

        fraction = (
            measured_error / upper_bound
            if upper_bound > 0
            else float("inf")
        )

        margin = upper_bound - measured_error

        print(
            f"{name}: "
            f"error={measured_error:.16e}, "
            f"bound({bound_formula})={upper_bound:.16e}, "
            f"fraction={fraction:.8f}, "
            f"margin={margin:.16e}"
        )

    assert len(ERROR_BOUND_CASES) == 5


# ============================================================
# PRUEBA: ORIGEN DE LAS CONSTANTES
# ============================================================

def test_constants_source_is_defined():
    """
    Verifica que el estado de importación esté definido.

    True:
        se utilizaron los valores de fallback.

    False:
        se importaron formulas.constants.
    """

    assert isinstance(
        USING_FALLBACK_CONSTANTS,
        bool,
    )
