import pytest
import sys
import os

# Esto fuerza a Python a buscar en la raíz del proyecto, sin importar dónde esté el test
sys.path.insert(0, os.getcwd())

# CAMBIA 'uis_core' POR EL NOMBRE REAL DE TU ARCHIVO (sin el .py)
try:
    from uis_core import is_prime_uis, find_next_prime_uis
except ImportError:
    # Fallback por si el archivo tiene otro nombre
    raise ImportError("No encuentro tu archivo de código. Asegúrate de que el nombre en el 'from' coincida con tu archivo.")

def test_uis_integridad_estructural():
    assert is_prime_uis(7) is True
    assert is_prime_uis(13) is True
    assert is_prime_uis(25) is False
    assert is_prime_uis(11) is False

def test_next_prime_logic():
    p1 = 37
    p2 = find_next_prime_uis(p1)
    assert p2 > p1
    assert p2 % 6 == 1
    assert is_prime_uis(p2) is True

def test_large_number_consistency():
    p = 1000000007 
    assert is_prime_uis(p) is True
