"""
core/meta_verification/constants.py

El meta-verificador solo conoce α y β.
Nada más del framework debe importarse aquí.
"""

from fractions import Fraction

ALPHA_FRACTION = Fraction(26, 27)
BETA_FRACTION = Fraction(1, 27)

ALPHA = float(ALPHA_FRACTION)
BETA = float(BETA_FRACTION)

EPSILON = 1e-12


def verify_alpha_beta() -> bool:
    """
    Verifica las invariantes mínimas del meta-verificador.
    """
    if ALPHA_FRACTION != Fraction(26, 27):
        return False

    if BETA_FRACTION != Fraction(1, 27):
        return False

    if ALPHA_FRACTION + BETA_FRACTION != 1:
        return False

    if not BETA < ALPHA:
        return False

    return True
