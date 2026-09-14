"""
L1 — CUERPO / HARDWARE
Integridad física del sistema. Sustrato material.

Rol en el framework:
  L1 mide la salud del soporte físico (hardware, energía, red).
  Sin cuerpo no hay sistema. Su fricción (φ=0.02) es la más baja
  de las capas con fricción — el hardware bien mantenido
  introduce muy poco ruido.

Estado honesto:
  L=1.0  — sin datos externos, se asume hardware operativo
  φ=0.02 — fricción mínima del sustrato físico

  Cuando se disponga de métricas reales (CPU, memoria, red),
  llamar activate(L_real, phi_real) para actualizar el estado.

Autor: Ilver Villasmil / Framework Omega
"""

from __future__ import annotations


class BodyLayer:
    """
    Capa L1 — Integridad del sustrato físico.

    Atributos públicos (contrato con el motor):
        L   : float — activación [0.0, 1.0]
        phi : float — fricción   [0.0, 1.0)
        name: str   — identificador semántico
    """

    #: Fricción base del hardware en estado nominal.
    PHI_BASE: float = 0.02

    def __init__(self) -> None:
        self.name: str = "L1 — Body (Integridad física)"
        # Sin datos externos, se asume hardware operativo.
        self.L: float = 1.0
        self.phi: float = self.PHI_BASE

    def activate(self, L: float, phi: float) -> None:
        """Actualiza el estado con métricas reales del hardware."""
        self.L = max(0.0, min(1.0, float(L)))
        self.phi = max(0.0, float(phi))

    def calculate_integrity(
        self, hardware_health: float, energy_stability: float
    ) -> float:
        """
        Calcula la integridad física como media de factores físicos.
        Mantiene compatibilidad con la API original.
        """
        return (
            max(0.0, min(1.0, hardware_health))
            + max(0.0, min(1.0, energy_stability))
        ) / 2.0

    def export(self) -> dict:
        """Exporta el estado actual para el motor."""
        return {"L": self.L, "phi": self.phi, "name": self.name}

    def status(self) -> dict:
        """Resumen de estado para diagnóstico."""
        return {
            "layer": self.name,
            "L": self.L,
            "phi": self.phi,
            "note": "Sustrato físico. L=1.0 = hardware operativo nominal.",
        }
