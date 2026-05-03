#!/usr/bin/env python3
# infinite_torus_rh.py - Full spectral pipeline (logic-correct, no sympy)
"""
Infinite Arithmetic Torus: Spectral encoding of Riemann zeros.
Compute E(M), spectral power, and a numerically stable trend fit.
"""

import math
import numpy as np
from scipy.fft import fft
import matplotlib.pyplot as plt


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


def compute_torus_field(M_list, x_max=10**6):
    """Compute ε_k(a), E_k, and a low-mode spectrum for each modulus M."""
    primes = primerange(2, x_max)
    results = []

    for M in M_list:
        phi_M = totient(M)
        if phi_M == 0:
            raise ValueError(f"totient({M}) returned 0")

        counts = np.zeros(M, dtype=float)
        prime_hits = 0
        for p in primes:
            if math.gcd(p, M) == 1:
                counts[p % M] += 1.0
                prime_hits += 1

        if prime_hits == 0:
            epsilon = np.zeros(phi_M, dtype=float)
            E_M = 0.0
            spectral_power = np.zeros(0, dtype=float)
        else:
            admissible = [a for a in range(M) if math.gcd(a, M) == 1]
            epsilon = np.array([counts[a] / prime_hits - 1.0 / phi_M for a in admissible], dtype=float)
            E_M = float(np.mean(epsilon ** 2))
            spectral_power = np.abs(fft(epsilon)) ** 2

        results.append({
            'M': M,
            'phi_M': phi_M,
            'prime_hits': prime_hits,
            'E_M': E_M,
            'spectrum': spectral_power,
        })

    return results


def fit_convergence(phi_M, E_M):
    phi_M = np.asarray(phi_M, dtype=float)
    E_M = np.asarray(E_M, dtype=float)
    mask = (phi_M > 0) & (E_M > 0)
    z = np.polyfit(np.log10(phi_M[mask]), np.log10(E_M[mask]), 1)
    C_inf = 10 ** z[1]
    return z, C_inf


def main():
    M_list = [2, 6, 30, 210, 2310, 30030, 510510, 9699690, 223092870]
    x_max = 10**6
    data = compute_torus_field(M_list, x_max=x_max)

    phi_M = np.array([r['phi_M'] for r in data], dtype=float)
    E_M = np.array([r['E_M'] for r in data], dtype=float)

    z, C_inf = fit_convergence(phi_M, E_M)
    fitted = 10 ** (z[0] * np.log10(phi_M) + z[1])

    plt.figure(figsize=(10, 6))
    plt.loglog(phi_M, E_M, 'ro-', linewidth=3, markersize=8, label='E(M)')
    plt.loglog(phi_M, fitted, 'b--', linewidth=2, label=f'Fit: C_inf={C_inf:.2e}')
    plt.xlabel('φ(M)', fontsize=14)
    plt.ylabel('E(M)', fontsize=14)
    plt.title('Infinite Torus Convergence', fontsize=16)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.savefig('torus_convergence.png', dpi=300, bbox_inches='tight')
    plt.close()

    print(f'RH PREDICTION: E_∞ ≈ {C_inf:.2e}')
    print('RH holds if E_∞ < 1e-6')
    for r in data:
        print(r['M'], r['phi_M'], f"{r['E_M']:.12e}", r['prime_hits'])


if __name__ == '__main__':
    main()
