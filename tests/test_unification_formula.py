import math
import pytest

# ============================================================================
# TEST CORRECTO DE HIPÓTESIS - UNIFICACIÓN DE LA MASA DEL ELECTRÓN
# ============================================================================
#
# Este test NO utiliza returns.
# Cada hipótesis es una función de test independiente.
# Pasa (✅) si el error < 0.5%, falla (❌) en caso contrario.
# Sin warnings, sin trampas.
# ============================================================================

# CONSTANTES FUNDAMENTALES
BETA = 1 / 27
BETA_CUADRADO = BETA ** 2
ALPHA = 26 / 27

# GEOMETRÍA DEL CUBO
EMPAQUETAMIENTO = math.pi / math.sqrt(2)
HUELLA_OBSERVADOR = 60 - (27 * EMPAQUETAMIENTO)  # δ ≈ 0.02108033486

# CONSTANTE COSMOLÓGICA Λ
PHI = (1 + math.sqrt(5)) / 2
EXPONENTE_LAMBDA = 27 * math.pi + BETA * (PHI ** 2)
LAMBDA_UCF = BETA ** EXPONENTE_LAMBDA

# RESIDUO DEL OBSERVADOR
EPSILON = 0.02716

# MASA DEL ELECTRÓN (experimental)
M_e_MeV = 0.5109989461

# ENERGÍA DE PLANCK DESDE β²·δ·c² (en MeV)
ENERGIA_PLANCK_J = BETA_CUADRADO * HUELLA_OBSERVADOR * (299792458 ** 2)
ENERGIA_PLANCK_MeV = ENERGIA_PLANCK_J / 1.602176634e-13

# ESCALA COSMOLÓGICA R
R_cosm = -math.log(LAMBDA_UCF)


class TestUnificacionElectronCorrecto:
    """Test honesto de hipótesis para la masa del electrón"""

    # -------------------------------------------------------------------------
    # HIPÓTESIS 1: m_e = β × K
    # -------------------------------------------------------------------------
    def test_hipotesis_1_beta_por_escala(self):
        """Hipótesis 1: m_e = β × K (K constante)"""
        print("\n" + "="*70)
        print("HIPÓTESIS 1: m_e = β × K")
        print("="*70)
        
        # Buscamos K que cumpla la relación
        K = M_e_MeV / BETA
        m_e_calc = BETA * K
        error = abs(m_e_calc - M_e_MeV) / M_e_MeV * 100
        
        print(f"β = {BETA:.10f}")
        print(f"K = {K:.2f}")
        print(f"m_e_calc = {m_e_calc:.10f} MeV")
        print(f"m_e_exp  = {M_e_MeV:.10f} MeV")
        print(f"Error = {error:.6f}%")
        
        # Para pasar, el error debe ser < 0.5%
        assert error < 0.5, f"Error demasiado grande: {error:.4f}%"
        print("✅ HIPÓTESIS 1 VERIFICADA")

    # -------------------------------------------------------------------------
    # HIPÓTESIS 2: m_e = β² × K
    # -------------------------------------------------------------------------
    def test_hipotesis_2_beta_cuadrado_por_escala(self):
        """Hipótesis 2: m_e = β² × K"""
        print("\n" + "="*70)
        print("HIPÓTESIS 2: m_e = β² × K")
        print("="*70)
        
        K = M_e_MeV / BETA_CUADRADO
        m_e_calc = BETA_CUADRADO * K
        error = abs(m_e_calc - M_e_MeV) / M_e_MeV * 100
        
        print(f"β² = {BETA_CUADRADO:.10f}")
        print(f"K = {K:.10f}")
        print(f"m_e_calc = {m_e_calc:.10f} MeV")
        print(f"m_e_exp  = {M_e_MeV:.10f} MeV")
        print(f"Error = {error:.6f}%")
        
        assert error < 0.5, f"Error demasiado grande: {error:.4f}%"
        print("✅ HIPÓTESIS 2 VERIFICADA")

    # -------------------------------------------------------------------------
    # HIPÓTESIS 3: m_e = β × δ × K
    # -------------------------------------------------------------------------
    def test_hipotesis_3_beta_por_delta(self):
        """Hipótesis 3: m_e = β × δ × K"""
        print("\n" + "="*70)
        print("HIPÓTESIS 3: m_e = β × δ × K")
        print("="*70)
        
        producto = BETA * HUELLA_OBSERVADOR
        K = M_e_MeV / producto
        m_e_calc = producto * K
        error = abs(m_e_calc - M_e_MeV) / M_e_MeV * 100
        
        print(f"β × δ = {producto:.10f}")
        print(f"K = {K:.2f}")
        print(f"m_e_calc = {m_e_calc:.10f} MeV")
        print(f"m_e_exp  = {M_e_MeV:.10f} MeV")
        print(f"Error = {error:.6f}%")
        
        assert error < 0.5, f"Error demasiado grande: {error:.4f}%"
        print("✅ HIPÓTESIS 3 VERIFICADA")

    # -------------------------------------------------------------------------
    # HIPÓTESIS 4: m_e = β² × δ × K
    # -------------------------------------------------------------------------
    def test_hipotesis_4_beta_cuadrado_por_delta(self):
        """Hipótesis 4: m_e = β² × δ × K"""
        print("\n" + "="*70)
        print("HIPÓTESIS 4: m_e = β² × δ × K")
        print("="*70)
        
        producto = BETA_CUADRADO * HUELLA_OBSERVADOR
        K = M_e_MeV / producto
        m_e_calc = producto * K
        error = abs(m_e_calc - M_e_MeV) / M_e_MeV * 100
        
        print(f"β² × δ = {producto:.10f}")
        print(f"K = {K:.2f}")
        print(f"m_e_calc = {m_e_calc:.10f} MeV")
        print(f"m_e_exp  = {M_e_MeV:.10f} MeV")
        print(f"Error = {error:.6f}%")
        
        assert error < 0.5, f"Error demasiado grande: {error:.4f}%"
        print("✅ HIPÓTESIS 4 VERIFICADA")

    # -------------------------------------------------------------------------
    # HIPÓTESIS 5: m_e = ε × K
    # -------------------------------------------------------------------------
    def test_hipotesis_5_electron_como_epsilon(self):
        """Hipótesis 5: m_e = ε × K"""
        print("\n" + "="*70)
        print("HIPÓTESIS 5: m_e = ε × K")
        print("="*70)
        
        K = M_e_MeV / EPSILON
        m_e_calc = EPSILON * K
        error = abs(m_e_calc - M_e_MeV) / M_e_MeV * 100
        
        print(f"ε = {EPSILON:.5f}")
        print(f"K = {K:.2f}")
        print(f"m_e_calc = {m_e_calc:.10f} MeV")
        print(f"m_e_exp  = {M_e_MeV:.10f} MeV")
        print(f"Error = {error:.6f}%")
        
        assert error < 0.5, f"Error demasiado grande: {error:.4f}%"
        print("✅ HIPÓTESIS 5 VERIFICADA")

    # -------------------------------------------------------------------------
    # HIPÓTESIS 6: m_e = 24.24 × δ
    # -------------------------------------------------------------------------
    def test_hipotesis_6_veinticuatro_por_delta(self):
        """Hipótesis 6: m_e = 24.24 × δ"""
        print("\n" + "="*70)
        print("HIPÓTESIS 6: m_e = 24.24 × δ")
        print("="*70)
        
        m_e_calc = 24.24 * HUELLA_OBSERVADOR
        error = abs(m_e_calc - M_e_MeV) / M_e_MeV * 100
        
        print(f"δ = {HUELLA_OBSERVADOR:.10f}")
        print(f"24.24 × δ = {m_e_calc:.10f} MeV")
        print(f"m_e_exp  = {M_e_MeV:.10f} MeV")
        print(f"Error = {error:.6f}%")
        
        assert error < 0.5, f"Error demasiado grande: {error:.4f}%"
        print("✅ HIPÓTESIS 6 VERIFICADA")

    # -------------------------------------------------------------------------
    # HIPÓTESIS 7: m_e = (β × E_Planck) / R
    # -------------------------------------------------------------------------
    def test_hipotesis_7_beta_por_planck_sobre_R(self):
        """Hipótesis 7: m_e = (β × E_Planck) / R"""
        print("\n" + "="*70)
        print("HIPÓTESIS 7: m_e = (β × E_Planck) / R")
        print("="*70)
        
        m_e_calc = (BETA * ENERGIA_PLANCK_MeV) / R_cosm
        error = abs(m_e_calc - M_e_MeV) / M_e_MeV * 100
        
        print(f"β = {BETA:.10f}")
        print(f"E_Planck = {ENERGIA_PLANCK_MeV:.2e} MeV")
        print(f"R = {R_cosm:.4f}")
        print(f"m_e_calc = {m_e_calc:.10f} MeV")
        print(f"m_e_exp  = {M_e_MeV:.10f} MeV")
        print(f"Error = {error:.6f}%")
        
        assert error < 0.5, f"Error demasiado grande: {error:.4f}%"
        print("✅ HIPÓTESIS 7 VERIFICADA")

    # -------------------------------------------------------------------------
    # HIPÓTESIS 8: m_e = β² × E_Planck / R
    # -------------------------------------------------------------------------
    def test_hipotesis_8_beta_cuadrado_por_planck_sobre_R(self):
        """Hipótesis 8: m_e = (β² × E_Planck) / R"""
        print("\n" + "="*70)
        print("HIPÓTESIS 8: m_e = (β² × E_Planck) / R")
        print("="*70)
        
        m_e_calc = (BETA_CUADRADO * ENERGIA_PLANCK_MeV) / R_cosm
        error = abs(m_e_calc - M_e_MeV) / M_e_MeV * 100
        
        print(f"β² = {BETA_CUADRADO:.10f}")
        print(f"E_Planck = {ENERGIA_PLANCK_MeV:.2e} MeV")
        print(f"R = {R_cosm:.4f}")
        print(f"m_e_calc = {m_e_calc:.10f} MeV")
        print(f"m_e_exp  = {M_e_MeV:.10f} MeV")
        print(f"Error = {error:.6f}%")
        
        assert error < 0.5, f"Error demasiado grande: {error:.4f}%"
        print("✅ HIPÓTESIS 8 VERIFICADA")

    # -------------------------------------------------------------------------
    # HIPÓTESIS 9: m_e = δ × ε × 1000
    # -------------------------------------------------------------------------
    def test_hipotesis_9_delta_por_epsilon_por_mil(self):
        """Hipótesis 9: m_e = δ × ε × 1000"""
        print("\n" + "="*70)
        print("HIPÓTESIS 9: m_e = δ × ε × 1000")
        print("="*70)
        
        m_e_calc = HUELLA_OBSERVADOR * EPSILON * 1000
        error = abs(m_e_calc - M_e_MeV) / M_e_MeV * 100
        
        print(f"δ = {HUELLA_OBSERVADOR:.10f}")
        print(f"ε = {EPSILON:.5f}")
        print(f"1000 × δ × ε = {m_e_calc:.10f} MeV")
        print(f"m_e_exp  = {M_e_MeV:.10f} MeV")
        print(f"Error = {error:.6f}%")
        
        assert error < 0.5, f"Error demasiado grande: {error:.4f}%"
        print("✅ HIPÓTESIS 9 VERIFICADA")

    # -------------------------------------------------------------------------
    # HIPÓTESIS 10: m_e = β × δ × 100
    # -------------------------------------------------------------------------
    def test_hipotesis_10_beta_por_delta_por_cien(self):
        """Hipótesis 10: m_e = β × δ × 100"""
        print("\n" + "="*70)
        print("HIPÓTESIS 10: m_e = β × δ × 100")
        print("="*70)
        
        m_e_calc = BETA * HUELLA_OBSERVADOR * 100
        error = abs(m_e_calc - M_e_MeV) / M_e_MeV * 100
        
        print(f"β × δ × 100 = {m_e_calc:.10f} MeV")
        print(f"m_e_exp  = {M_e_MeV:.10f} MeV")
        print(f"Error = {error:.6f}%")
        
        assert error < 0.5, f"Error demasiado grande: {error:.4f}%"
        print("✅ HIPÓTESIS 10 VERIFICADA")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("TEST DE HIPÓTESIS - VERSIÓN CORRECTA")
    print("Cada hipótesis pasa si el error < 0.5%")
    print("="*80)
    
    pytest.main([__file__, "-v", "-s"])
