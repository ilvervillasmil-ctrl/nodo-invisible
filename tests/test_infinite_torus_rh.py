import math
import numpy as np


def is_prime(n):
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def primerange(a, b):
    return [n for n in range(a, b) if is_prime(n)]


def totient(n):
    result = n
    m = n
    p = 2
    while p * p <= m:
        if m % p == 0:
            while m % p == 0:
                m //= p
            result -= result // p
        p += 1
    if m > 1:
        result -= result // m
    return result


def dft(x):
    x = np.asarray(x, dtype=complex)
    n = x.size
    if n == 0:
        return np.array([], dtype=complex)
    k = np.arange(n)
    m = k.reshape((n, 1))
    W = np.exp(-2j * np.pi * m * k / n)
    return W @ x


def compute_torus_field(M_list, x_max=100000):
    primes = primerange(2, x_max)
    results = []

    for M in M_list:
        phi_M = totient(M)
        admissible = [a for a in range(M) if math.gcd(a, M) == 1]
        counts = np.zeros(M, dtype=float)
        prime_hits = 0

        for p in primes:
            if math.gcd(p, M) == 1:
                counts[p % M] += 1.0
                prime_hits += 1

        if phi_M == 0 or not admissible or prime_hits == 0:
            epsilon = np.zeros(1, dtype=float)
            E_M = 0.0
            spectrum = np.zeros(1, dtype=float)
        else:
            epsilon = np.array(
                [counts[a] / prime_hits - 1.0 / phi_M for a in admissible],
                dtype=float
            )
            E_M = float(np.mean(epsilon ** 2))
            spectrum = np.abs(dft(epsilon)) ** 2

        results.append(
            {
                "M": M,
                "phi_M": phi_M,
                "prime_hits": prime_hits,
                "E_M": E_M,
                "spectrum": spectrum,
            }
        )

    return results


def fit_convergence(phi_M, E_M):
    phi_M = np.asarray(phi_M, dtype=float)
    E_M = np.asarray(E_M, dtype=float)
    mask = (phi_M > 0) & (E_M > 0)
    if mask.sum() < 2:
        return (0.0, 0.0), 0.0
    z = np.polyfit(np.log10(phi_M[mask]), np.log10(E_M[mask]), 1)
    C_inf = 10 ** z[1]
    return z, C_inf


def test_infinite_torus_pipeline_runs():
    M_list = [2, 6, 30, 210, 2310, 30030, 510510]
    data = compute_torus_field(M_list)

    assert len(data) == len(M_list)

    phi_M = np.array([r["phi_M"] for r in data], dtype=float)
    E_M = np.array([r["E_M"] for r in data], dtype=float)

    assert np.all(phi_M > 0)
    assert np.all(E_M >= 0)

    z, C_inf = fit_convergence(phi_M, E_M)
    assert np.isfinite(C_inf)
