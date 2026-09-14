"""
L5 — Meta-Observador
====================
El sistema observándose a sí mismo. L5 mide la capacidad del framework de
detectar sus propios errores y reportarlos con precisión.

Principio de diseño:
    El meta-observador no puede fingir que ve más de lo que ve.
    Lo que el sistema SÍ puede observar de sí mismo sin sesión externa:
      1. Tasa de tests pasando (el sistema se auto-verifica)
      2. Cobertura de la suite de tests (qué fracción del sistema está observada)
    L5 = tasa de tests pasando (desde pytest cache si existe, 0.9 conservador si no).
    phi = 1 - L.

Fricción base:
    phi = 0.0 cuando todos los tests pasan (observación perfecta).
    phi > 0 cuando hay tests fallando (puntos ciegos del observador).
"""

import json
from pathlib import Path
from typing import Optional


def _read_pass_rate_from_cache() -> float:
    """
    Lee la tasa de tests pasando desde el cache de pytest.
    Si no existe el cache, retorna 0.9 como valor conservador honesto
    (el sistema no puede afirmar que pasa el 100% sin haberlo verificado).
    """
    root = Path(__file__).resolve().parent.parent
    nodeids_path = root / ".pytest_cache" / "v" / "cache" / "nodeids"
    lastfailed_path = root / ".pytest_cache" / "v" / "cache" / "lastfailed"

    try:
        if nodeids_path.exists() and lastfailed_path.exists():
            nodeids = json.loads(nodeids_path.read_text())
            lastfailed = json.loads(lastfailed_path.read_text())
            total = len(nodeids)
            failed = len(lastfailed)
            if total > 0:
                return (total - failed) / total
        # Cache existe pero sin lastfailed → todos pasaron en el último run
        if nodeids_path.exists():
            nodeids = json.loads(nodeids_path.read_text())
            if len(nodeids) > 0:
                return 1.0
    except Exception:
        pass

    # Sin cache: valor conservador honesto — no afirmamos 100% sin evidencia
    return 0.9


class LayerMeta:
    """
    L5 — Meta-Observador.

    Auto-inicialización: lee la tasa de tests pasando desde el cache de pytest.
    L = pass_rate.
    phi = 1 - L.

    Contrato con el motor:
        - L ∈ [0, 1]
        - phi ≥ 0
        - activate(L, phi) sobreescribe con valores externos cuando existen.

    Represents the system's ability to watch its own processes.
    """

    def __init__(self, lower_layers: Optional[list] = None):
        """
        Parámetros
        ----------
        lower_layers : no usado en L5 (meta-observación es sobre el sistema completo).
                       Aceptado por compatibilidad con el contrato de discover_layer_states.
        """
        self.name = "Meta-Observer"
        pass_rate = _read_pass_rate_from_cache()
        self.L = max(0.0, min(1.0, pass_rate))
        self.phi = round(1.0 - self.L, 6)

    def activate(self, L: float, phi: float) -> None:
        """
        Activates L5.
        Represents the system's ability to watch its own processes.
        Sobreescribe con valores externos cuando hay sesión activa.
        """
        self.L = max(0.0, min(1.0, float(L)))
        self.phi = max(0.0, float(phi))

    def export(self) -> dict:
        return {"L": self.L, "phi": self.phi, "name": self.name}
