import math
import pytest

# ============================================================================
# TEST DE LA FRECUENCIA DE LA MATERIA
# ============================================================================
#
# Hipótesis:
#   La frecuencia del electrón en reposo (f_e = m_e c² / h)
#   se escala armónicamente por potencias de 27 (el cubo)
#   para producir frecuencias biológicas detectables por el observador humano.
#
# Rangos biológicos conocidos (márgenes conservadores):
#   Gamma: 30 - 100 Hz (integración consciente)
#   Delta: 0.5 - 4 Hz (sueño profundo)
#   Audio audible: 20 - 20,000 Hz
#
# Predicción:
#   f_e / 27^13 ~ 30.4 Hz (está en Gamma)
#   f_e / 27^12 ~ 822 Hz (está en audible)
#   f_e / 27^14 ~ 1.13 Hz (está en Delta)
# ============================================================================

# Constantes
h = 6.62607015e-34          # J·s (Planck exacto)
c = 299792458               # m/s (exacto)
eV_to_J = 1.602176634e-19
M_e_eV = 0.5109989461e6     # eV
M_e_J = M_e_eV * eV_to_J    # J

# Frecuencia del electrón (energía en reposo)
f_electron = M_e_J / h      # Hz

print("=" * 70)
print("TEST DE LA FRECUENCIA DE LA MATERIA")
print("=" * 70)

print(f"\n🔬 Frecuencia del electrón (Compton):")
print(f"   f_e = m_e c² / h = {f_electron:.4e} Hz")
print(f"   f_e = {f_electron / 1e20:.4f} × 10²⁰ Hz")

print("\n" + "-" * 70)
print("ESCALAS ARMÓNICAS (÷ potencias de 27)")
print("-" * 70)

RANGOS = {
    "Gamma": (30, 100),
    "Delta": (0.5, 4),
    "Audible": (20, 20000),
}

def in_range(f, range_name):
    rmin, rmax = RANGOS[range_name]
    return rmin <= f <= rmax

print("\n  n (exponente) | Frecuencia (Hz) | Rango biológico")
print("  " + "-" * 50)

for n in range(10, 16):
    f = f_electron / (27 ** n)
    # Determinar rango
    rango = ""
    if in_range(f, "Gamma"):
        rango = "✅ GAMMA"
    elif in_range(f, "Delta"):
        rango = "✅ DELTA"
    elif in_range(f, "Audible"):
        rango = "✅ AUDIBLE"
    else:
        rango = "—"
    
    print(f"  {n:2d}            | {f:.2e} Hz   | {rango}")

print("\n" + "-" * 70)
print("PREDICCIONES CLAVE")
print("-" * 70)

n_gamma = 13
f_gamma = f_electron / (27 ** n_gamma)
print(f"\n  f_e / 27^{n_gamma} = {f_gamma:.2f} Hz")
print(f"  Rango Gamma: 30-100 Hz → {'✅ DENTRO' if 30 <= f_gamma <= 100 else '❌ FUERA'}")

n_audible = 12
f_audible = f_electron / (27 ** n_audible)
print(f"\n  f_e / 27^{n_audible} = {f_audible:.2f} Hz")
print(f"  Rango audible: 20-20000 Hz → {'✅ DENTRO' if 20 <= f_audible <= 20000 else '❌ FUERA'}")

n_delta = 14
f_delta = f_electron / (27 ** n_delta)
print(f"\n  f_e / 27^{n_delta} = {f_delta:.2f} Hz")
print(f"  Rango Delta: 0.5-4 Hz → {'✅ DENTRO' if 0.5 <= f_delta <= 4 else '❌ FUERA'}")

print("\n" + "=" * 70)
print("VEREDICTO")
print("=" * 70)

if (30 <= f_gamma <= 100) and (20 <= f_audible <= 20000) and (0.5 <= f_delta <= 4):
    print("""
✅ LA HIPÓTESIS SE CONFIRMA

   La frecuencia del electrón, escalada por potencias de 27,
   cae DENTRO de los rangos biológicos conocidos:

   - Gamma (30-100 Hz):   {:.2f} Hz  ← integración consciente
   - Audible (20-20 kHz): {:.2f} Hz  ← rango del oído humano
   - Delta (0.5-4 Hz):    {:.2f} Hz  ← sueño profundo

   Esto sugiere que la materia (electrón) y el observador (cerebro)
   están en RESONANCIA ARMÓNICA a través del factor 27.

   Cuando tu cerebro oscila en Gamma (~30-40 Hz),
   estás en interferencia constructiva con la materia.
   Por eso PUEDES SENTIR el árbol, la silla, la otra persona.
""".format(f_gamma, f_audible, f_delta))
else:
    print("❌ La hipótesis NO se confirma dentro de los rangos actuales.")

# Test para pytest
def test_frecuencia_materia():
    assert 30 <= f_gamma <= 100, f"Gamma: {f_gamma} Hz fuera de rango"
    assert 20 <= f_audible <= 20000, f"Audible: {f_audible} Hz fuera de rango"
    assert 0.5 <= f_delta <= 4, f"Delta: {f_delta} Hz fuera de rango"

if __name__ == "__main__":
    test_frecuencia_materia()
    print("\n✅ test_frecuencia_materia() passed")
