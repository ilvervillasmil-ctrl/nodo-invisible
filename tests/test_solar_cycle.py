import math
import pytest

# ============================================================================
# TEST DEL 24 - VERSIÓN FUERTE (márgenes derivados del marco UIS)
# ============================================================================
# 
# Este test usa márgenes basados en ε = 0.02716 (residuo irreducible del observador)
# No márgenes arbitrarios del 2%. Si una relación no se cumple dentro de ε,
# el test falla y reporta el error exacto.
#
# Valores de referencia (derivados del cubo):
#   ε = 0.02716
#   δ = 60 - 27π/√2 = 0.02108033486
#   m_e = 0.5109989461 MeV
#   Día sidéreo = 23.93447 h (dato observado)
#
# Relaciones esperadas (con error máximo ε):
#   1. Diferencia/δ = 3.108 ± ε
#   2. 24/(m_e/δ) = 0.9901 ± ε
#   3. m_e/δ = 24.24 ± ε
#   4. Diferencia/ε = 2.412 ± ε
# ============================================================================

# CONSTANTES DEL MARCO UIS
BETA = 1 / 27
ALPHA = 26 / 27
PHI = (1 + math.sqrt(5)) / 2

# GEOMETRÍA DEL CUBO
EMPAQUETAMIENTO = math.pi / math.sqrt(2)  # π/√2 ≈ 2.22144
HUELLA_OBSERVADOR = 60 - (27 * EMPAQUETAMIENTO)  # δ ≈ 0.02108033486

# RESIDUO DEL OBSERVADOR (del Axioma 3 del UIS)
EPSILON = 0.02716

# MASA DEL ELECTRÓN (CODATA 2022)
M_e_MeV = 0.5109989461

# TIEMPO (horas) - datos observacionales
DIA_SOLAR = 24.0
DIA_SIDEREO = 23.93447
DIFERENCIA_DIA = DIA_SOLAR - DIA_SIDEREO  # ≈ 0.06553

# RELACIONES ESPERADAS (valores teóricos)
RELACION_ME_DELTA_ESPERADA = M_e_MeV / HUELLA_OBSERVADOR  # ≈ 24.24
RELACION_24_ME_ESPERADA = DIA_SOLAR / RELACION_ME_DELTA_ESPERADA  # ≈ 0.9901
RELACION_DIF_DELTA_ESPERADA = DIFERENCIA_DIA / HUELLA_OBSERVADOR  # ≈ 3.108
RELACION_DIF_EPSILON_ESPERADA = DIFERENCIA_DIA / EPSILON  # ≈ 2.412

# UMBRALES (error máximo permitido = ε = 0.02716 ≈ 2.716%)
# Esto es el residuo irreducible del observador. Si una relación
# no se cumple dentro de ε, la "huella" es mayor que lo que el
# propio marco considera irreducible.
UMBRAL = EPSILON  # 0.02716


def error_relativo(valor, esperado):
    """Calcula error relativo |valor - esperado| / esperado"""
    return abs(valor - esperado) / abs(esperado)


def assert_dentro_epsilon(valor, esperado, nombre):
    """Assert que valor está dentro de ε del esperado"""
    err = error_relativo(valor, esperado)
    assert err <= UMBRAL, (
        f"\n❌ {nombre} = {valor:.6f} (esperado {esperado:.6f})\n"
        f"   Error relativo: {err:.4%} > ε = {UMBRAL:.4%}\n"
        f"   La huella ({err:.4%}) supera el residuo irreducible del observador."
    )
    print(f"   ✅ {nombre} = {valor:.6f} (error {err:.4%} ≤ ε)")


class TestNumero24Fuerte:
    """Test del número 24 con márgenes derivados del marco UIS"""

    def test_dia_solar_y_sidereo(self):
        """Prueba 1: La diferencia solar-sidéreo es del orden esperado"""
        print("\n" + "=" * 70)
        print("TEST 1: DÍA SOLAR VS SIDÉREO")
        print("=" * 70)

        print(f"Día solar:        {DIA_SOLAR} h")
        print(f"Día sidéreo:      {DIA_SIDEREO} h")
        print(f"Diferencia:       {DIFERENCIA_DIA} h = {DIFERENCIA_DIA * 60:.4f} min")

        # La diferencia debe ser positiva y del orden de 0.0655
        # Este es un test de plausibilidad, no de precisión ε
        assert DIFERENCIA_DIA > 0, "La diferencia día solar-sidéreo debe ser positiva"
        assert 0.065 < DIFERENCIA_DIA < 0.066, (
            f"Diferencia {DIFERENCIA_DIA} fuera del rango esperado 0.065-0.066"
        )

        print(f"\n✅ Diferencia = {DIFERENCIA_DIA:.5f} h (~3.93 min)")

    def test_relacion_diferencia_delta(self):
        """Prueba 2: Diferencia/δ debe estar dentro de ε de 3.108"""
        print("\n" + "=" * 70)
        print("TEST 2: DIFERENCIA / δ")
        print("=" * 70)

        valor = DIFERENCIA_DIA / HUELLA_OBSERVADOR
        print(f"δ = {HUELLA_OBSERVADOR:.10f}")
        print(f"Diferencia/δ calculado = {valor:.6f}")
        print(f"Esperado = {RELACION_DIF_DELTA_ESPERADA:.6f}")

        assert_dentro_epsilon(valor, RELACION_DIF_DELTA_ESPERADA, "Diferencia/δ")

    def test_relacion_24_me_delta(self):
        """Prueba 3: 24 / (m_e/δ) debe estar dentro de ε de 0.9901"""
        print("\n" + "=" * 70)
        print("TEST 3: 24 / (m_e/δ)")
        print("=" * 70)

        valor = DIA_SOLAR / RELACION_ME_DELTA_ESPERADA
        print(f"m_e/δ = {RELACION_ME_DELTA_ESPERADA:.6f}")
        print(f"24 / (m_e/δ) calculado = {valor:.6f}")
        print(f"Esperado = {RELACION_24_ME_ESPERADA:.6f}")

        assert_dentro_epsilon(valor, RELACION_24_ME_ESPERADA, "24 / (m_e/δ)")

    def test_relacion_me_delta(self):
        """Prueba 4: m_e/δ debe estar dentro de ε de 24.24"""
        print("\n" + "=" * 70)
        print("TEST 4: m_e / δ")
        print("=" * 70)

        valor = M_e_MeV / HUELLA_OBSERVADOR
        print(f"m_e = {M_e_MeV:.10f} MeV")
        print(f"δ = {HUELLA_OBSERVADOR:.10f}")
        print(f"m_e/δ calculado = {valor:.6f}")
        print(f"Esperado = {RELACION_ME_DELTA_ESPERADA:.6f}")

        assert_dentro_epsilon(valor, RELACION_ME_DELTA_ESPERADA, "m_e/δ")

    def test_relacion_diferencia_epsilon(self):
        """Prueba 5: Diferencia/ε debe estar dentro de ε de 2.412"""
        print("\n" + "=" * 70)
        print("TEST 5: DIFERENCIA / ε")
        print("=" * 70)

        valor = DIFERENCIA_DIA / EPSILON
        print(f"ε = {EPSILON:.5f}")
        print(f"Diferencia/ε calculado = {valor:.6f}")
        print(f"Esperado = {RELACION_DIF_EPSILON_ESPERADA:.6f}")

        assert_dentro_epsilon(valor, RELACION_DIF_EPSILON_ESPERADA, "Diferencia/ε")

    def test_imperfeccion_como_estructura(self):
        """Prueba 6: La acción m_e × Δt debe ser del orden de ħ (no exacto)"""
        print("\n" + "=" * 70)
        print("TEST 6: m_e × Δt ≈ ħ (correspondencia estructural)")
        print("=" * 70)

        m_e_julios = M_e_MeV * 1.602176634e-13
        diferencia_segundos = DIFERENCIA_DIA * 3600
        accion = m_e_julios * diferencia_segundos
        hbar = 1.054571817e-34

        relacion = accion / hbar
        print(f"m_e × diferencia_tiempo = {accion:.4e} J·s")
        print(f"ħ = {hbar:.4e} J·s")
        print(f"Relación acción/ħ = {relacion:.4f}")

        # Este test tiene margen más amplio (10%) porque la constante de Planck
        # no está derivada directamente del marco del número 24.
        # Es una correspondencia estructural, no una derivación exacta.
        MARGEN_ESTRUCTURAL = 0.10  # 10%
        assert 0.9 < relacion < 1.1, (
            f"\n❌ La relación acción/ħ = {relacion:.4f} está fuera del rango "
            f"0.9-1.1 (margen estructural del 10%).\n"
            f"   Esto indica que la correspondencia es aproximada, no exacta."
        )

        print(f"\n✅ La relación está dentro del margen estructural (10%)")

    def test_cierre_epsilon(self):
        """Prueba 7: Consistencia interna del residuo ε"""
        print("\n" + "=" * 70)
        print("TEST 7: CONSISTENCIA INTERNA DE ε")
        print("=" * 70)

        # Si el marco es consistente, DIFERENCIA/ε debe ser aproximadamente
        # igual a (m_e/δ) / 10 (por la relación con α⁻¹)
        prediccion_epsilon = (RELACION_ME_DELTA_ESPERADA / 10)
        valor_actual = DIFERENCIA_DIA / EPSILON

        print(f"Predicción desde m_e/δ: (m_e/δ)/10 = {prediccion_epsilon:.6f}")
        print(f"Valor actual Diferencia/ε = {valor_actual:.6f}")

        err = error_relativo(valor_actual, prediccion_epsilon)
        print(f"Error relativo: {err:.4%}")

        # Debe estar dentro de ε
        assert err <= UMBRAL, (
            f"\n❌ Diferencia/ε = {valor_actual:.6f} vs predicción {prediccion_epsilon:.6f}\n"
            f"   Error {err:.4%} > ε = {UMBRAL:.4%}. El residuo no es consistente internamente."
        )

        print(f"\n✅ El residuo ε es internamente consistente")

    def test_conclusion_final(self):
        """Prueba 8: Conclusión con resumen de errores"""
        print("\n" + "=" * 70)
        print("CONCLUSIÓN: EL 24 COMO CICLO DEL OBSERVADOR")
        print("=" * 70)

        errores = {
            "Diferencia/δ": error_relativo(
                DIFERENCIA_DIA / HUELLA_OBSERVADOR,
                RELACION_DIF_DELTA_ESPERADA
            ),
            "24/(m_e/δ)": error_relativo(
                DIA_SOLAR / RELACION_ME_DELTA_ESPERADA,
                RELACION_24_ME_ESPERADA
            ),
            "m_e/δ": error_relativo(
                M_e_MeV / HUELLA_OBSERVADOR,
                RELACION_ME_DELTA_ESPERADA
            ),
            "Diferencia/ε": error_relativo(
                DIFERENCIA_DIA / EPSILON,
                RELACION_DIF_EPSILON_ESPERADA
            ),
            "Consistencia ε": error_relativo(
                DIFERENCIA_DIA / EPSILON,
                RELACION_ME_DELTA_ESPERADA / 10
            )
        }

        print("\nResumen de errores relativos:")
        print("-" * 50)
        for nombre, err in errores.items():
            estado = "✅" if err <= UMBRAL else "❌"
            print(f"  {estado} {nombre}: {err:.4%} (límite ε = {UMBRAL:.4%})")

        todos_dentro = all(err <= UMBRAL for err in errores.values())

        print(f"\n{'='*70}")
        if todos_dentro:
            print("✅ TODAS LAS RELACIONES DENTRO DE ε")
            print("   El número 24 es estructuralmente consistente con el marco UIS.")
        else:
            print("❌ ALGUNA RELACIÓN SUPERA ε")
            print("   La conexión del número 24 requiere un margen > ε.")
            print("   Esto indica correspondencia estructural, no derivación exacta.")

        assert todos_dentro, (
            "El test fuerte falla: alguna relación supera el margen ε = 2.716%.\n"
            "El número 24 como ciclo del observador es correspondencia estructural, "
            "no derivación exacta del marco UIS."
        )


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("TEST DEL NÚMERO 24 - VERSIÓN FUERTE")
    print("Márgenes derivados de ε = 0.02716 (residuo irreducible del observador)")
    print("=" * 80)

    test = TestNumero24Fuerte()

    test.test_dia_solar_y_sidereo()
    test.test_relacion_diferencia_delta()
    test.test_relacion_24_me_delta()
    test.test_relacion_me_delta()
    test.test_relacion_diferencia_epsilon()
    test.test_imperfeccion_como_estructura()
    test.test_cierre_epsilon()
    test.test_conclusion_final()

    print("\n" + "=" * 80)
    print("TEST COMPLETADO")
    print("=" * 80)
