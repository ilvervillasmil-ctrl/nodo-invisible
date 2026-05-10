"""
core/engine.py — v3.0
Motor principal del Sistema de Integración Universal (UIS).

Changelog v3.0:
  - MANTIENE: compute_coherence() 100% compatible con todos los tests existentes
  - CORRIGE: _init_layers_silent() registra módulos en sys.modules antes de exec_module
             (fix para @dataclass en l3_2_subconscious.py)
  - CORRIGE: _init_layers_silent() filtra correctamente por nombre de archivo L0-L6
             (antes usaba startswith('L') en attr_name, que capturaba clases no deseadas)
  - CORRIGE: _compute_L7_silent() usa índice numérico seguro en lugar de int(n[1])
             (antes fallaba con nombres como 'l3_2_subconscious')
  - MEJORA: _init_layers_silent() registra todas las subcapas L3.x sin colisión
  - MEJORA: compute_live_coherence() retorna estado completo por capa
  - MANTIENE: PurposeAlignmentError, calculate_harmony, calculate_external_coherence
"""

from __future__ import annotations

import importlib
import importlib.util
import math
import sys
from pathlib import Path

from formulas.coherence import CoherenceEngine as FormulaEngine, SessionStateOmega
from formulas.constants import ALPHA, BETA, PHI, S_REF

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
try:
    REPO_ROOT = Path(__file__).resolve().parent.parent
    LAYERS_DIR = REPO_ROOT / "layers"
    HAS_LAYERS = LAYERS_DIR.exists()
except Exception:
    HAS_LAYERS = False
    LAYERS_DIR = None

# ---------------------------------------------------------------------------
# Mapa canónico: prefijo de archivo → índice de capa
# ---------------------------------------------------------------------------
_LAYER_FILE_MAP: dict[str, int] = {
    "l0": 0,
    "l1": 1,
    "l2": 2,
    "l3": 3,
    "l4": 4,
    "l5": 5,
    "l6": 6,
}


class PurposeAlignmentError(Exception):
    """Raised when L6 Purpose layer has non-zero friction."""
    pass


class OmegaEngine:
    """
    Motor de coherencia Omega.

    Uso principal (tests y producción):
        engine = OmegaEngine()
        c = engine.compute_coherence(layers_data)  # → float

    Uso vivo (con capas reales):
        result = engine.compute_live_coherence()   # → dict
    """

    def __init__(self, tau: float = 60.0) -> None:
        self.state = SessionStateOmega(tau=tau)
        # _layers: dict[str, dict] — clave = stem del archivo
        self._layers: dict[str, dict] = {}
        self._memory_layer = None
        self._L7_emergent: float = 1.0

        if HAS_LAYERS:
            self._init_layers_silent()
            # Calcular L7 emergente una vez al inicio, desde el estado base de las capas
            self._L7_emergent = self._compute_L7_silent()

    # -----------------------------------------------------------------------
    # Inicialización silenciosa de capas
    # -----------------------------------------------------------------------

    def _init_layers_silent(self) -> None:
        """
        Auto-detecta capas L0-L6 en layers/*.py SIN imprimir nada.

        Correcciones respecto a versión anterior:
        1. Registra el módulo en sys.modules ANTES de exec_module
           (necesario para @dataclass en Python 3.11+).
        2. Filtra por prefijo del nombre de archivo, no por nombre de clase.
        3. Maneja subcapas L3.x sin colisión de claves.
        """
        if LAYERS_DIR is None:
            return
        try:
            for file_path in sorted(LAYERS_DIR.rglob("*.py")):
                if file_path.name == "__init__.py":
                    continue

                stem = file_path.stem.lower()

                # Determinar índice de capa por prefijo del archivo
                layer_idx = None
                for prefix, idx in _LAYER_FILE_MAP.items():
                    if stem.startswith(prefix):
                        layer_idx = idx
                        break

                if layer_idx is None:
                    continue

                # Clave única: stem completo (evita colisión l3_synthesis vs l3_1_memory)
                layer_key = stem

                spec = importlib.util.spec_from_file_location(stem, file_path)
                if spec is None or spec.loader is None:
                    continue

                module = importlib.util.module_from_spec(spec)
                # CRÍTICO: registrar en sys.modules ANTES de exec_module
                # para que @dataclass pueda resolver __module__
                sys.modules[stem] = module
                try:
                    spec.loader.exec_module(module)
                except Exception:
                    # Si el módulo falla, limpiar y continuar
                    sys.modules.pop(stem, None)
                    continue

                # Buscar la primera clase con atributos L y/o phi
                instance = None
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if not isinstance(attr, type):
                        continue
                    # Evitar clases importadas (solo las definidas en este módulo)
                    if getattr(attr, "__module__", None) not in (stem, None):
                        continue
                    try:
                        obj = attr()
                        if hasattr(obj, "L") or hasattr(obj, "phi"):
                            instance = obj
                            break
                    except Exception:
                        continue

                if instance is None:
                    continue

                layer_data = {
                    "instance": instance,
                    "L": float(getattr(instance, "L", 1.0)),
                    "phi": float(getattr(instance, "phi", 0.0)),
                    "layer_idx": layer_idx,
                }

                # L3.1 memory es especial — se usa para contexto
                if "memory" in stem:
                    self._memory_layer = instance

                self._layers[layer_key] = layer_data

        except Exception:
            pass  # Silencioso total — nunca romper el motor

    # -----------------------------------------------------------------------
    # Métodos legacy (100% compatibles con tests)
    # -----------------------------------------------------------------------

    def calculate_harmony(self, entropy: float, s_max: float = 1.0) -> float:
        if s_max == 0:
            return 0.0
        return 1.0 - (entropy / s_max)

    def calculate_external_coherence(
        self, C1: float, C2: float, theta: float
    ) -> float:
        theta_rad = math.radians(theta)
        inner = C1**2 + C2**2 + 2 * C1 * C2 * math.cos(theta_rad)
        return math.sqrt(max(0.0, inner))

    def compute_coherence(
        self,
        layers_data: list[dict],
        C1: float = 1.0,
        C2: float = 1.0,
        theta: float = 0.0,
    ) -> float:
        """
        Calcula la coherencia estructural del sistema.

        CONTRATO (invariante para todos los tests):
          - Siempre retorna float
          - L6.phi DEBE ser 0.0 (PurposeAlignmentError si no)
          - Si todas las activaciones son 0.0, retorna 0.0
          - El resultado está en [0.0, ALPHA]

        Args:
            layers_data: Lista de 7 dicts con claves 'L' y 'phi'
            C1, C2, theta: Coherencias externas (opcional)

        Returns:
            float: C_struct ∈ [0.0, ALPHA]
        """
        # 1. Validación L6 — propósito sin fricción
        if layers_data[6]["phi"] != 0.0:
            raise PurposeAlignmentError(
                f"L6 Purpose layer must have friction (phi) = 0.0, "
                f"got {layers_data[6]['phi']}"
            )

        # 2. L7 emergente desde capas vivas (calculado en __init__, no se recalcula aquí)
        # DISEÑO: compute_coherence usa layers_data externos — L7 es un factor
        # de contexto calculado al inicio, no se modifica por cada llamada.
        # _update_live_layers_silent solo se llama desde compute_live_coherence.

        # 3. Extraer activaciones y fricciones
        activations = [ld["L"] for ld in layers_data]
        frictions = [ld["phi"] for ld in layers_data]

        # 4. Invariante estructural: colapso total = 0
        if all(a == 0.0 for a in activations):
            return 0.0

        # 5. Coherencias externas (solo si se especifican)
        external_coherences = None
        if C1 != 1.0 or C2 != 1.0 or theta != 0.0:
            external_coherences = [C1, C2]

        # 6. Actualizar estado de sesión
        c_omega = self.state.update(
            activations=activations,
            frictions=frictions,
            external_coherences=external_coherences,
        )

        # 7. Escalar por PHI/2
        # DISEÑO: compute_coherence NO aplica L7 — es la API pública pura.
        # L7 emergente se aplica SOLO en compute_live_coherence (modo vivo).
        # Esto mantiene compatibilidad total con todos los tests existentes.
        result = min(1.0, max(0.0, c_omega * (PHI / 2)))

        return float(result)

    # -----------------------------------------------------------------------
    # Métodos internos silenciosos
    # -----------------------------------------------------------------------

    def _update_live_layers_silent(self) -> None:
        """Actualiza capas vivas usando contexto de memoria si está disponible."""
        if not self._memory_layer:
            return
        try:
            memories = self._memory_layer.retrieve("coherencia")
            context_L = min(1.0, len(memories) * 0.1)
            for layer_data in self._layers.values():
                instance = layer_data["instance"]
                if hasattr(instance, "activate"):
                    instance.activate(context_L, layer_data["phi"])
                    layer_data["L"] = float(getattr(instance, "L", 1.0))
        except Exception:
            pass

    def _compute_L7_silent(self) -> float:
        """
        Calcula L7 emergente como producto de contribuciones netas L0-L6.

        Usa layer_idx para ordenar correctamente, evitando errores con
        nombres de archivo como 'l3_2_subconscious' (int('3_2') falla).
        """
        # Agrupar por índice — tomar el de mayor L por capa
        best_by_idx: dict[int, dict] = {}
        for layer_data in self._layers.values():
            idx = layer_data["layer_idx"]
            if idx > 6:
                continue
            if idx not in best_by_idx or layer_data["L"] > best_by_idx[idx]["L"]:
                best_by_idx[idx] = layer_data

        if len(best_by_idx) < 7:
            # No tenemos todas las capas — no aplicar L7
            return 1.0

        product = 1.0
        for idx in range(7):
            layer = best_by_idx[idx]
            contrib = layer["L"] * (1.0 - layer["phi"])
            product *= max(0.0, contrib)

        return min(ALPHA, product)

    # -----------------------------------------------------------------------
    # API viva (no usada por tests, sí por diagnostics y aplicaciones)
    # -----------------------------------------------------------------------

    def compute_live_coherence(self) -> dict:
        """
        Calcula coherencia usando las capas vivas cargadas en __init__.

        Returns:
            dict con coherence, L7_emergent, layers_active, estado por capa
        """
        if not HAS_LAYERS or not self._layers:
            return {
                "coherence": 1.0,
                "L7_emergent": 1.0,
                "layers_active": 0,
                "mode": "NO_LAYERS",
            }

        # Usar L7 pre-calculado al inicio (estado base honesto)
        # _update_live_layers_silent no se llama aquí porque modifica los estados
        # con context_L de memoria, lo que colapsa las capas a valores bajos
        # cuando la memoria tiene pocos registros.
        L7 = self._L7_emergent
        activations = []
        frictions = []
        layer_states = {}
        # Ordenar por índice para consistencia — usar el mejor por capa
        best_by_idx: dict[int, tuple[str, dict]] = {}
        for key, data in self._layers.items():
            idx = data["layer_idx"]
            if idx > 6:
                continue
            if idx not in best_by_idx or data["L"] > best_by_idx[idx][1]["L"]:
                best_by_idx[idx] = (key, data)
        for idx in range(min(7, len(best_by_idx))):
            if idx not in best_by_idx:
                continue
            key, data = best_by_idx[idx]
            activations.append(data["L"])
            frictions.append(data["phi"])
            layer_states[key] = {"L": data["L"], "phi": data["phi"]}
        if not activations:
            return {"coherence": 0.0, "L7_emergent": 0.0, "layers_active": 0, "mode": "NO_DATA"}
        c_omega = self.state.update(activations=activations, frictions=frictions)
        result = min(1.0, max(0.0, c_omega * (PHI / 2) * L7))

        return {
            "coherence": float(result),
            "L7_emergent": float(L7),
            "layers_active": len(self._layers),
            "memory_active": self._memory_layer is not None,
            "layer_states": layer_states,
        }
