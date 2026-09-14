"""
L3 — Síntesis
=============
Integra los outputs de L0 (caos/movimiento), L1 (cuerpo/energía) y L2 (ego/identidad)
en una señal coherente. No inventa lo que no existe: mide la contribución real de las
capas inferiores y la usa como estado base.

Principio de diseño:
    L3 no puede sintetizar lo que no recibió.
    Pero tampoco puede fingir que no existe cuando L0-L2 están activas.
    Estado base = media geométrica de las contribuciones reales de L0, L1, L2.

Fricción base:
    phi = 1 - L  (la fricción refleja la brecha entre la síntesis actual y la perfecta)
"""

from typing import Optional


class LayerSynthesis:
    """
    L3 — Síntesis.

    Auto-inicialización: al instanciar sin argumentos, calcula L y phi
    desde las contribuciones reales de las capas inferiores disponibles.
    Si no hay datos de capas inferiores, usa los defaults del sistema
    (L0=1.0/φ=0, L1=1.0/φ=0, L2=1.0/φ=0.05 — valores live actuales).

    Contrato con el motor:
        - L ∈ [0, 1]
        - phi ≥ 0
        - activate(L, phi) sobreescribe con valores externos cuando existen
    """

    # Defaults del sistema cuando no hay sesión activa.
    # Refleja el estado real de L0-L2 en el framework actual.
    _DEFAULT_LOWER_LAYERS = [
        {"L": 1.0, "phi": 0.0},   # L0 chaos  — default framework
        {"L": 1.0, "phi": 0.0},   # L1 body   — default framework
        {"L": 1.0, "phi": 0.05},  # L2 ego    — live layer, phi=0.05
    ]

    def __init__(self, lower_layers: Optional[list] = None):
        """
        Parámetros
        ----------
        lower_layers : lista de dicts {"L": float, "phi": float} para L0, L1, L2.
                       Si es None, usa los defaults del sistema.
        """
        self.name = "Synthesis"
        layers = lower_layers if lower_layers is not None else self._DEFAULT_LOWER_LAYERS
        self.L, self.phi = self._compute_base(layers)

    @staticmethod
    def _compute_base(lower_layers: list) -> tuple:
        """
        L3 base = media geométrica de las contribuciones netas de L0-L2.
        Contribución neta de capa i = Li * (1 - phi_i).
        phi3 = 1 - L3  (fricción como complemento de la activación).
        """
        contributions = [
            max(0.0, layer["L"] * (1.0 - layer["phi"]))
            for layer in lower_layers
        ]
        n = len(contributions)
        if n == 0 or all(c == 0.0 for c in contributions):
            return 0.0, 1.0  # sin inputs → sin síntesis, fricción máxima

        product = 1.0
        for c in contributions:
            product *= c
        L = product ** (1.0 / n)
        L = max(0.0, min(1.0, L))
        phi = round(1.0 - L, 6)
        return L, phi

    def activate(self, L: float, phi: float) -> None:
        """
        Sobreescribe con valores externos cuando hay sesión activa.
        Llamar esto cuando el sistema tiene datos reales de síntesis.
        """
        self.L = max(0.0, min(1.0, float(L)))
        self.phi = max(0.0, float(phi))

    def export(self) -> dict:
        return {"L": self.L, "phi": self.phi, "name": self.name}
