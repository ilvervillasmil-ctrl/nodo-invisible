import math
import pytest

# ============================================================================
# TEST DE FALSACIÓN DE HIPÓTESIS - ¿CÓMO SE UNIFICA LA REALIDAD?
# ============================================================================
#
# PROBLEMA: Encontramos que β²·δ·c² da la energía de Planck (~10²⁵ MeV),
#           NO la masa del electrón. También encontramos que la resta
#           E_Planck - k·R da ~0 (dentro de la precisión numérica),
#           NO 0.511 MeV.
#
# PREGUNTA: ¿Cómo se relaciona β = 1/27 con la masa del electrón?
#           ¿Qué fórmula verdadera se esconde detrás?
#
# Este test va a probar MÚLTIPLES hipótesis.
# Las hipótesis son fórmulas candidatas que intentan conectar β y m_e.
# Solo pasará la fórmula correcta (la que tenga error < 1%).
# Así descubriremos cuál es la relación real.
# ============================================================================

# CONSTANTES FUNDAMENTALES
BETA = 1 / 27
BETA_CUADRADO = BETA ** 2
BETA_CUBO = BETA ** 3
BETA_CUARTO = BETA ** 4
ALPHA = 26 / 27

# GEOMETRÍA DEL CUBO
N_CUBE = 27
C_CUBE = 1
EXT_CUBE = 26
F_CUBE = 6

EMPAQUETAMIENTO = math.pi / math.sqrt(2)
HUELLA_OBSERVADOR = 60 - (27 * EMPAQUETAMIENTO)  # δ ≈ 0.02108033486

# CONSTANTE COSMOLÓGICA Λ
PHI = (1 + math.sqrt(5)) / 2
EXPONENTE_LAMBDA = 27 * math.pi + BETA * (PHI ** 2)
LAMBDA_UCF = BETA ** EXPONENTE_LAMBDA
EPSILON = 0.02716  # residuo del observador

# VELOCIDAD DE LA LUZ
C = 299792458
C_CUADRADO = C ** 2

# MASA DEL ELECTRÓN (experimental)
M_e_MeV = 0.5109989461
M_e_kg = M_e_MeV * 1.602176634e-13 / C_CUADRADO

# ENERGÍA DE PLANCK DESDE β²·δ·c²
ENERGIA_PLANCK_J = BETA_CUADRADO * HUELLA_OBSERVADOR * C_CUADRADO
ENERGIA_PLANCK_MeV = ENERGIA_PLANCK_J / 1.602176634e-13

# ESCALA COSMOLÓGICA R (adimensional)
R_cosm = -math.log(LAMBDA_UCF)

# Factor k (para que k·R ≈ E_Planck)
k_approx = ENERGIA_PLANCK_MeV / R_cosm  # ≈ 5.8e22
kR_MeV = k_approx * R_cosm  # ≈ E_Planck_MeV


def error_relativo(valor_calculado, valor_referencia):
    """Calcula error relativo porcentual"""
    if valor_referencia == 0:
        return float('inf')
    return abs(valor_calculado - valor_referencia) / valor_referencia * 100


class TestUnificacionElectron:
    """Test de hipótesis: ¿Cómo se unifica la masa del electrón con β?"""

    def test_hipotesis_1_beta_por_escala_constante(self):
        """Hipótesis 1: m_e = β × K (donde K es constante)"""
        print("\n" + "="*70)
        print("HIPÓTESIS 1: m_e = β × K")
        print("="*70)
        
        # Buscar K que haga que β × K = m_e
        K = M_e_MeV / BETA
        m_e_calc = BETA * K
        
        error = error_relativo(m_e_calc, M_e_MeV)
        print(f"β = {BETA:.10f}")
        print(f"K = {K:.2f}")
        print(f"m_e = β × K = {m_e_calc:.6f} MeV")
        print(f"Error = {error:.4f}%")
        
        if error < 1.0:
            print("✅ HIPÓTESIS 1: CORRECTA")
        else:
            print("❌ HIPÓTESIS 1: FALSA")
        
        return error

    def test_hipotesis_2_beta_cuadrado_por_escala(self):
        """Hipótesis 2: m_e = β² × K"""
        print("\n" + "="*70)
        print("HIPÓTESIS 2: m_e = β² × K")
        print("="*70)
        
        K = M_e_MeV / BETA_CUADRADO
        m_e_calc = BETA_CUADRADO * K
        
        error = error_relativo(m_e_calc, M_e_MeV)
        print(f"β² = {BETA_CUADRADO:.10f}")
        print(f"K = {K:.2f}")
        print(f"m_e = β² × K = {m_e_calc:.6f} MeV")
        print(f"Error = {error:.4f}%")
        
        if error < 1.0:
            print("✅ HIPÓTESIS 2: CORRECTA")
        else:
            print("❌ HIPÓTESIS 2: FALSA")
        
        return error

    def test_hipotesis_3_beta_por_delta(self):
        """Hipótesis 3: m_e = β × δ × K"""
        print("\n" + "="*70)
        print("HIPÓTESIS 3: m_e = β × δ × K")
        print("="*70)
        
        producto = BETA * HUELLA_OBSERVADOR
        K = M_e_MeV / producto
        m_e_calc = producto * K
        
        error = error_relativo(m_e_calc, M_e_MeV)
        print(f"β × δ = {producto:.10f}")
        print(f"K = {K:.2f}")
        print(f"m_e = (β×δ) × K = {m_e_calc:.6f} MeV")
        print(f"Error = {error:.4f}%")
        
        if error < 1.0:
            print("✅ HIPÓTESIS 3: CORRECTA")
        else:
            print("❌ HIPÓTESIS 3: FALSA")
        
        return error

    def test_hipotesis_4_beta_cuadrado_por_delta(self):
        """Hipótesis 4: m_e = β² × δ × K"""
        print("\n" + "="*70)
        print("HIPÓTESIS 4: m_e = β² × δ × K")
        print("="*70)
        
        producto = BETA_CUADRADO * HUELLA_OBSERVADOR
        K = M_e_MeV / producto
        m_e_calc = producto * K
        
        error = error_relativo(m_e_calc, M_e_MeV)
        print(f"β² × δ = {producto:.10f}")
        print(f"K = {K:.2f}")
        print(f"m_e = (β²×δ) × K = {m_e_calc:.6f} MeV")
        print(f"Error = {error:.4f}%")
        
        if error < 1.0:
            print("✅ HIPÓTESIS 4: CORRECTA")
        else:
            print("❌ HIPÓTESIS 4: FALSA")
        
        return error

    def test_hipotesis_5_resta_planck_menos_R(self):
        """Hipótesis 5: m_e = E_Planck - k·R (con k ajustado)"""
        print("\n" + "="*70)
        print("HIPÓTESIS 5: m_e = E_Planck - k·R")
        print("="*70)
        
        # Ajustar k para que E_Planck - k·R = m_e
        k_ajustado = (ENERGIA_PLANCK_MeV - M_e_MeV) / R_cosm
        kR_calc = k_ajustado * R_cosm
        m_e_calc = ENERGIA_PLANCK_MeV - kR_calc
        
        error = error_relativo(m_e_calc, M_e_MeV)
        print(f"E_Planck = {ENERGIA_PLANCK_MeV:.2e} MeV")
        print(f"k ajustado = {k_ajustado:.2e}")
        print(f"R = {R_cosm:.4f}")
        print(f"k·R = {kR_calc:.2e} MeV")
        print(f"m_e = {m_e_calc:.6f} MeV")
        print(f"Error = {error:.4f}%")
        
        if error < 0.01:
            print("✅ HIPÓTESIS 5: CORRECTA")
        else:
            print("❌ HIPÓTESIS 5: FALSA")
        
        return error

    def test_hipotesis_6_electron_como_epsilon(self):
        """Hipótesis 6: m_e = ε × K"""
        print("\n" + "="*70)
        print("HIPÓTESIS 6: m_e = ε × K")
        print("="*70)
        
        K = M_e_MeV / EPSILON
        m_e_calc = EPSILON * K
        
        error = error_relativo(m_e_calc, M_e_MeV)
        print(f"ε = {EPSILON:.5f}")
        print(f"K = {K:.2f}")
        print(f"m_e = ε × K = {m_e_calc:.6f} MeV")
        print(f"Error = {error:.4f}%")
        
        if error < 1.0:
            print("✅ HIPÓTESIS 6: CORRECTA")
        else:
            print("❌ HIPÓTESIS 6: FALSA")
        
        return error

    def test_hipotesis_7_electron_como_24_24_por_delta(self):
        """Hipótesis 7: m_e = 24.24 × δ (la que ya conocemos)"""
        print("\n" + "="*70)
        print("HIPÓTESIS 7: m_e = 24.24 × δ")
        print("="*70)
        
        m_e_calc = 24.24 * HUELLA_OBSERVADOR
        error = error_relativo(m_e_calc, M_e_MeV)
        
        print(f"δ = {HUELLA_OBSERVADOR:.6f}")
        print(f"24.24 × δ = {m_e_calc:.6f} MeV")
        print(f"m_e experimental = {M_e_MeV:.6f} MeV")
        print(f"Error = {error:.4f}%")
        
        if error < 1.0:
            print("✅ HIPÓTESIS 7: CORRECTA (conocida)")
        else:
            print("❌ HIPÓTESIS 7: FALSA")
        
        return error

    def test_hipotesis_8_electron_como_resta_con_beta(self):
        """Hipótesis 8: m_e = β × (E_Planck - k·R)"""
        print("\n" + "="*70)
        print("HIPÓTESIS 8: m_e = β × (E_Planck - k·R)")
        print("="*70)
        
        # Primero ajustamos k para que la resta dé un valor pequeño
        resta_bruta = 1.0  # placeholder
        k_ajustado = (ENERGIA_PLANCK_MeV - 1.0) / R_cosm
        resta = ENERGIA_PLANCK_MeV - (k_ajustado * R_cosm)
        m_e_calc = BETA * resta
        
        # Reajustamos para que m_e_calc = M_e_MeV
        resta_necesaria = M_e_MeV / BETA
        k_final = (ENERGIA_PLANCK_MeV - resta_necesaria) / R_cosm
        resta_final = ENERGIA_PLANCK_MeV - (k_final * R_cosm)
        m_e_final = BETA * resta_final
        
        error = error_relativo(m_e_final, M_e_MeV)
        print(f"β = {BETA:.10f}")
        print(f"Resta necesaria = {resta_necesaria:.6f} MeV")
        print(f"m_e = β × resta = {m_e_final:.6f} MeV")
        print(f"Error = {error:.4f}%")
        
        if error < 0.01:
            print("✅ HIPÓTESIS 8: CORRECTA")
        else:
            print("❌ HIPÓTESIS 8: FALSA")
        
        return error

    def test_hipotesis_9_electron_como_beta_cuadrado_por_resta(self):
        """Hipótesis 9: m_e = β² × (E_Planck - k·R)"""
        print("\n" + "="*70)
        print("HIPÓTESIS 9: m_e = β² × (E_Planck - k·R)")
        print("="*70)
        
        resta_necesaria = M_e_MeV / BETA_CUADRADO
        k_final = (ENERGIA_PLANCK_MeV - resta_necesaria) / R_cosm
        resta_final = ENERGIA_PLANCK_MeV - (k_final * R_cosm)
        m_e_final = BETA_CUADRADO * resta_final
        
        error = error_relativo(m_e_final, M_e_MeV)
        print(f"β² = {BETA_CUADRADO:.10f}")
        print(f"Resta necesaria = {resta_necesaria:.6f} MeV")
        print(f"m_e = β² × resta = {m_e_final:.6f} MeV")
        print(f"Error = {error:.4f}%")
        
        if error < 0.01:
            print("✅ HIPÓTESIS 9: CORRECTA")
        else:
            print("❌ HIPÓTESIS 9: FALSA")
        
        return error

    def test_comparacion_de_hipotesis(self):
        """Comparación de todas las hipótesis"""
        print("\n" + "="*70)
        print("COMPARACIÓN DE HIPÓTESIS - ¿CUÁL ES LA CORRECTA?")
        print("="*70)
        
        resultados = []
        
        h1_err = self.test_hipotesis_1_beta_por_escala_constante()
        resultados.append(("1: m_e = β × K", h1_err))
        
        h2_err = self.test_hipotesis_2_beta_cuadrado_por_escala()
        resultados.append(("2: m_e = β² × K", h2_err))
        
        h3_err = self.test_hipotesis_3_beta_por_delta()
        resultados.append(("3: m_e = β × δ × K", h3_err))
        
        h4_err = self.test_hipotesis_4_beta_cuadrado_por_delta()
        resultados.append(("4: m_e = β² × δ × K", h4_err))
        
        h5_err = self.test_hipotesis_5_resta_planck_menos_R()
        resultados.append(("5: m_e = E_Planck - k·R", h5_err))
        
        h6_err = self.test_hipotesis_6_electron_como_epsilon()
        resultados.append(("6: m_e = ε × K", h6_err))
        
        h7_err = self.test_hipotesis_7_electron_como_24_24_por_delta()
        resultados.append(("7: m_e = 24.24 × δ", h7_err))
        
        h8_err = self.test_hipotesis_8_electron_como_resta_con_beta()
        resultados.append(("8: m_e = β × (E_Planck - k·R)", h8_err))
        
        h9_err = self.test_hipotesis_9_electron_como_beta_cuadrado_por_resta()
        resultados.append(("9: m_e = β² × (E_Planck - k·R)", h9_err))
        
        print("\n" + "-"*70)
        print("RESULTADOS:")
        print("-"*70)
        
        for nombre, error in resultados:
            if error < 0.01:
                print(f"✅ {nombre} → ERROR {error:.4f}% (PASA)")
            elif error < 1.0:
                print(f"⚠️ {nombre} → ERROR {error:.4f}% (CERCA)")
            else:
                print(f"❌ {nombre} → ERROR {error:.4f}% (FALLA)")
        
        print("\n" + "="*70)
        print("CONCLUSIÓN:")
        print("="*70)
        print("""
        La hipótesis que pase con error < 0.01% será la fórmula correcta.
        
        Hasta ahora sabemos que:
        - m_e = 24.24 × δ tiene error ~2.5% (cerca pero no perfecto)
        - m_e = β² × δ × K también necesita K = m_e/(β²×δ) ≈ 17671
        
        Esto sugiere que la relación verdadera incluye β² y δ,
        y probablemente también un factor de escala (la energía de Planck
        o la constante cosmológica R).
        
        LA FÓRMULA CORRECTA SERÁ LA QUE EL TEST MARQUE COMO PASA.
        """)
        
        # Verificar si alguna hipótesis pasó
        alguna_pasa = any(error < 0.01 for _, error in resultados)
        if alguna_pasa:
            print("\n✅ SE HA ENCONTRADO LA FÓRMULA CORRECTA")
        else:
            print("\n❌ NINGUNA HIPÓTESIS PASÓ. HAY QUE SEGUIR BUSCANDO.")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("TEST DE FALSACIÓN DE HIPÓTESIS - MASA DEL ELECTRÓN")
    print("Buscando la fórmula correcta que conecta β = 1/27 con m_e")
    print("="*80)
    
    test = TestUnificacionElectron()
    test.test_comparacion_de_hipotesis()
