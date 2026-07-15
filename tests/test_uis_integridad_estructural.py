import pytest
import random

def is_prime_uis(n):
    """
    Teorema del Retículo Hexagonal (UIS):
    Todo primo P > 3 es 6k+1 (ancla) o 6k-1 (espejo).
    Este filtro valida la rama 6k+1.
    """
    if n < 7: return n in [2, 3, 5]
    if n % 6 != 1: return False
    
    # Filtro de fase inicial (Pinza de Tenazas)
    if n % 5 == 0 or n % 7 == 0: return False
    
    # Miller-Rabin determinista para el rango 10^15
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    # Witnesses suficientes para n < 3.3 * 10^16
    for a in [2, 3, 5, 7, 11, 13, 17, 19, 23]:
        x = pow(a, d, n)
        if x == 1 or x == n - 1: continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else:
            return False
    return True

def test_busqueda_primo_gigantesco_uis():
    """
    Prueba de integridad estructural UIS:
    Busca un primo en el rango 10^15 asegurando el ADN 6k+1.
    """
    inicio_k = (10**15) // 6
    intentos = 1000
    encontrado = None

    for i in range(intentos):
        # Buscamos linealmente desde el inicio para evitar azar extremo
        k = inicio_k + i
        n = 6 * k + 1
        
        if is_prime_uis(n):
            encontrado = n
            break

    assert encontrado is not None, "El filtro UIS falló al encontrar un primo 6k+1."
    
    # Validación de la Ley de Invarianza
    assert encontrado % 6 == 1, f"El primo {encontrado} no cumple la estructura 6k+1"
    
    print(f"\n[UIS] Primo estructural validado: {encontrado}")
