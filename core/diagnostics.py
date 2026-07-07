from dataclasses import dataclass
from core.constants import (
    ALPHA,
    BETA,
    CODE_ARCHITECT,
    CODE_SYNCHRONY,
    CODE_ENTROPY,
)

# ============================================================
# DIAGNOSTIC STATE
# ============================================================

@dataclass(frozen=True)
class DiagnosticState:

    lower: float
    upper: float

    legacy_code: int

    name: str
    description: str


# ============================================================
# MASTER TABLE
# ============================================================

DIAGNOSTIC_STATES = [

    DiagnosticState(ALPHA, ALPHA, CODE_ARCHITECT,
        "Arquitecto Integrado",
        "Máxima integración estructural."),

    DiagnosticState(0.700, ALPHA,
        CODE_SYNCHRONY,
        "Altamente Coherente",
        "Sistema altamente coherente."),

    DiagnosticState(BETA,0.450,
        CODE_ENTROPY,
        "Entropía",
        "Sistema por debajo del umbral crítico.")
]


# ============================================================
# MASTER DIAGNOSTIC
# ============================================================

class DiagnosticSystem:

    # --------------------------------------------------------
    # CHECK 0
    # --------------------------------------------------------

    @staticmethod
    def validate_domain(c):

        if c < BETA:
            raise ValueError(
                f"CΩ={c:.6f} below β={BETA:.6f}"
            )

        if c > ALPHA:
            raise ValueError(
                f"CΩ={c:.6f} above α={ALPHA:.6f}"
            )

    # --------------------------------------------------------
    # CHECK 1
    # Tabla Maestra
    # --------------------------------------------------------

    @staticmethod
    def classify_from_table(c):

        for state in DIAGNOSTIC_STATES:

            if state.lower <= c <= state.upper:

                return state

        raise RuntimeError("No diagnostic state found.")

    # --------------------------------------------------------
    # CHECK 2
    # Independiente
    # --------------------------------------------------------

    @staticmethod
    def classify_from_percent(c):

        p = (
            (c - BETA)
            /
            (ALPHA - BETA)
        )

        if p >= 0.95:
            return CODE_ARCHITECT

        if p >= 0.70:
            return CODE_SYNCHRONY

        return CODE_ENTROPY

    # --------------------------------------------------------
    # DOUBLE CHECK
    # --------------------------------------------------------

    @staticmethod
    def get_status_code(c_omega):

        DiagnosticSystem.validate_domain(c_omega)

        # Camino A
        table_state = DiagnosticSystem.classify_from_table(
            c_omega
        )

        # Camino B
        percent_code = DiagnosticSystem.classify_from_percent(
            c_omega
        )

        # =====================================================
        # DOUBLE CHECK
        # =====================================================

        if table_state.legacy_code != percent_code:

            raise RuntimeError(
                "Diagnostic mismatch\n"
                f"Table={table_state.legacy_code}\n"
                f"Percent={percent_code}"
            )

        return (
            f"CODE {table_state.legacy_code}: "
            f"{table_state.name} - "
            f"{table_state.description}"
        )

    # --------------------------------------------------------
    # LAYER CHECK
    # --------------------------------------------------------

    @staticmethod
    def check_layer_friction(layers_data):

        alerts = []

        for i, layer in enumerate(layers_data):

            phi = layer["phi"]

            if phi > 0.15:

                alerts.append(
                    f"L{i}: φ={phi:.3f}"
                )

        return alerts

    # --------------------------------------------------------
    # SELF AUDIT
    # --------------------------------------------------------

    @staticmethod
    def self_audit():

        errors = []

        if not BETA < ALPHA:
            errors.append("β >= α")

        if DIAGNOSTIC_STATES[0].lower != ALPHA:
            errors.append("Architect state invalid")

        if errors:

            raise RuntimeError(
                "\n".join(errors)
            )

        return True
