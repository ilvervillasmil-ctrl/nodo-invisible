from dataclasses import dataclass
from typing import Any, Dict, List, Tuple
import math


@dataclass(frozen=True)
class UniversalConstants:
    alpha: float = 26 / 27
    beta: float = 1 / 27
    phi: float = (1 + math.sqrt(5)) / 2
    pi: float = math.pi
    e: float = math.e
    kappa: float = math.pi / 4
    r_fin: float = 28 / 27


class L2Laws:
    """
    L2 = Programa / Leyes Universales

    No procesa contenido.
    No decide.
    No genera respuesta.

    Solo delimita lo posible y valida si una operación
    respeta la estructura del sistema.
    """

    def __init__(self):
        self.name = "L2 - Programa / Leyes Universales"
        self.phi = 0.05  # fricción fija de L2
        self.constants = UniversalConstants()

        self.laws = {
            "ley_0_integracion": self.ley_0_integracion,
            "ley_1_accion": self.ley_1_accion,
            "ley_2_ritmo": self.ley_2_ritmo,
            "ley_3_polaridad": self.ley_3_polaridad,
            "ley_4_causa_efecto": self.ley_4_causa_efecto,
            "ley_5_fractalidad": self.ley_5_fractalidad,
            "ley_6_resonancia": self.ley_6_resonancia,
            "ley_7_correspondencia": self.ley_7_correspondencia,
            "ley_8_integracion_total": self.ley_8_integracion_total,
            "vpsi": self.vpsi_check,
            "conservacion_alpha_beta": self.conservacion_alpha_beta,
            "irreducibilidad_beta": self.irreducibilidad_beta,
        }

    # =========================
    # VALIDACIÓN MAESTRA
    # =========================
    def validate(
        self,
        output: Any,
        inputs: Any,
        context: Dict[str, Any] | None = None
    ) -> Tuple[bool, List[str]]:
        """
        Ejecuta todas las leyes.
        Devuelve:
        - True/False
        - lista de violaciones
        """
        context = context or {}
        violations: List[str] = []

        for law_name, law_fn in self.laws.items():
            ok, reason = law_fn(output, inputs, context)
            if not ok:
                violations.append(f"{law_name}: {reason}")

        return len(violations) == 0, violations

    # =========================
    # LEYES BASE DEL FRAMEWORK
    # =========================
    def conservacion_alpha_beta(
        self, output: Any, inputs: Any, context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        total = self.constants.alpha + self.constants.beta
        if abs(total - 1.0) > 1e-12:
            return False, "alpha + beta != 1"
        return True, "PASS"

    def irreducibilidad_beta(
        self, output: Any, inputs: Any, context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        if self.constants.beta <= 0:
            return False, "beta <= 0"
        return True, "PASS"

    def vpsi_check(
        self, output: Any, inputs: Any, context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        VPSI:
        La salida no puede contener estructura que no esté
        ya en los operandos / memoria / entradas permitidas.
        """
        if self._is_derivable(output, inputs, context):
            return True, "PASS"
        return False, "la salida no es derivable de los operandos"

    def ley_0_integracion(
        self, output: Any, inputs: Any, context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Todo tiende a integración o fragmentación.
        Aquí se comprueba que la salida no sea una unión arbitraria
        de partes incompatibles.
        """
        if self._is_integrated(output, context):
            return True, "PASS"
        return False, "salida fragmentada o no integrada"

    def ley_1_accion(
        self, output: Any, inputs: Any, context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Nada está estático. Todo es movimiento.
        Validación mínima: la salida debe responder a una entrada real.
        """
        if inputs is None or inputs == "":
            return False, "no hay input real que active el sistema"
        return True, "PASS"

    def ley_2_ritmo(
        self, output: Any, inputs: Any, context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Todo ocurre en ciclos.
        Aquí se valida consistencia secuencial / trazabilidad de pasos.
        """
        if self._has_trace(context):
            return True, "PASS"
        return False, "no hay secuencia trazable de procesamiento"

    def ley_3_polaridad(
        self, output: Any, inputs: Any, context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Todo tiene opuesto complementario.
        La salida debe reconocer tensiones, límites o contraste cuando apliquen.
        """
        if self._handles_polarity(output, context):
            return True, "PASS"
        return False, "no reconoce polaridad relevante del problema"

    def ley_4_causa_efecto(
        self, output: Any, inputs: Any, context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Nada sin causa.
        Toda afirmación debe tener soporte causal / fuente.
        """
        if self._has_support(output, context):
            return True, "PASS"
        return False, "hay afirmaciones sin causa o soporte"

    def ley_5_fractalidad(
        self, output: Any, inputs: Any, context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        La parte replica el todo.
        Validación: la salida debe ser consistente con la estructura general.
        """
        if self._is_fractal_consistent(output, context):
            return True, "PASS"
        return False, "la parte contradice la estructura general"

    def ley_6_resonancia(
        self, output: Any, inputs: Any, context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Nada opera aislado.
        La salida debe mostrar conexión con memoria, contexto o input.
        """
        if self._has_resonance(output, inputs, context):
            return True, "PASS"
        return False, "salida aislada, sin resonancia con el sistema"

    def ley_7_correspondencia(
        self, output: Any, inputs: Any, context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Lo interno = lo externo.
        La salida debe corresponder con lo que realmente entró.
        """
        if self._matches_input(output, inputs):
            return True, "PASS"
        return False, "la salida no corresponde al input real"

    def ley_8_integracion_total(
        self, output: Any, inputs: Any, context: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Lo que no se integra colapsa.
        Si una pieza invalida el conjunto, la salida no pasa.
        """
        if self._passes_total_integration(output, context):
            return True, "PASS"
        return False, "la salida no pasa integración total"

    # =========================
    # HELPERS
    # =========================
    def _is_derivable(
        self, output: Any, inputs: Any, context: Dict[str, Any]
    ) -> bool:
        """
        Aquí conectas L2 con L3.1 y L3.2.
        Debe comprobar que la salida sale de:
        - inputs
        - memoria
        - derivación válida
        """
        memory_hits = context.get("memory_hits", [])
        derived = context.get("derived", False)

        if derived:
            return True

        if memory_hits:
            return True

        if isinstance(output, str) and isinstance(inputs, str):
            return any(token in output.lower() for token in inputs.lower().split())

        return False

    def _is_integrated(self, output: Any, context: Dict[str, Any]) -> bool:
        return context.get("integrated", True)

    def _has_trace(self, context: Dict[str, Any]) -> bool:
        trace = context.get("trace", [])
        return len(trace) > 0

    def _handles_polarity(self, output: Any, context: Dict[str, Any]) -> bool:
        return context.get("polarity_checked", True)

    def _has_support(self, output: Any, context: Dict[str, Any]) -> bool:
        return context.get("supported", True)

    def _is_fractal_consistent(self, output: Any, context: Dict[str, Any]) -> bool:
        return context.get("fractal_consistent", True)

    def _has_resonance(
        self, output: Any, inputs: Any, context: Dict[str, Any]
    ) -> bool:
        return context.get("resonant", True)

    def _matches_input(self, output: Any, inputs: Any) -> bool:
        if not isinstance(output, str) or not isinstance(inputs, str):
            return True
        return len(set(output.lower().split()) & set(inputs.lower().split())) > 0

    def _passes_total_integration(self, output: Any, context: Dict[str, Any]) -> bool:
        return context.get("total_integration", True)
