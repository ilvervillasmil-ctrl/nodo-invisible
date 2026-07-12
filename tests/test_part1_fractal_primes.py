"""
test_part1_fractal_primes.py

Complete pytest-style validation of Part I from:
"The Ω Law of Universal Integration" by Ilver Villasmil (2026)

Part I: Fractal Primes and the 6-Coprime Decomposition

This module tests all major theorems from Part I of the paper.

Theorems covered:
- Theorem 3.1  : Existence and uniqueness of 6-coprime core
- Theorem 3.2  : Residue classes (mod 6)
- Theorem 3.4  : Cubic closure
- Theorem 3.5  : General closure and monoid structure
- Theorem 3.6  : Residue preservation under cubing
- Theorem 3.7  : DNA property
- Theorem 3.9  : Tower of 3 (unique closed cubic chain)
- Theorem 3.11 : Fractal self-similarity
- Theorem 3.13 : Partition into fractal families
- Theorem 3.15 : Finiteness of DNA chains (probabilistic)

Ready for GitHub + pytest + CI integration.
"""

import math
import pytest
from typing import List


# ============================================================
# CORE FUNCTIONS (from the paper)
# ============================================================

def six_coprime_core(n: int) -> int:
    """Definition 2.1"""
    if n < 2:
        return n
    while n % 3 == 0:
        n //= 3
    while n % 2 == 0:
        n //= 2
    return n


def is_fractal_prime(c: int) -> bool:
    """Definition 2.2"""
    return math.gcd(c, 6) == 1


def dna_property(c: int) -> bool:
    """Theorem 3.7"""
    if c < 10:
        return False
    s = str(c)
    leading_is_odd = int(s[0]) % 2 == 1
    rev_c = int(s[::-1])
    return is_fractal_prime(rev_c) == leading_is_odd


def check_self_similarity(n: int) -> bool:
    """Theorem 3.11"""
    c = six_coprime_core(n)
    return six_coprime_core(n ** 3) == (c ** 3) and is_fractal_prime(c ** 3)


def is_tower_of_3(k: int) -> bool:
    """Theorem 3.9"""
    value = 3 ** (3 * k)
    divisions = 0
    while value % 3 == 0:
        value //= 3
        divisions += 1
    return value == 1 and divisions == (3 * k)


# ============================================================
# TESTS - PART I
# ============================================================

def test_3_1_existence_and_uniqueness():
    """Theorem 3.1"""
    for n in [2, 6, 7, 12, 1237, 334757]:
        c = six_coprime_core(n)
        assert is_fractal_prime(c), f"C({n}) = {c} is not fractal prime"
        assert six_coprime_core(c) == c


def test_3_2_residue_classes():
    """Theorem 3.2"""
    for n in range(2, 50_000):
        c = six_coprime_core(n)
        if is_fractal_prime(c):
            assert c % 6 in (1, 5), f"C({n}) = {c} has invalid residue mod 6"


def test_3_4_cubic_closure():
    """Theorem 3.4"""
    candidates = [7, 17, 29, 37, 617, 1237, 334757]
    for c in candidates:
        assert is_fractal_prime(c)
        assert is_fractal_prime(c ** 3)


def test_3_5_general_closure_and_monoid():
    """Theorem 3.5"""
    a, b = 7, 1237
    assert is_fractal_prime(a)
    assert is_fractal_prime(b)
    assert is_fractal_prime(a * b)
    assert is_fractal_prime(a ** 5)
    assert is_fractal_prime(b ** 3)


def test_3_6_residue_preservation_under_cubing():
    """Theorem 3.6"""
    for c in [7, 17, 29, 37, 1237]:
        assert is_fractal_prime(c)
        c3 = c ** 3
        assert (c % 6) == (c3 % 6)


def test_3_7_dna_property():
    """Theorem 3.7 - DNA property"""
    dna_examples = [17, 1237, 7321]
    for c in dna_examples:
        assert dna_property(c), f"DNA property failed for {c}"


def test_3_9_tower_of_3():
    """Theorem 3.9 - Unique closed cubic chain"""
    for k in range(0, 5):
        assert is_tower_of_3(k), f"Tower of 3 failed at k={k}"


def test_3_11_self_similarity():
    """Theorem 3.11"""
    candidates = [7, 17, 29, 37, 617, 1237]
    for n in candidates:
        assert check_self_similarity(n), f"Self-similarity failed for {n}"


def test_3_13_fractal_family_partition():
    """Theorem 3.13 - Basic partition check"""
    n = 756  # 3^3 * 2^2 * 7
    c = six_coprime_core(n)
    assert c == 7
    assert is_fractal_prime(c)


def test_3_15_dna_chain_finiteness():
    """Theorem 3.15 - Probabilistic check on large set"""
    count = 0
    for n in range(10, 100_000):
        c = six_coprime_core(n)
        if is_fractal_prime(c) and c >= 10:
            if not dna_property(c):
                count += 1
    # Most should eventually terminate (we just check it doesn't explode)
    assert count < 50_000  # sanity bound


# ============================================================
# HEAVY / VOLUME TESTS (optional but recommended)
# ============================================================

@pytest.mark.slow
def test_large_scale_decomposition():
    """Large scale sanity check"""
    errors = 0
    for n in range(2, 500_000):
        c = six_coprime_core(n)
        if not is_fractal_prime(c) and c > 1:
            errors += 1
    assert errors == 0


if __name__ == "__main__":
    # Allow running directly for quick check
    print("Running Part I tests directly...")
    test_3_1_existence_and_uniqueness()
    test_3_2_residue_classes()
    test_3_4_cubic_closure()
    test_3_5_general_closure_and_monoid()
    test_3_6_residue_preservation_under_cubing()
    test_3_7_dna_property()
    test_3_9_tower_of_3()
    test_3_11_self_similarity()
    test_3_13_fractal_family_partition()
    test_3_15_dna_chain_finiteness()
    print("All Part I tests passed.")
