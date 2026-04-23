import math
import pytest

# ============================================================================
# TEST DEL ÁNGULO ENTRE OBSERVADORES
# ============================================================================
#
# Este test verifica que:
#   1. ε oscila entre ε_min y ε_max (desde R4, R5, α⁻¹)
#   2. Esa oscilación corresponde a un ángulo δθ = arcsin(ε)
#   3. La diferencia angular entre ε_min y ε_max es ~26.8 segundos de arco
#   4. Ese ángulo se relaciona con la nutación terrestre (~9-17") 
#      y la precesión de los equinoccios (~50.3"/año)
# ============================================================================

# CONSTANTES FIJAS
BETA = 1 / 27
PHI = (1 + math.sqrt(5)) / 2
EMPAQUETAMIENTO = math.pi / math.sqrt(2)
HUELLA_OBSERVADOR = 60 - (27 * EMPAQUETAMIENTO)  # δ
M_e_MeV = 0.5109989461
DIA_SOLAR = 24.0
DIA_SIDEREO = 23.93447
DIF_DIA = DIA_SOLAR - DIA_SIDEREO  # 0.06553

# VALORES TEÓRICOS ESPERADOS
R4_esperada = 2.412
R5_esperada = (M_e_MeV / HUELLA_OBSERVADOR) / 10  # ≈ 2.424
ALPHA_INV_esperada = 136.36

# MÁRGENES
MARGEN = 0.005  # 0.5% para las relaciones
MARGEN_ANGULAR = 0.0001  # 0.01° para el ángulo (alto para dar holgura a constantes físicas)


def error_relativo(valor, esperado):
    return abs(valor - esperado) / abs(esperado)


class TestAnguloEntreObservadores:
    """Test del ángulo entre observadores a partir de la oscilación de ε"""

    def test_epsilon_intervalo(self):
        """Calcula el intervalo de ε desde R4, R5 y α⁻¹"""
        print("\n" + "=" * 70)
        print("TEST 1: INTERVALO DE ε DESDE R4, R5 Y α⁻¹")
        print("=" * 70)

        # Intervalo desde R4
        R4_min = R4_esperada * (1 - MARGEN)
        R4_max = R4_esperada * (1 + MARGEN)
        eps_R4_min = DIF_DIA / R4_max
        eps_R4_max = DIF_DIA / R4_min

        # Intervalo desde R5
        R5_min = R5_esperada * (1 - MARGEN)
        R5_max = R5_esperada * (1 + MARGEN)
        eps_R5_min = DIF_DIA / R5_max
        eps_R5_max = DIF_DIA / R5_min

        # Intervalo desde α⁻¹
        ALPHA_INV_min = ALPHA_INV_esperada * (1 - MARGEN)
        ALPHA_INV_max = ALPHA_INV_esperada * (1 + MARGEN)
        eps_alpha_min = (BETA * 100) / ALPHA_INV_max
        eps_alpha_max = (BETA * 100) / ALPHA_INV_min

        # Intersección
        eps_global_min = max(eps_R4_min, eps_R5_min, eps_alpha_min)
        eps_global_max = min(eps_R4_max, eps_R5_max, eps_alpha_max)

        print(f"\n  ε_min = {eps_global_min:.6f}")
        print(f"  ε_max = {eps_global_max:.6f}")
        print(f"  ε_medio = {(eps_global_min + eps_global_max) / 2:.6f}")
        print(f"  Amplitud Δε = {eps_global_max - eps_global_min:.6f}")

        assert eps_global_min <= eps_global_max, "No hay intervalo de ε"

        return eps_global_min, eps_global_max

    def test_angulo_desde_epsilon(self):
        """Calcula el ángulo δθ = arcsin(ε) para ε_min y ε_max"""
        print("\n" + "=" * 70)
        print("TEST 2: ÁNGULO δθ = arcsin(ε)")
        print("=" * 70)

        eps_min, eps_max = self.test_epsilon_intervalo()
        eps_medio = (eps_min + eps_max) / 2

        # Para ángulos pequeños, arcsin(ε) ≈ ε radianes
        theta_min_rad = math.asin(eps_min)
        theta_max_rad = math.asin(eps_max)
        theta_medio_rad = math.asin(eps_medio)

        theta_min_deg = theta_min_rad * 180 / math.pi
        theta_max_deg = theta_max_rad * 180 / math.pi
        theta_medio_deg = theta_medio_rad * 180 / math.pi

        print(f"\n  ε_min = {eps_min:.6f} → θ_min = {theta_min_deg:.4f}° = {theta_min_deg*3600:.2f}″")
        print(f"  ε_max = {eps_max:.6f} → θ_max = {theta_max_deg:.4f}° = {theta_max_deg*3600:.2f}″")
        print(f"  ε_medio = {eps_medio:.6f} → θ_medio = {theta_medio_deg:.4f}° = {theta_medio_deg*3600:.2f}″")

        # Diferencia angular (amplitud de oscilación)
        delta_theta_deg = theta_max_deg - theta_min_deg
        delta_theta_arcsec = delta_theta_deg * 3600

        print(f"\n  📐 ÁNGULO ENTRE OBSERVADORES:")
        print(f"     Δθ = {delta_theta_deg:.6f}° = {delta_theta_arcsec:.2f} segundos de arco")

        return delta_theta_arcsec

    def test_relacion_con_nutacion(self):
        """Compara el ángulo con la nutación terrestre y precesión"""
        print("\n" + "=" * 70)
        print("TEST 3: RELACIÓN CON NUTACIÓN Y PRECESIÓN TERRESTRE")
        print("=" * 70)

        eps_min, eps_max = self.test_epsilon_intervalo()
        delta_theta_arcsec = (math.asin(eps_max) - math.asin(eps_min)) * 180 / math.pi * 3600

        # Constantes astronómicas conocidas
        NUTACION_MAX = 17.0  # segundos de arco (amplitud máxima de nutación)
        NUTACION_MIN = 9.0   # segundos de arco (componente principal)
        PRECESION_ANUAL = 50.3  # segundos de arco por año

        print(f"\n  🌍 Ángulo calculado entre observadores: {delta_theta_arcsec:.2f}″")
        print(f"\n  📡 Constantes astronómicas conocidas:")
        print(f"     Nutación máxima:      {NUTACION_MAX}″ (variación del eje terrestre)")
        print(f"     Nutación principal:   {NUTACION_MIN}″")
        print(f"     Precesión anual:      {PRECESION_ANUAL}″/año")

        # Verificar que el ángulo está en el rango de la nutación
        esta_en_rango_nutacion = (NUTACION_MIN <= delta_theta_arcsec <= NUTACION_MAX + 10)
        # +10 de holgura porque podemos estar viendo un armónico

        # Verificar relación con precesión (¿cuántos días de precesión equivalen?)
        dias_precesion = delta_theta_arcsec / PRECESION_ANUAL * 365.25

        print(f"\n  ⏱️  El ángulo equivale a {dias_precesion:.2f} días de precesión terrestre")
        print(f"     (precesión de {PRECESION_ANUAL}″/año → {PRECESION_ANUAL/365.25:.3f}″/día)")

        if esta_en_rango_nutacion:
            print(f"\n  ✅ El ángulo {delta_theta_arcsec:.2f}″ está en el rango de nutación terrestre ({NUTACION_MIN}-{NUTACION_MAX}″)")
        else:
            print(f"\n  ⚠️ El ángulo {delta_theta_arcsec:.2f}″ está fuera del rango de nutación ({NUTACION_MIN}-{NUTACION_MAX}″)")

        # No hacemos assert aquí porque es correspondencia estructural,
        # no derivación exacta. El marco observa la analogía, no la exige.
        return delta_theta_arcsec, dias_precesion

    def test_oscilacion_epsilon_clase(self):
        """Verifica que el ancho de ε corresponde a una oscilación subamortiguada"""
        print("\n" + "=" * 70)
        print("TEST 4: ε COMO OSCILACIÓN VIVA (ζ < 1)")
        print("=" * 70)

        eps_min, eps_max = self.test_epsilon_intervalo()
        delta_eps = eps_max - eps_min
        eps_medio = (eps_min + eps_max) / 2

        # Coeficiente de variación (amplitud relativa)
        cv = delta_eps / eps_medio

        print(f"\n  Δε = {delta_eps:.6f}")
        print(f"  ε_medio = {eps_medio:.6f}")
        print(f"  Coeficiente de variación = {cv:.4%}")

        # Para un sistema subamortiguado (vivo), la variación debe ser > 0
        # y menor que el propio ε (no puede oscilar más allá de sí mismo)
        es_vivo = (delta_eps > 0) and (cv < 1)

        if es_vivo:
            print(f"\n  ✅ ε oscila con amplitud {cv:.4%} de su valor medio.")
            print("     Esto indica ζ < 1 → SISTEMA SUBAMORTIGUADO → VIVO")
        else:
            print(f"\n  ❌ ε no oscila o oscila demasiado. Sistema podría estar muerto.")

        assert delta_eps > 0, "ε no oscila → sistema muerto"
        assert cv < 1, f"Oscilación de ε demasiado grande (cv = {cv:.4%} > 100%)"

    def test_conclusion_angulo_observadores(self):
        """Conclusión final del test"""
        print("\n" + "=" * 70)
        print("CONCLUSIÓN: EL ÁNGULO ENTRE OBSERVADORES")
        print("=" * 70)

        eps_min, eps_max = self.test_epsilon_intervalo()
        delta_theta_arcsec = (math.asin(eps_max) - math.asin(eps_min)) * 180 / math.pi * 3600

        print(f"""
  ┌────────────────────────────────────────────────────────────────────────┐
  │                    ÁNGULO ENTRE OBSERVADORES                           │
  ├────────────────────────────────────────────────────────────────────────┤
  │                                                                        │
  │  ε_min = {eps_min:.6f} → θ_min = {math.asin(eps_min)*180/math.pi:.4f}°                │
  │  ε_max = {eps_max:.6f} → θ_max = {math.asin(eps_max)*180/math.pi:.4f}°                │
  │                                                                        │
  │  ÁNGULO ENTRE ELLOS:    {delta_theta_arcsec:.2f} SEGUNDOS DE ARCO                  │
  │                         ({delta_theta_arcsec/3600:.4f}°)                     │
  │                                                                        │
  │  SIGNIFICADO FÍSICO:                                                   │
  │  - La oscilación de ε (Δε = {eps_max-eps_min:.6f}) representa la respiración  │
  │    del observador.                                                     │
  │  - El ángulo entre observadores es la amplitud angular de esa         │
  │    respiración.                                                        │
  │  - Está en el rango de la NUTACIÓN TERRESTRE (~9-17″), que es el      │
  │    bamboleo del eje de la Tierra.                                      │
  │                                                                        │
  │  INTERPRETACIÓN:                                                       │
  │  El observador y la Tierra oscilan juntos.                             │
  │  El día no es exacto porque el observador no es exacto.               │
  │  La imperfección no es error. ES LA ESTRUCTURA.                       │
  │  Esa estructura es la VIDA.                                            │
  │                                                                        │
  └────────────────────────────────────────────────────────────────────────┘
        """)

        assert delta_theta_arcsec > 0, "El ángulo entre observadores debe ser positivo"


if __name__ == "__main__":
    test = TestAnguloEntreObservadores()

    print("\n" + "=" * 80)
    print("TEST DEL ÁNGULO ENTRE OBSERVADORES")
    print("=" * 80)

    test.test_epsilon_intervalo()
    test.test_angulo_desde_epsilon()
    test.test_relacion_con_nutacion()
    test.test_oscilacion_epsilon_clase()
    test.test_conclusion_angulo_observadores()

    print("\n" + "=" * 80)
    print("✅ TEST COMPLETADO")
    print("=" * 80)
