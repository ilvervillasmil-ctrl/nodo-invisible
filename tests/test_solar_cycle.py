import math

# Constantes fijas (no cambian)
BETA = 1 / 27
PHI = (1 + math.sqrt(5)) / 2
EMPAQUETAMIENTO = math.pi / math.sqrt(2)
HUELLA_OBSERVADOR = 60 - (27 * EMPAQUETAMIENTO)  # δ
M_e_MeV = 0.5109989461
DIA_SOLAR = 24.0
DIA_SIDEREO = 23.93447
DIF_DIA = DIA_SOLAR - DIA_SIDEREO  # 0.06553

# ε original y ε optimizado
EPSILON_ORIGINAL = 0.02716
EPSILON_OPTIMO = DIF_DIA / ((M_e_MeV / HUELLA_OBSERVADOR) / 10)

print("=" * 70)
print("AJUSTE DE ε PARA CERRAR LA RELACIÓN 5")
print("=" * 70)

print(f"\nε original:        {EPSILON_ORIGINAL:.6f}")
print(f"ε óptimo:          {EPSILON_OPTIMO:.6f}")
print(f"Diferencia:        {EPSILON_ORIGINAL - EPSILON_OPTIMO:.6f}")
print(f"Error relativo:    {(EPSILON_ORIGINAL - EPSILON_OPTIMO)/EPSILON_ORIGINAL:.4%}")

# Relaciones con ε original
m_e_sobre_delta = M_e_MeV / HUELLA_OBSERVADOR
r5_original = DIF_DIA / EPSILON_ORIGINAL
r5_esperada = m_e_sobre_delta / 10

print(f"\n📊 RELACIÓN 5 (Consistencia ε):")
print(f"  (m_e/δ)/10 esperado = {r5_esperada:.6f}")
print(f"  Diferencia/ε (original) = {r5_original:.6f}")
print(f"  Error original: {(r5_original - r5_esperada)/r5_esperada:.4%}")

# Relaciones con ε optimizado
r5_optimo = DIF_DIA / EPSILON_OPTIMO
print(f"\n  Diferencia/ε (óptimo) = {r5_optimo:.6f}")
print(f"  Error óptimo: {(r5_optimo - r5_esperada)/r5_esperada:.4%}")

print("\n" + "=" * 70)
print("IMPACTO EN OTRAS RELACIONES QUE USAN ε")
print("=" * 70)

# Relación 4: Diferencia/ε
r4_original = DIF_DIA / EPSILON_ORIGINAL
r4_optimo = DIF_DIA / EPSILON_OPTIMO
r4_esperada = 2.412  # valor teórico

print(f"\nR4 (Diferencia/ε):")
print(f"  Esperado: {r4_esperada:.6f}")
print(f"  Original: {r4_original:.6f} (error {(r4_original - r4_esperada)/r4_esperada:.4%})")
print(f"  Óptimo:   {r4_optimo:.6f} (error {(r4_optimo - r4_esperada)/r4_esperada:.4%})")

# Si ε cambia, ¿afecta a qué otras constantes del marco?
print("\n🔗 OTRAS CONSTANTES DEL MARCO QUE DEPENDEN DE ε:")
print("  - α⁻¹_puro = (β/ε) × 100")
print("  - Λ (indirectamente, por ε en exponente?)")
print("  - m_e (no depende directamente de ε)")

alpha_inv_original = (BETA / EPSILON_ORIGINAL) * 100
alpha_inv_optimo = (BETA / EPSILON_OPTIMO) * 100
alpha_inv_esperado = 136.36

print(f"\n  α⁻¹_puro:")
print(f"    Esperado: {alpha_inv_esperado:.4f}")
print(f"    Original: {alpha_inv_original:.4f} (error {(alpha_inv_original - alpha_inv_esperado)/alpha_inv_esperado:.4%})")
print(f"    Óptimo:   {alpha_inv_optimo:.4f} (error {(alpha_inv_optimo - alpha_inv_esperado)/alpha_inv_esperado:.4%})")

print("\n" + "=" * 70)
print("CONCLUSIÓN")
print("=" * 70)

if abs(alpha_inv_optimo - alpha_inv_esperado) / alpha_inv_esperado < 0.001:
    print("\n✅ ε óptimo CIERRA α⁻¹_puro dentro del 0.1%")
else:
    print(f"\n⚠️ ε óptimo mueve α⁻¹_puro a {alpha_inv_optimo:.2f}")
    print("   La relación 5 se cierra, pero se abre otra incoherencia.")
