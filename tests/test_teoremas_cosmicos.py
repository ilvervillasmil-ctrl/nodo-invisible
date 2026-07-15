import pytest
import numpy as np

# Pinza reducida a 17 (los primeros 7 primos: 2, 3, 5, 7, 11, 13, 17)
# Nota: La guía UIS ya integra el 2 y 3.
MODULOS_AJUSTADOS = [5, 7, 11, 13, 17]

def test_convergencia_inmutable_10_300():
    """
    TEST ID: UIS-INMUTABLE-10-300
    Denominación: Prueba de estrés con Pinza de Tenazas reducida (17).
    """
    inicio = 10**300
    ventana = 10**6 
    muestras = 1000000 
    
    # Conversión a float para estabilidad en cálculos logarítmicos
    inicio_float = float(inicio)
    
    supervivientes = 0
    for _ in range(muestras):
        # Generación de candidatos en escala 10^300
        n = inicio_float + np.random.randint(0, ventana)
        
        # Guía 6k+1: El eje inmutable del retículo
        if n % 6 != 1:
            n = 6 * (int(n) // 6) + 1
            
        # Filtrado con la Pinza ajustada a 17
        if all(n % m != 0 for m in MODULOS_AJUSTADOS):
            supervivientes += 1
            
    densidad = supervivientes / muestras
    
    print(f"\n[UIS-INMUTABLE-17] Densidad a 10^300: {densidad:.6f}")
    
    # Opción binaria: Pasa (Estabilidad) o señala la incoherencia (Colapso)
    assert densidad > 0, "Incoherencia detectada: el sistema colapsó con Pinza de 17."
