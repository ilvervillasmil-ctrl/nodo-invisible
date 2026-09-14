import math
import pytest

PHI = (1 + math.sqrt(5)) / 2
ALPHA = 26 / 27
BETA = 1 / 27
R_FIN = 28 / 27
ALPHA_OVER_S = (ALPHA * math.pi) / math.e
LAYER_FRICTION = [0.10, 0.02, 0.05, 0.03, 0.01, 0.01, 0.00]
NUM_LAYERS = 7


def _frequency(i):
    return PHI ** (i / 2)


E0_REF = _frequency(0)

PRODUCTO_MAX = 1.0
for _i in range(NUM_LAYERS):
    _e = 1.0 * (1.0 - LAYER_FRICTION[_i]) * _frequency(_i)
    PRODUCTO_MAX *= _e

C_BETA_MAX = ALPHA_OVER_S * R_FIN


def _compute_c_beta(activations, rho=1.0, p_t=1.0, a=0.632, i_ext=1.0):
    producto_raw = 1.0
    for i in range(NUM_LAYERS):
        e_i = activations[i] * (1.0 - LAYER_FRICTION[i]) * _frequency(i)
        producto_raw *= (e_i / E0_REF)
    producto_norm = producto_raw / PRODUCTO_MAX
    return producto_norm * ALPHA_OVER_S * R_FIN * rho * p_t * a * i_ext, producto_norm


def _compute_c_alpha(I=0.7, Q=0.7, D=1.0, U=0.1):
    return (I * Q) / (D + U + BETA)


def _c_omega(activations, I=0.7, Q=0.7, D=1.0, U=0.1,
             rho=1.0, p_t=1.0, a=0.632, i_ext=1.0):
    cb, _ = _compute_c_beta(activations, rho, p_t, a, i_ext)
    ca = _compute_c_alpha(I, Q, D, U)
    ct = math.sqrt(cb**2 + ca**2)
    return min(1.0, ct * (PHI / 2)), cb, ca, ct


class TestNormalizationInvariants:

    def test_producto_max_positive(self):
        assert PRODUCTO_MAX > 0

    def test_producto_max_expected_value(self):
        assert abs(PRODUCTO_MAX - 124.624) < 0.01

    def test_producto_norm_all_ones_equals_one(self):
        _, pn = _compute_c_beta([1.0] * NUM_LAYERS)
        assert abs(pn - 1.0) < 1e-10

    def test_producto_norm_zero_when_any_layer_zero(self):
        for dead_layer in range(NUM_LAYERS):
            acts = [0.9] * NUM_LAYERS
            acts[dead_layer] = 0.0
            _, pn = _compute_c_beta(acts)
            assert pn == 0.0

    def test_producto_norm_always_in_0_1(self):
        test_cases = [
            [1.0] * NUM_LAYERS,
            [0.9] * NUM_LAYERS,
            [0.5] * NUM_LAYERS,
            [0.1] * NUM_LAYERS,
            [0.85, 0.90, 0.80, 0.85, 0.90, 0.90, 0.90],
        ]
        for acts in test_cases:
            _, pn = _compute_c_beta(acts)
            assert 0.0 <= pn <= 1.0

    def test_c_beta_monotone_with_activations(self):
        cb_low, _ = _compute_c_beta([0.5] * NUM_LAYERS)
        cb_high, _ = _compute_c_beta([0.9] * NUM_LAYERS)
        assert cb_high > cb_low

    def test_c_beta_and_c_alpha_comparable_magnitude(self):
        cb, _ = _compute_c_beta([0.85, 0.90, 0.80, 0.85, 0.90, 0.90, 0.90])
        ca = _compute_c_alpha(0.85, 0.80, 1.2, 0.15)
        ratio = cb / ca if ca > 0 else float('inf')
        assert 0.1 < ratio < 10.0


class TestDiagnosticRanges:

    def test_perfect_system_reaches_1144(self):
        cw, _, _, _ = _c_omega(
            [1.0] * NUM_LAYERS,
            I=1.0, Q=1.0, D=0.5, U=0.05,
            rho=1.0, p_t=1.0, a=0.865, i_ext=1.9
        )
        assert cw >= ALPHA

    def test_high_system_reaches_1122(self):
        cw, _, _, _ = _c_omega(
            [0.90] * NUM_LAYERS,
            I=0.9, Q=0.9, D=0.8, U=0.08,
            rho=0.90, p_t=0.85, a=0.75, i_ext=1.764
        )
        assert 0.40 <= cw < ALPHA

    def test_typical_session_reaches_1122(self):
        cw, _, _, _ = _c_omega(
            [0.85, 0.90, 0.80, 0.85, 0.90, 0.90, 0.90],
            I=0.85, Q=0.80, D=1.2, U=0.15,
            rho=0.88, p_t=0.819, a=0.753, i_ext=1.764
        )
        assert 0.40 <= cw < 1.0

    def test_collapsed_layer_gives_0000(self):
        acts = [0.85, 0.85, 0.00, 0.85, 0.85, 0.85, 0.85]
        cw, cb, _, _ = _c_omega(acts, I=0.7, Q=0.7)
        assert cb == 0.0
        assert cw < 0.40

    def test_c_omega_never_exceeds_one(self):
        for acts in [[1.0] * NUM_LAYERS, [0.99] * NUM_LAYERS]:
            cw, _, _, _ = _c_omega(
                acts, I=1.0, Q=1.0, D=0.1, U=0.01,
                rho=1.0, p_t=1.0, a=1.0, i_ext=2.0
            )
            assert cw <= 1.0

    def test_c_omega_never_negative(self):
        cw, _, _, _ = _c_omega([0.0] * NUM_LAYERS, I=0.0, Q=0.0)
        assert cw >= 0.0


class TestBackwardCompatibility:

    def test_alpha_beta_conservation_unaffected(self):
        assert abs(ALPHA + BETA - 1.0) < 1e-10

    def test_l6_zero_friction_still_required(self):
        assert LAYER_FRICTION[6] == 0.0

    def test_zero_activation_gives_zero_c_beta(self):
        cb, pn = _compute_c_beta([0.0] * NUM_LAYERS)
        assert cb == 0.0
        assert pn == 0.0

    def test_normalization_preserves_monotonicity(self):
        prev_cb = -1
        for la in [0.3, 0.5, 0.7, 0.9]:
            cb, _ = _compute_c_beta([la] * NUM_LAYERS)
            assert cb > prev_cb
            prev_cb = cb
