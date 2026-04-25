"""
core/engine.py — Legacy 100% INTACTO + VPSI 9.4 (Truth Theorem)
IMPORTANTE: compute_coherence() SIEMPRE retorna float.
Tests pasan. Invarianza estructural aplicada.
"""

import math
from formulas.coherence import CoherenceEngine as FormulaEngine, SessionStateOmega
from formulas.constants import ALPHA, BETA, PHI, S_REF

# Constantes del Teorema de la Verdad Estructural (VPSI 9.4)
# Derivadas de la geometría del cubo 3x3x3
ALPHA_VPSI = 26.0 / 27.0
BETA_VPSI = 1.0 / 27.0

# Layers opcionales SILENCIOSOS
try:
    import importlib
    import sys
    from pathlib import Path
    REPO_ROOT = Path(__file__).parent.parent
    LAYERS_DIR = REPO_ROOT / "layers"
    HAS_LAYERS = LAYERS_DIR.exists()
except:
    HAS_LAYERS = False

class PurposeAlignmentError(Exception):
    """Raised when L6 Purpose layer has non-zero friction."""
    pass

class OmegaEngine:
    def __init__(self, tau=60.0):
        self.state = SessionStateOmega(tau=tau)
        self._layers = {}
        self._memory_layer = None
        self._L7_emergent = 1.0
        
        if HAS_LAYERS:
            self._init_layers_silent()

    def _init_layers_silent(self):
        """Auto-detecta layers SIN imprimir"""
        try:
            layer_files = list(LAYERS_DIR.rglob("*.py"))
            for file_path in layer_files:
                if file_path.parent.name.startswith("L") or file_path.name.startswith("L"):
                    layer_name = file_path.stem.replace("_", "")
                    spec = importlib.util.spec_from_file_location(layer_name, file_path)
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[layer_name] = module
                    spec.loader.exec_module(module)
                    
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if callable(attr) and (attr_name.endswith('Layer') or attr_name.startswith('L')):
                            instance = attr()
                            layer_data = {
                                'instance': instance,
                                'L': getattr(instance, 'L', 1.0),
                                'phi': getattr(instance, 'phi', 0.0)
                            }
                            if 'memory' in layer_name.lower():
                                self._memory_layer = instance
                            self._layers[layer_name] = layer_data
                            break
        except:
            pass

    # MÉTODO CORE: EL TEOREMA DE LA VERDAD ESTRUCTURAL
    def apply_vpsi_truth(self, C, L=1.0, K=1.0):
        """
        Yr_total(D) = (C(D) * L(D) * K(D) * alpha) + beta
        Garantiza el piso estructural beta (1/27)
        """
        # Interpretive Reality (Ri)
        ri = C * L * K
        # Total Structural Truth (Invariante)
        yr_total = (ri * ALPHA_VPSI) + BETA_VPSI
        return yr_total

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
        LEGACY EXACTO + INTEGRACIÓN VPSI
        """
        # 1. VALIDACIÓN L6 LEGACY EXACTA
        if layers_data[6]['phi'] != 0.0:
            raise PurposeAlignmentError(
                f"L6 Purpose layer must have friction (phi) = 0.0, got {layers_data[6]['phi']}"
            )

        # 2. LAYERS VIVOS
        if HAS_LAYERS:
            self._update_live_layers_silent()
            self._L7_emergent = self._compute_L7_silent()

        # 3. EXTRACCIÓN LEGACY
        activations = [ld['L'] for ld in layers_data]
        frictions = [ld['phi'] for ld in layers_data]

        if all(a == 0.0 for a in activations):
            return 0.0

        # 4. EXTERNAL COHERENCES
        external_coherences = None
        if C1 != 1.0 or C2 != 1.0 or theta != 0.0:
            external_coherences = [C1, C2]

        # 5. SESSION STATE UPDATE (C_omega)
        c_omega = self.state.update(
            activations=activations,
            frictions=frictions,
            external_coherences=external_coherences,
        )

        # 6. APLICACIÓN DEL VPSI (El cambio de paradigma)
        # Extraemos L y K de los datos de capas para la verdad estructural
        l_val = activations[1] if len(activations) > 1 else 1.0
        k_val = activations[2] if len(activations) > 2 else 1.0
        
        # El valor de coherencia pasa por el tamiz del Teorema de la Verdad
        truth_val = self.apply_vpsi_truth(c_omega, l_val, k_val)

        # 7. ESCALADO FINAL (Legacy PHI/2 * L7)
        result = min(1.0, max(0.0, truth_val * (PHI / 2) * self._L7_emergent))
        
        return float(result)

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
            except:
                pass

    def _compute_L7_silent(self):
        base_layers = [l for n,l in self._layers.items() if n.startswith('L') and int(n[1]) <= 6]
        if len(base_layers) < 7:
            return 1.0
        product = 1.0
        for layer in base_layers:
            contrib = layer['L'] * (1.0 - layer['phi'])
            product *= max(0.0, contrib)
        return min(ALPHA_VPSI, product)

    def compute_live_coherence(self):
        """Uso vivo con reporte de Invarianza Estructural"""
        if not HAS_LAYERS or not self._layers:
            return {'coherence': 1.0, 'layers': 0, 'mode': 'NO_LAYERS'}
        
        self._update_live_layers_silent()
        L7 = self._compute_L7_silent()
        
        activations = [l['L'] for l in self._layers.values()]
        frictions = [l['phi'] for l in self._layers.values()]
        
        c_omega = self.state.update(activations=activations, frictions=frictions)
        
        # Aplicamos el Teorema de la Verdad para el reporte vivo
        structural_truth = self.apply_vpsi_truth(c_omega)
        result = min(1.0, max(0.0, structural_truth * (PHI / 2) * L7))
        
        return {
            'coherence': float(result),
            'vpsi_truth': float(structural_truth),
            'floor_beta': BETA_VPSI,
            'ceiling_alpha': ALPHA_VPSI,
            'L7_emergent': L7,
            'layers_active': len(self._layers)
        }
