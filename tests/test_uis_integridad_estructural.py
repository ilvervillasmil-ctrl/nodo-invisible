import pytest
import time

def is_prime_uis_xtreme(n):
    """
    Motor CRF-UIS.
    Explora candidatos en las dos clases permitidas:
    6k+1 y 6k-1.
    """
    if n < 2:
        return False

    if n % 2 == 0:
        return n == 2

    if n % 3 == 0:
        return n == 3

    for p in [5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]:
        if n % p == 0:
            return n == p

    d = n - 1
    s = 0

    while d % 2 == 0:
        d //= 2
        s += 1

    witnesses = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]

    for a in witnesses:
        if a >= n:
            break

        x = pow(a, d, n)

        if x == 1 or x == n - 1:
            continue

        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False

    return True


def test_busqueda_bidireccional_10_300():

    inicio_val = 10**300
    inicio_k = inicio_val // 6

    inicio_tiempo = time.time()

    encontrado = None
    familia = None

    ventana = 5000000

    for i in range(ventana):

        # rama positiva
        n_pos = 6 * (inicio_k + i) + 1

        if is_prime_uis_xtreme(n_pos):
            encontrado = n_pos
            familia = "6k+1"
            break


        # rama negativa
        n_neg = 6 * (inicio_k + i) - 1

        if is_prime_uis_xtreme(n_neg):
            encontrado = n_neg
            familia = "6k-1"
            break


    duracion = time.time() - inicio_tiempo


    print(f"\nPrimo encontrado: {encontrado}")
    print(f"Familia: {familia}")
    print(f"Tiempo: {duracion:.4f}s")


    assert encontrado is not None
    assert duracion < 120.0

    assert (
        encontrado % 6 == 1 or
        encontrado % 6 == 5
    )
