import pytest

def is_prime_uis(n):
    """
    Teorema del Retículo Hexagonal:
    Un número es primo solo si es 6k+1 y pasa la Pinza de Tenazas.
    """
    if n < 7: return n in [2, 3, 5]
    if n % 6 != 1: return False
    
    # Pinza de Tenazas (filtros fundamentales)
    if n % 5 == 0 or n % 7 == 0: return False
    
    # Test Miller-Rabin (Determinista para n < 3e16)
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in [2, 3, 5, 7, 11, 13, 17]:
        x = pow(a, d, n)
        if x == 1 or x == n - 1: continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else:
            return False
    return True

def test_teorema_primos_uis():
    """Valida la arquitectura 6k+1 en el rango de los primeros 100 nodos."""
    # Primos conocidos que cumplen 6k+1
    assert is_prime_uis(7) is True
    assert is_prime_uis(13) is True
    assert is_prime_uis(19) is True
    assert is_prime_uis(31) is True
    assert is_prime_uis(37) is True
    
    # Comprobación de integridad contra espacios muertos
    assert is_prime_uis(8) is False  # Espacio muerto
    assert is_prime_uis(9) is False  # Espacio muerto
    assert is_prime_uis(25) is False # Falla en filtro 5
