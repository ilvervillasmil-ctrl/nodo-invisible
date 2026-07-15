import pytest
import random


def test_busqueda_primo_gigantesco_uis():
    """
    Prueba de estrés del Teorema del Retículo Hexagonal (UIS).

    Busca un primo grande en la rama 6k+1 sin usar valores conocidos.
    El test falla si el filtro UIS no encuentra un nodo válido.
    """

    inicio = 10**15
    intentos = 100000

    encontrado = None

    # Genera posiciones grandes aleatorias en la rama 6k+1
    for _ in range(intentos):

        k = random.randint(inicio // 6, inicio // 6 + 10**8)

        n = 6 * k + 1

        if is_prime_uis(n):
            encontrado = n
            break

    assert encontrado is not None, (
        "El filtro UIS no encontró un primo 6k+1 "
        "en la búsqueda de alto rango"
    )

    print(f"\nPrimo encontrado por UIS: {encontrado}")
    print(f"Residuo módulo 6: {encontrado % 6}")

    assert encontrado % 6 == 1
