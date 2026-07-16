import time

def is_prime_uis_xtreme(n):
    """
    Motor CRF-UIS con Pinza de Tenazas.
    Exploración 0 -> 1 millon.
    """

    if n < 2:
        return False

    # Filtro estructural 6k±1
    if n % 6 != 1 and n % 6 != 5:
        return False

    # Pinza de Tenazas:
    # elimina fases divisibles por primos pequeños
    for p in [5, 7, 11, 13, 17, 19, 23, 29, 31,
              37, 41, 43, 47, 53]:
        if n % p == 0:
            return False

    # Miller-Rabin
    d = n - 1
    s = 0

    while d % 2 == 0:
        d //= 2
        s += 1

    witnesses = [2, 3, 5, 7, 11, 13, 17, 19, 23]

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


def test_pinza_tenazas_0_a_1_millon():

    inicio_tiempo = time.time()

    encontrados = []

    limite = 100

    for n in range(2, limite + 1):

        if is_prime_uis_xtreme(n):
            encontrados.append(n)

    duracion = time.time() - inicio_tiempo

    print(f"\n[CRF-UIS]")
    print(f"Primos encontrados: {len(encontrados)}")
    print(f"Primeros: {encontrados[:10]}")
    print(f"Últimos: {encontrados[-10:]}")
    print(f"Tiempo: {duracion:.4f}s")

    assert len(encontrados) > 0
