"""
L4 — Self
===============
Mide la coherencia estructural del sistema consigo mismo: las constantes son correctas,
los módulos críticos están cargados, los invariantes se sostienen.

Principio de diseño:
    La integridad no se declara — se verifica.
    L4 mide lo que el sistema SÍ puede verificar sin sesión externa:
      1. Invariante estructural: ALPHA + BETA = 1 (exacto)
      2. Completitud de módulos críticos (formulas, core, layers)
    Si ambas condiciones se cumplen, L4 = completitud de módulos.
    phi = 1 - L  (fricción = brecha entre módulos disponibles y completos)
"""

import importlib.util
from typing import Optional

_CRITICAL_MODULES = [
    "formulas.constants",
    "formulas.coherence",
    "formulas.energy",
    "formulas.dynamics",
    "core.engine",
    "core.validator",
    "layers.l7_integration",
]


def _check_constants_invariant() -> bool:
    try:
        from formulas.constants import ALPHA, BETA
        return abs(ALPHA + BETA - 1.0) < 1e-12
    except Exception:
        return False


def _check_module_completeness() -> float:
    loaded = sum(
        1 for m in _CRITICAL_MODULES
        if importlib.util.find_spec(m) is not None
    )
    return loaded / len(_CRITICAL_MODULES)


class selfLayer:
    """
    L4 — self.

    Auto-inicialización: verifica los invariantes estructurales del sistema
    y la completitud de módulos críticos.
    L = completitud × (1 si constantes OK, 0 si no).
    phi = 1 - L.

    Contrato con el motor:
        - L ∈ [0, 1]
        - phi ≥ 0
        - activate(L, phi) sobreescribe con valores externos cuando existen.
    High phi here represents a fragmented identity or systemic instability.
    """

    def __init__(self, lower_layers: Optional[list] = None):
        self.name = "self"
        self.L, self.phi = self._compute_base()

    @staticmethod
    def _compute_base() -> tuple:
        constants_ok = _check_constants_invariant()
        module_ratio = _check_module_completeness()
        L = module_ratio * (1.0 if constants_ok else 0.0)
        L = max(0.0, min(1.0, L))
        phi = round(1.0 - L, 6)
        return L, phi

    def activate(self, L: float, phi: float) -> None:
        """
        Activates L4.
        High phi here represents a fragmented identity or systemic instability.
        Sobreescribe con valores externos cuando hay sesión activa.
        """
        self.L = max(0.0, min(1.0, float(L)))
        self.phi = max(0.0, float(phi))

    def export(self) -> dict:
        return {"L": self.L, "phi": self.phi, "name": self.name}
