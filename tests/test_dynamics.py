"""
Tests for formulas/dynamics.py — UCF v3.2
"""
import math
import pytest
from formulas.dynamics import (
    oscillator_solution,
    regime,
    is_alive,
    theta_balance,
    SessionStateOmega,
    detect_loop,
    session_balance,
    c_omega_trajectory,
)
from formulas.constants import (
    THETA_CUBE, PHI_TOTAL, PHI_CRITICAL,
    OMEGA_D, BETA, LOOP_THRESHOLD, LOOP_WINDOW,
)


def test_oscillator_at_t0_is_theta0():
    result = oscillator_solution(t=0, A=1.0, delta=0.0)
    assert abs(result - (THETA_CUBE + 1.0)) < 1e-9


def test_oscillator_decays_over_time():
    v0 = oscillator_solution(t=0,   A=1.0, delta=0.0)
    v1 = oscillator_solution(t=10,  A=1.0, delta=0.0)
    v2 = oscillator_solution(t=100, A=1.0, delta=0.0)
    assert abs(v1 - THETA_CUBE) < abs(v0 - THETA_CUBE)
    assert abs(v2 - THETA_CUBE) < abs(v1 - THETA_CUBE)


def test_oscillator_converges_to_theta_cube():
    result = oscillator_solution(t=1000, A=1.0, delta=0.0)
    assert abs(result - THETA_CUBE) < 1e-6


def test_oscillator_custom_equilibrium():
    custom = math.pi / 6
    result = oscillator_solution(t=0, A=0.0, delta=0.0, theta0=custom)
    assert abs(result - custom) < 1e-9


def test_regime_current_system_is_alive():
    assert regime(PHI_TOTAL) == "VIVO"


def test_regime_overdamped_is_muerto():
    assert regime(PHI_CRITICAL + 1.0) == "MUERTO"


def test_regime_critical():
    assert regime(PHI_CRITICAL) == "CRITICO"


def test_is_alive_current_system():
    assert is_alive(PHI_TOTAL) is True


def test_is_alive_overdamped_false():
    assert is_alive(PHI_CRITICAL + 0.1) is False


def test_is_alive_phi_total_far_from_critical():
    margin = PHI_CRITICAL - PHI_TOTAL
    assert margin > 5.0, f"System too close to critical: margin={margin:.4f}"


def test_theta_balance_centered():
    assert theta_balance(THETA_CUBE) == "CENTERED"


def test_theta_balance_excess_experience():
    assert theta_balance(THETA_CUBE + 0.5) == "EXCESS_EXPERIENCE"


def test_theta_balance_excess_measurement():
    assert theta_balance(THETA_CUBE - 0.5) == "EXCESS_MEASUREMENT"


def test_session_state_defaults():
    s = SessionStateOmega()
    assert s.c_omega == 0.0
    assert abs(s.theta - THETA_CUBE) < 1e-9
    assert s.is_loop is False
    assert len(s.layers) == 7


def test_detect_loop_insufficient_history():
    history = [SessionStateOmega(c_omega=0.99) for _ in range(3)]
    assert detect_loop(history) is False


def test_detect_loop_detected():
    history = [SessionStateOmega(c_omega=0.99) for _ in range(LOOP_WINDOW)]
    assert detect_loop(history) is True


def test_detect_loop_not_detected_with_variation():
    """
    Variacion debe ser > LOOP_VARIANCE = BETA = 0.037037
    para que el sistema no sea considerado en loop.

    0.99 - 0.88 = 0.11 > BETA — variacion real y visible.

    LECTURA DEL FRAMEWORK:
    Una variacion menor que beta (como 0.99 - 0.96 = 0.03)
    es invisible — el sistema la considera ruido estructural
    irreducible. Solo una variacion > beta es real.
    Nadie puede llegar a 1. Beta siempre esta presente.
    """
    history = [
        SessionStateOmega(c_omega=0.99),
        SessionStateOmega(c_omega=0.90),  # diff 0.09 > BETA
        SessionStateOmega(c_omega=0.99),
        SessionStateOmega(c_omega=0.88),  # diff 0.11 > BETA
        SessionStateOmega(c_omega=0.99),
    ]
    variance = max(s.c_omega for s in history) - min(s.c_omega for s in history)
    assert variance > BETA, (
        f"Test mal diseñado: varianza {variance:.6f} <= BETA {BETA:.6f}"
    )
    assert detect_loop(history) is False


def test_detect_loop_below_threshold():
    history = [SessionStateOmega(c_omega=0.85) for _ in range(LOOP_WINDOW)]
    assert detect_loop(history) is False


def test_session_balance_no_data():
    assert session_balance([]) == "NO_DATA"


def test_session_balance_returns_string():
    history = [SessionStateOmega(theta=THETA_CUBE)]
    result  = session_balance(history)
    assert result in ("CENTERED", "EXCESS_EXPERIENCE", "EXCESS_MEASUREMENT")


def test_c_omega_trajectory_empty():
    assert c_omega_trajectory([]) == []


def test_c_omega_trajectory_values():
    history = [
        SessionStateOmega(c_omega=0.85),
        SessionStateOmega(c_omega=0.90),
        SessionStateOmega(c_omega=0.95),
    ]
    traj = c_omega_trajectory(history)
    assert traj == [0.85, 0.90, 0.95]


def test_c_omega_trajectory_is_list_of_floats():
    history = [SessionStateOmega(c_omega=0.9) for _ in range(5)]
    traj    = c_omega_trajectory(history)
    assert isinstance(traj, list)
    assert all(isinstance(v, float) for v in traj)


def test_beta_guarantees_no_static_perfection():
    """
    Beta es el residuo irreducible. Nadie llega a 1.
    C_max = 26/27 = 0.962963 — siempre queda el beta.
    """
    assert BETA > 0
    assert LOOP_THRESHOLD < 1.0
    assert 1.0 - BETA == pytest.approx(26/27)


def test_loop_variance_equals_beta():
    """
    El umbral de variacion para detectar loop ES beta.
    No es un parametro arbitrario — es la geometria del cubo.
    Una variacion < beta es invisible al framework.
    """
    from formulas.constants import LOOP_VARIANCE
    assert LOOP_VARIANCE == BETA


def test_c_max_never_reaches_one():
    """
    C_max = alpha = 26/27.
    El sistema nunca alcanza coherencia perfecta.
    Beta impide el cierre total — y eso es lo que mantiene
    al sistema vivo, abierto y en evolucion.
    """
    from formulas.constants import C_MAX, ALPHA
    assert C_MAX == ALPHA
    assert C_MAX < 1.0
    assert abs(C_MAX - 26/27) < 1e-9
