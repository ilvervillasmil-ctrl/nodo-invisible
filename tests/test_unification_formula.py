import math

BETA = 1 / 27
BETA_CUADRADO = BETA ** 2
ALPHA = 26 / 27
HUELLA_OBSERVADOR = 60 - 27 * math.pi / math.sqrt(2)
EPSILON = 0.02716
R_cosm = -math.log(BETA ** (27 * math.pi + BETA * ((1+math.sqrt(5))/2)**2))
ALPHA_EM_PURA = 42 * math.pi / ALPHA

# Factores geométricos
KAPPA_H = 27**3 * math.sqrt(3) / (math.pi * 1.2)  # η ~ 1.2 empaquetamiento

# K candidatos
K1 = BETA / EPSILON
K2 = 1 / (BETA_CUADRADO * HUELLA_OBSERVADOR)
K3 = 27**3 * (math.pi / math.sqrt(2))
K4 = R_cosm / BETA
K5 = ALPHA_EM_PURA / 100
K6 = KAPPA_H / BETA

# Masa del electrón experimental
m_e_MeV = 0.5109989461

# Masa del electrón PREDICHA por cada K
m1 = BETA * K1
m2 = BETA_CUADRADO * K2
m3 = BETA * K3
m4 = BETA_CUADRADO * K4
m5 = BETA * K5
m6 = BETA_CUADRADO * K6

print("🔬 TEST DE K COMO CONSTANTE ESTRICTAMENTE DERIVADA")
print("="*60)
for i, (k_val, m_pred, nombre) in enumerate([
    (K1, m1, "β / ε"),
    (K2, m2, "1/(β²·δ)"),
    (K3, m3, "27³·(π/√2)"),
    (K4, m4, "R_cosm / β"),
    (K5, m5, "α_em⁻¹/100"),
    (K6, m6, "κ_H / β")
], 1):
    error = abs(m_pred - m_e_MeV) / m_e_MeV * 100
    print(f"\nK{i} = {nombre}")
    print(f"  K = {k_val:.4e}")
    print(f"  m_e predicha = {m_pred:.6f} MeV")
    print(f"  m_e exp      = {m_e_MeV:.6f} MeV")
    print(f"  Error = {error:.4f}%")
    if error < 0.5:
        print("  ✅ K válido (error < 0.5%)")
    else:
        print("  ❌ K NO válido")
