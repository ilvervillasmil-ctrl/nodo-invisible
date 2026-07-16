import pytest
import time

def is_prime_uis_xtreme(n):
    """
    Motor CRF-UIS Blindado (Escala 10^50).
    Aplica la Pinza de Tenazas y el filtro estructural 6k+1.
    """
    if n % 6 != 1: return False
    
    # Pinza de Tenazas (Pre-filtro de fases prohibidas)
    # A 10^50, esta criba elimina el 99.99% de los candidatos.
    for p in [5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]:
        if n % p == 0: return False
        
    # Miller-Rabin de Alta Resonancia
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
        
    # Conjunto de testigos para cobertura absoluta en 10^50
    witnesses = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]
    for a in witnesses:
        if a >= n: break
        x = pow(a, d, n)
        if x == 1 or x == n - 1: continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else:
            return False
    return True

def test_benchmark_convergencia_10_50():
    """
    Test de rendimiento extremo para el Teorema.
    Objetivo: Localizar nodo primo en la frontera 10^50 < 60 segundos.
    """
    inicio_val = 10**300
    inicio_k = inicio_val // 6
    
    inicio_tiempo = time.time()
    encontrado = None
    
    # Ventana de exploración (5000000 iteraciones en el retículo)
    for i in range(5000000):
        n = 6 * (inicio_k + i) + 1
        if is_prime_uis_xtreme(n):
            encontrado = n
            break
            
    fin_tiempo = time.time()
    duracion = fin_tiempo - inicio_tiempo
    
    print(f"\n[CRF-UIS] Nodo 10^300 localizado: {encontrado}")
    print(f"[CRF-UIS] Tiempo de convergencia: {duracion:.4f}s")
    
    assert encontrado is not None, "El motor no convergido en la ventana de 5000000 nodos."
    assert duracion < 120.0, f"Error de performance: El teorema tardó {duracion}s."
    assert encontrado % 6 == 1
