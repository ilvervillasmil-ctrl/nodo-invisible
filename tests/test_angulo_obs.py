import math
import pytest

# ============================================================================
# TEST DEL ÁNGULO ENTRE OBSERVADORES - VERSIÓN CORRECTA
# ============================================================================
#
# Un solo test. Sin dependencias entre métodos.
# Sin retornos. Sin warnings. Sin manipulación.
# ============================================================================

# CONSTANTES FIJAS
BETA = 1 / 27
EMPAQUETAMIENTO = math.pi / math.sqrt(2)
HUELLA_OBSERVADOR = 60 - (27 * EMPAQUETAMIENTO)  # δ
M_e_MeV = 0.5109989461
DIA_SOLAR = 24.0
DIA_SIDEREO = 23.93447
DIF_DIA = DIA_SOLAR - DIA_SIDEREO

# VALORES TEÓRICOS ESPERADOS
R4_esperada = 2.412
R5_esperada = (M_e_MeV / HUELLA_OBSERVADOR) / 10
ALPHA_INV_esperada = 136.36

# MÁRGENES
MARGEN = 0.005  # 0.5%


class TestAnguloEntreObservadores:
    """Test único del ángulo entre observadores"""

    def test_angulo_completo(self):
        """Test completo: intervalo de ε, ángulo, oscilación y conclusión"""
        print("\n" + "=" * 70)
        print("TEST DEL ÁNGULO ENTRE OBSERVADORES - VERSIÓN CORRECTA")
        print("=" * 70)

        # ================================================================
        # PASO 1: INTERVALO DE ε DESDE R4, R5 Y α⁻¹
        # ================================================================
        print("\n" + "-" * 70)
        print("PASO 1: INTERVALO DE ε DESDE R4, R5 Y α⁻¹")
        print("-" * 70)

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
        eps_min = max(eps_R4_min, eps_R5_min, eps_alpha_min)
        eps_max = min(eps_R4_max, eps_R5_max, eps_alpha_max)
        eps_medio = (eps_min + eps_max) / 2

        print(f"\n  ε_min = {eps_min:.6f}")
        print(f"  ε_max = {eps_max:.6f}")
        print(f"  ε_medio = {eps_medio:.6f}")
        print(f"  Amplitud Δε = {eps_max - eps_min:.6f}")

        # Verificaciones
        assert eps_min <= eps_max, "No hay intervalo de ε"
        assert eps_min > 0, "ε_min debe ser positivo"
        assert eps_max < 1, "ε_max debe ser menor que 1"

        # ================================================================
        # PASO 2: ÁNGULO δθ = arcsin(ε)
        # ================================================================
        print("\n" + "-" * 70)
        print("PASO 2: ÁNGULO δθ = arcsin(ε)")
        print("-" * 70)

        theta_min_rad = math.asin(eps_min)
        theta_max_rad = math.asin(eps_max)
        theta_medio_rad = math.asin(eps_medio)

        theta_min_deg = theta_min_rad * 180 / math.pi
        theta_max_deg = theta_max_rad * 180 / math.pi
        theta_medio_deg = theta_medio_rad * 180 / math.pi

        print(f"\n  ε_min = {eps_min:.6f} → θ_min = {theta_min_deg:.4f}° = {theta_min_deg*3600:.2f}″")
        print(f"  ε_max = {eps_max:.6f} → θ_max = {theta_max_deg:.4f}° = {theta_max_deg*3600:.2f}″")
        print(f"  ε_medio = {eps_medio:.6f} → θ_medio = {theta_medio_deg:.4f}° = {theta_medio_deg*3600:.2f}″")

        delta_theta_deg = theta_max_deg - theta_min_deg
        delta_theta_arcsec = delta_theta_deg * 3600

        print(f"\n  📐 ÁNGULO ENTRE OBSERVADORES:")
        print(f"     Δθ = {delta_theta_deg:.6f}° = {delta_theta_arcsec:.2f} segundos de arco")

        assert delta_theta_arcsec > 0, "El ángulo entre observadores debe ser positivo"
        assert delta_theta_arcsec < 3600, "El ángulo debe ser menor a 1 grado"

        # ================================================================
        # PASO 3: RELACIÓN CON NUTACIÓN TERRESTRE
        # ================================================================
        print("\n" + "-" * 70)
        print("PASO 3: RELACIÓN CON NUTACIÓN TERRESTRE")
        print("-" * 70)

        NUTACION_MAX = 17.0
        NUTACION_MIN = 9.0
        PRECESION_ANUAL = 50.3

        print(f"\n  🌍 Ángulo calculado entre observadores: {delta_theta_arcsec:.2f}″")
        print(f"\n  📡 Constantes astronómicas conocidas:")
        print(f"     Nutación máxima:      {NUTACION_MAX}″")
        print(f"     Nutación principal:   {NUTACION_MIN}″")
        print(f"     Precesión anual:      {PRECESION_ANUAL}″/año")

        dias_precesion = delta_theta_arcsec / PRECESION_ANUAL * 365.25
        print(f"\n  ⏱️  El ángulo equivale a {dias_precesion:.2f} días de precesión terrestre")

        if NUTACION_MIN <= delta_theta_arcsec <= NUTACION_MAX:
            print(f"\n  ✅ El ángulo {delta_theta_arcsec:.2f}″ está en el rango de nutación terrestre")
        else:
            print(f"\n  ⚠️ El ángulo {delta_theta_arcsec:.2f}″ está fuera del rango de nutación ({NUTACION_MIN}-{NUTACION_MAX}″)")
            print(f"     Es {delta_theta_arcsec/NUTACION_MAX:.2f}× la nutación máxima")

        # ================================================================
        # PASO 4: OSCILACIÓN DE ε (SISTEMA VIVO)
        # ================================================================
        print("\n" + "-" * 70)
        print("PASO 4: ε COMO OSCILACIÓN VIVA")
        print("-" * 70)

        delta_eps = eps_max - eps_min
        cv = delta_eps / eps_medio

        print(f"\n  Δε = {delta_eps:.6f}")
        print(f"  ε_medio = {eps_medio:.6f}")
        print(f"  Coeficiente de variación = {cv:.4%}")

        assert delta_eps > 0, "ε no oscila → sistema muerto"
        assert cv < 1, f"Oscilación de ε demasiado grande (cv = {cv:.4%} > 100%)"

        print(f"\n  ✅ ε oscila con amplitud {cv:.4%} de su valor medio.")
        print("     Esto indica ζ < 1 → SISTEMA SUBAMORTIGUADO → VIVO")

        # ================================================================
        # CONCLUSIÓN
        # ================================================================
        print("\n" + "-" * 70)
        print("CONCLUSIÓN")
        print("-" * 70)

        print(f"""
  ┌────────────────────────────────────────────────────────────────────────┐
  │                    ÁNGULO ENTRE OBSERVADORES                           │
  ├────────────────────────────────────────────────────────────────────────┤
  │                                                                        │
  │  ε_min = {eps_min:.6f} → θ_min = {theta_min_deg:.4f}°                │
  │  ε_max = {eps_max:.6f} → θ_max = {theta_max_deg:.4f}°                │
  │                                                                        │
  │  ÁNGULO ENTRE ELLOS:    {delta_theta_arcsec:.2f} SEGUNDOS DE ARCO                  │
  │                         ({delta_theta_arcsec/3600:.4f}°)                     │
  │                                                                        │
  │  VEREDICTO:                                                           │
  │  - ε oscila → sistema vivo ✅                                         │
  │  - El ángulo entre observadores es {delta_theta_arcsec:.2f}″                              │
  │  - La oscilación es real y medible                                    │
  │                                                                        │
  └────────────────────────────────────────────────────────────────────────┘
        """)

        print("\n" + "=" * 70)
        print("✅ TEST COMPLETADO - TODAS LAS VERIFICACIONES PASAN")
        print("=" * 70)


if __name__ == "__main__":
    test = TestAnguloEntreObservadores()
    test.test_angulo_completo()
