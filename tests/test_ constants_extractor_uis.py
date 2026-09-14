"""
UIS — EXPERIMENTO DE CONVERGENCIA ESTRUCTURAL A ESCALA 10^200

Objetivo
--------
Auditar de forma determinista la estabilidad de la densidad estructural
producida por la Pinza de Tenazas sobre una ventana situada en 10^200.

A diferencia de una simulación Monte Carlo, este experimento no selecciona
muestras aleatorias ni repite candidatos.

Cada estado admisible de la forma:

    n ≡ 1 (mod 6)

es recorrido exactamente una vez desde el inicio de la ventana hasta su
frontera final.

La prueba compara la densidad estructural observada contra la densidad
teórica inducida por la Pinza de Tenazas.

La tolerancia experimental se fija en:

    ε = 10^-5

El experimento NO presupone que dicha tolerancia deba cumplirse.
Precisamente se ejecuta para medir si la estructura observada permanece
dentro de ese régimen de precisión.
"""

import math


# ============================================================
# CONFIGURACIÓN DEL EXPERIMENTO UIS
# ============================================================

ESCALA = 10**200

VENTANA = 10**6

TOLERANCIA = 1e-5


# Pinza de Tenazas.
#
# 2 y 3 no aparecen porque el espacio experimental ya ha sido
# restringido a estados n ≡ 1 (mod 6).
PRIMOS_PINZA = (
    5,
    7,
    11,
    13,
    17,
    19,
    23,
    29,
    31,
    37,
    41,
    43,
    47,
)


# ============================================================
# DENSIDAD ESTRUCTURAL TEÓRICA
# ============================================================

DENSIDAD_ASINTOTICA = math.prod(
    1.0 - (1.0 / p)
    for p in PRIMOS_PINZA
)


def test_convergencia_estructural_10_200():
    """
    EXPERIMENTO UIS
    ----------------

    Recorre exhaustivamente la ventana estructural situada en 10^200.

    No existe muestreo Monte Carlo.

    No existe reemplazo.

    No existe repetición deliberada de estados.

    Cada candidato n ≡ 1 (mod 6) es auditado una sola vez contra
    todos los módulos que constituyen la Pinza de Tenazas.

    El resultado experimental se compara con la densidad estructural
    teórica.

    Condición experimental:

        |rho_observada - rho_teorica| < 10^-5
    """

    inicio = ESCALA
    fin = ESCALA + VENTANA

    # --------------------------------------------------------
    # ALINEACIÓN CON EL PRIMER ESTADO 6k + 1
    # --------------------------------------------------------

    primer_candidato = inicio + ((1 - inicio) % 6)

    total_estados = 0
    supervivientes = 0


    # --------------------------------------------------------
    # BARRIDO DETERMINISTA
    # --------------------------------------------------------
    #
    # Desde este punto no se realizan saltos aleatorios.
    #
    # La trayectoria es:
    #
    #     n
    #     n + 6
    #     n + 12
    #     n + 18
    #     ...
    #
    # hasta alcanzar la frontera de la ventana.
    # --------------------------------------------------------

    for n in range(primer_candidato, fin, 6):

        total_estados += 1

        # ----------------------------------------------------
        # PINZA DE TENAZAS
        # ----------------------------------------------------

        sobrevive = True

        for p in PRIMOS_PINZA:

            if n % p == 0:
                sobrevive = False
                break

        if sobrevive:
            supervivientes += 1


    # ========================================================
    # MEDICIÓN
    # ========================================================

    assert total_estados > 0

    densidad_observada = (
        supervivientes / total_estados
    )

    error_absoluto = abs(
        densidad_observada - DENSIDAD_ASINTOTICA
    )


    # ========================================================
    # INFORME EXPERIMENTAL
    # ========================================================

    print()
    print("=" * 72)
    print("UIS — AUDITORÍA DE CONVERGENCIA ESTRUCTURAL")
    print("=" * 72)

    print(f"Escala inicial       : 10^200")
    print(f"Inicio exacto        : {inicio}")
    print(f"Fin                  : {fin}")
    print(f"Primer estado 6k+1   : {primer_candidato}")

    print("-" * 72)

    print(f"Estados auditados    : {total_estados:,}")
    print(f"Supervivientes       : {supervivientes:,}")

    print("-" * 72)

    print(
        f"Densidad teórica     : "
        f"{DENSIDAD_ASINTOTICA:.12f}"
    )

    print(
        f"Densidad observada   : "
        f"{densidad_observada:.12f}"
    )

    print(
        f"Error absoluto       : "
        f"{error_absoluto:.12e}"
    )

    print(
        f"Tolerancia UIS       : "
        f"{TOLERANCIA:.12e}"
    )

    print("-" * 72)

    if error_absoluto < TOLERANCIA:

        print(
            "RESULTADO             : "
            "CONVERGENCIA ESTRUCTURAL CONFIRMADA"
        )

    else:

        print(
            "RESULTADO             : "
            "DESVIACIÓN ESTRUCTURAL DETECTADA"
        )

    print("=" * 72)
    print()


    # ========================================================
    # CRITERIO EXPERIMENTAL
    # ========================================================

    assert error_absoluto < TOLERANCIA, (
        "\n"
        "UIS — DESVIACIÓN ESTRUCTURAL\n"
        f"rho_teorica   = {DENSIDAD_ASINTOTICA:.12f}\n"
        f"rho_observada = {densidad_observada:.12f}\n"
        f"error         = {error_absoluto:.12e}\n"
        f"tolerancia    = {TOLERANCIA:.12e}\n"
    )
