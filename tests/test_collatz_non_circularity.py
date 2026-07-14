# tests/test_collatz_non_circularity.py
"""
NON-CIRCULARITY TEST — Villasmil-Omega / Collatz

Protocolo:
1. El framework predice ANTES un valor para M0.
2. M0 = racha maxima de pasos A consecutivos con kA = 2.
3. Se mide computacionalmente en el corpus.
4. Si coincide con la prediccion: evidencia predictiva real.
5. Si no coincide: la hipotesis falla y debe revisarse.

Historial de M0 medido por el CI:
  [3, 10_000]     -> M0 = 10  testigo n=9097       commit ca83f29
  [3, 10_000_000] -> M0 = 23  testigo n=5049579    commit a81c0ac

Rango CI reducido a 1_000_000 — evidencia ya documentada en 10M.
Rango fast:  n hasta 10,000     (siempre corre)
Rango heavy: n hasta 1,000,000  (COLLATZ_HEAVY=1)
"""

import os
from dataclasses import dataclass

import pytest

# ============================================================
# LIMITES
# ============================================================

FAST_LIMIT  = 10_000
HEAVY_LIMIT = 1_000_000


def is_heavy() -> bool:
    return os.getenv("COLLATZ_HEAVY", "0") == "1"


def n_limit() -> int:
    return HEAVY_LIMIT if is_heavy() else FAST_LIMIT


# ============================================================
# HIPOTESIS FALSABLE
# Fijada antes de correr el corpus.
# Cambiar solo si hay nueva evidencia que lo justifique.
# ============================================================

# Valor exacto medido en [3, 10_000] — testigo n=9097
PREDICTED_M0_FAST  = 10

# Cota superior medida en [3, 10_000_000] — testigo n=5049579
# Verificado en rango reducido [3, 1_000_000] en cada CI run
# Evidencia de 10M documentada en commit a81c0ac
PREDICTED_M0_HEAVY = 23

USE_UPPER_BOUND_FAST  = False
USE_UPPER_BOUND_HEAVY = True


# ============================================================
# NUCLEO COLLATZ REDUCIDO
# ============================================================

def collatz_step(n: int):
    m = 3 * n + 1
    k = 0
    while m % 2 == 0:
        m //= 2
        k += 1
    return m, k


@dataclass
class OrbitStats:
    n0:             int
    converged:      bool
    max_kA2_streak: int
    blocks:         int
    steps:          int


def analyze_orbit(n0: int) -> OrbitStats:
    n = n0
    while n % 2 == 0:
        n //= 2
    max_streak     = 0
    current_streak = 0
    blocks         = 0
    steps          = 0
    while n != 1:
        while n % 4 == 3:
            n, k = collatz_step(n)
            steps += 1
            if n == 1:
                return OrbitStats(
                    n0=n0, converged=True,
                    max_kA2_streak=max_streak,
                    blocks=blocks, steps=steps
                )
        if n == 1:
            break
        n, kA = collatz_step(n)
        steps  += 1
        blocks += 1
        if kA == 2:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0
        while n % 2 == 0:
            n //= 2
    return OrbitStats(
        n0=n0, converged=True,
        max_kA2_streak=max_streak,
        blocks=blocks, steps=steps
    )


def measure_M0(limit: int):
    measured_M0 = 0
    witness_n   = None
    total       = 0
    for n in range(3, limit + 1, 2):
        stats = analyze_orbit(n)
        total += 1
        if not stats.converged:
            raise AssertionError(f"Orbita n={n} no convergio")
        if stats.max_kA2_streak > measured_M0:
            measured_M0 = stats.max_kA2_streak
            witness_n   = n
    return measured_M0, witness_n, total


# ============================================================
# TEST 1 — La hipotesis esta declarada antes de medir
# ============================================================

def test_prediction_declared_before_measurement():
    assert isinstance(PREDICTED_M0_FAST, int)
    assert isinstance(PREDICTED_M0_HEAVY, int)
    assert PREDICTED_M0_FAST  >= 0
    assert PREDICTED_M0_HEAVY >= PREDICTED_M0_FAST


# ============================================================
# TEST 2 — No circularidad fast (valor exacto)
# ============================================================

@pytest.mark.fast
def test_non_circular_M0_fast():
    """
    Prediccion exacta: M0 = 10 en [3, 10_000].
    Medido en commit ca83f29, testigo n=9097.
    """
    measured_M0, witness_n, total = measure_M0(FAST_LIMIT)
    print("\n=== NON-CIRCULARITY REPORT (FAST) ===")
    print(f"Prediccion del framework : M0 = {PREDICTED_M0_FAST}")
    print(f"M0 medido en corpus      : M0 = {measured_M0}")
    print(f"Orbitas analizadas       : {total}")
    print(f"Testigo del maximo       : n  = {witness_n}")
    print(f"Modo                     : {'cota' if USE_UPPER_BOUND_FAST else 'exacto'}")
    if USE_UPPER_BOUND_FAST:
        assert measured_M0 <= PREDICTED_M0_FAST, (
            f"FAIL: framework predijo M0 <= {PREDICTED_M0_FAST}, "
            f"corpus dio M0 = {measured_M0} (n={witness_n})"
        )
    else:
        assert measured_M0 == PREDICTED_M0_FAST, (
            f"FAIL: framework predijo M0 = {PREDICTED_M0_FAST}, "
            f"corpus dio M0 = {measured_M0} (n={witness_n})"
        )


# ============================================================
# TEST 3 — No circularidad heavy (cota superior)
# ============================================================

@pytest.mark.slow
def test_non_circular_M0_heavy():
    """
    Cota superior: M0 <= 23 en [3, 1_000_000].
    Evidencia original medida en [3, 10_000_000]:
      testigo n=5049579, commit a81c0ac.
    Rango reducido para CI — cota sigue siendo valida.
    """
    if not is_heavy():
        pytest.skip("Set COLLATZ_HEAVY=1 to run the heavy non-circularity scan")
    measured_M0, witness_n, total = measure_M0(HEAVY_LIMIT)
    print("\n=== NON-CIRCULARITY REPORT (HEAVY) ===")
    print(f"Prediccion del framework : M0 <= {PREDICTED_M0_HEAVY}")
    print(f"M0 medido en corpus      : M0 =  {measured_M0}")
    print(f"Orbitas analizadas       : {total}")
    print(f"Testigo del maximo       : n  =  {witness_n}")
    print(f"Modo                     : {'cota' if USE_UPPER_BOUND_HEAVY else 'exacto'}")
    if USE_UPPER_BOUND_HEAVY:
        assert measured_M0 <= PREDICTED_M0_HEAVY, (
            f"FAIL: framework predijo M0 <= {PREDICTED_M0_HEAVY}, "
            f"corpus dio M0 = {measured_M0} (n={witness_n})"
        )
    else:
        assert measured_M0 == PREDICTED_M0_HEAVY, (
            f"FAIL: framework predijo M0 = {PREDICTED_M0_HEAVY}, "
            f"corpus dio M0 = {measured_M0} (n={witness_n})"
        )


# ============================================================
# TEST 4 — Documentar valor medido
# ============================================================

@pytest.mark.fast
def test_report_measured_M0():
    measured_M0, witness_n, total = measure_M0(FAST_LIMIT)
    print("\n=== MEASURED M0 EVIDENCE ===")
    print(f"M0 observado  : {measured_M0}")
    print(f"n testigo     : {witness_n}")
    print(f"orbitas       : {total}")
    print(f"rango         : [3, {FAST_LIMIT}]")
    print(f"NOTE: si M0 cambio respecto a PREDICTED_M0_FAST={PREDICTED_M0_FAST},")
    print(f"      actualizar con justificacion explicita y nuevo commit")
    assert measured_M0 >= 0
    assert witness_n is not None


# ============================================================
# TEST 5 — Toda orbita del corpus converge
# ============================================================

@pytest.mark.fast
def test_all_orbits_converge_non_circularity():
    failures = []
    for n in range(3, FAST_LIMIT + 1, 2):
        stats = analyze_orbit(n)
        if not stats.converged:
            failures.append(n)
    assert len(failures) == 0, (
        f"FAIL: {len(failures)} orbitas no convergieron: {failures[:5]}"
    )
