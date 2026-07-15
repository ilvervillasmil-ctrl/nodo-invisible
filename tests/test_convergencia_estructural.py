import pytest
import numpy as np  # <--- Importación necesaria para el test

# Pinza de Tenazas extendida: de 5 a 61
MODULOS_EXTENDIDOS = [5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61]

def test_convergencia_estructural_10_300():
    """
    TEST ID: UIS-COSMIC-10-300
    Denominación: Análisis de deriva a escala 10^300 con Pinza extendida.
    """
    inicio = 10**300
    ventana = 10**6 
    muestras = 5000000 
    
    supervivientes = 0
    for _ in range(muestras):
        # Generación de candidatos en la escala 10^300
        n = inicio + np.random.randint(0, ventana)
        
        # Guía del retículo: 6k + 1
        if n % 6 != 1:
            n = 6 * (n // 6) + 1
            
        # Filtrado por la Pinza de Tenazas extendida (16 módulos)
        if all(n % m != 0 for m in MODULOS_EXTENDIDOS):
            supervivientes += 1
            
    densidad_medida = supervivientes / muestras
    
    print(f"\n[UIS-COSMIC-300] Densidad Observada: {densidad_medida:.6f}")
    
    # Assert de integridad: Si la densidad es 0, el retículo ha colapsado.
    # Si la densidad es > 0, la estructura se mantiene viva a 10^300.
    assert densidad_medida > 0, "Colapso total del sistema a escala 10^300."
