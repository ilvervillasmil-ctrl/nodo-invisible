"""
diagnostics.py
=========================================================
MASTER DIAGNOSTIC ENGINE
Single Source of Truth
Anti-Hardcoded
Self-Audited
=========================================================
"""

from dataclasses import dataclass
from core.constants import ALPHA, BETA

# ==========================================================
# PHYSICAL CONSTANTS
# ==========================================================

CRITICAL_THRESHOLD = 0.450000000000
DANGER_THRESHOLD  = 0.370000000000

# ==========================================================
# STATE
# ==========================================================

@dataclass(frozen=True)
class DiagnosticState:

    lower: float
    upper: float

    code: str
    name: str
    symbol: str
    description: str

# ==========================================================
# MASTER TABLE
# ==========================================================

DIAGNOSTIC_STATES = [

    DiagnosticState(
        lower=0.916666666667,
        upper=ALPHA,
        code="1144",
        name="Arquitecto Integrado",
        symbol="⟨◉⟩",
        description="Máxima integración estructural."
    ),

    DiagnosticState(
        lower=0.777777777778,
        upper=0.916666666667,
        code="1133",
        name="Integración Superior",
        symbol="⟨◎⟩",
        description="Alta estabilidad estructural."
    ),

    DiagnosticState(
        lower=0.638888888889,
        upper=0.777777777778,
        code="1044",
        name="Integración Avanzada",
        symbol="⟨◐⟩",
        description="Alta coherencia operacional."
    ),

    DiagnosticState(
        lower=0.500000000000,
        upper=0.638888888889,
        code="0144",
        name="Integración Funcional",
        symbol="⟨◑⟩",
        description="Sistema estable con margen de crecimiento."
    ),

    DiagnosticState(
        lower=CRITICAL_THRESHOLD,
        upper=0.500000000000,
        code="1122",
        name="Umbral Crítico",
        symbol="⟨◒⟩",
        description="Límite mínimo de autosostenibilidad."
    ),

    DiagnosticState(
        lower=DANGER_THRESHOLD,
        upper=CRITICAL_THRESHOLD,
        code="1111",
        name="Zona de Peligro",
        symbol="⟨◯⟩",
        description="Fragilidad estructural."
    ),

    DiagnosticState(
        lower=BETA,
        upper=DANGER_THRESHOLD,
        code="0000",
        name="Colapso Estructural",
        symbol="⟨○⟩",
        description="Coherencia insuficiente."
    )
]

# ==========================================================
# MASTER ENGINE
# ==========================================================

class DiagnosticSystem:

    @staticmethod
    def structural_percent(c: float) -> float:
        """
        β -> 0 %
        α -> 100 %
        """
        c = max(BETA, min(ALPHA, float(c)))
        return 100.0 * (c - BETA) / (ALPHA - BETA)

    @staticmethod
    def classify(c: float) -> DiagnosticState:

        if not (BETA <= c <= ALPHA):
            raise ValueError(
                f"CΩ={c:.6f} outside physical domain "
                f"[{BETA:.6f},{ALPHA:.6f}]"
            )

        for state in DIAGNOSTIC_STATES:

            if state.lower <= c <= state.upper:
                return state

        raise RuntimeError("Diagnostic table incomplete.")

# ==========================================================
# SELF AUDIT
# ==========================================================

    @staticmethod
    def self_audit():

        errors = []

        if not BETA < ALPHA:
            errors.append("β must be smaller than α.")

        previous = ALPHA

        for state in DIAGNOSTIC_STATES:

            if state.upper > previous + 1e-12:
                errors.append(
                    f"Overlap above {state.name}"
                )

            previous = state.lower

        if abs(DIAGNOSTIC_STATES[0].upper - ALPHA) > 1e-12:
            errors.append("Top state does not end at α.")

        if abs(DIAGNOSTIC_STATES[-1].lower - BETA) > 1e-12:
            errors.append("Bottom state does not start at β.")

        codes = [s.code for s in DIAGNOSTIC_STATES]

        if len(codes) != len(set(codes)):
            errors.append("Duplicated diagnostic codes.")

        names = [s.name for s in DIAGNOSTIC_STATES]

        if len(names) != len(set(names)):
            errors.append("Duplicated diagnostic names.")

        if errors:

            raise RuntimeError(
                "\n".join(errors)
            )

        return True
