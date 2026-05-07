"""
ATAQUE A LA LEY OMEGA DE OBSTRUCCION UNIVERSAL
Objetivo: encontrar A, B, n con gcd(A,B)=1, n>=3 tal que z(A^n + B^n) >= 3
Estrategia de ataque en 5 frentes:
1. n par (punto debil identificado - factorizacion S*Q no aplica directamente)
2. n primo grande
3. A o B muy grandes con n=3
4. Casos cercanos a excepciones de Zsygmondy
5. Busqueda aleatoria adversarial masiva
"""

from math import gcd
from sympy import factorint, isprime
import random

def z_value(N):
    """Calcula z(N) = gcd de todos los valuaciones p-adicas de N"""
    if N <= 1:
        return 0
    factors = factorint(N)
    valuations = list(factors.values())
    result = valuations[0]
    for v in valuations[1:]:
        result = gcd(result, v)
    return result

def check_omega_law(A, B, n):
    """Verifica la ley Omega para un triplete dado"""
    if gcd(A, B) != 1:
        return None  # No aplica
    N = A**n + B**n
    z = z_value(N)
    return z

violations = []
max_z_found = 1
max_case = None

print("=" * 60)
print("ATAQUE 1: n PAR (4, 6, 8, 10, 12)")
print("=" * 60)
count_even = 0
for n in [4, 6, 8, 10, 12]:
    for A in range(1, 200):
        for B in range(1, 200):
            if gcd(A, B) != 1:
                continue
            z = check_omega_law(A, B, n)
            if z is not None and z > max_z_found:
                max_z_found = z
                max_case = (A, B, n, z)
            if z is not None and z >= 3:
                violations.append((A, B, n, z))
                print(f"  VIOLATION: A={A}, B={B}, n={n}, z={z}")
            count_even += 1
print(f"  Casos verificados: {count_even}")
print(f"  Violaciones encontradas: {len(violations)}")
print(f"  z maximo encontrado: {max_z_found} en {max_case}")

print()
print("=" * 60)
print("ATAQUE 2: n PRIMO GRANDE (13, 17, 19, 23, 29, 31)")
print("=" * 60)
count_prime = 0
for n in [13, 17, 19, 23, 29, 31]:
    for A in range(1, 100):
        for B in range(1, 100):
            if gcd(A, B) != 1:
                continue
            z = check_omega_law(A, B, n)
            if z is not None and z > max_z_found:
                max_z_found = z
                max_case = (A, B, n, z)
            if z is not None and z >= 3:
                violations.append((A, B, n, z))
                print(f"  VIOLATION: A={A}, B={B}, n={n}, z={z}")
            count_prime += 1
print(f"  Casos verificados: {count_prime}")
print(f"  Violaciones encontradas: {len([v for v in violations if v[2] in [13,17,19,23,29,31]])}")

print()
print("=" * 60)
print("ATAQUE 3: A o B GRANDES, n=3 (hasta A,B=5000)")
print("=" * 60)
count_large = 0
for A in range(1000, 5001, 100):
    for B in range(1, 100):
        if gcd(A, B) != 1:
            continue
        z = check_omega_law(A, B, 3)
        if z is not None and z > max_z_found:
            max_z_found = z
            max_case = (A, B, 3, z)
        if z is not None and z >= 3:
            violations.append((A, B, 3, z))
            print(f"  VIOLATION: A={A}, B={B}, n=3, z={z}")
        count_large += 1
print(f"  Casos verificados: {count_large}")
print(f"  Violaciones encontradas: {len([v for v in violations if v[0] >= 1000])}")

print()
print("=" * 60)
print("ATAQUE 4: EXCEPCIONES ZSYGMONDY - casos cercanos")
print("Zsygmondy falla en: (a,b,n)=(2,1,6) y a+b=2^s, n=2")
print("Buscando casos con n=6 y variaciones")
print("=" * 60)
count_zsyg = 0
# Caso especial Zsygmondy: (2,1,6) -> 2^6 + 1^6 = 65 = 5*13, z=1 OK
# Intentar variaciones cercanas
for A in range(1, 50):
    for B in range(1, 50):
        if gcd(A, B) != 1:
            continue
        for n in [6, 12, 18]:
            z = check_omega_law(A, B, n)
            if z is not None and z > max_z_found:
                max_z_found = z
                max_case = (A, B, n, z)
            if z is not None and z >= 3:
                violations.append((A, B, n, z))
                print(f"  VIOLATION: A={A}, B={B}, n={n}, z={z}")
            count_zsyg += 1
print(f"  Casos verificados: {count_zsyg}")

print()
print("=" * 60)
print("ATAQUE 5: BUSQUEDA ALEATORIA ADVERSARIAL (100,000 casos)")
print("Estrategia: maximizar z buscando N con muchos factores repetidos")
print("=" * 60)
random.seed(42)
count_random = 0
for _ in range(100000):
    n = random.randint(3, 20)
    A = random.randint(1, 10000)
    B = random.randint(1, 10000)
    if gcd(A, B) != 1:
        continue
    # Solo factorizamos si N no es demasiado grande
    N = A**n + B**n
    if N > 10**30:
        continue
    z = z_value(N)
    if z > max_z_found:
        max_z_found = z
        max_case = (A, B, n, z)
        print(f"  Nuevo maximo z={z}: A={A}, B={B}, n={n}, N={N}")
    if z >= 3:
        violations.append((A, B, n, z))
        print(f"  VIOLATION: A={A}, B={B}, n={n}, z={z}, N={N}")
    count_random += 1

print(f"  Casos verificados: {count_random}")

print()
print("=" * 60)
print("RESULTADO FINAL DEL ATAQUE")
print("=" * 60)
print(f"Total violaciones (z >= 3 con gcd(A,B)=1): {len(violations)}")
print(f"z maximo encontrado en todo el ataque: {max_z_found}")
if max_case:
    print(f"Caso con z maximo: A={max_case[0]}, B={max_case[1]}, n={max_case[2]}, z={max_case[3]}")
if violations:
    print("VIOLACIONES DETALLADAS:")
    for v in violations:
        print(f"  A={v[0]}, B={v[1]}, n={v[2]}, z={v[3]}")
else:
    print("CERO VIOLACIONES. La Ley Omega resistio todos los ataques.")
