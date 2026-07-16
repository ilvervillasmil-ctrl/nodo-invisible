import pytest
import numpy as np


def test_convergencia_estructural_10_200():
    """
    TEST ID: UIS-COSMIC-10-200
    Denominación: Análisis de deriva a escala 10^200.
    """
    inicio = 10**200
    ventana = 10**6 
    muestras = 80000000 # Aumentamos resolución para capturar la oscilación
    
    supervivientes = 0
    for _ in range(muestras):
        # Muestreo en el entorno de 10^200
        n = inicio + np.random.randint(0, ventana)
        if n % 6 != 1:
            n = 6 * (n // 6) + 1
            
        # Pinza de Tenazas extendida (necesaria para estabilidad a 10^200)
        if all(n % m != 0 for m in [5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]):
            supervivientes += 1
            
    densidad_medida = supervivientes / muestras
    error = abs(densidad_medida - DENSIDAD_ASINTOTICA)
    
    # Registro de la oscilación en el log
    print(f"\n[UIS-COSMIC-200] Densidad: {densidad_medida}")
    print(f"[UIS-COSMIC-200] Error: {error}")
    
   
    # Si la oscilación excede 0.1, el retículo está entrando en modo caótico.
    assert error < 0.1, f"Colapso de fase: deriva excesiva {error}"
