import math
import pytest

# ============================================================================
# MODELO DE COHERENCIA DE AGUJEROS NEGROS
# ============================================================================
#
# Hipótesis:
#
#   α = 26/27  -> parte activa / observable / energética
#   β = 1/27   -> núcleo irreducible / singularidad invisible
#
#   Coherencia:
#
#       C = α_visible + β_núcleo
#
#   donde:
#
#       α_visible = eficiencia observable normalizada
#       β_núcleo  = componente irreducible mínima
#
# ============================================================================
# CONSTANTES FUNDAMENTALES
# ============================================================================

ALPHA = 26 / 27
BETA = 1 / 27

# Tolerancia numérica
TOL = 1e-10

# ============================================================================
# DATOS REALES (APROXIMADOS)
# ============================================================================
#
# efficiency:
#   eficiencia de conversión acreción → radiación
#
# Valores aproximados astrofísicos:
#
#   Schwarzschild BH ~ 0.057
#   Kerr rotación media ~ 0.1 - 0.2
#   Kerr extremo ~ 0.42
#
# Normalizamos respecto al máximo teórico observable.
# ============================================================================

BLACK_HOLES = [
    {
        "name": "Sagittarius A*",
        "mass_solar": 4.1e6,
        "efficiency": 0.10,
    },
    {
        "name": "M87*",
        "mass_solar": 6.5e9,
        "efficiency": 0.15,
    },
    {
        "name": "Cygnus X-1",
        "mass_solar": 21.0,
        "efficiency": 0.20,
    },
    {
        "name": "GRS 1915+105",
        "mass_solar": 12.4,
        "efficiency": 0.30,
    },
    {
        "name": "Extreme Kerr",
        "mass_solar": 10.0,
        "efficiency": 0.42,
    },
]

# ============================================================================
# FUNCIONES
# ============================================================================

def normalize_efficiency(efficiency, max_efficiency=0.42):
    """
    Normaliza eficiencia observada al rango [0,1].
    """
    return efficiency / max_efficiency


def visible_component(normalized_efficiency):
    """
    Parte visible asociada al 26/27.
    """
    return normalized_efficiency * ALPHA


def invisible_component():
    """
    Núcleo irreducible.
    """
    return BETA


def coherence(normalized_efficiency):
    """
    Coherencia total del agujero negro.
    """
    return (
        visible_component(normalized_efficiency)
        + invisible_component()
    )


# ============================================================================
# TESTS ESTRUCTURALES
# ============================================================================

def test_alpha_beta_close_unity():
    """
    α + β = 1
    """
    total = ALPHA + BETA
    assert abs(total - 1.0) < TOL


def test_beta_irreducible_positive():
    """
    β debe existir siempre.
    """
    assert BETA > 0
    assert BETA < 0.1


def test_alpha_dominates_visible_structure():
    """
    α domina la estructura observable.
    """
    assert ALPHA > BETA
    assert ALPHA > 0.9


# ============================================================================
# TESTS DE COHERENCIA
# ============================================================================

@pytest.mark.parametrize("bh", BLACK_HOLES)
def test_coherence_is_bounded(bh):

    norm_eff = normalize_efficiency(bh["efficiency"])
    coh = coherence(norm_eff)

    # Nunca puede caer debajo del núcleo irreducible
    assert coh >= BETA

    # Nunca puede superar 1
    assert coh <= 1.0 + TOL


@pytest.mark.parametrize("bh", BLACK_HOLES)
def test_visible_component_matches_alpha_structure(bh):

    norm_eff = normalize_efficiency(bh["efficiency"])
    visible = visible_component(norm_eff)

    assert visible <= ALPHA + TOL
    assert visible >= 0


@pytest.mark.parametrize("bh", BLACK_HOLES)
def test_extreme_black_hole_converges_to_unity(bh):

    norm_eff = normalize_efficiency(bh["efficiency"])
    coh = coherence(norm_eff)

    # El caso extremo debería aproximarse a 1
    if bh["name"] == "Extreme Kerr":
        assert coh > 0.99


# ============================================================================
# TESTS FÍSICOS
# ============================================================================

@pytest.mark.parametrize("bh", BLACK_HOLES)
def test_mass_positive(bh):

    assert bh["mass_solar"] > 0


@pytest.mark.parametrize("bh", BLACK_HOLES)
def test_efficiency_physical(bh):

    eff = bh["efficiency"]

    # eficiencia física válida
    assert 0 <= eff <= 0.42


# ============================================================================
# TEST DE INVARIANTE
# ============================================================================

def test_invariant_structure():

    coherences = []

    for bh in BLACK_HOLES:

        norm_eff = normalize_efficiency(
            bh["efficiency"]
        )

        coh = coherence(norm_eff)

        coherences.append(coh)

    # Todas las coherencias deben contener β
    for coh in coherences:
        assert coh >= BETA

    # El sistema completo permanece contenido en [β,1]
    assert min(coherences) >= BETA
    assert max(coherences) <= 1.0 + TOL


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    pytest.main(
        [
            "-v",
            "--tb=short",
        ]
    )
