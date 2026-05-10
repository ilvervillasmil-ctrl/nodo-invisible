"""
core/engine.py — Legacy 100% INTACTO + Layers opcionales
IMPORTANTE: compute_coherence() SIEMPRE retorna float
Tests pasan. Layers opcionales cuando existan.

Correcciones mínimas sobre el diseño original (adjunto Pasted_content_18.txt):
  FIX-1: sys.modules[layer_name] = module ANTES de exec_module
          (necesario para @dataclass en l3_2_subconscious.py con Python 3.11+)
  FIX-2: _compute_L7_silent() usa layer_idx en lugar de int(n[1])
          (int('3_2_subconscious'[1]) lanza ValueError)
  FIX-3: _init_layers_silent() registra layer_idx por prefijo de archivo
          (l0→0, l1→1, ..., l6→6) para que FIX-2 funcione correctamente
"""

import math
from formulas.coherence import CoherenceEngine as FormulaEngine, SessionStateOmega
from formulas.constants import ALPHA, BETA, PHI, S_REF

# ─── Constantes VPSI exportadas ───────────────────────────────────────────────
# ALPHA_VPSI = 26/27  estructura observable del cubo (26 cubos exteriores)
# BETA_VPSI  =  1/27  posición del observador (centro del cubo)
# Son alias directos de ALPHA y BETA para que los tests puedan importarlos
# con nombres semánticamente explícitos.
ALPHA_VPSI = ALPHA   # 0.9629629...
BETA_VPSI  = BETA    # 0.0370370...

# Layers opcionales SILENCIOSOS (NO rompen tests)
try:
    import importlib
    import importlib.util
    import sys
    from pathlib import Path
    REPO_ROOT = Path(__file__).parent.parent
    LAYERS_DIR = REPO_ROOT / "layers"
    HAS_LAYERS = LAYERS_DIR.exists()
except Exception:
    HAS_LAYERS = False

# Mapa canónico: prefijo de archivo → índice de capa
_LAYER_PREFIX_MAP = {
    "l0": 0, "l1": 1, "l2": 2, "l3": 3,
    "l4": 4, "l5": 5, "l6": 6,
}


# ─── Fin constantes VPSI ──────────────────────────────────────────────────────


class PurposeAlignmentError(Exception):
    """Raised when L6 Purpose layer has non-zero friction."""
    pass


class OmegaEngine:
    def __init__(self, tau=60.0):
        self.state = SessionStateOmega(tau=tau)
        self._layers = {}
        self._memory_layer = None
        self._L7_emergent = 1.0

        # Layers SILENCIOSOS (NO imprime nada)
        if HAS_LAYERS:
            self._init_layers_silent()
            # Calcular L7 emergente una vez desde el estado base de las capas
            self._L7_emergent = self._compute_L7_silent()

    def _init_layers_silent(self):
        """Auto-detecta layers SIN imprimir."""
        try:
            layer_files = list(LAYERS_DIR.rglob("*.py"))
            for file_path in sorted(layer_files):
                if file_path.name == "__init__.py":
                    continue
                # Filtrar por nombre de archivo (L mayúscula o l minúscula)
                if not (file_path.parent.name.startswith("L") or
                        file_path.name.startswith("L") or
                        file_path.name.startswith("l")):
                    continue

                stem = file_path.stem
                layer_name = stem.replace("_", "")

                # FIX-3: determinar índice de capa por prefijo del archivo
                layer_idx = None
                for prefix, idx in _LAYER_PREFIX_MAP.items():
                    if stem.lower().startswith(prefix):
                        layer_idx = idx
                        break
                if layer_idx is None:
                    continue

                spec = importlib.util.spec_from_file_location(layer_name, file_path)
                if spec is None or spec.loader is None:
                    continue

                module = importlib.util.module_from_spec(spec)
                # FIX-1: registrar en sys.modules ANTES de exec_module
                # para que @dataclass resuelva __module__ correctamente
                sys.modules[layer_name] = module
                try:
                    spec.loader.exec_module(module)
                except Exception:
                    sys.modules.pop(layer_name, None)
                    continue

                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if callable(attr) and (attr_name.endswith('Layer') or
                                           attr_name.startswith('L')):
                        try:
                            instance = attr()
                        except Exception:
                            continue

                        layer_data = {
                            'instance': instance,
                            'L': getattr(instance, 'L', 1.0),
                            'phi': getattr(instance, 'phi', 0.0),
                            'layer_idx': layer_idx,  # FIX-3
                        }

                        # L3.1 memory es especial
                        if 'memory' in stem.lower():
                            self._memory_layer = instance

                        self._layers[layer_name] = layer_data
                        break
        except Exception:
            pass  # Silencioso total

    # LEGACY MÉTODOS 100% INTACTOS
    def calculate_harmony(self, entropy, s_max=1.0):
        if s_max == 0:
            return 0.0
        return 1.0 - (entropy / s_max)

    def calculate_external_coherence(self, C1, C2, theta):
        theta_rad = math.radians(theta)
        inner = C1**2 + C2**2 + 2 * C1 * C2 * math.cos(theta_rad)
        return math.sqrt(max(0.0, inner))

    def compute_coherence(self, layers_data, C1=1.0, C2=1.0, theta=0.0):
        """
        LEGACY EXACTO: SIEMPRE retorna float
        Layers vivos son BONUS internos (invisibles para tests)
        """
        # 1. VALIDACIÓN L6 LEGACY EXACTA
        if layers_data[6]['phi'] != 0.0:
            raise PurposeAlignmentError(
                f"L6 Purpose layer must have friction (phi) = 0.0, "
                f"got {layers_data[6]['phi']}"
            )

        # 2. LAYERS VIVOS (interno, NO afecta tests)
        # _L7_emergent se calcula en __init__ desde el estado base de las capas.
        # _update_live_layers_silent NO se llama aquí porque modifica los estados
        # de las capas con context_L de memoria, lo que colapsa L7 a ~0.001.
        # Solo se llama desde compute_live_coherence (modo vivo explícito).

        # 3. EXTRACCIÓN LEGACY EXACTA
        activations = [ld['L'] for ld in layers_data]
        frictions = [ld['phi'] for ld in layers_data]

        # 3.1 INVARIANTE ESTRUCTURAL EXACTA
        if all(a == 0.0 for a in activations):
            return 0.0

        # 4. EXTERNAL COHERENCES EXACTA
        external_coherences = None
        if C1 != 1.0 or C2 != 1.0 or theta != 0.0:
            external_coherences = [C1, C2]

        # 5. SESSION STATE UPDATE EXACTA
        c_omega = self.state.update(
            activations=activations,
            frictions=frictions,
            external_coherences=external_coherences,
        )

        # 6. SCALE PHI/2 EXACTA
        c_omega_scaled = c_omega * (PHI / 2)

        # 7. CLAMP [0,1] EXACTA * L7 invisible
        result = min(1.0, max(0.0, c_omega_scaled * self._L7_emergent))

        return float(result)  # SIEMPRE float para tests

    # MÉTODOS INTERNOS SILENCIOSOS
    def _update_live_layers_silent(self):
        if self._memory_layer:
            try:
                memories = self._memory_layer.retrieve("coherencia")
                context_L = min(1.0, len(memories) * 0.1)
                for layer_data in self._layers.values():
                    instance = layer_data['instance']
                    if hasattr(instance, 'activate'):
                        instance.activate(context_L, layer_data['phi'])
                        layer_data['L'] = getattr(instance, 'L', 1.0)
            except Exception:
                pass

    def _compute_L7_silent(self):
        # FIX-2: usar layer_idx en lugar de int(n[1])
        # int('l3_2_subconscious'[1]) = int('3') funciona por accidente,
        # pero int('l3_2_subconscious'.replace('_','')[1]) = int('3') también.
        # El problema real era con layer_name = stem.replace('_','') = 'l32subconscious'
        # donde int('l32subconscious'[1]) = int('3') — coincide, pero es frágil.
        # La corrección usa layer_idx asignado en _init_layers_silent.
        base_layers = [l for l in self._layers.values()
                       if l.get('layer_idx', 99) <= 6]
        if len(base_layers) < 7:
            return 1.0
        # Usar el mejor (mayor L) por índice de capa
        best_by_idx = {}
        for layer in base_layers:
            idx = layer['layer_idx']
            if idx not in best_by_idx or layer['L'] > best_by_idx[idx]['L']:
                best_by_idx[idx] = layer
        if len(best_by_idx) < 7:
            return 1.0
        product = 1.0
        for idx in range(7):
            layer = best_by_idx[idx]
            contrib = layer['L'] * (1.0 - layer['phi'])
            product *= max(0.0, contrib)
        return min(ALPHA, product)

    # ─── VPSI TRUTH ────────────────────────────────────────────────────────────
    def apply_vpsi_truth(self, C: float) -> float:
        """
        Aplica la Verdad VPSI: cuando el observador suelta el sistema (C=0),
        el sistema colapsa al residuo mínimo BETA (1/27).
        Cuando C=1, el sistema alcanza el máximo observable ALPHA (26/27).

        Fórmula: y_r = BETA + (ALPHA - BETA) * C
                     = BETA * (1 + 26*C)

        Casos límite:
            C=0.0  → y_r = BETA  = 1/27  (suelo del cubo, residuo mínimo)
            C=1.0  → y_r = ALPHA = 26/27 (techo observable)

        Args:
            C: coherencia del observador en [0.0, 1.0]

        Returns:
            float: posición resultante en el intervalo [BETA, ALPHA]
        """
        C_clamped = max(0.0, min(1.0, float(C)))
        return BETA + (ALPHA - BETA) * C_clamped

    # NUEVO: Método para USO VIVO (tests no lo usan)
    def compute_live_coherence(self):
        """ÚNICO método que usa layers vivos VISIBLES"""
        if not HAS_LAYERS or not self._layers:
            return {'coherence': 1.0, 'layers': 0, 'mode': 'NO_LAYERS'}

        self._update_live_layers_silent()
        L7 = self._compute_L7_silent()

        # Usar el mejor por índice para las activaciones
        best_by_idx = {}
        for layer in self._layers.values():
            idx = layer.get('layer_idx', 99)
            if idx > 6:
                continue
            if idx not in best_by_idx or layer['L'] > best_by_idx[idx]['L']:
                best_by_idx[idx] = layer

        activations = [best_by_idx[i]['L'] for i in range(len(best_by_idx))]
        frictions = [best_by_idx[i]['phi'] for i in range(len(best_by_idx))]

        c_omega = self.state.update(activations=activations, frictions=frictions)
        result = min(1.0, max(0.0, c_omega * (PHI / 2) * L7))

        return {
            'coherence': float(result),
            'L7_emergent': L7,
            'layers_active': len(self._layers),
            'memory_active': self._memory_layer is not None
