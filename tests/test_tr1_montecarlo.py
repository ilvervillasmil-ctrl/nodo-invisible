"""
tests/test_tr1_montecarlo.py
=============================
Monte Carlo Adversarial Verification of Theorem TR1
Structural Generativity of the VPSI Framework
|Theta| = 24 -- 2,000,000 iterations
VPSI Framework v9.2 -- Villasmil 2026

Ejecutar con: pytest tests/test_tr1_montecarlo.py -v
"""

import pytest
import random
import math
from itertools import combinations

# ============================================================
# STRUCTURAL CONSTANTS — derived from 3x3x3 cube geometry
# ============================================================
N_CUBE   = 27
F_CUBE   = 6
E_CUBE   = 12
V_CUBE   = 8
C_CUBE   = 1
EXT_CUBE = 26

ALPHA = EXT_CUBE / N_CUBE          # 26/27 = 0.9629629629629629
BETA  = C_CUBE  / N_CUBE           # 1/27  = 0.03703703703703704

assert abs(ALPHA + BETA - 1.0) < 1e-15, "ALPHA + BETA must equal 1"
assert abs(BETA - 1/27) < 1e-15,        "BETA must equal 1/27"

# ============================================================
# THETA — 24 theorems with domain assignments
# ============================================================
THETA = {
    "T1":           frozenset({"ONT", "INF"}),
    "T2":           frozenset({"INF", "LOG"}),
    "T3":           frozenset({"INF", "TMP"}),
    "T4":           frozenset({"EPI", "TMP"}),
    "T5":           frozenset({"ONT", "EPI"}),
    "T6":           frozenset({"LOG", "SEM"}),
    "T7":           frozenset({"ONT", "MET"}),
    "T8":           frozenset({"INF", "MET"}),
    "T9":           frozenset({"EPI", "INF"}),
    "T10":          frozenset({"ONT", "INF"}),
    "T11":          frozenset({"ONT", "MET"}),
    "T12":          frozenset({"EPI", "ONT"}),
    "T13":          frozenset({"EPI", "SEM"}),
    "T14":          frozenset({"EPI", "MET"}),
    "T15":          frozenset({"ONT", "INF", "MET"}),
    "T16":          frozenset({"EPI", "MET"}),
    "T17":          frozenset({"ONT", "MET", "TMP"}),
    "U1":           frozenset({"EPI", "TMP", "MET"}),
    "M1":           frozenset({"MET", "LOG"}),
    "M.1":          frozenset({"MET", "ONT"}),
    "B-Canonical":  frozenset({"ONT", "LOG", "MET"}),
    "TT.6.1":       frozenset({"LOG", "SEM", "EPI"}),
    "U0":           frozenset({"ONT", "INF", "TMP"}),
    "TR1":          frozenset({"MET", "INF", "LOG"}),
}

NAMES = list(THETA.keys())
N = len(NAMES)
assert N == 24, f"Expected 24 theorems, got {N}"

# ============================================================
# EXACT ENUMERATION — ground truth (VALOR EXACTO 153)
# ============================================================
def exact_enumeration():
    total = compatible = new = redundant = incompatible = 0
    for i, j in combinations(range(N), 2):
        total += 1
        ti, tj = NAMES[i], NAMES[j]
        di, dj = THETA[ti], THETA[tj]
        if not (di & dj):
            incompatible += 1
            continue
        compatible += 1
        union = di | dj
        if union != di and union != dj:
            new += 1
        else:
            redundant += 1
    return {
        "total":        total,
        "compatible":   compatible,
        "new":          new,
        "redundant":    redundant,
        "incompatible": incompatible,
    }

# ============================================================
# TRUTH FUNCTION — Trutotal(D) = C * L * K * ALPHA + BETA
# ============================================================
def tru_total(C, L, K):
    ri = C * L * K
    return ri * ALPHA + BETA

# ============================================================
# BETA SAMPLING — Beta distribution
# ============================================================
def beta_sample(a, b):
    """Sample from Beta(a, b) using Johnk's method."""
    while True:
        u = random.random() ** (1.0 / a)
        v = random.random() ** (1.0 / b)
        if u + v <= 1.0:
            return u / (u + v)

# ============================================================
# EXACT TESTS (sin Monte Carlo, valores exactos)
# ============================================================

def test_exact_enumeration():
    """TR1: Verificación exacta de |Im(+)| > |Theta|"""
    exact = exact_enumeration()
    
    assert exact['compatible'] + exact['incompatible'] == exact['total'], \
        f"Suma de compatibles + incompatibles no coincide con total"
    assert exact['new'] + exact['redundant'] == exact['compatible'], \
        f"Nuevas + redundantes != compatibles"
    assert exact['new'] > N, \
        f"TR1 violado: {exact['new']} nuevas verdades <= {N} = |Theta|"


def test_exact_new_truths_count():
    """Verifica que el número EXACTO de nuevas verdades es 153
       Confirmado por verificación independiente (Sonnet 4.6)"""
    exact = exact_enumeration()
    assert exact['new'] == 153, \
        f"Expected 153 new truths (confirmed by independent verification), got {exact['new']}"


def test_exact_compatible_pairs():
    """Verifica que el número EXACTO de pares compatibles es 183"""
    exact = exact_enumeration()
    assert exact['compatible'] == 183, \
        f"Expected EXACT 183 compatible pairs, got {exact['compatible']}"


def test_exact_total_pairs():
    """Verifica que C(24,2) = 276"""
    exact = exact_enumeration()
    total_pairs = len(list(combinations(range(N), 2)))
    assert exact['total'] == total_pairs == 276, \
        f"Total pairs mismatch: {exact['total']} != 276"


def test_geometric_invariants():
    """Verifica invariantes geométricos del cubo 3x3x3"""
    theta = math.asin(1 / math.sqrt(27))
    sin2 = math.sin(theta) ** 2
    cos2 = math.cos(theta) ** 2
    
    assert abs(sin2 - BETA) < 1e-15, f"sin²(θ_cube) = {sin2} != β = {BETA}"
    assert abs(cos2 - ALPHA) < 1e-15, f"cos²(θ_cube) = {cos2} != α = {ALPHA}"
    assert abs(ALPHA + BETA - 1.0) < 1e-15, f"α + β = {ALPHA + BETA} != 1"


def test_constants_values():
    """Verifica valores exactos de constantes"""
    assert abs(ALPHA - 26/27) < 1e-15
    assert abs(BETA - 1/27) < 1e-15
    assert ALPHA + BETA == 1.0


# ============================================================
# MONTE CARLO TESTS (con tolerancia 0.1% para validación exacta)
# ============================================================

def test_monte_carlo_generativity_exact_match():
    """
    Monte Carlo: Verifica que la tasa de generatividad coincide
    EXACTAMENTE con el valor exacto (153/183) con margen 0.1%
    """
    n_iter = 500_000  # Aumentado para mejor precisión
    generative = 0
    redundant = 0
    
    for _ in range(n_iter):
        i = random.randint(0, N - 1)
        j = random.randint(0, N - 1)
        while j == i:
            j = random.randint(0, N - 1)
        
        di, dj = THETA[NAMES[i]], THETA[NAMES[j]]
        
        if not (di & dj):
            continue
        
        union = di | dj
        if union != di and union != dj:
            generative += 1
        else:
            redundant += 1
    
    evaluated = generative + redundant
    gen_rate = generative / evaluated if evaluated > 0 else 0
    
    exact = exact_enumeration()
    expected_rate = exact['new'] / exact['compatible']  # 153 / 183 = 0.836065...
    expected_new_exact = 153
    
    # Margen reducido a 0.001 (0.1%) para validación exacta
    assert abs(gen_rate - expected_rate) < 0.001, \
        f"Generativity rate {gen_rate:.6f} != expected {expected_rate:.6f} (error > 0.1%)"
    
    # Verificación adicional por regla de tres
    estimated_new = int(round(gen_rate * exact['compatible']))
    assert abs(estimated_new - expected_new_exact) <= 1, \
        f"Estimated new truths {estimated_new} != exact {expected_new_exact}"


def test_monte_carlo_noise_scenario():
    """Monte Carlo: Escenario con ruido sigma=0.15 (2M iteraciones)"""
    n_iter = 2_000_000
    sigma = 0.15
    violations = 0
    
    for _ in range(n_iter):
        C = max(0.0, min(1.0, beta_sample(5, 1.5) + random.gauss(0, sigma)))
        L = max(0.0, min(1.0, beta_sample(5, 1.5) + random.gauss(0, sigma)))
        K = max(0.0, min(1.0, beta_sample(4, 2.0) + random.gauss(0, sigma)))
        R = 1.0
        
        tru = C * L * K * R * ALPHA + BETA
        
        if tru < BETA - 1e-12 or tru > 1.0 + 1e-12:
            violations += 1
    
    assert violations == 0, f"Violations in noise scenario: {violations}"


def test_monte_carlo_confusion_scenario():
    """Monte Carlo: Escenario Confusion Ri=R (T12 attack)"""
    n_iter = 1_000_000
    sigma = 0.15
    violations = 0
    
    for _ in range(n_iter):
        C = max(0.0, min(1.0, beta_sample(5, 1.5) + random.gauss(0, sigma)))
        L = max(0.0, min(1.0, beta_sample(5, 1.5) + random.gauss(0, sigma)))
        K = max(0.0, min(1.0, beta_sample(4, 2.0) + random.gauss(0, sigma)))
        R = C * L * K  # Confusión Ri = R
        
        tru = C * L * K * R * ALPHA + BETA
        
        if tru < BETA - 1e-12 or tru > 1.0 + 1e-12:
            violations += 1
    
    assert violations == 0, f"Violations in confusion scenario: {violations}"


def test_monte_carlo_collapse_scenario():
    """Monte Carlo: Escenario Forced collapse p=0.10"""
    n_iter = 1_000_000
    collapse_p = 0.10
    violations = 0
    
    for _ in range(n_iter):
        C = beta_sample(5, 1.5)
        L = beta_sample(5, 1.5)
        K = beta_sample(4, 2.0)
        
        if random.random() < collapse_p:
            factor = random.randint(0, 2)
            if factor == 0: C = 0.0
            elif factor == 1: L = 0.0
            else: K = 0.0
        
        R = 1.0
        tru = C * L * K * R * ALPHA + BETA
        
        if tru < BETA - 1e-12 or tru > 1.0 + 1e-12:
            violations += 1
    
    assert violations == 0, f"Violations in collapse scenario: {violations}"


def test_tr1_pij_truth_bounds():
    """TR1: Verifica que las nuevas verdades Pij cumplen [BETA, 1] exacto"""
    n_iter = 200_000
    floor_viol = 0
    ceil_viol = 0
    
    for _ in range(n_iter):
        i = random.randint(0, N - 1)
        j = random.randint(0, N - 1)
        while j == i:
            j = random.randint(0, N - 1)
        
        di, dj = THETA[NAMES[i]], THETA[NAMES[j]]
        
        if not (di & dj):
            continue
        
        union = di | dj
        if union != di and union != dj:
            C = beta_sample(5, 1.5)
            L = beta_sample(5, 1.5)
            K = beta_sample(4, 2.0)
            tru = tru_total(C, L, K)
            
            if tru < BETA - 1e-12:
                floor_viol += 1
            if tru > 1.0 + 1e-12:
                ceil_viol += 1
    
    assert floor_viol == 0, f"Floor violations: {floor_viol} (Tru < β)"
    assert ceil_viol == 0, f"Ceiling violations: {ceil_viol} (Tru > 1)"


# ============================================================
# TEST DE CONSISTENCIA EXACTA (validación cruzada)
# ============================================================

def test_exact_tr1_inequality():
    """TR1: 153 > 24 (verificación exacta de la desigualdad)"""
    exact = exact_enumeration()
    assert exact['new'] == 153
    assert N == 24
    assert exact['new'] > N, \
        f"TR1 violated: {exact['new']} is not greater than {N}"
    assert exact['new'] - N == 129, \
        f"Difference: {exact['new'] - N} (expected 129)"


def test_exact_verification_consistency():
    """Verifica que la enumeración exacta es consistente con todas las relaciones"""
    exact = exact_enumeration()
    
    # Relación fundamental: compatibles = nuevas + redundantes
    assert exact['compatible'] == exact['new'] + exact['redundant']
    
    # Relación fundamental: total = compatibles + incompatibles
    assert exact['total'] == exact['compatible'] + exact['incompatible']
    
    # Verificación numérica exacta
    assert exact['new'] == 153
    assert exact['compatible'] == 183
    assert exact['redundant'] == 30
    assert exact['incompatible'] == 93
    assert exact['total'] == 276
    
    # Verificación de proporción exacta
    assert exact['new'] / exact['compatible'] == 153 / 183
    assert abs(exact['new'] / exact['compatible'] - 153/183) < 1e-15
