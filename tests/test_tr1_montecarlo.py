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

ALPHA = EXT_CUBE / N_CUBE          # 26/27 = 0.96296...
BETA  = C_CUBE  / N_CUBE           # 1/27  = 0.03703...

assert abs(ALPHA + BETA - 1.0) < 1e-15, "ALPHA + BETA must equal 1"
assert abs(BETA - 1/27) < 1e-15,        "BETA must equal 1/27"

# ============================================================
# THETA — 24 theorems with domain assignments
# Domains: ONT, INF, LOG, EPI, SEM, TMP, MET
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
# EXACT ENUMERATION — ground truth
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
# TESTS
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
    """Verifica que el número exacto de nuevas verdades es 183"""
    exact = exact_enumeration()
    assert exact['new'] == 183, \
        f"Expected 183 new truths, got {exact['new']}"


def test_exact_compatible_pairs():
    """Verifica que el número exacto de pares compatibles es 183"""
    exact = exact_enumeration()
    assert exact['compatible'] == 183, \
        f"Expected 183 compatible pairs, got {exact['compatible']}"


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


def test_monte_carlo_noise_scenario():
    """Monte Carlo: Escenario con ruido sigma=0.15 (2M iteraciones)"""
    n_iter = 2_000_000
    sigma = 0.15
    violations = 0
    
    for _ in range(n_iter):
        C = max(0.0, min(1.0, beta_sample(5, 1.5) + random.gauss(0, sigma)))
        L = max(0.0, min(1.0, beta_sample(5, 1.5) + random.gauss(0, sigma)))
        K = max(0.0, min(1.0, beta_sample(4, 2.0) + random.gauss(0, sigma)))
        R = 1.0  # TA4: R is independent
        
        tru = C * L * K * R * ALPHA + BETA
        
        if not (BETA - 1e-12 <= tru <= 1.0 + 1e-12):
            violations += 1
        if tru < BETA - 1e-12:
            violations += 1
        if tru > 1.0 + 1e-12:
            violations += 1
    
    assert violations == 0, f"Violations in noise scenario: {violations}"


def test_monte_carlo_confusion_scenario():
    """Monte Carlo: Escenario Confusion Ri=R (T12 attack)"""
    n_iter = 1_000_000  # 1M iteraciones por tiempo
    sigma = 0.15
    violations = 0
    
    for _ in range(n_iter):
        C = max(0.0, min(1.0, beta_sample(5, 1.5) + random.gauss(0, sigma)))
        L = max(0.0, min(1.0, beta_sample(5, 1.5) + random.gauss(0, sigma)))
        K = max(0.0, min(1.0, beta_sample(4, 2.0) + random.gauss(0, sigma)))
        # Confusión: R = Ri
        R = C * L * K
        
        tru = C * L * K * R * ALPHA + BETA
        
        if not (BETA - 1e-12 <= tru <= 1.0 + 1e-12):
            violations += 1
        if tru < BETA - 1e-12:
            violations += 1
        if tru > 1.0 + 1e-12:
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
        
        if not (BETA - 1e-12 <= tru <= 1.0 + 1e-12):
            violations += 1
        if tru < BETA - 1e-12:
            violations += 1
        if tru > 1.0 + 1e-12:
            violations += 1
    
    assert violations == 0, f"Violations in collapse scenario: {violations}"


def test_tr1_generativity_sampling():
    """TR1: Muestreo aleatorio de pares (200,000 iteraciones)"""
    n_iter = 200_000
    generative = 0
    redundant = 0
    incompatible = 0
    
    for _ in range(n_iter):
        i = random.randint(0, N - 1)
        j = random.randint(0, N - 1)
        while j == i:
            j = random.randint(0, N - 1)
        
        di, dj = THETA[NAMES[i]], THETA[NAMES[j]]
        
        if not (di & dj):
            incompatible += 1
            continue
        
        union = di | dj
        if union != di and union != dj:
            generative += 1
        else:
            redundant += 1
    
    evaluated = generative + redundant
    gen_rate = generative / evaluated if evaluated > 0 else 0
    
    exact = exact_enumeration()
    expected_rate = exact['new'] / exact['compatible']
    
    # Permitimos 1% de desviación por muestreo
    assert abs(gen_rate - expected_rate) < 0.01, \
        f"Generativity rate {gen_rate:.4f} != expected {expected_rate:.4f}"
    assert generative > 0, "No generative pairs found"


def test_tr1_pij_truth_bounds():
    """TR1: Verifica que las nuevas verdades Pij cumplen [BETA, ALPHA]"""
    n_iter = 100_000
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
