import pytest
import sys
import os

# Fuerza a Python a mirar en la raíz del repositorio
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# CAMBIA 'NOMBRE_DE_TU_ARCHIVO' por el nombre real SIN el .py
from NOMBRE_DE_TU_ARCHIVO import is_prime_uis, find_next_prime_uis

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
