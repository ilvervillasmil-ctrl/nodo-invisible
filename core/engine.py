"""
core/engine.py — Legacy + VPSI 9.4 Truth Theorem + Anti-Circularity Guard
compute_coherence() SIEMPRE retorna float.
Invarianza estructural aplicada.
"""

import math
from formulas.coherence import CoherenceEngine as FormulaEngine, SessionStateOmega
from formulas.constants import ALPHA, BETA, PHI, S_REF

ALPHA_VPSI = 26.0 / 27.0
BETA_VPSI = 1.0 / 27.0
EPSILON = 1e-12


try:
    import importlib
    import sys
    from pathlib import Path

    REPO_ROOT = Path(__file__).parent.parent
    LAYERS_DIR = REPO_ROOT / "layers"
    HAS_LAYERS = LAYERS_DIR.exists()
except Exception:
    HAS_LAYERS = False


class PurposeAlignmentError(Exception):
    """Raised when L6 Purpose layer has non-zero friction."""
    pass


class StructuralIntegrityError(Exception):
    """Raised when incoming data violates VPSI structural invariance."""
    pass


class CircularityDetectedError(Exception):
    """Raised when circular references or circular formula feedback are detected."""
    pass


class OmegaEngine:
    def __init__(self, tau=60.0):
        self.state = SessionStateOmega(tau=tau)
        self._layers = {}
        self._memory_layer = None
        self._L7_emergent = 1.0

        if HAS_LAYERS:
            self._init_layers_silent()

    # ============================================================
    # ANTI-HACK / STRUCTURAL GUARD
    # ============================================================

    def _is_finite_number(self, value):
        return isinstance(value, (int, float)) and math.isfinite(value)

    def _detect_reference_cycle(self, obj, seen=None, path="root"):
        """
        Detecta circularidad real de objetos:
        ejemplo: a = []; a.append(a)
        """
        if seen is None:
            seen = set()

        if isinstance(obj, (dict, list, tuple, set)):
            obj_id = id(obj)

            if obj_id in seen:
                raise CircularityDetectedError(
                    f"Circular reference detected at {path}."
                )

            seen.add(obj_id)

            if isinstance(obj, dict):
                for key, value in obj.items():
                    self._detect_reference_cycle(value, seen, f"{path}.{key}")
            else:
                for i, value in enumerate(obj):
                    self._detect_reference_cycle(value, seen, f"{path}[{i}]")

            seen.remove(obj_id)

    def _validate_layer_data(self, layers_data):
        """
        Valida que layers_data cumpla estructura base:
        - lista
        - exactamente 7 capas
        - cada capa es dict
        - cada capa tiene L y phi
        - L y phi son números finitos
        - L ∈ [0,1]
        - phi ∈ [0,1]
        """
        self._detect_reference_cycle(layers_data)

        if not isinstance(layers_data, list):
            raise TypeError("layers_data must be a list of 7 layer dictionaries.")

        if len(layers_data) != 7:
            raise ValueError(
                f"layers_data must contain exactly 7 layers, got {len(layers_data)}."
            )

        for i, layer in enumerate(layers_data):
            if not isinstance(layer, dict):
                raise TypeError(f"Layer L{i} must be a dictionary.")

            if "L" not in layer:
                raise KeyError(f"Layer L{i} is missing required key 'L'.")

            if "phi" not in layer:
                raise KeyError(f"Layer L{i} is missing required key 'phi'.")

            L = layer["L"]
            phi = layer["phi"]

            if not self._is_finite_number(L):
                raise StructuralIntegrityError(
                    f"Layer L{i} activation must be a finite number, got {L}."
                )

            if not self._is_finite_number(phi):
                raise StructuralIntegrityError(
                    f"Layer L{i} friction phi must be a finite number, got {phi}."
                )

            if not 0.0 <= L <= 1.0:
                raise StructuralIntegrityError(
                    f"Layer L{i} activation violates domain [0,1], got {L}."
                )

            if not 0.0 <= phi <= 1.0:
                raise StructuralIntegrityError(
                    f"Layer L{i} friction phi violates domain [0,1], got {phi}."
                )

        if layers_data[6]["phi"] != 0.0:
            raise PurposeAlignmentError(
                f"L6 Purpose layer must have friction phi = 0.0, got {layers_data[6]['phi']}."
            )

    def _validate_external_inputs(self, C1, C2, theta):
        for name, value in {"C1": C1, "C2": C2, "theta": theta}.items():
            if not self._is_finite_number(value):
                raise StructuralIntegrityError(
                    f"{name} must be a finite number, got {value}."
                )

        if C1 < 0.0 or C2 < 0.0:
            raise StructuralIntegrityError(
                f"External coherences must be non-negative, got C1={C1}, C2={C2}."
            )

    def _assert_truth_formula(self, C, L, K, truth_value):
        """
        Anti-manipulación:
        verifica que la salida cumpla exactamente la fórmula base:

        Truth_total = beta + alpha * C * L * K
        """
        expected = BETA_VPSI + (ALPHA_VPSI * C * L * K)

        if abs(truth_value - expected) > EPSILON:
            raise StructuralIntegrityError(
                f"Truth formula violation: expected {expected}, got {truth_value}."
            )

        if truth_value < BETA_VPSI - EPSILON:
            raise StructuralIntegrityError(
                f"Truth value below structural floor beta: {truth_value}."
            )

        if truth_value > 1.0 + EPSILON:
            raise StructuralIntegrityError(
                f"Truth value above structural ceiling 1: {truth_value}."
            )

    def _detect_formula_circularity(self, c_omega, truth_value):
        """
        Detecta circularidad funcional simple:
        el sistema no debe usar Truth_total como si fuera C_omega de entrada.
        """
        if abs(c_omega - truth_value) <= EPSILON and c_omega not in (0.0, 1.0):
            raise CircularityDetectedError(
                "Formula circularity detected: CΩ and Truth_total collapsed into same value."
            )

    # ============================================================
    # LAYERS
    # ============================================================

    def _init_layers_silent(self):
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
                        if callable(attr) and (
                            attr_name.endswith("Layer") or attr_name.startswith("L")
                        ):
                            instance = attr()
                            layer_data = {
                                "instance": instance,
                                "L": getattr(instance, "L", 1.0),
                                "phi": getattr(instance, "phi", 0.0),
                            }
                            if "memory" in layer_name.lower():
                                self._memory_layer = instance
                            self._layers[layer_name] = layer_data
                            break
        except Exception:
            pass

    def _update_live_layers_silent(self):
        if self._memory_layer:
            try:
                memories = self._memory_layer.retrieve("coherencia")
                context_L = min(1.0, len(memories) * 0.1)

                for layer_data in self._layers.values():
                    instance = layer_data["instance"]
                    if hasattr(instance, "activate"):
                        instance.activate(context_L, layer_data["phi"])
                        layer_data["L"] = getattr(instance, "L", 1.0)
            except Exception:
                pass

    def _compute_L7_silent(self):
        try:
            base_layers = [
                l for n, l in self._layers.items()
                if n.startswith("L") and int(n[1]) <= 6
            ]
        except Exception:
            return 1.0

        if len(base_layers) < 6:
            return 1.0

        product = 1.0
        for layer in base_layers:
            contrib = layer["L"] * (1.0 - layer["phi"])
            product *= max(0.0, contrib)

        return min(ALPHA_VPSI, product)

    # ============================================================
    # VPSI TRUTH THEOREM
    # ============================================================

    def apply_vpsi_truth(self, C, L=1.0, K=1.0):
        """
        Truth_total(D) = beta + alpha * C(D) * L(D) * K(D)
        """
        for name, value in {"C": C, "L": L, "K": K}.items():
            if not self._is_finite_number(value):
                raise StructuralIntegrityError(
                    f"{name} must be a finite number, got {value}."
                )

            if not 0.0 <= value <= 1.0:
                raise StructuralIntegrityError(
                    f"{name} violates domain [0,1], got {value}."
                )

        ri = C * L * K
        truth_total = BETA_VPSI + (ALPHA_VPSI * ri)

        self._assert_truth_formula(C, L, K, truth_total)

        return float(truth_total)

    # ============================================================
    # LEGACY METHODS
    # ============================================================

    def calculate_harmony(self, entropy, s_max=1.0):
        if not self._is_finite_number(entropy):
            raise StructuralIntegrityError(f"entropy must be finite, got {entropy}.")

        if not self._is_finite_number(s_max):
            raise StructuralIntegrityError(f"s_max must be finite, got {s_max}.")

        if s_max == 0:
            return 0.0

        return float(1.0 - (entropy / s_max))

    def calculate_external_coherence(self, C1, C2, theta):
        self._validate_external_inputs(C1, C2, theta)

        theta_rad = math.radians(theta)
        inner = C1**2 + C2**2 + 2.0 * C1 * C2 * math.cos(theta_rad)

        return float(math.sqrt(max(0.0, inner)))

    def compute_coherence(self, layers_data, C1=1.0, C2=1.0, theta=0.0):
        """
        Core deterministic computation.
        Siempre retorna float si las entradas respetan la estructura.
        """
        self._validate_layer_data(layers_data)
        self._validate_external_inputs(C1, C2, theta)

        if HAS_LAYERS:
            self._update_live_layers_silent()
            self._L7_emergent = self._compute_L7_silent()

        activations = [float(ld["L"]) for ld in layers_data]
        frictions = [float(ld["phi"]) for ld in layers_data]

        if all(a == 0.0 for a in activations):
            return 0.0

        external_coherences = None
        if C1 != 1.0 or C2 != 1.0 or theta != 0.0:
            i_ext = self.calculate_external_coherence(C1, C2, theta)
            external_coherences = [i_ext]

        c_omega = self.state.update(
            activations=activations,
            frictions=frictions,
            external_coherences=external_coherences,
        )

        if not self._is_finite_number(c_omega):
            raise StructuralIntegrityError(f"CΩ must be finite, got {c_omega}.")

        c_omega = min(ALPHA_VPSI, max(0.0, float(c_omega)))

        l_val = activations[1] if len(activations) > 1 else 1.0
        k_val = activations[2] if len(activations) > 2 else 1.0

        truth_val = self.apply_vpsi_truth(c_omega, l_val, k_val)

        self._detect_formula_circularity(c_omega, truth_val)

        # No doble escalado de CΩ.
        # CΩ ya viene escalado desde formulas.coherence.
        # Aquí solo se aplica VPSI + L7 emergente.
        result = truth_val * self._L7_emergent
        result = min(1.0, max(0.0, result))

        return float(result)

    def compute_live_coherence(self):
        if not HAS_LAYERS or not self._layers:
            return {
                "coherence": 1.0,
                "layers": 0,
                "mode": "NO_LAYERS",
            }

        self._update_live_layers_silent()
        L7 = self._compute_L7_silent()

        activations = [float(l["L"]) for l in self._layers.values()]
        frictions = [float(l["phi"]) for l in self._layers.values()]

        c_omega = self.state.update(
            activations=activations,
            frictions=frictions,
        )

        c_omega = min(ALPHA_VPSI, max(0.0, float(c_omega)))

        structural_truth = self.apply_vpsi_truth(c_omega)

        self._detect_formula_circularity(c_omega, structural_truth)

        result = structural_truth * L7
        result = min(1.0, max(0.0, result))

        return {
            "coherence": float(result),
            "vpsi_truth": float(structural_truth),
            "floor_beta": BETA_VPSI,
            "ceiling_alpha": ALPHA_VPSI,
            "L7_emergent": float(L7),
            "layers_active": len(self._layers),
        }
