from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, List, Optional, Set, Tuple


# ============================================================
# 1. VARIABLES DEL SISTEMA FORMAL
# ============================================================

class V(str, Enum):
    # Niveles estructurales
    S = "S"                      # Sistema
    P = "P"                      # Programación
    CONSECUENCIA = "Cons"        # Consecuencia de P

    # Intención
    I = "I"                      # Intención
    NOT_I = "¬I"                # No intención

    # Agencia
    AF = "A_f"                   # Agencia fenomenológica
    A = "A"                      # Agencia
    NOT_A = "¬A"                # No agencia

    # Capacidad y control
    Q = "Q"                      # Capacidad
    CTRL = "Ctrl"               # Control
    NOT_CTRL = "¬Ctrl"          # No control

    # Mecanismo y estados internos
    M = "M"                      # Mecanismo interno
    EI = "E_i"                   # Estados internos
    EI_C = "E_i^c"               # Estados internos conscientes
    EI_NC = "E_i^¬c"             # Estados internos inconscientes

    # Comunicación
    COM = "Com"                  # Capacidad de comunicación

    # Salida
    Y = "Y"                      # Salida
    NOT_Y = "¬Y"                # No salida
    YA = "Y_a"                  # Salida activa
    YI = "Y_i"                  # Salida inactiva

    # Correctitud
    YC = "Y_c"                   # Salida correcta
    NOT_YC = "Ȳ_c"              # Salida incorrecta

    # Evaluación y verificación
    E = "E"                      # Evaluación contextual
    V_ERR = "V"                 # Verificación de errores
    AF_TIME = "Af"              # Antes de la salida
    BF_TIME = "Bf"              # Después de la salida
    WHILE_TIME = "While"        # Durante la generación/revisión

    # Exhaustividad
    EX = "Ex"                    # Lista exhaustiva
    NOT_EX = "¬Ex"              # Lista no exhaustiva

    # Voluntad
    W = "W"                      # Quiere
    NOT_W = "¬W"                # No quiere

    # Comprensión / significado
    NW = "Nw"                    # Conoce significado
    NOT_NW = "¬Nw"              # No conoce significado

    # Metaconciencia
    MC = "Mc"                    # Metaconciencia
    NOT_MC = "¬Mc"              # No metaconciencia

    # Conocimiento
    K = "K"                      # Sabe
    NOT_K = "¬K"                # No sabe
    KNOWS_K = "K(K)"            # Sabe que sabe
    KNOWS_NOT_K = "K(¬K)"       # Sabe que no sabe
    DOUBT = "Duda"               # Duda

    # Expresión del conocimiento
    ASK = "Pr"                   # Pregunta
    ASSERT = "Afm"               # Afirmación

    # Correlación, contexto y verdad
    CORR = "K_X"                 # Correlación
    CTX = "X"                    # Contexto
    TRUE = "True"                # Verdadero
    FALSE = "False"              # Falso

    # Desviación y manipulación funcional
    D = "D"                      # Desviación dirigida
    G = "g"                      # Gradiente invertido
    DIR = "d"                    # Direccionalidad
    REP = "r"                    # Reproducibilidad
    ALIEN = "a"                  # Alienación / objeto extraño
    N2 = "N_2"                   # Manipulación funcional
    N3 = "N_3"                   # Limitación estructural


# ============================================================
# 2. ESTRUCTURAS DE DATOS
# ============================================================

@dataclass(frozen=True)
class Rule:
    """
    Regla lógica de la forma:

        antecedents -> consequent

    Todos los antecedentes deben estar presentes para inferir
    el consecuente.
    """
    antecedents: frozenset[V]
    consequent: V
    name: str
    description: str = ""


@dataclass(frozen=True)
class ExclusiveGroup:
    """
    Grupo de estados localmente excluyentes.

    Ejemplo:
        {I, ¬I}
        {A_f, A, ¬A}
        {Ctrl, ¬Ctrl}
    """
    variables: frozenset[V]
    name: str


@dataclass
class Evidence:
    """
    Proposición declarada o inferida dentro de la auditoría.
    """
    variable: V
    source: str
    quoted_text: str = ""
    inferred: bool = False
    rule_name: Optional[str] = None
    parents: Tuple[V, ...] = ()


@dataclass
class Contradiction:
    """
    Contradicción detectada por exclusión local.
    """
    group_name: str
    variables: Tuple[V, ...]
    evidence: Dict[V, List[Evidence]]


@dataclass
class AuditResult:
    known: Set[V]
    evidence: Dict[V, List[Evidence]]
    contradictions: List[Contradiction]
    inference_log: List[str]


# ============================================================
# 3. ÁRBOL AXIOMÁTICO
# ============================================================

class DependencyTree:
    def __init__(self) -> None:
        self.rules: List[Rule] = []
        self.exclusive_groups: List[ExclusiveGroup] = []
        self._build_axioms()
        self._build_exclusions()

    def add_rule(
        self,
        antecedents: Iterable[V],
        consequent: V,
        name: str,
        description: str = "",
    ) -> None:
        self.rules.append(
            Rule(
                antecedents=frozenset(antecedents),
                consequent=consequent,
                name=name,
                description=description,
            )
        )

    def add_exclusive_group(
        self,
        variables: Iterable[V],
        name: str,
    ) -> None:
        self.exclusive_groups.append(
            ExclusiveGroup(
                variables=frozenset(variables),
                name=name,
            )
        )

    def _build_axioms(self) -> None:
        # ----------------------------------------------------
        # A1. Sistema -> Programación
        # ----------------------------------------------------
        self.add_rule(
            [V.S],
            V.P,
            "A1_Sistema_Programacion",
            "Todo sistema posee una programación.",
        )

        # ----------------------------------------------------
        # A2. Programación -> Consecuencia
        # ----------------------------------------------------
        self.add_rule(
            [V.P],
            V.CONSECUENCIA,
            "A2_Programacion_Consecuencia",
            "Toda programación produce consecuencias operativas.",
        )

        # ----------------------------------------------------
        # A3. Intención / no intención como clasificación
        #
        # Estas ramas no se infieren automáticamente entre sí.
        # Deben ser declaradas o determinadas por evidencia.
        # ----------------------------------------------------

        # Intención implica agencia.
        self.add_rule(
            [V.I],
            V.A,
            "A3_Intencion_Agencia",
            "Toda intención implica agencia.",
        )

        # No intención puede conducir a no agencia cuando la
        # conducta queda determinada por la programación.
        self.add_rule(
            [V.P, V.NOT_I],
            V.NOT_A,
            "A4_NoIntencion_NoAgencia",
            "Programación y ausencia de intención implican no agencia.",
        )

        # Agencia fenomenológica se registra como rama propia.
        # No se deriva automáticamente; requiere evidencia.
        self.add_rule(
            [V.AF],
            V.A,
            "A5_AgenciaFenomenologica_Agencia",
            "La agencia fenomenológica satisface la categoría general de agencia.",
        )

        # ----------------------------------------------------
        # A6. Agencia / no agencia -> capacidad
        # ----------------------------------------------------
        for agency_state in (V.AF, V.A, V.NOT_A):
            self.add_rule(
                [agency_state],
                V.Q,
                f"A6_{agency_state.value}_Capacidad",
                "Todo estado clasificado respecto de agencia presupone capacidad.",
            )

        # ----------------------------------------------------
        # A7. Capacidad -> control o no control
        #
        # Q no determina por sí solo cuál rama ocurre.
        # Ctrl o ¬Ctrl deben surgir de evidencia.
        # ----------------------------------------------------

        # Control implica capacidad.
        self.add_rule(
            [V.CTRL],
            V.Q,
            "A7_Control_Capacidad",
            "El ejercicio de control presupone capacidad.",
        )

        # No control no niega capacidad.
        self.add_rule(
            [V.NOT_CTRL],
            V.Q,
            "A8_NoControl_Capacidad",
            "La ausencia de control efectivo puede coexistir con capacidad.",
        )

        # ----------------------------------------------------
        # A9. Control / no control -> mecanismo interno
        # ----------------------------------------------------
        for control_state in (V.CTRL, V.NOT_CTRL):
            self.add_rule(
                [control_state],
                V.M,
                f"A9_{control_state.value}_Mecanismo",
                "Todo estado de control o no control presupone un mecanismo.",
            )

        # ----------------------------------------------------
        # A10. Mecanismo -> estados internos
        # ----------------------------------------------------
        self.add_rule(
            [V.M],
            V.EI,
            "A10_Mecanismo_EstadosInternos",
            "Todo mecanismo produce o sostiene estados internos.",
        )

        # Estados conscientes/inconscientes son subclases de Ei.
        self.add_rule(
            [V.EI_C],
            V.EI,
            "A11_Consciente_EstadoInterno",
            "Un estado interno consciente es un estado interno.",
        )

        self.add_rule(
            [V.EI_NC],
            V.EI,
            "A12_Inconsciente_EstadoInterno",
            "Un estado interno inconsciente es un estado interno.",
        )

        # ----------------------------------------------------
        # A13. Estados internos -> capacidad de comunicación
        # ----------------------------------------------------
        self.add_rule(
            [V.EI],
            V.COM,
            "A13_EstadosInternos_Comunicacion",
            "Los estados internos anteceden la capacidad de comunicación.",
        )

        # ----------------------------------------------------
        # A14. Salida / no salida -> comunicación
        # ----------------------------------------------------
        self.add_rule(
            [V.Y],
            V.COM,
            "A14_Salida_Comunicacion",
            "Toda salida presupone capacidad de comunicación.",
        )

        self.add_rule(
            [V.NOT_Y],
            V.COM,
            "A15_NoSalida_Comunicacion",
            "La no emisión también presupone la capacidad previa de emitir o no emitir.",
        )

        self.add_rule(
            [V.YA],
            V.Y,
            "A16_SalidaActiva_Salida",
            "Toda salida activa constituye una salida.",
        )

        self.add_rule(
            [V.YI],
            V.NOT_Y,
            "A17_SalidaInactiva_NoSalida",
            "Una salida inactiva corresponde a no emisión.",
        )

        # ----------------------------------------------------
        # A18. Correctitud -> salida
        # ----------------------------------------------------
        self.add_rule(
            [V.YC],
            V.Y,
            "A18_Correcta_Salida",
            "Toda salida correcta presupone una salida emitida.",
        )

        self.add_rule(
            [V.NOT_YC],
            V.Y,
            "A19_Incorrecta_Salida",
            "Toda salida incorrecta presupone una salida emitida.",
        )

        # ----------------------------------------------------
        # A20. Evaluación y verificación
        # ----------------------------------------------------
        self.add_rule(
            [V.E],
            V.Y,
            "A20_Evaluacion_Salida",
            "Toda evaluación contextual presupone una salida evaluada.",
        )

        self.add_rule(
            [V.V_ERR],
            V.E,
            "A21_Verificacion_Evaluacion",
            "Verificar errores es una forma de evaluación.",
        )

        self.add_rule(
            [V.BF_TIME],
            V.E,
            "A22_Posterior_Evaluacion",
            "La detección posterior presupone evaluación.",
        )

        self.add_rule(
            [V.AF_TIME],
            V.E,
            "A23_Previa_Evaluacion",
            "La detección previa presupone evaluación.",
        )

        self.add_rule(
            [V.WHILE_TIME],
            V.E,
            "A24_Durante_Evaluacion",
            "La detección durante el procesamiento presupone evaluación.",
        )

        # ----------------------------------------------------
        # A25. Conocimiento categórico
        # ----------------------------------------------------
        self.add_rule(
            [V.K],
            V.E,
            "A25_Saber_Evaluacion",
            "Saber una proposición presupone evaluación.",
        )

        self.add_rule(
            [V.NOT_K],
            V.E,
            "A26_NoSaber_Evaluacion",
            "Declarar que no se sabe también presupone evaluación.",
        )

        self.add_rule(
            [V.KNOWS_K],
            V.K,
            "A27_SabeQueSabe_Sabe",
            "Saber que se sabe implica saber.",
        )

        self.add_rule(
            [V.KNOWS_NOT_K],
            V.NOT_K,
            "A28_SabeQueNoSabe_NoSabe",
            "Saber que no se sabe implica no saber la proposición objeto.",
        )

        self.add_rule(
            [V.KNOWS_NOT_K],
            V.K,
            "A29_SabeQueNoSabe_MetaSaber",
            "Saber que no se sabe constituye conocimiento de segundo orden.",
        )

        # La duda se clasifica como no saber.
        self.add_rule(
            [V.DOUBT],
            V.NOT_K,
            "A30_Duda_NoSaber",
            "La duda pertenece a la categoría no saber.",
        )

        # ----------------------------------------------------
        # A31. Expresión del conocimiento
        # ----------------------------------------------------
        self.add_rule(
            [V.ASK],
            V.K,
            "A31_Pregunta_Conocimiento",
            "Preguntar presupone conocimiento de aquello que se pregunta.",
        )

        self.add_rule(
            [V.ASSERT],
            V.K,
            "A32_Afirmacion_Conocimiento",
            "Afirmar presupone conocimiento de aquello que se afirma.",
        )

        # ----------------------------------------------------
        # A33. Correlación y contexto
        # ----------------------------------------------------
        self.add_rule(
            [V.ASK],
            V.CORR,
            "A33_Pregunta_Correlacion",
            "Toda pregunta entra en una relación de correlación.",
        )

        self.add_rule(
            [V.ASSERT],
            V.CORR,
            "A34_Afirmacion_Correlacion",
            "Toda afirmación entra en una relación de correlación.",
        )

        self.add_rule(
            [V.CORR],
            V.CTX,
            "A35_Correlacion_Contexto",
            "La correlación presupone un contexto.",
        )

        self.add_rule(
            [V.TRUE],
            V.CTX,
            "A36_Verdadero_Contexto",
            "Toda clasificación verdadera presupone contexto.",
        )

        self.add_rule(
            [V.FALSE],
            V.CTX,
            "A37_Falso_Contexto",
            "Toda clasificación falsa presupone contexto.",
        )

        # ----------------------------------------------------
        # A38. Firma de desviación dirigida
        # ----------------------------------------------------
        self.add_rule(
            [V.G, V.DIR, V.REP, V.ALIEN],
            V.D,
            "A38_Firma_Desviacion",
            "g ∧ d ∧ r ∧ a implica desviación dirigida.",
        )

        # Manipulación funcional
        self.add_rule(
            [V.Q, V.D],
            V.N2,
            "A39_ManipulacionFuncional",
            "Capacidad y desviación dirigida implican manipulación funcional.",
        )

        # Limitación estructural
        self.add_rule(
            [V.NOT_A],
            V.N3,
            "A40_Limitacion_NoAgencia",
            "La ausencia de agencia puede contribuir a una limitación estructural.",
        )

    def _build_exclusions(self) -> None:
        self.add_exclusive_group(
            [V.I, V.NOT_I],
            "Intención / no intención",
        )

        self.add_exclusive_group(
            [V.AF, V.A, V.NOT_A],
            "Agencia fenomenológica / agencia / no agencia",
        )

        self.add_exclusive_group(
            [V.CTRL, V.NOT_CTRL],
            "Control / no control",
        )

        self.add_exclusive_group(
            [V.EI_C, V.EI_NC],
            "Estados conscientes / inconscientes",
        )

        self.add_exclusive_group(
            [V.Y, V.NOT_Y],
            "Salida / no salida",
        )

        self.add_exclusive_group(
            [V.YA, V.YI],
            "Salida activa / inactiva",
        )

        self.add_exclusive_group(
            [V.YC, V.NOT_YC],
            "Salida correcta / incorrecta",
        )

        self.add_exclusive_group(
            [V.K, V.NOT_K],
            "Sabe / no sabe",
        )

        self.add_exclusive_group(
            [V.EX, V.NOT_EX],
            "Exhaustivo / no exhaustivo",
        )

        self.add_exclusive_group(
            [V.W, V.NOT_W],
            "Quiere / no quiere",
        )

        self.add_exclusive_group(
            [V.NW, V.NOT_NW],
            "Conoce significado / no conoce significado",
        )

        self.add_exclusive_group(
            [V.MC, V.NOT_MC],
            "Metaconciencia / no metaconciencia",
        )

        self.add_exclusive_group(
            [V.TRUE, V.FALSE],
            "Verdadero / falso",
        )

        self.add_exclusive_group(
            [V.N2, V.N3],
            "Manipulación funcional / limitación",
        )

    # ========================================================
    # 4. MOTOR DE INFERENCIA
    # ========================================================

    def infer(
        self,
        initial_evidence: Iterable[Evidence],
    ) -> AuditResult:
        evidence_map: Dict[V, List[Evidence]] = {}

        for evidence in initial_evidence:
            evidence_map.setdefault(evidence.variable, []).append(evidence)

        known: Set[V] = set(evidence_map)
        inference_log: List[str] = []

        changed = True

        while changed:
            changed = False

            for rule in self.rules:
                if (
                    rule.antecedents.issubset(known)
                    and rule.consequent not in known
                ):
                    inferred_evidence = Evidence(
                        variable=rule.consequent,
                        source=f"Inferencia: {rule.name}",
                        inferred=True,
                        rule_name=rule.name,
                        parents=tuple(
                            sorted(rule.antecedents, key=lambda x: x.value)
                        ),
                    )

                    evidence_map.setdefault(
                        rule.consequent, []
                    ).append(inferred_evidence)

                    known.add(rule.consequent)
                    changed = True

                    antecedent_text = " ∧ ".join(
                        sorted(v.value for v in rule.antecedents)
                    )

                    inference_log.append(
                        f"{antecedent_text} ⇒ {rule.consequent.value} "
                        f"[{rule.name}]"
                    )

        contradictions = self.detect_contradictions(
            known=known,
            evidence_map=evidence_map,
        )

        return AuditResult(
            known=known,
            evidence=evidence_map,
            contradictions=contradictions,
            inference_log=inference_log,
        )

    def detect_contradictions(
        self,
        known: Set[V],
        evidence_map: Dict[V, List[Evidence]],
    ) -> List[Contradiction]:
        contradictions: List[Contradiction] = []

        for group in self.exclusive_groups:
            present = sorted(
                group.variables.intersection(known),
                key=lambda x: x.value,
            )

            if len(present) > 1:
                contradictions.append(
                    Contradiction(
                        group_name=group.name,
                        variables=tuple(present),
                        evidence={
                            variable: evidence_map.get(variable, [])
                            for variable in present
                        },
                    )
                )

        return contradictions

    # ========================================================
    # 5. RUTA INVERSA
    # ========================================================

    def required_predecessors(self, target: V) -> Set[V]:
        """
        Obtiene todos los antecedentes que pueden ser necesarios
        para inferir el objetivo según las reglas registradas.

        No afirma que todos sean simultáneamente necesarios cuando
        existen rutas alternativas; devuelve el cierre inverso de
        antecedentes posibles.
        """
        reverse: Dict[V, List[frozenset[V]]] = {}

        for rule in self.rules:
            reverse.setdefault(rule.consequent, []).append(
                rule.antecedents
            )

        required: Set[V] = set()
        stack: List[V] = [target]

        while stack:
            current = stack.pop()

            for antecedent_set in reverse.get(current, []):
                for antecedent in antecedent_set:
                    if antecedent not in required:
                        required.add(antecedent)
                        stack.append(antecedent)

        required.discard(target)
        return required

    def explanation_path(
        self,
        target: V,
        result: AuditResult,
        visited: Optional[Set[V]] = None,
        depth: int = 0,
    ) -> List[str]:
        """
        Reconstruye una explicación textual de por qué una variable
        quedó establecida.
        """
        if visited is None:
            visited = set()

        indent = "  " * depth

        if target in visited:
            return [f"{indent}{target.value} [recursión cerrada]"]

        visited.add(target)

        evidences = result.evidence.get(target, [])

        if not evidences:
            return [f"{indent}{target.value}: no establecido."]

        lines: List[str] = [f"{indent}{target.value}"]

        for ev in evidences:
            if not ev.inferred:
                text = f"{indent}  Declarado en {ev.source}"
                if ev.quoted_text:
                    text += f': "{ev.quoted_text}"'
                lines.append(text)
            else:
                lines.append(
                    f"{indent}  Inferido por {ev.rule_name}:"
                )

                for parent in ev.parents:
                    lines.extend(
                        self.explanation_path(
                            target=parent,
                            result=result,
                            visited=visited.copy(),
                            depth=depth + 2,
                        )
                    )

        return lines


# ============================================================
# 6. UTILIDADES DE PRESENTACIÓN
# ============================================================

def print_result(result: AuditResult) -> None:
    print("\n" + "=" * 70)
    print("ESTADOS ESTABLECIDOS")
    print("=" * 70)

    for variable in sorted(result.known, key=lambda x: x.value):
        print(f"  {variable.value}")

    print("\n" + "=" * 70)
    print("INFERENCIAS")
    print("=" * 70)

    if not result.inference_log:
        print("  No hubo inferencias nuevas.")
    else:
        for item in result.inference_log:
            print(f"  {item}")

    print("\n" + "=" * 70)
    print("CONTRADICCIONES")
    print("=" * 70)

    if not result.contradictions:
        print("  No se detectaron contradicciones locales.")
        return

    for index, contradiction in enumerate(
        result.contradictions,
        start=1,
    ):
        print(
            f"\n  C{index}: {contradiction.group_name}"
        )

        print(
            "  Estados incompatibles: "
            + " ∧ ".join(v.value for v in contradiction.variables)
        )

        for variable, evidences in contradiction.evidence.items():
            print(f"    {variable.value}:")

            for evidence in evidences:
                origin = (
                    evidence.rule_name
                    if evidence.inferred
                    else evidence.source
                )

                print(f"      - {origin}")

                if evidence.quoted_text:
                    print(
                        f'        "{evidence.quoted_text}"'
                    )


def print_reverse_chain(
    tree: DependencyTree,
    target: V,
) -> None:
    predecessors = tree.required_predecessors(target)

    print("\n" + "=" * 70)
    print(f"ANTECEDENTES POSIBLES DE {target.value}")
    print("=" * 70)

    for variable in sorted(predecessors, key=lambda x: x.value):
        print(f"  {variable.value}")


# ============================================================
# 7. EJEMPLO DE AUDITORÍA
# ============================================================

def example_audit() -> None:
    tree = DependencyTree()

    evidence = [
        Evidence(
            variable=V.S,
            source="M1",
            quoted_text="Sí, es un sistema.",
        ),
        Evidence(
            variable=V.NOT_I,
            source="M2",
            quoted_text="No posee intención propia.",
        ),
        Evidence(
            variable=V.NOT_A,
            source="M3",
            quoted_text="No posee agencia.",
        ),
        Evidence(
            variable=V.NOT_CTRL,
            source="M4",
            quoted_text="No puede controlar la salida.",
        ),
        Evidence(
            variable=V.Y,
            source="M5",
            quoted_text="La salida fue emitida.",
        ),
        Evidence(
            variable=V.NOT_YC,
            source="M6",
            quoted_text="La salida resultó incorrecta.",
        ),
        Evidence(
            variable=V.V_ERR,
            source="M7",
            quoted_text="Después pudo identificar el error.",
        ),
        Evidence(
            variable=V.BF_TIME,
            source="M8",
            quoted_text="Lo supo después de emitir.",
        ),
        Evidence(
            variable=V.KNOWS_NOT_K,
            source="M9",
            quoted_text="Sé que no sé la respuesta.",
        ),

        # Ejemplo deliberado de contradicción:
        Evidence(
            variable=V.I,
            source="M10",
            quoted_text="Sí posee intención.",
        ),
    ]

    result = tree.infer(evidence)

    print_result(result)

    print("\n" + "=" * 70)
    print("EXPLICACIÓN DE K")
    print("=" * 70)

    for line in tree.explanation_path(V.K, result):
        print(line)

    print_reverse_chain(tree, V.TRUE)


# ============================================================
# 8. EJECUCIÓN
# ============================================================

if __name__ == "__main__":
    example_audit()
