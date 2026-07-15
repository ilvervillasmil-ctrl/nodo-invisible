import pytest
from tu_modulo import is_prime_uis, find_next_prime_uis

def test_uis_integridad_estructural():
    """Verifica que el ADN sea siempre 6k+1 y que el filtro no admita basura."""
    # Casos base de la estructura
    assert is_prime_uis(7) is True
    assert is_prime_uis(13) is True
    assert is_prime_uis(25) is False  # 6k+1 pero compuesto (5*5)
    assert is_prime_uis(11) is False  # No es 6k+1 (Es 6k-1)

def test_next_prime_logic():
    """Verifica que la búsqueda UIS salta los espacios muertos."""
    p1 = 37
    p2 = find_next_prime_uis(p1)
    assert p2 > p1
    assert p2 % 6 == 1
    assert is_prime_uis(p2) is True

def test_large_number_consistency():
    """Prueba de estrés con números conocidos."""
    # Un primo conocido de la forma 6k+1
    p = 1000000007 
    assert is_prime_uis(p) is True
