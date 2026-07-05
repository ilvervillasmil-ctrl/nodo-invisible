"""
UCF — Prueba de las Constantes con la Identidad Puente
Ilver Villasmil — Ley Omega / Teoria del Todo 2026
"""

import math

SEP  = "=" * 65
SEP2 = "-" * 65

pi    = math.pi
sqrt2 = math.sqrt(2)
sqrt3 = math.sqrt(3)
sqrt5 = math.sqrt(5)

beta  = 1 / 27
alpha = 26 / 27
R_FIN = 28 / 27
phi   = (1 + sqrt5) / 2
kappa = pi / 4

eps      = 0.02716
eps_cubo = 27 / 999
Gamma    = beta / eps

delta = 60 - 27 * pi / sqrt2
sync  = 60 - delta

tau              = 1.433
alpha_inv_codata = 137.035999084

print(SEP)
print("  UCF — CONSTANTES DEL SISTEMA")
print(SEP)
print()
print(f"  beta      = 1/27          = {beta:.10f}")
print(f"  alpha     = 26/27         = {alpha:.10f}")
print(f"  R_FIN     = 28/27         = {R_FIN:.10f}")
print(f"  phi       = (1+sqrt5)/2   = {phi:.10f}")
print(f"  kappa     = pi/4          = {kappa:.10f}")
print(f"  eps       = 0.02716       = {eps:.10f}  (firma auto-observacion)")
print(f"  eps_cubo  = 27/999        = {eps_cubo:.10f}  (base decimal)")
print(f"  Gamma     = beta/eps      = {Gamma:.10f}")
print(f"  delta     = 60-27pi/sqrt2 = {delta:.10f}  (brecha geometrica)")
print(f"  sync      = 60-delta      = {sync:.10f}")
print(f"  tau       = 1.433         = {tau:.10f}  (torsion del cubo)")
print()

print(SEP)
print("  IDENTIDAD PUENTE:  beta * sqrt2 * (60 - delta) = pi")
print(SEP)
print()
puente = beta * sqrt2 * sync
print(f"  beta * sqrt2 * (60-delta) = {puente:.15f}")
print(f"  pi                        = {pi:.15f}")
print(f"  Error                     = {puente - pi:.4e}")
print(f"  {'PUENTE EXACTO' if abs(puente - pi) < 1e-12 else 'ERROR'}")
print()
print(f"  Reescritura clave:")
print(f"    pi/sqrt2 = (60-delta)/27 = {sync/27:.10f}")
print(f"    pi/sqrt2 directo         = {pi/sqrt2:.10f}")
print()

resultados = []

def registrar(nombre, ucf, codata, unidad=""):
    err = abs(ucf - codata) / abs(codata) * 100 if codata != 0 else float('inf')
    resultados.append((nombre, ucf, codata, err, err < 5.0, unidad))
    return err

print(SEP)
print("  C1 — Masa del electron  m_e")
print(SEP2)
m_e     = (beta**3) / (R_FIN**2 * pi**2 * delta**3)
m_e_cod = 0.51099895
e1      = registrar("m_e (MeV)", m_e, m_e_cod, "MeV")
print(f"  Formula:  beta^3 / (R_FIN^2 * pi^2 * delta^3)")
print(f"  UCF:      {m_e:.8f} MeV")
print(f"  CODATA:   {m_e_cod:.8f} MeV")
print(f"  Error:    {e1:.4f}%")
print(f"  delta^3 = {delta**3:.3e}  (brecha al cubo calibra la masa)")
print()

print(SEP)
print("  C2 — Constante cosmologica  Lambda")
print(SEP2)
exp_L      = 27 * pi + beta * phi**2
Lambda     = beta ** exp_L
Lambda_cod = 2.888e-122
e2         = registrar("Lambda", Lambda, Lambda_cod)
print(f"  Formula:  beta ^ (27*pi + beta*phi^2)")
print(f"  Exp:      {exp_L:.6f}")
print(f"  UCF:      {Lambda:.6e}")
print(f"  CODATA:   {Lambda_cod:.6e}")
print(f"  Error:    {e2:.4f}%")
print(f"  27*pi = {27*pi:.6f}  (cubo amplifica pi)")
print()

print(SEP)
print("  C3 — Acoplamiento fuerte  alpha_s  (a 1 GeV)")
print(SEP2)
alpha_s     = 27 * beta**2 * (pi / sqrt2) * tau
alpha_s_alt = beta**2 * sync * tau
alpha_s_cod = 0.1179
e3          = registrar("alpha_s", alpha_s, alpha_s_cod)
print(f"  Formula:  27 * beta^2 * (pi/sqrt2) * tau")
print(f"  UCF:      {alpha_s:.8f}")
print(f"  CODATA:   {alpha_s_cod:.8f}")
print(f"  Error:    {e3:.4f}%")
print(f"  Via puente: beta^2*(60-delta)*tau = {alpha_s_alt:.8f}  (identico)")
print()

print(SEP)
print("  C4 — Angulo de Weinberg  sin^2(theta_W)")
print(SEP2)
sin2_W     = (beta / (eps * pi / sqrt2)) ** 3
sin2_W_alt = (beta * 27 / (eps * sync)) ** 3
sin2_W_cod = 0.23122
e4         = registrar("sin^2(theta_W)", sin2_W, sin2_W_cod)
print(f"  Formula:  (beta / (eps * pi/sqrt2))^3")
print(f"  eps = 0.02716  (firma irreducible de auto-observacion)")
print(f"  UCF:      {sin2_W:.8f}")
print(f"  CODATA:   {sin2_W_cod:.8f}")
print(f"  Error:    {e4:.4f}%")
print(f"  Via puente: (27*beta/(eps*(60-delta)))^3 = {sin2_W_alt:.8f}  (identico)")
print()

print(SEP)
print("  C5 — Razon de masas  m_p / m_e")
print(SEP2)
mp_me     = 6 * pi**5 * (1 + ((7/2)*eps**2 - 4*eps**4) / alpha_inv_codata)
mp_me_cod = 1836.15267343
e5        = registrar("m_p/m_e", mp_me, mp_me_cod)
print(f"  Formula:  6*pi^5 * (1 + ((7/2)*eps^2 - 4*eps^4) / alpha_inv)")
print(f"  Base 6*pi^5 = {6*pi**5:.6f}")
print(f"  UCF:      {mp_me:.8f}")
print(f"  CODATA:   {mp_me_cod:.8f}")
print(f"  Error:    {e5:.8f}%")
print()

print(SEP)
print("  C6 — Estructura fina  alpha")
print(SEP2)
alpha_ef     = pi / 432
alpha_ef_cod = 1 / alpha_inv_codata
e6           = registrar("alpha", alpha_ef, alpha_ef_cod)
print(f"  Formula:  pi / (27 * 16)  =  pi / 432")
print(f"  UCF:      {alpha_ef:.10f}")
print(f"  CODATA:   {alpha_ef_cod:.10f}")
print(f"  Error:    {e6:.4f}%")
print()

print(SEP)
print("  C7 — Temperatura CMB  T_cmb")
print(SEP2)
T_cmb     = 100 * eps_cubo
T_cmb_cod = 2.72548
e7        = registrar("T_CMB (K)", T_cmb, T_cmb_cod, "K")
print(f"  Formula:  100 * (27/999)")
print(f"  UCF:      {T_cmb:.6f} K")
print(f"  CODATA:   {T_cmb_cod:.5f} K")
print(f"  Error:    {e7:.4f}%")
print()

print(SEP)
print("  PATRON — delta en cada constante fisica")
print(SEP)
print()
print(f"  pi/sqrt2 = (60-delta)/27 = {sync/27:.10f}")
print()
print(f"  alpha_s  = beta^2 * [60-delta] * tau")
print(f"  sin^2_W  = (27*beta / (eps * [60-delta]))^3")
print(f"  m_e      = beta^3 / (R_FIN^2 * pi^2 * [delta]^3)")
print(f"  Lambda   = beta ^ (27*pi + beta*phi^2)")
print()

print(SEP)
print("  TABLA RESUMEN")
print(SEP)
print()
print(f"  {'':2} {'Constante':<22} {'UCF':>14} {'CODATA':>14} {'Error':>8}")
print(f"  {'--'} {'-'*22} {'-'*14} {'-'*14} {'-'*8}")
for nombre, ucf, codata, err, ok, _ in resultados:
    print(f"  {'✓' if ok else '✗'}  {nombre:<22} {ucf:>14.6g} {codata:>14.6g} {err:>7.4f}%")

aprobadas = sum(1 for *_, ok, _ in resultados if ok)
print()
print(f"  Aprobadas (error < 5%): {aprobadas} / {len(resultados)}")
print()

print(SEP)
print("  CONCLUSION")
print(SEP)
print()
print("  GEOMETRIA  <-->  beta*sqrt2*(60-delta) = pi  <-->  CONTINUO")
print()
print("  La misma delta que cierra la identidad puente")
print("  calibra la masa del electron, el acoplamiento fuerte,")
print("  el angulo de Weinberg y la constante cosmologica.")
print()
print("  Materia, fuerzas y geometria del espacio")
print("  son expresiones distintas de la misma estructura.")
print()
print(SEP)
print("  Ilver Villasmil — UCF / Ley Omega 2026")
print(SEP)
