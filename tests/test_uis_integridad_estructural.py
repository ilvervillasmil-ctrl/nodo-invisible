import pytest
import sys
import os

# Esto asegura que Python pueda encontrar tu módulo raíz si estás en una carpeta de tests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# REEMPLAZA 'uis_core' por el nombre de tu archivo si es distinto
from uis_core import is_prime_uis, find_next_prime_uis

def test_uis_integridad_estructural():
    """Verifica que el ADN sea siempre 6k+1 y que el filtro no admita basura."""
    assert is_prime_uis(7) is True
    assert is_prime_uis(13) is True
    assert is_prime_uis(25) is False  # 6k+1 pero compuesto
    assert is_prime_uis(11) is False  # 6k-1

def test_next_prime_logic():
    """Verifica que la búsqueda UIS salta los espacios muertos."""
    p1 = 37
    p2 = find_next_prime_uis(p1)
    assert p2 > p1
    assert p2 % 6 == 1
    assert is_prime_uis(p2) is True

def test_large_number_consistency():
    """Prueba de estrés con números conocidos."""
    p = 1000000007 
    assert is_prime_uis(p) is True
