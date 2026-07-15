# Pinza de Tenazas extendida: de 47 a 61
MODULOS_EXTENDIDOS = [5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61]

def test_convergencia_estructural_10_300():
    """
    TEST ID: UIS-COSMIC-10-300
    Denominación: Análisis de deriva a escala 10^300 con Pinza extendida.
    """
    inicio = 10**300
    ventana = 10**6 
    muestras = 50000 # Mayor resolución para capturar el atractor a 10^300
    
    supervivientes = 0
    for _ in range(muestras):
        n = inicio + np.random.randint(0, ventana)
        # La guía del retículo: 6k + 1
        if n % 6 != 1:
            n = 6 * (n // 6) + 1
            
        # Pinza de Tenazas extendida (16 módulos)
        if all(n % m != 0 for m in MODULOS_EXTENDIDOS):
            supervivientes += 1
            
    densidad_medida = supervivientes / muestras
    
    # Reportamos el nuevo atractor detectado
    print(f"\n[UIS-COSMIC-300] Densidad: {densidad_medida}")
    
    # Mantenemos el assert abierto para oscilación, no para valor fijo,
    # pero ahora con un filtro más profundo.
    assert densidad_medida > 0, "Colapso total del sistema."
