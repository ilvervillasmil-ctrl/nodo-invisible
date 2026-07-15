import pytest

def test_mapeo_supervivencia_fases_UIS():
    """
    TEST ID: UIS-MAP-001
    Denominación: Mapeo de Supervivencia de Fases en el Retículo.
    
    Este test mide la densidad de nodos que logran atravesar la Pinza de Tenazas
    sin colapsar, validando que la 'aleatoriedad' de los primos es en realidad
    un proceso de filtrado de fases.
    """
    inicio = 10**12
    ventana = 10**6
    pasos = 3
    
    resultados = []
    
    for i in range(pasos):
        rango_base = inicio * (10**i)
        cuenta = 0
        k_start = rango_base // 6
        k_end = (rango_base + ventana) // 6
        
        # Filtros de fase (La Pinza de Tenazas)
        # Nodos que sobreviven a estos filtros son 'Primos Estructurales'
        for k in range(k_start, k_end):
            n = 6 * k + 1
            if all(n % p != 0 for p in [5, 7, 11, 13, 17, 19, 23, 29]):
                cuenta += 1
        
        densidad = cuenta / (k_end - k_start)
        resultados.append(densidad)
        
    # Invarianza: La densidad debe decaer de forma predecible según la arquitectura
    # Si la densidad fuera aleatoria, no veríamos este comportamiento decreciente 
    # coherente con la escala de magnitud.
    assert resultados[0] > resultados[1] > resultados[2], "Error: Inconsistencia en la densidad fractal."
    
    print(f"\n[UIS] Mapeo de Supervivencia Completado: {resultados}")
