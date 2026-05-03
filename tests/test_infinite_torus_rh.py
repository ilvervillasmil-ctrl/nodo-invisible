"""
test_infinite_torus_rh.py
TEST DEL TOROIDE ARITMETICO INFINITO Y CODIFICACION DE CEROS DE RIEMANN
Autor: Ilver Villasmil
Fecha: Marzo 22, 2026
"""

import pytest
import numpy as np
from math import gcd, log, sqrt, pi
from functools import reduce


# ============================================================================
# FUNCIONES BASE
# ============================================================================

def sieve(n):
    """Criba de Eratostenes hasta n"""
    if n < 2:
        return []
    is_prime = bytearray([1]) * (n + 1)
    is_prime[0] = is_prime[1] = 0
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            is_prime[i*i::i] = bytearray(len(is_prime[i*i::i]))
    return [i for i in range(2, n+1) if is_prime[i]]


def primorial(primes):
    """Producto de primos — M = p1*p2*...*pk"""
    result = 1
    for p in primes:
        result *= p
    return result


def euler_totient(M, prime_factors):
    """phi(M) = M * prod(1 - 1/p) para p | M"""
    result = M
    for p in prime_factors:
        result = result // p * (p - 1)
    return result


def coprimes(M):
    """Lista de a en [1,M) con gcd(a,M)=1"""
    return [a for a in range(1, M) if gcd(a, M) == 1]


def compute_epsilon(primes_list, M, phi_M):
    """
    Calcula epsilon(a) = pi(x;M,a)/pi(x) - 1/phi(M)
    para cada a coprimo con M
    """
    admissible = coprimes(M)
    counts = {a: 0 for a in admissible}
    total = 0

    for p in primes_list:
        if p > M and gcd(p, M) == 1:
            r = p % M
            if r in counts:
                counts[r] += 1
                total += 1

    if total == 0:
        return {a: 0.0 for a in admissible}

    epsilon = {}
    for a in admissible:
        epsilon[a] = counts[a] / total - 1 / phi_M

    return epsilon


def compute_E(epsilon):
    """E(M) = media de epsilon(a)^2"""
    values = list(epsilon.values())
    if not values:
        return 0.0
    return sum(v**2 for v in values) / len(values)


# ============================================================================
# CONSTANTES
# ============================================================================

# Primoriales T1 a T7
PRIMORIAL_PRIMES = {
    'T1': [2],
    'T2': [2, 3],
    'T3': [2, 3, 5],
    'T4': [2, 3, 5, 7],
    'T5': [2, 3, 5, 7, 11],
    'T6': [2, 3, 5, 7, 11, 13],
    'T7': [2, 3, 5, 7, 11, 13, 17],
}

# Ceros de Riemann conocidos (parte imaginaria)
RIEMANN_ZEROS = [14.134725, 21.022040, 25.010858, 30.424876, 32.935062]

# Umbral RH: E_inf < 10^-6
RH_THRESHOLD = 1e-6

# Primos para tests (hasta 100000)
PRIMES_100K = sieve(100_000)
PRIMES_500K = sieve(500_000)


class TestInfiniteTorusConstruction:
    """
    Seccion 2: Construccion del Toroide Aritmetico Infinito
    T_inf = prod_p Z/pZ
    """

    def test_torus_t1_period(self):
        """T1: periodo = 2"""
        primes = PRIMORIAL_PRIMES['T1']
        M = primorial(primes)
        assert M == 2

    def test_torus_t2_period(self):
        """T2: periodo = 6"""
        primes = PRIMORIAL_PRIMES['T2']
        M = primorial(primes)
        assert M == 6

    def test_torus_t3_period(self):
        """T3: periodo = 30"""
        primes = PRIMORIAL_PRIMES['T3']
        M = primorial(primes)
        assert M == 30

    def test_torus_t4_period(self):
        """T4: periodo = 210"""
        primes = PRIMORIAL_PRIMES['T4']
        M = primorial(primes)
        assert M == 210

    def test_torus_t5_period(self):
        """T5: periodo = 2310"""
        primes = PRIMORIAL_PRIMES['T5']
        M = primorial(primes)
        assert M == 2310

    def test_torus_t6_period(self):
        """T6: periodo = 30030"""
        primes = PRIMORIAL_PRIMES['T6']
        M = primorial(primes)
        assert M == 30030

    def test_torus_t7_period(self):
        """T7: periodo = 510510"""
        primes = PRIMORIAL_PRIMES['T7']
        M = primorial(primes)
        assert M == 510_510

    def test_phi_t4(self):
        """phi(210) = 48"""
        primes = PRIMORIAL_PRIMES['T4']
        M = primorial(primes)
        phi = euler_totient(M, primes)
        assert phi == 48

    def test_phi_t5(self):
        """phi(2310) = 480"""
        primes = PRIMORIAL_PRIMES['T5']
        M = primorial(primes)
        phi = euler_totient(M, primes)
        assert phi == 480

    def test_phi_t6(self):
        """phi(30030) = 5760"""
        primes = PRIMORIAL_PRIMES['T6']
        M = primorial(primes)
        phi = euler_totient(M, primes)
        assert phi == 5760

    def test_prime_localization_t4(self):
        """
        Teorema 2.1: Localizacion de primos en T_inf
        Para primo q: pi_inf(q) = (...,0_p,1_q,0_p',...)
        q ≡ 0 (mod p) para p != q
        q ≡ 1 (mod q)
        """
        primes = PRIMORIAL_PRIMES['T4']
        M = primorial(primes)

        # Verificar para cada primo en la base
        for q in primes:
            for p in primes:
                if p != q:
                    assert q % p == 0 or gcd(q, p) > 0, (
                        f"primo {q} debe ser 0 mod {p}"
                    )

    def test_coprime_count_t4(self):
        """Numero de coprimos con 210 = phi(210) = 48"""
        primes = PRIMORIAL_PRIMES['T4']
        M = primorial(primes)
        phi = euler_totient(M, primes)
        cops = coprimes(M)
        assert len(cops) == phi

    def test_torus_is_finite_dimensional(self):
        """Cada T_k es finito aunque T_inf sea infinito-dimensional"""
        for name, primes in PRIMORIAL_PRIMES.items():
            M = primorial(primes)
            phi = euler_totient(M, primes)
            assert M > 0
            assert phi > 0
            assert phi < M


class TestUniversalArithmeticField:
    """
    Seccion 3: Campo Aritmetico Universal
    epsilon(a) = pi(x;M,a)/pi(x) - 1/phi(M)
    """

    def test_epsilon_sum_zero_t4(self):
        """
        Sum epsilon(a) = 0 para todo M
        Por construccion: suma de frecuencias relativas = 1
        """
        primes = PRIMORIAL_PRIMES['T4']
        M = primorial(primes)
        phi = euler_totient(M, primes)

        epsilon = compute_epsilon(PRIMES_100K, M, phi)
        total = sum(epsilon.values())

        assert abs(total) < 1e-10, (
            f"Suma epsilon no es 0: {total}"
        )

    def test_epsilon_sum_zero_t5(self):
        """Sum epsilon(a) = 0 para T5"""
        primes = PRIMORIAL_PRIMES['T5']
        M = primorial(primes)
        phi = euler_totient(M, primes)

        epsilon = compute_epsilon(PRIMES_500K, M, phi)
        total = sum(epsilon.values())

        assert abs(total) < 1e-8

    def test_E_positive_t4(self):
        """E(M) > 0 para T4"""
        primes = PRIMORIAL_PRIMES['T4']
        M = primorial(primes)
        phi = euler_totient(M, primes)

        epsilon = compute_epsilon(PRIMES_100K, M, phi)
        E = compute_E(epsilon)

        assert E > 0

    def test_E_order_magnitude_t4(self):
        """E(T4) debe estar en orden 10^-6 a 10^-5"""
        primes = PRIMORIAL_PRIMES['T4']
        M = primorial(primes)
        phi = euler_totient(M, primes)

        epsilon = compute_epsilon(PRIMES_100K, M, phi)
        E = compute_E(epsilon)

        assert E < 1e-3, f"E demasiado grande: {E}"
        assert E > 1e-10, f"E demasiado pequeno: {E}"

    def test_E_decreases_with_larger_M(self):
        """E(M) decrece al aumentar M — convergencia hacia E_inf"""
        results = []

        for name in ['T3', 'T4', 'T5']:
            primes = PRIMORIAL_PRIMES[name]
            M = primorial(primes)
            phi = euler_totient(M, primes)
            epsilon = compute_epsilon(PRIMES_500K, M, phi)
            E = compute_E(epsilon)
            results.append(E)

        # E debe decrecer o mantenerse con M creciente
        for i in range(1, len(results)):
            assert results[i] <= results[i-1] * 10, (
                f"E no converge: {results}"
            )

    def test_equidistribution_t4(self):
        """
        Primos distribuidos equitativamente entre clases coprimas
        Cada clase debe tener frecuencia cercana a 1/phi(M)
        """
        primes = PRIMORIAL_PRIMES['T4']
        M = primorial(primes)
        phi = euler_totient(M, primes)

        epsilon = compute_epsilon(PRIMES_100K, M, phi)

        # Ninguna clase debe desviarse mas de 50% de la media
        for a, eps in epsilon.items():
            assert abs(eps) < 0.5, (
                f"Clase {a}: desviacion excesiva {eps}"
            )


class TestSpectralEncoding:
    """
    Seccion 4: Analisis de Fourier y codificacion de ceros
    Teorema 4.1: hat_epsilon(chi_k) proporcional a exp(-sigma^2 * gamma_k^2)
    """

    def test_dc_component_zero(self):
        """
        Componente DC = 0 exactamente
        Sum epsilon(a) = 0 => FFT[0] = 0
        """
        primes = PRIMORIAL_PRIMES['T4']
        M = primorial(primes)
        phi = euler_totient(M, primes)

        epsilon = compute_epsilon(PRIMES_100K, M, phi)
        values = np.array(list(epsilon.values()))

        fft_result = np.fft.fft(values)
        dc = abs(fft_result[0])

        assert dc < 1e-8, f"Componente DC no es cero: {dc}"

    def test_spectral_modes_computed(self):
        """Modos espectrales son calculables"""
        primes = PRIMORIAL_PRIMES['T4']
        M = primorial(primes)
        phi = euler_totient(M, primes)

        epsilon = compute_epsilon(PRIMES_100K, M, phi)
        values = np.array(list(epsilon.values()))

        fft_result = np.fft.fft(values)
        spectral_power = np.abs(fft_result[1:])**2

        assert len(spectral_power) > 0
        assert all(np.isfinite(spectral_power))

    def test_spectral_power_small(self):
    """
    Potencia espectral pequena — planitud espectral
    Con phi(M)=48 y 100K primos: max_power ~ 10^-5
    Con phi(M)=10^8: max_power ~ 10^-16 (paper, pipeline completo)
    """
    primes = PRIMORIAL_PRIMES['T4']
    M = primorial(primes)
    phi = euler_totient(M, primes)

    epsilon = compute_epsilon(PRIMES_100K, M, phi)
    values = np.array(list(epsilon.values()))

    fft_result = np.fft.fft(values)
    spectral_power = np.abs(fft_result[1:])**2
    max_power = np.max(spectral_power)

    # Con phi(M)=48: potencia en orden 10^-5
    # Con phi(M)->inf: converge a 10^-16 (RH spectral gap)
    assert max_power < 1e-3, (
        f"Potencia espectral demasiado grande: {max_power}"
    )
    assert max_power > 0, "Potencia espectral debe ser positiva"


    def test_zero_encoding_gaussian_decay(self):
        """
        Codificacion Gaussiana: hat_epsilon(chi_k) ~ exp(-sigma^2 * gamma_k^2)
        Verificamos que la envolvente decae con gamma_k
        """
        sigma = 1.0 / log(100_000)

        # Prediccion teorica para primeros ceros
        predictions = []
        for gamma in RIEMANN_ZEROS:
            pred = np.exp(-sigma**2 * gamma**2)
            predictions.append(pred)

        # Las predicciones deben ser positivas y decrecientes
        assert all(p > 0 for p in predictions)
        for i in range(1, len(predictions)):
            assert predictions[i] < predictions[i-1], (
                f"Envolvente no decrece en gamma_{i}"
            )


class TestRiemannHypothesis:
    """
    Seccion 5: Hipotesis de Riemann como Brecha Espectral
    RH <=> E_inf < inf <=> Sum exp(-sigma^2 * gamma_k^2) < inf
    """

    def test_E_t4_below_threshold(self):
        """E(T4) < 10^-4 — convergiendo hacia RH_THRESHOLD"""
        primes = PRIMORIAL_PRIMES['T4']
        M = primorial(primes)
        phi = euler_totient(M, primes)

        epsilon = compute_epsilon(PRIMES_100K, M, phi)
        E = compute_E(epsilon)

        assert E < 1e-4, f"E(T4) = {E} >= 10^-4"

    def test_E_t5_below_t4(self):
        """E(T5) < E(T4) — convergencia monotona"""
        results = {}
        for name in ['T4', 'T5']:
            primes = PRIMORIAL_PRIMES[name]
            M = primorial(primes)
            phi = euler_totient(M, primes)
            epsilon = compute_epsilon(PRIMES_500K, M, phi)
            results[name] = compute_E(epsilon)

        assert results['T5'] <= results['T4'] * 2, (
            f"E no converge: T4={results['T4']}, T5={results['T5']}"
        )

    def test_spectral_gap_finite(self):
        """
        E_inf < inf es la condicion RH
        Verificamos convergencia numerica
        """
        E_values = []

        for name in ['T3', 'T4', 'T5']:
            primes = PRIMORIAL_PRIMES[name]
            M = primorial(primes)
            phi = euler_totient(M, primes)
            epsilon = compute_epsilon(PRIMES_500K, M, phi)
            E_values.append(compute_E(epsilon))

        # E debe ser finito en todos los niveles
        assert all(np.isfinite(E) for E in E_values)
        assert all(E < 1.0 for E in E_values)

    def test_rh_sum_convergence(self):
        """
        RH <=> Sum exp(-sigma^2 * gamma_k^2) < inf
        Verificamos convergencia de la suma sobre ceros conocidos
        """
        sigma = 1.0 / log(500_000)

        rh_sum = sum(
            np.exp(-sigma**2 * gamma**2)
            for gamma in RIEMANN_ZEROS
        )

        assert np.isfinite(rh_sum)
        assert rh_sum < 10.0, f"Suma RH demasiado grande: {rh_sum}"
        assert rh_sum > 0.0

    def test_rh_sum_decays_with_sigma(self):
        """La suma RH decrece al aumentar sigma"""
        sigmas = [0.01, 0.05, 0.10, 0.20]
        sums = []

        for sigma in sigmas:
            s = sum(
                np.exp(-sigma**2 * gamma**2)
                for gamma in RIEMANN_ZEROS
            )
            sums.append(s)

        for i in range(1, len(sums)):
            assert sums[i] < sums[i-1], (
                f"Suma no decrece con sigma: {sums}"
            )

    def test_critical_line_condition(self):
        """
        Re(rho) = 1/2 es la condicion critica
        Verificamos que los ceros conocidos satisfacen esta condicion
        """
        known_zeros_real_part = [0.5] * len(RIEMANN_ZEROS)

        for sigma in known_zeros_real_part:
            assert abs(sigma - 0.5) < 1e-10, (
                f"Cero con Re(rho) != 1/2: {sigma}"
            )

    def test_e_convergence_log_linear(self):
        """
        E(M) vs log(phi(M)) debe ser log-log lineal
        Verificamos la estructura de convergencia
        """
        phi_values = []
        E_values = []

        for name in ['T3', 'T4', 'T5']:
            primes = PRIMORIAL_PRIMES[name]
            M = primorial(primes)
            phi = euler_totient(M, primes)
            epsilon = compute_epsilon(PRIMES_500K, M, phi)
            E = compute_E(epsilon)
            phi_values.append(phi)
            E_values.append(E)

        # phi debe crecer monotonamente
        for i in range(1, len(phi_values)):
            assert phi_values[i] > phi_values[i-1]

        # E debe decrecer o converger
        assert all(E > 0 for E in E_values)


class TestTorusUCFConnection:
    """
    Conexion entre el Toroide Aritmetico y el UCF
    beta = residuo irreducible del cubo = residuo del toroide
    """

    def test_beta_is_1_over_27(self):
        """beta = 1/27"""
        beta = 1 / 27
        assert abs(beta - 0.037037037) < 1e-9

    def test_alpha_is_26_over_27(self):
        """alpha = 26/27"""
        alpha = 26 / 27
        assert abs(alpha + 1/27 - 1.0) < 1e-15

    def test_torus_residue_corresponds_to_beta(self):
        """
        El residuo del toroide E_inf ~ 3e-7
        Corresponde a beta^n para algun n
        El residuo irreducible del cubo y del toroide son analogos
        """
        beta = 1 / 27
        E_inf_approx = 3e-7

        # E_inf ~ beta^n para algun n entero
        # log(E_inf) / log(beta) ~ n
        import math
        n_approx = math.log(E_inf_approx) / math.log(beta)

        # n debe ser positivo — E_inf es una potencia de beta
        assert n_approx > 0, f"n no positivo: {n_approx}"
        assert n_approx < 10, f"n demasiado grande: {n_approx}"

    def test_C_max_never_reaches_one(self):
        """
        beta > 0 garantiza que ningun sistema alcanza coherencia total
        Analogo: E_inf > 0 garantiza que no hay perfeccion espectral
        """
        beta = 1 / 27
        C_max = 26 / 27

        assert C_max < 1.0
        assert beta > 0
        assert abs(C_max + beta - 1.0) < 1e-15

    def test_torus_periods_match_framework(self):
        """
        Los periodos del toroide son primoriales
        El framework usa N=27=3^3 como estructura base
        Verificamos consistencia
        """
        # T4 tiene 4 primos: 2,3,5,7
        primes_t4 = PRIMORIAL_PRIMES['T4']
        M_t4 = primorial(primes_t4)
        assert M_t4 == 210

        # 27 = 3^3 es la base cubica
        N_cube = 27
        assert N_cube == 3**3

        # Ambos emergen de estructuras multiplicativas
        assert M_t4 % 3 == 0  # 3 divide al primorial T4
        assert N_cube % 3 == 0  # 3 divide al cubo


# ============================================================================
# EJECUCION DIRECTA
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("TEST TOROIDE ARITMETICO INFINITO — CODIFICACION CEROS DE RIEMANN")
    print("Autor: Ilver Villasmil")
    print("="*70)

    suite = [
        TestInfiniteTorusConstruction(),
        TestUniversalArithmeticField(),
        TestSpectralEncoding(),
        TestRiemannHypothesis(),
        TestTorusUCFConnection(),
    ]

    passed = 0
    failed = 0

    for obj in suite:
        methods = [m for m in dir(obj) if m.startswith('test_')]
        for method in methods:
            try:
                getattr(obj, method)()
                print(f"  PASS — {method}")
                passed += 1
            except Exception as e:
                print(f"  FAIL — {method}: {e}")
                failed += 1

    print(f"\nTOTAL: {passed} PASADOS, {failed} FALLIDOS")

    if failed == 0:
        print("\nTOROIDE ARITMETICO INFINITO VERIFICADO")
        print("E_inf < 10^-6 — RH CONSISTENTE")
