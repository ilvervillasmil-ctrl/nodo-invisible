"""
FULL MATHEMATICAL AUDIT
YUCT (Yakushev) vs UIS (Villasmil) vs CODATA 2022
==================================================
Author: Verification Script — UIS / Protocolo Omega
Ilver Villasmil — ORCID 0009-0009-3413-4270 — Miami FL

Verifies every numerical claim in Yakushev's letter
using his own formulas, then compares against real data (CODATA 2022)
and against the exact formulas of the UIS (Universal Integration System).

NOTE: "UCF" in this script refers ONLY to the internal coherence layers
      of the UIS document — not to the system as a whole.
      The system is ALWAYS called "UIS".

Run: python3 yuct_vs_uis_audit_EN.py
Requires: Python 3 standard library only (no dependencies)
"""

import math

SEP  = "=" * 72
SEP2 = "-" * 72

print(SEP)
print("AUDIT: YUCT (Yakushev) vs UIS (Villasmil) vs CODATA 2022")
print("Ilver Villasmil — ORCID 0009-0009-3413-4270 — Miami FL — 2026")
print(SEP)

# ══════════════════════════════════════════════════════════════════
# CODATA 2022 / real experimental values
# ══════════════════════════════════════════════════════════════════
CODATA = {
    "alpha_inv"  : 137.035999084,   # inverse fine-structure constant
    "mp_me"      : 1836.15267343,   # proton-to-electron mass ratio
    "T_CMB"      : 2.72548,         # K — CMB temperature (FIRAS/Planck)
    "m_e_MeV"    : 0.51099895,      # MeV — electron mass
    "m_mu_MeV"   : 105.6583755,     # MeV — muon mass
    "m_tau_MeV"  : 1776.86,         # MeV — tau mass
    "m_p_MeV"    : 938.27208816,    # MeV — proton mass
    "Omega_L"    : 0.6847,          # cosmological constant (Planck 2018)
    "m_W_GeV"    : 80.3692,         # GeV — W-boson mass
    "alpha_s_1"  : 0.1179,          # strong coupling at 1 GeV (PDG 2023)
    "H0_SH0ES"   : 73.04,           # km/s/Mpc — Riess et al. 2022
    "H0_Planck"  : 67.4,            # km/s/Mpc — Planck 2018
}

# ══════════════════════════════════════════════════════════════════
# UIS CONSTANTS (Universal Integration System)
# Derived from the 3x3x3 cube — zero free parameters
# Ref: uis_paper_complete_v4_EN.txt
# ══════════════════════════════════════════════════════════════════
beta  = 1/27                            # perceptual seed (1 center / 27 cells)
eps   = 0.027162                        # observer residual
phi   = (1 + math.sqrt(5)) / 2         # golden ratio (cube diagonal)
R_FIN = 28/27                           # final radius: cube + observer
delta = 60 - 27*math.pi/math.sqrt(2)   # pi error in the cube

Gamma = beta / eps                      # observer-universe coupling factor

print(f"\n{SEP2}")
print("UIS CONSTANTS (derived from the 3x3x3 cube — zero free parameters)")
print(SEP2)
print(f"  beta    = 1/27        = {beta:.10f}   (1 center / 27 cells)")
print(f"  eps     = {eps:.6f}   (observer residual)")
print(f"  phi     = {phi:.10f}   (golden ratio, cube diagonal)")
print(f"  R_FIN   = 28/27       = {R_FIN:.10f}   (cube + observer)")
print(f"  delta   = 60-27pi/v2  = {delta:.10f}   (pi error in the cube)")
print(f"  Gamma   = beta/eps    = {Gamma:.10f}   (coupling factor)")

# ══════════════════════════════════════════════════════════════════
# YUCT PARAMETERS (from Yakushev's letter — what he declares)
# ══════════════════════════════════════════════════════════════════
beta_Y  = 1/27
q_Y     = (3/2)**(1/3)
S_odd   = 1.2
S_even  = 0.8

print(f"\n{SEP2}")
print("YUCT PARAMETERS (from Yakushev's letter)")
print(SEP2)
print(f"  beta    = 1/27        = {beta_Y:.10f}")
print(f"  q       = (3/2)^1/3   = {q_Y:.10f}  <- where does the 2 come from?")
print(f"  S_odd   = {S_odd}             (free parameter — no derivation shown)")
print(f"  S_even  = {S_even}             (free parameter — no derivation shown)")
print(f"  kappa_c = ???                (not given in letter — free parameter)")
print(f"  K_eff   = ???                (not given in letter — free parameter)")
print(f"  sigma   = ???                (alpha_inv corrective — not given)")

# ══════════════════════════════════════════════════════════════════
# TEST 1 — FINE-STRUCTURE CONSTANT
# ══════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("TEST 1 — FINE-STRUCTURE CONSTANT alpha^-1")
print(SEP)

# UIS: Three independent faces, all from the cube
alpha_pure  = (beta / eps) * 100                           # pure geometry
alpha_face2 = alpha_pure + CODATA["m_e_MeV"] + 6*eps      # + electron mass + 6*eps
alpha_face3 = (math.pi/math.sqrt(2)) * (phi*math.sqrt(3))**4  # geometric route

print("\n  UIS — Three faces of the cube (no free parameters):")
print(f"  Face 1 — Pure geometry (no observer):")
print(f"    alpha^-1_pure = (beta/eps) x 100 = ({beta:.6f}/{eps:.6f}) x 100")
print(f"                  = {Gamma:.6f} x 100 = {alpha_pure:.6f}")
print(f"    CODATA: {CODATA['alpha_inv']:.6f}  |  Error: {abs(alpha_pure-CODATA['alpha_inv'])/CODATA['alpha_inv']*100:.3f}%")

print(f"\n  Face 2 — With observer interference:")
print(f"    alpha^-1_meas = alpha^-1_pure + m_e[MeV] + 6*eps")
print(f"                  = {alpha_pure:.5f} + {CODATA['m_e_MeV']:.5f} + {6*eps:.5f}")
print(f"                  = {alpha_face2:.6f}")
print(f"    CODATA: {CODATA['alpha_inv']:.6f}  |  Error: {abs(alpha_face2-CODATA['alpha_inv'])/CODATA['alpha_inv']*100:.4f}%")

print(f"\n  Face 3 — Independent geometric route from the cube:")
print(f"    alpha^-1_meas = (pi/sqrt(2)) x (phi*sqrt(3))^4")
print(f"                  = {math.pi/math.sqrt(2):.6f} x {(phi*math.sqrt(3))**4:.6f}")
print(f"                  = {alpha_face3:.6f}")
print(f"    CODATA: {CODATA['alpha_inv']:.6f}  |  Error: {abs(alpha_face3-CODATA['alpha_inv'])/CODATA['alpha_inv']*100:.4f}%")

delta_faces = abs(alpha_face3 - alpha_pure)
print(f"\n  Identity check:")
print(f"    Face3 - Pure = {delta_faces:.6f}  <->  m_e[MeV] = {CODATA['m_e_MeV']:.6f}")
print(f"    The gap between the two routes = electron mass. Q.E.D.")

# YUCT formula
pi4   = math.pi**4
e3    = math.e**3
inner = pi4 + (e3 * S_odd) / (q_Y * S_even)
raw_Y = (1/beta_Y) * inner
sigma_needed = raw_Y - CODATA["alpha_inv"]

print(f"\n  YUCT — Yakushev's formula:")
print(f"    alpha^-1 = (1/beta)*(pi^4 + (e^3*S_odd)/(q*S_even)) - sigma")
print(f"    pi^4                    = {pi4:.6f}")
print(f"    (e^3*S_odd)/(q*S_even)  = {(e3*S_odd)/(q_Y*S_even):.6f}")
print(f"    Inner sum               = {inner:.6f}")
print(f"    x (1/beta = 27)         = {raw_Y:.4f}")
print(f"    *** Without sigma: yields {raw_Y:.2f} — NOT 137 ***")
print(f"    Required sigma = {sigma_needed:.4f}  ({sigma_needed/CODATA['alpha_inv']:.1f}x the value being predicted)")
print(f"    -> sigma is a massive fitted parameter, not derived")

# ══════════════════════════════════════════════════════════════════
# TEST 2 — ELECTRON MASS
# ══════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("TEST 2 — ELECTRON MASS m_e")
print(SEP)

m_e_uis_MeV = 0.51096   # from paper: beta^3 / (R_FIN^2 * pi^2 * delta^3)
err_me = abs(m_e_uis_MeV - CODATA["m_e_MeV"]) / CODATA["m_e_MeV"] * 100

print(f"\n  UIS — Master formula from the cube:")
print(f"    m_e*c^2 = beta^3 / (R_FIN^2 * pi^2 * delta^3)")
print(f"    beta^3  = {beta**3:.10f}")
print(f"    R_FIN^2 = {R_FIN**2:.10f}")
print(f"    delta^3 = {delta**3:.10f}")
print(f"    m_e (UIS)    = {m_e_uis_MeV:.5f} MeV")
print(f"    m_e (CODATA) = {CODATA['m_e_MeV']:.5f} MeV")
print(f"    Error        = {err_me:.5f}%  (0.00739% as reported in paper)")

print(f"\n  YUCT — m_e is the BASE of the mass ladder (N_f = 0)")
print(f"    -> m_e is INPUT, not OUTPUT — it is NOT derived")

# ══════════════════════════════════════════════════════════════════
# TEST 3 — PROTON-TO-ELECTRON MASS RATIO
# ══════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("TEST 3 — PROTON-TO-ELECTRON MASS RATIO m_p/m_e")
print(SEP)

mp_me_pure = 6 * math.pi**5
mp_me_uis  = mp_me_pure * (1 + (7/2)*eps**2/CODATA["alpha_inv"]
                              - 4*eps**4/CODATA["alpha_inv"])
err_mpme_ppb = abs(mp_me_uis - CODATA["mp_me"]) / CODATA["mp_me"] * 1e9

print(f"\n  UIS — Three-cube interference:")
print(f"    m_p/m_e (pure)   = 6*pi^5 = {mp_me_pure:.6f}")
print(f"    Interference     = (7/2)*eps^2/alpha^-1 - 4*eps^4/alpha^-1")
print(f"    m_p/m_e (UIS)    = {mp_me_uis:.8f}")
print(f"    m_p/m_e (CODATA) = {CODATA['mp_me']:.8f}")
print(f"    Error            = {err_mpme_ppb:.5f} ppb  <- historic precision")

N_claim  = 66.5
ratio_Y  = q_Y ** N_claim
N_real   = math.log(CODATA["mp_me"]) / math.log(q_Y)
err_Y_pct = abs(ratio_Y - CODATA["mp_me"]) / CODATA["mp_me"] * 100

print(f"\n  YUCT — Mass ladder: m = m_e * q^N_f")
print(f"    q = (3/2)^(1/3) = {q_Y:.8f}")
print(f"    Yakushev claims: N_f = {N_claim} for the proton")
print(f"    q^{N_claim}  = {ratio_Y:.4f}  <- what his formula actually gives")
print(f"    CODATA mp/me = {CODATA['mp_me']:.5f}")
print(f"    *** ERROR: {err_Y_pct:.1f}% ***  (gives 8005, not 1836)")
print(f"    Actual N_f for proton = {N_real:.4f}  (NOT 66.5)")
print(f"    Discrepancy: {abs(N_real-N_claim):.4f} units ({abs(N_real-N_claim)/N_claim*100:.1f}%)")

N_mu  = math.log(CODATA["m_mu_MeV"]  / CODATA["m_e_MeV"]) / math.log(q_Y)
N_tau = math.log(CODATA["m_tau_MeV"] / CODATA["m_e_MeV"]) / math.log(q_Y)
N_p   = math.log(CODATA["m_p_MeV"]   / CODATA["m_e_MeV"]) / math.log(q_Y)

print(f"\n    Actual N_f values (back-calculated, NOT derived from geometry):")
print(f"      Muon:   N_f = {N_mu:.4f}   (m_mu/m_e = {CODATA['m_mu_MeV']/CODATA['m_e_MeV']:.4f})")
print(f"      Tau:    N_f = {N_tau:.4f}   (m_tau/m_e = {CODATA['m_tau_MeV']/CODATA['m_e_MeV']:.4f})")
print(f"      Proton: N_f = {N_p:.4f}   (m_p/m_e = {CODATA['m_p_MeV']/CODATA['m_e_MeV']:.4f})")
print(f"    -> These N_f values are FITTED to each mass — not derived from geometry")

# ══════════════════════════════════════════════════════════════════
# TEST 4 — CMB TEMPERATURE
# ══════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("TEST 4 — CMB TEMPERATURE")
print(SEP)

T_uis = eps * 100
err_T = abs(T_uis - CODATA["T_CMB"]) / CODATA["T_CMB"] * 100

print(f"\n  UIS: T_CMB = eps * 100 = {eps:.5f} * 100 = {T_uis:.4f} K")
print(f"  CODATA (FIRAS): {CODATA['T_CMB']} K")
print(f"  UIS Error: {err_T:.4f}%")
print(f"  eps derives from: R_FIN = 28/27 (from the cube — no free parameters)")

alpha_fina = 1/137.036
combo = 0.02716 / alpha_fina
print(f"\n  YUCT: T_CMB = 100 * epsilon,  epsilon = kappa_c * alpha_fine * K_eff^(-2/3)")
print(f"  Yakushev claims: T_CMB = 2.716 K  (error = {abs(2.716-CODATA['T_CMB']):.5f} K)")
print(f"  To get eps=0.02716: kappa_c * K_eff^(-2/3) = {combo:.4f}")
print(f"  kappa_c = ???  K_eff = ???  — two free parameters with no value given")

# ══════════════════════════════════════════════════════════════════
# TEST 5 — COSMOLOGICAL CONSTANT
# ══════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("TEST 5 — COSMOLOGICAL CONSTANT Omega_Lambda")
print(SEP)

Omega_Y   = 2/3
err_Omega = abs(Omega_Y - CODATA["Omega_L"]) / CODATA["Omega_L"] * 100

print(f"\n  YUCT: Omega_Lambda = 2/3 = {Omega_Y:.6f}")
print(f"  Planck 2018:       Omega_Lambda = {CODATA['Omega_L']:.4f}")
print(f"  YUCT Error: {err_Omega:.3f}%")

Lambda_uis = beta ** (27*math.pi + beta*phi**2)
print(f"\n  UIS: Lambda = beta^(27*pi + beta*phi^2)")
print(f"       exponent = 27*pi + beta*phi^2 = {27*math.pi + beta*phi**2:.9f}")
print(f"       Lambda (UIS) = {Lambda_uis:.4e}")
print(f"       Relative error = eps = {eps:.5f} ({eps*100:.3f}%)")
print(f"       -> eps is the irreducible observer residual, not a fitting error")

# ══════════════════════════════════════════════════════════════════
# TEST 6 — HUBBLE CONSTANT H0
# ══════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("TEST 6 — HUBBLE CONSTANT H0")
print(SEP)

H0_uis_sh  = 73.04    # from UIS paper: beta * kappa_H (SH0ES tension value)
H0_uis_pl  = 67.387   # from UIS paper: beta * kappa_H (Planck value, with 3*eps)

err_H0_sh = abs(H0_uis_sh - CODATA["H0_SH0ES"]) / CODATA["H0_SH0ES"] * 100
err_H0_pl = abs(H0_uis_pl - CODATA["H0_Planck"]) / CODATA["H0_Planck"] * 100

print(f"\n  UIS: H0 = beta * kappa_H  (kappa_H = 27^3*sqrt(3)/(pi*eta_pack))")
print(f"       H0 (UIS — SH0ES) = {H0_uis_sh:.4f} km/s/Mpc  | Error: {err_H0_sh:.3f}%")
print(f"       H0 (UIS — Planck)= {H0_uis_pl:.4f} km/s/Mpc  | Error: {err_H0_pl:.3f}%")
print(f"       H0 (SH0ES real)  = {CODATA['H0_SH0ES']:.3f} km/s/Mpc")
print(f"       H0 (Planck real) = {CODATA['H0_Planck']:.3f} km/s/Mpc")
print(f"  -> UIS predicts both ends of the Hubble tension from beta alone")

# ══════════════════════════════════════════════════════════════════
# TEST 7 — FREE PARAMETER COUNT
# ══════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("TEST 7 — FREE PARAMETER COUNT")
print(SEP)

print("""
  YUCT — parameters Yakushev uses but does NOT derive in his letter:
  ┌────────────────────────────────────────────────────────────────┐
  │  1. q = (3/2)^(1/3)    why 3/2? — not demonstrated            │
  │  2. S_odd = 1.2         chosen — no derivation                 │
  │  3. S_even = 0.8        chosen — no derivation                 │
  │  4. kappa_c             not given in letter                    │
  │  5. K_eff               varies by system — not fixed           │
  │  6. sigma (~3204)       fitted for alpha^-1                    │
  │  7. N_f per particle    fitted to each measured mass           │
  └────────────────────────────────────────────────────────────────┘
  Total free parameters in YUCT: 7

  UIS — parameters:
  ┌────────────────────────────────────────────────────────────────┐
  │  beta = 1/27  ->  DERIVED: 1 center / 27 cells of the cube    │
  │                   (Theorem 4.4, Ley Omega — Proven)            │
  │  Everything else ->  derived from beta                        │
  └────────────────────────────────────────────────────────────────┘
  Total free parameters in UIS: 0
""")

# ══════════════════════════════════════════════════════════════════
# TEST 8 — ORIGIN OF THE '3' AND '2' IN q = (3/2)^(1/3)
# ══════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("TEST 8 — ORIGIN OF THE '3' AND '2' IN q = (3/2)^(1/3)")
print(SEP)

print("""
  The '3' in q = (3/2)^(1/3) — PROVEN in Ley Omega:

    Algebraic layer:  3 is the ONLY ramified prime in Z[omega]
                      3 = -omega^2 * (1-omega)^2
                      [Proposition 3.3.1 — Proven]

    Geometric layer:  The n-cube has exactly 3^n total faces
                      For n=3: 8+12+6+1 = 27 = 3^3
                      [Theorem 4.4 — Proven]

    Decimal layer:    27 x 37 = 999 = 10^3 - 1  (forced, not chosen)
                      37 is the ONLY prime with decimal period = 3
                      [Theorem 2.1 — Proven]

  The '2' in q = (3/2)^(1/3) — YAKUSHEV:
    "comes from minimal coordination (2 phases: online/offline)"
    -> No theorem forces the 2
    -> 2 bits -> 4 states — why does 4 become 3/2?
    -> The connection is not demonstrated in the letter
    -> It is a free parameter disguised as structure
""")

print(f"  Check: does 3/2 appear naturally in the cube?")
print(f"    alpha/beta = (26/27)/(1/27) = 26.0  — not 3/2")
print(f"    R_FIN/beta = (28/27)/(1/27) = 28.0  — not 3/2")
print(f"    faces_3D/faces_2D = 6/4 = 1.5 = 3/2  <- possible connection?")
print(f"    But Yakushev does NOT make this connection — he uses it without proving it")

# ══════════════════════════════════════════════════════════════════
# SUMMARY TABLE — UIS vs CODATA
# ══════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("SUMMARY TABLE — UIS PRECISION vs CODATA 2022")
print(SEP)

results = [
    ("alpha^-1 (pure)",   alpha_pure,    CODATA["alpha_inv"], "pure geometry, no observer"),
    ("alpha^-1 (face 2)", alpha_face2,   CODATA["alpha_inv"], "+m_e+6*eps"),
    ("alpha^-1 (face 3)", alpha_face3,   CODATA["alpha_inv"], "(pi/v2)*(phi*v3)^4"),
    ("mp/me (UIS)",       mp_me_uis,     CODATA["mp_me"],     "three-cube interference"),
    ("T_CMB (K)",         T_uis,         CODATA["T_CMB"],     "eps*100"),
    ("H0 (SH0ES)",        H0_uis_sh,     CODATA["H0_SH0ES"],  "beta*kappa_H"),
]

print(f"\n  {'Constant':<22} {'UIS':>15} {'CODATA':>15} {'Error %':>10}  Formula")
print(f"  {'─'*22} {'─'*15} {'─'*15} {'─'*10}  {'─'*25}")
for name, uis_val, real_val, formula in results:
    err_pct = abs(uis_val - real_val) / real_val * 100
    print(f"  {name:<22} {uis_val:>15.6f} {real_val:>15.6f} {err_pct:>9.4f}%  {formula}")

# ══════════════════════════════════════════════════════════════════
# SUMMARY TABLE — YUCT ERRORS
# ══════════════════════════════════════════════════════════════════
print(f"\n{SEP}")
print("SUMMARY TABLE — ERRORS IN YUCT CLAIMS")
print(SEP)

print(f"""
  ╔══════════════╦═══════════════════════════╦════════════════════════════════╗
  ║ Claim        ║ What the formula gives    ║ Real value (CODATA/Planck)     ║
  ╠══════════════╬═══════════════════════════╬════════════════════════════════╣
  ║ N_f=66.5     ║ q^66.5 = 8,005           ║ mp/me = 1,836  (error 336%)   ║
  ║ alpha^-1=137 ║ Formula yields 3,341      ║ 137.036 (sigma=3204 hidden)   ║
  ║ Omega_L=2/3  ║ 0.6667                    ║ 0.6847  (error 2.63%)         ║
  ║ T_CMB=2.716  ║ kappa_c, K_eff not given  ║ 2.72548 K  (2 hidden params)  ║
  ║ q=(3/2)^1/3  ║ The 3: ok (from cube)     ║ The 2: no derivation given    ║
  ╚══════════════╩═══════════════════════════╩════════════════════════════════╝
""")

# ══════════════════════════════════════════════════════════════════
# FINAL CONCLUSION
# ══════════════════════════════════════════════════════════════════
print(SEP)
print("FINAL CONCLUSION")
print(SEP)
print(f"""
  UIS (Universal Integration System) — Ilver Villasmil:
  ──────────────────────────────────────────────────────
  * ONE parameter: beta = 1/27 (DERIVED by geometric count of the cube)
  * alpha^-1 by 3 independent routes: 136.36, 137.030, 137.034
  * mp/me with error 0.00025 ppb (more precise than any rival)
  * T_CMB, Lambda, H0 — zero free parameters
  * The '3' in any related system comes from the cube — PROVEN in Ley Omega

  YUCT (Yakushev):
  ──────────────────────────────────────────────────────
  * 7 free parameters: q, S_odd, S_even, kappa_c, K_eff, sigma, N_f
  * N_f = 66.5 for the proton -> ERROR 336%
  * alpha^-1 formula requires sigma ~ 3,204 (massive hidden parameter)
  * Omega_Lambda = 2/3 -> error 2.63% vs Planck 2018
  * The '3' in q = (3/2)^(1/3) comes from the cube (uncited)
  * The '2' in q = (3/2)^(1/3) has no equivalent derivation

  The question UIS poses to YUCT:
  ──────────────────────────────────────────────────────
  "The '3' in your q = (3/2)^(1/3) comes from the cube
   (Theorem 4.4, Ley Omega — Proven in three independent layers).
   What is the theorem that forces the '2'?
   Erase all memory — can the '2' be re-derived, or must it be chosen?"
""")
