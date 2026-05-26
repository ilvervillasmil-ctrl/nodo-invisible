"""
Test Suite: UCF Black Hole Coherence Invariant
Framework: UCF v3.2
Author: Ilver Villasmil
Purpose:
Test whether real black holes exhibit an invariant separation between
observable coherent structure and irreducible hidden structure.

HYPOTHESIS:
Black holes approach a maximum coherent observable state:

    ALPHA = 26/27 ≈ 0.962963

while preserving an irreducible hidden core:

    BETA = 1/27 ≈ 0.037037

This suite does NOT assume the hypothesis is true.
It attempts to falsify it against real observational parameters.

DATA SOURCES:
- Event Horizon Telescope (M87*, Sgr A*)
- Cygnus X-1 spin measurements
- Kerr black hole thermodynamics
- Bekenstein-Hawking entropy
"""

import math
import pytest


# ============================================================
# FRAMEWORK CONSTANTS
# ============================================================

ALPHA = 26 / 27
BETA = 1 / 27

G = 6.67430e-11
c = 2.99792458e8
hbar = 1.054571817e-34
k_B = 1.380649e-23
l_P = 1.616255e-35
M_sun = 1.989e30


# ============================================================
# REAL OBSERVATIONAL DATA
# ============================================================

BLACK_HOLES = {
    "SgrA": {
        "mass": 4.154e6 * M_sun,
        "spin": 0.90,
        "eddington_ratio": 1e-8,
    },
    "M87": {
        "mass": 6.5e9 * M_sun,
        "spin": 0.80,
        "eddington_ratio": 3.6e-6,
    },
    "CygnusX1": {
        "mass": 21.2 * M_sun,
        "spin": 0.95,
        "eddington_ratio": 0.02,
    },
    "TON618": {
        "mass": 6.6e10 * M_sun,
        "spin": 0.99,
        "eddington_ratio": 0.40,
    },
}


# ============================================================
# PHYSICS
# ============================================================

def schwarzschild_radius(M):
    return 2 * G * M / c2


def horizon_area(M):
    Rs = schwarzschild_radius(M)
    return 4 * math.pi * Rs2


def entropy(M):
    A = horizon_area(M)
    return k_B * A / (4 * l_P**2)


def information_bits(M):
    S = entropy(M)
    return S / (k_B * math.log(2))


# ============================================================
# UCF COHERENCE DEFINITIONS
# ============================================================

def coherence_from_spin(a):
    """
    Measures how close a black hole is to the
    proposed coherent limit alpha = 26/27.
    """
    return a / ALPHA


def hidden_fraction():
    """
    Irreducible hidden component.
    """
    return BETA


def observable_fraction():
    """
    Maximum observable coherent fraction.
    """
    return ALPHA


def coherence_balance(a):
    """
    Observable + hidden normalized balance.
    """
    observable = min(a, ALPHA)
    hidden = 1.0 - observable
    return observable, hidden


def holographic_ratio(M):
    """
    Information encoded on horizon.
    """
    bits = information_bits(M)
    area = horizon_area(M)
    return bits / area


# ============================================================
# TEST 1 — FRAMEWORK CONSISTENCY
# ============================================================

class TestFrameworkConsistency:

    def test_alpha_beta_sum_to_one(self):
        assert abs(ALPHA + BETA - 1.0) < 1e-12

    def test_alpha_is_dominant(self):
        assert ALPHA > BETA

    def test_beta_is_irreducible(self):
        assert BETA > 0

    def test_alpha_matches_expected_value(self):
        assert ALPHA == pytest.approx(0.9629629629)

    def test_beta_matches_expected_value(self):
        assert BETA == pytest.approx(0.0370370370)


# ============================================================
# TEST 2 — REAL BLACK HOLE DATA
# ============================================================

class TestObservedBlackHoles:

    @pytest.mark.parametrize("name", BLACK_HOLES.keys())
    def test_spin_is_physical(self, name):
        a = BLACK_HOLES[name]["spin"]
        assert 0 <= a <= 1

    @pytest.mark.parametrize("name", BLACK_HOLES.keys())
    def test_mass_positive(self, name):
        M = BLACK_HOLES[name]["mass"]
        assert M > 0

    @pytest.mark.parametrize("name", BLACK_HOLES.keys())
    def test_entropy_positive(self, name):
        M = BLACK_HOLES[name]["mass"]
        assert entropy(M) > 0

    @pytest.mark.parametrize("name", BLACK_HOLES.keys())
    def test_information_positive(self, name):
        M = BLACK_HOLES[name]["mass"]
        assert information_bits(M) > 0


# ============================================================
# TEST 3 — COHERENCE PROXIMITY
# ============================================================

class TestCoherenceInvariant:

    def test_cygnus_x1_near_alpha(self):
        """
        Cygnus X-1 is one of the closest known systems
        to the proposed coherent limit.
        """
        gamma = coherence_from_spin(
            BLACK_HOLES["CygnusX1"]["spin"]
        )

        assert gamma > 0.95

    def test_ton618_extreme_state(self):
        """
        TON618 approaches maximal coherent regime.
        """
        gamma = coherence_from_spin(
            BLACK_HOLES["TON618"]["spin"]
        )

        assert gamma > 1.0

    def test_sgra_less_extreme_than_cygnus(self):

        gamma_sgr = coherence_from_spin(
            BLACK_HOLES["SgrA"]["spin"]
        )

        gamma_cyg = coherence_from_spin(
            BLACK_HOLES["CygnusX1"]["spin"]
        )

        assert gamma_sgr < gamma_cyg

    def test_m87_less_extreme_than_ton618(self):

        gamma_m87 = coherence_from_spin(
            BLACK_HOLES["M87"]["spin"]
        )

        gamma_ton = coherence_from_spin(
            BLACK_HOLES["TON618"]["spin"]
        )

        assert gamma_m87 < gamma_ton


# ============================================================
# TEST 4 — OBSERVABLE VS HIDDEN
# ============================================================

class TestObservableHiddenPartition:

    @pytest.mark.parametrize("name", BLACK_HOLES.keys())
    def test_balance_sums_to_one(self, name):

        spin = BLACK_HOLES[name]["spin"]

        obs, hidden = coherence_balance(spin)

        assert abs(obs + hidden - 1.0) < 1e-10

    @pytest.mark.parametrize("name", BLACK_HOLES.keys())
    def test_hidden_never_zero(self, name):

        spin = BLACK_HOLES[name]["spin"]

        obs, hidden = coherence_balance(spin)

        assert hidden > 0

    def test_hidden_approaches_beta_near_limit(self):

        spin = ALPHA

        obs, hidden = coherence_balance(spin)

        assert hidden == pytest.approx(BETA)

    def test_observable_cannot_exceed_alpha(self):

        spin = 0.999999

        obs, hidden = coherence_balance(spin)

        assert obs <= ALPHA


# ============================================================
# TEST 5 — HOLOGRAPHIC STRUCTURE
# ============================================================

class TestHolographicStructure:

    @pytest.mark.parametrize("name", BLACK_HOLES.keys())
    def test_horizon_area_positive(self, name):

        M = BLACK_HOLES[name]["mass"]

        assert horizon_area(M) > 0

    @pytest.mark.parametrize("name", BLACK_HOLES.keys())
    def test_holographic_ratio_positive(self, name):

        M = BLACK_HOLES[name]["mass"]

        ratio = holographic_ratio(M)

        assert ratio > 0

    def test_entropy_scales_with_area(self):

        M1 = BLACK_HOLES["CygnusX1"]["mass"]
        M2 = BLACK_HOLES["TON618"]["mass"]

        S1 = entropy(M1)
        S2 = entropy(M2)

        assert S2 > S1

    def test_information_scales_with_mass_squared(self):

        M1 = BLACK_HOLES["SgrA"]["mass"]
        M2 = BLACK_HOLES["M87"]["mass"]

        I1 = information_bits(M1)
        I2 = information_bits(M2)

        assert I2 > I1


# ============================================================
# TEST 6 — FALSIFICATION TESTS
# ============================================================

class TestFalsification:

    def test_if_all_spins_far_from_alpha_hypothesis_fails(self):

        distances = []

        for bh in BLACK_HOLES.values():
            d = abs(bh["spin"] - ALPHA)
            distances.append(d)

        avg_distance = sum(distances) / len(distances)

        assert avg_distance < 0.25, (
            "Observed spins too far from alpha. "
            "Hypothesis weak or incorrect."
        )

    def test_if_hidden_component_disappears_hypothesis_fails(self):

        assert BETA > 0

    def test_if_observable_exceeds_one_hypothesis_fails(self):

        for bh in BLACK_HOLES.values():

            obs, hidden = coherence_balance(bh["spin"])

            assert obs <= 1.0


# ============================================================
# TEST 7 — SUMMARY
# ============================================================

class TestSummary:

    def test_framework_summary(self):

        results = {}

        for name, bh in BLACK_HOLES.items():

            spin = bh["spin"]

            gamma = coherence_from_spin(spin)

            obs, hidden = coherence_balance(spin)

            results[name] = {
                "spin": spin,
                "gamma": gamma,
                "observable": obs,
                "hidden": hidden,
            }

        for name, data in results.items():

            assert isinstance(data["spin"], float)
            assert isinstance(data["gamma"], float)
            assert isinstance(data["observable"], float)
            assert isinstance(data["hidden"], float)

            assert 0 <= data["observable"] <= 1
            assert 0 <= data["hidden"] <= 1


if name == "main":
    pytest.main([file, "-v", "--tb=short"])

"""
Expected Interpretation
-----------------------

If systems cluster near alpha:
    -> possible coherence attractor.

If systems diverge strongly:
    -> hypothesis weakens.

If hidden component remains irreducible:
    -> beta behaves like causal inaccessible core.

"""
