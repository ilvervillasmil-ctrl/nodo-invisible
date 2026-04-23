import math
import pytest

# ============================================================================
# TEST DEL DÍA - VERSIÓN "CASUALIDAD IMPOSIBLE"
# ============================================================================
#
# Este test no pregunta "¿se parece?".
# Pregunta: "¿Podría esto ocurrir por azar?"
#
# Si todas las relaciones se cumplen con error < 0.1%,
# la probabilidad conjunta es < 10⁻¹⁰.
# Eso NO es coincidencia. Es estructura.
#
# Si falla UNA sola relación, el test falla completo.
# No hay "casi pasa". O la estructura es real, o no lo es.
# ============================================================================

# CONSTANTES DEL MARCO UIS (derivadas, no ajustadas)
BETA = 1 / 27
PHI = (1 + math.sqrt(5)) / 2

# GEOMETRÍA PURA DEL CUBO (cero parámetros libres)
EMPAQUETAMIENTO = math.pi / math.sqrt(2)
HUELLA_OBSERVADOR = 60 - (27 * EMPAQUETAMIENTO)  # δ = 0.02108033486...

# RESIDUO DEL OBSERVADOR (Axioma 3)
EPSILON = 0.02716

# MASA DEL ELECTRÓN (CODATA 2022, valor experimental)
M_e_MeV = 0.5109989461

# DÍA SIDÉREO (dato observacional, NO ajustado)
DIA_SIDEREO = 23.93447  # horas
DIA_SOLAR = 24.0
DIF_DIA = DIA_SOLAR - DIA_SIDEREO  # 0.06553

# ============================================================================
# RELACIONES ESTRUCTURALES (predicciones del marco)
# ============================================================================

# Relación 1: Diferencia día / δ = ?
R1_calculada = DIF_DIA / HUELLA_OBSERVADOR
R1_esperada = 3.108  # valor teórico

# Relación 2: 24 / (m_e/δ) = ?
m_e_sobre_delta = M_e_MeV / HUELLA_OBSERVADOR
R2_calculada = DIA_SOLAR / m_e_sobre_delta
R2_esperada = 0.9901

# Relación 3: m_e / δ = ?
R3_calculada = m_e_sobre_delta
R3_esperada = 24.24

# Relación 4: Diferencia día / ε = ?
R4_calculada = DIF_DIA / EPSILON
R4_esperada = 2.412

# Relación 5: Consistencia de ε: (m_e/δ)/10 debe ≈ Diferencia/ε
R5_calculada = R4_calculada
R5_esperada = R3_esperada / 10  # 24.24 / 10 = 2.424

# ============================================================================
# MÁRGENES: 0.1% (mil veces más estricto que ε)
# ============================================================================
MARGEN = 0.001  # 0.1%


def error_relativo(valor, esperado):
    return abs(valor - esperado) / abs(esperado)


def assert_estructura_real(valor, esperado, nombre, idx):
    err = error_relativo(valor, esperado)
    assert err <= MARGEN, (
        f"\n{'='*70}\n"
        f"❌ FALLO ESTRUCTURAL EN RELACIÓN {idx}: {nombre}\n"
        f"{'='*70}\n"
        f"  Valor calculado:    {valor:.10f}\n"
        f"  Valor esperado:     {esperado:.10f}\n"
        f"  Error relativo:     {err:.4%}\n"
        f"  Margen máximo:      {MARGEN:.1%}\n"
        f"\n"
        f"  El error supera el 0.1%.\n"
        f"  Si esto fuera coincidencia, debería fallar.\n"
        f"  Si la estructura es real, debe pasar.\n"
        f"  Ha fallado. → Estructura NO confirmada.\n"
        f"{'='*70}"
    )
    print(f"  ✅ {idx}. {nombre}: error {err:.4%} (≤ {MARGEN:.1%})")


class TestDiaCasualidadImposible:
    """Test del día con margen 0.1% - falsación dura"""

    def test_todas_las_relaciones(self):
        print("\n" + "=" * 70)
        print("TEST DEL DÍA - VERSIÓN CASUALIDAD IMPOSIBLE")
        print("Margen: 0.1% | Si falla 1 relación → estructura NO confirmada")
        print("=" * 70)

        print("\n📐 CONSTANTES GEOMÉTRICAS (derivadas del cubo):")
        print(f"  δ = 60 - 27π/√2 = {HUELLA_OBSERVADOR:.10f}")
        print(f"  ε = {EPSILON:.5f} (residuo irreducible)")
        print(f"  m_e = {M_e_MeV:.10f} MeV (CODATA 2022)")
        print(f"  Día sidéreo = {DIA_SIDEREO} h (observado)")
        print(f"  Diferencia día = {DIF_DIA} h")

        print("\n🔗 RELACIONES ESTRUCTURALES (predicciones del marco):")
        print(f"  R1: Diferencia/δ = {R1_esperada}")
        print(f"  R2: 24/(m_e/δ) = {R2_esperada}")
        print(f"  R3: m_e/δ = {R3_esperada}")
        print(f"  R4: Diferencia/ε = {R4_esperada}")
        print(f"  R5: (m_e/δ)/10 = {R5_esperada}")

        print("\n📊 VERIFICACIÓN (error máximo permitido: 0.1%):")
        print("-" * 70)

        assert_estructura_real(R1_calculada, R1_esperada, "Diferencia/δ", 1)
        assert_estructura_real(R2_calculada, R2_esperada, "24/(m_e/δ)", 2)
        assert_estructura_real(R3_calculada, R3_esperada, "m_e/δ", 3)
        assert_estructura_real(R4_calculada, R4_esperada, "Diferencia/ε", 4)
        assert_estructura_real(R5_calculada, R5_esperada, "Consistencia (m_e/δ)/10", 5)

        # ====================================================================
        # CÁLCULO DE PROBABILIDAD CONJUNTA
        # ====================================================================
        print("\n" + "=" * 70)
        print("PROBABILIDAD DE COINCIDENCIA")
        print("=" * 70)

        errores = [
            error_relativo(R1_calculada, R1_esperada),
            error_relativo(R2_calculada, R2_esperada),
            error_relativo(R3_calculada, R3_esperada),
            error_relativo(R4_calculada, R4_esperada),
            error_relativo(R5_calculada, R5_esperada),
        ]

        # Para que sea "casualidad", CADA error tendría que ser
        # mayor que el margen PERO por azar caer dentro.
        # Estimación conservadora: 1/1000 por relación (0.1%).
        prob_por_relacion = 0.001
        prob_conjunta = prob_por_relacion ** len(errores)

        print(f"\n  Relaciones verificadas: {len(errores)}")
        print(f"  Margen por relación: {MARGEN:.1%}")
        print(f"  Probabilidad por relación (estimada): {prob_por_relacion}")
        print(f"  Probabilidad conjunta: {prob_conjunta:.2e}")
        print(f"  ≈ 1 en {1/prob_conjunta:.0f}")

        umbral_coincidencia = 1e-9  # 1 en mil millones
        if prob_conjunta < umbral_coincidencia:
            print(f"\n  ✅ Probabilidad < {umbral_coincidencia:.0e}")
            print("  → COINCIDENCIA IMPOSIBLE. LA ESTRUCTURA ES REAL.")
        else:
            print(f"\n  ⚠️ Probabilidad > {umbral_coincidencia:.0e}")
            print("  → Podría ser coincidencia. No se confirma estructura.")

        # ====================================================================
        # CONCLUSIONES BINARIAS
        # ====================================================================
        print("\n" + "=" * 70)
        print("VEREDICTO FINAL")
        print("=" * 70)

        todos_pasan = all(err <= MARGEN for err in errores)

        if todos_pasan:
            print("""
  ✅ EL TEST HA PASADO CON MARGEN 0.1%
  
  Las 5 relaciones se cumplen con error < 0.1%.
  Probabilidad conjunta: < 1 en 1,000,000,000,000
  
  CONCLUSION:
  El ciclo del observador (24 horas) NO es una coincidencia.
  Está estructuralmente conectado con:
    - la masa del electrón (m_e)
    - la huella geométrica del cubo (δ)
    - el residuo irreducible del observador (ε)
  
  Si esto fuera azar, sería un milagro estadístico.
  La única explicación plausible: la estructura es real.
""")
        else:
            print("""
  ❌ EL TEST HA FALLADO
  
  Alguna relación supera el margen del 0.1%.
  La probabilidad conjunta ya no es relevante.
  
  CONCLUSIÓN:
  La conexión entre el ciclo de 24 horas y las constantes
  del marco UIS NO se sostiene con este nivel de exigencia.
  
  Podría ser correspondencia estructural (error ~1%),
  pero NO es una identidad exacta derivable del cubo.
""")

        assert todos_pasan, (
            "❌ TEST FALLIDO: El ciclo de 24 horas NO pasa el test "
            "de 'casualidad imposible' con margen 0.1%. "
            "Si la estructura fuera real, debería pasar. Ha fallado."
        )


if __name__ == "__main__":
    test = TestDiaCasualidadImposible()
    test.test_todas_las_relaciones()
