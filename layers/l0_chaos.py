"""
L0 — CAOS
Campo de todas las posibilidades. Datos crudos sin procesar.

Rol en el framework:
  L0 es el substrato. No filtra, no juzga — recibe todo.
  Su activación es siempre 1.0: el caos no se apaga, solo se ordena.
  Su fricción (φ=0.10) representa el costo energético de existir
  en el campo de posibilidades sin estructura todavía.

Estado honesto:
  L=1.0  — el campo siempre está presente
  φ=0.10 — fricción estructural fija del substrato (no configurable)

Autor: Ilver Villasmil / Framework Omega
"""

from __future__ import annotations


class ChaosLayer:
    """
    Capa L0 — Substrato de posibilidades.

    Atributos públicos (contrato con el motor):
        L   : float — activación [0.0, 1.0]
        phi : float — fricción   [0.0, 1.0)
        name: str   — identificador semántico
    """

    #: Fricción estructural del substrato — no es configurable.
    #: Representa el costo mínimo de existir en el campo de posibilidades.
    PHI_BASE: float = 0.10

    def __init__(self) -> None:
        self.name: str = "L0 — Chaos (Campo de posibilidades)"
        # El campo siempre está presente — L=1.0 es el estado natural de L0.
        self.L: float = 1.0
        # Fricción fija del substrato.
        self.phi: float = self.PHI_BASE

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def get_potential(self, raw_input_quality: float) -> float:
        """
        Retorna el potencial del campo dado un input crudo.
        L0 no filtra — solo clampea al rango válido.

        Args:
            raw_input_quality: Calidad del input crudo [0.0, 1.0]

        Returns:
            float: Potencial neto = input × (1 − φ)
        """
        q = max(0.0, min(1.0, raw_input_quality))
        return q * (1.0 - self.phi)

    def export(self) -> dict:
        """Exporta el estado actual para el motor."""
        return {"L": self.L, "phi": self.phi, "name": self.name}

    def status(self) -> dict:
        """Resumen de estado para diagnóstico."""
        return {
            "layer": self.name,
            "L": self.L,
            "phi": self.phi,
            "note": "Substrato siempre activo. φ fijo = costo de existir.",
        }
