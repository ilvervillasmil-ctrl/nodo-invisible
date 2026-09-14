import math
from formulas.coherence import CoherenceEngine
from formulas.constants import ALPHA, CODE_ENTROPY, CODE_SATURATION, CODE_INTEGRATED


def test_climate_system_coherence_terminal_entropy():
    """
    Climate System 2026 – Ω Framework

    Verifica que, con el estado de capas estimado para el sistema climático global
    (CO₂ ~429 ppm, fragmentación geopolítica, ciencia fuerte pero policy colapsado),
    la coherencia total cae en la banda de ENTROPÍA TERMINAL (código 0).
    """

    # Activaciones estimadas (L0–L6) para clima global 2026
    activations = [
        0.85,  # L0 Caos: entrada energética alta (sol, ENSO)
        0.65,  # L1 Cuerpo: océanos/criosfera degradados
        0.25,  # L2 Ego: geopolítica saturada
        0.95,  # L3 Mente: ciencia climática muy fuerte
        0.20,  # L4 Self: policy integrada muy baja
        0.40,  # L5 Meta: monitoreo parcial
        0.05,  # L6 Propósito: casi inexistente
    ]

    # Fricciones por capa (L2 ligeramente por encima del rango óptimo)
    frictions = [0.10, 0.02, 0.15, 0.03, 0.01, 0.01, 0.00]

    # Ejecutar análisis completo sin interacción externa explícita
    result = CoherenceEngine.full_analysis(
        activations=activations,
        frictions=frictions,
        rho=1.0,
        delta_t=0.0,
        tau=1.0,
        novelty=5.0,
        sensitivity=5.0,
        external_coherences=None,
        integration=0.3,   # integración baja entre actores
        quality=0.4,       # calidad media de implementación
        complexity=0.8,    # alta complejidad del sistema
        uncertainty=0.4,   # incertidumbre política/geopolítica
    )

    c_beta = result["c_beta"]["c_beta"]
    c_total = result["c_total"]["c_total"]
    code = result["diagnostic_code"]

    # 1) C_beta debe ser muy bajo (producto multiplicativo casi colapsado)
    assert isinstance(c_beta, float)
    assert 0.0 <= c_beta <= 0.1, f"C_beta demasiado alto para clima 2026: {c_beta}"

    # 2) Coherencia total debe estar en banda de Entropía Terminal (< 0.4)
    assert isinstance(c_total, float)
    assert 0.0 <= c_total < 0.4, f"C_total inesperado para clima 2026: {c_total}"

    # 3) Código diagnóstico debe ser ENTROPÍA TERMINAL (0000)
    assert code == CODE_ENTROPY, f"Código diagnóstico inesperado: {code}"

    # 4) No debe estar en bandas de Saturación o Arquitecto Integrado
    assert code != CODE_SATURATION
    assert code != CODE_INTEGRATED
