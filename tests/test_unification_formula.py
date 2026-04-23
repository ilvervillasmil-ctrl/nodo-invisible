import math
import pytest

# ============================================================================
# TEST DE LA CONSTANTE K - ¿ES REAL O ES UN PARCHE?
# ============================================================================
#
# Hipótesis: La masa del electrón se puede escribir como m_e = β × K
# donde K debe ser una constante derivada del marco (no un número arbitrario).
#
# Probamos diferentes candidatos para K:
#   K1 = β / ε
#   K2 = 1 / (β² × δ)
#   K3 = 27³ × (π/√2) / 100
#   K4 = α_em⁻¹ pura / 100
#   K5 = R_cosm / β
#   K6 = ε / β²
#
# Si algún K constante del marco hace que m_e = β × K (o β² × K),
# entonces la masa del electrón está DERIVADA, no ajustada.
# ============================================================================

# CONSTANTES FUNDAMENTALES
BETA = 1 / 27
BETA_CUADRADO = BETA ** 2
ALPHA = 26 / 27

# GEOMETRÍA DEL CUBO
EMPAQUETAMIENTO = math.pi / math.sqrt(2)
HUELLA_OBSERVADOR = 60 - (27 * EMPAQUETAMIENTO)  # δ = 0.02108033486

# CONSTANTE COSMOLÓGICA Λ
PHI = (1 + math.sqrt(5)) / 2
EXPONENTE_LAMBDA = 27 * math.pi + BETA * (PHI ** 2)
LAMBDA_UCF = BETA ** EXPONENTE_LAMBDA

# RESIDUO DEL OBSERVADOR
EPSILON = 0.02716

# CONSTANTE DE ESTRUCTURA FINA PURA
ALPHA_EM_PURA = (42 * math.pi) / ALPHA  # = 137.022

# ESCALA COSMOLÓGICA R
R_cosm = -math.log(LAMBDA_UCF)

# MASA DEL ELECTRÓN (experimental)
M_e_MeV = 0.5109989461


class TestConstanteK:
    """Test para determinar si K es una constante real del marco"""

    # -------------------------------------------------------------------------
    # HIPÓTESIS: K1 = β / ε
    # m_e = β × K1 = β × (β / ε) = β² / ε
    # -------------------------------------------------------------------------
    def test_k1_beta_cuadrado_sobre_epsilon(self):
        """Hipótesis K1: m_e = β² / ε"""
        print("\n" + "="*70)
        print("TEST K1: m_e = β² / ε")
        print("="*70)
        
        m_e_calc = BETA_CUADRADO / EPSILON
        error = abs(m_e_calc - M_e_MeV) / M_e_MeV * 100
        
        print(f"β² = {BETA_CUADRADO:.10f}")
        print(f"ε = {EPSILON:.5f}")
        print(f"β² / ε = {m_e_calc:.6f} MeV")
        print(f"m_e experimental = {M_e_MeV:.6f} MeV")
        print(f"Error = {error:.4f}%")
        
        # Un error < 5% sería aceptable (estamos cerca)
        if error < 5.0:
            print("✅ K1: CERCA (error < 5%)")
        else:
            print("❌ K1: FALLA")
        
        assert error < 5.0, f"K1 falla: error {error:.2f}%"

    # -------------------------------------------------------------------------
    # HIPÓTESIS: K2 = 1 / (β² × δ)
    # m_e = β² × K2 = 1 / δ
    # -------------------------------------------------------------------------
    def test_k2_inverso_de_delta(self):
        """Hipótesis K2: m_e = 1 / δ"""
        print("\n" + "="*70)
        print("TEST K2: m_e = 1 / δ")
        print("="*70)
        
        m_e_calc = 1 / HUELLA_OBSERVADOR
        error = abs(m_e_calc - M_e_MeV) / M_e_MeV * 100
        
        print(f"δ = {HUELLA_OBSERVADOR:.6f}")
        print(f"1/δ = {m_e_calc:.6f} MeV")
        print(f"m_e experimental = {M_e_MeV:.6f} MeV")
        print(f"Error = {error:.4f}%")
        
        if error < 5.0:
            print("✅ K2: CERCA (error < 5%)")
        else:
            print("❌ K2: FALLA")
        
        assert error < 5.0, f"K2 falla: error {error:.2f}%"

    # -------------------------------------------------------------------------
    # HIPÓTESIS: K3 = α_em⁻¹ pura / 100
    # m_e = β² × K3
    # -------------------------------------------------------------------------
    def test_k3_alpha_em_pura_sobre_cien(self):
        """Hipótesis K3: m_e = β² × (α_em⁻¹ pura / 100)"""
        print("\n" + "="*70)
        print("TEST K3: m_e = β² × (α_em⁻¹ pura / 100)")
        print("="*70)
        
        K3 = ALPHA_EM_PURA / 100
        m_e_calc = BETA_CUADRADO * K3
        error = abs(m_e_calc - M_e_MeV) / M_e_MeV * 100
        
        print(f"α_em⁻¹ pura = {ALPHA_EM_PURA:.3f}")
        print(f"K3 = α_em⁻¹/100 = {K3:.6f}")
        print(f"β² = {BETA_CUADRADO:.10f}")
        print(f"β² × K3 = {m_e_calc:.6f} MeV")
        print(f"m_e experimental = {M_e_MeV:.6f} MeV")
        print(f"Error = {error:.4f}%")
        
        if error < 5.0:
            print("✅ K3: CERCA (error < 5%)")
        else:
            print("❌ K3: FALLA")
        
        assert error < 5.0, f"K3 falla: error {error:.2f}%"

    # -------------------------------------------------------------------------
    # HIPÓTESIS: K4 = 27³ × (π/√2) / 100
    # m_e = β² × K4
    # -------------------------------------------------------------------------
    def test_k4_geometria_del_cubo(self):
        """Hipótesis K4: m_e = β² × (27³ × (π/√2) / 100)"""
        print("\n" + "="*70)
        print("TEST K4: m_e = β² × (27³ × (π/√2) / 100)")
        print("="*70)
        
        factor_geometrico = (27 ** 3) * (math.pi / math.sqrt(2))
        K4 = factor_geometrico / 100
        m_e_calc = BETA_CUADRADO * K4
        error = abs(m_e_calc - M_e_MeV) / M_e_MeV * 100
        
        print(f"27³ × (π/√2) = {factor_geometrico:.2f}")
        print(f"K4 = {K4:.4f}")
        print(f"β² = {BETA_CUADRADO:.10f}")
        print(f"β² × K4 = {m_e_calc:.6f} MeV")
        print(f"m_e experimental = {M_e_MeV:.6f} MeV")
        print(f"Error = {error:.4f}%")
        
        if error < 5.0:
            print("✅ K4: CERCA (error < 5%)")
        else:
            print("❌ K4: FALLA")
        
        assert error < 5.0, f"K4 falla: error {error:.2f}%"

    # -------------------------------------------------------------------------
    # HIPÓTESIS: K5 = β × R_cosm
    # m_e = β² × R_cosm
    # -------------------------------------------------------------------------
    def test_k5_beta_por_R_cosm(self):
        """Hipótesis K5: m_e = β² × R_cosm"""
        print("\n" + "="*70)
        print("TEST K5: m_e = β² × R_cosm")
        print("="*70)
        
        m_e_calc = BETA_CUADRADO * R_cosm
        error = abs(m_e_calc - M_e_MeV) / M_e_MeV * 100
        
        print(f"R_cosm = {R_cosm:.4f}")
        print(f"β² = {BETA_CUADRADO:.10f}")
        print(f"β² × R_cosm = {m_e_calc:.6f} MeV")
        print(f"m_e experimental = {M_e_MeV:.6f} MeV")
        print(f"Error = {error:.4f}%")
        
        if error < 5.0:
            print("✅ K5: CERCA (error < 5%)")
        else:
            print("❌ K5: FALLA")
        
        assert error < 5.0, f"K5 falla: error {error:.2f}%"

    # -------------------------------------------------------------------------
    # HIPÓTESIS: K6 = δ × 1000
    # m_e = K6 × β
    # -------------------------------------------------------------------------
    def test_k6_delta_por_mil(self):
        """Hipótesis K6: m_e = (δ × 1000) × β"""
        print("\n" + "="*70)
        print("TEST K6: m_e = (δ × 1000) × β")
        print("="*70)
        
        K6 = HUELLA_OBSERVADOR * 1000
        m_e_calc = K6 * BETA
        error = abs(m_e_calc - M_e_MeV) / M_e_MeV * 100
        
        print(f"δ × 1000 = {K6:.4f}")
        print(f"β = {BETA:.10f}")
        print(f"(δ×1000) × β = {m_e_calc:.6f} MeV")
        print(f"m_e experimental = {M_e_MeV:.6f} MeV")
        print(f"Error = {error:.4f}%")
        
        if error < 5.0:
            print("✅ K6: CERCA (error < 5%)")
        else:
            print("❌ K6: FALLA")
        
        assert error < 5.0, f"K6 falla: error {error:.2f}%"

    # -------------------------------------------------------------------------
    # LA QUE YA CONOCEMOS: m_e = 24.24 × δ
    # -------------------------------------------------------------------------
    def test_veinticuatro_por_delta(self):
        """Referencia: m_e = 24.24 × δ (error ~2.5%)"""
        print("\n" + "="*70)
        print("REFERENCIA: m_e = 24.24 × δ")
        print("="*70)
        
        m_e_calc = 24.24 * HUELLA_OBSERVADOR
        error = abs(m_e_calc - M_e_MeV) / M_e_MeV * 100
        
        print(f"24.24 × δ = {m_e_calc:.6f} MeV")
        print(f"m_e experimental = {M_e_MeV:.6f} MeV")
        print(f"Error = {error:.4f}%")
        
        # Esta ya sabemos que pasa (error ~2.5%)
        assert error < 3.0, f"Referencia falla: error {error:.2f}%"
        print("✅ REFERENCIA VERIFICADA")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("TEST DE LA CONSTANTE K")
    print("Buscando si K es una constante real del marco o un ajuste arbitrario")
    print("="*80)
    
    pytest.main([__file__, "-v", "-s"])
