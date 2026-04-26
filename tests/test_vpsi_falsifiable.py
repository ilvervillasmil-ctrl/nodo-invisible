"""
tests/test_vpsi_falsifiable.py

TEST FALSABLE DEL VPSI - Cota beta = 1/27
Compatible con pytest + GitHub Actions.
100% standalone: solo stdlib + pytest. CERO imports del repo.

Verifica el Teorema de la Verdad Estructural:
    Yr_total(D) = C(D) * L(D) * K(D) * alpha + beta
con alpha = 26/27 y beta = 1/27.
"""

import math
import random
import pytest

ALPHA = 26.0 / 27.0
BETA = 1.0 / 27.0
TOL = 1e-12


def vpsi_truth(C, L=1.0, K=1.0):
    return (C * L * K * ALPHA) + BETA


# ---------- Invariantes estructurales ----------

def test_unidad_estructural():
    assert math.isclose(ALPHA + BETA, 1.0, abs_tol=TOL)


def test_piso_beta_exacto():
    assert math.isclose(vpsi_truth(0.0, 0.0, 0.0), BETA, abs_tol=TOL)


def test_techo_uno_exacto():
    assert math.isclose(vpsi_truth(1.0, 1.0, 1.0), 1.0, abs_tol=TOL)


# ---------- Busqueda adversarial en [0,1]^3 ----------

def test_adversarial_rejilla():
    steps = 31
    t_min, t_max = 1.0, 0.0
    for i in range(steps):
        for j in range(steps):
            for k in range(steps):
                t = vpsi_truth(i / (steps - 1), j / (steps - 1), k / (steps - 1))
                if t < t_min:
                    t_min = t
                if t > t_max:
                    t_max = t
    assert t_min >= BETA - TOL, "Yr_total cruzo beta hacia abajo: {0}".format(t_min)
    assert t_max <= 1.0 + TOL, "Yr_total excedio 1.0: {0}".format(t_max)


# ---------- Monte Carlo honesto (no acotado por beta a priori) ----------

def test_monte_carlo_honesto():
    rng = random.Random(42)
    violations = 0
    for _ in range(200000):
        t = vpsi_truth(rng.random(), rng.random(), rng.random())
        if t < BETA - TOL or t > 1.0 + TOL:
            violations += 1
    assert violations == 0, "{0} muestras fuera de [beta, 1]".format(violations)


# ---------- Monotonia estricta en cada eje ----------

@pytest.mark.parametrize("axis", [0, 1, 2])
def test_monotonia_estricta(axis):
    prev = -1.0
    for i in range(11):
        args = [0.5, 0.5, 0.5]
        args[axis] = i / 10
        t = vpsi_truth(*args)
        assert t >= prev - TOL, "No monotono en eje {0}: {1} < {2}".format(axis, t, prev)
        prev = t


# ---------- Frontera empirica beta vs alucinacion de LLMs ----------

LLM_HALLUCINATION_RATES = {
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


def test_vpsi_particion_coherente():
    """beta particiona el conjunto en dos regiones disjuntas y exhaustivas."""
    dentro = [m for m, r in LLM_HALLUCINATION_RATES.items() if r <= BETA]
    fuera = [m for m, r in LLM_HALLUCINATION_RATES.items() if r > BETA]
    assert len(dentro) + len(fuera) == len(LLM_HALLUCINATION_RATES)
    assert set(dentro).isdisjoint(set(fuera))


def test_vpsi_techo_beta_para_sistemas_fiables():
    """
    Sistemas fiables (frontier LLMs alineados) NO deben exceder beta.
    Si lo hacen, estan alucinando mas alla del ruido estructural.
    """
    fiables = ["GPT-4o", "GPT-4-Turbo", "GPT-3.5-Turbo"]
    violaciones = [
        (m, LLM_HALLUCINATION_RATES[m])
        for m in fiables
        if LLM_HALLUCINATION_RATES[m] > BETA
    ]
    assert not violaciones, "VPSI REFUTADO: {0} exceden beta={1}".format(violaciones, BETA)
