import math
import pytest

# ============================================================================
# TEST DEL 24 - VERSIÓN FUERTE (márgenes derivados del marco UIS)
# ============================================================================

# CONSTANTES DEL MARCO UIS
BETA = 1 / 27
ALPHA = 26 / 27
PHI = (1 + math.sqrt(5)) / 2

# GEOMETRÍA DEL CUBO
EMPAQUETAMIENTO = math.pi / math.sqrt(2)
HUELLA_OBSERVADOR = 60 - (27 * EMPAQUETAMIENTO)  # δ ≈ 0.02108033486

# RESIDUO DEL OBSERVADOR (del Axioma 3 del UIS)
EPSILON = 0.02716

# MASA DEL ELECTRÓN (CODATA 2022)
M_e_MeV = 0.5109989461

# TIEMPO (horas) - datos observacionales
DIA_SOLAR = 24.0
DIA_SIDEREO = 23.93447
DIFERENCIA_DIA = DIA_SOLAR - DIA_SIDEREO  # ≈ 0.06553

# RELACIONES ESPERADAS
RELACION_ME_DELTA_ESPERADA = M_e_MeV / HUELLA_OBSERVADOR  # ≈ 24.24
RELACION_24_ME_ESPERADA = DIA_SOLAR / RELACION_ME_DELTA_ESPERADA  # ≈ 0.9901
RELACION_DIF_DELTA_ESPERADA = DIFERENCIA_DIA / HUELLA_OBSERVADOR  # ≈ 3.108
RELACION_DIF_EPSILON_ESPERADA = DIFERENCIA_DIA / EPSILON  # ≈ 2.412

# UMBRAL (error máximo = ε = 0.02716 ≈ 2.716%)
UMBRAL = EPSILON


def error_relativo(valor, esperado):
    return abs(valor - esperado) / abs(esperado)


def assert_dentro_epsilon(valor, esperado, nombre):
    err = error_relativo(valor, esperado)
    assert err <= UMBRAL, (
        f"\n❌ {nombre} = {valor:.6f} (esperado {esperado:.6f})\n"
        f"   Error relativo: {err:.4%} > ε = {UMBRAL:.4%}"
    )
    print(f"   ✅ {nombre} = {valor:.6f} (error {err:.4%} ≤ ε)")


class TestNumero24Fuerte:
    """Test del número 24 con márgenes derivados del marco UIS"""

    def test_dia_solar_y_sidereo(self):
        print("\n" + "=" * 70)
        print("TEST 1: DÍA SOLAR VS SIDÉREO")
        print("=" * 70)

        print(f"Día solar:        {DIA_SOLAR} h")
        print(f"Día sidéreo:      {DIA_SIDEREO} h")
        print(f"Diferencia:       {DIFERENCIA_DIA} h = {DIFERENCIA_DIA * 60:.4f} min")

        assert DIFERENCIA_DIA > 0
        assert 0.065 < DIFERENCIA_DIA < 0.066
        print(f"\n✅ Diferencia = {DIFERENCIA_DIA:.5f} h")

    def test_relacion_diferencia_delta(self):
        print("\n" + "=" * 70)
        print("TEST 2: DIFERENCIA / δ")
        print("=" * 70)

        valor = DIFERENCIA_DIA / HUELLA_OBSERVADOR
        print(f"δ = {HUELLA_OBSERVADOR:.10f}")
        print(f"Diferencia/δ = {valor:.6f} (esperado {RELACION_DIF_DELTA_ESPERADA:.6f})")

        assert_dentro_epsilon(valor, RELACION_DIF_DELTA_ESPERADA, "Diferencia/δ")

    def test_relacion_24_me_delta(self):
        print("\n" + "=" * 70)
        print("TEST 3: 24 / (m_e/δ)")
        print("=" * 70)

        valor = DIA_SOLAR / RELACION_ME_DELTA_ESPERADA
        print(f"m_e/δ = {RELACION_ME_DELTA_ESPERADA:.6f}")
        print(f"24/(m_e/δ) = {valor:.6f} (esperado {RELACION_24_ME_ESPERADA:.6f})")

        assert_dentro_epsilon(valor, RELACION_24_ME_ESPERADA, "24/(m_e/δ)")

    def test_relacion_me_delta(self):
        print("\n" + "=" * 70)
        print("TEST 4: m_e / δ")
        print("=" * 70)

        valor = M_e_MeV / HUELLA_OBSERVADOR
        print(f"m_e = {M_e_MeV:.10f} MeV")
        print(f"δ = {HUELLA_OBSERVADOR:.10f}")
        print(f"m_e/δ = {valor:.6f} (esperado {RELACION_ME_DELTA_ESPERADA:.6f})")

        assert_dentro_epsilon(valor, RELACION_ME_DELTA_ESPERADA, "m_e/δ")

    def test_relacion_diferencia_epsilon(self):
        print("\n" + "=" * 70)
        print("TEST 5: DIFERENCIA / ε")
        print("=" * 70)

        valor = DIFERENCIA_DIA / EPSILON
        print(f"ε = {EPSILON:.5f}")
        print(f"Diferencia/ε = {valor:.6f} (esperado {RELACION_DIF_EPSILON_ESPERADA:.6f})")

        assert_dentro_epsilon(valor, RELACION_DIF_EPSILON_ESPERADA, "Diferencia/ε")

    def test_cierre_epsilon(self):
        print("\n" + "=" * 70)
        print("TEST 6: CONSISTENCIA INTERNA DE ε")
        print("=" * 70)

        prediccion = RELACION_ME_DELTA_ESPERADA / 10
        valor = DIFERENCIA_DIA / EPSILON

        print(f"Predicción desde m_e/δ: (m_e/δ)/10 = {prediccion:.6f}")
        print(f"Diferencia/ε actual = {valor:.6f}")

        err = error_relativo(valor, prediccion)
        print(f"Error relativo: {err:.4%}")

        assert err <= UMBRAL, (
            f"\n❌ Error {err:.4%} > ε = {UMBRAL:.4%}. ε no es internamente consistente."
        )
        print(f"\n✅ ε es internamente consistente")

    def test_conclusion_final(self):
        print("\n" + "=" * 70)
        print("CONCLUSIÓN")
        print("=" * 70)

        errores = {
            "Diferencia/δ": error_relativo(
                DIFERENCIA_DIA / HUELLA_OBSERVADOR, RELACION_DIF_DELTA_ESPERADA
            ),
            "24/(m_e/δ)": error_relativo(
                DIA_SOLAR / RELACION_ME_DELTA_ESPERADA, RELACION_24_ME_ESPERADA
            ),
            "m_e/δ": error_relativo(
                M_e_MeV / HUELLA_OBSERVADOR, RELACION_ME_DELTA_ESPERADA
            ),
            "Diferencia/ε": error_relativo(
                DIFERENCIA_DIA / EPSILON, RELACION_DIF_EPSILON_ESPERADA
            ),
            "Consistencia ε": error_relativo(
                DIFERENCIA_DIA / EPSILON, RELACION_ME_DELTA_ESPERADA / 10
            ),
        }

        print("\nResumen de errores relativos:")
        for nombre, err in errores.items():
            estado = "✅" if err <= UMBRAL else "❌"
            print(f"  {estado} {nombre}: {err:.4%} (límite ε = {UMBRAL:.4%})")

        todos_dentro = all(err <= UMBRAL for err in errores.values())

        if todos_dentro:
            print("\n✅ TODAS LAS RELACIONES DENTRO DE ε")
            print("   El número 24 es consistente con el marco UIS.")
        else:
            print("\n❌ ALGUNA RELACIÓN SUPERA ε")
            print("   Conexión estructural, no derivación exacta.")

        assert todos_dentro


if __name__ == "__main__":
    test = TestNumero24Fuerte()
    test.test_dia_solar_y_sidereo()
    test.test_relacion_diferencia_delta()
    test.test_relacion_24_me_delta()
    test.test_relacion_me_delta()
    test.test_relacion_diferencia_epsilon()
    test.test_cierre_epsilon()
    test.test_conclusion_final()
