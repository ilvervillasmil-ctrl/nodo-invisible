import math
import pytest

# ============================================================================
# TEST DE FRECUENCIA DE MATERIA - VERSIÓN CORRECTA
# ============================================================================

h = 6.62607015e-34
eV_to_J = 1.602176634e-19
MeV_to_J = eV_to_J * 1e6

# Constantes del cubo
BETA = 1 / 27
BETA_CUADRADO = BETA ** 2
DELTA = 60 - (27 * math.pi / math.sqrt(2))

# Energía de Planck según el marco (Parte VI del documento)
E_P_marco_J = (27 ** 6) * ((math.pi / math.sqrt(2)) ** 2)  # ≈ 1.912e9 J

# Energía del electrón desde el cubo
E_e_cubo_J = BETA_CUADRADO * DELTA * E_P_marco_J
E_e_cubo_MeV = E_e_cubo_J / MeV_to_J

# Experimental
E_e_exp_MeV = 0.5109989461

print("=" * 70)
print("TEST DE FRECUENCIA DE MATERIA - VERSIÓN CORRECTA")
print("=" * 70)

print(f"\n🔬 Energía de Planck (desde cubo):")
print(f"   E_P = 27^6 × (π/√2)² = {E_P_marco_J:.4e} J")

print(f"\n🔬 Energía del electrón DESDE EL CUBO:")
print(f"   β² = {BETA_CUADRADO:.10f}")
print(f"   δ = {DELTA:.10f}")
print(f"   E_e = β²·δ·E_P = {E_e_cubo_MeV:.6f} MeV")
print(f"   m_e c² experimental = {E_e_exp_MeV:.6f} MeV")

error = abs(E_e_cubo_MeV - E_e_exp_MeV) / E_e_exp_MeV
print(f"\n   Error: {error * 100:.4f}%")

# Frecuencia de la materia desde el cubo
f_materia = E_e_cubo_J / h
print(f"\n📡 Frecuencia de la materia: f = E_e / h = {f_materia:.4e} Hz")

print("\n" + "-" * 70)
print("ESCALAS ARMÓNICAS (f_materia / 27^n)")
print("-" * 70)

for n in range(10, 16):
    divisor = 27 ** n
    f_armonica = f_materia / divisor
    
    rango = "—"
    if 30 <= f_armonica <= 100:
        rango = "✅ GAMMA"
    elif 0.5 <= f_armonica <= 4:
        rango = "✅ DELTA"
    elif 20 <= f_armonica <= 20000:
        rango = "✅ AUDIBLE"
    elif f_armonica < 0.1:
        rango = "🌊 INFRABAJAS"
    
    print(f"  n={n:2d}  | 27^{n:2d} = {divisor:.2e} | {f_armonica:.4e} Hz | {rango}")

print("\n" + "-" * 70)
print("PREDICCIONES CLAVE")
print("-" * 70)

f_audible = f_materia / (27 ** 12)
f_gamma = f_materia / (27 ** 13)
f_delta = f_materia / (27 ** 14)

print(f"\n  f_materia / 27^12 = {f_audible:.2f} Hz (Audible)")
print(f"  f_materia / 27^13 = {f_gamma:.2f} Hz (Gamma)")
print(f"  f_materia / 27^14 = {f_delta:.2f} Hz (Delta)")

gamma_ok = 30 <= f_gamma <= 100
delta_ok = 0.5 <= f_delta <= 4
audible_ok = 20 <= f_audible <= 20000

print("\n" + "-" * 70)
print("VERIFICACIÓN")
print("-" * 70)
print(f"  Gamma (30-100 Hz): {f_gamma:.2f} Hz → {'✅ DENTRO' if gamma_ok else '❌ FUERA'}")
print(f"  Delta (0.5-4 Hz):  {f_delta:.2f} Hz → {'✅ DENTRO' if delta_ok else '❌ FUERA'}")
print(f"  Audible (20-20k):  {f_audible:.2f} Hz → {'✅ DENTRO' if audible_ok else '❌ FUERA'}")

print("\n" + "=" * 70)
print("CONCLUSIÓN")
print("=" * 70)

if gamma_ok and delta_ok and audible_ok and error < 0.02716:
    print("""
✅ HIPÓTESIS CONFIRMADA

   La masa del electrón proviene de:
   E_e = β² · δ · E_P
   donde E_P = 27^6 × (π/√2)² es la energía de Planck derivada del cubo.

   Error vs experimental: {:.4f}% (dentro de ε = 2.716%)

   La frecuencia de la materia es:
   f_materia = E_e / h = {:.4e} Hz

   Sus armónicas (dividiendo por potencias de 27) producen
   las frecuencias biológicas del observador:

   • Gamma: {:.2f} Hz  ← integración consciente
   • Audible: {:.2f} Hz ← rango del oído
   • Delta: {:.2f} Hz ← sueño profundo

   La materia vibra a {:.2e} Hz.
   Tú vibras en armonía a {:.2f} Hz (Gamma).
""".format(error*100, f_materia, f_gamma, f_audible, f_delta, f_materia, f_gamma))
else:
    print("❌ Hipótesis NO confirmada (alguna verificación falló)")

# Test para pytest
def test_frecuencia_materia_cubo():
    E_e_cubo_MeV = (BETA_CUADRADO * DELTA * E_P_marco_J) / MeV_to_J
    error = abs(E_e_cubo_MeV - 0.5109989461) / 0.5109989461
    assert error < 0.02716, f"Error {error*100:.2f}% > ε"
    
    f_materia = E_e_cubo_MeV * MeV_to_J / h
    f_gamma = f_materia / (27 ** 13)
    assert 30 <= f_gamma <= 100, f"Gamma: {f_gamma} Hz"
    f_audible = f_materia / (27 ** 12)
    assert 20 <= f_audible <= 20000, f"Audible: {f_audible} Hz"
    f_delta = f_materia / (27 ** 14)
    assert 0.5 <= f_delta <= 4, f"Delta: {f_delta} Hz"

if __name__ == "__main__":
    test_frecuencia_materia_cubo()
    print("\n✅ test_frecuencia_materia_cubo() passed")
