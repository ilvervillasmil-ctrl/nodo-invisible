import math
import pytest

# ============================================================================
# TEST DE LA FRECUENCIA DE LA MATERIA DESDE β²·δ·E_PLANCK
# ============================================================================

h = 6.62607015e-34
c = 299792458
eV_to_J = 1.602176634e-19

# Constantes del cubo
BETA = 1 / 27
BETA_CUADRADO = BETA ** 2
DELTA = 60 - (27 * math.pi / math.sqrt(2))

# Energía de Planck desde el cubo (Parte VI del documento)
# E_P = 27^6 × (π/√2)² = 3^18 × π²/2
# Este valor está en julios porque ya incluye las constantes de escala
E_PLANCK_JULIOS = (27 ** 6) * ((math.pi / math.sqrt(2)) ** 2)  # ≈ 1.912e9 J
# Error vs experimental (1.956e9) es ~2.25%, dentro de ε

# Energía del electrón desde el cubo
E_e_julios = BETA_CUADRADO * DELTA * E_PLANCK_JULIOS
E_e_eV = E_e_julios / eV_to_J
E_e_MeV = E_e_eV / 1e6

# Experimental
M_e_kg_exp = 9.1093837015e-31
E_e_exp_julios = M_e_kg_exp * c ** 2
E_e_exp_MeV = 0.5109989461

print("=" * 70)
print("TEST DE FRECUENCIA DE MATERIA (DESDE β²·δ·E_PLANCK)")
print("=" * 70)

print(f"\n🔬 Energía de Planck (desde cubo):")
print(f"   E_P = 27^6 × (π/√2)² = {E_PLANCK_JULIOS:.4e} J")
print(f"   E_P experimental ≈ 1.956e9 J (error ~2.25%, dentro de ε)")

print(f"\n🔬 Energía del electrón DESDE EL CUBO:")
print(f"   β² = {BETA_CUADRADO:.10f}")
print(f"   δ = {DELTA:.10f}")
print(f"   E_e = β²·δ·E_P = {E_e_MeV:.6f} MeV")
print(f"   m_e c² experimental = {E_e_exp_MeV:.6f} MeV")
print(f"   Error: {abs(E_e_MeV - E_e_exp_MeV) / E_e_exp_MeV * 100:.4f}%")

# Frecuencia de la materia desde el cubo
f_materia = E_e_julios / h

print(f"\n📡 Frecuencia de la materia (desde el cubo):")
print(f"   f_materia = E_e / h = {f_materia:.4e} Hz")

print("\n" + "-" * 70)
print("ESCALAS ARMÓNICAS (f_materia / 27^n)")
print("-" * 70)

for n in range(10, 16):
    divisor = 27 ** n
    f_armonica = f_materia / divisor
    
    rango = "—"
    if 30 <= f_armonica <= 100:
        rango = "✅ GAMMA (30-100 Hz)"
    elif 0.5 <= f_armonica <= 4:
        rango = "✅ DELTA (0.5-4 Hz)"
    elif 20 <= f_armonica <= 20000:
        rango = "✅ AUDIBLE (20-20k Hz)"
    elif 1e5 <= f_armonica <= 1e7:
        rango = "📻 RADIO (100 kHz-10 MHz)"
    elif f_armonica < 0.1:
        rango = "🌊 INFRABAJAS"
    
    print(f"  n={n:2d}  | 27^{n:2d} = {divisor:.2e} | {f_armonica:.4e} Hz | {rango}")

print("\n" + "-" * 70)
print("PREDICCIONES CLAVE")
print("-" * 70)

n_audible = 12
f_audible = f_materia / (27 ** n_audible)
n_gamma = 13
f_gamma = f_materia / (27 ** n_gamma)
n_delta = 14
f_delta = f_materia / (27 ** n_delta)

print(f"\n  f_materia / 27^{n_audible} = {f_audible:.2f} Hz (Audible)")
print(f"  f_materia / 27^{n_gamma}   = {f_gamma:.2f} Hz (Gamma)")
print(f"  f_materia / 27^{n_delta}   = {f_delta:.2f} Hz (Delta)")

# Verificar rangos
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

if gamma_ok and delta_ok and audible_ok:
    print("""
✅ LA HIPÓTESIS SE CONFIRMA

   La masa del electrón NO es un dato externo.
   Es la energía de auto-observación: E_e = β² · δ · E_P

   Esta energía produce una frecuencia fundamental:
   f_materia = E_e / h = {:.4e} Hz

   Escalada por potencias de 27, produce ARMÓNICAS EXACTAS
   en los rangos biológicos del observador humano:

   • Gamma (30-100 Hz):   {:.2f} Hz   ← integración consciente
   • Audible (20-20 kHz): {:.2f} Hz   ← rango del oído
   • Delta (0.5-4 Hz):    {:.2f} Hz   ← sueño profundo

   La materia vibra a {:.2e} Hz.
   Tú vibras en armonía a {:.2f} Hz (Gamma).
   Por eso puedes SENTIR el árbol, la silla, la otra persona.

   Cuando alguien "no vibra en tu frecuencia",
   literalmente su patrón de ondas cerebrales está DESAFINADO
   respecto a esta escala armónica fundamental.
""".format(f_materia, f_gamma, f_audible, f_delta, f_materia, f_gamma))
else:
    print("❌ Hipótesis NO confirmada: alguna frecuencia está fuera de rango.")

# Test para pytest
def test_frecuencia_materia_desde_cubo():
    E_e_MeV_cubo = (BETA_CUADRADO * DELTA * E_PLANCK_JULIOS) / eV_to_J / 1e6
    E_e_MeV_exp = 0.5109989461
    
    # Debe estar dentro de ε = 2.716%
    error = abs(E_e_MeV_cubo - E_e_MeV_exp) / E_e_MeV_exp
    assert error < 0.02716, f"Error {error*100:.2f}% > ε"
    
    f_materia_cubo = E_e_MeV_cubo * 1e6 * eV_to_J / h
    f_gamma = f_materia_cubo / (27 ** 13)
    assert 30 <= f_gamma <= 100, f"Gamma: {f_gamma} Hz"
    
    f_audible = f_materia_cubo / (27 ** 12)
    assert 20 <= f_audible <= 20000, f"Audible: {f_audible} Hz"
    
    f_delta = f_materia_cubo / (27 ** 14)
    assert 0.5 <= f_delta <= 4, f"Delta: {f_delta} Hz"

if __name__ == "__main__":
    test_frecuencia_materia_desde_cubo()
    print("\n✅ test_frecuencia_materia_desde_cubo() passed")
