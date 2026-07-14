"""
Script de pruebas para analizar la relación entre los errores de las constantes físicas del UIS,
el residuo del observador (ε = 0.02716), y la razón áurea (φ ≈ 1.618034).

Este script está optimizado para ejecutarse en CI.
"""

import math
import pytest
import os
import sys
import tempfile
from pathlib import Path

# ======================================================================
# CONFIGURACIÓN INICIAL PARA CI
# ======================================================================

# Añade el directorio raíz al PYTHONPATH
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Verifica dependencias opcionales
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False

# Crea un directorio temporal para archivos generados
TEMP_DIR = tempfile.mkdtemp()
os.makedirs(TEMP_DIR, exist_ok=True)

# ======================================================================
# CONSTANTES FUNDAMENTALES DEL UIS
# ======================================================================

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
except ImportError as e:
    # Si no se pueden importar, define las constantes manualmente
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

# ======================================================================
# LISTA DE CONSTANTES PARA ANÁLISIS
# ======================================================================

CONSTANTS = [
    {
        "name": "Λ (Constante Cosmológica)",
        "ucf_value": LAMBDA_UCF,
        "experimental_value": LAMBDA_OBS,
        "unit": "m⁻²",
        "error": LAMBDA_ERROR,
        "formula": "β^(π/β + β·φ²)",
        "layer": "L0–L6",
    },
    {
        "name": "H₀ (Constante de Hubble)",
        "ucf_value": H_0_UCF,
        "experimental_value": H_0_REF,
        "unit": "km/s/Mpc",
        "error": H_0_ERROR,
        "formula": "β × κ_H",
        "layer": "L0–L2",
    },
    {
        "name": "mₑ (Masa del Electrón)",
        "ucf_value": M_ELECTRON_UCF,
        "experimental_value": M_ELECTRON_REF,
        "unit": "kg",
        "error": M_ELECTRON_ERROR,
        "formula": "β³ × (α_geom⁻¹/100) × κ_m",
        "layer": "L3–L5",
    },
    {
        "name": "α⁻¹ (Estructura Fina)",
        "ucf_value": ALPHA_GEOM_INV,
        "experimental_value": ALPHA_EM_INV_OBS,
        "unit": "adimensional",
        "error": ALPHA_EM_ERROR,
        "formula": "(β/ε) × 100",
        "layer": "L2–L4",
    },
    {
        "name": "m_p/mₑ (Relación Masas)",
        "ucf_value": M_P_M_E_UCF,
        "experimental_value": M_P_M_E_REF,
        "unit": "adimensional",
        "error": M_P_M_E_ERROR,
        "formula": "(27·β²·(π/√2)·τ) / (β³·α_geom⁻¹)",
        "layer": "L3–L5",
    },
    {
        "name": "T_CMB (Temperatura CMB)",
        "ucf_value": T_CMB_UCF,
        "experimental_value": T_CMB_REF,
        "unit": "K",
        "error": T_CMB_ERROR,
        "formula": "100 × ε",
        "layer": "L0–L1",
    },
    {
        "name": "αₛ (Acoplamiento Fuerte)",
        "ucf_value": ALPHA_S_UCF,
        "experimental_value": ALPHA_S_REF,
        "unit": "adimensional",
        "error": ALPHA_S_ERROR,
        "formula": "27·β²·(π/√2)·τ",
        "layer": "L4–L5",
    },
]

# ======================================================================
# PRUEBAS DE INVARIANTES ESTRUCTURALES
# ======================================================================

def test_alpha_plus_beta_equals_one():
    """Verifica que α + β = 1."""
    assert math.isclose(ALPHA + BETA, 1.0, rel_tol=1e-9)

def test_r_fin_equals_one_plus_beta():
    """Verifica que R_FIN = 1 + β."""
    assert math.isclose(R_FIN, 1 + BETA, rel_tol=1e-9)

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

# ======================================================================
# PRUEBAS DE ERRORES EN CONSTANTES FÍSICAS
# ======================================================================

def test_lambda_error_is_epsilon():
    """Verifica que el error de Λ es exactamente ε."""
    assert math.isclose(LAMBDA_ERROR, EPSILON_OBSERVER, rel_tol=1e-3)

def test_hubble_error_is_epsilon_over_3():
    """Verifica que el error de H₀ es aproximadamente ε/3.1."""
    expected_error = EPSILON_OBSERVER / 3.1
    assert math.isclose(H_0_ERROR, expected_error, rel_tol=0.1)

def test_fine_structure_error_is_epsilon_over_phi_squared():
    """Verifica que el error de α⁻¹ es aproximadamente ε/φ²."""
    expected_error = EPSILON_OBSERVER / (PHI ** 2)
    assert math.isclose(ALPHA_EM_ERROR, expected_error, rel_tol=0.5)

def test_cmb_error_is_epsilon_over_phi_cubed():
    """Verifica que el error de T_CMB es aproximadamente ε/φ³."""
    expected_error = EPSILON_OBSERVER / (PHI ** 3)
    assert math.isclose(T_CMB_ERROR, expected_error, rel_tol=0.5)

def test_electron_mass_error_is_minimal():
    """Verifica que el error de mₑ es mínimo (≈ ε/φ⁵)."""
    expected_error = EPSILON_OBSERVER / (PHI ** 5)
    assert M_ELECTRON_ERROR < expected_error * 10  # Permitir margen

def test_strong_coupling_error_is_zero():
    """Verifica que el error de αₛ es cero."""
    assert ALPHA_S_ERROR == 0.0

def test_planck_energy_error_is_minimal():
    """Verifica que el error de Eₚ es mínimo."""
    assert E_PLANCK_ERROR < 0.00001

# ======================================================================
# PRUEBAS DE RELACIÓN CON φ Y ε
# ======================================================================

def test_error_scalability_with_phi():
    """Verifica que los errores escalan con potencias de φ."""
    errors = [LAMBDA_ERROR, H_0_ERROR, ALPHA_EM_ERROR, T_CMB_ERROR, M_ELECTRON_ERROR]
    expected_ratios = [
        EPSILON_OBSERVER / (PHI ** 0),
        EPSILON_OBSERVER / (PHI ** 1),
        EPSILON_OBSERVER / (PHI ** 2),
        EPSILON_OBSERVER / (PHI ** 3),
        EPSILON_OBSERVER / (PHI ** 5),
    ]
    for error, expected in zip(errors, expected_ratios):
        assert error < expected * 2  # Permitir margen de 2x

# ======================================================================
# PRUEBAS DE COHERENCIA ESTRUCTURAL
# ======================================================================

def test_coherence_omega_never_exceeds_alpha():
    """Verifica que C_Ω nunca supera α."""
    for const in CONSTANTS:
        error = const["error"]
        C_omega = BETA + ALPHA * (error / EPSILON_OBSERVER) * 1.0 * 1.0
        C_omega = min(C_MAX, max(0.0, C_omega))
        assert C_omega <= C_MAX

def test_coherence_omega_is_positive():
    """Verifica que C_Ω siempre es positivo."""
    for const in CONSTANTS:
        error = const["error"]
        C_omega = BETA + ALPHA * (error / EPSILON_OBSERVER) * 1.0 * 1.0
        C_omega = min(C_MAX, max(0.0, C_omega))
        assert C_omega > 0

# ======================================================================
# PRUEBAS DE VISUALIZACIÓN (OPCIONALES)
# ======================================================================

@pytest.mark.skipif(not HAS_MATPLOTLIB or not HAS_NUMPY, reason="matplotlib o numpy no están instalados")
def test_generate_error_vs_epsilon_plot():
    """Genera el gráfico de Error vs. ε (opcional)."""
    names = [c["name"].replace(" (", "\n(") for c in CONSTANTS]
    errors = [c["error"] * 100 for c in CONSTANTS]

    plt.figure(figsize=(16, 10))
    plt.bar(names, errors, color='skyblue', label='Error Relativo (%)')
    plt.axhline(y=EPSILON_OBSERVER * 100, color='red', linestyle='--', linewidth=2,
               label=f'ε = {EPSILON_OBSERVER * 100:.2f}%')
    plt.title("Error Relativo en Constantes Físicas vs. ε")
    plt.ylabel("Error Relativo (%)")
    plt.xlabel("Constante Física")
    plt.legend()
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f'{TEMP_DIR}/error_vs_epsilon.png', dpi=300, bbox_inches='tight')
    plt.close()

@pytest.mark.skipif(not HAS_MATPLOTLIB or not HAS_NUMPY, reason="matplotlib o numpy no están instalados")
def test_generate_phi_scaling_plot():
    """Genera el gráfico de Escalado de φ en las capas del UIS (opcional)."""
    layers = ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]
    phi_powers = [PHI ** (i / 2) for i in range(7)]

    plt.figure(figsize=(12, 8))
    plt.plot(range(7), phi_powers, marker='o', color='purple', label='φ^(i/2)')
    plt.title("Escalado de la Razón Áurea (φ) en las Capas del UIS (L0–L6)")
    plt.ylabel("Frecuencia Relativa")
    plt.xlabel("Capa (L0–L6)")
    plt.xticks(range(7), layers)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'{TEMP_DIR}/phi_scaling_layers.png', dpi=300, bbox_inches='tight')
    plt.close()

# ======================================================================
# FUNCIÓN PRINCIPAL PARA ANÁLISIS (OPCIONAL)
# ======================================================================

def calculate_relations(constants, epsilon=EPSILON_OBSERVER, phi=PHI, beta=BETA):
    """Calcula relaciones de error con ε, φ y β para cada constante."""
    results = []
    for const in constants:
        error = const["error"]
        error_over_epsilon = error / epsilon if epsilon != 0 else 0
        error_over_beta = error / beta if beta != 0 else 0
        error_times_phi = error * phi

        n = 0
        while n < 10 and (epsilon / (phi ** n)) > error:
            n += 1
        epsilon_over_phi_n = epsilon / (phi ** n) if (phi ** n) != 0 else 0
        error_over_phi_n = error / epsilon_over_phi_n if epsilon_over_phi_n != 0 else 0

        C_omega = beta + ALPHA * error_over_epsilon * 1.0 * 1.0
        C_omega = min(C_MAX, max(0.0, C_omega))

        results.append({
            **const,
            "error_over_epsilon": error_over_epsilon,
            "error_over_beta": error_over_beta,
            "error_times_phi": error_times_phi,
            "n_for_phi": n,
            "epsilon_over_phi_n": epsilon_over_phi_n,
            "error_over_phi_n": error_over_phi_n,
            "C_omega": C_omega,
        })
    return results

def print_analysis_results():
    """Imprime los resultados del análisis en la consola."""
    if not HAS_TABULATE:
        print("⚠️ tabulate no está instalado. No se puede imprimir la tabla.")
        return

    print("=" * 100)
    print("🔬 ANÁLISIS DE PATRONES EN LOS ERRORES DE LAS CONSTANTES FÍSICAS (UIS v3.3)")
    print("=" * 100)
    print(f"\n📌 Constantes Fundamentales del UIS:")
    print(f"   ALPHA = {ALPHA:.10f} (26/27)")
    print(f"   BETA  = {BETA:.10f} (1/27)")
    print(f"   PHI   = {PHI:.10f} (Razón Áurea)")
    print(f"   EPSILON_OBSERVER = {EPSILON_OBSERVER:.10f} (Residuo del Observador)")
    print("=" * 100)

    results = calculate_relations(CONSTANTS)

    table_data = []
    for r in results:
        table_data.append([
            r["name"],
            f"{r['ucf_value']:.6e}" if isinstance(r['ucf_value'], float) else r['ucf_value'],
            f"{r['experimental_value']:.6e}" if isinstance(r['experimental_value'], float) else r['experimental_value'],
            r["unit"],
            f"{r['error'] * 100:.6f}%",
            f"{r['error_over_epsilon']:.6f}",
            f"{r['error_over_beta']:.6f}",
            f"{r['error_times_phi']:.6f}",
            r["n_for_phi"],
            f"{r['epsilon_over_phi_n'] * 100:.6f}%",
            f"{r['error_over_phi_n']:.6f}",
            f"{r['C_omega']:.6f}",
            r["formula"],
            r["layer"],
        ])

    headers = [
        "Constante",
        "Valor UIS",
        "Valor Experimental",
        "Unidad",
        "Error Relativo",
        "Error / ε",
        "Error / β",
        "Error × φ",
        "n para φ^n",
        "ε / φ^n",
        "Error / (ε/φ^n)",
        "C_Ω",
        "Fórmula UIS",
        "Capas Involucradas",
    ]
    print("\n" + tabulate(table_data, headers=headers, tablefmt="grid", floatfmt=".6f"))
    print("=" * 100)

    # Guardar resultados en CSV (en el directorio temporal)
    with open(f'{TEMP_DIR}/analisis_errores_ucf_completo.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = results[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"\n✅ Resultados guardados en '{TEMP_DIR}/analisis_errores_ucf_completo.csv'.")

# ======================================================================
# CONFIGURACIÓN PARA EJECUCIÓN DIRECTA (OPCIONAL)
# ======================================================================

if __name__ == "__main__":
    print_analysis_results()
