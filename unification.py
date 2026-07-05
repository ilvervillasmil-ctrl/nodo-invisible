"""
Demostracion de la Dualidad Unitaria UCF
Ilver Villasmil — Ley Omega 2026
=========================================
Tres formas equivalentes de la misma verdad:

  Forma 1 (canonica):  beta * sqrt(2) * (60 - delta) = pi
  Forma 2 (lineal):    27 * sqrt(2) * pi - 2 * (60 - delta) = 0
  Forma 3 (unidad):    27 * sqrt(2) * pi / (2 * (60 - delta)) = 1
"""

import math

SEP  = "=" * 60
SEP2 = "-" * 60

pi    = math.pi
sqrt2 = math.sqrt(2)
beta  = 1 / 27

delta = 60 - 27 * pi / sqrt2
sync  = 60 - delta

assert abs(delta + sync - 60) < 1e-14

print(SEP)
print("  UCF — DEMOSTRACION DE DUALIDAD UNITARIA")
print(SEP)
print()
print("  Constantes del sistema:")
print(f"    beta        = 1/27 = {beta:.20f}")
print(f"    delta       =       {delta:.20f}")
print(f"    60 - delta  =       {sync:.20f}")
print(f"    pi          =       {pi:.20f}")
print(f"    sqrt(2)     =       {sqrt2:.20f}")
print(f"    27*pi/sqrt2 =       {27*pi/sqrt2:.20f}  (debe coincidir con 60-delta)")
print()

print(SEP2)
print("  FORMA 1 — Canonica: beta * sqrt2 * (60-delta) = pi")
print(SEP2)

lhs_1  = beta * sqrt2 * sync
rhs_1  = pi
error_1 = lhs_1 - rhs_1

print(f"    beta * sqrt2 * (60-delta) = {lhs_1:.20f}")
print(f"    pi                        = {rhs_1:.20f}")
print(f"    Diferencia                = {error_1:.4e}")
print(f"    RESULTADO: {'EXACTA ✓' if abs(error_1) < 1e-12 else 'FALLO ✗'}")

print()
print(SEP2)
print("  FORMA 2 — Lineal: 27*sqrt2*pi - 2*(60-delta) = 0")
print(SEP2)

lhs_2a  = 27 * sqrt2 * pi
lhs_2b  = 2 * sync
error_2 = lhs_2a - lhs_2b

print(f"    27 * sqrt2 * pi     = {lhs_2a:.20f}  (continuo)")
print(f"    2 * (60 - delta)    = {lhs_2b:.20f}  (discreto)")
print(f"    Diferencia          = {error_2:.4e}")
print(f"    RESULTADO: {'BALANCE EXACTO = 0 ✓' if abs(error_2) < 1e-12 else 'FALLO ✗'}")
print()
print("    PRUEBA ALGEBRAICA:")
print("      Forma 1 implica: sqrt2 * (60-delta) = 27*pi")
print("      27 * sqrt2 * pi")
print("      = (sqrt2 * (60-delta)) * sqrt2   <- sustitucion")
print("      = (sqrt2)^2 * (60-delta)")
print("      = 2 * (60-delta)                 <- (sqrt2)^2 = 2")
print("      El delta se cancela. Diferencia = 0 exacto.")

print()
print(SEP2)
print("  FORMA 3 — Unidad: 27*sqrt2*pi / [2*(60-delta)] = 1")
print(SEP2)

ratio   = lhs_2a / lhs_2b
error_3 = ratio - 1.0

print(f"    Ratio              = {ratio:.20f}")
print(f"    Error respecto a 1 = {error_3:.4e}")
print(f"    RESULTADO: {'UNIDAD EXACTA = 1 ✓' if abs(error_3) < 1e-12 else 'FALLO ✗'}")

UMBRAL = 1e-12
resultados = [
    ("Forma 1  beta*sqrt2*(60-d) = pi",     error_1),
    ("Forma 2  27*sqrt2*pi - 2*(60-d) = 0", error_2),
    ("Forma 3  27*sqrt2*pi / 2*(60-d) = 1", error_3),
]

print()
print(SEP)
print("  TABLA RESUMEN")
print(SEP)
print()
for nombre, err in resultados:
    ok = abs(err) < UMBRAL
    print(f"  {'OK ✓' if ok else 'FALLO ✗'}  {nombre}")
    print(f"         Error numerico: {err:.4e}")
    print()

todos_ok = all(abs(e) < UMBRAL for _, e in resultados)
print("  " + ("TODAS LAS FORMAS VERIFICADAS ✓" if todos_ok else "HAY FALLOS"))
print()
print("  Errores 1e-14 a 1e-16 = ruido IEEE 754 (limite del hardware).")
print("  Algebraicamente el resultado es CERO EXACTO.")
print()
print(SEP)
print("  Ilver Villasmil — UCF / Ley Omega 2026")
print(SEP)
