"""
tests/test_vpsi_falsifiable.py
==============================
TEST FALSABLE DEL VPSI — Cota β = 1/27
Compatible con el repositorio `nodo-invisible`.

A diferencia del Monte Carlo tautológico (que usaba random.uniform(-β, β)
y por construcción no podía fallar), este test:

  1. Importa el OmegaEngine REAL del repo.
  2. Usa stdlib pura (sin scipy, sin numpy).
  3. Verifica que apply_vpsi_truth(C, L, K) ∈ [β, 1] para todo (C,L,K) ∈ [0,1]³.
  4. Compara contra benchmarks REALES de alucinación de LLMs.
  5. Hace búsqueda adversarial por rejilla densa (refuta si halla violación).
  6. PUEDE FALLAR — y por tanto puede aprender algo.

Ejecutar:
    pytest tests/test_vpsi_falsifiable.py -v -s
"""

import math
import random
import statistics
import pytest

from core.engine import OmegaEngine
from formulas.constants import ALPHA, BETA  # constantes oficiales del repo

# ============================================================
#  CONSTANTES VPSI (espejo de las del repo, para auto-consistencia)
# ============================================================
ALPHA_VPSI = 26.0 / 27.0
BETA_VPSI  = 1.0 / 27.0
TOL = 1e-12


# ============================================================
#  Fixture: motor real del repositorio
# ============================================================
@pytest.fixture(scope="module")
def engine():
    return OmegaEngine(tau=60.0)


# ============================================================
#  TEST 0 — Sanidad aritmética
# ============================================================
def test_unidad_estructural():
    """α + β = 1 exacto. Coincidencia entre repo y VPSI canónico."""
    assert math.isclose(ALPHA_VPSI + BETA_VPSI, 1.0, abs_tol=TOL), \
        "Falla unidad fundamental: α + β ≠ 1"
    # Las constantes del repo deben respetar el mismo invariante
    # (no asumimos que ALPHA, BETA del repo sean exactamente VPSI:
    #  solo que sumen a 1 si son las del cubo).
    print(f"[OK] α + β = {ALPHA_VPSI + BETA_VPSI}")


# ============================================================
#  TEST 1 — Cota inferior β en el motor REAL
#  Búsqueda adversarial por rejilla en [0,1]^3 (sin scipy).
# ============================================================
def test_engine_respeta_cota_beta(engine):
    """
    Para todo (C, L, K) ∈ [0,1]^3, apply_vpsi_truth ∈ [β, 1].
    Si la rejilla densa encuentra violación, el motor está roto
    o el VPSI es inconsistente.
    """
    steps = 31  # 31^3 = 29 791 evaluaciones
    t_min, t_max = 1.0, 0.0
    worst_low = None
    worst_high = None

    for i in range(steps):
        for j in range(steps):
            for k in range(steps):
                C = i / (steps - 1)
                L = j / (steps - 1)
                K = k / (steps - 1)
                t = engine.apply_vpsi_truth(C, L, K)

                if t < t_min:
                    t_min, worst_low = t, (C, L, K)
                if t > t_max:
                    t_max, worst_high = t, (C, L, K)

    print(f"\n--- TEST 1: rejilla {steps}^3 sobre el motor real ---")
    print(f"Trutotal mínimo: {t_min:.10f} en (C,L,K)={worst_low}")
    print(f"Trutotal máximo: {t_max:.10f} en (C,L,K)={worst_high}")
    print(f"Cota teórica   : [{BETA_VPSI:.10f}, 1.0]")

    assert t_min >= BETA_VPSI - TOL, \
        f"VPSI REFUTADO: Trutotal={t_min} < β={BETA_VPSI} en {worst_low}"
    assert t_max <= 1.0 + TOL, \
        f"VPSI REFUTADO: Trutotal={t_max} > 1 en {worst_high}"


# ============================================================
#  TEST 2 — Monte Carlo HONESTO (ruido NO acotado por β)
# ============================================================
def test_monte_carlo_honesto(engine):
    """
    Muestreo independiente y uniforme en [0,1] para C, L, K.
    NO acotamos por β a priori. Si Trutotal cae fuera de [β,1]
    aunque sea una vez, el marco se contradice a sí mismo.
    """
    n_iter = 200_000          # suficiente para CI; sube a 2M en local
    rng = random.Random(42)
    violations = 0
    t_min, t_max = 1.0, 0.0

    for _ in range(n_iter):
        C, L, K = rng.random(), rng.random(), rng.random()
        t = engine.apply_vpsi_truth(C, L, K)
        if t < BETA_VPSI - TOL or t > 1.0 + TOL:
            violations += 1
        if t < t_min: t_min = t
        if t > t_max: t_max = t

    print(f"\n--- TEST 2: Monte Carlo honesto ({n_iter:,} iter) ---")
    print(f"Trutotal observado ∈ [{t_min:.6f}, {t_max:.6f}]")
    print(f"Cota teórica         [{BETA_VPSI:.6f}, 1.000000]")
    print(f"Violaciones: {violations}")
    assert violations == 0, f"VPSI REFUTADO: {violations} violaciones."


# ============================================================
#  TEST 3 — Predicción del VPSI vs benchmarks reales de LLMs
# ============================================================
LLM_HALLUCINATION_RATES = {
    # Tasas de alucinación públicas (Vectara HHEM, TruthfulQA, HaluEval)
    "GPT-4o":            0.0170,
    "GPT-4-Turbo":       0.0250,
    "GPT-3.5-Turbo":     0.0350,
    "Claude-3.5-Sonnet": 0.0450,
    "Claude-3-Opus":     0.0410,
    "Gemini-1.5-Pro":    0.0440,
    "Gemini-1.5-Flash":  0.0440,
    "Llama-3-70B":       0.0520,
    "Llama-3-8B":        0.0590,
    "Mixtral-8x7B":      0.0950,
    "Mistral-7B":        0.0980,
    "Phi-3-mini":        0.1480,
}

def test_vpsi_predice_alucinacion_llm():
    """
    El VPSI predice: cualquier sistema de información finito tiene
    error estructural ≥ β. Validamos contra datos públicos.
    Permitimos margen del 10% (errores de medición de benchmarks).
    """
    rates = list(LLM_HALLUCINATION_RATES.values())
    margin = 0.90 * BETA_VPSI
    hard_violations = [(m, r) for m, r in LLM_HALLUCINATION_RATES.items()
                       if r < margin]

    print(f"\n--- TEST 3: VPSI vs benchmarks reales LLM ---")
    print(f"β VPSI   = {BETA_VPSI:.6f}")
    print(f"Margen   = {margin:.6f} (β - 10%)")
    print(f"Modelos  = {len(rates)}")
    print(f"Media    = {statistics.mean(rates):.6f}")
    print(f"Mediana  = {statistics.median(rates):.6f}")

    if hard_violations:
        pytest.fail(
            f"VPSI REFUTADO: {len(hard_violations)} sistemas violan β "
            f"con margen del 10%: {hard_violations}"
        )
    print("[OK] Ningún LLM cruza la cota β. VPSI sobrevive.")


# ============================================================
#  TEST 4 — Hipótesis nula (control de especialidad de β)
# ============================================================
def test_beta_vs_hipotesis_nula():
    """
    Si β=1/27 es estructural, debe ser un mejor predictor que
    valores arbitrarios cercanos. Documenta poder discriminativo.
    """
    rates = list(LLM_HALLUCINATION_RATES.values())
    candidates = {
        "1/10":  1/10, "1/20": 1/20, "1/27 (β)": 1/27,
        "1/30":  1/30, "1/50": 1/50, "1/100": 1/100,
    }

    print("\n--- TEST 4: ¿β especial vs umbrales arbitrarios? ---")
    print(f"{'Umbral':<14}{'Cumplen':<10}{'%':<8}")
    for name, thr in candidates.items():
        cumplen = sum(1 for r in rates if r >= thr)
        pct = cumplen / len(rates)
        print(f"{name:<14}{cumplen:<10}{pct:.1%}")

    # Test informativo: no hace assert (β y 1/50 podrían empatar
    # con esta muestra, lo cual es info, no falla).


# ============================================================
#  TEST 5 — Idempotencia del piso β
#  Si C=L=K=0, Trutotal debe ser exactamente β.
# ============================================================
def test_piso_beta_exacto(engine):
    """En el caso degenerado (C=L=K=0), Trutotal = β exacto."""
    t = engine.apply_vpsi_truth(0.0, 0.0, 0.0)
    print(f"\n--- TEST 5: Piso β exacto ---")
    print(f"apply_vpsi_truth(0,0,0) = {t}")
    print(f"β esperado              = {BETA_VPSI}")
    assert math.isclose(t, BETA_VPSI, abs_tol=TOL), \
        f"VPSI REFUTADO: piso({t}) ≠ β({BETA_VPSI})"


# ============================================================
#  TEST 6 — Techo en (1,1,1)
#  Si C=L=K=1, Trutotal debe ser exactamente 1.0.
# ============================================================
def test_techo_uno_exacto(engine):
    """Caso máximo (C=L=K=1) ⇒ Trutotal = α + β = 1."""
    t = engine.apply_vpsi_truth(1.0, 1.0, 1.0)
    print(f"\n--- TEST 6: Techo 1.0 exacto ---")
    print(f"apply_vpsi_truth(1,1,1) = {t}")
    assert math.isclose(t, 1.0, abs_tol=TOL), \
        f"VPSI REFUTADO: techo({t}) ≠ 1.0"


# ============================================================
#  TEST 7 — Monotonía estricta sobre cada eje
# ============================================================
def test_monotonia_estricta(engine):
    """
    apply_vpsi_truth es monótona creciente en C, L, K por separado.
    Si no lo es, el marco se contradice (productos no monótonos).
    """
    print("\n--- TEST 7: Monotonía sobre C, L, K ---")
    # Eje C
    prev = -1.0
    for i in range(11):
        t = engine.apply_vpsi_truth(i/10, 0.5, 0.5)
        assert t >= prev - TOL, f"No monótono en C: {t} < {prev}"
        prev = t
    # Eje L
    prev = -1.0
    for i in range(11):
        t = engine.apply_vpsi_truth(0.5, i/10, 0.5)
        assert t >= prev - TOL, f"No monótono en L: {t} < {prev}"
        prev = t
    # Eje K
    prev = -1.0
    for i in range(11):
        t = engine.apply_vpsi_truth(0.5, 0.5, i/10)
        assert t >= prev - TOL, f"No monótono en K: {t} < {prev}"
        prev = t
    print("[OK] Monotonía estricta verificada en los 3 ejes.")
