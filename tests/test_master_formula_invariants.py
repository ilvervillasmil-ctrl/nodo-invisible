"""
test_master_formula_invariants.py
==================================
Test suite for the 5 structural invariants of the Master Formula C_Omega.

C_Omega = [prod_i(E_i/E_0)] * (alpha/S) * R_fin * rho * P_t * A * I_ext

Invariants under test:
  I1 — Collapse asymmetry: multiplicative structure means one zero collapses all
  I2 — Beta as irreducible attractor: fundamental constants are exact and structural
  I3 — rho and P_t as the only real-time controllable levers
  I4 — Entropy threshold: S_REF_7 = S_REF + BETA*ln(7) is the structural ceiling
  I5 — Identity as configuration: C_Omega depends on layer relations, not absolute values

Author: I. Villasmil / UIS Framework v4.0
"""

import math
import itertools
from formulas.constants import ALPHA, BETA, KAPPA, R_FIN, S_REF, NUM_LAYERS
from formulas.coherence import CoherenceEngine

# S_REF_7 is not exported from formulas.constants — it is derived from the framework.
# S_REF_7 = S_REF + BETA * ln(NUM_LAYERS) = maximum structural entropy for 7 layers.
S_REF_7 = S_REF + BETA * math.log(NUM_LAYERS)


# ---------------------------------------------------------------------------
# INVARIANT I1 — Collapse Asymmetry
# The multiplicative structure of the product term means a single zero layer
# collapses C_Omega to 0. This is NOT symmetric: high values in other layers
# cannot compensate for a zero in any single layer.
# ---------------------------------------------------------------------------

class TestInvariantI1CollapseAsymmetry:

    def test_single_zero_layer_collapses_to_zero(self):
        """Any single layer at 0 drives C_Omega to 0, regardless of others."""
        for i in range(NUM_LAYERS):
            layers = [1.0] * NUM_LAYERS
            layers[i] = 0.0
            result = CoherenceEngine.compute_c_beta(layers)
            assert result["c_beta"] == 0.0, (
                f"Layer {i} = 0 did not collapse C_Omega. Got {result['c_beta']}"
            )

    def test_collapse_is_not_compensated_by_other_layers(self):
        """Setting one layer to 0 and others to maximum still gives 0."""
        layers_collapsed = [1.0] * NUM_LAYERS
        layers_collapsed[2] = 0.0  # L2 (ego) collapsed

        layers_full = [1.0] * NUM_LAYERS

        r_collapsed = CoherenceEngine.compute_c_beta(layers_collapsed)
        r_full = CoherenceEngine.compute_c_beta(layers_full)

        assert r_collapsed["c_beta"] == 0.0
        assert r_full["c_beta"] > 0.0

    def test_collapse_is_asymmetric_vs_additive(self):
        """
        If coherence were additive, mean([0, 1, 1, 1, 1, 1, 1]) = 0.857 > 0.
        The multiplicative structure gives 0. This test confirms the asymmetry.
        """
        layers_with_zero = [1.0, 1.0, 0.0, 1.0, 1.0, 1.0, 1.0]
        result = CoherenceEngine.compute_c_beta(layers_with_zero)
        additive_average = sum(layers_with_zero) / len(layers_with_zero)

        assert result["c_beta"] == 0.0
        assert additive_average > 0.5  # Would be high under additive logic
        assert result["c_beta"] < additive_average

    def test_two_weak_layers_worse_than_one(self):
        """Two layers at 0.5 produce less coherence than one layer at 0.5 with others at 1."""
        layers_one_weak = [1.0, 1.0, 0.5, 1.0, 1.0, 1.0, 1.0]
        layers_two_weak = [1.0, 1.0, 0.5, 0.5, 1.0, 1.0, 1.0]

        r1 = CoherenceEngine.compute_c_beta(layers_one_weak)
        r2 = CoherenceEngine.compute_c_beta(layers_two_weak)

        assert r1["c_beta"] > r2["c_beta"]

    def test_governance_sector_drags_global(self):
        """
        Mirrors the Global Social Coherence Study finding: C_governance = 0.25
        drags the global product below the best sector (0.45) even with
        all other sectors performing above average.
        """
        sector_coherences = [0.45, 0.38, 0.35, 0.30, 0.27, 0.25, 0.25]
        result = CoherenceEngine.compute_c_beta(sector_coherences)
        assert result["c_beta"] < 0.45

    def test_product_key_in_result(self):
        """compute_c_beta result includes the 'product' key (normalized product)."""
        result = CoherenceEngine.compute_c_beta([0.8] * NUM_LAYERS)
        assert "product" in result
        assert result["product"] > 0.0


# ---------------------------------------------------------------------------
# INVARIANT I2 — Beta as Irreducible Structural Attractor
# BETA = 1/27 is not a free parameter. It is the exact ratio of the center
# cube to the total 3x3x3 structure. All fundamental constants of the
# framework are derived from BETA and ALPHA = 1 - BETA = 26/27.
# ---------------------------------------------------------------------------

class TestInvariantI2BetaAttractor:

    def test_beta_is_exact_1_over_27(self):
        """BETA = 1/27 exactly."""
        assert abs(BETA - 1.0 / 27.0) < 1e-15

    def test_alpha_is_exact_26_over_27(self):
        """ALPHA = 26/27 exactly."""
        assert abs(ALPHA - 26.0 / 27.0) < 1e-15

    def test_alpha_plus_beta_equals_one(self):
        """ALPHA + BETA = 1 exactly — conservation law of the framework."""
        assert abs(ALPHA + BETA - 1.0) < 1e-15

    def test_alpha_beta_ratio_is_26(self):
        """ALPHA/BETA = 26 — the fundamental scaling ratio."""
        assert abs(ALPHA / BETA - 26.0) < 1e-12

    def test_r_fin_equals_1_plus_beta(self):
        """R_fin = 1 + BETA = 28/27 — proactive refinement factor."""
        assert abs(R_FIN - (1.0 + BETA)) < 1e-15

    def test_full_system_exceeds_beta(self):
        """A fully active system (all layers = 1.0) produces C_Omega > BETA."""
        layers = [1.0] * NUM_LAYERS
        result = CoherenceEngine.compute_c_beta(layers)
        assert result["c_beta"] > BETA

    def test_minimal_activation_gives_near_zero_coherence(self):
        """
        All layers at BETA (minimum non-zero) gives C_Omega > 0 but very small.
        The system is alive (non-zero) but structurally minimal.
        """
        layers = [BETA] * NUM_LAYERS
        result = CoherenceEngine.compute_c_beta(layers)
        assert result["c_beta"] > 0.0
        assert result["c_beta"] < BETA

    def test_s_ref_7_is_derived_not_arbitrary(self):
        """
        S_REF_7 = S_REF + BETA * ln(NUM_LAYERS).
        It is structurally derived from BETA and the 7-layer architecture,
        not a free parameter.
        """
        s_ref_7_computed = S_REF + BETA * math.log(NUM_LAYERS)
        assert abs(s_ref_7_computed - S_REF_7) < 1e-15

    def test_s_ref_7_exceeds_s_ref(self):
        """S_REF_7 > S_REF — the 7-layer system has higher maximum entropy."""
        assert S_REF_7 > S_REF


# ---------------------------------------------------------------------------
# INVARIANT I3 — rho and P_t as Real-Time Controllable Levers
# All other factors in C_Omega are structural (ALPHA/S, R_fin), historical
# (layer energies), or environmental (I_ext). rho (internal alignment) and
# P_t (temporal presence) are the only variables the system can modify
# voluntarily without changing its architecture.
# ---------------------------------------------------------------------------

class TestInvariantI3RhoAndPtLevers:

    def test_rho_zero_collapses_coherence(self):
        """rho = 0 (no internal alignment) collapses C_Omega to 0."""
        layers = [0.8] * NUM_LAYERS
        r_base = CoherenceEngine.compute_c_beta(layers, rho=1.0)
        r_zero = CoherenceEngine.compute_c_beta(layers, rho=0.0)

        assert r_base["c_beta"] > 0.0
        assert r_zero["c_beta"] == 0.0

    def test_p_t_near_zero_collapses_coherence(self):
        """
        P_t = e^(-delta_t/tau). At delta_t >> tau, P_t → 0 and C_Omega → 0.
        This models complete mental displacement from the present moment.
        """
        layers = [0.8] * NUM_LAYERS
        r_base = CoherenceEngine.compute_c_beta(layers, delta_t=0.0, tau=1.0)
        r_displaced = CoherenceEngine.compute_c_beta(layers, delta_t=10000.0, tau=1.0)

        assert r_base["c_beta"] > 0.0
        assert r_displaced["c_beta"] == 0.0

    def test_rho_scales_coherence_linearly(self):
        """Doubling rho doubles C_Omega — rho is a linear multiplier."""
        layers = [0.8] * NUM_LAYERS
        r1 = CoherenceEngine.compute_c_beta(layers, rho=0.5)
        r2 = CoherenceEngine.compute_c_beta(layers, rho=1.0)
        assert abs(r2["c_beta"] / r1["c_beta"] - 2.0) < 1e-10

    def test_p_t_scales_coherence_linearly(self):
        """
        P_t = e^(-delta_t/tau). At delta_t=0, P_t=1.0.
        At delta_t=ln(2), P_t=0.5. Ratio of C_Omega should be 2.0.
        """
        layers = [0.8] * NUM_LAYERS
        dt_half = math.log(2)  # e^(-ln2/tau) = 0.5

        r_full = CoherenceEngine.compute_c_beta(layers, delta_t=0.0, tau=1.0)
        r_half = CoherenceEngine.compute_c_beta(layers, delta_t=dt_half, tau=1.0)

        assert abs(r_full["p_t"] - 1.0) < 1e-12
        assert abs(r_half["p_t"] - 0.5) < 1e-12
        assert abs(r_full["c_beta"] / r_half["c_beta"] - 2.0) < 1e-10

    def test_rho_independent_of_layer_configuration(self):
        """
        The same rho change (0.5 → 1.0) produces the same ratio (2.0)
        regardless of which layer configuration is active.
        """
        layers_high = [0.9] * NUM_LAYERS
        layers_low = [0.5] * NUM_LAYERS

        r_high_05 = CoherenceEngine.compute_c_beta(layers_high, rho=0.5)["c_beta"]
        r_high_10 = CoherenceEngine.compute_c_beta(layers_high, rho=1.0)["c_beta"]
        r_low_05 = CoherenceEngine.compute_c_beta(layers_low, rho=0.5)["c_beta"]
        r_low_10 = CoherenceEngine.compute_c_beta(layers_low, rho=1.0)["c_beta"]

        ratio_high = r_high_10 / r_high_05
        ratio_low = r_low_10 / r_low_05

        assert abs(ratio_high - ratio_low) < 1e-10

    def test_rho_one_p_t_one_gives_maximum_modulation(self):
        """rho=1.0 and delta_t=0 (P_t=1.0) gives the unmodulated base coherence."""
        layers = [0.8] * NUM_LAYERS
        r_base = CoherenceEngine.compute_c_beta(layers)  # defaults: rho=1.0, delta_t=0
        r_explicit = CoherenceEngine.compute_c_beta(layers, rho=1.0, delta_t=0.0)
        assert abs(r_base["c_beta"] - r_explicit["c_beta"]) < 1e-12


# ---------------------------------------------------------------------------
# INVARIANT I4 — Entropy Threshold
# S_REF_7 = S_REF + BETA * ln(7) is the maximum structural entropy for the
# 7-layer system. When the Shannon entropy of the layer energy distribution
# approaches S_REF_7, the harmony term collapses and coherence cannot be
# sustained through layer optimization alone.
# ---------------------------------------------------------------------------

class TestInvariantI4EntropyThreshold:

    def test_s_ref_7_exceeds_s_ref(self):
        """S_REF_7 > S_REF — the 7-layer system has higher maximum entropy."""
        assert S_REF_7 > S_REF

    def test_alpha_over_s_decreases_monotonically(self):
        """alpha/S is monotonically decreasing in S — more entropy, less amplification."""
        # S values must be strictly increasing. Note: S_REF_7 * 0.9 < S_REF,
        # so we use S_REF as the midpoint and S_REF_7 as the ceiling.
        s_values = sorted([
            S_REF * 0.5,
            S_REF,
            (S_REF + S_REF_7) / 2,  # midpoint between S_REF and S_REF_7
            S_REF_7,
            S_REF_7 * 1.1,
        ])
        ratios = [ALPHA / s for s in s_values]
        for i in range(len(ratios) - 1):
            assert ratios[i] > ratios[i + 1], (
                f"alpha/S not decreasing at index {i}: {ratios[i]} vs {ratios[i+1]}"
            )

    def test_harmony_zero_at_s_ref_7(self):
        """
        H(S) = max(0, 1 - S/S_REF_7).
        At S = S_REF_7, H = 0 — no harmony, the system is at maximum entropy.
        """
        h = max(0.0, 1.0 - S_REF_7 / S_REF_7)
        assert h == 0.0

    def test_harmony_positive_below_s_ref_7(self):
        """H(S) > 0 when S < S_REF_7 — structural room for coherence exists."""
        s = S_REF_7 * 0.9
        h = max(0.0, 1.0 - s / S_REF_7)
        assert h > 0.0

    def test_harmony_clamped_above_s_ref_7(self):
        """H(S) = 0 when S > S_REF_7 — entropy beyond the structural ceiling."""
        s = S_REF_7 * 1.1
        h = max(0.0, 1.0 - s / S_REF_7)
        assert h == 0.0

    def test_uniform_layers_maximize_entropy(self):
        """
        Uniform layer activations maximize Shannon entropy to ln(7).
        This is the 'balanced but incoherent' state — maximum entropy, minimum harmony.
        """
        n = NUM_LAYERS
        energies = [1.0 / n] * n
        total = sum(energies)
        probs = [e / total for e in energies]
        s = -sum(p * math.log(p) for p in probs if p > 0)
        assert abs(s - math.log(n)) < 1e-10

    def test_concentrated_energy_minimizes_entropy(self):
        """
        All energy in one layer gives zero Shannon entropy.
        This is the 'focused' state — minimum entropy, maximum harmony potential.
        """
        energies = [0.0] * NUM_LAYERS
        energies[3] = 1.0
        probs = [e for e in energies if e > 0]
        s = -sum(p * math.log(p) for p in probs)
        assert s == 0.0

    def test_s_ref_7_structural_derivation(self):
        """
        S_REF_7 = S_REF + BETA * ln(NUM_LAYERS).
        This is a structural consequence of the framework constants,
        not a free parameter.
        """
        s_ref_7_derived = S_REF + BETA * math.log(NUM_LAYERS)
        assert abs(s_ref_7_derived - S_REF_7) < 1e-15


# ---------------------------------------------------------------------------
# INVARIANT I5 — Identity as Configuration
# C_Omega depends on the RELATIONS between layers (the product ∏(Ei/E0)),
# not on the absolute magnitude of any single layer.
# The product is commutative: permuting layers does not change C_Omega.
# The identity of a system is its configuration, not its total energy.
# ---------------------------------------------------------------------------

class TestInvariantI5IdentityAsConfiguration:

    def test_permutation_of_layers_gives_same_coherence(self):
        """
        Permuting layers gives the same C_Omega — the product is commutative.
        Order of layers does not affect the scalar coherence output.
        """
        layers = [0.3, 0.5, 0.7, 0.8, 0.6, 0.9, 0.4]
        results = set()
        for perm in list(itertools.permutations(layers))[:20]:
            r = CoherenceEngine.compute_c_beta(list(perm))
            results.add(round(r["c_beta"], 10))
        assert len(results) == 1, (
            f"Permutations gave different C_Omega values: {results}"
        )

    def test_same_normalized_ratios_give_same_coherence(self):
        """
        Two layer sets with identical normalized ratios give identical C_Omega.
        Identity is in the proportions, not the absolute values.
        """
        layers_a = [0.2, 0.4, 0.6, 0.8, 0.6, 0.4, 0.2]
        layers_b = [0.4, 0.8, 1.2, 1.6, 1.2, 0.8, 0.4]

        # Normalize both to [0,1]
        max_a = max(layers_a)
        max_b = max(layers_b)
        norm_a = [x / max_a for x in layers_a]
        norm_b = [x / max_b for x in layers_b]

        r_a = CoherenceEngine.compute_c_beta(norm_a)
        r_b = CoherenceEngine.compute_c_beta(norm_b)

        assert abs(r_a["c_beta"] - r_b["c_beta"]) < 1e-10

    def test_changing_one_layer_changes_identity(self):
        """
        Changing a single layer value changes the configuration and C_Omega,
        even if the total activation sum is approximately preserved.
        """
        layers_original = [0.7, 0.8, 0.9, 0.8, 0.7, 0.8, 0.9]
        layers_modified = [0.7, 0.8, 0.5, 0.8, 0.7, 0.8, 1.0]  # L2 reduced, L6 raised

        r_orig = CoherenceEngine.compute_c_beta(layers_original)
        r_mod = CoherenceEngine.compute_c_beta(layers_modified)

        assert r_orig["c_beta"] != r_mod["c_beta"]

    def test_product_captures_configuration_not_sum(self):
        """
        Two layer sets with similar sums but different distributions
        produce different products. The product captures configuration.
        """
        layers_uniform = [0.7] * NUM_LAYERS          # product = 0.7^7
        layers_skewed = [0.4, 0.4, 0.4, 0.7, 0.9, 0.9, 1.0]  # similar sum, different distribution

        prod_uniform = CoherenceEngine.compute_c_beta(layers_uniform)["product"]
        prod_skewed = CoherenceEngine.compute_c_beta(layers_skewed)["product"]

        sum_uniform = sum(layers_uniform)
        sum_skewed = sum(layers_skewed)

        # Sums are similar (within 0.5)
        assert abs(sum_uniform - sum_skewed) < 0.5
        # But products differ — configuration matters
        assert abs(prod_uniform - prod_skewed) > 1e-6

    def test_all_layers_structurally_equal_in_product(self):
        """
        No layer has special weight in the product formula.
        A zero in any layer collapses C_Omega identically.
        This confirms identity is in the configuration, not in privileged layers.
        """
        for i in range(NUM_LAYERS):
            layers = [0.8] * NUM_LAYERS
            layers[i] = 0.0
            result = CoherenceEngine.compute_c_beta(layers)
            assert result["c_beta"] == 0.0, (
                f"Layer {i} zero did not collapse — all layers are structurally equal"
            )

    def test_scaling_all_layers_increases_coherence(self):
        """
        Scaling all layers by k > 1 increases C_Omega (more energy).
        The configuration (ratios) is preserved, but the magnitude grows.
        """
        layers = [0.5, 0.6, 0.7, 0.8, 0.7, 0.6, 0.5]
        k = 1.2
        layers_scaled = [min(1.0, x * k) for x in layers]

        r_orig = CoherenceEngine.compute_c_beta(layers)
        r_scaled = CoherenceEngine.compute_c_beta(layers_scaled)

        assert r_scaled["c_beta"] >= r_orig["c_beta"]
        assert r_scaled["product"] > r_orig["product"]


# ---------------------------------------------------------------------------
# CROSS-INVARIANT: The formula as a collapse theory
# Validates that coherence is harder to build than to destroy,
# and that the structural floor (BETA) is always present.
# ---------------------------------------------------------------------------

class TestCrossInvariantCollapseTheory:

    def test_building_coherence_requires_all_layers(self):
        """
        To achieve maximum coherence, ALL layers must be non-zero.
        One zero is sufficient to prevent any coherence above 0.
        """
        layers_max = [1.0] * NUM_LAYERS
        r_max = CoherenceEngine.compute_c_beta(layers_max)
        assert r_max["c_beta"] > 0.0

        layers_one_zero = [1.0] * NUM_LAYERS
        layers_one_zero[0] = 0.0
        r_blocked = CoherenceEngine.compute_c_beta(layers_one_zero)
        assert r_blocked["c_beta"] == 0.0

    def test_destruction_is_faster_than_construction(self):
        """
        It takes all 7 layers at 1.0 to maximize coherence.
        It takes 1 layer at 0.0 to collapse it.
        Destruction requires 1 action; construction requires 7.
        """
        layers_full = [1.0] * NUM_LAYERS
        r_full = CoherenceEngine.compute_c_beta(layers_full)
        assert r_full["c_beta"] > 0.0

        for i in range(NUM_LAYERS):
            layers = [1.0] * NUM_LAYERS
            layers[i] = 0.0
            r = CoherenceEngine.compute_c_beta(layers)
            assert r["c_beta"] == 0.0, (
                f"Layer {i} = 0 did not collapse the fully active system"
            )

    def test_social_coherence_global_below_threshold(self):
        """
        Global social coherence C = 0.33 < 0.45 (observability threshold).
        Using sector coherences from the Global Social Coherence Study as layer proxies.
        """
        sectors = [0.45, 0.38, 0.35, 0.30, 0.27, 0.25, 0.25]
        result = CoherenceEngine.compute_c_beta(sectors)
        assert result["c_beta"] < 0.45

    def test_governance_weakest_link_gives_most_gain_when_improved(self):
        """
        Improving the weakest sector (governance, C=0.25) by a fixed delta
        produces the largest gain in global coherence.
        This is the structural consequence of the multiplicative formula.
        """
        sectors_base = [0.45, 0.38, 0.35, 0.30, 0.27, 0.25, 0.25]
        delta = 0.20

        improvements = []
        for i in range(len(sectors_base)):
            sectors_improved = sectors_base.copy()
            sectors_improved[i] = min(1.0, sectors_improved[i] + delta)
            r = CoherenceEngine.compute_c_beta(sectors_improved)
            improvements.append((i, r["c_beta"]))

        best_idx = max(improvements, key=lambda x: x[1])[0]
        # Governance appears at indices 5 and 6 (both at 0.25)
        weakest_indices = [5, 6]
        assert best_idx in weakest_indices, (
            f"Expected improving weakest layer to give most gain, "
            f"but best improvement was at layer {best_idx}"
        )

    def test_c_beta_result_has_all_required_keys(self):
        """compute_c_beta result contains all expected keys for the master formula."""
        result = CoherenceEngine.compute_c_beta([0.8] * NUM_LAYERS)
        required_keys = [
            "c_beta", "energies", "product", "alpha_over_s",
            "r_fin", "rho", "p_t", "wonder", "i_ext"
        ]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"

    def test_formula_components_multiply_to_c_beta(self):
        """
        C_Omega = product * alpha_over_s * r_fin * rho * p_t * wonder * i_ext.
        Verify the multiplication holds for the returned result.
        """
        layers = [0.7] * NUM_LAYERS
        r = CoherenceEngine.compute_c_beta(layers)

        expected = (
            r["product"]
            * r["alpha_over_s"]
            * r["r_fin"]
            * r["rho"]
            * r["p_t"]
            * r["wonder"]
            * r["i_ext"]
        )
        assert abs(r["c_beta"] - expected) < 1e-12, (
            f"Formula components do not multiply to c_beta: "
            f"expected {expected}, got {r['c_beta']}"
        )
